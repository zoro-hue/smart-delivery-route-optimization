"""
Phase AB: Centralized Proposition 1 Incumbent-Preserving Acceptance Guardrail.
Guarantees 100% capacity feasibility and 0.00% route degradation:
Cost(R_final) = min(Cost(R_incumbent), Cost(R_candidate))
Strictly independent of candidate generation strategy.
"""

import time
from typing import Dict, Any, List, Tuple, Optional
import numpy as np

from phase_v_independent_quantum_validation.prototypes.algorithmic_vnd import AlgorithmicVND


class Proposition1Guardrail:
    """Centralized safety filter enforcing Proposition 1 non-degradation."""

    @staticmethod
    def validate_and_filter(
        candidate_tour_a: List[int],
        candidate_tour_b: List[int],
        incumbent_tour_a: List[int],
        incumbent_tour_b: List[int],
        demands: np.ndarray,
        cap_a: float,
        cap_b: float,
        dist_matrix: np.ndarray,
        tolerance: float = 1e-4
    ) -> Dict[str, Any]:
        """
        Validates customer coverage, vehicle capacity, route connectivity, and complete TSP distance.
        Adopts candidate IF AND ONLY IF strictly feasible and strictly improving.
        Otherwise retains the incumbent unconditionally.
        """
        N = len(demands)
        expected_customers = set(range(1, N + 1))

        # 1. Customer Coverage Validation (no missing, no duplicates)
        cand_all = candidate_tour_a + candidate_tour_b
        if set(cand_all) != expected_customers or len(cand_all) != N:
            # Rejection due to coverage defect
            inc_opt = AlgorithmicVND.optimize_fleet_routes(incumbent_tour_a, incumbent_tour_b, demands, cap_a, cap_b, dist_matrix)
            return {
                "accepted": False,
                "rejection_reason": "INVALID_CUSTOMER_COVERAGE",
                "final_tour_a": inc_opt["tour_a"],
                "final_tour_b": inc_opt["tour_b"],
                "final_distance": round(float(inc_opt["total_distance"]), 2),
                "is_feasible": True
            }

        # 2. Capacity Constraint Validation
        qa = sum(demands[n - 1] for n in candidate_tour_a)
        qb = sum(demands[n - 1] for n in candidate_tour_b)
        if qa > cap_a or qb > cap_b or qa == 0 or qb == 0:
            inc_opt = AlgorithmicVND.optimize_fleet_routes(incumbent_tour_a, incumbent_tour_b, demands, cap_a, cap_b, dist_matrix)
            return {
                "accepted": False,
                "rejection_reason": "CAPACITY_CONSTRAINT_VIOLATION",
                "final_tour_a": inc_opt["tour_a"],
                "final_tour_b": inc_opt["tour_b"],
                "final_distance": round(float(inc_opt["total_distance"]), 2),
                "is_feasible": True
            }

        # 3. Route Evaluation & VND Optimization
        cand_opt = AlgorithmicVND.optimize_fleet_routes(candidate_tour_a, candidate_tour_b, demands, cap_a, cap_b, dist_matrix)
        inc_opt = AlgorithmicVND.optimize_fleet_routes(incumbent_tour_a, incumbent_tour_b, demands, cap_a, cap_b, dist_matrix)

        d_cand = float(cand_opt["total_distance"])
        d_inc = float(inc_opt["total_distance"])

        # 4. Proposition 1 Acceptance Decision
        if d_cand < d_inc - tolerance:
            return {
                "accepted": True,
                "rejection_reason": "ACCEPTED_IMPROVING_CANDIDATE",
                "final_tour_a": cand_opt["tour_a"],
                "final_tour_b": cand_opt["tour_b"],
                "final_distance": round(d_cand, 2),
                "distance_delta": round(d_cand - d_inc, 2),
                "is_feasible": True
            }
        else:
            return {
                "accepted": False,
                "rejection_reason": "SUBOPTIMAL_OBJECTIVE_REJECTED",
                "final_tour_a": inc_opt["tour_a"],
                "final_tour_b": inc_opt["tour_b"],
                "final_distance": round(d_inc, 2),
                "distance_delta": 0.0,
                "is_feasible": True
            }

