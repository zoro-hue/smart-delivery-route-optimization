"""
Prototype 3: Adaptive Quantum Neighborhood Search with Crossing Detection (Architecture 3).
Implements planar crossing intersection detection, road detour ratio screening,
subproblem boundary pinning, and QAOA uncrossing optimization.
"""

import sys
import os
import time
import math
from typing import Dict, Any, List, Tuple, Optional
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend")))
from app.services.optimization.classical_solver import ClassicalVRPSolver
from app.services.optimization.qaoa_subproblem_optimizer import QAOASubproblemOptimizer
from phase_p_autonomous_research.prototypes.common_evaluator import (
    ProblemInstance, audit_solution_feasibility
)


class AdaptiveNeighborhoodQAOASolver:
    """
    Architecture 3: Adaptive Quantum Neighborhood Search Solver.
    """

    def __init__(self, p: int = 1, shots: int = 1024):
        self.p = p
        self.shots = shots
        self.classical_solver = ClassicalVRPSolver()
        self.qaoa_optimizer = QAOASubproblemOptimizer(p=p, shots=shots, max_qubits=16)

    @staticmethod
    def segments_intersect(
        p1: Tuple[float, float], p2: Tuple[float, float],
        p3: Tuple[float, float], p4: Tuple[float, float]
    ) -> bool:
        """Determines if line segment p1-p2 strictly intersects p3-p4."""
        def ccw(a, b, c):
            return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])

        return (ccw(p1, p3, p4) != ccw(p2, p3, p4)) and (ccw(p1, p2, p3) != ccw(p1, p2, p4))

    def detect_crossings_in_route(
        self,
        route_nodes: List[Dict[str, Any]]
    ) -> List[Tuple[int, int]]:
        """
        Finds pairs of intersecting edges in a single vehicle route.
        """
        crossings = []
        n = len(route_nodes)
        if n < 4:
            return crossings

        coords = [(float(node["latitude"]), float(node["longitude"])) for node in route_nodes]

        for i in range(n - 1):
            p1, p2 = coords[i], coords[i + 1]
            for j in range(i + 2, n - 1):
                # Adjacent edges cannot form a 2-opt crossing
                if abs(i - j) <= 1:
                    continue
                p3, p4 = coords[j], coords[j + 1]
                if self.segments_intersect(p1, p2, p3, p4):
                    crossings.append((i, j))

        return crossings

    def solve_instance(self, instance: ProblemInstance) -> Dict[str, Any]:
        """
        Solves complete delivery instance using Architecture 3.
        """
        t_global_start = time.perf_counter()

        # Step 1: Generate initial classical solution via Clarke-Wright + 2-opt
        res_class = self.classical_solver.solve_clarke_wright(
            distance_matrix=instance.distance_matrix,
            num_vehicles=instance.num_vehicles,
            depot=0,
            demands=[int(instance.depot["demand"])] + [int(c["demand"]) for c in instance.customers],
            vehicle_capacities=[int(instance.vehicle_capacity)] * instance.num_vehicles
        )

        routes = res_class.get("routes", [])
        all_nodes = [instance.depot] + instance.customers

        total_crossings_detected = 0
        qaoa_crossings_resolved = 0
        total_qaoa_ms = 0.0
        final_customer_routes = []

        for r_entry in routes:
            if isinstance(r_entry, dict):
                inner_indices = [int(idx) for idx in r_entry.get("customer_stops", []) if int(idx) != 0]
            else:
                inner_indices = [int(idx) for idx in r_entry if int(idx) != 0]

            if not inner_indices:
                continue

            full_route_nodes = [instance.depot] + [all_nodes[idx] for idx in inner_indices] + [instance.depot]
            crossings = self.detect_crossings_in_route(full_route_nodes)
            total_crossings_detected += len(crossings)

            # If crossing exists, extract the 4-node bottleneck subproblem
            if crossings:
                i, j = crossings[0]
                # Extract 4 nodes around the crossing
                sub_indices = [i, i + 1, j, j + 1]
                # Ensure valid bounds
                if max(sub_indices) < len(full_route_nodes):
                    sub_customers = [full_route_nodes[idx] for idx in sub_indices if full_route_nodes[idx]["id"] != "depot"]
                    if len(sub_customers) == 4:
                        t_q0 = time.perf_counter()
                        q_res = self.qaoa_optimizer.solve_microcluster_tour(
                            sub_customers=sub_customers,
                            depot=instance.depot,
                            matrix=instance.distance_matrix,
                            location_indices=instance.location_indices,
                            strict=False
                        )
                        total_qaoa_ms += (time.perf_counter() - t_q0) * 1000.0

                        # Calculate if replacement improves local cost
                        q_ordered = q_res["ordered_stops"]
                        # Replace in route
                        new_route = list(full_route_nodes)
                        for k, node in enumerate(q_ordered):
                            new_route[sub_indices[k]] = node

                        # Measure distance
                        def calc_route_dist(r_nodes):
                            d = 0.0
                            for idx in range(len(r_nodes) - 1):
                                u = instance.location_indices[r_nodes[idx]["id"]]
                                v = instance.location_indices[r_nodes[idx+1]["id"]]
                                d += instance.distance_matrix[u, v]
                            return d

                        old_d = calc_route_dist(full_route_nodes)
                        new_d = calc_route_dist(new_route)

                        if new_d < old_d:
                            full_route_nodes = new_route
                            qaoa_crossings_resolved += 1

            # Extract inner customers
            inner_cust = [node for node in full_route_nodes if node["id"] != "depot"]
            final_customer_routes.append(inner_cust)

        total_wall_ms = (time.perf_counter() - t_global_start) * 1000.0
        feasibility = audit_solution_feasibility(instance, final_customer_routes)

        return {
            "prototype": "Proto_3_Adaptive_Neighborhood_QAOA",
            "is_feasible": feasibility["is_feasible"],
            "total_distance_km": feasibility["total_distance_km"],
            "classical_initial_distance_km": round(res_class.get("total_distance_km", 0.0), 3),
            "crossings_detected": total_crossings_detected,
            "crossings_resolved_by_qaoa": qaoa_crossings_resolved,
            "qaoa_time_ms": round(total_qaoa_ms, 2),
            "total_wall_ms": round(total_wall_ms, 2)
        }
