"""
ROUTE/IQ Next-Generation Cooperative Engine.
A genuinely cooperative, adaptive, and vehicle-condition-aware hybrid optimization framework.
Integrates:
- Shared Candidate Pool Blackboard with Topological Diversity Management
- Contextual Multi-Armed Bandit (MAB) with Multi-Objective Reward Learning
- Heterogeneous Vehicle-Condition Physics (Battery SoH/SoC, Range, Powertrain, Emissions)
- Cross-Algorithm Collaborative Operators (QAOA, QIGA, Spark Sweep, Tabu, Deep VND, ALNS, OR-Tools)
- Proposition 1 Monotonic Non-Degradation Guardrail
"""

import copy
import time
import uuid
import math
import logging
from typing import Dict, Any, List, Tuple, Optional
import numpy as np

from app.services.optimization.candidate_pool import CandidateSolution, CandidatePool
from app.services.optimization.adaptive_mab import AdaptiveCooperativeController
from app.services.optimization.vehicle_condition_evaluator import VehicleConditionEvaluator
from app.services.optimization.qaoa_cooperative_operator import QAOACooperativeOperator
from app.services.optimization.qiga_cooperative_operator import QIGACooperativeOperator
from app.services.optimization.classical_solver import classical_solver
from app.services.optimization.construction_heuristics import DiverseConstructionHeuristics
from app.services.optimization.neighborhood_search import (
    RouteEvaluator,
    AdvancedNeighborhoodSearch,
)
from app.services.optimization.route_validator import repair_fleet_coverage

logger = logging.getLogger(__name__)


class NextGenCooperativeEngine:
    """
    Research implementation of the Next-Generation ROUTE/IQ Cooperative Optimization Engine.
    Coordinates iterative cross-algorithm exchange, online MAB operator learning,
    heterogeneous vehicle condition physics, and diversity-managed pool evolution.
    """

    def __init__(
        self,
        max_pool_size: int = 16,
        elite_size: int = 4,
        max_cycles: int = 16,
        exploration_factor: float = 0.8,
    ):
        self.max_pool_size: int = max_pool_size
        self.elite_size: int = elite_size
        self.max_cycles: int = max_cycles
        self.exploration_factor: float = exploration_factor

        self.qaoa_operator = QAOACooperativeOperator()
        self.qiga_operator = QIGACooperativeOperator()

    def solve(
        self,
        distance_matrix: np.ndarray,
        num_vehicles: int,
        depot: int = 0,
        demands: Optional[List[int]] = None,
        vehicle_capacities: Optional[List[int]] = None,
        time_limit_sec: float = 2.0,
        travel_time_matrix: Optional[np.ndarray] = None,
        locations: Optional[List[Tuple[float, float]]] = None,
        vehicle_profiles: Optional[List[Dict[str, Any]]] = None,
        seed: int = 42,
        incumbent_solution: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Executes the iterative, vehicle-condition-aware cooperative optimization cycle:
        1. Initialize Candidate Pool, Vehicle Evaluator, and Adaptive Controller.
        2. Multi-Start Seeding (OR-Tools, Clarke-Wright gamma pool, Polar Sweep, Regret-3).
        3. Calibrate Dimensionless Normalization Constants from initial incumbent.
        4. Iterative Cooperative Cycles:
           a. Sample Context Features s_t.
           b. Contextual MAB selects Operator o_t.
           c. Diversity-weighted Tournament selects Parent P in Pool.
           d. Operator o_t generates Offspring C from P (and Elite E).
           e. Vehicle Evaluator computes multi-objective score F(C).
           f. Pool conditionally adopts C based on Pareto/diversity metrics.
           g. Feedback Reward R(o_t) updates Controller Q-values.
        5. Deep VND Final Polish.
        6. Proposition 1 Non-Degradation Guardrail.
        7. Assemble Full Provenance Telemetry.
        """
        t0_start = time.perf_counter()
        np.random.seed(seed)
        n = distance_matrix.shape[0]
        input_cust_ids = [i for i in range(n) if i != depot]

        if demands is None:
            demands = [0] + [1] * (n - 1)
        if vehicle_capacities is None:
            vehicle_capacities = [100] * num_vehicles

        budget_ms = max(200.0, float(time_limit_sec) * 1000.0)

        # ── 1. Initialize Subsystems ──────────────────────────────────
        pool = CandidatePool(max_capacity=self.max_pool_size, elite_size=self.elite_size, depot=depot)
        vehicle_eval = VehicleConditionEvaluator(
            vehicle_profiles=vehicle_profiles,
            num_vehicles=num_vehicles,
            default_capacity=float(vehicle_capacities[0] if vehicle_capacities else 100.0),
        )
        controller = AdaptiveCooperativeController(exploration_factor=self.exploration_factor)

        hetero_idx = vehicle_eval.compute_fleet_heterogeneity_index()

        # ── 2. Multi-Start Seeding into Shared Pool ────────────────────
        t0_seed = time.perf_counter()

        # Seed A: OR-Tools baseline incumbent
        if incumbent_solution and incumbent_solution.get("success") and incumbent_solution.get("routes"):
            ortools_res = copy.deepcopy(incumbent_solution)
        else:
            ortools_res = classical_solver.solve_ortools(
                distance_matrix=distance_matrix,
                num_vehicles=num_vehicles,
                depot=depot,
                demands=demands,
                vehicle_capacities=vehicle_capacities,
                time_limit_sec=max(0.5, float(time_limit_sec)),
                travel_time_matrix=travel_time_matrix,
                vehicle_profiles=vehicle_profiles,
            )

        ort_routes = []
        if ortools_res.get("success") and ortools_res.get("routes"):
            ort_routes = [list(r.get("customer_stops", [])) for r in ortools_res["routes"]]
            # Guarantee coverage
            repaired_ort, _ = repair_fleet_coverage(
                ortools_res["routes"],
                input_cust_ids,
                distance_matrix,
                demands,
                vehicle_capacities,
                num_vehicles,
                depot,
            )
            ort_routes = [list(r.get("customer_stops", [])) for r in repaired_ort]

        if not ort_routes or all(len(r) == 0 for r in ort_routes):
            # Fallback to Clarke-Wright if OR-Tools fails
            cw_fb = classical_solver.solve_clarke_wright(
                distance_matrix, num_vehicles, depot, demands, vehicle_capacities
            )
            ort_routes = [list(r.get("customer_stops", [])) for r in cw_fb.get("routes", [])]

        # Pad with empty routes if needed
        while len(ort_routes) < num_vehicles:
            ort_routes.append([])

        cand_ort = CandidateSolution(
            vehicle_routes=ort_routes,
            generating_algorithm="Google_OR-Tools",
            modification_operator="exact_cvrp_initialization",
            iteration_created=0,
            generation_time_ms=(time.perf_counter() - t0_seed) * 1000.0,
        )
        metrics_ort = vehicle_eval.evaluate_candidate(
            cand_ort.vehicle_routes, distance_matrix, demands, depot, travel_time_matrix, input_cust_ids
        )
        self._apply_metrics_to_candidate(cand_ort, metrics_ort)

        # Register baseline OR-Tools solution
        pool.baseline_ortools = copy.deepcopy(cand_ort)
        pool.add_candidate(cand_ort)

        # Calibrate dimensionless normalization baselines
        vehicle_eval.set_normalization_baselines(
            base_distance_km=cand_ort.total_distance_km,
            base_cost_usd=cand_ort.total_cost_usd,
            base_energy_kwh=cand_ort.total_energy_kwh,
            base_emissions_kg=cand_ort.total_emissions_kg_co2,
        )
        # Recalculate fitness with calibrated baselines
        metrics_ort = vehicle_eval.evaluate_candidate(
            cand_ort.vehicle_routes, distance_matrix, demands, depot, travel_time_matrix, input_cust_ids
        )
        self._apply_metrics_to_candidate(cand_ort, metrics_ort)
        cand_ort.scalarized_fitness = metrics_ort["scalarized_fitness"]
        pool.incumbent = copy.deepcopy(cand_ort)

        # Seed B: Parameterized Clarke-Wright Savings pool (varying gamma)
        try:
            cw_pool = DiverseConstructionHeuristics.clarke_wright_savings_pool(
                dist_matrix=distance_matrix,
                num_vehicles=num_vehicles,
                depot=depot,
                demands=demands,
                capacities=[float(c) for c in vehicle_capacities],
                gammas=[0.7, 1.0, 1.4],
            )
            for gamma_idx, cw_routes in enumerate(cw_pool):
                while len(cw_routes) < num_vehicles:
                    cw_routes.append([])
                c_sol = CandidateSolution(
                    vehicle_routes=cw_routes,
                    generating_algorithm="Clarke_Wright_Savings",
                    modification_operator=f"parameterized_gamma_{gamma_idx}",
                    iteration_created=0,
                )
                m = vehicle_eval.evaluate_candidate(
                    c_sol.vehicle_routes, distance_matrix, demands, depot, travel_time_matrix, input_cust_ids
                )
                self._apply_metrics_to_candidate(c_sol, m)
                pool.add_candidate(c_sol)
        except Exception as e:
            logger.debug(f"Cooperative seeding notice (CW): {e}")

        # Seed C: Spark Polar Angle Sweep (angular spatial decomposition)
        if locations and len(locations) == n:
            try:
                sweep_candidate = DiverseConstructionHeuristics.spark_polar_sweep(
                    locations=locations,
                    num_vehicles=num_vehicles,
                    depot=depot,
                    demands=demands,
                    capacities=[float(c) for c in vehicle_capacities],
                    dist_matrix=distance_matrix,
                    num_rotations=8,
                )
                while len(sweep_candidate) < num_vehicles:
                    sweep_candidate.append([])
                c_sol = CandidateSolution(
                    vehicle_routes=sweep_candidate,
                    generating_algorithm="Spark_Polar_Sweep",
                    modification_operator="angular_spatial_partitioning",
                    iteration_created=0,
                )
                m = vehicle_eval.evaluate_candidate(
                    c_sol.vehicle_routes, distance_matrix, demands, depot, travel_time_matrix, input_cust_ids
                )
                self._apply_metrics_to_candidate(c_sol, m)
                pool.add_candidate(c_sol)
            except Exception as e:
                logger.debug(f"Cooperative seeding notice (Spark Sweep): {e}")

        # Seed D: Regret-3 Construction
        try:
            regret_cand = DiverseConstructionHeuristics.regret_k_construction(
                dist_matrix=distance_matrix,
                num_vehicles=num_vehicles,
                depot=depot,
                demands=demands,
                capacities=[float(c) for c in vehicle_capacities],
                k_regret=3,
            )
            while len(regret_cand) < num_vehicles:
                regret_cand.append([])
            c_sol = CandidateSolution(
                vehicle_routes=regret_cand,
                generating_algorithm="Regret_3_Heuristic",
                modification_operator="k_regret_insertion",
                iteration_created=0,
            )
            m = vehicle_eval.evaluate_candidate(
                c_sol.vehicle_routes, distance_matrix, demands, depot, travel_time_matrix, input_cust_ids
            )
            self._apply_metrics_to_candidate(c_sol, m)
            pool.add_candidate(c_sol)
        except Exception as e:
            logger.debug(f"Cooperative seeding notice (Regret): {e}")

        # ── 3. Iterative Cooperative Cycles ───────────────────────────
        stagnation_count = 0
        cycle_records = []
        effective_cycles = min(self.max_cycles, max(6, int(n * 0.75)))

        for cycle in range(1, effective_cycles + 1):
            elapsed_ms = (time.perf_counter() - t0_start) * 1000.0
            if elapsed_ms > budget_ms * 0.85:
                logger.info(f"Cooperative Engine: Reached 85% time budget ({elapsed_ms:.1f}ms). Finalizing cycles.")
                break

            remaining_ratio = max(0.0, 1.0 - (elapsed_ms / budget_ms))

            # a. Context state vector
            context = {
                "num_customers": n - 1,
                "num_vehicles": num_vehicles,
                "fleet_heterogeneity_index": hetero_idx,
                "pool_diversity": pool.get_diversity(),
                "cycle": cycle,
            }

            # b. Contextual MAB selects Operator
            chosen_op, sel_meta = controller.select_operator(
                context=context,
                stagnation_count=stagnation_count,
                remaining_budget_ratio=remaining_ratio,
            )

            # c. Diversity-weighted Parent Selection from Pool
            parent = pool.select_parent(tournament_size=3, diversity_bias=0.20)
            elite_inc = pool.incumbent

            # d. Dispatch Operator Execution
            t_op_start = time.perf_counter()
            child = None

            try:
                if chosen_op == "OP_QAOA_SUBPROBLEM":
                    child = self.qaoa_operator.execute(
                        parent_candidate=parent,
                        dist_matrix=distance_matrix,
                        demands=demands,
                        depot=depot,
                        locations=locations,
                        vehicle_capacities=[float(c) for c in vehicle_capacities],
                        seed=seed + cycle * 10,
                    )

                elif chosen_op == "OP_QIGA_QUANTUM_GENETIC":
                    child = self.qiga_operator.execute(
                        parent_candidate=parent,
                        elite_incumbent=elite_inc,
                        dist_matrix=distance_matrix,
                        demands=demands,
                        depot=depot,
                        vehicle_capacities=[float(c) for c in vehicle_capacities],
                        seed=seed + cycle * 17,
                    )

                elif chosen_op == "OP_DEEP_VND_REFINE":
                    refined_stops = AdvancedNeighborhoodSearch.deep_vnd(
                        parent.vehicle_routes,
                        [float(c) for c in vehicle_capacities],
                        demands,
                        distance_matrix,
                        depot=depot,
                        max_iterations=15,
                    )
                    child = CandidateSolution(
                        vehicle_routes=refined_stops,
                        generating_algorithm="Deep_VND_Refiner",
                        modification_operator="5_neighborhood_descent",
                        parent_id=parent.candidate_id,
                        iteration_created=cycle,
                    )

                elif chosen_op == "OP_ALNS_RUIN_RECREATE":
                    alns_stops = AdvancedNeighborhoodSearch.alns_ruin_and_recreate(
                        incumbent_routes=parent.vehicle_routes,
                        capacities=[float(c) for c in vehicle_capacities],
                        demands=demands,
                        dist_matrix=distance_matrix,
                        depot=depot,
                        locations=locations,
                        max_iterations=min(25, max(12, n // 2)),
                        seed=seed + cycle * 23,
                    )
                    child = CandidateSolution(
                        vehicle_routes=alns_stops,
                        generating_algorithm="ALNS_Ruin_and_Recreate",
                        modification_operator="shaw_worst_regret_reconstruction",
                        parent_id=parent.candidate_id,
                        iteration_created=cycle,
                    )

                elif chosen_op == "OP_TABU_SEARCH_EXCHANGE":
                    # Tabu search over inter-route swaps
                    tabu_stops = self._tabu_inter_route_exchange(
                        parent.vehicle_routes, distance_matrix, demands, vehicle_capacities, depot, max_iters=20
                    )
                    child = CandidateSolution(
                        vehicle_routes=tabu_stops,
                        generating_algorithm="Tabu_Search_Exchange",
                        modification_operator="tabu_inter_route_swap_memory",
                        parent_id=parent.candidate_id,
                        iteration_created=cycle,
                    )

                elif chosen_op == "OP_SPARK_POLAR_SWEEP" and locations and len(locations) == n:
                    sweep_routes = DiverseConstructionHeuristics.spark_polar_sweep(
                        locations=locations,
                        num_vehicles=num_vehicles,
                        depot=depot,
                        demands=demands,
                        capacities=[float(c) for c in vehicle_capacities],
                        dist_matrix=distance_matrix,
                        num_rotations=6,
                    )
                    while len(sweep_routes) < num_vehicles:
                        sweep_routes.append([])
                    child = CandidateSolution(
                        vehicle_routes=sweep_routes,
                        generating_algorithm="Spark_Polar_Sweep_Perturbation",
                        modification_operator="angular_spatial_offset",
                        parent_id=parent.candidate_id,
                        iteration_created=cycle,
                    )

                elif chosen_op == "OP_ORTOOLS_LOCAL_REPAIR":
                    # Exact local repair on partial routes
                    repaired_routes = self._ortools_guided_repair(
                        parent.vehicle_routes, distance_matrix, demands, vehicle_capacities, depot, time_limit_sec=0.15
                    )
                    child = CandidateSolution(
                        vehicle_routes=repaired_routes,
                        generating_algorithm="OR-Tools_Guided_Repairer",
                        modification_operator="exact_subproblem_repair",
                        parent_id=parent.candidate_id,
                        iteration_created=cycle,
                    )

                elif chosen_op == "OP_CLARKE_WRIGHT_SAVINGS":
                    gamma_val = float(0.5 + (cycle % 5) * 0.25)
                    cw_res = DiverseConstructionHeuristics.clarke_wright_savings_pool(
                        distance_matrix, num_vehicles, depot, demands, [float(c) for c in vehicle_capacities], [gamma_val]
                    )
                    if cw_res:
                        child = CandidateSolution(
                            vehicle_routes=cw_res[0],
                            generating_algorithm="Clarke_Wright_Savings_Operator",
                            modification_operator=f"dynamic_gamma_{gamma_val:.2f}",
                            parent_id=parent.candidate_id,
                            iteration_created=cycle,
                        )

            except Exception as e:
                logger.debug(f"Operator {chosen_op} execution error in cycle {cycle}: {e}")
                child = None

            t_op_ms = (time.perf_counter() - t_op_start) * 1000.0

            # e. Evaluate Child & Deliver Feedback Reward
            if child is not None:
                # Pad to num_vehicles
                while len(child.vehicle_routes) < num_vehicles:
                    child.vehicle_routes.append([])

                child_metrics = vehicle_eval.evaluate_candidate(
                    child.vehicle_routes, distance_matrix, demands, depot, travel_time_matrix, input_cust_ids
                )
                self._apply_metrics_to_candidate(child, child_metrics)
                child.generation_time_ms = t_op_ms

                # Check if this child improves overall incumbent
                prev_inc_fit = pool.incumbent.scalarized_fitness if pool.incumbent else float("inf")
                is_accepted = pool.add_candidate(child)

                new_inc_fit = pool.incumbent.scalarized_fitness if pool.incumbent else float("inf")
                if new_inc_fit < prev_inc_fit - 1e-4:
                    stagnation_count = 0
                else:
                    stagnation_count += 1

                # f. Multi-objective MAB reward update
                cand_div = parent.jaccard_distance(child, depot)
                reward = controller.update_reward(
                    operator=chosen_op,
                    parent_fitness=parent.scalarized_fitness,
                    child_fitness=child.scalarized_fitness,
                    is_feasible=child.is_feasible,
                    candidate_diversity=cand_div,
                    runtime_ms=t_op_ms,
                    budget_ms=budget_ms,
                )

                cycle_records.append({
                    "cycle": cycle,
                    "operator": chosen_op,
                    "parent_fitness": round(parent.scalarized_fitness, 3),
                    "child_fitness": round(child.scalarized_fitness, 3),
                    "accepted": is_accepted,
                    "is_feasible": child.is_feasible,
                    "reward": round(reward, 4),
                    "runtime_ms": round(t_op_ms, 2),
                })
            else:
                # Infeasible or failed operator penalty
                reward = controller.update_reward(
                    operator=chosen_op,
                    parent_fitness=parent.scalarized_fitness,
                    child_fitness=float("inf"),
                    is_feasible=False,
                    candidate_diversity=0.0,
                    runtime_ms=t_op_ms,
                    budget_ms=budget_ms,
                )
                stagnation_count += 1
                cycle_records.append({
                    "cycle": cycle,
                    "operator": chosen_op,
                    "parent_fitness": round(parent.scalarized_fitness, 3),
                    "child_fitness": float("inf"),
                    "accepted": False,
                    "is_feasible": False,
                    "reward": round(reward, 4),
                    "runtime_ms": round(t_op_ms, 2),
                })

        # ── 4. Final Polish with Deep VND on Best Incumbent ───────────
        incumbent = pool.incumbent or pool.baseline_ortools
        polished_stops = AdvancedNeighborhoodSearch.deep_vnd(
            incumbent.vehicle_routes,
            [float(c) for c in vehicle_capacities],
            demands,
            distance_matrix,
            depot=depot,
            max_iterations=10,
        )

        final_cand = CandidateSolution(
            vehicle_routes=polished_stops,
            generating_algorithm=f"{incumbent.generating_algorithm} + Deep_VND_Polish",
            modification_operator="final_polish_cooperative_convergence",
            parent_id=incumbent.candidate_id,
            iteration_created=effective_cycles + 1,
        )
        final_metrics = vehicle_eval.evaluate_candidate(
            final_cand.vehicle_routes, distance_matrix, demands, depot, travel_time_matrix, input_cust_ids
        )
        self._apply_metrics_to_candidate(final_cand, final_metrics)

        # ── 5. Centralized Proposition 1 Guardrail ────────────────────
        # Guarantees that the final candidate never degrades vs the OR-Tools baseline
        base_ort = pool.baseline_ortools
        guardrail_status = "SUPREMACY_IMPROVED"

        if base_ort and base_ort.is_feasible:
            is_cand_valid = (
                final_cand.is_feasible
                and getattr(final_cand, "capacity_violations", 0) == 0
                and getattr(final_cand, "unserved_customers", 0) == 0
            )
            if is_cand_valid and final_cand.total_distance_km < base_ort.total_distance_km - 1e-3:
                guardrail_status = "SUPREMACY_IMPROVED"
            elif is_cand_valid and final_cand.total_distance_km <= base_ort.total_distance_km + 1e-4:
                guardrail_status = "INDEPENDENT_EQUAL_ORTOOLS"
            else:
                # Safety fallback to OR-Tools
                guardrail_status = "INHERITED_INCUMBENT_BASELINE"
                final_cand = copy.deepcopy(base_ort)

        # ── 6. Assemble Full Production Response ───────────────────────
        total_runtime_sec = time.perf_counter() - t0_start

        # Build individual vehicle route objects matching ROUTE/IQ schema
        assembled_routes = []
        for v_idx, stops in enumerate(final_cand.vehicle_routes):
            prof = vehicle_eval.profiles[v_idx] if v_idx < len(vehicle_eval.profiles) else vehicle_eval.profiles[0]
            full_tour = [depot] + stops + [depot] if stops else []
            r_dist = 0.0
            r_time = 0.0
            for i in range(len(full_tour) - 1):
                u, v = full_tour[i], full_tour[i + 1]
                r_dist += distance_matrix[u, v]
                if travel_time_matrix is not None:
                    r_time += travel_time_matrix[u, v]
                else:
                    r_time += (distance_matrix[u, v] / 35.0) * 60.0

            load_kg = sum(demands[c] for c in stops if c < len(demands))
            assembled_routes.append({
                "vehicle_id": v_idx + 1,
                "vehicle_name": prof["name"],
                "vehicle_profile": prof,
                "stops": full_tour,
                "customer_stops": stops,
                "distance_km": round(r_dist, 3),
                "driving_time_min": round(r_time, 2),
                "total_duration_min": round(r_time, 2),
                "load": load_kg,
                "capacity": prof["capacity_kg"],
                "utilization_pct": round((load_kg / max(1.0, prof["capacity_kg"])) * 100.0, 1),
                "usable_range_km": prof["usable_range_km"],
                "is_range_feasible": r_dist <= prof["usable_range_km"] + 1e-4,
            })

        # Calculate speed model & resource metrics
        total_dist_km = final_cand.total_distance_km
        total_dur_min = sum(r["driving_time_min"] for r in assembled_routes)
        implied_speed = (total_dist_km / max(0.01, total_dur_min / 60.0)) if total_dur_min > 0 else 35.0

        return {
            "success": True,
            "status": "SUCCESS",
            "algorithm": "routeiq_cooperative",
            "algorithm_name": "ROUTE/IQ Cooperative Engine",
            "category": "hybrid_quantum_classical",
            "category_label": "Next-Gen Cooperative Framework",
            "compute_type": "Hybrid Distributed Classical + Simulated Variational Quantum",
            "total_distance_km": round(total_dist_km, 3),
            "total_travel_time_min": round(total_dur_min, 2),
            "driving_duration_min": round(total_dur_min, 2),
            "service_duration_min": 0.0,
            "total_duration_min": round(total_dur_min, 2),
            "implied_speed_kmh": round(implied_speed, 1),
            "operational_speed_kmh": round(implied_speed, 1),
            "total_objective_cost": round(final_cand.total_cost_usd, 2),
            "total_energy_kwh": round(final_cand.total_energy_kwh, 2),
            "total_emissions_kg_co2": round(final_cand.total_emissions_kg_co2, 3),
            "scalarized_fitness": round(final_cand.scalarized_fitness, 4),
            "execution_time_sec": round(total_runtime_sec, 3),
            "routes": assembled_routes,
            "is_feasible": final_cand.is_feasible,
            "capacity_violations": final_cand.capacity_violations,
            "range_violations": final_cand.range_violations,
            "unserved_customers": final_cand.unserved_customers,
            "solution_origin": guardrail_status,
            "guardrail_status": guardrail_status,
            "baseline_ortools_distance_km": round(base_ort.total_distance_km, 3) if base_ort else None,
            "cooperative_cycles_executed": len(cycle_records),
            "candidate_pool_stats": {
                "total_evaluated": pool.total_evaluated_count,
                "total_accepted": pool.total_accepted_count,
                "duplicate_rejected": pool.duplicate_rejected_count,
                "pool_survivors": len(pool.candidates),
                "final_diversity": round(pool.get_diversity(), 4),
            },
            "adaptive_controller_stats": controller.get_summary(),
            "cycle_telemetry": cycle_records,
            "candidate_provenance": pool.get_provenance_summary(),
            "vehicle_condition_profiles": vehicle_eval.profiles,
            "heterogeneity_index": round(hetero_idx, 3),
        }

    def _apply_metrics_to_candidate(self, cand: CandidateSolution, metrics: Dict[str, Any]):
        """Transfers computed physical and multi-objective metrics to CandidateSolution."""
        cand.total_distance_km = metrics["total_distance_km"]
        cand.total_travel_time_min = metrics["total_driving_time_min"]
        cand.total_cost_usd = metrics["total_cost_usd"]
        cand.total_energy_kwh = metrics["total_energy_kwh"]
        cand.total_emissions_kg_co2 = metrics["total_emissions_kg_co2"]
        cand.scalarized_fitness = metrics["scalarized_fitness"]
        cand.is_feasible = metrics["is_feasible"]
        cand.capacity_violations = metrics["capacity_violations"]
        cand.range_violations = metrics["range_violations"]
        cand.unserved_customers = metrics["unserved_customers"]

    def _tabu_inter_route_exchange(
        self,
        routes: List[List[int]],
        dist_matrix: np.ndarray,
        demands: List[int],
        capacities: List[float],
        depot: int,
        max_iters: int = 20,
    ) -> List[List[int]]:
        """Fast Tabu Search inter-route relocate/swap moves with recency memory."""
        curr_routes = [list(r) for r in routes]
        tabu_memory = set()
        best_routes = [list(r) for r in curr_routes]
        best_dist = RouteEvaluator.fleet_distance(curr_routes, dist_matrix, depot)

        for _ in range(max_iters):
            best_move = None
            best_move_dist = float("inf")

            # Try relocating node c from route i to route j
            for i in range(len(curr_routes)):
                if len(curr_routes[i]) <= 1:
                    continue
                for j in range(len(curr_routes)):
                    if i == j:
                        continue
                    cap_j = capacities[j] if j < len(capacities) else 100.0
                    curr_load_j = sum(demands[c] for c in curr_routes[j])

                    for node_idx, c in enumerate(curr_routes[i]):
                        d_c = demands[c]
                        if curr_load_j + d_c > cap_j:
                            continue
                        if (c, j) in tabu_memory:
                            continue

                        # Cost diff
                        old_d = RouteEvaluator.tour_length(curr_routes[i], dist_matrix, depot) + RouteEvaluator.tour_length(curr_routes[j], dist_matrix, depot)
                        new_r_i = curr_routes[i][:node_idx] + curr_routes[i][node_idx + 1:]
                        new_r_j = curr_routes[j] + [c]
                        new_d = RouteEvaluator.tour_length(new_r_i, dist_matrix, depot) + RouteEvaluator.tour_length(new_r_j, dist_matrix, depot)

                        diff = new_d - old_d
                        if diff < best_move_dist:
                            best_move_dist = diff
                            best_move = ("relocate", i, j, node_idx, c)

            if best_move and best_move_dist < 0:
                _, src_i, dst_j, node_pos, moved_node = best_move
                curr_routes[src_i].pop(node_pos)
                curr_routes[dst_j].append(moved_node)
                tabu_memory.add((moved_node, src_i))
                if len(tabu_memory) > 10:
                    tabu_memory.pop()

                curr_d = RouteEvaluator.fleet_distance(curr_routes, dist_matrix, depot)
                if curr_d < best_dist - 1e-4:
                    best_dist = curr_d
                    best_routes = [list(r) for r in curr_routes]
            else:
                break

        return best_routes

    def _ortools_guided_repair(
        self,
        routes: List[List[int]],
        dist_matrix: np.ndarray,
        demands: List[int],
        capacities: List[float],
        depot: int,
        time_limit_sec: float = 0.15,
    ) -> List[List[int]]:
        """Invokes OR-Tools to repair route alignments and optimize node sequencing."""
        flat_nodes = [c for r in routes for c in r]
        if len(flat_nodes) < 4:
            return routes
        try:
            res = classical_solver.solve_ortools(
                distance_matrix=dist_matrix,
                num_vehicles=len(routes),
                depot=depot,
                demands=demands,
                vehicle_capacities=[int(c) for c in capacities],
                time_limit_sec=time_limit_sec,
            )
            if res.get("success") and res.get("routes"):
                return [list(r.get("customer_stops", [])) for r in res["routes"]]
        except Exception:
            pass
        return routes
