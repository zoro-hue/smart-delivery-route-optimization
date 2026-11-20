"""
ROUTE/IQ Diverse Initial Construction Heuristics Library.
Provides multi-heuristic initial fleet candidate generation:
1. Multi-parameter Clarke-Wright Savings (shape parameter gamma in [0.8, 1.0, 1.2, 1.4]).
2. Spark Polar Angle Sweep Construction (angular wedge partitioning around depot).
3. Regret-2 Insertion Construction.
"""

import math
from typing import List, Tuple, Dict, Any, Optional
import numpy as np

from app.services.optimization.neighborhood_search import (
    RouteEvaluator,
    AdvancedNeighborhoodSearch,
)


class DiverseConstructionHeuristics:
    """Diverse initial fleet route construction generators."""

    @classmethod
    def clarke_wright_savings_pool(
        cls,
        dist_matrix: np.ndarray,
        num_vehicles: int,
        depot: int,
        demands: List[int],
        capacities: List[float],
        gammas: Optional[List[float]] = None,
    ) -> List[List[List[int]]]:
        """
        Generates fleet routes using parameterized Clarke-Wright savings.
        Varying gamma changes the weighting between depot distances and customer distances.
        """
        n = dist_matrix.shape[0]
        if gammas is None:
            gammas = [0.8, 1.0, 1.2, 1.4]

        candidates = []
        max_cap = max(capacities) if capacities else 100.0

        for gamma in gammas:
            savings = []
            for i in range(1, n):
                for j in range(i + 1, n):
                    s = dist_matrix[depot, i] + dist_matrix[depot, j] - gamma * dist_matrix[i, j]
                    savings.append((s, i, j))
            savings.sort(key=lambda x: x[0], reverse=True)

            routes = [[i] for i in range(1, n)]
            node_to_route = {i: i for i in range(1, n)}

            for _, i, j in savings:
                r_i = node_to_route[i]
                r_j = node_to_route[j]
                if r_i == r_j:
                    continue

                route_i = None
                route_j = None
                for r in routes:
                    if r and (r[0] == r_i or i in r):
                        route_i = r
                    if r and (r[0] == r_j or j in r):
                        route_j = r
                if route_i is None or route_j is None or route_i == route_j:
                    continue

                if sum(demands[k] for k in route_i) + sum(demands[k] for k in route_j) > max_cap:
                    continue

                if route_i[-1] == i and route_j[0] == j:
                    merged = route_i + route_j
                elif route_i[0] == i and route_j[-1] == j:
                    merged = route_j + route_i
                elif route_i[-1] == i and route_j[-1] == j:
                    merged = route_i + route_j[::-1]
                elif route_i[0] == i and route_j[0] == j:
                    merged = route_i[::-1] + route_j
                else:
                    continue

                routes.remove(route_i)
                routes.remove(route_j)
                routes.append(merged)
                for node in merged:
                    node_to_route[node] = merged[0]

            # Merge if more routes than available vehicles
            while len(routes) > num_vehicles:
                routes.sort(key=lambda r: sum(demands[k] for k in r))
                merged_any = False
                for a_idx in range(len(routes)):
                    for b_idx in range(a_idx + 1, len(routes)):
                        if sum(demands[k] for k in routes[a_idx]) + sum(demands[k] for k in routes[b_idx]) <= max_cap:
                            routes[a_idx] = routes[a_idx] + routes[b_idx]
                            routes.pop(b_idx)
                            merged_any = True
                            break
                    if merged_any:
                        break
                if not merged_any:
                    break

            while len(routes) < num_vehicles:
                routes.append([])

            if len(routes) == num_vehicles:
                opt_routes = AdvancedNeighborhoodSearch.deep_vnd(
                    routes, capacities, demands, dist_matrix, depot
                )
                candidates.append(opt_routes)

        return candidates

    @classmethod
    def spark_polar_sweep(
        cls,
        locations: List[Tuple[float, float]],
        num_vehicles: int,
        depot: int,
        demands: List[int],
        capacities: List[float],
        dist_matrix: np.ndarray,
        num_rotations: int = 8,
    ) -> List[List[int]]:
        """
        Spark polar sweep clustering:
        Orders customers by polar angle relative to the depot and clusters into vehicle routes.
        Tries multiple angular offsets to find the best angular partition.
        """
        n = len(locations)
        depot_loc = locations[depot]

        angles = []
        for c in range(n):
            if c == depot:
                continue
            lat, lon = locations[c]
            ang = math.atan2(lat - depot_loc[0], lon - depot_loc[1])
            angles.append((ang, c))
        angles.sort(key=lambda x: x[0])

        step = max(1, len(angles) // num_rotations)
        offsets = range(0, len(angles), step)

        best_routes = None
        best_cost = float("inf")

        for offset in offsets:
            rot_angles = angles[offset:] + angles[:offset]
            routes = [[] for _ in range(num_vehicles)]
            v_idx = 0
            cur_load = 0
            feasible = True

            for _, c in rot_angles:
                cap_v = capacities[v_idx] if v_idx < len(capacities) else 100.0
                if cur_load + demands[c] <= cap_v:
                    routes[v_idx].append(c)
                    cur_load += demands[c]
                else:
                    v_idx += 1
                    if v_idx >= num_vehicles:
                        feasible = False
                        break
                    routes[v_idx].append(c)
                    cur_load = demands[c]

            if feasible and all(len(r) > 0 for r in routes):
                opt_routes = AdvancedNeighborhoodSearch.deep_vnd(
                    routes, capacities, demands, dist_matrix, depot
                )
                c_cost = RouteEvaluator.fleet_distance(opt_routes, dist_matrix, depot)
                if c_cost < best_cost:
                    best_cost = c_cost
                    best_routes = opt_routes

        return best_routes or [[] for _ in range(num_vehicles)]
