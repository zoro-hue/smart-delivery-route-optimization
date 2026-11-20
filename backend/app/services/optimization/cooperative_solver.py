"""
ROUTE/IQ Cooperative Optimization Engine Solver Service.
Integrates:
- Pillar 1: Apache Spark Workload Decomposition & Spatial Partitioning
- Pillar 2: Variational Quantum Candidate Generation (Fast QAOA) & Classical Metaheuristics
- Multi-Start Heuristic Initialization Pool (OR-Tools, Clarke-Wright, Spark Polar Sweep, Tabu)
- Deep Algorithmic Variable Neighborhood Descent (2-opt*, Or-opt, Cross-Exchange, Relocate, Swap)
- Adaptive Large Neighborhood Search (ALNS Ruin-and-Recreate: Shaw Spatial & Worst Detour Removal)
- Centralized Non-Degradation Guardrail (Proposition 1)

This service implements the complete end-to-end cooperative architecture established in
Phases AB, AC, and AD for production deployment in ROUTE/IQ.
"""

import os
import sys
import uuid
import time
import math
import copy
import logging
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import pandas as pd

# Ensure project root is in sys.path for phase_v and phase_ab imports
_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)
_backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from app.services.optimization.classical_solver import classical_solver
from app.services.optimization.route_validator import repair_fleet_coverage, validate_fleet_coverage
from app.services.optimization.neighborhood_search import (
    RouteEvaluator,
    AdvancedNeighborhoodSearch,
)
from app.services.optimization.construction_heuristics import (
    DiverseConstructionHeuristics,
)
from phase_v_independent_quantum_validation.prototypes.algorithmic_vnd import AlgorithmicVND
from phase_ab_cooperative_optimization_engine.engine.cooperative_engine import CooperativeOptimizationEngine
from phase_ab_cooperative_optimization_engine.engine.spark_preprocessor import SparkWorkloadOrganizer
from phase_ab_cooperative_optimization_engine.engine.classical_engine import ClassicalOptimizationEngine

logger = logging.getLogger(__name__)


class CooperativeVRPSolver:
    """Production Cooperative Optimization Solver for ROUTE/IQ with Algorithmic Supremacy."""

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
        time_limit_sec: float = 0.5,
        objective_weights: Optional[Dict[str, float]] = None,
        travel_time_matrix: Optional[np.ndarray] = None,
        locations: Optional[List[Tuple[float, float]]] = None,
        strategy_override: Optional[str] = None,
        seed: int = 42,
        incumbent_solution: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Solves CVRP cooperatively using Hybrid Big Data + Classical + Quantum Pipeline:
        1. Spark spatial preprocessing and order ingestion validation.
        2. High-quality initial feasible fleet incumbent using OR-Tools CVRP.
        3. Multi-start candidate pool: Clarke-Wright (multiple gammas), Spark Polar Sweep, Tabu.
        4. Spatial route boundary decomposition via Spark polar/wedge partitioning.
        5. Quantum variational candidate generation (QAOA simulation) on boundary subproblems.
        6. Deep Algorithmic VND (2-opt*, Or-opt, Cross-Exchange, intra-route 2-opt).
        7. Adaptive Large Neighborhood Search (ALNS Ruin-and-Recreate) perturbation.
        8. Centralized Proposition 1 Non-Degradation Guardrail: Cost(Final) <= Cost(Incumbent).
        """
        t0 = time.perf_counter()
        solver_execution_id = str(uuid.uuid4())
        n = distance_matrix.shape[0]

        if demands is None:
            demands = [0] + [1] * (n - 1)
        if vehicle_capacities is None:
            vehicle_capacities = [100] * num_vehicles

        effective_limit = float(time_limit_sec) if time_limit_sec is not None else 0.5
        input_cust_ids = [i for i in range(n) if i != depot]

        # ── Pillar 1: Spark Preprocessing & Ingestion Validation ────────
        t0_spark = time.perf_counter()
        spark_mode = "Single_Machine_Vectorized"
        clean_df = None
        if locations and len(locations) == n:
            try:
                df_raw = pd.DataFrame({
                    "stop_id": [f"stop_{i}" for i in range(n)],
                    "latitude": [float(loc[0]) for loc in locations],
                    "longitude": [float(loc[1]) for loc in locations],
                    "demand": [float(d) for d in demands],
                })
                if self.spark_organizer:
                    clean_df, _ = self.spark_organizer.ingest_and_validate(df_raw)
                    spark_mode = self.spark_organizer.execution_mode
                else:
                    clean_df = df_raw.dropna().copy()
            except Exception as e:
                logger.debug(f"Spark ingestion notice: {e}")
        t_spark_ms = (time.perf_counter() - t0_spark) * 1000.0

        # ── Step 1: Classical Incumbent Generation (OR-Tools) ───────────
        t0_inc = time.perf_counter()
        if incumbent_solution and incumbent_solution.get("routes"):
            logger.info("Cooperative Solver: Using pre-computed incumbent solution.")
            incumbent_res = copy.deepcopy(incumbent_solution)
        else:
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

        # Use incumbent_res total_distance_km if available to prevent 1-mm float drift from summing rounded route distances
        if "total_distance_km" in incumbent_res and incumbent_res["total_distance_km"] > 0:
            ortools_distance = float(incumbent_res["total_distance_km"])
        else:
            ortools_distance = float(sum(r.get("distance_km", 0.0) for r in incumbent_routes))
        ortools_incumbent_routes = copy.deepcopy(incumbent_routes)
        t_incumbent_ms = (time.perf_counter() - t0_inc) * 1000.0

        # Extract stop lists from incumbent routes
        pool_candidates: List[List[List[int]]] = []
        ort_stops = [list(r.get("customer_stops", [])) for r in incumbent_routes]
        pool_candidates.append(ort_stops)

        # ── Step 2: Diverse Multi-Start Initial Candidate Pool ──────────
        t0_pool = time.perf_counter()

        # A. Parameterized Clarke-Wright Savings pool (varying gamma)
        try:
            cw_pool = DiverseConstructionHeuristics.clarke_wright_savings_pool(
                dist_matrix=distance_matrix,
                num_vehicles=num_vehicles,
                depot=depot,
                demands=demands,
                capacities=[float(c) for c in vehicle_capacities],
                gammas=[0.6, 0.8, 1.0, 1.2, 1.4, 1.6],
            )
            pool_candidates.extend(cw_pool)
        except Exception as e:
            logger.debug(f"CW pool generation notice: {e}")

        # B. Spark Polar Angle Sweep (angular spatial decomposition)
        if locations and len(locations) == n:
            try:
                sweep_candidate = DiverseConstructionHeuristics.spark_polar_sweep(
                    locations=locations,
                    num_vehicles=num_vehicles,
                    depot=depot,
                    demands=demands,
                    capacities=[float(c) for c in vehicle_capacities],
                    dist_matrix=distance_matrix,
                    num_rotations=12,
                )
                if any(len(r) > 0 for r in sweep_candidate):
                    pool_candidates.append(sweep_candidate)
            except Exception as e:
                logger.debug(f"Spark sweep generation notice: {e}")

        # C. Multi-Start Regret-3 and Regret-2 Insertion Construction
        try:
            regret3_candidate = DiverseConstructionHeuristics.regret_k_construction(
                dist_matrix=distance_matrix,
                num_vehicles=num_vehicles,
                depot=depot,
                demands=demands,
                capacities=[float(c) for c in vehicle_capacities],
                k_regret=3,
            )
            if any(len(r) > 0 for r in regret3_candidate):
                pool_candidates.append(regret3_candidate)
        except Exception as e:
            logger.debug(f"Regret-3 construction notice: {e}")

        try:
            regret2_candidate = DiverseConstructionHeuristics.regret_k_construction(
                dist_matrix=distance_matrix,
                num_vehicles=num_vehicles,
                depot=depot,
                demands=demands,
                capacities=[float(c) for c in vehicle_capacities],
                k_regret=2,
            )
            if any(len(r) > 0 for r in regret2_candidate):
                pool_candidates.append(regret2_candidate)
        except Exception as e:
            logger.debug(f"Regret-2 construction notice: {e}")

        # Select best candidate from initialization pool
        def evaluate_candidate(cand_routes: List[List[int]]) -> float:
            # Check coverage
            visited = [c for r in cand_routes for c in r]
            if len(visited) != len(input_cust_ids) or set(visited) != set(input_cust_ids):
                return float("inf")
            # Check capacity
            for v_idx, r in enumerate(cand_routes):
                cap = vehicle_capacities[v_idx] if v_idx < len(vehicle_capacities) else 100.0
                if sum(demands[c] for c in r) > cap:
                    return float("inf")
            return RouteEvaluator.fleet_distance(cand_routes, distance_matrix, depot)

        valid_pool = [(evaluate_candidate(c), c) for c in pool_candidates if evaluate_candidate(c) < float("inf")]
        if valid_pool:
            valid_pool.sort(key=lambda x: x[0])
            best_pool_dist, best_pool_routes = valid_pool[0]
            current_fleet_stops = copy.deepcopy(best_pool_routes)
        else:
            current_fleet_stops = copy.deepcopy(ort_stops)
            best_pool_dist = ortools_distance

        t_pool_ms = (time.perf_counter() - t0_pool) * 1000.0

        # Telemetry accumulators
        t_spatial_ms = 0.0
        t_boundary_ms = 0.0
        t_qaoa_circuit_ms = 0.0
        t_qaoa_sim_ms = 0.0
        t_qaoa_sampling_ms = 0.0
        t_repair_ms = 0.0
        subproblem_telemetry = []

        # ── Step 3: Spark Spatial Boundary Decomposition & QAOA Variational Cuts ──
        if len(current_fleet_stops) >= 2 and n >= 4:
            t0_spatial = time.perf_counter()
            logger.info("Cooperative Solver: Identifying spatial route boundaries for quantum exploration...")

            # Derive spatial centroids for each route
            route_centroids = []
            for c_nodes in current_fleet_stops:
                if not c_nodes:
                    route_centroids.append((0.0, 0.0))
                elif locations and len(locations) >= n:
                    avg_lat = float(np.mean([locations[c][0] for c in c_nodes]))
                    avg_lon = float(np.mean([locations[c][1] for c in c_nodes]))
                    route_centroids.append((avg_lat, avg_lon))
                else:
                    avg_r = float(np.mean([distance_matrix[depot, c] for c in c_nodes]))
                    route_centroids.append((avg_r, 0.0))

            pair_candidates = []
            for i in range(len(current_fleet_stops)):
                for j in range(i + 1, len(current_fleet_stops)):
                    ci, cj = route_centroids[i], route_centroids[j]
                    spatial_dist = math.hypot(ci[0] - cj[0], ci[1] - cj[1])
                    pair_candidates.append((spatial_dist, i, j))
            pair_candidates.sort(key=lambda x: x[0])
            t_spatial_ms = (time.perf_counter() - t0_spatial) * 1000.0

            # Optimize top boundary pairs (bounded to preserve sub-2s responsive latency)
            max_boundary_pairs = 1 if n <= 25 else 2
            for _, idx_a, idx_b in pair_candidates[:min(max_boundary_pairs, len(pair_candidates))]:
                t0_boundary = time.perf_counter()
                stops_a = list(current_fleet_stops[idx_a])
                stops_b = list(current_fleet_stops[idx_b])

                if not stops_a or not stops_b:
                    continue

                cap_a = float(vehicle_capacities[idx_a] if idx_a < len(vehicle_capacities) else 100.0)
                cap_b = float(vehicle_capacities[idx_b] if idx_b < len(vehicle_capacities) else 100.0)
                ca_pt = route_centroids[idx_a]
                cb_pt = route_centroids[idx_b]

                def boundary_distance(node_idx, own_c, other_c):
                    if locations and len(locations) >= n:
                        loc = locations[node_idx]
                        return math.hypot(loc[0] - other_c[0], loc[1] - other_c[1]) - math.hypot(loc[0] - own_c[0], loc[1] - own_c[1])
                    return distance_matrix[node_idx, depot]

                sorted_a = sorted(stops_a, key=lambda c: boundary_distance(c, ca_pt, cb_pt))
                sorted_b = sorted(stops_b, key=lambda c: boundary_distance(c, cb_pt, ca_pt))

                bound_a = sorted_a[:min(4, len(sorted_a))]
                bound_b = sorted_b[:min(4, len(sorted_b))]
                sub_custs = bound_a + bound_b
                sub_k = len(sub_custs)

                if sub_k < 4:
                    continue

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

                t_boundary_ms += (time.perf_counter() - t0_boundary) * 1000.0

                try:
                    opt_result = self.engine.optimize_subproblem(
                        dist_matrix=sub_dist,
                        demands=sub_demands,
                        cap_a=sub_cap_a,
                        cap_b=sub_cap_b,
                        c_a=np.array([ca_pt[0], ca_pt[1]]),
                        c_b=np.array([cb_pt[0], cb_pt[1]]),
                        strategy_override=strategy_override,
                        budget_evals=32,
                        seed=seed + idx_a * 10 + idx_b,
                    )

                    t_qaoa_circuit_ms += opt_result.get("circuit_build_time_ms", 0.0)
                    t_qaoa_sim_ms += opt_result.get("simulation_time_ms", 0.0)
                    t_qaoa_sampling_ms += opt_result.get("sampling_time_ms", 0.0)
                    t_repair_ms += opt_result.get("repair_time_ms", 0.0)

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

                    if opt_result.get("guardrail_accepted"):
                        tour_a_sub = opt_result.get("final_tour_a", [])
                        tour_b_sub = opt_result.get("final_tour_b", [])

                        new_custs_a = [sub_to_node[s] for s in tour_a_sub if s in sub_to_node]
                        new_custs_b = [sub_to_node[s] for s in tour_b_sub if s in sub_to_node]

                        cand_set_a = unaffected_a + new_custs_a
                        cand_set_b = unaffected_b + new_custs_b

                        if sum(demands[c] for c in cand_set_a) <= cap_a and sum(demands[c] for c in cand_set_b) <= cap_b:
                            opt_tour_a = AdvancedNeighborhoodSearch.run_2opt(cand_set_a, distance_matrix, depot)
                            opt_tour_b = AdvancedNeighborhoodSearch.run_2opt(cand_set_b, distance_matrix, depot)

                            orig_pair_dist = RouteEvaluator.tour_length(stops_a, distance_matrix, depot) + RouteEvaluator.tour_length(stops_b, distance_matrix, depot)
                            new_pair_dist = RouteEvaluator.tour_length(opt_tour_a, distance_matrix, depot) + RouteEvaluator.tour_length(opt_tour_b, distance_matrix, depot)

                            if new_pair_dist < orig_pair_dist - 1e-4:
                                current_fleet_stops[idx_a] = opt_tour_a
                                current_fleet_stops[idx_b] = opt_tour_b

                except Exception as e:
                    logger.warning(f"Cooperative subproblem optimization error for routes ({idx_a}, {idx_b}): {e}")

        # ── Step 4: Deep Variable Neighborhood Descent (VND) ────────────
        t0_vnd = time.perf_counter()
        current_fleet_stops = AdvancedNeighborhoodSearch.deep_vnd(
            current_fleet_stops,
            [float(c) for c in vehicle_capacities],
            demands,
            distance_matrix,
            depot=depot,
            max_iterations=30,
        )
        t_vnd_ms = (time.perf_counter() - t0_vnd) * 1000.0

        # ── Step 5: Adaptive Large Neighborhood Search (ALNS Ruin-and-Recreate) ───
        t0_alns = time.perf_counter()
        alns_iters = min(40, max(20, n))
        current_fleet_stops = AdvancedNeighborhoodSearch.alns_ruin_and_recreate(
            incumbent_routes=current_fleet_stops,
            capacities=[float(c) for c in vehicle_capacities],
            demands=demands,
            dist_matrix=distance_matrix,
            depot=depot,
            locations=locations,
            max_iterations=alns_iters,
            seed=seed,
        )
        # Final hierarchical polish
        current_fleet_stops = AdvancedNeighborhoodSearch.deep_vnd(
            current_fleet_stops,
            [float(c) for c in vehicle_capacities],
            demands,
            distance_matrix,
            depot=depot,
            max_iterations=10,
        )
        t_alns_ms = (time.perf_counter() - t0_alns) * 1000.0

        # Format routes for validation & guardrail
        final_candidate_routes = []
        for v_idx, c_stops in enumerate(current_fleet_stops):
            dist_k = RouteEvaluator.tour_length(c_stops, distance_matrix, depot)
            final_candidate_routes.append({
                "vehicle_id": v_idx + 1,
                "stops": [depot] + c_stops + [depot],
                "customer_stops": c_stops,
                "distance_km": round(dist_k, 3),
                "load": sum(demands[c] for c in c_stops),
                "capacity": vehicle_capacities[v_idx] if v_idx < len(vehicle_capacities) else 100,
            })

        # Repair coverage defensively if any node was omitted
        final_candidate_routes, cand_val = repair_fleet_coverage(
            final_candidate_routes,
            input_cust_ids,
            distance_matrix,
            demands,
            vehicle_capacities,
            num_vehicles,
            depot,
        )
        cand_total_dist = float(sum(r.get("distance_km", 0.0) for r in final_candidate_routes))

        # ── Step 6: Centralized Proposition 1 Non-Degradation Guardrail ───
        t0_guard = time.perf_counter()
        is_supremacy_winner = False
        improvement_km = 0.0
        improvement_pct = 0.0
        solution_origin = "INHERITED_INCUMBENT_BASELINE"

        # Check candidate validity & cost relative to OR-Tools incumbent
        # Strictly enforce: Cost(Final) <= Cost(OR-Tools Incumbent) + 1e-4
        if cand_val["is_valid"] and cand_total_dist < ortools_distance - 1e-3:
            # Genuine supremacy improvement over OR-Tools
            is_supremacy_winner = True
            solution_origin = "SUPREMACY_IMPROVED"
            routes = final_candidate_routes
            final_total_dist = cand_total_dist
            improvement_km = round(ortools_distance - final_total_dist, 3)
            improvement_pct = round((improvement_km / ortools_distance) * 100.0, 2)
            logger.info(
                f"Proposition 1 Supremacy: Cooperative Engine outperformed OR-Tools! "
                f"{ortools_distance:.3f} km -> {final_total_dist:.3f} km (-{improvement_km:.3f} km, -{improvement_pct:.2f}%)"
            )
        elif cand_val["is_valid"] and cand_total_dist <= ortools_distance + 1e-4:
            # Reached identical or effectively equal cost independently
            # Verify if route stop sequences are identical or an alternative optimum
            cand_stops = [tuple(r.get("stops", [])) for r in final_candidate_routes]
            ortools_stops = [tuple(r.get("stops", [])) for r in ortools_incumbent_routes]

            # Compare sets of route sequences (direction/index invariant)
            cand_set = {frozenset([s, tuple(reversed(s))]) for s in cand_stops}
            ortools_set = {frozenset([s, tuple(reversed(s))]) for s in ortools_stops}

            if sorted(cand_stops) == sorted(ortools_stops) or cand_set == ortools_set:
                solution_origin = "INDEPENDENT_IDENTICAL_CONVERGENCE"
            else:
                solution_origin = "INDEPENDENT_ALTERNATIVE_OPTIMUM"

            # Preserve Cooperative Engine's independently discovered routes
            routes = final_candidate_routes
            final_total_dist = cand_total_dist
            improvement_km = round(max(0.0, ortools_distance - final_total_dist), 3)
            improvement_pct = round((improvement_km / ortools_distance) * 100.0, 2) if ortools_distance > 0 else 0.0
            logger.info(
                f"Proposition 1 Independent Discovery ({solution_origin}): "
                f"Cooperative Engine retained independent routes at {final_total_dist:.3f} km (OR-Tools: {ortools_distance:.3f} km)"
            )
        else:
            # Incumbent was strictly superior or candidate invalid; adopt incumbent baseline
            solution_origin = "INHERITED_INCUMBENT_BASELINE"
            logger.info(
                f"Proposition 1 Guardrail: Adopting OR-Tools incumbent baseline ({ortools_distance:.3f} km)"
            )
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

        repaired_dist = float(sum(r.get("distance_km", 0.0) for r in routes))
        if repaired_dist > ortools_distance + 1e-4:
            # Enforce non-degradation: never return a solution worse than OR-Tools incumbent
            routes = copy.deepcopy(ortools_incumbent_routes)
            final_total_dist = ortools_distance
            is_supremacy_winner = False
            solution_origin = "INHERITED_INCUMBENT_BASELINE"
            improvement_km = 0.0
            improvement_pct = 0.0
        else:
            final_total_dist = repaired_dist
        t_guardrail_ms = (time.perf_counter() - t0_guard) * 1000.0

        # ── Step 7: Route Reconstruction & Telemetry Compilation ─────────
        t0_recon = time.perf_counter()
        for v_idx, r in enumerate(routes, 1):
            r["vehicle_id"] = v_idx
            r["total_distance_km"] = r.get("distance_km", 0.0)
            if "travel_time_min" not in r:
                r["travel_time_min"] = round(r["distance_km"] / 40.0 * 60.0, 1)

        final_total_time = float(
            sum(r.get("travel_time_min", r.get("distance_km", 0.0) / 40.0 * 60.0) for r in routes)
        )
        final_obj_cost = final_total_dist
        t_reconstruct_ms = (time.perf_counter() - t0_recon) * 1000.0

        exec_time = time.perf_counter() - t0

        primary_strategy = (
            subproblem_telemetry[0]["strategy"]
            if subproblem_telemetry
            else ("ALNS_Ruin_Recreate_Supremacy" if is_supremacy_winner else "Adaptive_VND_Refinement")
        )

        profiling_breakdown = {
            "spark_preprocessing_ms": round(t_spark_ms, 2),
            "classical_incumbent_ms": round(t_incumbent_ms, 2),
            "initialization_pool_ms": round(t_pool_ms, 2),
            "spatial_decomposition_ms": round(t_spatial_ms, 2),
            "boundary_extraction_ms": round(t_boundary_ms, 2),
            "qaoa_circuit_construction_ms": round(t_qaoa_circuit_ms, 2),
            "qaoa_simulation_and_sampling_ms": round(t_qaoa_sim_ms + t_qaoa_sampling_ms, 2),
            "candidate_feasibility_repair_ms": round(t_repair_ms, 2),
            "vnd_local_search_ms": round(t_vnd_ms, 2),
            "alns_ruin_recreate_ms": round(t_alns_ms, 2),
            "proposition1_guardrail_ms": round(t_guardrail_ms, 2),
            "route_reconstruction_ms": round(t_reconstruct_ms, 2),
            "total_cooperative_time_ms": round(exec_time * 1000.0, 2),
        }

        timings_summary = {
            "spark_preprocessing_sec": round(t_spark_ms / 1000.0, 4),
            "qaoa_quantum_simulation_sec": round((t_qaoa_circuit_ms + t_qaoa_sim_ms + t_qaoa_sampling_ms) / 1000.0, 4),
            "classical_optimization_sec": round((t_incumbent_ms + t_pool_ms + t_vnd_ms + t_alns_ms) / 1000.0, 4),
            "total_execution_sec": round(float(exec_time), 4),
        }

        algo_status = (
            "SUPREMACY_WINNER"
            if is_supremacy_winner
            else ("FEASIBLE" if final_val["is_valid"] else "PENALIZED")
        )

        return {
            "success": True,
            "algorithm": "routeiq_cooperative",
            "algorithm_name": "ROUTE/IQ Cooperative Engine",
            "execution_id": solver_execution_id,
            "solution_origin": solution_origin,
            "category": "cooperative",
            "category_label": "Hybrid Big Data + Quantum",
            "compute_type": "Hybrid (Spark + QAOA + Adaptive Deep VND + ALNS)",
            "status": algo_status,
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
                "execution_id": solver_execution_id,
                "solution_origin": solution_origin,
                "spark_mode": spark_mode,
                "initial_incumbent_distance_km": round(ortools_distance, 3),
                "final_distance_km": round(float(final_total_dist), 3),
                "distance_improvement_km": round(max(0.0, ortools_distance - final_total_dist), 3),
                "improvement_percentage": improvement_pct,
                "supremacy_winner": is_supremacy_winner,
                "subproblems_evaluated": len(subproblem_telemetry),
                "subproblem_details": subproblem_telemetry,
                "primary_strategy": primary_strategy,
                "proposition1_guaranteed": True,
                "profiling_breakdown": profiling_breakdown,
                "timings": timings_summary,
            },
        }


# Global singleton instance (Spark enabled conditionally for big-data workloads to preserve 512MB container RAM)
_enable_spark = os.environ.get("ENABLE_SPARK_VRP", "0").lower() in ("1", "true", "yes")
cooperative_solver = CooperativeVRPSolver(use_spark=_enable_spark)
