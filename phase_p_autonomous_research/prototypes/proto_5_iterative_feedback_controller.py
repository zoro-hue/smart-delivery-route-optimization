"""
Prototype 5: Incumbent-Preserving Cooperative Quantum Engine (IP-CQE) (Architecture 15 & 9).
Candidate Master Research Architecture for ROUTE/IQ.
Integrates Spark preprocessing, OR-Tools global optimization, Crossing-triggered Warm-Start QAOA,
2-opt local search refinement, and Proposition 1 Monotonic Incumbent Preservation.
"""

import sys
import os
import time
import math
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend")))
from app.services.spark_routing_preprocessor import SparkRoutingPreprocessor
from app.services.optimization.classical_solver import ClassicalVRPSolver
from app.services.optimization.qaoa_subproblem_optimizer import QAOASubproblemOptimizer
from phase_p_autonomous_research.prototypes.common_evaluator import (
    ProblemInstance, audit_solution_feasibility
)
from phase_p_autonomous_research.prototypes.proto_1_classical_seeded_qaoa import ClassicalSeededQAOASolver
from phase_p_autonomous_research.prototypes.proto_3_adaptive_neighborhood_qaoa import AdaptiveNeighborhoodQAOASolver


class IncumbentPreservingCooperativeEngine:
    """
    Architecture 15: Incumbent-Preserving Cooperative Quantum Engine (IP-CQE).
    """

    def __init__(
        self,
        qaoa_p: int = 1,
        qaoa_shots: int = 1024,
        spark_master: str = "local[*]",
        max_feedback_rounds: int = 2
    ):
        self.qaoa_solver = ClassicalSeededQAOASolver(p=qaoa_p, shots=qaoa_shots)
        self.preprocessor = SparkRoutingPreprocessor(master=spark_master)
        self.classical_solver = ClassicalVRPSolver()
        self.max_feedback_rounds = max_feedback_rounds

    def apply_two_opt_polish(
        self,
        route_nodes: List[Dict[str, Any]],
        instance: ProblemInstance
    ) -> List[Dict[str, Any]]:
        """Applies fast classical 2-opt edge uncrossing polish on a single vehicle route."""
        n = len(route_nodes)
        if n < 4:
            return route_nodes

        best_route = list(route_nodes)
        depot_idx = instance.location_indices[instance.depot["id"]]

        def route_len(r):
            d = instance.distance_matrix[depot_idx, instance.location_indices[r[0]["id"]]]
            for i in range(len(r) - 1):
                d += instance.distance_matrix[instance.location_indices[r[i]["id"]], instance.location_indices[r[i+1]["id"]]]
            d += instance.distance_matrix[instance.location_indices[r[-1]["id"]], depot_idx]
            return d

        best_cost = route_len(best_route)
        improved = True

        while improved:
            improved = False
            for i in range(n - 1):
                for j in range(i + 1, n):
                    # 2-opt reversal
                    cand = best_route[:i] + best_route[i:j+1][::-1] + best_route[j+1:]
                    c_cost = route_len(cand)
                    if c_cost < best_cost - 1e-4:
                        best_cost = c_cost
                        best_route = cand
                        improved = True
                        break
                if improved:
                    break

        return best_route

    def solve_instance(self, instance: ProblemInstance, use_spark: bool = True) -> Dict[str, Any]:
        """
        Solves complete delivery instance using Architecture 15.
        """
        t_global_start = time.perf_counter()

        # Step 1: Spark Preprocessing & Polar Spatial Analysis
        df_cust = pd.DataFrame([
            {
                "order_id": c["id"],
                "customer_id": c["id"],
                "latitude": float(c["latitude"]),
                "longitude": float(c["longitude"]),
                "demand": float(c["demand"]),
                "original_dict": c
            }
            for c in instance.customers
        ])

        depot_lat = float(instance.depot["latitude"])
        depot_lon = float(instance.depot["longitude"])

        if use_spark:
            clusters, t_spark_ms = self.preprocessor.partition_customers_spark(
                df_cust, depot_lat, depot_lon, instance.vehicle_capacity
            )
        else:
            clusters, t_spark_ms = self.preprocessor.partition_customers_single_machine(
                df_cust, depot_lat, depot_lon, instance.vehicle_capacity
            )

        # Step 2: Classical OR-Tools Global Incumbent Solution
        t_class_start = time.perf_counter()
        res_ortools = self.classical_solver.solve_ortools(
            distance_matrix=instance.distance_matrix,
            num_vehicles=instance.num_vehicles,
            depot=0,
            demands=[int(instance.depot["demand"])] + [int(c["demand"]) for c in instance.customers],
            vehicle_capacities=[int(instance.vehicle_capacity)] * instance.num_vehicles,
            time_limit_sec=15
        )
        t_class_ms = (time.perf_counter() - t_class_start) * 1000.0

        all_nodes = [instance.depot] + instance.customers
        ortools_routes = []
        for r_entry in res_ortools.get("routes", []):
            if isinstance(r_entry, dict):
                inner = [int(idx) for idx in r_entry.get("customer_stops", []) if int(idx) != 0]
            else:
                inner = [int(idx) for idx in r_entry if int(idx) != 0]

            if inner:
                ortools_routes.append([all_nodes[i] for i in inner])

        incumbent_audit = audit_solution_feasibility(instance, ortools_routes)
        incumbent_cost = incumbent_audit["total_distance_km"]

        # Step 3: Cooperative Quantum Neighborhood Exploration
        # For each route, detect planar crossings or dense clusters and invoke Warm-Start QAOA
        active_routes = [list(r) for r in ortools_routes]
        total_qaoa_ms = 0.0
        qaoa_calls = 0
        qaoa_improvements = 0

        for r_idx in range(len(active_routes)):
            curr_route = active_routes[r_idx]
            if len(curr_route) >= 4:
                # Detect crossing
                full_r = [instance.depot] + curr_route + [instance.depot]
                crossings = AdaptiveNeighborhoodQAOASolver().detect_crossings_in_route(full_r)

                if crossings:
                    i, j = crossings[0]
                    # Select 4 nodes around crossing
                    sub_idx = [i, i + 1, j, j + 1]
                    if max(sub_idx) < len(full_r):
                        sub = [full_r[k] for k in sub_idx if full_r[k]["id"] != "depot"]
                        if len(sub) == 4:
                            # Invoke Warm-Start QAOA
                            entry = instance.depot
                            exit_node = instance.depot
                            q_res = self.qaoa_solver.solve_microcluster_warm_start(
                                sub_nodes=sub,
                                entry_node=entry,
                                exit_node=exit_node,
                                dist_matrix=instance.distance_matrix,
                                loc_indices=instance.location_indices
                            )
                            total_qaoa_ms += q_res["total_time_ms"]
                            qaoa_calls += 1
                            if q_res["improved"]:
                                qaoa_improvements += 1
                                for k, node in enumerate(q_res["ordered_nodes"]):
                                    full_r[sub_idx[k]] = node
                                curr_route = [node for node in full_r if node["id"] != "depot"]
                else:
                    # Explore first 4 dense nodes with Warm-Start QAOA
                    sub = curr_route[:4]
                    rest = curr_route[4:]
                    entry = instance.depot
                    exit_node = rest[0] if rest else instance.depot
                    q_res = self.qaoa_solver.solve_microcluster_warm_start(
                        sub_nodes=sub,
                        entry_node=entry,
                        exit_node=exit_node,
                        dist_matrix=instance.distance_matrix,
                        loc_indices=instance.location_indices
                    )
                    total_qaoa_ms += q_res["total_time_ms"]
                    qaoa_calls += 1
                    if q_res["improved"]:
                        qaoa_improvements += 1
                        curr_route = q_res["ordered_nodes"] + rest

            # Step 4: Classical 2-opt post-polish on refined route
            t_pol_start = time.perf_counter()
            polished_route = self.apply_two_opt_polish(curr_route, instance)
            active_routes[r_idx] = polished_route

        # Step 5: Proposition 1 Monotonic Incumbent Guardrail
        candidate_audit = audit_solution_feasibility(instance, active_routes)
        candidate_cost = candidate_audit["total_distance_km"]

        # Deterministic guardrail check
        if candidate_audit["is_feasible"] and candidate_cost < incumbent_cost:
            final_accepted_routes = active_routes
            final_cost = candidate_cost
            guardrail_triggered = False
            quantum_net_improvement = round(incumbent_cost - candidate_cost, 3)
        else:
            final_accepted_routes = ortools_routes
            final_cost = incumbent_cost
            guardrail_triggered = True
            quantum_net_improvement = 0.0

        total_wall_ms = (time.perf_counter() - t_global_start) * 1000.0
        final_audit = audit_solution_feasibility(instance, final_accepted_routes)

        return {
            "prototype": "Proto_5_IP_CQE_Master",
            "is_feasible": final_audit["is_feasible"],
            "total_distance_km": final_audit["total_distance_km"],
            "ortools_initial_distance_km": round(incumbent_cost, 3),
            "quantum_net_improvement_km": quantum_net_improvement,
            "improvement_over_ortools_pct": round(
                (incumbent_cost - final_cost) / max(1e-4, incumbent_cost) * 100.0, 3
            ),
            "guardrail_triggered": guardrail_triggered,
            "qaoa_calls": qaoa_calls,
            "qaoa_improvements": qaoa_improvements,
            "spark_time_ms": round(t_spark_ms, 2),
            "classical_time_ms": round(t_class_ms, 2),
            "qaoa_time_ms": round(total_qaoa_ms, 2),
            "total_wall_ms": round(total_wall_ms, 2)
        }
