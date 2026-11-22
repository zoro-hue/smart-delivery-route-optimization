import pytest
import numpy as np
import pandas as pd
import os
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from phase_ab_cooperative_optimization_engine.engine.spark_preprocessor import SparkWorkloadOrganizer
from phase_ab_cooperative_optimization_engine.engine.candidate_generators import (
    UniformRandomGenerator,
    KernighanLinGenerator,
    TabuSearchGenerator,
    QAOACandidateGenerator
)
from phase_ab_cooperative_optimization_engine.engine.classical_engine import ClassicalOptimizationEngine
from phase_ab_cooperative_optimization_engine.engine.proposition1_guardrail import Proposition1Guardrail
from phase_ab_cooperative_optimization_engine.engine.adaptive_controller import AdaptiveCooperativeController
from phase_ab_cooperative_optimization_engine.engine.cooperative_engine import CooperativeOptimizationEngine


def test_spark_workload_organizer():
    organizer = SparkWorkloadOrganizer(master="local[1]")
    raw_data = {
        "stop_id": [1, 2, 3, 4, 5, 2], # duplicate stop 2
        "latitude": [12.91, 12.92, 12.95, 12.98, None, 12.92], # NaN latitude on row 4
        "longitude": [77.58, 77.60, 77.62, 77.65, 77.70, 77.60],
        "demand": [5.0, 10.0, 15.0, 12.0, 8.0, 10.0]
    }
    df_raw = pd.DataFrame(raw_data)
    df_clean, t_ingest = organizer.ingest_and_validate(df_raw)

    assert df_clean.shape[0] == 4
    assert set(df_clean["stop_id"]) == {1, 2, 3, 4}
    assert t_ingest >= 0.0

    # Test spatial partitioning & boundary extraction
    depot = (12.90, 77.55)
    centroid_a = (12.92, 77.59)
    centroid_b = (12.96, 77.64)

    partition_res = organizer.partition_fleet_workload(
        df_clean=df_clean,
        depot_coords=depot,
        centroid_a=centroid_a,
        centroid_b=centroid_b,
        boundary_threshold=0.08,
        max_boundary_size=16
    )

    assert "boundary_stop_ids" in partition_res
    assert "total_customers_processed" in partition_res
    assert partition_res["total_customers_processed"] == 4
    assert partition_res["decomposition_latency_ms"] >= 0.0


def test_candidate_generators_standardized_interface():
    N = 6
    Q = np.zeros((N, N))
    demands = np.array([5.0, 8.0, 6.0, 7.0, 9.0, 5.0])
    h_diff = np.zeros(N)
    cap_a = 25.0
    cap_b = 25.0

    # Populate synthetic symmetric Q matrix
    for i in range(N):
        for j in range(i + 1, N):
            Q[i, j] = -0.5
            Q[j, i] = -0.5

    generators = [
        ("KL_Single", KernighanLinGenerator(multistart=False)),
        ("Multistart_KL", KernighanLinGenerator(multistart=True)),
        ("Tabu_Search", TabuSearchGenerator()),
        ("Random_Feasible", UniformRandomGenerator()),
        ("QAOA_Fast", QAOACandidateGenerator(use_xy_mixer=True, fast_mode=True))
    ]

    for name, gen in generators:
        res = gen.generate(
            Q=Q,
            demands=demands,
            h_diff=h_diff,
            cap_a=cap_a,
            cap_b=cap_b,
            budget_evals=32,
            time_budget_ms=100.0,
            seed=42
        )
        assert res.generator_id is not None
        assert res.best_partition is not None
        assert len(res.best_partition) == N
        assert res.num_generated > 0
        assert res.total_time_ms >= 0.0
        assert "Classical" in res.backend_device or "IBM" in res.backend_device


def test_proposition1_guardrail_guarantee():
    guardrail = Proposition1Guardrail()
    demands = np.array([10.0, 10.0, 10.0, 10.0])
    cap_a = 25.0
    cap_b = 25.0

    # 5x5 distance matrix (0=depot, 1..4=customers)
    dist_matrix = np.array([
        [0.0, 2.0, 2.0, 8.0, 8.0],
        [2.0, 0.0, 1.0, 7.0, 7.0],
        [2.0, 1.0, 0.0, 7.0, 7.0],
        [8.0, 7.0, 7.0, 0.0, 1.0],
        [8.0, 7.0, 7.0, 1.0, 0.0]
    ])

    incumbent_ta = [1, 2] # demand = 20 <= 25
    incumbent_tb = [3, 4] # demand = 20 <= 25

    # 1. Candidate with capacity violation: Vehicle A has [1, 2, 3] demand = 30 > 25
    viol_cand_ta = [1, 2, 3]
    viol_cand_tb = [4]
    res_viol = guardrail.validate_and_filter(
        viol_cand_ta, viol_cand_tb, incumbent_ta, incumbent_tb, demands, cap_a, cap_b, dist_matrix
    )
    assert not res_viol["accepted"]
    assert "CAPACITY" in res_viol["rejection_reason"]
    assert res_viol["is_feasible"] is True

    # 2. Candidate with invalid customer coverage: Missing customer 4
    cov_cand_ta = [1, 2]
    cov_cand_tb = [3]
    res_cov = guardrail.validate_and_filter(
        cov_cand_ta, cov_cand_tb, incumbent_ta, incumbent_tb, demands, cap_a, cap_b, dist_matrix
    )
    assert not res_cov["accepted"]
    assert res_cov["rejection_reason"] == "INVALID_CUSTOMER_COVERAGE"

    # 3. Degraded candidate: cross-swapped tours that increase distance
    deg_cand_ta = [1, 4]
    deg_cand_tb = [2, 3]
    res_deg = guardrail.validate_and_filter(
        deg_cand_ta, deg_cand_tb, incumbent_ta, incumbent_tb, demands, cap_a, cap_b, dist_matrix
    )
    assert not res_deg["accepted"]
    assert "SUBOPTIMAL" in res_deg["rejection_reason"]
    assert res_deg["final_distance"] <= 35.0  # Retains incumbent


def test_adaptive_controller_feature_routing():
    controller = AdaptiveCooperativeController(exploration_factor=0.0)

    # Tight budget (< 15ms) -> fast fallback KL_Single
    strat, meta = controller.select_strategy(
        subproblem_size=8,
        capacity_slack=0.20,
        interaction_density=0.50,
        stagnation_count=0,
        remaining_budget_ms=10.0,
        seed=42
    )
    assert strat == "KL_Single"
    assert meta["reason"] == "TIME_BUDGET_EXHAUSTED"

    # Severe stagnation -> Tabu Search (best memory-guided escape)
    strat_stag, meta_stag = controller.select_strategy(
        subproblem_size=12,
        capacity_slack=0.15,
        interaction_density=0.60,
        stagnation_count=5,
        remaining_budget_ms=100.0,
        seed=42
    )
    assert strat_stag == "Tabu_Search"
    assert "STAGNATION_ESCAPE" in meta_stag["reason"]

    # High interaction curvature -> QAOA
    strat_qaoa, meta_qaoa = controller.select_strategy(
        subproblem_size=12,
        capacity_slack=0.01,
        interaction_density=1.2,
        stagnation_count=0,
        remaining_budget_ms=100.0,
        seed=42
    )
    assert strat_qaoa == "QAOA_Quantum"
    assert "HIGH_INTERACTION_CURVATURE" in meta_qaoa["reason"]

    # History update
    controller.update_history("Tabu_Search", improved=True, elapsed_ms=15.0)
    assert controller.strategy_history["Tabu_Search"]["calls"] == 1
    assert controller.strategy_history["Tabu_Search"]["improvements"] == 1


def test_cooperative_optimization_engine_subproblem_flow():
    engine = CooperativeOptimizationEngine(use_spark=False, default_time_budget_ms=100.0)

    # 5 locations: depot (0) + 4 boundary customers (1, 2, 3, 4)
    dist_matrix = np.array([
        [0.0, 3.0, 3.5, 4.0, 4.5],
        [3.0, 0.0, 1.2, 5.0, 5.5],
        [3.5, 1.2, 0.0, 5.2, 5.8],
        [4.0, 5.0, 5.2, 0.0, 1.1],
        [4.5, 5.5, 5.8, 1.1, 0.0]
    ])
    demands = np.array([8.0, 9.0, 7.0, 8.0])
    cap_a = 22.0
    cap_b = 22.0
    c_a = np.array([12.92, 77.59])
    c_b = np.array([12.96, 77.64])

    result = engine.optimize_subproblem(
        dist_matrix=dist_matrix,
        demands=demands,
        cap_a=cap_a,
        cap_b=cap_b,
        c_a=c_a,
        c_b=c_b,
        strategy_override="Tabu_Search",
        budget_evals=64,
        seed=42
    )

    assert result["strategy_used"] == "Tabu_Search"
    assert result["final_distance_km"] <= result["initial_distance_km"]
    assert result["guardrail_accepted"] in [True, False]
    assert len(result["final_tour_a"]) + len(result["final_tour_b"]) == 4
    assert set(result["final_tour_a"] + result["final_tour_b"]) == {1, 2, 3, 4}
