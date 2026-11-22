"""
Unit tests for Phase Y Advanced Quantum Formulations.
"""

import sys
import os
import numpy as np
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from phase_y_breakthrough_engineering.prototypes.advanced_quantum_formulations import (
    AdvancedQuantumFormulations
)

def test_calibrated_penalty():
    W = np.array([[0, 2.5], [2.5, 0]])
    demands = np.array([2, 3])
    penalty = AdvancedQuantumFormulations.calculate_calibrated_penalty(W, demands)
    assert penalty > 0.0
    assert penalty == 1.875

def test_asymmetric_ising_construction():
    dist_matrix = np.zeros((5, 5))
    dist_matrix[1, 2] = 10.0
    dist_matrix[2, 1] = 14.0  # asymmetric
    cust_indices = [1, 2, 3, 4]
    demands = np.array([2, 2, 3, 3])
    cap_a = 6.0
    cap_b = 6.0
    lambda_c = 1.5

    h, J, c0 = AdvancedQuantumFormulations.build_asymmetric_ising(
        dist_matrix, cust_indices, demands, cap_a, cap_b, lambda_c
    )
    assert len(h) == 4
    assert J.shape == (4, 4)
    assert np.allclose(J, J.T)  # J must be symmetric

def test_sampling_modes():
    h = np.array([0.5, -0.5, 1.0, -1.0])
    J = np.zeros((4, 4))
    demands = np.array([2, 2, 2, 2])
    cap_a = 5.0
    cap_b = 5.0

    # 1. Standard
    res_std = AdvancedQuantumFormulations.simulate_sampling_generic(h, J, demands, cap_a, cap_b, shots=100)
    assert len(res_std["best_x"]) == 4

    # 2. XY Mixer (fixed Hamming weight 2)
    res_xy = AdvancedQuantumFormulations.simulate_sampling_generic(h, J, demands, cap_a, cap_b, shots=100, use_xy_mixer=True)
    assert len(res_xy["best_x"]) == 4

    # 3. Warm-Start
    warm = np.array([1, 1, 0, 0])
    res_warm = AdvancedQuantumFormulations.simulate_sampling_generic(h, J, demands, cap_a, cap_b, shots=100, warm_seed=warm)
    assert len(res_warm["best_x"]) == 4

    # 4. Fast Mode
    res_fast = AdvancedQuantumFormulations.simulate_sampling_generic(h, J, demands, cap_a, cap_b, fast_mode=True)
    assert res_fast["time_ms"] < res_std["time_ms"]

