"""
ROUTE/IQ Next-Generation Diverse Initial Construction Heuristics Library.
Provides multi-heuristic initial fleet candidate generation:
1. Multi-parameter Clarke-Wright Savings (shape parameter gamma in [0.6, 0.8, 1.0, 1.2, 1.4, 1.6]).
2. Spark Polar Angle Sweep Construction (12 angular offsets, clockwise and counter-clockwise).
3. Regret-2 and Regret-3 Initial Route Construction.
4. Cheapest Feasible Insertion Construction.
"""

import math
import copy
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
            gammas = [0.6, 0.8, 1.0, 1.2, 1.4, 1.6]

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
        num_rotations: int = 12,
    ) -> List[List[int]]:
        """
        Spark polar sweep clustering:
        Orders customers by polar angle relative to the depot and clusters into vehicle routes.
        Tries multiple angular offsets and directions to find the best angular partition.
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

        for direction in (1, -1):
            base_angles = angles if direction == 1 else angles[::-1]
            for offset in offsets:
                rot_angles = base_angles[offset:] + base_angles[:offset]
                routes = [[] for _ in range(num_vehicles)]
                v_idx = 0
                cur_load = 0
                feasible = True
                target_per_veh = max(1, math.ceil(len(rot_angles) / num_vehicles))

                for idx_c, (_, c) in enumerate(rot_angles):
                    rem_c = len(rot_angles) - idx_c
                    rem_v = num_vehicles - 1 - v_idx
                    cap_v = capacities[v_idx] if v_idx < len(capacities) else 100.0
                    should_advance = (v_idx < num_vehicles - 1) and (
                        (rem_c <= rem_v and len(routes[v_idx]) > 0) or
                        (len(routes[v_idx]) >= target_per_veh and cur_load > 0 and rem_v > 0) or
                        (cur_load + demands[c] > cap_v)
                    )
                    if should_advance:
                        v_idx += 1
                        cur_load = 0
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

                if feasible and any(len(r) > 0 for r in routes):
                    # Check all customers visited
                    visited = [c for r in routes for c in r]
                    if len(visited) == n - 1:
                        opt_routes = AdvancedNeighborhoodSearch.deep_vnd(
                            routes, capacities, demands, dist_matrix, depot
                        )
                        c_cost = RouteEvaluator.fleet_distance(opt_routes, dist_matrix, depot)
                        if c_cost < best_cost:
                            best_cost = c_cost
                            best_routes = opt_routes

        if best_routes:
            target_active = min(num_vehicles, n - 1)
            for _ in range(target_active * 2):
                empty_r = [i for i in range(target_active) if len(best_routes[i]) == 0]
                if not empty_r:
                    break
                donor_idx = max(range(target_active), key=lambda i: len(best_routes[i]))
                if len(best_routes[donor_idx]) < 2:
                    break
                moved_c = best_routes[donor_idx].pop()
                best_routes[empty_r[0]].append(moved_c)

        return best_routes or [[] for _ in range(num_vehicles)]

    @classmethod
    def regret_k_construction(
        cls,
        dist_matrix: np.ndarray,
        num_vehicles: int,
        depot: int,
        demands: List[int],
        capacities: List[float],
        k_regret: int = 2,
    ) -> List[List[int]]:
        """
        Constructs a complete CVRP solution using Regret-k (k=2 or k=3) insertion.
        Initializes vehicles with seeds chosen to maximize mutual separation from depot.
        """
        n = dist_matrix.shape[0]
        customers = [i for i in range(n) if i != depot]
        if not customers:
            return [[] for _ in range(num_vehicles)]

        routes = [[] for _ in range(num_vehicles)]
        unassigned = list(customers)

        # Seed initial vehicles with nodes farthest from depot and mutually separated
        unassigned.sort(key=lambda c: dist_matrix[depot, c], reverse=True)
        for v in range(min(num_vehicles, len(unassigned))):
            if v == 0:
                seed_c = unassigned[0]
            else:
                # Pick node maximizing minimum distance to already seeded vehicles
                already_seeded = [routes[i][0] for i in range(v) if routes[i]]
                seed_c = max(
                    unassigned,
                    key=lambda c: min(dist_matrix[c, s] for s in already_seeded),
                )
            cap_v = capacities[v] if v < len(capacities) else 100.0
            if demands[seed_c] <= cap_v:
                routes[v].append(seed_c)
                unassigned.remove(seed_c)

        # Regret-k iterative insertion
        while unassigned:
            best_cust = None
            max_regret = -float("inf")
            best_v = None
            best_pos = None

            for c in unassigned:
                ins_costs = []
                for v in range(num_vehicles):
                    r = routes[v]
                    cap_v = capacities[v] if v < len(capacities) else 100.0
                    if sum(demands[k] for k in r) + demands[c] <= cap_v:
                        c_r = RouteEvaluator.tour_length(r, dist_matrix, depot)
                        best_i_c, best_i_p = float("inf"), 0
                        for pos in range(len(r) + 1):
                            cand = r[:pos] + [c] + r[pos:]
                            del_c = RouteEvaluator.tour_length(cand, dist_matrix, depot) - c_r
                            if del_c < best_i_c:
                                best_i_c, best_i_p = del_c, pos
                        ins_costs.append((best_i_c, v, best_i_p))

                if not ins_costs:
                    continue

                ins_costs.sort(key=lambda x: x[0])
                if k_regret == 3 and len(ins_costs) >= 3:
                    regret = (ins_costs[1][0] - ins_costs[0][0]) + (ins_costs[2][0] - ins_costs[0][0])
                elif len(ins_costs) >= 2:
                    regret = ins_costs[1][0] - ins_costs[0][0]
                else:
                    regret = ins_costs[0][0] * 2.0

                if regret > max_regret:
                    max_regret = regret
                    best_cust = c
                    best_v = ins_costs[0][1]
                    best_pos = ins_costs[0][2]

            if best_cust is not None:
                routes[best_v].insert(best_pos, best_cust)
                unassigned.remove(best_cust)
            else:
                # Find vehicle with least load and add
                for c in list(unassigned):
                    min_v = min(range(num_vehicles), key=lambda idx: sum(demands[k] for k in routes[idx]))
                    routes[min_v].append(c)
                    unassigned.remove(c)

        return AdvancedNeighborhoodSearch.deep_vnd(routes, capacities, demands, dist_matrix, depot)
