"""
ROUTE/IQ Next-Generation Cooperative Engine: Adaptive Cooperative Controller.
Implements Contextual Multi-Armed Bandit (MAB) with Upper Confidence Bound (UCB-1)
and Multi-Objective Reward Learning for dynamic operator orchestration.
"""

import math
import time
import logging
from typing import Dict, Any, List, Tuple, Optional
import numpy as np

logger = logging.getLogger(__name__)


class AdaptiveCooperativeController:
    """
    Contextual Multi-Armed Bandit (MAB) Controller for the Next-Generation Cooperative Engine.
    Dynamically orchestrates heterogeneous heuristic, metaheuristic, and quantum operators
    based on instance context features and online multi-objective feedback rewards.
    """

    OPERATORS = [
        "OP_SPARK_POLAR_SWEEP",
        "OP_CLARKE_WRIGHT_SAVINGS",
        "OP_ORTOOLS_LOCAL_REPAIR",
        "OP_QAOA_SUBPROBLEM",
        "OP_QIGA_QUANTUM_GENETIC",
        "OP_TABU_SEARCH_EXCHANGE",
        "OP_DEEP_VND_REFINE",
        "OP_ALNS_RUIN_RECREATE",
    ]

    def __init__(
        self,
        exploration_factor: float = 0.8,
        learning_rate: float = 0.25,
        w_improvement: float = 0.50,
        w_feasibility: float = 0.25,
        w_diversity: float = 0.20,
        w_runtime: float = 0.05,
    ):
        self.exploration_factor: float = exploration_factor
        self.learning_rate: float = learning_rate

        # Multi-objective reward weights: R = w1*Δ_norm + w2*I_feas + w3*Div - w4*T_norm
        self.w_improvement: float = w_improvement
        self.w_feasibility: float = w_feasibility
        self.w_diversity: float = w_diversity
        self.w_runtime: float = w_runtime

        # Statistics per operator
        self.q_values: Dict[str, float] = {op: 0.5 for op in self.OPERATORS}
        self.action_counts: Dict[str, int] = {op: 0 for op in self.OPERATORS}
        self.success_counts: Dict[str, int] = {op: 0 for op in self.OPERATORS}
        self.total_invocations: int = 0

        # Detailed execution log
        self.history: List[Dict[str, Any]] = []

    def select_operator(
        self,
        context: Dict[str, Any],
        stagnation_count: int = 0,
        remaining_budget_ratio: float = 1.0,
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Selects next optimization operator using Contextual UCB-1 with contextual biasing:
        Score(o) = Q(o) + c * sqrt(ln(T) / N(o)) + ContextBias(o, context)
        """
        self.total_invocations += 1
        T = self.total_invocations

        # Compute UCB scores
        scores = {}
        for op in self.OPERATORS:
            n_o = self.action_counts[op]
            if n_o == 0:
                # Untried operator gets maximum priority
                scores[op] = 100.0 + np.random.uniform(0.0, 1.0)
                continue

            exploit = self.q_values[op]
            explore = self.exploration_factor * math.sqrt(math.log(T + 1) / n_o)
            context_bias = self._calculate_context_bias(op, context, stagnation_count, remaining_budget_ratio)
            scores[op] = exploit + explore + context_bias

        # Select highest-scoring operator (with slight tie-breaking noise)
        chosen_op = max(scores.keys(), key=lambda op: scores[op] + np.random.normal(0, 1e-4))
        self.action_counts[chosen_op] += 1

        selection_metadata = {
            "operator": chosen_op,
            "ucb_score": round(float(scores[chosen_op]), 4),
            "q_value": round(float(self.q_values[chosen_op]), 4),
            "invocations": self.action_counts[chosen_op],
            "stagnation": stagnation_count,
            "remaining_budget_ratio": round(remaining_budget_ratio, 3),
        }

        return chosen_op, selection_metadata

    def update_reward(
        self,
        operator: str,
        parent_fitness: float,
        child_fitness: float,
        is_feasible: bool,
        candidate_diversity: float,
        runtime_ms: float,
        budget_ms: float = 500.0,
    ) -> float:
        """
        Computes formal multi-objective feedback reward and updates operator Q-value:
        R(o) = w1 * Δ_norm + w2 * I_feas + w3 * Div - w4 * T_norm
        """
        if operator not in self.q_values:
            return 0.0

        # 1. Relative normalized improvement
        if parent_fitness > 1e-6 and math.isfinite(parent_fitness) and math.isfinite(child_fitness):
            improvement_ratio = max(0.0, (parent_fitness - child_fitness) / parent_fitness)
            norm_improvement = min(1.0, improvement_ratio * 10.0)  # scale 10% gain to 1.0
        else:
            norm_improvement = 0.0

        # 2. Feasibility indicator
        feas_score = 1.0 if is_feasible else -0.5

        # 3. Candidate diversity (0.0 to 1.0)
        div_score = min(1.0, max(0.0, candidate_diversity))

        # 4. Normalized runtime penalty
        norm_runtime = min(1.0, max(0.0, runtime_ms / max(10.0, budget_ms)))

        # Composite scalar reward
        reward = (
            self.w_improvement * norm_improvement
            + self.w_feasibility * feas_score
            + self.w_diversity * div_score
            - self.w_runtime * norm_runtime
        )
        reward = float(np.clip(reward, -1.0, 2.0))

        # Exponential moving average update
        alpha = self.learning_rate
        self.q_values[operator] = (1.0 - alpha) * self.q_values[operator] + alpha * reward

        if norm_improvement > 1e-4 and is_feasible:
            self.success_counts[operator] += 1

        self.history.append({
            "operator": operator,
            "reward": round(reward, 4),
            "norm_improvement": round(norm_improvement, 4),
            "is_feasible": is_feasible,
            "diversity": round(div_score, 4),
            "runtime_ms": round(runtime_ms, 2),
            "updated_q": round(self.q_values[operator], 4),
        })

        return reward

    def _calculate_context_bias(
        self,
        operator: str,
        context: Dict[str, Any],
        stagnation: int,
        budget_ratio: float,
    ) -> float:
        """
        Computes instance-specific contextual bias based on problem characteristics:
        - Small N (<= 15): favors OR-Tools and exact local search.
        - High Stagnation (>= 3): favors QIGA, ALNS, and QAOA to break out of local optima.
        - Low Budget (< 0.2): penalizes expensive operators like QAOA/ALNS in favor of fast VND.
        - High Heterogeneity: favors Clarke-Wright and Tabu exchange.
        """
        bias = 0.0
        n_cust = context.get("num_customers", 20)
        fleet_hetero = context.get("fleet_heterogeneity_index", 0.0)
        pool_diversity = context.get("pool_diversity", 0.5)

        # 1. Stagnation-driven diversification
        if stagnation >= 2:
            if operator in ("OP_QIGA_QUANTUM_GENETIC", "OP_ALNS_RUIN_RECREATE", "OP_QAOA_SUBPROBLEM"):
                bias += 0.35 * min(3, stagnation)
            elif operator in ("OP_DEEP_VND_REFINE", "OP_ORTOOLS_LOCAL_REPAIR"):
                bias -= 0.15

        # 2. Low population diversity
        if pool_diversity < 0.25:
            if operator in ("OP_QIGA_QUANTUM_GENETIC", "OP_SPARK_POLAR_SWEEP"):
                bias += 0.25

        # 3. Problem scale
        if n_cust <= 15:
            if operator in ("OP_ORTOOLS_LOCAL_REPAIR", "OP_DEEP_VND_REFINE"):
                bias += 0.20
        elif n_cust >= 30:
            if operator in ("OP_SPARK_POLAR_SWEEP", "OP_ALNS_RUIN_RECREATE", "OP_TABU_SEARCH_EXCHANGE"):
                bias += 0.25

        # 4. Fleet heterogeneity
        if fleet_hetero > 0.3 and operator in ("OP_CLARKE_WRIGHT_SAVINGS", "OP_TABU_SEARCH_EXCHANGE"):
            bias += 0.20

        # 5. Low remaining time budget
        if budget_ratio < 0.25:
            if operator in ("OP_QAOA_SUBPROBLEM", "OP_ALNS_RUIN_RECREATE"):
                bias -= 0.40  # prevent timeout
            elif operator in ("OP_DEEP_VND_REFINE", "OP_TABU_SEARCH_EXCHANGE"):
                bias += 0.25

        return float(bias)

    def get_summary(self) -> Dict[str, Any]:
        """Returns statistical overview of operator performance and selection frequencies."""
        return {
            "total_invocations": self.total_invocations,
            "operator_performance": {
                op: {
                    "invocations": self.action_counts[op],
                    "successes": self.success_counts[op],
                    "success_rate": round(
                        self.success_counts[op] / max(1, self.action_counts[op]), 3
                    ),
                    "q_value": round(self.q_values[op], 4),
                }
                for op in self.OPERATORS
            },
        }
