"""
ROUTE/IQ Next-Generation Cooperative Engine: Quantum-Inspired Genetic Algorithm (QIGA).
Implements Q-bit chromosome representation, quantum rotation gate updates,
and probability amplitude sampling for cooperative candidate diversification.
"""

import time
import math
import copy
import logging
from typing import Dict, Any, List, Tuple, Optional
import numpy as np

logger = logging.getLogger(__name__)


class QIGACooperativeOperator:
    """
    Quantum-Inspired Genetic Algorithm (QIGA) Operator for the ROUTE/IQ Cooperative Pool.
    Represents customer-to-vehicle assignments as quantum probability vectors:
    |psi_i> = sum_k alpha_{ik} |k>, with sum_k |alpha_{ik}|^2 = 1.
    Applies quantum rotation gates Delta theta guided by elite pool incumbents to explore
    diverse combinatorial assignments that escape local classical search basins.
    """

    def __init__(
        self,
        population_size: int = 12,
        generations: int = 5,
        rotation_angle_base: float = 0.05 * math.pi,
    ):
        self.population_size: int = population_size
        self.generations: int = generations
        self.rotation_angle_base: float = rotation_angle_base

    def execute(
        self,
        parent_candidate,
        elite_incumbent,
        dist_matrix: np.ndarray,
        demands: List[int],
        depot: int = 0,
        vehicle_capacities: Optional[List[float]] = None,
        seed: int = 42,
    ) -> Optional[Any]:
        """
        Executes QIGA exploration on parent candidate guided by elite incumbent:
        1. Encodes customer-to-vehicle assignments into Q-bit probability matrix.
        2. Applies quantum rotation gates toward incumbent alleles with exploration entropy.
        3. Collapses Q-bits to sample combinatorial assignment vectors.
        4. Reconstructs intra-route tours via 2-opt.
        5. Validates vehicle capacities and returns offspring candidate.
        """
        from app.services.optimization.candidate_pool import CandidateSolution

        t0 = time.perf_counter()
        np.random.seed(seed)

        n = dist_matrix.shape[0]
        cust_ids = [i for i in range(n) if i != depot]
        N = len(cust_ids)
        K = len(parent_candidate.vehicle_routes)

        if N < 4 or K < 2:
            return None

        caps = (
            [float(c) for c in vehicle_capacities]
            if vehicle_capacities and len(vehicle_capacities) >= K
            else [100.0] * K
        )

        # 1. Initialize Q-bit probability amplitudes: alpha_{ik} in [0, 1]
        # Map each customer to current assigned vehicle in parent
        parent_assign = {}
        for k, r in enumerate(parent_candidate.vehicle_routes):
            for c in r:
                parent_assign[c] = k

        # Map each customer to assigned vehicle in elite incumbent
        inc_assign = {}
        if elite_incumbent:
            for k, r in enumerate(elite_incumbent.vehicle_routes):
                for c in r:
                    inc_assign[c] = k
        else:
            inc_assign = parent_assign

        # Initialize probability distribution P[cust_idx, k] with bias toward parent
        P = np.full((N, K), 0.15 / max(1, K - 1))
        for idx, c in enumerate(cust_ids):
            k_p = parent_assign.get(c, 0)
            P[idx, k_p] = 0.85

        # 2. Iterative Quantum Rotation Gate Updates
        best_child_routes = None
        best_child_dist = float("inf")

        for gen in range(self.generations):
            for idx, c in enumerate(cust_ids):
                target_k = inc_assign.get(c, parent_assign.get(c, 0))
                # Apply rotation gate toward target vehicle allele: Delta theta
                theta = self.rotation_angle_base * (1.0 - (gen / max(1, self.generations)))
                # Adjust probability vector smoothly
                for k in range(K):
                    if k == target_k:
                        P[idx, k] = min(0.92, P[idx, k] + math.sin(theta))
                    else:
                        P[idx, k] = max(0.02, P[idx, k] - (math.sin(theta) / (K - 1)))
                # Renormalize probability simplex
                P[idx] = P[idx] / np.sum(P[idx])

            # 3. Collapse/Sample population of solutions
            for _ in range(self.population_size):
                assignment = [[] for _ in range(K)]
                caps_rem = list(caps)

                # Probabilistic sampling of vehicle for each customer
                for idx, c in enumerate(cust_ids):
                    probs = P[idx]
                    chosen_k = int(np.random.choice(K, p=probs))

                    # Feasibility check: does customer fit in chosen vehicle?
                    d_c = demands[c] if c < len(demands) else 1
                    if caps_rem[chosen_k] >= d_c:
                        assignment[chosen_k].append(c)
                        caps_rem[chosen_k] -= d_c
                    else:
                        # Fallback to vehicle with highest remaining capacity
                        k_alt = int(np.argmax(caps_rem))
                        if caps_rem[k_alt] >= d_c:
                            assignment[k_alt].append(c)
                            caps_rem[k_alt] -= d_c
                        else:
                            # Infeasible assignment in this sample
                            assignment = None
                            break

                if assignment is None:
                    continue

                # Ensure all vehicles are represented or at least feasible
                all_assigned = [c for r in assignment for c in r]
                if len(all_assigned) != N:
                    continue

                # 4. Tour Reconstruction via 2-opt
                total_cand_dist = 0.0
                opt_routes = []
                for k in range(K):
                    r_stops = assignment[k]
                    if len(r_stops) <= 2:
                        opt_r = list(r_stops)
                    else:
                        # Quick greedy + 2-opt
                        opt_r = self._optimize_tour(r_stops, dist_matrix, depot)
                    opt_routes.append(opt_r)

                    # Compute tour distance
                    full = [depot] + opt_r + [depot]
                    total_cand_dist += sum(dist_matrix[full[i], full[i + 1]] for i in range(len(full) - 1))

                if total_cand_dist < best_child_dist:
                    best_child_dist = total_cand_dist
                    best_child_routes = opt_routes

        if best_child_routes is None:
            return None

        t_elapsed_ms = (time.perf_counter() - t0) * 1000.0

        child = CandidateSolution(
            vehicle_routes=best_child_routes,
            generating_algorithm="QIGA_Quantum_Inspired_Operator",
            modification_operator="quantum_rotation_gate_sampling",
            parent_id=parent_candidate.candidate_id,
            iteration_created=parent_candidate.iteration_created + 1,
            generation_time_ms=t_elapsed_ms,
        )
        child.improvement_history = parent_candidate.improvement_history + [
            f"QIGA quantum rotation exploration ({self.generations} generations, {self.population_size} samples)"
        ]
        child.metadata["qiga_generations"] = self.generations
        child.metadata["qiga_population"] = self.population_size

        return child

    def _optimize_tour(self, stops: List[int], dist_matrix: np.ndarray, depot: int) -> List[int]:
        """Runs fast 2-opt local search on single route."""
        tour = list(stops)
        n = len(tour)
        if n <= 2:
            return tour

        best_d = sum(dist_matrix[tour[i], tour[i + 1]] for i in range(n - 1)) + dist_matrix[depot, tour[0]] + dist_matrix[tour[-1], depot]
        improved = True
        iters = 0
        while improved and iters < 15:
            improved = False
            iters += 1
            for i in range(n - 1):
                for j in range(i + 1, n):
                    new_t = tour[:i] + tour[i:j + 1][::-1] + tour[j + 1:]
                    new_d = sum(dist_matrix[new_t[k], new_t[k + 1]] for k in range(n - 1)) + dist_matrix[depot, new_t[0]] + dist_matrix[new_t[-1], depot]
                    if new_d < best_d - 1e-4:
                        best_d = new_d
                        tour = new_t
                        improved = True
                        break
                if improved:
                    break
        return tour
