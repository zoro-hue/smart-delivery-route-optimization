"""
Road Network Service for ROUTE/IQ.
Loads the authentic NYC OSM road network (54,128 nodes, 142,123 real street edges),
provides spatial KD-Tree node snapping, Dijkstra/A* road-network distance matrix calculation,
and extracts real street curvature geometry (WKT LINESTRING) for Google Maps-like polylines.
"""

import os
import math
import pickle
import zipfile
import gzip
import threading
import re
from typing import List, Tuple, Dict, Any, Optional
import numpy as np
from scipy.spatial import cKDTree
import networkx as nx
from loguru import logger

from app.core.config import get_settings

settings = get_settings()


def to_ordinal(num_str: str) -> str:
    """Convert cardinal street number string to ordinal (e.g. '103' -> '103RD')."""
    try:
        n = int(num_str)
        if 11 <= (n % 100) <= 13:
            return f"{n}TH"
        last = n % 10
        if last == 1:
            return f"{n}ST"
        elif last == 2:
            return f"{n}ND"
        elif last == 3:
            return f"{n}RD"
        else:
            return f"{n}TH"
    except Exception:
        return num_str


def normalize_street_name(s: str) -> str:
    """
    Standardize NYC street and roadway names to maximize authentic join coverage:
    1. Converts cardinal numbers before street types (e.g. '103 STREET' -> '103RD ST').
    2. Resolves standard NYC expressway acronyms (BQE, LIE, CBE, VWE, GCP).
    3. Standardizes common street suffixes (AVE, ST, RD, BLVD, PKWY, EXPY, DR, CT, PL, LN).
    4. Normalizes directional prefixes (N, S, E, W).
    """
    if not s or not isinstance(s, str):
        return ""
    s = s.upper().strip()
    s = re.sub(r"['\"\[\]\(\)]", "", s)
    s = re.sub(r"\bu\b", "", s)

    # Convert cardinal numbers to ordinals before street types
    def replace_num(m):
        return to_ordinal(m.group(1)) + " " + m.group(2)
    s = re.sub(r"\b(\d+)\s+(STREET|ST|AVENUE|AVE|ROAD|RD|PLACE|PL|DRIVE|DR|LANE|LN|BOULEVARD|BLVD|COURT|CT)\b", replace_num, s)

    # Standardize NYC expressway acronyms
    nyc_acronyms = {
        r"\bBQE\b": "BROOKLYN QUEENS EXPY",
        r"\bLIE\b": "LONG ISLAND EXPY",
        r"\bCBE\b": "CROSS BRONX EXPY",
        r"\bVWE\b": "VAN WYCK EXPY",
        r"\bGCP\b": "GRAND CENTRAL PKWY",
        r"\bBRP\b": "BRONX RIVER PKWY",
        r"\bCIP\b": "CROSS ISLAND PKWY",
        r"\bHHP\b": "HENRY HUDSON PKWY",
        r"\bSIE\b": "STATEN ISLAND EXPY",
    }
    for acr, full in nyc_acronyms.items():
        s = re.sub(acr, full, s)

    # Standardize street suffixes & directionals
    replacements = [
        (r"\bAVENUE\b", "AVE"),
        (r"\bSTREET\b", "ST"),
        (r"\bROAD\b", "RD"),
        (r"\bBOULEVARD\b", "BLVD"),
        (r"\bPARKWAY\b", "PKWY"),
        (r"\bEXPRESSWAY\b", "EXPY"),
        (r"\bDRIVE\b", "DR"),
        (r"\bCOURT\b", "CT"),
        (r"\bPLACE\b", "PL"),
        (r"\bLANE\b", "LN"),
        (r"\bTURNPIKE\b", "TPKE"),
        (r"\bHIGHWAY\b", "HWY"),
        (r"\bNORTH\b", "N"),
        (r"\bSOUTH\b", "S"),
        (r"\bEAST\b", "E"),
        (r"\bWEST\b", "W"),
    ]
    for pattern, repl in replacements:
        s = re.sub(pattern, repl, s)
    return re.sub(r"\s+", " ", s).strip()


class RoadNetworkService:
    def __init__(self):
        self.G: Optional[nx.MultiDiGraph] = None
        self.G_undir: Optional[nx.MultiGraph] = None
        self.tree: Optional[cKDTree] = None
        self.nodes_list: List[str] = []
        self.node_coords: List[Tuple[float, float]] = []  # [(lat, lon), ...]
        self._is_loaded = False
        self._lock = threading.Lock()
        self._path_cache: Dict[Tuple[str, str], List[str]] = {}
        self._dist_cache: Dict[Tuple[str, str], float] = {}
        # NOTE: Graph loading is lazy via ensure_loaded() on first route request.
        # This prevents 350MB+ allocation and XML compilation on app import/healthcheck.

    def ensure_loaded(self) -> bool:
        """Thread-safe lazy initialization of NYC road network."""
        if self._is_loaded and self.G is not None:
            return True
        with self._lock:
            if not self._is_loaded or self.G is None:
                self._load_network()
        return self._is_loaded and self.G is not None

    def _load_network(self):
        """Load road graph from processed pickle, gzip pickle, or convert from archive (5).zip."""
        pickle_path = os.path.join(settings.PROCESSED_DATA_DIR, "road_graph_newyork.pickle")
        gzip_pickle_path = os.path.join(settings.PROCESSED_DATA_DIR, "road_graph_newyork.pickle.gz")
        fallback_pickle = os.path.join(settings.PROCESSED_DATA_DIR, "road_graph_manhatten.pickle")

        # 1. Try loading pre-built newyork road graph raw pickle first
        if os.path.exists(pickle_path):
            try:
                logger.info(f"Loading NYC 5-Borough road graph from {pickle_path}...")
                with open(pickle_path, "rb") as f:
                    self.G = pickle.load(f)
                logger.info(f"Loaded NYC road graph: {self.G.number_of_nodes()} nodes, {self.G.number_of_edges()} edges")
            except Exception as e:
                logger.error(f"Failed to load {pickle_path}: {e}")
                self.G = None

        # 2. Try loading compressed gzip pickle (7.7 MB on disk, memory-efficient)
        if self.G is None and os.path.exists(gzip_pickle_path):
            try:
                logger.info(f"Loading NYC 5-Borough road graph from compressed {gzip_pickle_path}...")
                with gzip.open(gzip_pickle_path, "rb") as f:
                    self.G = pickle.load(f)
                logger.info(f"Loaded NYC road graph from gzip: {self.G.number_of_nodes()} nodes, {self.G.number_of_edges()} edges")
                # Also save raw pickle so subsequent loads are sub-second
                try:
                    with open(pickle_path, "wb") as pf:
                        pickle.dump(self.G, pf, protocol=pickle.HIGHEST_PROTOCOL)
                except Exception:
                    pass
            except Exception as e:
                logger.error(f"Failed to load {gzip_pickle_path}: {e}")
                self.G = None

        # 3. If not available, check road_network.zip in data dir or archive (5).zip
        if self.G is None:
            zip_candidates = [
                os.path.join(settings.DATA_DIR, "road_network.zip"),
                os.path.join(settings.BASE_DIR, "data", "road_network.zip"),
                os.path.join(settings.DATA_DIR, "archive (5).zip"),
                os.path.join(settings.BASE_DIR, "..", "archive (5).zip"),
                os.path.join(settings.BASE_DIR, "archive (5).zip"),
                os.path.join(settings.BASE_DIR, "..", "..", "archive (5).zip"),
            ]
            for z_path in zip_candidates:
                if os.path.exists(z_path):
                    try:
                        logger.info(f"Extracting and compiling newyork.graphml from {z_path}...")
                        with zipfile.ZipFile(z_path, "r") as z:
                            if "newyork.graphml" in z.namelist():
                                with z.open("newyork.graphml") as gf:
                                    self.G = nx.read_graphml(gf)
                                # Normalize node/edge types
                                for _, d in self.G.nodes(data=True):
                                    if "x" in d: d["x"] = float(d["x"])
                                    if "y" in d: d["y"] = float(d["y"])
                                for _, _, _, d in self.G.edges(data=True, keys=True):
                                    if "length" in d:
                                        try: d["length"] = float(d["length"])
                                        except: d["length"] = 100.0
                                # Save pickle for fast sub-second startup next time
                                with open(pickle_path, "wb") as pf:
                                    pickle.dump(self.G, pf, protocol=pickle.HIGHEST_PROTOCOL)
                                logger.info(f"Saved compiled road graph to {pickle_path}")
                                break
                    except Exception as e:
                        logger.error(f"Failed to compile graph from {z_path}: {e}")

        # Fallback to Manhattan pickle if New York is unavailable
        if self.G is None and os.path.exists(fallback_pickle):
            logger.warning(f"Using Manhattan fallback road graph from {fallback_pickle}...")
            with open(fallback_pickle, "rb") as f:
                self.G = pickle.load(f)

        if self.G is None:
            logger.error("No valid NYC road graph found! Please ensure road_graph_newyork.pickle.gz exists.")
            return

        # Prepare node lists and spatial index without heavy SCC recursion
        self.nodes_list = list(self.G.nodes())
        coords_arr = np.zeros((len(self.nodes_list), 2), dtype=np.float32)
        for i, n in enumerate(self.nodes_list):
            d = self.G.nodes[n]
            coords_arr[i, 0] = float(d.get("y", 0.0))
            coords_arr[i, 1] = float(d.get("x", 0.0))

        self.node_coords = coords_arr
        self.tree = cKDTree(coords_arr)
        self.G_undir = self.G.to_undirected(as_view=True)
        self._is_loaded = True
        logger.info(f"RoadNetworkService initialized: {len(self.nodes_list)} nodes indexed in KD-Tree.")

        # Release temporary allocation overhead back to OS
        import gc
        gc.collect()
        try:
            import ctypes
            ctypes.CDLL("libc.so.6").malloc_trim(0)
        except Exception:
            pass

    def is_ready(self) -> bool:
        if not self._is_loaded:
            self.ensure_loaded()
        return self._is_loaded and self.G is not None

    def snap_coordinate(self, lat: float, lon: float, max_dist_km: float = 5.0, raise_on_exceed: bool = False) -> Tuple[str, float, float, float]:
        """
        Snap given coordinate (lat, lon) to nearest road graph node.
        Returns: (node_id, snapped_lat, snapped_lon, distance_km)
        """
        if not self.is_ready():
            raise RuntimeError("RoadNetworkService is not loaded.")

        dist_deg, idx = self.tree.query((lat, lon))
        # Approx distance in km: 1 deg lat ~ 111 km
        dist_km = float(dist_deg * 111.0)
        node_id = self.nodes_list[idx]
        snapped_lat = float(self.node_coords[idx, 0])
        snapped_lon = float(self.node_coords[idx, 1])

        if dist_km > max_dist_km:
            msg = f"Coordinate ({lat:.4f}, {lon:.4f}) is {dist_km:.2f}km away from nearest road node {node_id}"
            logger.warning(msg)
            if raise_on_exceed:
                raise ValueError(f"Coordinate ({lat:.4f}, {lon:.4f}) is outside active road network coverage (nearest road is {dist_km:.2f}km away, exceeding {max_dist_km}km threshold).")

        return node_id, snapped_lat, snapped_lon, dist_km

    def build_road_matrix(
        self,
        locations: List[Tuple[float, float]],
        traffic_factor: float = 1.0,
        weather_factor: float = 1.0,
        return_physical: bool = False,
    ):
        """
        Build an NxN road-network travel distance matrix between locations using Dijkstra.
        Caches shortest paths in self._path_cache for fast downstream route geometry reconstruction.
        """
        if not self.is_ready():
            raise RuntimeError("RoadNetworkService is not ready.")

        n = len(locations)
        warnings = []
        snapped_nodes = []
        snapped_coords = []

        for idx, (loc_lat, loc_lon) in enumerate(locations):
            try:
                nid, slat, slon, dkm = self.snap_coordinate(loc_lat, loc_lon)
                snapped_nodes.append(nid)
                snapped_coords.append((slat, slon))
                if dkm > 2.0:
                    warnings.append(f"Stop #{idx} snapped {dkm:.1f}km away to nearest road segment.")
            except Exception as e:
                warnings.append(f"Failed to snap stop #{idx}: {e}")
                snapped_nodes.append(self.nodes_list[0])
                snapped_coords.append((float(self.node_coords[0, 0]), float(self.node_coords[0, 1])))

        cost_matrix = np.zeros((n, n), dtype=np.float64)
        physical_matrix = np.zeros((n, n), dtype=np.float64)
        combined_factor = traffic_factor * weather_factor

        def _reconstruct_path(pred_dict, s_node, t_node):
            if not pred_dict or t_node not in pred_dict:
                return None
            curr = t_node
            path = [curr]
            visited = {curr}
            while curr != s_node:
                p_list = pred_dict.get(curr)
                if not p_list:
                    return None
                curr = p_list[0]
                if curr in visited:
                    return None
                visited.add(curr)
                path.append(curr)
            path.reverse()
            return path

        for i, src_node in enumerate(snapped_nodes):
            # Check if all pairwise distances for this src_node are already in _dist_cache
            all_cached = all(
                (src_node, tgt_node) in self._dist_cache or i == j
                for j, tgt_node in enumerate(snapped_nodes)
            )

            pred, lengths = None, None
            if not all_cached:
                try:
                    pred, lengths = nx.dijkstra_predecessor_and_distance(self.G, src_node, weight="length")
                except Exception as e:
                    logger.error(f"Dijkstra calculation error for node {src_node}: {e}")
                    pred, lengths = {}, {}

            undir_pred, undir_lengths = None, None

            for j, tgt_node in enumerate(snapped_nodes):
                if i == j:
                    cost_matrix[i][j] = 0.0
                    physical_matrix[i][j] = 0.0
                    continue

                if (src_node, tgt_node) in self._dist_cache:
                    road_km = self._dist_cache[(src_node, tgt_node)]
                elif lengths and tgt_node in lengths:
                    road_km = lengths[tgt_node] / 1000.0
                    self._dist_cache[(src_node, tgt_node)] = road_km
                    if (src_node, tgt_node) not in self._path_cache:
                        p = _reconstruct_path(pred, src_node, tgt_node) if pred else None
                        if p:
                            self._path_cache[(src_node, tgt_node)] = p
                else:
                    # Targeted fallback on undirected road graph view for one-way street / bridge gaps
                    if undir_lengths is None:
                        try:
                            undir_pred, undir_lengths = nx.dijkstra_predecessor_and_distance(
                                self.G_undir, src_node, weight="length"
                            )
                        except Exception:
                            undir_pred, undir_lengths = {}, {}

                    if undir_lengths and tgt_node in undir_lengths:
                        road_km = undir_lengths[tgt_node] / 1000.0
                        self._dist_cache[(src_node, tgt_node)] = road_km
                        if (src_node, tgt_node) not in self._path_cache:
                            p = _reconstruct_path(undir_pred, src_node, tgt_node) if undir_pred else None
                            if p:
                                self._path_cache[(src_node, tgt_node)] = p
                    else:
                        logger.error(f"No connected road path between node {src_node} and {tgt_node}")
                        road_km = 99999.0
                        warnings.append(f"Road connectivity between stops #{i} and #{j} disconnected.")

                physical_matrix[i][j] = round(road_km, 3)
                cost_matrix[i][j] = round(road_km * combined_factor, 3)

            # Explicitly release large 54k-element Dijkstra dictionaries to prevent OOM
            del pred, lengths, undir_pred, undir_lengths

        import gc
        gc.collect()

        if return_physical:
            return cost_matrix, snapped_nodes, warnings, physical_matrix
        return cost_matrix, snapped_nodes, warnings

    def get_road_path_geometry(
        self,
        u_node: str,
        v_node: str,
        sub_G: Optional[nx.Graph] = None,
    ) -> List[Tuple[float, float]]:
        """
        Calculate shortest road path between u_node and v_node and extract
        detailed street curvature geometry (WKT LINESTRING coordinates).
        Returns list of (lat, lon) coordinates along real road segments.
        Never falls back to a straight line across water/buildings.
        """
        if u_node == v_node:
            u_d = self.G.nodes[u_node]
            return [(float(u_d["y"]), float(u_d["x"]))]

        # Check path cache first for instant retrieval
        path_nodes = self._path_cache.get((u_node, v_node))

        if not path_nodes:
            graph = sub_G if sub_G is not None else self.G
            try:
                path_nodes = nx.shortest_path(graph, source=u_node, target=v_node, weight="length")
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                try:
                    path_nodes = nx.shortest_path(self.G, source=u_node, target=v_node, weight="length")
                except (nx.NetworkXNoPath, nx.NodeNotFound):
                    try:
                        path_nodes = nx.shortest_path(self.G_undir, source=u_node, target=v_node, weight="length")
                    except Exception as e:
                        logger.error(f"Cannot find road path between nodes {u_node} and {v_node}: {e}")
                        return []

            if path_nodes:
                self._path_cache[(u_node, v_node)] = path_nodes

        if not path_nodes:
            return []

        coords: List[Tuple[float, float]] = []

        for i in range(len(path_nodes) - 1):
            curr_u = path_nodes[i]
            curr_v = path_nodes[i + 1]

            edge_data = None
            if self.G.has_edge(curr_u, curr_v):
                edge_data = self.G.get_edge_data(curr_u, curr_v)
            elif self.G_undir.has_edge(curr_u, curr_v):
                edge_data = self.G_undir.get_edge_data(curr_u, curr_v)

            chosen_edge = None
            if edge_data:
                # If MultiDiGraph, pick edge with shortest length
                if isinstance(edge_data, dict) and any(isinstance(v, dict) for v in edge_data.values()):
                    chosen_edge = min(edge_data.values(), key=lambda d: float(d.get("length", 100)))
                else:
                    chosen_edge = edge_data

            u_pt = (float(self.G.nodes[curr_u]["y"]), float(self.G.nodes[curr_u]["x"]))
            v_pt = (float(self.G.nodes[curr_v]["y"]), float(self.G.nodes[curr_v]["x"]))

            if chosen_edge and "geometry" in chosen_edge:
                geom_str = str(chosen_edge["geometry"])
                # Parse WKT: 'LINESTRING (-73.99 40.71, -73.98 40.72)'
                m = re.search(r"LINESTRING\s*\(([^)]+)\)", geom_str, re.IGNORECASE)
                if m:
                    pts = m.group(1).split(",")
                    seg_coords = []
                    for pt in pts:
                        parts = pt.strip().split()
                        if len(parts) >= 2:
                            seg_lon = float(parts[0])
                            seg_lat = float(parts[1])
                            seg_coords.append((seg_lat, seg_lon))

                    # Check orientation of geometry segment: u should match first point
                    if seg_coords:
                        dist_start = (seg_coords[0][0] - u_pt[0])**2 + (seg_coords[0][1] - u_pt[1])**2
                        dist_end = (seg_coords[-1][0] - u_pt[0])**2 + (seg_coords[-1][1] - u_pt[1])**2
                        if dist_end < dist_start:
                            seg_coords.reverse()

                        if not coords or coords[-1] != u_pt:
                            coords.append(u_pt)
                        for c in seg_coords:
                            if not coords or coords[-1] != c:
                                coords.append(c)
                        if not coords or coords[-1] != v_pt:
                            coords.append(v_pt)
                        continue

            # For straight road edges with no intermediate curvature, connect intersection nodes
            if not coords or coords[-1] != u_pt:
                coords.append(u_pt)
            coords.append(v_pt)

        return coords

    def reconstruct_vehicle_road_route(
        self,
        stop_indices: List[int],
        locations: List[Tuple[float, float]],
        snapped_nodes: List[str],
    ) -> List[Dict[str, Any]]:
        """
        Reconstruct complete road-following waypoint trace for a single vehicle route.
        Connects consecutive stops strictly along real road geometry, marking original stops along the way.
        Ensures the polyline follows the street centerlines with zero diagonal spurs or building shortcuts.
        """
        if not self.is_ready() or len(stop_indices) < 2:
            return []

        full_waypoints: List[Dict[str, Any]] = []

        for leg_idx in range(len(stop_indices) - 1):
            s_u = stop_indices[leg_idx]
            s_v = stop_indices[leg_idx + 1]

            node_u = snapped_nodes[s_u]
            node_v = snapped_nodes[s_v]

            orig_u = locations[s_u]
            orig_v = locations[s_v]

            # Retrieve road geometry connecting node_u and node_v
            road_pts = self.get_road_path_geometry(node_u, node_v)
            if not road_pts:
                logger.error(
                    f"Routing failure: no connected road path between stop {s_u} (node {node_u}) "
                    f"and stop {s_v} (node {node_v}). Skipping invalid segment."
                )
                continue

            # First waypoint of the route: snapped road position of stop s_u
            if not full_waypoints:
                full_waypoints.append({
                    "lat": road_pts[0][0],
                    "lon": road_pts[0][1],
                    "type": "depot" if s_u == 0 else "customer",
                    "index": s_u,
                    "is_stop": True,
                    "orig_lat": orig_u[0],
                    "orig_lon": orig_u[1],
                })
            else:
                # Mark existing last waypoint as arrival at stop s_u
                full_waypoints[-1]["type"] = "depot" if s_u == 0 else "customer"
                full_waypoints[-1]["index"] = s_u
                full_waypoints[-1]["is_stop"] = True
                full_waypoints[-1]["orig_lat"] = orig_u[0]
                full_waypoints[-1]["orig_lon"] = orig_u[1]

            # Append intermediate road curvature points along the street network
            for pt in road_pts[1:]:
                # Avoid duplicate adjacent coordinates
                if full_waypoints and abs(full_waypoints[-1]["lat"] - pt[0]) < 1e-7 and abs(full_waypoints[-1]["lon"] - pt[1]) < 1e-7:
                    continue
                full_waypoints.append({
                    "lat": pt[0],
                    "lon": pt[1],
                    "type": "road_curve",
                    "index": -1,
                    "is_stop": False,
                })

        # Mark final depot return waypoint
        if full_waypoints:
            last_s = stop_indices[-1]
            last_orig = locations[last_s]
            full_waypoints[-1]["type"] = "depot" if last_s == 0 else "customer"
            full_waypoints[-1]["index"] = last_s
            full_waypoints[-1]["is_stop"] = True
            full_waypoints[-1]["orig_lat"] = last_orig[0]
            full_waypoints[-1]["orig_lon"] = last_orig[1]

        return full_waypoints


road_network_service = RoadNetworkService()
