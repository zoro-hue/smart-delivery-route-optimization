"""
Prototype 4: Cooperative QAOA + Classically-Seeded QIGA (Architecture 5).
Implements quantum-inspired evolutionary search with classical amplitude seeding,
combined with periodic QAOA sub-tour optimization and elite chromosome injection.
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


class CooperativeQAOAQIGASolver:
    """
    Architecture 5: Cooperative QAOA + QIGA Solver.
    """

    def __init__(
        self,
        pop_size: int = 20,
        generations: int = 30,
        qaoa_interval: int = 10,
        shots: int = 512
    ):
        self.pop_size = pop_size
        self.generations = generations
        self.qaoa_interval = qaoa_interval
        self.classical_solver = ClassicalVRPSolver()
        self.qaoa_optimizer = QAOASubproblemOptimizer(p=1, shots=shots, max_qubits=16)

    def solve_instance(self, instance: ProblemInstance) -> Dict[str, Any]:
        """
        Solves complete delivery instance using Architecture 5.
        """
        t_global_start = time.perf_counter()
        n = instance.num_customers
        customers = instance.customers
        cust_ids = [c["id"] for c in customers]
        depot_idx = instance.location_indices[instance.depot["id"]]

        # Step 1: Classical Seed Generation
        res_class = self.classical_solver.solve_clarke_wright(
            distance_matrix=instance.distance_matrix,
            num_vehicles=instance.num_vehicles,
            depot=0,
            demands=[int(instance.depot["demand"])] + [int(c["demand"]) for c in customers],
            vehicle_capacities=[int(instance.vehicle_capacity)] * instance.num_vehicles
        )

        class_routes = res_class.get("routes", [])
        # Compute customer order precedence from classical routes
        flat_order = []
        for r_entry in class_routes:
            if isinstance(r_entry, dict):
                stops = r_entry.get("customer_stops", [idx for idx in r_entry.get("stops", []) if idx != 0])
            else:
                stops = [idx for idx in r_entry if idx != 0]

            for idx in stops:
                val = int(idx)
                if val != 0:
                    flat_order.append(val - 1)  # 0-indexed customer

        # Fill any missing
        for idx in range(n):
            if idx not in flat_order:
                flat_order.append(idx)

        # Step 2: Initialize Q-bit population with classical amplitude bias
        # Population tensor: pop_size x n x 2 (alpha, beta)
        q_pop = np.zeros((self.pop_size, n, 2), dtype=np.float64)
        for rank, c_idx in enumerate(flat_order):
            precedence = 1.0 - (rank / max(1, n))
            # Probability P(|1>) = sin^2(theta)
            # Bound between 0.15 and 0.85
            p_val = 0.15 + 0.70 * precedence
            theta = math.asin(math.sqrt(p_val))
            # Individual 0 gets exact classical bias
            q_pop[0, c_idx, 0] = math.cos(theta)
            q_pop[0, c_idx, 1] = math.sin(theta)

        # Remaining individuals get perturbed bias
        for ind in range(1, self.pop_size):
            for c_idx in range(n):
                perturb = np.random.uniform(-0.15, 0.15)
                base_p = q_pop[0, c_idx, 1] ** 2
                p_clamped = max(0.05, min(0.95, base_p + perturb))
                theta = math.asin(math.sqrt(p_clamped))
                q_pop[ind, c_idx, 0] = math.cos(theta)
                q_pop[ind, c_idx, 1] = math.sin(theta)

        best_global_distance = float("inf")
        best_global_routes = []
        qaoa_calls = 0
        total_qaoa_ms = 0.0

        delta_theta = 0.02 * math.pi

        # Step 3: Evolutionary Loop with Periodic QAOA Intervention
        for gen in range(self.generations):
            gen_best_dist = float("inf")
            gen_best_routes = []
            gen_best_order = None

            for ind in range(self.pop_size):
                # Measure / collapse chromosome
                probs = q_pop[ind, :, 1] ** 2
                order = np.argsort(-probs)

                # Partition into vehicle routes based on capacity
                routes = []
                curr_route = []
                curr_load = 0.0

                for c_idx in order:
                    c = customers[c_idx]
                    dem = float(c["demand"])
                    if curr_load + dem <= instance.vehicle_capacity and len(routes) < instance.num_vehicles:
                        curr_route.append(c)
                        curr_load += dem
                    else:
                        if curr_route:
                            routes.append(curr_route)
                        curr_route = [c]
                        curr_load = dem

                if curr_route:
                    routes.append(curr_route)

                # Ensure at most num_vehicles by merging overflow
                while len(routes) > instance.num_vehicles:
                    last = routes.pop()
                    routes[-1].extend(last)

                audit = audit_solution_feasibility(instance, routes)
                dist = audit["total_distance_km"]

                if dist < gen_best_dist:
                    gen_best_dist = dist
                    gen_best_routes = routes
                    gen_best_order = order

            if gen_best_dist < best_global_distance:
                best_global_distance = gen_best_dist
                best_global_routes = gen_best_routes

            # Step 4: Periodic QAOA Sub-tour Optimization
            if (gen + 1) % self.qaoa_interval == 0 and best_global_routes:
                # Find longest vehicle route
                longest_route = max(best_global_routes, key=lambda r: len(r))
                if len(longest_route) >= 4:
                    sub = longest_route[:4]
                    t_q0 = time.perf_counter()
                    q_res = self.qaoa_optimizer.solve_microcluster_tour(
                        sub_customers=sub,
                        depot=instance.depot,
                        matrix=instance.distance_matrix,
                        location_indices=instance.location_indices,
                        strict=False
                    )
                    total_qaoa_ms += (time.perf_counter() - t_q0) * 1000.0
                    qaoa_calls += 1

                    # Re-inject QAOA improved sub-tour
                    longest_route[:4] = q_res["ordered_stops"]
                    post_audit = audit_solution_feasibility(instance, best_global_routes)
                    if post_audit["total_distance_km"] < best_global_distance:
                        best_global_distance = post_audit["total_distance_km"]

            # Step 5: Quantum Rotation Gates towards best order
            for ind in range(self.pop_size):
                for rank, c_idx in enumerate(gen_best_order):
                    target_beta = 1.0 if rank < n // 2 else 0.0
                    current_beta = q_pop[ind, c_idx, 1]
                    # Rotate towards target
                    direction = 1.0 if target_beta > current_beta else -1.0
                    curr_theta = math.asin(max(-1.0, min(1.0, current_beta)))
                    new_theta = curr_theta + direction * delta_theta
                    q_pop[ind, c_idx, 0] = math.cos(new_theta)
                    q_pop[ind, c_idx, 1] = math.sin(new_theta)

        total_wall_ms = (time.perf_counter() - t_global_start) * 1000.0
        feasibility = audit_solution_feasibility(instance, best_global_routes)

        return {
            "prototype": "Proto_4_Cooperative_QAOA_QIGA",
            "is_feasible": feasibility["is_feasible"],
            "total_distance_km": feasibility["total_distance_km"],
            "classical_initial_distance_km": round(res_class.get("total_distance_km", 0.0), 3),
            "improvement_pct": round(
                (res_class.get("total_distance_km", 0.0) - feasibility["total_distance_km"]) /
                max(1e-4, res_class.get("total_distance_km", 1.0)) * 100.0, 3
            ),
            "qaoa_calls": qaoa_calls,
            "qaoa_time_ms": round(total_qaoa_ms, 2),
            "generations": self.generations,
            "total_wall_ms": round(total_wall_ms, 2)
        }
