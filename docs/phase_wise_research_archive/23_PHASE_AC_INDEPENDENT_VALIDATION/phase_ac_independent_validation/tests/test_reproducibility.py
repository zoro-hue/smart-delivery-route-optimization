import pytest
import numpy as np
import pandas as pd
import os
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from phase_ab_cooperative_optimization_engine.benchmarks.benchmark_complete_system import CompleteSystemBenchmarkRunner
from phase_ab_cooperative_optimization_engine.engine.spark_preprocessor import SparkWorkloadOrganizer
from phase_ab_cooperative_optimization_engine.engine.adaptive_controller import AdaptiveCooperativeController


def test_instance_generation_reproducibility():
    """Verifies that seed-based instance generation produces bit-for-bit identical coordinates and demands."""
    runner = CompleteSystemBenchmarkRunner()
    inst1 = runner.generate_instance(seed=405, N=16)
    inst2 = runner.generate_instance(seed=405, N=16)

    np.testing.assert_array_equal(inst1["coords"], inst2["coords"])
    np.testing.assert_array_equal(inst1["dist_matrix"], inst2["dist_matrix"])
    np.testing.assert_array_equal(inst1["demands"], inst2["demands"])
    assert inst1["cap_a"] == inst2["cap_a"]
    assert inst1["cap_b"] == inst2["cap_b"]


def test_spark_vs_numpy_semantic_equivalence():
    """Verifies that Spark and NumPy extract the identical set of boundary customers."""
    spark_org = SparkWorkloadOrganizer(master="local[1]")
    numpy_org = SparkWorkloadOrganizer(master="local[1]")
    numpy_org.spark = None

    np.random.seed(123)
    df_raw = pd.DataFrame({
        "stop_id": [f"stop_{i}" for i in range(100)],
        "latitude": np.random.uniform(40.70, 40.85, 100),
        "longitude": np.random.uniform(-74.02, -73.93, 100),
        "demand": np.random.randint(1, 5, 100)
    })

    depot = (40.75, -73.98)
    c_a = (40.73, -73.99)
    c_b = (40.79, -73.95)

    res_spark = spark_org.partition_fleet_workload(df_raw, depot, c_a, c_b)
    res_numpy = numpy_org.partition_fleet_workload(df_raw, depot, c_a, c_b)

    assert set(res_spark["boundary_stop_ids"]) == set(res_numpy["boundary_stop_ids"])
    assert res_spark["num_boundary_customers"] == res_numpy["num_boundary_customers"]


def test_controller_feature_no_data_leakage():
    """Verifies that controller features do not contain or depend on candidate route outcomes."""
    controller = AdaptiveCooperativeController()
    features = {
        "subproblem_size": 16,
        "capacity_slack": 0.12,
        "interaction_density": 0.85,
        "stagnation_count": 0,
        "remaining_budget_ms": 45.0
    }
    # Features must evaluate without needing candidate distance or tour lengths
    strat, meta = controller.select_strategy(**features, seed=42)
    assert strat in ["KL_Single", "Tabu_Search", "Multistart_KL", "Random_Feasible", "QAOA_Quantum"]
    assert "score" in meta
    assert "reason" in meta
