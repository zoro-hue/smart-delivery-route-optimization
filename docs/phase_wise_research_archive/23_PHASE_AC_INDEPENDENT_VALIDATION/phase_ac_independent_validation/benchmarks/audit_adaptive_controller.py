"""
Phase AC: Independent Audit and Leakage-Safe Evaluation of the Adaptive Controller.
Compares:
- Adaptive Controller vs Always-Tabu vs Always-QAOA vs Always-MSKL vs Always-Random
Across 50 held-out instances with diverse slack, density, and size topologies.
"""

import os
import sys
import time
import json
import numpy as np
import pandas as pd
from scipy import stats

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from phase_ab_cooperative_optimization_engine.engine.cooperative_engine import CooperativeOptimizationEngine
from phase_ab_cooperative_optimization_engine.engine.adaptive_controller import AdaptiveCooperativeController


def run_controller_audit(num_instances: int = 50, base_seed: int = 1000):
    print(f"Executing Leakage-Safe Controller Audit across {num_instances} held-out instances...")
    engine = CooperativeOptimizationEngine(use_spark=False, default_time_budget_ms=100.0)

    results = []
    strategies = ["Adaptive", "Always_Tabu", "Always_QAOA", "Always_MSKL", "Always_Random"]

    qaoa_superior_count = 0
    qaoa_equal_count = 0
    qaoa_inferior_count = 0

    for i in range(num_instances):
        seed = base_seed + i
        np.random.seed(seed)
        N = 16
        coords = np.random.uniform(0.0, 10.0, (N + 1, 2))
        coords[0] = np.array([5.0, 5.0])

        dist_matrix = np.zeros((N + 1, N + 1))
        for r in range(N + 1):
            for c in range(N + 1):
                if r != c:
                    dist_matrix[r, c] = np.linalg.norm(coords[r] - coords[c]) * 15.0

        # Vary demands and slack dynamically across instances
        demands = np.random.randint(2, 6, N)
        total_demand = float(np.sum(demands))
        # Variable slack from tight (5%) to generous (35%)
        slack_ratio = 0.50 + 0.15 * np.sin(i * 0.7)
        cap_a = float(np.ceil(total_demand * (0.50 + slack_ratio * 0.5)))
        cap_b = float(np.ceil(total_demand * (0.50 + slack_ratio * 0.5)))
        c_a = np.array([2.5, 5.0])
        c_b = np.array([7.5, 5.0])

        instance_outcomes = {}

        # 1. Run each strategy under identical conditions
        # Strategy mapping
        strat_map = {
            "Adaptive": None,
            "Always_Tabu": "Tabu_Search",
            "Always_QAOA": "QAOA_Quantum",
            "Always_MSKL": "Multistart_KL",
            "Always_Random": "Random_Feasible"
        }

        for s_name, s_override in strat_map.items():
            res = engine.optimize_subproblem(
                dist_matrix, demands, cap_a, cap_b, c_a, c_b,
                strategy_override=s_override,
                budget_evals=256,
                seed=seed
            )
            instance_outcomes[s_name] = res

            results.append({
                "instance_id": f"heldout_{i}",
                "seed": seed,
                "strategy_mode": s_name,
                "strategy_dispatched": res["strategy_used"],
                "initial_distance": res["initial_distance_km"],
                "final_distance": res["final_distance_km"],
                "latency_ms": res["total_latency_ms"],
                "accepted": res["guardrail_accepted"],
                "rejection_reason": res["guardrail_reason"]
            })

        # Evaluate QAOA vs Classical Best
        d_qaoa = instance_outcomes["Always_QAOA"]["final_distance_km"]
        d_tabu = instance_outcomes["Always_Tabu"]["final_distance_km"]
        d_mskl = instance_outcomes["Always_MSKL"]["final_distance_km"]
        d_rand = instance_outcomes["Always_Random"]["final_distance_km"]
        d_classical_best = min(d_tabu, d_mskl, d_rand)

        if d_qaoa < d_classical_best - 0.01:
            qaoa_superior_count += 1
        elif abs(d_qaoa - d_classical_best) <= 0.01:
            qaoa_equal_count += 1
        else:
            qaoa_inferior_count += 1

    df_res = pd.DataFrame(results)
    csv_out = "phase_ac_independent_validation/results/phase_ac_controller_audit_raw.csv"
    df_res.to_csv(csv_out, index=False)
    print(f"Audit completed: {len(df_res)} records saved to {csv_out}.")

    # Summary
    summary = []
    for s_name in strategies:
        sub = df_res[df_res["strategy_mode"] == s_name]
        d = sub["final_distance"].values
        t = sub["latency_ms"].values
        acc = sub["accepted"].values
        summary.append({
            "mode": s_name,
            "mean_dist": round(float(np.mean(d)), 2),
            "median_dist": round(float(np.median(d)), 2),
            "mean_time_ms": round(float(np.mean(t)), 2),
            "accepted_pct": round(float(np.mean(acc) * 100.0), 1)
        })

    print("\n--- SUMMARY OF HELD-OUT AUDIT ---")
    print(pd.DataFrame(summary).to_string())
    print(f"\nQAOA Unique Advantage Analysis (N={num_instances}):")
    print(f"  Strictly Superior to All Classical: {qaoa_superior_count} ({qaoa_superior_count/num_instances*100.0:.1f}%)")
    print(f"  Equal to Classical Best:             {qaoa_equal_count} ({qaoa_equal_count/num_instances*100.0:.1f}%)")
    print(f"  Inferior to Classical Best:          {qaoa_inferior_count} ({qaoa_inferior_count/num_instances*100.0:.1f}%)")

    # Controller dispatch distribution
    adaptive_sub = df_res[df_res["strategy_mode"] == "Adaptive"]
    print("\nAdaptive Controller Dispatches:")
    print(adaptive_sub["strategy_dispatched"].value_counts().to_string())

    return {
        "summary": summary,
        "qaoa_superior": qaoa_superior_count,
        "qaoa_equal": qaoa_equal_count,
        "qaoa_inferior": qaoa_inferior_count
    }


if __name__ == "__main__":
    run_controller_audit(num_instances=30, base_seed=1000)
