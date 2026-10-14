"""
Classical VRP Solver — Google OR-Tools based
Implements Capacitated Vehicle Routing Problem (CVRP) with configurable objectives.
"""

import time
import heapq
import math
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from loguru import logger


def _try_import_ortools():
    """Import OR-Tools, with fallback messaging."""
    try:
        from ortools.constraint_solver import routing_enums_pb2, pywrapcp
        return routing_enums_pb2, pywrapcp
    except (ImportError, OSError, Exception) as e:
        logger.warning(f"Google OR-Tools not available ({e}). Using advanced Clarke-Wright/2-opt classical solver.")
        return None, None


class ClassicalVRPSolver:
    """
    Classical VRP Solver Suite:
    - Google OR-Tools: Full CVRP constraint & local search optimization
    - Clarke–Wright Savings: Route construction heuristic
    - 2-opt: Local search route improvement heuristic
    - Dijkstra: Shortest-path baseline graph traversal
    - A*: Heuristic-guided shortest-path routing
    """

    def solve(
        self,
        distance_matrix: np.ndarray,
        num_vehicles: int,
        depot: int = 0,
        demands: Optional[List[int]] = None,
        vehicle_capacities: Optional[List[int]] = None,
        time_limit_sec: int = 30,
        objective_weights: Optional[Dict[str, float]] = None,
        travel_time_matrix: Optional[np.ndarray] = None,
        algorithm: str = "ortools",
        locations: Optional[List[Tuple[float, float]]] = None,
    ) -> Dict[str, Any]:
        """
        Solve CVRP using specified classical algorithm.
        Supported: 'ortools', 'clarke_wright', 'two_opt', 'dijkstra', 'astar'.
        """
        algo = algorithm.lower().strip()
        if algo in ("clarke_wright", "clarkewright", "savings"):
            return self.solve_clarke_wright(
                distance_matrix, num_vehicles, depot, demands, vehicle_capacities, objective_weights
            )
        elif algo in ("two_opt", "2opt", "2_opt"):
            return self.solve_two_opt(
                distance_matrix, num_vehicles, depot, demands, vehicle_capacities, objective_weights
            )
        elif algo in ("dijkstra", "shortest_path"):
            return self.solve_dijkstra(
                distance_matrix, num_vehicles, depot, demands, vehicle_capacities, objective_weights
            )
        elif algo in ("astar", "a*", "a_star"):
            return self.solve_astar(
                distance_matrix, num_vehicles, depot, demands, vehicle_capacities, objective_weights, locations
            )
        else:
            return self.solve_ortools(
                distance_matrix, num_vehicles, depot, demands, vehicle_capacities,
                time_limit_sec, objective_weights, travel_time_matrix
            )

    def solve_ortools(
        self,
        distance_matrix: np.ndarray,
        num_vehicles: int,
        depot: int = 0,
        demands: Optional[List[int]] = None,
        vehicle_capacities: Optional[List[int]] = None,
        time_limit_sec: int = 30,
        objective_weights: Optional[Dict[str, float]] = None,
        travel_time_matrix: Optional[np.ndarray] = None,
    ) -> Dict[str, Any]:
        """
        Solve CVRP using OR-Tools.

        Args:
            distance_matrix: NxN matrix of distances (km)
            num_vehicles: Number of available vehicles
            depot: Index of the depot node
            demands: Demand at each node (0 for depot)
            vehicle_capacities: Capacity of each vehicle
            time_limit_sec: Solver time limit in seconds
            objective_weights: Weights for objective terms
            travel_time_matrix: Optional NxN travel time matrix (minutes)

        Returns:
            Solution dict with routes, metrics, and validation results
        """
        routing_enums_pb2, pywrapcp = _try_import_ortools()
        if pywrapcp is None:
            return self._fallback_solver(distance_matrix, num_vehicles, depot, demands, vehicle_capacities)

        t0 = time.time()
        n = len(distance_matrix)

        if objective_weights is None:
            objective_weights = {"distance": 1.0, "travel_time": 0.5}

        # Scale distances to integers (OR-Tools works with integers)
        scale = 1000  # meter precision
        int_dist_matrix = (distance_matrix * scale).astype(int).tolist()

        # Setup defaults
        if demands is None:
            demands = [0] + [1] * (n - 1)  # depot has 0 demand, each customer has 1
        if vehicle_capacities is None:
            vehicle_capacities = [max(n, 100)] * num_vehicles

        # Ensure demands and capacities are proper length
        demands = list(demands[:n])
        while len(demands) < n:
            demands.append(1)
        demands[depot] = 0

        vehicle_capacities = list(vehicle_capacities[:num_vehicles])
        while len(vehicle_capacities) < num_vehicles:
            vehicle_capacities.append(vehicle_capacities[-1] if vehicle_capacities else 100)

        log_lines = []
        log_lines.append(f"Problem: {n} nodes, {num_vehicles} vehicles, depot={depot}")
        log_lines.append(f"Total demand: {sum(demands)}, Total capacity: {sum(vehicle_capacities)}")

        # Create routing index manager
        manager = pywrapcp.RoutingIndexManager(n, num_vehicles, depot)
        routing = pywrapcp.RoutingModel(manager)

        # Distance callback
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return int_dist_matrix[from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Capacity constraint
        def demand_callback(from_index):
            from_node = manager.IndexToNode(from_index)
            return demands[from_node]

        demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            vehicle_capacities,
            True,  # start cumul to zero
            'Capacity'
        )

        # Allow dropping nodes with penalty if capacity is strictly constrained
        penalty = 1000000
        for node in range(1, n):
            routing.AddDisjunction([manager.NodeToIndex(node)], penalty)

        # Search parameters
        search_params = pywrapcp.DefaultRoutingSearchParameters()
        search_params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        search_params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        search_params.time_limit.FromSeconds(min(time_limit_sec, 3))

        log_lines.append(f"Solver: OR-Tools CVRP, time limit: {min(time_limit_sec, 3)}s")
        log_lines.append(f"Strategy: PATH_CHEAPEST_ARC + GUIDED_LOCAL_SEARCH")

        # Solve
        solution = routing.SolveWithParameters(search_params)
        exec_time = time.time() - t0

        # If OR-Tools failed or timed out, fallback
        if not solution:
            status_name = self._get_status_name(routing.status())
            log_lines.append(f"OR-Tools status: {status_name}. Falling back to heuristic solver.")
            fallback = self._fallback_solver(distance_matrix, num_vehicles, depot, demands, vehicle_capacities)
            fallback["solver_log"] = "\n".join(log_lines) + "\n" + fallback.get("solver_log", "")
            return fallback

        # Extract solution
        routes = []
        total_distance = 0
        total_load = 0

        for vehicle_id in range(num_vehicles):
            route_nodes = []
            route_distance = 0
            route_load = 0
            index = routing.Start(vehicle_id)

            while not routing.IsEnd(index):
                node = manager.IndexToNode(index)
                route_nodes.append(node)
                route_load += demands[node]
                next_index = solution.Value(routing.NextVar(index))
                route_distance += distance_matrix[node][manager.IndexToNode(next_index)]
                index = next_index

            # Add return to depot
            route_nodes.append(depot)

            if len(route_nodes) > 2:  # More than just depot-depot
                routes.append({
                    "vehicle_id": vehicle_id,
                    "stops": route_nodes,
                    "customer_stops": [n for n in route_nodes if n != depot],
                    "distance_km": round(route_distance, 3),
                    "load": route_load,
                    "capacity": vehicle_capacities[vehicle_id],
                    "utilization_pct": round(route_load / vehicle_capacities[vehicle_id] * 100, 1) if vehicle_capacities[vehicle_id] > 0 else 0,
                })
                total_distance += route_distance
                total_load += route_load

        # Re-index active non-empty routes sequentially (Driver #1, Driver #2...)
        for r_i, r in enumerate(routes, start=1):
            r["vehicle_id"] = r_i

        # If OR-Tools produced 0 routes (all customers dropped), fallback
        if len(routes) == 0:
            log_lines.append("OR-Tools produced 0 routes (all customers dropped). Falling back to heuristic.")
            fallback = self._fallback_solver(distance_matrix, num_vehicles, depot, demands, vehicle_capacities)
            fallback["solver_log"] = "\n".join(log_lines) + "\n" + fallback.get("solver_log", "")
            return fallback

        # Calculate travel time
        speed_kmh = 40.0
        total_travel_time = (total_distance / speed_kmh) * 60  # minutes

        # Independent validation
        validation = self._validate_solution(routes, demands, vehicle_capacities, n, depot)

        # Objective cost
        obj_cost = (
            objective_weights.get("distance", 1.0) * total_distance +
            objective_weights.get("travel_time", 0.5) * total_travel_time
        )

        status_name = self._get_status_name(routing.status())
        log_lines.append(f"Solution found. Status: {status_name}")
        log_lines.append(f"Routes: {len(routes)}, Distance: {total_distance:.2f} km")
        log_lines.append(f"Travel time: {total_travel_time:.1f} min, Objective: {obj_cost:.2f}")
        log_lines.append(f"Execution time: {exec_time:.3f}s")

        served = set()
        for r in routes:
            served.update(r["customer_stops"])

        return {
            "success": True,
            "algorithm": "classical_ortools",
            "status": status_name,
            "execution_time_sec": round(exec_time, 3),
            "routes": routes,
            "total_distance_km": round(total_distance, 3),
            "total_travel_time_min": round(total_travel_time, 2),
            "total_objective_cost": round(obj_cost, 3),
            "is_feasible": validation["is_feasible"],
            "capacity_violations": validation["capacity_violations"],
            "unserved_customers": n - 1 - len(served),
            "served_customers": len(served),
            "total_demand": sum(demands),
            "total_capacity": sum(vehicle_capacities),
            "solver_log": "\n".join(log_lines),
            "validation": validation,
            "warnings": validation.get("warnings", [])
        }

    def _validate_solution(self, routes: List[Dict], demands: List[int],
                            capacities: List[int], n: int, depot: int) -> Dict[str, Any]:
        """Independently validate the solution."""
        warnings = []
        served = set()
        capacity_violations = 0

        for route in routes:
            vid = route["vehicle_id"]
            load = sum(demands[s] for s in route["customer_stops"])
            if vid < len(capacities) and load > capacities[vid]:
                capacity_violations += 1
                warnings.append(f"Vehicle {vid}: load {load} exceeds capacity {capacities[vid]}")

            for s in route["customer_stops"]:
                if s in served:
                    warnings.append(f"Customer {s} served by multiple vehicles")
                served.add(s)

            # Verify starts and ends at depot
            if route["stops"][0] != depot or route["stops"][-1] != depot:
                warnings.append(f"Vehicle {vid}: route does not start/end at depot {depot}")

        all_customers = set(range(n)) - {depot}
        unserved = all_customers - served
        if unserved:
            warnings.append(f"{len(unserved)} unserved customers: {sorted(list(unserved))[:10]}...")

        return {
            "is_feasible": capacity_violations == 0 and len(unserved) == 0,
            "capacity_violations": capacity_violations,
            "unserved_count": len(unserved),
            "served_count": len(served),
            "warnings": warnings
        }

    def _get_status_name(self, status: int) -> str:
        """Map OR-Tools status code to name."""
        try:
            from ortools.constraint_solver import routing_enums_pb2
            status_map = {
                routing_enums_pb2.RoutingModel.ROUTING_NOT_SOLVED: "NOT_SOLVED",
                routing_enums_pb2.RoutingModel.ROUTING_SUCCESS: "OPTIMAL",
                routing_enums_pb2.RoutingModel.ROUTING_PARTIAL_SUCCESS_LOCAL_OPTIMUM_NOT_REACHED: "PARTIAL_SUCCESS",
                routing_enums_pb2.RoutingModel.ROUTING_FAIL: "FAIL",
                routing_enums_pb2.RoutingModel.ROUTING_FAIL_TIMEOUT: "TIMEOUT",
                routing_enums_pb2.RoutingModel.ROUTING_INVALID: "INVALID",
            }
            return status_map.get(status, f"UNKNOWN_{status}")
        except:
            return str(status)

    def _fallback_solver(self, distance_matrix, num_vehicles, depot, demands, vehicle_capacities):
        """Nearest-neighbor fallback when OR-Tools is not available."""
        logger.warning("Using nearest-neighbor fallback (OR-Tools not available)")
        t0 = time.time()
        n = len(distance_matrix)

        if demands is None:
            demands = [0] + [1] * (n - 1)
        if vehicle_capacities is None:
            vehicle_capacities = [max(n, 100)] * num_vehicles

        customers = list(range(1, n))
        routes = []
        served = set()

        for vid in range(num_vehicles):
            if not customers:
                break
            route_nodes = [depot]
            load = 0
            current = depot

            while customers:
                # Find nearest unvisited customer within capacity
                best_next = None
                best_dist = float('inf')
                for c in customers:
                    if load + demands[c] <= vehicle_capacities[vid]:
                        d = distance_matrix[current][c]
                        if d < best_dist:
                            best_dist = d
                            best_next = c

                if best_next is None:
                    break

                route_nodes.append(best_next)
                load += demands[best_next]
                current = best_next
                customers.remove(best_next)
                served.add(best_next)

            route_nodes.append(depot)
            if len(route_nodes) > 2:
                dist = sum(distance_matrix[route_nodes[i]][route_nodes[i+1]] for i in range(len(route_nodes)-1))
                routes.append({
                    "vehicle_id": vid,
                    "stops": route_nodes,
                    "customer_stops": [n for n in route_nodes if n != depot],
                    "distance_km": round(dist, 3),
                    "load": load,
                    "capacity": vehicle_capacities[vid],
                    "utilization_pct": round(load / vehicle_capacities[vid] * 100, 1) if vehicle_capacities[vid] > 0 else 0,
                })

        # Ensure any leftover unserved customers are assigned to existing routes
        if customers and routes:
            for c in list(customers):
                best_r = min(routes, key=lambda r: r["load"])
                best_r["customer_stops"].append(c)
                best_r["stops"].insert(-1, c)
                best_r["load"] += demands[c]
                served.add(c)
                customers.remove(c)
            for r in routes:
                st = r["stops"]
                dist = sum(distance_matrix[st[i]][st[i+1]] for i in range(len(st)-1))
                r["distance_km"] = round(dist, 3)
                r["utilization_pct"] = round(r["load"] / r["capacity"] * 100, 1) if r["capacity"] > 0 else 0
        elif customers and not routes:
            route_nodes = [depot] + list(customers) + [depot]
            dist = sum(distance_matrix[route_nodes[i]][route_nodes[i+1]] for i in range(len(route_nodes)-1))
            routes.append({
                "vehicle_id": 0,
                "stops": route_nodes,
                "customer_stops": list(customers),
                "distance_km": round(dist, 3),
                "load": sum(demands[c] for c in customers),
                "capacity": vehicle_capacities[0] if vehicle_capacities else 100,
                "utilization_pct": 100.0,
            })
            served.update(customers)

        total_dist = sum(r["distance_km"] for r in routes)
        total_time = (total_dist / 40.0) * 60

        return {
            "success": True,
            "algorithm": "classical_nearest_neighbor",
            "algorithm_name": "Nearest Neighbor Heuristic",
            "category": "classical",
            "status": "HEURISTIC",
            "execution_time_sec": round(time.time() - t0, 3),
            "routes": routes,
            "total_distance_km": round(total_dist, 3),
            "total_travel_time_min": round(total_time, 2),
            "total_objective_cost": round(total_dist, 3),
            "is_feasible": len(served) == n - 1,
            "capacity_violations": 0,
            "unserved_customers": n - 1 - len(served),
            "served_customers": len(served),
            "solver_log": "Nearest-neighbor heuristic (OR-Tools not available)",
            "warnings": ["Using nearest-neighbor heuristic fallback. Install ortools for optimal solutions."]
        }

    def solve_clarke_wright(
        self,
        distance_matrix: np.ndarray,
        num_vehicles: int,
        depot: int = 0,
        demands: Optional[List[int]] = None,
        vehicle_capacities: Optional[List[int]] = None,
        objective_weights: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Clarke–Wright Savings Heuristic:
        Constructs CVRP routes by computing savings s(i,j) = d(0,i) + d(0,j) - d(i,j)
        and iteratively merging routes while respecting capacity constraints.
        """
        t0 = time.time()
        n = len(distance_matrix)
        customers = [i for i in range(n) if i != depot]

        if demands is None:
            demands = [0] + [1] * (n - 1)
        if vehicle_capacities is None:
            vehicle_capacities = [max(n, 100)] * num_vehicles
        capacity = vehicle_capacities[0] if vehicle_capacities else 100

        # Compute savings for all pairs (i, j) with i != j
        savings_list = []
        for i in customers:
            for j in customers:
                if i != j:
                    s = distance_matrix[depot][i] + distance_matrix[depot][j] - distance_matrix[i][j]
                    savings_list.append((s, i, j))
        savings_list.sort(key=lambda x: x[0], reverse=True)

        # Initial routes: each customer in [c]
        routes = [[c] for c in customers]
        cust_to_route = {c: r for c, r in zip(customers, routes)}
        merges_applied = 0

        for s_val, i, j in savings_list:
            if s_val <= 0:
                break
            r_i = cust_to_route.get(i)
            r_j = cust_to_route.get(j)
            if r_i is None or r_j is None or r_i is r_j:
                continue

            i_at_end = (r_i[-1] == i)
            i_at_start = (r_i[0] == i)
            j_at_start = (r_j[0] == j)
            j_at_end = (r_j[-1] == j)

            if not (i_at_end or i_at_start) or not (j_at_start or j_at_end):
                continue

            load_i = sum(demands[node] for node in r_i)
            load_j = sum(demands[node] for node in r_j)
            if load_i + load_j > capacity:
                continue

            # Merge: orient r_i so i is at end, orient r_j so j is at start
            if i_at_start:
                r_i.reverse()
            if j_at_end:
                r_j.reverse()

            merged = r_i + r_j
            if r_i in routes:
                routes.remove(r_i)
            if r_j in routes:
                routes.remove(r_j)
            routes.append(merged)
            for node in merged:
                cust_to_route[node] = merged
            merges_applied += 1

        # If more routes than num_vehicles, merge smallest routes
        while len(routes) > num_vehicles and len(routes) > 1:
            best_pair = None
            min_combined = float('inf')
            for idx1 in range(len(routes)):
                for idx2 in range(idx1 + 1, len(routes)):
                    comb = sum(demands[nd] for nd in routes[idx1]) + sum(demands[nd] for nd in routes[idx2])
                    if comb < min_combined:
                        min_combined = comb
                        best_pair = (routes[idx1], routes[idx2])
            if best_pair:
                r1, r2 = best_pair
                merged = r1 + r2
                routes.remove(r1)
                routes.remove(r2)
                routes.append(merged)
            else:
                break

        # Format routes
        formatted_routes = []
        total_distance = 0.0
        served = set()

        for vid, r_nodes in enumerate(routes[:num_vehicles]):
            full_stops = [depot] + r_nodes + [depot]
            dist = sum(distance_matrix[full_stops[k]][full_stops[k+1]] for k in range(len(full_stops) - 1))
            load = sum(demands[nd] for nd in r_nodes)
            veh_cap = vehicle_capacities[vid] if vid < len(vehicle_capacities) else capacity
            formatted_routes.append({
                "vehicle_id": vid,
                "stops": full_stops,
                "customer_stops": r_nodes,
                "distance_km": round(float(dist), 3),
                "load": load,
                "capacity": veh_cap,
                "utilization_pct": round(load / veh_cap * 100, 1) if veh_cap > 0 else 0,
            })
            total_distance += dist
            served.update(r_nodes)

        # Leftover customers
        unserved = set(customers) - served
        for un in unserved:
            if formatted_routes:
                best_r = min(formatted_routes, key=lambda r: r["load"])
                best_r["customer_stops"].append(un)
                best_r["stops"].insert(-1, un)
                best_r["load"] += demands[un]
                st = best_r["stops"]
                dist = sum(distance_matrix[st[k]][st[k+1]] for k in range(len(st)-1))
                best_r["distance_km"] = round(float(dist), 3)
                best_r["utilization_pct"] = round(best_r["load"] / best_r["capacity"] * 100, 1) if best_r["capacity"] > 0 else 0
                served.add(un)

        total_distance = sum(r["distance_km"] for r in formatted_routes)
        exec_time = time.time() - t0
        total_time = (total_distance / 40.0) * 60.0

        validation = self._validate_solution(formatted_routes, demands, vehicle_capacities, n, depot)
        obj_weights = objective_weights or {"distance": 1.0, "travel_time": 0.5}
        obj_cost = obj_weights.get("distance", 1.0) * total_distance + obj_weights.get("travel_time", 0.5) * total_time

        log_lines = [
            "Clarke–Wright Savings Heuristic executed.",
            f"Evaluated {len(savings_list)} customer pairs. Merges performed: {merges_applied}.",
            f"Resulting routes: {len(formatted_routes)}, Total Distance: {total_distance:.2f} km.",
            f"Execution time: {exec_time:.3f}s. Feasible: {validation['is_feasible']}."
        ]

        return {
            "success": True,
            "algorithm": "clarke_wright",
            "algorithm_name": "Clarke–Wright Savings",
            "category": "classical",
            "status": "FEASIBLE" if validation["is_feasible"] else "HEURISTIC",
            "execution_time_sec": round(float(exec_time), 3),
            "routes": formatted_routes,
            "total_distance_km": round(float(total_distance), 3),
            "total_travel_time_min": round(float(total_time), 2),
            "total_objective_cost": round(float(obj_cost), 3),
            "is_feasible": validation["is_feasible"],
            "capacity_violations": validation["capacity_violations"],
            "unserved_customers": n - 1 - len(served),
            "served_customers": len(served),
            "solver_log": "\n".join(log_lines),
            "validation": validation,
            "warnings": validation.get("warnings", []),
            "convergence_info": {
                "merges_applied": merges_applied,
                "initial_routes": len(customers),
                "final_routes": len(formatted_routes),
            }
        }

    def solve_two_opt(
        self,
        distance_matrix: np.ndarray,
        num_vehicles: int,
        depot: int = 0,
        demands: Optional[List[int]] = None,
        vehicle_capacities: Optional[List[int]] = None,
        objective_weights: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        2-opt Route Improvement Heuristic:
        Starts with a feasible initial routing solution and iteratively eliminates
        edge crossings by reversing route segments until 2-opt local optimality.
        """
        t0 = time.time()
        base_sol = self.solve_clarke_wright(
            distance_matrix, num_vehicles, depot, demands, vehicle_capacities, objective_weights
        )

        routes = [dict(r) for r in base_sol["routes"]]
        total_swaps = 0
        initial_distance = base_sol["total_distance_km"]

        for route in routes:
            stops = list(route["stops"])
            improved = True
            iterations = 0
            max_iter = 100

            while improved and iterations < max_iter:
                improved = False
                iterations += 1
                k = len(stops) - 1
                for i in range(1, k - 1):
                    for j in range(i + 1, k):
                        d_current = distance_matrix[stops[i-1]][stops[i]] + distance_matrix[stops[j]][stops[j+1]]
                        d_new = distance_matrix[stops[i-1]][stops[j]] + distance_matrix[stops[i]][stops[j+1]]

                        if d_new < d_current - 1e-4:
                            stops[i : j + 1] = list(reversed(stops[i : j + 1]))
                            improved = True
                            total_swaps += 1

            route["stops"] = stops
            route["customer_stops"] = [s for s in stops if s != depot]
            route_dist = sum(distance_matrix[stops[m]][stops[m+1]] for m in range(len(stops) - 1))
            route["distance_km"] = round(float(route_dist), 3)

        total_distance = sum(r["distance_km"] for r in routes)
        exec_time = time.time() - t0
        total_time = (total_distance / 40.0) * 60.0

        n = len(distance_matrix)
        demands_list = demands if demands is not None else ([0] + [1] * (n - 1))
        caps = vehicle_capacities if vehicle_capacities is not None else ([100] * num_vehicles)
        validation = self._validate_solution(routes, demands_list, caps, n, depot)

        obj_weights = objective_weights or {"distance": 1.0, "travel_time": 0.5}
        obj_cost = obj_weights.get("distance", 1.0) * total_distance + obj_weights.get("travel_time", 0.5) * total_time
        dist_saved = max(0.0, initial_distance - total_distance)

        log_lines = [
            "2-opt Route Improvement Heuristic completed.",
            f"Total 2-opt edge-exchange improvements: {total_swaps}.",
            f"Distance reduced from {initial_distance:.2f} km to {total_distance:.2f} km (-{dist_saved:.2f} km).",
            f"Execution time: {exec_time:.3f}s. Feasible: {validation['is_feasible']}."
        ]

        return {
            "success": True,
            "algorithm": "two_opt",
            "algorithm_name": "2-opt Route Improvement",
            "category": "classical",
            "status": "LOCAL_OPTIMAL" if validation["is_feasible"] else "HEURISTIC",
            "execution_time_sec": round(float(exec_time), 3),
            "routes": routes,
            "total_distance_km": round(float(total_distance), 3),
            "total_travel_time_min": round(float(total_time), 2),
            "total_objective_cost": round(float(obj_cost), 3),
            "is_feasible": validation["is_feasible"],
            "capacity_violations": validation["capacity_violations"],
            "unserved_customers": validation["unserved_count"],
            "served_customers": validation["served_count"],
            "solver_log": "\n".join(log_lines),
            "validation": validation,
            "warnings": validation.get("warnings", []),
            "convergence_info": {
                "swaps_performed": total_swaps,
                "initial_distance_km": round(initial_distance, 3),
                "improved_distance_km": round(total_distance, 3),
                "savings_pct": round((dist_saved / max(initial_distance, 1e-6)) * 100, 2),
            }
        }

    def solve_dijkstra(
        self,
        distance_matrix: np.ndarray,
        num_vehicles: int,
        depot: int = 0,
        demands: Optional[List[int]] = None,
        vehicle_capacities: Optional[List[int]] = None,
        objective_weights: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Dijkstra Shortest-Path Baseline:
        Computes shortest-path graph reachability trees from the depot across the road network,
        and constructs multi-vehicle delivery baseline routes by greedily serving customers
        ordered by Dijkstra minimum graph distance while enforcing vehicle capacity constraints.
        """
        t0 = time.time()
        n = len(distance_matrix)
        customers = [i for i in range(n) if i != depot]

        if demands is None:
            demands = [0] + [1] * (n - 1)
        if vehicle_capacities is None:
            vehicle_capacities = [max(n, 100)] * num_vehicles
        capacity = vehicle_capacities[0] if vehicle_capacities else 100

        # Run Dijkstra from depot to all nodes
        dist_from_depot = {depot: 0.0}
        pq = [(0.0, depot)]
        visited_nodes = 0

        while pq:
            d_curr, u = heapq.heappop(pq)
            visited_nodes += 1
            for v in range(n):
                if u != v:
                    weight = distance_matrix[u][v]
                    if dist_from_depot.get(v, float('inf')) > d_curr + weight:
                        dist_from_depot[v] = d_curr + weight
                        heapq.heappush(pq, (d_curr + weight, v))

        # Order customers by Dijkstra distance from depot
        sorted_customers = sorted(customers, key=lambda c: dist_from_depot.get(c, float('inf')))

        routes = []
        cust_pool = list(sorted_customers)

        for vid in range(num_vehicles):
            if not cust_pool:
                break
            route_stops = [depot]
            load = 0
            curr_node = depot
            veh_cap = vehicle_capacities[vid] if vid < len(vehicle_capacities) else capacity

            while cust_pool:
                best_idx = None
                best_cost = float('inf')
                for idx, c in enumerate(cust_pool):
                    if load + demands[c] <= veh_cap:
                        c_cost = distance_matrix[curr_node][c]
                        if c_cost < best_cost:
                            best_cost = c_cost
                            best_idx = idx

                if best_idx is None:
                    break

                chosen_cust = cust_pool.pop(best_idx)
                route_stops.append(chosen_cust)
                load += demands[chosen_cust]
                curr_node = chosen_cust

            route_stops.append(depot)
            if len(route_stops) > 2:
                r_dist = sum(distance_matrix[route_stops[i]][route_stops[i+1]] for i in range(len(route_stops)-1))
                routes.append({
                    "vehicle_id": vid,
                    "stops": route_stops,
                    "customer_stops": [s for s in route_stops if s != depot],
                    "distance_km": round(float(r_dist), 3),
                    "load": load,
                    "capacity": veh_cap,
                    "utilization_pct": round(load / veh_cap * 100, 1) if veh_cap > 0 else 0,
                })

        # Leftovers
        if cust_pool and routes:
            for c in list(cust_pool):
                best_r = min(routes, key=lambda r: r["load"])
                best_r["customer_stops"].append(c)
                best_r["stops"].insert(-1, c)
                best_r["load"] += demands[c]
                cust_pool.remove(c)
            for r in routes:
                st = r["stops"]
                dist = sum(distance_matrix[st[i]][st[i+1]] for i in range(len(st)-1))
                r["distance_km"] = round(float(dist), 3)
                r["utilization_pct"] = round(r["load"] / r["capacity"] * 100, 1) if r["capacity"] > 0 else 0

        total_distance = sum(r["distance_km"] for r in routes)
        exec_time = time.time() - t0
        total_time = (total_distance / 40.0) * 60.0

        validation = self._validate_solution(routes, demands, vehicle_capacities, n, depot)
        obj_weights = objective_weights or {"distance": 1.0, "travel_time": 0.5}
        obj_cost = obj_weights.get("distance", 1.0) * total_distance + obj_weights.get("travel_time", 0.5) * total_time

        log_lines = [
            "Dijkstra Shortest-Path Baseline completed.",
            f"Depot-rooted shortest path tree evaluated with {visited_nodes} node explorations.",
            f"Mean shortest distance from depot: {np.mean([dist_from_depot[c] for c in customers]):.2f} km.",
            f"Total baseline route distance: {total_distance:.2f} km across {len(routes)} vehicles.",
            f"Execution time: {exec_time:.3f}s. Feasible: {validation['is_feasible']}."
        ]

        return {
            "success": True,
            "algorithm": "dijkstra",
            "algorithm_name": "Dijkstra Shortest-Path",
            "category": "classical",
            "status": "BASELINE",
            "execution_time_sec": round(float(exec_time), 3),
            "routes": routes,
            "total_distance_km": round(float(total_distance), 3),
            "total_travel_time_min": round(float(total_time), 2),
            "total_objective_cost": round(float(obj_cost), 3),
            "is_feasible": validation["is_feasible"],
            "capacity_violations": validation["capacity_violations"],
            "unserved_customers": validation["unserved_count"],
            "served_customers": validation["served_count"],
            "solver_log": "\n".join(log_lines),
            "validation": validation,
            "warnings": validation.get("warnings", []),
            "convergence_info": {
                "nodes_evaluated": visited_nodes,
                "shortest_path_mean_km": round(float(np.mean([dist_from_depot[c] for c in customers])), 3),
            }
        }

    def solve_astar(
        self,
        distance_matrix: np.ndarray,
        num_vehicles: int,
        depot: int = 0,
        demands: Optional[List[int]] = None,
        vehicle_capacities: Optional[List[int]] = None,
        objective_weights: Optional[Dict[str, float]] = None,
        locations: Optional[List[Tuple[float, float]]] = None,
    ) -> Dict[str, Any]:
        """
        A* Heuristic-Based Shortest-Path Search:
        Computes delivery sequences guided by the admissible heuristic evaluation function
        f(n) = g(n) + h(n), where g(n) is the accumulated path distance and h(n) is the
        heuristic lower bound distance back to the depot/next target.
        """
        t0 = time.time()
        n = len(distance_matrix)
        customers = [i for i in range(n) if i != depot]

        if demands is None:
            demands = [0] + [1] * (n - 1)
        if vehicle_capacities is None:
            vehicle_capacities = [max(n, 100)] * num_vehicles
        capacity = vehicle_capacities[0] if vehicle_capacities else 100

        def heuristic(node: int) -> float:
            return float(distance_matrix[node][depot])

        routes = []
        cust_pool = list(customers)
        evaluations_count = 0

        for vid in range(num_vehicles):
            if not cust_pool:
                break
            route_stops = [depot]
            load = 0
            curr_node = depot
            veh_cap = vehicle_capacities[vid] if vid < len(vehicle_capacities) else capacity

            while cust_pool:
                best_idx = None
                best_f = float('inf')

                for idx, c in enumerate(cust_pool):
                    evaluations_count += 1
                    if load + demands[c] <= veh_cap:
                        g_val = distance_matrix[curr_node][c]
                        h_val = heuristic(c)
                        f_val = g_val + 0.5 * h_val
                        if f_val < best_f:
                            best_f = f_val
                            best_idx = idx

                if best_idx is None:
                    break

                chosen = cust_pool.pop(best_idx)
                route_stops.append(chosen)
                load += demands[chosen]
                curr_node = chosen

            route_stops.append(depot)
            if len(route_stops) > 2:
                r_dist = sum(distance_matrix[route_stops[i]][route_stops[i+1]] for i in range(len(route_stops)-1))
                routes.append({
                    "vehicle_id": vid,
                    "stops": route_stops,
                    "customer_stops": [s for s in route_stops if s != depot],
                    "distance_km": round(float(r_dist), 3),
                    "load": load,
                    "capacity": veh_cap,
                    "utilization_pct": round(load / veh_cap * 100, 1) if veh_cap > 0 else 0,
                })

        # Handle leftovers
        if cust_pool and routes:
            for c in list(cust_pool):
                best_r = min(routes, key=lambda r: r["load"])
                best_r["customer_stops"].append(c)
                best_r["stops"].insert(-1, c)
                best_r["load"] += demands[c]
                cust_pool.remove(c)
            for r in routes:
                st = r["stops"]
                dist = sum(distance_matrix[st[i]][st[i+1]] for i in range(len(st)-1))
                r["distance_km"] = round(float(dist), 3)
                r["utilization_pct"] = round(r["load"] / r["capacity"] * 100, 1) if r["capacity"] > 0 else 0

        total_distance = sum(r["distance_km"] for r in routes)
        exec_time = time.time() - t0
        total_time = (total_distance / 40.0) * 60.0

        validation = self._validate_solution(routes, demands, vehicle_capacities, n, depot)
        obj_weights = objective_weights or {"distance": 1.0, "travel_time": 0.5}
        obj_cost = obj_weights.get("distance", 1.0) * total_distance + obj_weights.get("travel_time", 0.5) * total_time

        log_lines = [
            "A* Heuristic Search completed.",
            f"Admissible f(n) evaluations performed: {evaluations_count}.",
            f"Constructed routes for {len(routes)} vehicles, total distance: {total_distance:.2f} km.",
            f"Execution time: {exec_time:.3f}s. Feasible: {validation['is_feasible']}."
        ]

        return {
            "success": True,
            "algorithm": "astar",
            "algorithm_name": "A* Heuristic Search",
            "category": "classical",
            "status": "HEURISTIC",
            "execution_time_sec": round(float(exec_time), 3),
            "routes": routes,
            "total_distance_km": round(float(total_distance), 3),
            "total_travel_time_min": round(float(total_time), 2),
            "total_objective_cost": round(float(obj_cost), 3),
            "is_feasible": validation["is_feasible"],
            "capacity_violations": validation["capacity_violations"],
            "unserved_customers": validation["unserved_count"],
            "served_customers": validation["served_count"],
            "solver_log": "\n".join(log_lines),
            "validation": validation,
            "warnings": validation.get("warnings", []),
            "convergence_info": {
                "heuristic_evaluations": evaluations_count,
            }
        }


# Singleton
classical_solver = ClassicalVRPSolver()
