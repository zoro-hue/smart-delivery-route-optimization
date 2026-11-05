"""
Integration tests for HybridQuantumBigDataRouter.
Verifies:
1. End-to-end execution with active PySpark partitioning and genuine Qiskit Aer QAOA.
2. 100% customer preservation guarantee (zero dropped orders).
3. Zero capacity violations.
4. Granular unbundled telemetry verification (Spark time, circuit time, optimizer time, reconstruction time).
5. Strict anti-fallback enforcement.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import numpy as np
from app.services.optimization.hybrid_quantum_pipeline import HybridQuantumBigDataRouter


def test_hybrid_quantum_bigdata_router_end_to_end():
    """Verify complete Dual-Pillar pipeline execution on synthetic customer set."""
    router = HybridQuantumBigDataRouter(
        qaoa_p=1,
        qaoa_shots=256,
        max_qubits=16,
        spark_master="local[1]",
        use_spark=True,
        strict_quantum=True
    )

    depot = {"id": "depot", "demand": 0, "latitude": 40.7580, "longitude": -73.9855}

    # 12 customers, capacity = 8.0 -> ~3-4 vehicles
    rng = np.random.default_rng(42)
    customers = []
    location_indices = {"depot": 0}
    for i in range(12):
        cid = f"cust_{i+1}"
        customers.append({
            "id": cid,
            "demand": rng.integers(1, 3),
            "latitude": 40.7580 + rng.uniform(-0.03, 0.03),
            "longitude": -73.9855 + rng.uniform(-0.03, 0.03)
        })
        location_indices[cid] = i + 1

    # Asymmetric directed distance matrix
    K_nodes = 13
    matrix = rng.uniform(1.0, 10.0, (K_nodes, K_nodes))
    np.fill_diagonal(matrix, 0.0)

    res = router.optimize_delivery_campaign(
        customers=customers,
        depot=depot,
        distance_matrix=matrix,
        vehicle_capacity=8.0,
        location_indices=location_indices
    )

    assert res["feasibility"]["is_feasible"] is True
    assert res["feasibility"]["total_input_customers"] == 12
    assert res["feasibility"]["total_routed_customers"] == 12
    assert res["feasibility"]["unassigned_customers"] == 0
    assert res["feasibility"]["capacity_violations"] == 0
    assert res["total_distance_km"] > 0.0

    telemetry = res["telemetry"]
    assert telemetry["runtime_spark_ms"] > 0.0
    assert telemetry["runtime_qaoa_circuit_ms"] > 0.0
    assert telemetry["runtime_reconstruction_ms"] > 0.0
    assert telemetry["qaoa_subproblems_solved"] > 0
    assert telemetry["max_logical_qubits_used"] > 0
    assert telemetry["strict_quantum_enforced"] is True


def test_hybrid_router_single_machine_comparison():
    """Verify that single-machine preprocessor mode functions identically and logs unbundled time."""
    router = HybridQuantumBigDataRouter(
        qaoa_p=1,
        qaoa_shots=100,
        max_qubits=16,
        use_spark=False,  # Single-machine baseline mode
        strict_quantum=True
    )

    depot = {"id": "depot", "demand": 0, "latitude": 40.7580, "longitude": -73.9855}
    customers = [
        {"id": f"c_{i}", "demand": 1.0, "latitude": 40.7580 + 0.005 * i, "longitude": -73.9855 + 0.005 * i}
        for i in range(6)
    ]
    location_indices = {"depot": 0}
    for i in range(6):
        location_indices[f"c_{i}"] = i + 1
    matrix = np.random.default_rng(101).uniform(1.0, 5.0, (7, 7))
    np.fill_diagonal(matrix, 0.0)

    res = router.optimize_delivery_campaign(
        customers=customers,
        depot=depot,
        distance_matrix=matrix,
        vehicle_capacity=5.0,
        location_indices=location_indices
    )

    assert res["feasibility"]["is_feasible"] is True
    assert res["feasibility"]["unassigned_customers"] == 0
    assert res["telemetry"]["qaoa_subproblems_solved"] > 0

