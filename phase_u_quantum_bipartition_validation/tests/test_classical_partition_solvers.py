"""
Unit tests for Phase U Classical Partitioning Solvers Suite.
"""

import sys
import os
import math
import pytest
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from phase_u_quantum_bipartition_validation.prototypes.classical_partition_solvers import (
    ClassicalPartitioningSuite
)


def test_classical_partitioning_methods():
    suite = ClassicalPartitioningSuite()
    np.random.seed(42)

    N = 8
    Q = np.random.uniform(-5.0, 5.0, (N, N))
    Q = 0.5 * (Q + Q.T)
    demands = np.random.randint(2, 6, N)
    h_diff = np.random.uniform(-10.0, 10.0, N)
    cap_a = 18.0
    cap_b = 18.0
    polar_angles = np.random.uniform(-math.pi, math.pi, N)

    # 1. Exact Enumeration
    res_exact = suite.exact_enumeration(Q, demands, cap_a, cap_b)
    assert res_exact["states_evaluated"] == 256
    assert sum(demands[i] for i in range(N) if res_exact["best_feasible_partition"][i] == 1) <= cap_a

    # 2. Greedy
    res_greedy = suite.greedy_capacity_constrained(Q, demands, h_diff, cap_a, cap_b)
    assert sum(demands[i] for i in range(N) if res_greedy["partition"][i] == 1) <= cap_a
    assert sum(demands[i] for i in range(N) if res_greedy["partition"][i] == 0) <= cap_b

    # 3. Sweep
    res_sweep = suite.sweep_partitioning(Q, demands, polar_angles, cap_a, cap_b, h_diff)
    assert sum(demands[i] for i in range(N) if res_sweep["partition"][i] == 1) <= cap_a
    assert sum(demands[i] for i in range(N) if res_sweep["partition"][i] == 0) <= cap_b

    # 4. Kernighan-Lin
    res_kl = suite.kernighan_lin_balanced(Q, demands, h_diff, cap_a, cap_b)
    assert sum(demands[i] for i in range(N) if res_kl["partition"][i] == 1) <= cap_a
    assert sum(demands[i] for i in range(N) if res_kl["partition"][i] == 0) <= cap_b

    # 5. Multistart Local Search
    res_ms = suite.multistart_local_search(Q, demands, h_diff, cap_a, cap_b, restarts=10)
    assert sum(demands[i] for i in range(N) if res_ms["partition"][i] == 1) <= cap_a

    # 6. Simulated Annealing
    res_sa = suite.simulated_annealing(Q, demands, h_diff, cap_a, cap_b, steps=100)
    assert sum(demands[i] for i in range(N) if res_sa["partition"][i] == 1) <= cap_a
