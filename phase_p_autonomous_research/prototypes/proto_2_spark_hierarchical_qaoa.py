"""
Prototype 2: Spark-Driven Hierarchical Quantum Decomposition (Architecture 2).
Implements PySpark 4.2.0 polar window partitioning, dense core QAOA subproblem isolation,
and dynamic programming boundary route reconstruction.
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
from app.services.optimization.qaoa_subproblem_optimizer import QAOASubproblemOptimizer
from phase_p_autonomous_research.prototypes.common_evaluator import (
    ProblemInstance, audit_solution_feasibility
)


class SparkHierarchicalQAOASolver:
    """
    Architecture 2: Spark-Driven Hierarchical Quantum Decomposition Solver.
    """

    def __init__(self, p: int = 1, shots: int = 1024, spark_master: str = "local[*]"):
        self.p = p
        self.shots = shots
        self.preprocessor = SparkRoutingPreprocessor(master=spark_master)
        self.qaoa_optimizer = QAOASubproblemOptimizer(p=p, shots=shots, max_qubits=16)

    def reconstruct_route_with_boundary_dp(
        self,
        core_route: List[Dict[str, Any]],
        boundary_nodes: List[Dict[str, Any]],
        depot: Dict[str, Any],
        dist_matrix: np.ndarray,
        loc_indices: Dict[str, int]
    ) -> List[Dict[str, Any]]:
        """
        Dynamic Programming Minimum Incremental Cost Insertion for boundary nodes.
        """
        current_route = list(core_route)
        depot_idx = loc_indices[depot["id"]]

        for b_node in boundary_nodes:
            b_idx = loc_indices[b_node["id"]]
            best_pos = -1
            min_inc_cost = float("inf")

            # Try inserting b_node at all possible positions in current_route
            n_curr = len(current_route)
            for pos in range(n_curr + 1):
                prev_idx = depot_idx if pos == 0 else loc_indices[current_route[pos - 1]["id"]]
                next_idx = depot_idx if pos == n_curr else loc_indices[current_route[pos]["id"]]

                old_edge = dist_matrix[prev_idx, next_idx]
                new_edges = dist_matrix[prev_idx, b_idx] + dist_matrix[b_idx, next_idx]
                inc_cost = new_edges - old_edge

                if inc_cost < min_inc_cost:
                    min_inc_cost = inc_cost
                    best_pos = pos

            current_route.insert(best_pos, b_node)

        return current_route

    def solve_instance(self, instance: ProblemInstance, use_spark: bool = True) -> Dict[str, Any]:
        """
        Solves complete delivery instance using Architecture 2.
        """
        t_global_start = time.perf_counter()

        # Step 1: Preprocessing & Spatial/Capacity Partitioning
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
            clusters, t_preproc_ms = self.preprocessor.partition_customers_spark(
                df_cust, depot_lat, depot_lon, instance.vehicle_capacity
            )
        else:
            clusters, t_preproc_ms = self.preprocessor.partition_customers_single_machine(
                df_cust, depot_lat, depot_lon, instance.vehicle_capacity
            )

        # Step 2: For each cluster, extract quantum subproblem and solve via QAOA
        final_routes = []
        total_qaoa_ms = 0.0
        total_recon_ms = 0.0
        qaoa_calls = 0

        for cl in clusters:
            cust_dicts = [row["original_dict"] for row in cl["customers"]]
            if not cust_dicts:
                continue

            payload = self.preprocessor.extract_quantum_subproblem_payload(
                cluster_customers=cust_dicts,
                depot=instance.depot,
                matrix=instance.distance_matrix,
                location_indices=instance.location_indices,
                core_budget=4
            )

            core_customers = payload["core_customers"]
            boundary_customers = payload["boundary_customers"]

            # Solve Core via QAOA
            t_q_start = time.perf_counter()
            q_res = self.qaoa_optimizer.solve_microcluster_tour(
                sub_customers=core_customers,
                depot=instance.depot,
                matrix=instance.distance_matrix,
                location_indices=instance.location_indices,
                strict=False
            )
            total_qaoa_ms += (time.perf_counter() - t_q_start) * 1000.0
            if q_res.get("did_qaoa", False):
                qaoa_calls += 1

            ordered_core = q_res["ordered_stops"]

            # Reconstruct boundary nodes via DP Minimum Incremental Cost
            t_rec_start = time.perf_counter()
            complete_cluster_route = self.reconstruct_route_with_boundary_dp(
                core_route=ordered_core,
                boundary_nodes=boundary_customers,
                depot=instance.depot,
                dist_matrix=instance.distance_matrix,
                loc_indices=instance.location_indices
            )
            total_recon_ms += (time.perf_counter() - t_rec_start) * 1000.0

            final_routes.append(complete_cluster_route)

        total_wall_ms = (time.perf_counter() - t_global_start) * 1000.0
        feasibility = audit_solution_feasibility(instance, final_routes)

        return {
            "prototype": "Proto_2_Spark_Hierarchical_QAOA" if use_spark else "Proto_2_Pandas_Hierarchical_QAOA",
            "is_feasible": feasibility["is_feasible"],
            "total_distance_km": feasibility["total_distance_km"],
            "clusters_count": len(clusters),
            "qaoa_calls": qaoa_calls,
            "preprocessing_time_ms": round(t_preproc_ms, 2),
            "qaoa_time_ms": round(total_qaoa_ms, 2),
            "reconstruction_time_ms": round(total_recon_ms, 2),
            "total_wall_ms": round(total_wall_ms, 2)
        }

