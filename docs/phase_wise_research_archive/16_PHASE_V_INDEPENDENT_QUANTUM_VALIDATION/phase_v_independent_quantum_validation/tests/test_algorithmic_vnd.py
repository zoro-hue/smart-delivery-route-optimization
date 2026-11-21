"""
Unit tests for Phase V Algorithmic VND.
"""

import sys
import os
import numpy as np
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from phase_v_independent_quantum_validation.prototypes.algorithmic_vnd import AlgorithmicVND


def test_algorithmic_vnd():
    # 5 nodes: 0 is depot, 1..4 are customers
    dist = np.array([
        [0.0, 2.0, 4.0, 3.0, 5.0],
        [2.0, 0.0, 2.0, 3.0, 4.0],
        [4.0, 2.0, 0.0, 3.0, 2.0],
        [3.0, 3.0, 3.0, 0.0, 2.0],
        [5.0, 4.0, 2.0, 2.0, 0.0]
    ])
    demands = np.array([2, 3, 2, 3])  # for nodes 1, 2, 3, 4
    cap_a = 6.0
    cap_b = 6.0

    tour_a = [1, 2]
    tour_b = [3, 4]

    init_dist = AlgorithmicVND.compute_tour_length(tour_a, dist) + AlgorithmicVND.compute_tour_length(tour_b, dist)
    res = AlgorithmicVND.optimize_fleet_routes(tour_a, tour_b, demands, cap_a, cap_b, dist)

    assert res["total_distance"] <= init_dist + 1e-4
    # Check that capacity is respected
    load_a = sum(demands[k - 1] for k in res["tour_a"])
    load_b = sum(demands[k - 1] for k in res["tour_b"])
    assert load_a <= cap_a
    assert load_b <= cap_b
    assert set(res["tour_a"] + res["tour_b"]) == {1, 2, 3, 4}
