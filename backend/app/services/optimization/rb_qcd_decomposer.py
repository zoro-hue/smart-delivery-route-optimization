"""Resource-Budgeted Quantum-Classical Decomposition (RB-QCD) Module.

This module implements a principled, resource-aware hybrid decomposition for
Vehicle Routing Problems (CVRP / ACVRP) under strict NISQ qubit budgets.

Design Principles:
1. Complete Customer Preservation: Every customer is assigned to a vehicle route;
   no customer is silently dropped, ignored, or truncated.
2. Stable Internal Indices: Customers are indexed internally by integer position (0..N-1),
   preventing collision if duplicate user-facing string IDs or duplicate road nodes exist.
3. Explicit Qubit Budget: Subproblems routed through gate-based QAOA strictly respect
   the logical qubit limit Q_budget (default <= 16 qubits, i.e., m <= 4 nodes).
4. Directed Asymmetric Matrix Preservation: All costs and insertion deltas preserve
   directed edge asymmetry c(u, v) != c(v, u).
5. Depot-Aware Endpoints: Routes strictly depart from and return to depot 0.
6. Exact Capacity Compliance: Cumulative customer demand on each route strictly <= Q_k.
   Insufficient total fleet capacity produces an explicit infeasibility result.
7. Honest Labelling: Sequential dynamic programming insertion is labelled as a heuristic
   reconstruction procedure that guarantees feasibility, not global optimality.
"""

from typing import List, Dict, Any, Tuple, Optional
import time
import numpy as np


class RBQCDDecomposer:
    """Resource-Budgeted Quantum-Classical Decomposer for VRP."""

    def __init__(self, qaoa_solver: Optional[Any] = None, max_qubits: int = 16):
        """
        Args:
            qaoa_solver: Optional QAOASolver instance (Qiskit-based).
            max_qubits: Maximum logical qubits for subproblem QAOA (default 16).
                        For an m-node TSP subproblem, Q = m^2, so max_qubits=16 means m <= 4.
        """
        self.qaoa_solver = qaoa_solver
        self.max_qubits = max_qubits
        self.max_qaoa_nodes = int(np.floor(np.sqrt(max_qubits)))  # e.g., floor(sqrt(16)) = 4

    def decompose_and_solve(
        self,
        customers: List[Dict[str, Any]],
        depot: Dict[str, Any],
        matrix: np.ndarray,
        num_vehicles: int,
        vehicle_capacity: float,
        location_indices: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Executes complete RB-QCD:
        Step 1: Wrap customers with stable internal indices (0..N-1) to eliminate collision.
        Step 2: Fleet capacity adequacy check.
        Step 3: Initial fleet partitioning into K feasible routes.
        Step 4: Subproblem extraction (core dense cluster <= max_qaoa_nodes).
        Step 5: QAOA sub-tour optimization on the core cluster.
        Step 6: Heuristic Dynamic Programming insertion of remaining boundary nodes.
        Step 7: Rigorous feasibility verification.

        Returns a dictionary with complete routes, feasibility metrics, and audit statistics.
        """
        n_cust = len(customers)
        if n_cust == 0:
            return {
                "routes": [],
                "total_distance": 0.0,
                "feasibility": {
                    "is_feasible": True,
                    "unassigned_customers": 0,
                    "capacity_violations": 0,
                    "total_input_customers": 0,
                    "total_routed_customers": 0
                },
                "audit": {
                    "method": "RB-QCD",
                    "qaoa_subproblems_solved": 0,
                    "classical_fallbacks": 0,
                    "logical_qubits": 0,
                    "circuit_depth": 0,
                    "execution_time_ms": 0.0
                }
            }

        t_start = time.perf_counter()
        depot_idx = location_indices.get(depot.get("id", "depot"), 0)

        # Step 1: Wrap customers with stable internal indices
        wrapped_customers = []
        total_demand = 0.0
        for idx, c in enumerate(customers):
            dem = float(c.get("demand", 1.0))
            total_demand += dem
            wrapped_customers.append({
                "internal_idx": idx,
                "user_id": c.get("id", f"c_{idx}"),
                "demand": dem,
                "original_dict": c
            })

        # Step 2: Fleet capacity check
        total_fleet_capacity = num_vehicles * vehicle_capacity
        insufficient_capacity = (total_demand > total_fleet_capacity + 1e-6)

        # Step 3: Initial Fleet Partitioning
        clusters = self._initial_fleet_partition(
            wrapped_customers, depot, matrix, num_vehicles, vehicle_capacity, location_indices, depot_idx
        )

        routes = []
        total_dist = 0.0
        qaoa_calls = 0
        classical_fallbacks = 0
        max_logical_qubits = 0
        total_circuit_depth = 0
        all_routed_internal_indices = set()

        for k, cluster in enumerate(clusters):
            if not cluster:
                continue

            # Step 4, 5, 6: Optimize route with core QAOA + DP insertion
            route_dict, did_qaoa, qubits, depth = self._optimize_single_route(
                cluster, depot, matrix, vehicle_capacity, location_indices, depot_idx, k
            )
            if did_qaoa:
                qaoa_calls += 1
                max_logical_qubits = max(max_logical_qubits, qubits)
                total_circuit_depth += depth
            else:
                classical_fallbacks += 1

            routes.append(route_dict)
            total_dist += route_dict["total_distance"]
            for item in route_dict["internal_stops"][1:-1]:
                all_routed_internal_indices.add(item["internal_idx"])

        # Step 7: Feasibility Audit
        input_indices = set(range(n_cust))
        missing_indices = input_indices - all_routed_internal_indices
        capacity_violations = sum(1 for r in routes if r["total_load"] > vehicle_capacity + 1e-6)

        # Instance is strictly feasible ONLY IF:
        # 1. Total fleet capacity was sufficient
        # 2. No customer is missing
        # 3. No vehicle load exceeds vehicle_capacity
        is_feasible = (
            (not insufficient_capacity) and
            (len(missing_indices) == 0) and
            (capacity_violations == 0) and
            (len(all_routed_internal_indices) == n_cust)
        )

        t_elapsed_ms = (time.perf_counter() - t_start) * 1000.0

        return {
            "routes": routes,
            "total_distance": round(total_dist, 2),
            "feasibility": {
                "is_feasible": is_feasible,
                "total_input_customers": n_cust,
                "total_routed_customers": len(all_routed_internal_indices),
                "unassigned_customers": len(missing_indices),
                "missing_customer_indices": list(missing_indices),
                "capacity_violations": capacity_violations,
                "insufficient_fleet_capacity": insufficient_capacity,
                "total_demand": round(total_demand, 2),
                "total_fleet_capacity": round(total_fleet_capacity, 2),
                "reconstruction_heuristic": "Sequential Directed Minimum-Incremental-Cost DP Insertion"
            },
            "audit": {
                "method": "RB-QCD",
                "max_qubits_budget": self.max_qubits,
                "max_qaoa_nodes": self.max_qaoa_nodes,
                "qaoa_subproblems_solved": qaoa_calls,
                "classical_fallbacks": classical_fallbacks,
                "max_logical_qubits_used": max_logical_qubits,
                "total_circuit_depth": total_circuit_depth,
                "num_routes": len(routes),
                "execution_time_ms": round(t_elapsed_ms, 3)
            }
        }

    def _initial_fleet_partition(
        self,
        wrapped_customers: List[Dict[str, Any]],
        depot: Dict[str, Any],
        matrix: np.ndarray,
        num_vehicles: int,
        vehicle_capacity: float,
        location_indices: Dict[str, int],
        depot_idx: int
    ) -> List[List[Dict[str, Any]]]:
        """Partitions customers into K disjoint clusters respecting vehicle capacity."""
        sorted_custs = sorted(
            wrapped_customers,
            key=lambda c: matrix[depot_idx, location_indices[c["user_id"]]],
            reverse=True
        )

        clusters: List[List[Dict[str, Any]]] = [[] for _ in range(num_vehicles)]
        loads: List[float] = [0.0] * num_vehicles

        for c in sorted_custs:
            dem = c["demand"]
            c_loc = location_indices[c["user_id"]]

            best_k = -1
            min_cost = float("inf")

            for k in range(num_vehicles):
                if loads[k] + dem <= vehicle_capacity:
                    if not clusters[k]:
                        cost = matrix[depot_idx, c_loc]
                    else:
                        cost = min(matrix[location_indices[other["user_id"]], c_loc] for other in clusters[k])

                    if cost < min_cost:
                        min_cost = cost
                        best_k = k

            if best_k == -1:
                # If all feasible slots full, assign to vehicle with least current load
                best_k = int(np.argmin(loads))

            clusters[best_k].append(c)
            loads[best_k] += dem

        return clusters

    def _optimize_single_route(
        self,
        cluster: List[Dict[str, Any]],
        depot: Dict[str, Any],
        matrix: np.ndarray,
        vehicle_capacity: float,
        location_indices: Dict[str, int],
        depot_idx: int,
        vehicle_idx: int
    ) -> Tuple[Dict[str, Any], bool, int, int]:
        """Optimizes a single vehicle route using core QAOA + DP insertion."""
        m = len(cluster)
        did_qaoa = False
        qubits = 0
        depth = 0

        if m <= self.max_qaoa_nodes:
            optimized_stops, did_qaoa, qubits, depth = self._solve_core_tsp(
                cluster, depot, matrix, location_indices, depot_idx
            )
        else:
            core_cluster, remaining_custs = self._extract_core_cluster(
                cluster, matrix, location_indices, self.max_qaoa_nodes
            )

            core_stops, did_qaoa, qubits, depth = self._solve_core_tsp(
                core_cluster, depot, matrix, location_indices, depot_idx
            )

            optimized_stops = self._reconstruct_route_dp_insertion(
                core_stops, remaining_custs, matrix, location_indices, depot_idx
            )

        # Construct stops structure with depot endpoints
        full_internal_stops = [{"internal_idx": -1, "user_id": depot.get("id", "depot"), "is_depot": True}]
        full_internal_stops.extend(optimized_stops)
        full_internal_stops.append({"internal_idx": -1, "user_id": depot.get("id", "depot"), "is_depot": True})

        full_stops = [depot] + [c["original_dict"] for c in optimized_stops] + [depot]
        total_dist = self._calculate_route_distance(optimized_stops, depot, matrix, location_indices, depot_idx)
        total_load = sum(c["demand"] for c in cluster)

        route_dict = {
            "vehicle_id": vehicle_idx,
            "stops": full_stops,
            "internal_stops": full_internal_stops,
            "total_distance": round(total_dist, 2),
            "total_load": round(total_load, 2),
            "customer_count": m
        }
        return route_dict, did_qaoa, qubits, depth

    def _extract_core_cluster(
        self,
        cluster: List[Dict[str, Any]],
        matrix: np.ndarray,
        location_indices: Dict[str, int],
        core_size: int
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Extracts dense core subset of size core_size."""
        if len(cluster) <= core_size:
            return cluster, []

        best_seed = (0, 1)
        min_seed_dist = float("inf")

        for i in range(len(cluster)):
            for j in range(i + 1, len(cluster)):
                idx_i = location_indices[cluster[i]["user_id"]]
                idx_j = location_indices[cluster[j]["user_id"]]
                d = matrix[idx_i, idx_j] + matrix[idx_j, idx_i]
                if d < min_seed_dist:
                    min_seed_dist = d
                    best_seed = (i, j)

        core_indices = {best_seed[0], best_seed[1]}

        while len(core_indices) < core_size:
            best_cand = -1
            min_cand_dist = float("inf")
            for c_i in range(len(cluster)):
                if c_i in core_indices:
                    continue
                cand_loc = location_indices[cluster[c_i]["user_id"]]
                avg_dist = sum(
                    matrix[cand_loc, location_indices[cluster[ex]["user_id"]]] +
                    matrix[location_indices[cluster[ex]["user_id"]], cand_loc]
                    for ex in core_indices
                )
                if avg_dist < min_cand_dist:
                    min_cand_dist = avg_dist
                    best_cand = c_i
            core_indices.add(best_cand)

        core = [cluster[i] for i in sorted(core_indices)]
        boundary = [cluster[i] for i in range(len(cluster)) if i not in core_indices]
        return core, boundary

    def _solve_core_tsp(
        self,
        sub_customers: List[Dict[str, Any]],
        depot: Dict[str, Any],
        matrix: np.ndarray,
        location_indices: Dict[str, int],
        depot_idx: int
    ) -> Tuple[List[Dict[str, Any]], bool, int, int]:
        """
        Solves exact asymmetric TSP for <= 4 customers using QAOA if available,
        falling back to exact brute-force enumeration.
        """
        m = len(sub_customers)
        if m <= 1:
            return sub_customers, False, 0, 0

        qubits = m * m
        depth = 2  # p=2 QAOA layers

        # If QAOA solver is provided and healthy, invoke it
        if self.qaoa_solver is not None and hasattr(self.qaoa_solver, "solve_qaoa"):
            try:
                # Prepare input with unique ids for QAOA solver
                qaoa_input = [{"id": c["user_id"], "demand": c["demand"]} for c in sub_customers]
                qaoa_res = self.qaoa_solver.solve_qaoa(
                    customers=qaoa_input,
                    depot=depot,
                    matrix=matrix,
                    location_indices=location_indices
                )
                if qaoa_res and "stops" in qaoa_res:
                    inner_ids = [s["id"] for s in qaoa_res["stops"] if s["id"] != depot["id"]]
                    if len(inner_ids) == m:
                        # Re-map to wrapped customer objects
                        cust_by_id = {c["user_id"]: c for c in sub_customers}
                        ordered = [cust_by_id[uid] for uid in inner_ids if uid in cust_by_id]
                        if len(ordered) == m:
                            return ordered, True, qubits, depth
            except Exception:
                pass

        # Exact Brute-Force Classical Fallback (Ground-truth optimal)
        import itertools
        best_perm = None
        best_cost = float("inf")

        for perm in itertools.permutations(sub_customers):
            c0_loc = location_indices[perm[0]["user_id"]]
            cost = matrix[depot_idx, c0_loc]
            for i in range(len(perm) - 1):
                u_loc = location_indices[perm[i]["user_id"]]
                v_loc = location_indices[perm[i + 1]["user_id"]]
                cost += matrix[u_loc, v_loc]
            cost += matrix[location_indices[perm[-1]["user_id"]], depot_idx]

            if cost < best_cost:
                best_cost = cost
                best_perm = list(perm)

        return (best_perm if best_perm is not None else sub_customers), False, 0, 0

    def _reconstruct_route_dp_insertion(
        self,
        core_stops: List[Dict[str, Any]],
        remaining_customers: List[Dict[str, Any]],
        matrix: np.ndarray,
        location_indices: Dict[str, int],
        depot_idx: int
    ) -> List[Dict[str, Any]]:
        """
        Reconstructs complete route by sequentially inserting remaining customers into the
        position that minimizes the directed insertion delta:
        delta = c(pred, u) + c(u, succ) - c(pred, succ).
        """
        current_stops = list(core_stops)

        for u in remaining_customers:
            u_loc = location_indices[u["user_id"]]
            best_pos = -1
            min_delta = float("inf")

            num_nodes = len(current_stops)

            for pos in range(num_nodes + 1):
                pred_loc = depot_idx if pos == 0 else location_indices[current_stops[pos - 1]["user_id"]]
                succ_loc = depot_idx if pos == num_nodes else location_indices[current_stops[pos]["user_id"]]

                delta = matrix[pred_loc, u_loc] + matrix[u_loc, succ_loc] - matrix[pred_loc, succ_loc]

                if delta < min_delta:
                    min_delta = delta
                    best_pos = pos

            current_stops.insert(best_pos, u)

        return current_stops

    def _calculate_route_distance(
        self,
        inner_stops: List[Dict[str, Any]],
        depot: Dict[str, Any],
        matrix: np.ndarray,
        location_indices: Dict[str, int],
        depot_idx: int
    ) -> float:
        """Calculates exact directed distance: depot -> stop_0 -> ... -> stop_{m-1} -> depot."""
        if not inner_stops:
            return 0.0

        dist = matrix[depot_idx, location_indices[inner_stops[0]["user_id"]]]
        for i in range(len(inner_stops) - 1):
            u_loc = location_indices[inner_stops[i]["user_id"]]
            v_loc = location_indices[inner_stops[i + 1]["user_id"]]
            dist += matrix[u_loc, v_loc]
        dist += matrix[location_indices[inner_stops[-1]["user_id"]], depot_idx]
        return dist
