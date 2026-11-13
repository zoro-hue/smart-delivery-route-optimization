"""
Unit tests for Phase T NextGen Bipartition Engine.
"""

import sys
import os
import pytest
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from phase_t_nextgen_hybrid_architecture.prototypes.proto_nextgen_bipartition_engine import (
    NextGenBipartitionEngine
)
from phase_p_autonomous_research.prototypes.common_evaluator import generate_benchmark_instance


def test_bipartition_qaoa_circuit_build():
    engine = NextGenBipartitionEngine(p=1, shots=128)
    N = 6
    J = np.random.uniform(0.1, 2.0, (N, N))
    h = np.random.uniform(-1.0, 1.0, N)

    qc, gammas, betas = engine.build_bipartition_qaoa_circuit(N, J, h)
    assert qc.num_qubits == N
    assert len(gammas) == 1
    assert len(betas) == 1


def test_solve_boundary_bipartition():
    engine = NextGenBipartitionEngine(p=1, shots=128)
    inst = generate_benchmark_instance(num_customers=10, num_vehicles=2, seed=42)

    custs = inst.customers[:6]
    res = engine.solve_boundary_bipartition_qaoa(
        boundary_customers=custs,
        dist_matrix=inst.distance_matrix,
        loc_indices=inst.location_indices,
        vehicle_a_centroid=(40.75, -73.98),
        vehicle_b_centroid=(40.78, -73.95)
    )

    assert len(res["partition"]) == 6
    assert all(b in [0, 1] for b in res["partition"])
    assert res["time_ms"] > 0


def test_full_routing_pipeline():
    engine = NextGenBipartitionEngine(p=1, shots=128)
    inst = generate_benchmark_instance(num_customers=10, num_vehicles=2, seed=42)

    res = engine.solve_full_routing(inst, use_quantum=True)
    assert res["is_feasible"] is True
    assert res["total_distance_km"] <= res["incumbent_cost_km"]

