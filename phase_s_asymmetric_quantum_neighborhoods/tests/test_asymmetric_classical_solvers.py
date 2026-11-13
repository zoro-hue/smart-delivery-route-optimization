"""
Unit tests for Phase S Asymmetric Classical Solvers Suite.
"""

import sys
import os
import pytest
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from phase_s_asymmetric_quantum_neighborhoods.prototypes.asymmetric_classical_solvers import (
    AsymmetricDirectedLocalSearchSuite
)


def test_asymmetric_directed_operators():
    suite = AsymmetricDirectedLocalSearchSuite()
    np.random.seed(42)

    # 6x6 highly asymmetric distance matrix
    dist_mat = np.random.uniform(5.0, 30.0, (6, 6))
    for i in range(6):
        for j in range(6):
            if i != j:
                dist_mat[i, j] += np.random.uniform(0.0, 20.0)
    np.fill_diagonal(dist_mat, 0.0)

    entry = 0
    exit_node = 5
    sub_locs = [1, 2, 3, 4]
    seed_perm = [3, 0, 2, 1]

    exact_res = suite.exact_enumeration(dist_mat, sub_locs, entry, exit_node)
    assert exact_res["evaluations"] == 24
    assert len(exact_res["best_perm"]) == 4

    # Test Directed 2-opt
    res_2opt = suite.directed_2opt(seed_perm, dist_mat, sub_locs, entry, exit_node)
    assert res_2opt["cost_km"] <= suite.compute_directed_cost(seed_perm, dist_mat, sub_locs, entry, exit_node)
    assert sorted(res_2opt["best_perm"]) == [0, 1, 2, 3]

    # Test Relocate
    res_reloc = suite.relocate_search(seed_perm, dist_mat, sub_locs, entry, exit_node)
    assert res_reloc["cost_km"] <= suite.compute_directed_cost(seed_perm, dist_mat, sub_locs, entry, exit_node)
    assert sorted(res_reloc["best_perm"]) == [0, 1, 2, 3]

    # Test Swap
    res_swap = suite.swap_search(seed_perm, dist_mat, sub_locs, entry, exit_node)
    assert res_swap["cost_km"] <= suite.compute_directed_cost(seed_perm, dist_mat, sub_locs, entry, exit_node)
    assert sorted(res_swap["best_perm"]) == [0, 1, 2, 3]

    # Test VND
    res_vnd = suite.variable_neighborhood_descent(seed_perm, dist_mat, sub_locs, entry, exit_node)
    assert res_vnd["cost_km"] <= res_2opt["cost_km"]
    assert sorted(res_vnd["best_perm"]) == [0, 1, 2, 3]

    # Test VNS
    res_vns = suite.variable_neighborhood_search(seed_perm, dist_mat, sub_locs, entry, exit_node, max_shaking_iter=5)
    assert res_vns["cost_km"] <= res_vnd["cost_km"] + 1e-4
    assert sorted(res_vns["best_perm"]) == [0, 1, 2, 3]

