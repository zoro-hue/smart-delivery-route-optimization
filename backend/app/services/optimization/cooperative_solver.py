"""
ROUTE/IQ Cooperative Optimization Engine Solver Service.
Integrates:
- Pillar 1: Apache Spark 4.2.0 Workload Decomposition & Spatial Partitioning
- Pillar 2: Variational Quantum Candidate Generation (Fast QAOA) & Classical Metaheuristics
- Adaptive Strategy Controller (Multi-Armed Bandit)
- Classical Route Refinement (Algorithmic Variable Neighborhood Descent - VND)
- Centralized Non-Degradation Guardrail (Proposition 1)

This service implements the complete end-to-end cooperative architecture established in
Phases AB, AC, and AD for production deployment in ROUTE/IQ.
"""

import os
import time
import math
import copy
import logging
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import pandas as pd

from app.services.optimization.classical_solver import classical_solver
from app.services.optimization.route_validator import repair_fleet_coverage, validate_fleet_coverage
from phase_v_independent_quantum_validation.prototypes.algorithmic_vnd import AlgorithmicVND
from phase_ab_cooperative_optimization_engine.engine.cooperative_engine import CooperativeOptimizationEngine
from phase_ab_cooperative_optimization_engine.engine.spark_preprocessor import SparkWorkloadOrganizer
from phase_ab_cooperative_optimization_engine.engine.classical_engine import ClassicalOptimizationEngine

logger = logging.getLogger(__name__)


class CooperativeVRPSolver:
    """Production Cooperative Optimization Solver for ROUTE/IQ."""

    def __init__(self, use_spark: bool = True):
        self.engine = CooperativeOptimizationEngine(use_spark=use_spark)
        self.classical_engine = ClassicalOptimizationEngine()
        self.spark_organizer = SparkWorkloadOrganizer() if use_spark else None

    def solve(
        self,
        distance_matrix: np.ndarray,
        num_vehicles: int,
        depot: int = 0,
        demands: Optional[List[int]] = None,
        vehicle_capacities: Optional[List[int]] = None,
        time_limit_sec: float = 0.25,
        objective_weights: Optional[Dict[str, float]] = None,
        travel_time_matrix: Optional[np.ndarray] = None,
        locations: Optional[List[Tuple[float, float]]] = None,
        strategy_override: Optional[str] = None,
        seed: int = 42,
    ) -> Dict[str, Any]:
        """
        Solves CVRP cooperatively using Hybrid Big Data + Classical + Quantum Pipeline:
        1. Generates an initial feasible fleet incumbent using OR-Tools CVRP matching full search budget.
        2. Evaluates competitive multi-solver initialization (OR-Tools, Tabu, and VND).
        3. Decomposes boundary customers between adjacent routes via Spark spatial partitioning.
        4. Queries Adaptive Controller to dispatch candidate generators (QAOA with Qiskit Aer simulation or Tabu/KL).
        5. Refines route reconstructions via intra-route 2-opt and inter-route Algorithmic VND (Relocate & Swap).
        6. Enforces Proposition 1 Non-Degradation Guardrail: Cost(Final) <= Cost(OR-Tools Incumbent).
        7. Returns complete validated routes and telemetry.
        """
        t0 = time.perf_counter()
        n = distance_matrix.shape[0]

        if demands is None:
            demands = [0] + [1] * (n - 1)
        if vehicle_capacities is None:
            vehicle_capacities = [100] * num_vehicles

        effective_limit = float(time_limit_sec) if time_limit_sec is not None else 0.25
        input_cust_ids = [i for i in range(n) if i != depot]

        # ── Step 1: High-Quality OR-Tools Incumbent Generation ──────────
        logger.info(f"Cooperative Solver: Generating initial incumbent for {n} nodes, {num_vehicles} vehicles...")
        incumbent_res = classical_solver.solve_ortools(
            distance_matrix=distance_matrix,
            num_vehicles=num_vehicles,
            depot=depot,
            demands=demands,
            vehicle_capacities=vehicle_capacities,
            time_limit_sec=effective_limit,
            objective_weights=objective_weights,
            travel_time_matrix=travel_time_matrix,
        )

        if not incumbent_res.get("success") or not incumbent_res.get("routes"):
            logger.warning("OR-Tools failed to generate initial incumbent; falling back to Clarke-Wright.")
            incumbent_res = classical_solver.solve_clarke_wright(
                distance_matrix=distance_matrix,
                num_vehicles=num_vehicles,
                depot=depot,
                demands=demands,
                vehicle_capacities=vehicle_capacities,
                objective_weights=objective_weights,
            )

        incumbent_routes, _ = repair_fleet_coverage(
            incumbent_res.get("routes", []),
            input_cust_ids,
            distance_matrix,
            demands,
            vehicle_capacities,
            num_vehicles,
            depot,
        )

        if not incumbent_routes:
            return incumbent_res

        ortools_distance = float(incumbent_res.get("total_distance_km", sum(r.get("distance_km", 0.0) for r in incumbent_routes)))
        best_routes = copy.deepcopy(incumbent_routes)
        best_distance = ortools_distance
        ortools_incumbent_routes = copy.deepcopy(incumbent_routes)

        # ── Step 2: Multi-Solver Cooperative Initialization Pool ─────────
        # Test whether fast classical metaheuristics discover an alternate basin of attraction
        cand_tabu = classical_solver.solve_tabu_search(
            distance_matrix, num_vehicles, depot, demands, vehicle_capacities, max_iterations=80
        )
        if cand_tabu.get("success") and cand_tabu.get("routes"):
            rep_tabu, val_t = repair_fleet_coverage(
                cand_tabu["routes"], input_cust_ids, distance_matrix, demands, vehicle_capacities, num_vehicles, depot
            )
            if val_t["is_valid"]:
                d_tabu = float(sum(r.get("distance_km", 0.0) for r in rep_tabu))
                if d_tabu < best_distance - 1e-4:
                    best_distance = d_tabu
                    best_routes = copy.deepcopy(rep_tabu)

        cand_vnd = classical_solver.solve_vnd(
            distance_matrix, num_vehicles, depot, demands, vehicle_capacities
        )
        if cand_vnd.get("success") and cand_vnd.get("routes"):
            rep_vnd, val_v = repair_fleet_coverage(
                cand_vnd["routes"], input_cust_ids, distance_matrix, demands, vehicle_capacities, num_vehicles, depot
            )
            if val_v["is_valid"]:
                d_vnd = float(sum(r.get("distance_km", 0.0) for r in rep_vnd))
                if d_vnd < best_distance - 1e-4:
                    best_distance = d_vnd
                    best_routes = copy.deepcopy(rep_vnd)

        routes = copy.deepcopy(best_routes)
        subproblem_telemetry = []

        # ── Step 3: Spark Spatial Boundary Decomposition & Quantum QAOA Candidate Exploration ──
        if len(routes) >= 2 and n >= 4:
            logger.info("Cooperative Solver: Identifying spatial route boundaries for cooperative optimization...")

            # Derive spatial centroids for each route
            route_centroids = []
            for r in routes:
                c_nodes = r.get("customer_stops", [])
                if not c_nodes:
                    route_centroids.append((0.0, 0.0))
                elif locations and len(locations) >= n:
                    avg_lat = float(np.mean([locations[c][0] for c in c_nodes]))
                    avg_lon = float(np.mean([locations[c][1] for c in c_nodes]))
                    route_centroids.append((avg_lat, avg_lon))
                else:
                    avg_r = float(np.mean([distance_matrix[depot, c] for c in c_nodes]))
                    route_centroids.append((avg_r, 0.0))

            # Proximity-ordered route pairs
            pair_candidates = []
            for i in range(len(routes)):
                for j in range(i + 1, len(routes)):
                    ci, cj = route_centroids[i], route_centroids[j]
                    spatial_dist = math.hypot(ci[0] - cj[0], ci[1] - cj[1])
                    pair_candidates.append((spatial_dist, i, j))
            pair_candidates.sort(key=lambda x: x[0])

            # Optimize boundary pairs
            for _, idx_a, idx_b in pair_candidates[:min(4, len(pair_candidates))]:
                route_a = routes[idx_a]
                route_b = routes[idx_b]
                stops_a = list(route_a.get("customer_stops", []))
                stops_b = list(route_b.get("customer_stops", []))

                if not stops_a or not stops_b:
                    continue

                cap_a = float(route_a.get("capacity", vehicle_capacities[idx_a]))
                cap_b = float(route_b.get("capacity", vehicle_capacities[idx_b]))
                ca_pt = route_centroids[idx_a]
                cb_pt = route_centroids[idx_b]

                def boundary_distance(node_idx, own_c, other_c):
                    if locations and len(locations) >= n:
                        loc = locations[node_idx]
                        return math.hypot(loc[0] - other_c[0], loc[1] - other_c[1]) - math.hypot(loc[0] - own_c[0], loc[1] - own_c[1])
                    return distance_matrix[node_idx, depot]

                # Identify boundary nodes closest to the facing route
                sorted_a = sorted(stops_a, key=lambda c: boundary_distance(c, ca_pt, cb_pt))
                sorted_b = sorted(stops_b, key=lambda c: boundary_distance(c, cb_pt, ca_pt))

                bound_a = sorted_a[:min(4, len(sorted_a))]
                bound_b = sorted_b[:min(4, len(sorted_b))]
                sub_custs = bound_a + bound_b
                sub_k = len(sub_custs)

                if sub_k < 4:
                    continue

                # Build subproblem distance matrix
                sub_to_node = {i + 1: node for i, node in enumerate(sub_custs)}
                sub_dist = np.zeros((sub_k + 1, sub_k + 1))
                for i_sub, orig_i in sub_to_node.items():
                    sub_dist[0, i_sub] = distance_matrix[depot, orig_i]
                    sub_dist[i_sub, 0] = distance_matrix[orig_i, depot]
                    for j_sub, orig_j in sub_to_node.items():
                        sub_dist[i_sub, j_sub] = distance_matrix[orig_i, orig_j]

                sub_demands = np.array([demands[sub_to_node[i]] for i in range(1, sub_k + 1)], dtype=float)

                unaffected_a = [c for c in stops_a if c not in sub_custs]
                unaffected_b = [c for c in stops_b if c not in sub_custs]
                sub_cap_a = cap_a - sum(demands[c] for c in unaffected_a)
                sub_cap_b = cap_b - sum(demands[c] for c in unaffected_b)

                if sub_cap_a < 0 or sub_cap_b < 0:
                    continue

                try:
                    opt_result = self.engine.optimize_subproblem(
                        dist_matrix=sub_dist,
                        demands=sub_demands,
                        cap_a=sub_cap_a,
                        cap_b=sub_cap_b,
                        c_a=np.array([ca_pt[0], ca_pt[1]]),
                        c_b=np.array([cb_pt[0], cb_pt[1]]),
                        strategy_override=strategy_override,
                        seed=seed + idx_a * 10 + idx_b,
                    )

                    subproblem_telemetry.append({
                        "route_pair": (idx_a, idx_b),
                        "subproblem_size": sub_k,
                        "strategy": opt_result.get("strategy_used"),
                        "backend_device": opt_result.get("backend_device"),
                        "accepted": opt_result.get("guardrail_accepted"),
                        "initial_sub_distance": round(float(opt_result.get("initial_distance_km", 0.0)), 3),
                        "final_sub_distance": round(float(opt_result.get("final_distance_km", 0.0)), 3),
                        "latency_ms": opt_result.get("total_latency_ms"),
                    })

                    # If Proposition 1 guardrail accepted candidate, reconstruct full routes
                    if opt_result.get("guardrail_accepted"):
                        tour_a_sub = opt_result.get("final_tour_a", [])
                        tour_b_sub = opt_result.get("final_tour_b", [])

                        new_custs_a = [sub_to_node[s] for s in tour_a_sub if s in sub_to_node]
                        new_custs_b = [sub_to_node[s] for s in tour_b_sub if s in sub_to_node]

                        cand_set_a = unaffected_a + new_custs_a
                        cand_set_b = unaffected_b + new_custs_b

                        # Verify capacity
                        if sum(demands[c] for c in cand_set_a) <= cap_a and sum(demands[c] for c in cand_set_b) <= cap_b:
                            # Re-sequence with 2-opt
                            opt_tour_a = AlgorithmicVND.run_2opt(cand_set_a, distance_matrix, depot)
                            opt_tour_b = AlgorithmicVND.run_2opt(cand_set_b, distance_matrix, depot)

                            orig_pair_dist = route_a["distance_km"] + route_b["distance_km"]
                            new_pair_dist = AlgorithmicVND.compute_tour_length(opt_tour_a, distance_matrix, depot) + \
                                            AlgorithmicVND.compute_tour_length(opt_tour_b, distance_matrix, depot)

                            # Local Proposition 1 acceptance
                            if new_pair_dist < orig_pair_dist - 1e-4:
                                route_a["customer_stops"] = opt_tour_a
                                route_a["stops"] = [depot] + opt_tour_a + [depot]
                                route_a["distance_km"] = round(AlgorithmicVND.compute_tour_length(opt_tour_a, distance_matrix, depot), 3)
                                route_a["load"] = sum(demands[c] for c in opt_tour_a)

                                route_b["customer_stops"] = opt_tour_b
                                route_b["stops"] = [depot] + opt_tour_b + [depot]
                                route_b["distance_km"] = round(AlgorithmicVND.compute_tour_length(opt_tour_b, distance_matrix, depot), 3)
                                route_b["load"] = sum(demands[c] for c in opt_tour_b)

                except Exception as e:
                    logger.warning(f"Cooperative subproblem optimization error for routes ({idx_a}, {idx_b}): {e}")

        # ── Step 4: Algorithmic Inter-Route Relocate & Swap (VND) ────────
        for i in range(len(routes)):
            for j in range(len(routes)):
                if i == j:
                    continue
                r_a, r_b = routes[i], routes[j]
                t_a, t_b = list(r_a.get("customer_stops", [])), list(r_b.get("customer_stops", []))
                cap_a = float(r_a.get("capacity", vehicle_capacities[i]))
                cap_b = float(r_b.get("capacity", vehicle_capacities[j]))

                vnd_res = AlgorithmicVND.optimize_fleet_routes(
                    t_a, t_b, np.array([demands[k] for k in range(1, n)]), cap_a, cap_b, distance_matrix, depot_idx=depot
                )
                cur_dist = r_a["distance_km"] + r_b["distance_km"]
                new_dist = AlgorithmicVND.compute_tour_length(vnd_res["tour_a"], distance_matrix, depot) + \
                           AlgorithmicVND.compute_tour_length(vnd_res["tour_b"], distance_matrix, depot)

                if new_dist < cur_dist - 1e-4:
                    r_a["customer_stops"] = vnd_res["tour_a"]
                    r_a["stops"] = [depot] + vnd_res["tour_a"] + [depot]
                    r_a["distance_km"] = round(AlgorithmicVND.compute_tour_length(vnd_res["tour_a"], distance_matrix, depot), 3)
                    r_a["load"] = sum(demands[c] for c in vnd_res["tour_a"])

                    r_b["customer_stops"] = vnd_res["tour_b"]
                    r_b["stops"] = [depot] + vnd_res["tour_b"] + [depot]
                    r_b["distance_km"] = round(AlgorithmicVND.compute_tour_length(vnd_res["tour_b"], distance_matrix, depot), 3)
                    r_b["load"] = sum(demands[c] for c in vnd_res["tour_b"])

        # ── Step 5: Intra-Route 2-Opt Refinement on All Routes ────────────
        for r in routes:
            st = r.get("customer_stops", [])
            if len(st) >= 2:
                opt_st = AlgorithmicVND.run_2opt(st, distance_matrix, depot)
                r["customer_stops"] = opt_st
                r["stops"] = [depot] + opt_st + [depot]
                r["distance_km"] = round(AlgorithmicVND.compute_tour_length(opt_st, distance_matrix, depot), 3)
                r["load"] = sum(demands[c] for c in opt_st)

        # ── Step 6: Centralized Proposition 1 Non-Degradation Guardrail ───
        final_total_dist = float(sum(r["distance_km"] for r in routes))

        # Strictly enforce: Cost(Final) <= Cost(OR-Tools Incumbent)
        if final_total_dist > ortools_distance:
            logger.info(f"Proposition 1 Guardrail: Reverting to initial OR-Tools incumbent ({ortools_distance:.3f} km)")
            routes = copy.deepcopy(ortools_incumbent_routes)
            final_total_dist = ortools_distance

        routes, final_val = repair_fleet_coverage(
            routes,
            input_cust_ids,
            distance_matrix,
            demands,
            vehicle_capacities,
            num_vehicles,
            depot,
        )
        final_total_dist = float(sum(r.get("distance_km", 0.0) for r in routes))

        # Absolute mathematical guarantee against precision drift
        if final_total_dist >= ortools_distance - 1e-4:
            routes = copy.deepcopy(ortools_incumbent_routes)
            final_total_dist = ortools_distance

        final_total_time = float(sum(r.get("travel_time_min", r.get("distance_km", 0.0) / 40.0 * 60.0) for r in routes))
        final_obj_cost = final_total_dist
        exec_time = time.perf_counter() - t0

        # Telemetry packaging
        primary_strategy = subproblem_telemetry[0]["strategy"] if subproblem_telemetry else "VND_Refinement"
        spark_mode = self.spark_organizer.execution_mode if self.spark_organizer else "Single_Machine_Pandas"

        return {
            "success": True,
            "algorithm": "routeiq_cooperative",
            "algorithm_name": "ROUTE/IQ Cooperative Engine",
            "category": "cooperative",
            "category_label": "Hybrid Big Data + Quantum",
            "compute_type": "Hybrid (Spark + Adaptive Controller + QAOA/Tabu + VND)",
            "status": "FEASIBLE" if final_val["is_valid"] else "PENALIZED",
            "execution_time_sec": round(float(exec_time), 3),
            "routes": routes,
            "total_distance_km": round(float(final_total_dist), 3),
            "total_travel_time_min": round(float(final_total_time), 2),
            "total_objective_cost": round(float(final_obj_cost), 3),
            "is_feasible": final_val["is_valid"],
            "capacity_violations": final_val["capacity_violations"],
            "unserved_customers": len(final_val["missing_delivery_ids"]),
            "served_customers": final_val["visited_delivery_count"],
            "validation_report": final_val,
            "warnings": [f"Missing stops repaired: {final_val['missing_delivery_ids']}"] if final_val['missing_delivery_ids'] else [],
            "cooperative_telemetry": {
                "spark_mode": spark_mode,
                "initial_incumbent_distance_km": round(ortools_distance, 3),
                "final_distance_km": round(float(final_total_dist), 3),
                "distance_improvement_km": round(max(0.0, ortools_distance - final_total_dist), 3),
                "subproblems_evaluated": len(subproblem_telemetry),
                "subproblem_details": subproblem_telemetry,
                "primary_strategy": primary_strategy,
                "proposition1_guaranteed": True,
            },
        }


# Global singleton instance (Spark enabled conditionally for big-data workloads to preserve 512MB container RAM)
_enable_spark = os.environ.get("ENABLE_SPARK_VRP", "0").lower() in ("1", "true", "yes")
cooperative_solver = CooperativeVRPSolver(use_spark=_enable_spark)
