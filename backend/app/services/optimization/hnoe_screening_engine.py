"""H-NOE Route-Pair Screening Engine (Capacity Filter & Exact Reference Audit).

IMPORTANT RESEARCH AUDIT NOTE (Phase 5C / 5D):
The previously proposed Four-Gamma Depot-Safe Bound (B = Psi_a + Psi_b - 2*(delta_ab + delta_ba))
was empirically DISPROVED in Phase 5C counterexample testing (produced 46 false prunings in 500 trials).
The assumption that directed insertion delta is lower-bounded by 2*delta is mathematically invalid
on asymmetric graphs. That formula has been STRICTLY DISABLED and REJECTED.

Active Capabilities:
1. Capacity Feasibility Filter: Strictly verified mathematical filter checking if
   min(load_a - d_u + d_v) > Q_a or min(load_b - d_v + d_u) > Q_b. (Zero false pruning).
2. Exact Route-Level Insertion Audit: Calculates ground truth Swap(1,1) savings for
   research validation and benchmarking.
"""

from typing import List, Dict, Any, Tuple
import numpy as np


class HNOEScreeningEngine:
    """Screening Engine with mathematically sound Capacity Filter and Exact Audit."""

    def __init__(self, enable_rejected_four_gamma: bool = False):
        """
        Args:
            enable_rejected_four_gamma: Strictly False. If True, raises ValueError
                                        to prevent accidental re-enabling of the flawed bound.
        """
        if enable_rejected_four_gamma:
            raise ValueError(
                "CRITICAL REJECTION: The Four-Gamma bound is mathematically invalid and produced "
                "false-pruning events in Phase 5C audit testing. It cannot be enabled."
            )
        self.enable_rejected_four_gamma = False

    def evaluate_swap_opportunity(
        self,
        route_a: List[Dict[str, Any]],
        route_b: List[Dict[str, Any]],
        matrix: np.ndarray,
        vehicle_capacity: float,
        location_indices: Dict[str, int],
        depot_idx: int = 0
    ) -> Dict[str, Any]:
        """
        Evaluates swap feasibility using only mathematically safe screening:
        1. Checks for empty routes.
        2. Evaluates the Capacity Filter: if every possible swap violates vehicle capacity,
           the route pair is safely pruned with zero false-pruning risk.
        3. Computes exact ground truth Swap(1,1) savings as a reference.
        """
        stops_a = route_a[1:-1]
        stops_b = route_b[1:-1]

        if not stops_a or not stops_b:
            return {
                "pruned": True,
                "stage_pruned": "empty_route",
                "upper_bound": 0.0,
                "true_max_savings": 0.0,
                "is_false_pruning": False
            }

        # Stage 1: Verified Capacity Feasibility Filter
        demands_a = [float(c.get("demand", 1.0)) for c in stops_a]
        demands_b = [float(c.get("demand", 1.0)) for c in stops_b]
        load_a = sum(demands_a)
        load_b = sum(demands_b)

        min_da, max_da = min(demands_a), max(demands_a)
        min_db, max_db = min(demands_b), max(demands_b)

        # For every swap (u, v):
        # new_load_a >= load_a - max_da + min_db
        # new_load_b >= load_b - max_db + min_da
        # If either lower bound exceeds vehicle_capacity, NO feasible swap exists!
        min_possible_new_a = load_a - max_da + min_db
        min_possible_new_b = load_b - max_db + min_da

        true_max_savings, has_improving = self._compute_true_max_savings(
            route_a, route_b, matrix, vehicle_capacity, location_indices, depot_idx
        )

        if (min_possible_new_a > vehicle_capacity) or (min_possible_new_b > vehicle_capacity):
            return {
                "pruned": True,
                "stage_pruned": "capacity",
                "upper_bound": 0.0,
                "true_max_savings": float(true_max_savings),
                "is_false_pruning": bool(has_improving)
            }

        # Four-Gamma Bound is explicitly omitted here.
        # Unpruned route pair passes through to full local search.
        return {
            "pruned": False,
            "stage_pruned": "none",
            "upper_bound": float("inf"),
            "true_max_savings": round(float(true_max_savings), 4),
            "is_false_pruning": False
        }

    def _compute_true_max_savings(
        self,
        route_a: List[Dict[str, Any]],
        route_b: List[Dict[str, Any]],
        matrix: np.ndarray,
        vehicle_capacity: float,
        location_indices: Dict[str, int],
        depot_idx: int
    ) -> Tuple[float, bool]:
        """Exhaustively evaluates every valid Swap(1,1) to establish ground truth."""
        stops_a = route_a[1:-1]
        stops_b = route_b[1:-1]
        load_a = sum(float(c.get("demand", 1.0)) for c in stops_a)
        load_b = sum(float(c.get("demand", 1.0)) for c in stops_b)

        max_savings = -float("inf")
        has_improving = False

        for i, u in enumerate(stops_a):
            d_u = float(u.get("demand", 1.0))
            u_idx = location_indices[u["id"]]
            p_a = depot_idx if i == 0 else location_indices[stops_a[i - 1]["id"]]
            s_a = depot_idx if i == len(stops_a) - 1 else location_indices[stops_a[i + 1]["id"]]

            cost_remove_u = matrix[p_a, u_idx] + matrix[u_idx, s_a] - matrix[p_a, s_a]

            for j, v in enumerate(stops_b):
                d_v = float(v.get("demand", 1.0))
                # Capacity feasibility
                if load_a - d_u + d_v > vehicle_capacity or load_b - d_v + d_u > vehicle_capacity:
                    continue

                v_idx = location_indices[v["id"]]
                p_b = depot_idx if j == 0 else location_indices[stops_b[j - 1]["id"]]
                s_b = depot_idx if j == len(stops_b) - 1 else location_indices[stops_b[j + 1]["id"]]

                cost_remove_v = matrix[p_b, v_idx] + matrix[v_idx, s_b] - matrix[p_b, s_b]

                cost_insert_v_in_a = matrix[p_a, v_idx] + matrix[v_idx, s_a] - matrix[p_a, s_a]
                cost_insert_u_in_b = matrix[p_b, u_idx] + matrix[u_idx, s_b] - matrix[p_b, s_b]

                # Exact savings: removal reductions minus insertion penalties
                savings = float((cost_remove_u + cost_remove_v) - (cost_insert_v_in_a + cost_insert_u_in_b))

                if savings > max_savings:
                    max_savings = savings
                if savings > 1e-9:
                    has_improving = True

        return (0.0 if max_savings == -float("inf") else max_savings), has_improving
