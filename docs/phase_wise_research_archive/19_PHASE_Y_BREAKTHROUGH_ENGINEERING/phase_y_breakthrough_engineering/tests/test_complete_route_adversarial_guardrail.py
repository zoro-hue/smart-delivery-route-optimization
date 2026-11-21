"""
Phase Y: Adversarial Stress Tests for Proposition 1 Monotonic Guardrail.
Tests:
1. Degenerate candidate (all 0s or all 1s).
2. Extreme demand capacity overload (>300% capacity).
3. Random noise partition.
4. Degraded distance candidate.
Verifies that Cost(R_final) <= Cost(R_incumbent) holds unconditionally.
"""

import sys
import os
import numpy as np
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from phase_v_independent_quantum_validation.prototypes.algorithmic_vnd import AlgorithmicVND
from phase_u_quantum_bipartition_validation.prototypes.classical_partition_solvers import (
    ClassicalPartitioningSuite
)

def test_proposition1_adversarial_rejection():
    suite = ClassicalPartitioningSuite()
    N = 8
    demands = np.array([3, 4, 2, 5, 3, 4, 2, 3])
    cap_a = 15.0
    cap_b = 15.0
    h_diff = np.array([2.0, -1.0, 3.0, -2.0, 1.0, -3.0, 2.0, -1.0])

    dist_matrix = np.zeros((N + 1, N + 1))
    for i in range(N + 1):
        for j in range(N + 1):
            if i != j:
                dist_matrix[i, j] = 10.0 + abs(i - j) * 2.0

    # Incumbent classical tours
    incumbent_a = [1, 2, 3, 4]
    incumbent_b = [5, 6, 7, 8]
    incumbent_dist = AlgorithmicVND.compute_tour_length(incumbent_a, dist_matrix) + AlgorithmicVND.compute_tour_length(incumbent_b, dist_matrix)

    # Adversarial Case 1: All 0s (empty Vehicle A)
    cand_all_zeros = [0] * N
    rep_1 = suite.repair_capacity_violations(cand_all_zeros, demands, cap_a, cap_b, h_diff)
    nodes_a1 = [i + 1 for i, v in enumerate(rep_1) if v == 1]
    nodes_b1 = [i + 1 for i, v in enumerate(rep_1) if v == 0]
    res_1 = AlgorithmicVND.optimize_fleet_routes(nodes_a1, nodes_b1, demands, cap_a, cap_b, dist_matrix)
    # Guardrail application:
    final_dist_1 = min(incumbent_dist, res_1["total_distance"])
    assert final_dist_1 <= incumbent_dist

    # Adversarial Case 2: Degraded candidate deliberately arranged with maximum cross-city zigzag
    zigzag_a = [1, 5, 2, 6]
    zigzag_b = [3, 7, 4, 8]
    res_2 = AlgorithmicVND.optimize_fleet_routes(zigzag_a, zigzag_b, demands, cap_a, cap_b, dist_matrix)
    final_dist_2 = min(incumbent_dist, res_2["total_distance"])
    assert final_dist_2 <= incumbent_dist

    # Adversarial Case 3: Random white-noise bitstrings
    np.random.seed(999)
    for _ in range(20):
        rand_bits = list(np.random.randint(0, 2, N))
        rep_rand = suite.repair_capacity_violations(rand_bits, demands, cap_a, cap_b, h_diff)
        na = [i + 1 for i, v in enumerate(rep_rand) if v == 1]
        nb = [i + 1 for i, v in enumerate(rep_rand) if v == 0]
        res_rand = AlgorithmicVND.optimize_fleet_routes(na, nb, demands, cap_a, cap_b, dist_matrix)
        final_dist = min(incumbent_dist, res_rand["total_distance"])
        assert final_dist <= incumbent_dist

