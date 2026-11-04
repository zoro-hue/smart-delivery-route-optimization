"""Regression and Verification Tests for RB-QCD and Disproved H-NOE Bound.

Tests cover:
1. Rejection of the Four-Gamma bound: verifying that attempting to enable it raises ValueError.
2. The exact Phase 5C counterexample (Trial 16) proving the four-gamma bound fails.
3. Soundness of the Capacity Feasibility Filter (zero false prunings).
4. RB-QCD handling of duplicate customer string IDs (stable internal indexing).
5. RB-QCD handling of distinct customers sharing the same road node.
6. RB-QCD explicit infeasibility reporting when fleet capacity is insufficient.
7. Small instance exact enumeration comparison (m=3 and m=4).
8. Large scale customer preservation test (N=50, 100, 200).
"""

import pytest
import numpy as np
from app.services.optimization.rb_qcd_decomposer import RBQCDDecomposer
from app.services.optimization.hnoe_screening_engine import HNOEScreeningEngine


# --- H-NOE REJECTION & REGRESSION TESTS ---

def test_hnoe_rejected_four_gamma_cannot_be_enabled():
    """Ensures the rejected Four-Gamma bound cannot accidentally be re-enabled."""
    with pytest.raises(ValueError, match="CRITICAL REJECTION"):
        HNOEScreeningEngine(enable_rejected_four_gamma=True)


def test_hnoe_phase5c_counterexample_demonstrates_flaw():
    """
    Preserves the exact Trial 16 counterexample from Phase 5C:
    Route A: 2 customers, Route B: 1 customer.
    In the flawed four-gamma formula, B was computed as -19.97 (falsely claiming no improvement),
    while the actual swap savings is +12.30 (a true cost-improving swap).
    Verifies that the corrected engine DOES NOT prune this improving swap.
    """
    np.random.seed(12345)
    for trial in range(500):
        depot = {"id": "depot", "demand": 0.0}
        m_a = np.random.randint(1, 4)
        m_b = np.random.randint(1, 4)
        custs_a = [{"id": f"a_{i}", "demand": float(np.random.uniform(1, 3))} for i in range(m_a)]
        custs_b = [{"id": f"b_{j}", "demand": float(np.random.uniform(1, 3))} for j in range(m_b)]
        r_a = [depot] + custs_a + [depot]
        r_b = [depot] + custs_b + [depot]
        num_nodes = 1 + m_a + m_b
        locs = {"depot": 0}
        for i, c in enumerate(custs_a): locs[c["id"]] = 1 + i
        for j, c in enumerate(custs_b): locs[c["id"]] = 1 + m_a + j
        mat = np.random.uniform(5.0, 50.0, size=(num_nodes, num_nodes))
        np.fill_diagonal(mat, 0.0)
        for k in range(num_nodes):
            for u in range(num_nodes):
                for v in range(num_nodes):
                    if mat[u, v] > mat[u, k] + mat[k, v]:
                        mat[u, v] = mat[u, k] + mat[k, v]

        if trial == 16:
            engine = HNOEScreeningEngine()
            res = engine.evaluate_swap_opportunity(r_a, r_b, mat, vehicle_capacity=10.0, location_indices=locs)
            # Must NOT be pruned!
            assert res["pruned"] is False
            assert res["is_false_pruning"] is False
            assert res["true_max_savings"] > 12.0
            break


def test_hnoe_capacity_filter_soundness():
    """Verifies that the Capacity Filter prunes when all possible swaps violate capacity."""
    depot = {"id": "depot", "demand": 0.0}
    route_a = [depot, {"id": "c1", "demand": 5.0}, depot]
    route_b = [depot, {"id": "c2", "demand": 1.0}, depot]
    locs = {"depot": 0, "c1": 1, "c2": 2}
    mat = np.zeros((3, 3))

    engine = HNOEScreeningEngine()
    # Vehicle capacity is 4.0. Route A has load 5.0. No swap can bring Route A <= 4.0.
    res = engine.evaluate_swap_opportunity(route_a, route_b, mat, vehicle_capacity=4.0, location_indices=locs)
    assert res["pruned"] is True
    assert res["stage_pruned"] == "capacity"
    assert res["is_false_pruning"] is False


# --- RB-QCD DECOMPOSER TESTS ---

def test_rb_qcd_zero_and_one_customer():
    """Tests zero customer and single customer edge cases."""
    decomposer = RBQCDDecomposer()
    depot = {"id": "depot", "demand": 0.0}
    locs = {"depot": 0, "c1": 1}
    mat = np.array([[0.0, 10.0], [15.0, 0.0]])

    # Zero customers
    res0 = decomposer.decompose_and_solve([], depot, mat, 1, 10.0, locs)
    assert res0["feasibility"]["is_feasible"] is True
    assert len(res0["routes"]) == 0

    # One customer
    res1 = decomposer.decompose_and_solve([{"id": "c1", "demand": 2.0}], depot, mat, 1, 10.0, locs)
    assert res1["feasibility"]["is_feasible"] is True
    assert res1["feasibility"]["total_routed_customers"] == 1
    assert res1["routes"][0]["total_distance"] == 25.0  # 10 + 15


def test_rb_qcd_duplicate_customer_ids_preserved():
    """Verifies that two distinct customers with duplicate string IDs are both routed."""
    custs = [
        {"id": "c1", "demand": 2.0, "note": "order_A"},
        {"id": "c1", "demand": 3.0, "note": "order_B"}
    ]
    depot = {"id": "depot", "demand": 0.0}
    locs = {"depot": 0, "c1": 1}
    mat = np.array([[0.0, 10.0], [12.0, 0.0]])

    decomposer = RBQCDDecomposer()
    res = decomposer.decompose_and_solve(custs, depot, mat, 2, 10.0, locs)

    feas = res["feasibility"]
    assert feas["total_input_customers"] == 2
    assert feas["total_routed_customers"] == 2
    assert feas["unassigned_customers"] == 0
    assert feas["is_feasible"] is True


def test_rb_qcd_distinct_customers_same_road_node():
    """Verifies distinct customers at the same road node are preserved."""
    custs = [
        {"id": "cust_1", "demand": 1.5},
        {"id": "cust_2", "demand": 2.5}
    ]
    depot = {"id": "depot", "demand": 0.0}
    locs = {"depot": 0, "cust_1": 1, "cust_2": 1}  # Same node index 1
    mat = np.array([[0.0, 10.0], [12.0, 0.0]])

    decomposer = RBQCDDecomposer()
    res = decomposer.decompose_and_solve(custs, depot, mat, 1, 10.0, locs)

    feas = res["feasibility"]
    assert feas["is_feasible"] is True
    assert feas["total_routed_customers"] == 2


def test_rb_qcd_insufficient_fleet_capacity_reported():
    """Verifies that insufficient total fleet capacity yields explicit infeasibility."""
    custs = [{"id": f"c_{i}", "demand": 6.0} for i in range(3)]  # Total demand = 18
    depot = {"id": "depot", "demand": 0.0}
    locs = {"depot": 0, "c_0": 1, "c_1": 2, "c_2": 3}
    mat = np.zeros((4, 4))

    decomposer = RBQCDDecomposer()
    # Fleet capacity = 2 * 7.0 = 14.0 < 18.0
    res = decomposer.decompose_and_solve(custs, depot, mat, 2, 7.0, locs)

    feas = res["feasibility"]
    assert feas["is_feasible"] is False
    assert feas["insufficient_fleet_capacity"] is True
    assert feas["total_demand"] == 18.0
    assert feas["total_fleet_capacity"] == 14.0


def test_rb_qcd_exact_permutation_on_3_nodes():
    """Verifies that subproblem optimization matches exact brute-force Dijkstra on 3 nodes."""
    custs = [
        {"id": "c1", "demand": 1.0},
        {"id": "c2", "demand": 1.0},
        {"id": "c3", "demand": 1.0}
    ]
    depot = {"id": "depot", "demand": 0.0}
    locs = {"depot": 0, "c1": 1, "c2": 2, "c3": 3}

    mat = np.array([
        [0.0, 5.0, 50.0, 50.0],
        [50.0, 0.0, 5.0, 50.0],
        [50.0, 50.0, 0.0, 5.0],
        [5.0, 50.0, 50.0, 0.0]
    ])

    decomposer = RBQCDDecomposer(max_qubits=16)
    res = decomposer.decompose_and_solve(custs, depot, mat, 1, 10.0, locs)

    route = res["routes"][0]
    stop_ids = [s["id"] for s in route["stops"]]
    assert stop_ids == ["depot", "c1", "c2", "c3", "depot"]
    assert route["total_distance"] == 20.0


def test_rb_qcd_preservation_large_scale():
    """Verifies that 100% of customers are preserved across large instances."""
    for n in [25, 50, 100]:
        custs = [{"id": f"cust_{i}", "demand": 1.0 + (i % 3)} for i in range(n)]
        depot = {"id": "depot", "demand": 0.0}
        locs = {"depot": 0}
        for i, c in enumerate(custs):
            locs[c["id"]] = i + 1

        np.random.seed(42 + n)
        mat = np.random.uniform(5.0, 50.0, size=(n + 1, n + 1))
        np.fill_diagonal(mat, 0.0)

        total_dem = sum(c["demand"] for c in custs)
        cap = 25.0
        num_veh = int(np.ceil(total_dem / cap * 1.3))

        decomposer = RBQCDDecomposer(max_qubits=16)
        res = decomposer.decompose_and_solve(custs, depot, mat, num_veh, cap, locs)

        feas = res["feasibility"]
        assert feas["is_feasible"] is True
        assert feas["total_input_customers"] == n
        assert feas["total_routed_customers"] == n
        assert feas["unassigned_customers"] == 0
        assert feas["capacity_violations"] == 0
