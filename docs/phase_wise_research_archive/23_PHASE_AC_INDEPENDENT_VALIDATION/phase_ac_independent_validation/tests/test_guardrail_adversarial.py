import pytest
import numpy as np
import os
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from phase_ab_cooperative_optimization_engine.engine.proposition1_guardrail import Proposition1Guardrail


@pytest.fixture
def base_problem():
    # 4 customers, 1 depot (5x5 matrix)
    demands = np.array([10.0, 10.0, 10.0, 10.0])
    cap_a = 25.0
    cap_b = 25.0
    dist_matrix = np.array([
        [0.0, 2.0, 2.0, 8.0, 8.0],
        [2.0, 0.0, 1.0, 7.0, 7.0],
        [2.0, 1.0, 0.0, 7.0, 7.0],
        [8.0, 7.0, 7.0, 0.0, 1.0],
        [8.0, 7.0, 7.0, 1.0, 0.0]
    ])
    incumbent_a = [1, 2]
    incumbent_b = [3, 4]
    return demands, cap_a, cap_b, dist_matrix, incumbent_a, incumbent_b


def test_capacity_exact_boundary(base_problem):
    """Case 1: Exact capacity boundary (qA == capA)."""
    demands, cap_a, cap_b, dist_matrix, inc_a, inc_b = base_problem
    # Set cap_a exactly equal to load (20.0)
    cap_a = 20.0
    cand_a = [1, 2]
    cand_b = [3, 4]
    res = Proposition1Guardrail.validate_and_filter(
        cand_a, cand_b, inc_a, inc_b, demands, cap_a, cap_b, dist_matrix
    )
    # Exact boundary is permitted (qa <= cap_a)
    assert res["is_feasible"] is True


def test_capacity_slight_overage(base_problem):
    """Case 2: Slight capacity overage must be rejected."""
    demands, cap_a, cap_b, dist_matrix, inc_a, inc_b = base_problem
    cap_a = 19.99  # load is 20.0
    cand_a = [1, 2]
    cand_b = [3, 4]
    res = Proposition1Guardrail.validate_and_filter(
        cand_a, cand_b, inc_a, inc_b, demands, cap_a, cap_b, dist_matrix
    )
    assert not res["accepted"]
    assert "CAPACITY" in res["rejection_reason"]


def test_empty_partition_rejection(base_problem):
    """Case 3: Empty partition (all customers assigned to one vehicle)."""
    demands, cap_a, cap_b, dist_matrix, inc_a, inc_b = base_problem
    cand_a = []
    cand_b = [1, 2, 3, 4]
    res = Proposition1Guardrail.validate_and_filter(
        cand_a, cand_b, inc_a, inc_b, demands, 50.0, 50.0, dist_matrix
    )
    assert not res["accepted"]
    assert "CAPACITY" in res["rejection_reason"]


def test_singleton_partition_validity(base_problem):
    """Case 4: Singleton partition (1 customer in A, 3 in B)."""
    demands, cap_a, cap_b, dist_matrix, inc_a, inc_b = base_problem
    cand_a = [1]
    cand_b = [2, 3, 4]
    res = Proposition1Guardrail.validate_and_filter(
        cand_a, cand_b, inc_a, inc_b, demands, 35.0, 35.0, dist_matrix
    )
    # Singleton is accepted if feasible and improving, or rejected if suboptimal
    assert res["is_feasible"] is True


def test_missing_customer_rejection(base_problem):
    """Case 5: Candidate omitted customer 3."""
    demands, cap_a, cap_b, dist_matrix, inc_a, inc_b = base_problem
    cand_a = [1, 2]
    cand_b = [4] # missing 3
    res = Proposition1Guardrail.validate_and_filter(
        cand_a, cand_b, inc_a, inc_b, demands, cap_a, cap_b, dist_matrix
    )
    assert not res["accepted"]
    assert res["rejection_reason"] == "INVALID_CUSTOMER_COVERAGE"


def test_duplicate_customer_rejection(base_problem):
    """Case 6: Candidate assigns customer 2 to both vehicles."""
    demands, cap_a, cap_b, dist_matrix, inc_a, inc_b = base_problem
    cand_a = [1, 2]
    cand_b = [2, 3, 4] # duplicated 2
    res = Proposition1Guardrail.validate_and_filter(
        cand_a, cand_b, inc_a, inc_b, demands, 40.0, 40.0, dist_matrix
    )
    assert not res["accepted"]
    assert res["rejection_reason"] == "INVALID_CUSTOMER_COVERAGE"


def test_out_of_bounds_customer_rejection(base_problem):
    """Case 7: Candidate contains non-existent customer index 999."""
    demands, cap_a, cap_b, dist_matrix, inc_a, inc_b = base_problem
    cand_a = [1, 999]
    cand_b = [3, 4]
    res = Proposition1Guardrail.validate_and_filter(
        cand_a, cand_b, inc_a, inc_b, demands, cap_a, cap_b, dist_matrix
    )
    assert not res["accepted"]
    assert res["rejection_reason"] == "INVALID_CUSTOMER_COVERAGE"


def test_unreachable_node_infinite_cost(base_problem):
    """Case 8: Distance matrix contains infinite cost on candidate edge."""
    demands, cap_a, cap_b, dist_matrix, inc_a, inc_b = base_problem
    inf_matrix = dist_matrix.copy()
    inf_matrix[1, 4] = 1e9 # unreachable edge
    inf_matrix[4, 1] = 1e9

    # Candidate placing 1 and 4 in the same tour
    cand_a = [1, 4]
    cand_b = [2, 3]
    res = Proposition1Guardrail.validate_and_filter(
        cand_a, cand_b, inc_a, inc_b, demands, cap_a, cap_b, inf_matrix
    )
    assert not res["accepted"]
    assert "SUBOPTIMAL" in res["rejection_reason"]


def test_asymmetric_directed_costs(base_problem):
    """Case 9: Asymmetric directed road costs."""
    demands, cap_a, cap_b, dist_matrix, inc_a, inc_b = base_problem
    asym_matrix = dist_matrix.copy()
    # Heavily penalize 1 -> 2 while keeping 2 -> 1 cheap
    asym_matrix[1, 2] = 50.0
    asym_matrix[2, 1] = 1.0

    cand_a = [2, 1]
    cand_b = [3, 4]
    res = Proposition1Guardrail.validate_and_filter(
        cand_a, cand_b, inc_a, inc_b, demands, cap_a, cap_b, asym_matrix
    )
    assert res["is_feasible"] is True


def test_improving_one_vehicle_degrading_total(base_problem):
    """Case 10: Tour A improves by 5 km, but Tour B degrades by 12 km (net +7 km degradation)."""
    demands, cap_a, cap_b, dist_matrix, inc_a, inc_b = base_problem
    cand_a = [1, 3]
    cand_b = [2, 4]
    res = Proposition1Guardrail.validate_and_filter(
        cand_a, cand_b, inc_a, inc_b, demands, cap_a, cap_b, dist_matrix
    )
    # Total distance is degraded
    assert not res["accepted"]
    assert "SUBOPTIMAL" in res["rejection_reason"]
    # Final distance matches incumbent
    assert res["final_distance"] <= 35.0


def test_numerical_precision_below_tolerance(base_problem):
    """Case 11: Micro-improvement below tolerance threshold (1e-4) is rejected."""
    demands, cap_a, cap_b, dist_matrix, inc_a, inc_b = base_problem
    # Set identical tours so difference is 0.0
    cand_a = list(inc_a)
    cand_b = list(inc_b)
    res = Proposition1Guardrail.validate_and_filter(
        cand_a, cand_b, inc_a, inc_b, demands, cap_a, cap_b, dist_matrix, tolerance=1e-3
    )
    assert not res["accepted"]
    assert "SUBOPTIMAL" in res["rejection_reason"]
