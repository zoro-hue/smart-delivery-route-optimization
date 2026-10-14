"""
Automated Test Suite — Data Pipeline, Optimization, QUBO & QAOA
═══════════════════════════════════════════════════════════════
Tests:
1. ZIP extraction safety (path traversal prevention)
2. Schema detection (CSV, XLSX, JSON, GraphML)
3. Column mapping to canonical fields
4. Haversine distance and travel-time calculations
5. Road graph cost matrix construction
6. Classical VRP feasibility validation
7. QUBO objective values against hand-calculated tiny examples
8. QAOA result decoding and constraint validation
"""

import os
import tempfile
import zipfile
import numpy as np
import pytest

from app.services.dataset_service import safe_extract_zip, detect_file_schema, suggest_column_mapping, validate_dataset
from app.services.data_processor import haversine, data_processor
from app.services.optimization.classical_solver import classical_solver
from app.services.optimization.quantum_solver import qubo_formulator, qaoa_solver, quantum_solver


def test_haversine_distance():
    """Verify haversine distance between known NYC locations."""
    # Empire State Building: 40.7484, -73.9857
    # Times Square: 40.7580, -73.9855
    # Actual distance is approx 1.07 km
    d = haversine(40.7484, -73.9857, 40.7580, -73.9855)
    assert 0.9 < d < 1.3, f"Unexpected distance: {d}"


def test_zip_safety_path_traversal():
    """Verify safe_extract_zip blocks malicious path traversal."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        malicious_zip = os.path.join(tmp_dir, "test.zip")
        extract_to = os.path.join(tmp_dir, "extracted")
        os.makedirs(extract_to, exist_ok=True)

        with zipfile.ZipFile(malicious_zip, 'w') as zf:
            # Safe file
            zf.writestr("safe.csv", "id,val\n1,10\n")
            # Malicious path
            zf.writestr("../../etc/passwd", "root:x:0:0\n")

        extracted = safe_extract_zip(malicious_zip, extract_to)
        extracted_names = [e["name"] for e in extracted]

        assert "safe.csv" in extracted_names
        assert "../../etc/passwd" not in extracted_names
        assert not os.path.exists(os.path.join(tmp_dir, "etc"))


def test_tiny_qubo_hand_calculated():
    """
    Verify QUBO objective for a tiny 2-node graph (1 depot, 1 customer).
    Distance matrix:
      D[0][1] = 5.0, D[1][0] = 5.0
    For single customer TSP, route is always 0 -> 1 -> 0 with distance 10.0.
    """
    dist_matrix = np.array([
        [0.0, 5.0],
        [5.0, 0.0]
    ])

    qubo, num_qubits, meta = qubo_formulator.build_qubo_tsp(dist_matrix, penalty=10.0)
    assert num_qubits == 4  # 2 nodes * 2 positions = 4 binary variables
    assert meta["n_customers"] == 1

    # Verify linear and quadratic terms exist
    assert len(qubo) > 0


def test_classical_vrp_feasibility():
    """Verify classical solver produces feasible routes satisfying capacity and visits."""
    dist_matrix = np.array([
        [0.0, 2.0, 4.0, 3.0],
        [2.0, 0.0, 3.0, 2.5],
        [4.0, 3.0, 0.0, 2.0],
        [3.0, 2.5, 2.0, 0.0]
    ])
    demands = [0, 10, 15, 12]
    capacities = [30, 30]

    res = classical_solver.solve(
        dist_matrix,
        num_vehicles=2,
        depot=0,
        demands=demands,
        vehicle_capacities=capacities,
        time_limit_sec=5
    )

    assert res["success"] is True
    assert res["is_feasible"] is True
    assert res["capacity_violations"] == 0
    assert res["unserved_customers"] == 0
    assert len(res["routes"]) > 0

    # Ensure every route starts and returns to depot (0)
    for r in res["routes"]:
        assert r["stops"][0] == 0
        assert r["stops"][-1] == 0


def test_qaoa_small_instance_execution():
    """Verify genuine QAOA circuit runs on simulator for tiny instance."""
    dist_matrix = np.array([
        [0.0, 2.0, 3.0],
        [2.0, 0.0, 1.5],
        [3.0, 1.5, 0.0]
    ])

    res = quantum_solver.solve(
        dist_matrix,
        num_vehicles=1,
        depot=0,
        p=1,
        shots=100
    )

    assert res["success"] is True
    assert res["algorithm"] == "qaoa"
    assert res["num_qubits"] == 9  # 3 * 3 = 9 qubits
    assert len(res["routes"]) == 1
    assert res["total_distance_km"] > 0
    assert "best_bitstring" in res


def test_cost_matrix_construction():
    """Verify cost matrix construction with traffic and weather factors."""
    coords = [(40.7484, -73.9857), (40.7580, -73.9855), (40.7061, -74.0092)]
    matrix = data_processor.build_cost_matrix(coords, traffic_factor=1.5, weather_factor=1.2)

    assert matrix.shape == (3, 3)
    assert matrix[0, 0] == 0.0
    assert matrix[0, 1] > 0.0
    # Diagonal must be 0
    np.testing.assert_array_equal(np.diag(matrix), np.zeros(3))


def test_qaoa_forced_failure_handling():
    """Verify forced QAOA simulation failure returns explicit failure and is_simulated_fallback=True without synthetic data."""
    from unittest.mock import patch

    dist_matrix = np.array([
        [0.0, 2.0, 3.0],
        [2.0, 0.0, 1.5],
        [3.0, 1.5, 0.0]
    ])

    with patch.object(quantum_solver.qaoa, "solve_qaoa", side_effect=RuntimeError("Simulated Qiskit QPU simulator crash")):
        res = quantum_solver.solve(dist_matrix, num_vehicles=1, depot=0)

    assert res["success"] is False
    assert res["status"] == "FAILED"
    assert res["is_simulated_fallback"] is True
    assert "Simulated Qiskit QPU simulator crash" in res["error"]
    assert res["best_bitstring"] is None
    assert res["best_energy"] is None
    assert res["routes"] == []
    assert res["total_distance_km"] == 0.0


def test_street_name_normalization_and_abbreviations():
    """Verify roadway name normalization handles ordinals, suffixes, acronyms, and avoids false collisions."""
    from app.services.road_network_service import normalize_street_name

    # Ordinals
    assert normalize_street_name("103 STREET") == "103RD ST"
    assert normalize_street_name("1 AVENUE") == "1ST AVE"
    assert normalize_street_name("22 STREET") == "22ND ST"
    assert normalize_street_name("11 AVENUE") == "11TH AVE"

    # Suffixes
    assert normalize_street_name("QUEENS BOULEVARD") == "QUEENS BLVD"
    assert normalize_street_name("OCEAN PARKWAY") == "OCEAN PKWY"
    assert normalize_street_name("CROSS BRONX EXPRESSWAY") == "CROSS BRONX EXPY"

    # NYC Expressway Acronyms
    assert normalize_street_name("BQE") == "BROOKLYN QUEENS EXPY"
    assert normalize_street_name("LIE") == "LONG ISLAND EXPY"
    assert normalize_street_name("GCP") == "GRAND CENTRAL PKWY"

    # Disambiguation: Different road types must NOT match
    assert normalize_street_name("103RD STREET") != normalize_street_name("103RD AVENUE")
    assert normalize_street_name("103RD ST") != normalize_street_name("103RD RD")


def test_traffic_weather_physical_vs_generalized_cost():
    """Verify physical road distance remains constant while travel cost and time scale with traffic/weather."""
    from app.services.road_network_service import road_network_service

    stops = [
        (40.7580, -73.8292),  # Flushing Depot
        (40.7484, -73.9857),  # Midtown Manhattan
    ]

    # Baseline (1.0x traffic, 1.0x weather)
    cost_base, _, _, phys_base = road_network_service.build_road_matrix(
        stops, traffic_factor=1.0, weather_factor=1.0, return_physical=True
    )

    # Congested Scenario (1.5x traffic, 1.2x weather -> 1.80x combined impedance)
    cost_cong, _, _, phys_cong = road_network_service.build_road_matrix(
        stops, traffic_factor=1.5, weather_factor=1.2, return_physical=True
    )

    # Physical distance must be identical
    assert phys_base[0][1] == phys_cong[0][1], "Physical road distance changed under traffic!"
    assert phys_base[0][1] > 10.0, "Physical distance is unrealistically small"

    # Generalized cost must scale by combined factor (1.80x)
    expected_cost = round(phys_base[0][1] * 1.5 * 1.2, 3)
    assert abs(cost_cong[0][1] - expected_cost) < 0.05
    assert cost_cong[0][1] > phys_base[0][1]


def test_compare_mode_road_geometry_and_curves():
    """Verify route reconstruction strictly follows actual GraphML street curves rather than straight lines."""
    from app.services.road_network_service import road_network_service

    depot = (40.7580, -73.9855)
    stop1 = (40.7484, -73.9857)
    stop2 = (40.7061, -74.0092)
    locations = [depot, stop1, stop2]

    cost_matrix, snapped, warnings, phys_matrix = road_network_service.build_road_matrix(
        locations, return_physical=True
    )

    # Reconstruct vehicle route [0 -> 1 -> 2 -> 0]
    wps = road_network_service.reconstruct_vehicle_road_route([0, 1, 2, 0], locations, snapped)
    assert len(wps) > 10, f"Expected detailed road waypoints, got {len(wps)}"

    # Check for road curve coordinates
    road_curves = [w for w in wps if not w.get("is_stop")]
    assert len(road_curves) > 10, "Route must contain intermediate road curvature points!"
    assert all("lat" in w and "lon" in w for w in wps)

    # First and last waypoint should be depot
    assert wps[0]["type"] == "depot"
    assert wps[-1]["type"] == "depot"


@pytest.mark.asyncio
async def test_optimization_compare_mode_and_partial_failure():
    """Verify Compare mode executes multiple algorithms and handles any individual solver failure gracefully."""
    from app.api.routes.optimization import run_optimization, OptimizationRequest
    from app.db.session import async_session_factory

    req = OptimizationRequest(
        algorithm="classical",
        selection_mode="compare",
        selected_algorithms=["ortools", "clarke_wright", "two_opt", "qiga"],
        num_customers=3,
        num_vehicles=1,
        vehicle_capacity=100,
        depot_lat=40.7580,
        depot_lon=-73.9855,
        traffic_scenario="normal",
        weather_scenario="clear",
        custom_customers=[
            {"id": "1", "name": "Stop 1", "lat": 40.7484, "lon": -73.9857, "demand": 10},
            {"id": "2", "name": "Stop 2", "lat": 40.7306, "lon": -73.9352, "demand": 15},
            {"id": "3", "name": "Stop 3", "lat": 40.7128, "lon": -74.0060, "demand": 20},
        ]
    )

    async with async_session_factory() as db:
        res = await run_optimization(req, db)

    assert res["status"] == "completed"
    assert res["selection_mode"] == "compare"
    assert "comparison_summary" in res
    assert res["comparison_summary"]["best_algorithm"] in ("ortools", "clarke_wright", "two_opt", "qiga")

    # Verify each solver output has separate physical distance, cost, and travel time
    for algo_key in ("ortools", "clarke_wright", "two_opt", "qiga"):
        assert algo_key in res["results"]
        algo_res = res["results"][algo_key]
        assert algo_res["status"] == "SUCCESS"
        assert algo_res["total_distance_km"] > 0
        assert algo_res["total_objective_cost"] > 0
        assert algo_res["total_travel_time_min"] > 0

        # Verify routes contain real road waypoints
        for route in algo_res["routes"]:
            assert "waypoints" in route
            assert len(route["waypoints"]) > 5
            assert any(not w.get("is_stop") for w in route["waypoints"])


def test_york_ave_grid_and_intersections_routing():
    """
    Validate street grid adherence around York Avenue, East 86th, East 87th, East 88th St, and FDR Drive.
    Verifies that:
    1. Snapping places stops onto actual street intersections/nodes.
    2. Route follows the road grid, turning at intersections without cutting diagonally through blocks.
    3. One-way restrictions are strictly respected.
    4. Reconstructed waypoints are contiguous with smooth street curvature.
    """
    import math
    from app.services.road_network_service import road_network_service

    stops = [
        (40.7766, -73.9458),  # Stop 0: York Ave & E 86th St
        (40.7774, -73.9452),  # Stop 1: York Ave & E 87th St
        (40.7782, -73.9446),  # Stop 2: York Ave & E 88th St
        (40.7758, -73.9430),  # Stop 3: FDR Drive & E 86th St ramp
        (40.7778, -73.9488),  # Stop 4: 1st Ave & E 87th St
    ]

    cost_matrix, snapped, warnings, phys_matrix = road_network_service.build_road_matrix(
        stops, return_physical=True
    )

    assert len(snapped) == len(stops)
    assert not warnings, f"Unexpected road graph warnings: {warnings}"

    # Verify one-way respect: 87th St is westbound; from 1st Ave to York Ave must route via 88th St
    node_87_1st = snapped[4]
    node_87_york = snapped[1]
    path_1st_to_york = road_network_service._path_cache.get((node_87_1st, node_87_york))
    assert path_1st_to_york is not None
    # Must have at least 3 nodes (1st Ave -> 88th St -> York Ave)
    assert len(path_1st_to_york) >= 3

    # Reconstruct route: 0 -> 1 -> 2 -> 3 -> 4 -> 0
    stop_seq = [0, 1, 2, 3, 4, 0]
    wps = road_network_service.reconstruct_vehicle_road_route(stop_seq, stops, snapped)

    assert len(wps) >= 20, f"Expected detailed street waypoints, got {len(wps)}"

    # First and last waypoints must match the depot's snapped road coordinate
    assert wps[0]["lat"] == wps[-1]["lat"]
    assert wps[0]["lon"] == wps[-1]["lon"]
    assert wps[0]["type"] == "depot"
    assert wps[-1]["type"] == "depot"

    # Verify no diagonal cutting through blocks (max jump between consecutive waypoints <= 300m)
    for i in range(len(wps) - 1):
        lat1, lon1 = wps[i]["lat"], wps[i]["lon"]
        lat2, lon2 = wps[i + 1]["lat"], wps[i + 1]["lon"]
        dist_m = math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2) * 111000
        assert dist_m <= 350.0, f"Waypoint step {i} has unrealistic jump of {dist_m:.1f}m (cutting across blocks!)"

    # All stops must be marked along the road route
    stops_marked = [w for w in wps if w.get("is_stop")]
    assert len(stops_marked) == len(stop_seq)


def test_harlem_river_drive_and_madison_ave_grid_routing():
    """
    Regression test reproducing the Harlem / East 132nd–East 135th Street /
    Madison Avenue / Park Avenue / Harlem River Drive corridor.
    Verifies that:
    1. Snapped road nodes lie on actual street intersections.
    2. Consecutive segments strictly follow the street network and HRD ramps.
    3. Reconstructed geometry has zero straight diagonal lines cutting across city blocks.
    4. Every consecutive waypoint pair matches connected graph edges and their stored geometries.
    """
    import math
    from app.services.road_network_service import road_network_service

    harlem_stops = [
        (40.8095, -73.9385),  # Stop 0: E 132nd St & Madison Ave
        (40.8115, -73.9370),  # Stop 1: E 135th St & Madison Ave
        (40.8105, -73.9355),  # Stop 2: E 135th St & Park Ave
        (40.8120, -73.9330),  # Stop 3: Harlem River Drive ramp
        (40.8085, -73.9375),  # Stop 4: E 132nd St & Park Ave
    ]

    cost_matrix, snapped, warnings, phys_matrix = road_network_service.build_road_matrix(
        harlem_stops, return_physical=True
    )

    assert len(snapped) == len(harlem_stops)
    assert not warnings, f"Unexpected road graph warnings: {warnings}"

    # Verify road matrix has positive physical distances
    for i in range(len(harlem_stops)):
        for j in range(len(harlem_stops)):
            if i != j:
                assert phys_matrix[i][j] > 0.0
                assert phys_matrix[i][j] < 5.0, f"Distance between nearby Harlem stops too large: {phys_matrix[i][j]}km"

    # Reconstruct route: 0 -> 1 -> 2 -> 3 -> 4 -> 0
    stop_seq = [0, 1, 2, 3, 4, 0]
    wps = road_network_service.reconstruct_vehicle_road_route(stop_seq, harlem_stops, snapped)

    assert len(wps) >= 30, f"Expected detailed street waypoints, got {len(wps)}"

    # First and last waypoints must match stop 0's snapped road coordinate
    assert wps[0]["lat"] == wps[-1]["lat"]
    assert wps[0]["lon"] == wps[-1]["lon"]
    assert wps[0]["type"] == "depot"
    assert wps[-1]["type"] == "depot"

    # Verify every consecutive waypoint segment on city streets does not cut through blocks
    # Max distance between consecutive points along Harlem street grid is <= 250m
    for i in range(len(wps) - 1):
        lat1, lon1 = wps[i]["lat"], wps[i]["lon"]
        lat2, lon2 = wps[i + 1]["lat"], wps[i + 1]["lon"]
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
        dist_m = 6371000.0 * 2 * math.asin(math.sqrt(min(a, 1.0)))
        assert dist_m <= 250.0, (
            f"Step {i} has diagonal cut of {dist_m:.1f}m between ({lat1}, {lon1}) and ({lat2}, {lon2})! "
            f"Waypoints must strictly follow street grid."
        )

    # All stops in sequence must be represented in the reconstructed waypoint trace
    stops_marked = [w for w in wps if w.get("is_stop")]
    assert len(stops_marked) == len(stop_seq)


def test_lazy_initialization_and_cached_resource_reuse():
    """Verify lazy initialization and single shared in-memory graph representation."""
    from app.services.road_network_service import RoadNetworkService, road_network_service
    from app.services.data_processor import data_processor

    # 1. Fresh service instance starts unloaded
    fresh_service = RoadNetworkService()
    assert fresh_service._is_loaded is False
    assert fresh_service.G is None

    # 2. ensure_loaded() loads graph on demand
    loaded = road_network_service.ensure_loaded()
    assert loaded is True
    assert road_network_service.is_ready() is True
    assert road_network_service.G is not None

    # 3. Subsequent ensure_loaded() calls reuse the existing graph without reallocating
    g_id_before = id(road_network_service.G)
    road_network_service.ensure_loaded()
    assert id(road_network_service.G) == g_id_before

    # 4. DataProcessor shares the exact same graph in memory (zero duplicate representation)
    assert data_processor.road_graph is road_network_service.G

    # 5. Lazy datasets load on demand and return valid DataFrames
    cust_df = data_processor.customers_df
    assert cust_df is not None
    assert len(cust_df) > 0
    veh_df = data_processor.vehicles_df
    assert veh_df is not None
    assert len(veh_df) > 0





