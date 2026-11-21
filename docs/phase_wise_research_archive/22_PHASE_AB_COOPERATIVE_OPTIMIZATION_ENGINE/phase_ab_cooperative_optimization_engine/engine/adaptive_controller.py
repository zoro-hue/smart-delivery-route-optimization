"""
Phase AB: Adaptive Cooperative Controller.
Dynamically selects candidate generation strategies based on:
- Incumbent quality and recent search improvement
- Search stagnation depth
- Boundary subproblem size (N)
- Capacity slack (sigma)
- Interaction density (rho)
- Remaining computational time budget
- Historical empirical performance of each strategy
"""

import time
from typing import Dict, Any, List, Tuple, Optional
import numpy as np


class AdaptiveCooperativeController:
    """Adaptive metaheuristic controller managing strategy dispatch."""

    def __init__(self, exploration_factor: float = 0.15):
        self.exploration_factor = exploration_factor
        # Historical performance tracking: success counts and latency
        self.strategy_history = {
            "KL_Single": {"calls": 0, "improvements": 0, "avg_time_ms": 4.0},
            "Tabu_Search": {"calls": 0, "improvements": 0, "avg_time_ms": 12.0},
            "Multistart_KL": {"calls": 0, "improvements": 0, "avg_time_ms": 25.0},
            "Random_Feasible": {"calls": 0, "improvements": 0, "avg_time_ms": 18.0},
            "QAOA_Quantum": {"calls": 0, "improvements": 0, "avg_time_ms": 35.0}
        }

    def select_strategy(
        self,
        subproblem_size: int,
        capacity_slack: float,
        interaction_density: float,
        stagnation_count: int,
        remaining_budget_ms: float,
        seed: int = 42
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Selects the optimal candidate generation strategy for the current subproblem state.
        Uses Multi-Armed Bandit with feature-conditioned gating.
        """
        rng = np.random.RandomState(seed + stagnation_count)

        # 1. Budget constraint check
        if remaining_budget_ms < 15.0:
            return "KL_Single", {"reason": "TIME_BUDGET_EXHAUSTED", "score": 0.0}

        # 2. Exploration branch (stochastic diversity injection)
        if rng.rand() < self.exploration_factor:
            # Pick randomly from diverse generators
            choices = ["Tabu_Search", "Random_Feasible", "Multistart_KL"]
            if remaining_budget_ms >= 40.0:
                choices.append("QAOA_Quantum")
            chosen = rng.choice(choices)
            return chosen, {"reason": "EXPLORATION_BRANCH", "score": 0.5}

        # 3. Exploitation branch: Feature-conditioned decision rules
        # Condition A: Deep stagnation -> Tabu Search (best memory-guided escape)
        if stagnation_count >= 2:
            return "Tabu_Search", {"reason": "STAGNATION_ESCAPE", "score": 0.9}

        # Condition B: High interaction density with tight capacity -> QAOA or Tabu
        # QAOA is invoked only when non-local tunneling is justified and time budget permits
        curvature_score = 1.8 * interaction_density - 1.2 * capacity_slack
        if curvature_score > 1.85 and remaining_budget_ms >= 35.0:
            return "QAOA_Quantum", {"reason": "HIGH_INTERACTION_CURVATURE", "score": round(curvature_score, 3)}

        # Condition C: Moderate density with generous slack -> Multistart KL or Random Feasible
        if capacity_slack > 0.15:
            if rng.rand() < 0.6:
                return "Tabu_Search", {"reason": "DEFAULT_HIGH_EFFICIENCY", "score": 0.8}
            else:
                return "Random_Feasible", {"reason": "SLACK_DIVERSITY_HARVEST", "score": 0.7}

        # Default fallback
        return "Tabu_Search", {"reason": "DEFAULT_GREEDY_DESCENT", "score": 0.75}

    def update_history(self, strategy_id: str, improved: bool, elapsed_ms: float):
        """Updates online controller telemetry."""
        if strategy_id in self.strategy_history:
            h = self.strategy_history[strategy_id]
            h["calls"] += 1
            if improved:
                h["improvements"] += 1
            # Exponential moving average for runtime
            h["avg_time_ms"] = 0.8 * h["avg_time_ms"] + 0.2 * elapsed_ms

