"""
Unit and Integration Tests for Quantum-Guided Adaptive Reconstruction (QGAR) Pipeline.
"""

import pytest
import numpy as np
from app.services.optimization.qgar_pipeline import (
    count_tour_crossings,
    QuantumCandidateEvaluator,
    AdaptiveQuantumInfluenceModel,
    QuantumGuidedAdaptiveRouter
)
from app.services.bigdata_pipeline import ensure_spark_environment

def test_tour_crossings_detection():
    # Square: (0,0) -> (1,0) -> (1,1) -> (0,1) -> (0,0) has 0 crossings
    convex_square = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
    assert count_tour_crossings(convex_square) == 0

    # Self-intersecting figure-8: (0,0) -> (1,1) -> (1,0) -> (0,1) -> (0,0) has 1 crossing
    fig_8 = [(0.0, 0.0), (1.0, 1.0), (1.0, 0.0), (0.0, 1.0)]
    assert count_tour_crossings(fig_8) == 1


def test_quality_aware_candidate_selection():
    # 3 customers + depot
    customers = [
        {"id": "c1", "latitude": 40.75, "longitude": -73.98},
        {"id": "c2", "latitude": 40.76, "longitude": -73.97},
        {"id": "c3", "latitude": 40.77, "longitude": -73.96}
    ]
    depot = {"id": "depot", "latitude": 40.74, "longitude": -73.99}
    loc_map = {"depot": 0, "c1": 1, "c2": 2, "c3": 3}

    # Asymmetric distance matrix
    matrix = np.array([
        [0.0, 2.0, 5.0, 8.0],
        [2.5, 0.0, 2.0, 6.0],
        [5.5, 2.5, 0.0, 2.0],
        [8.5, 6.5, 2.5, 0.0]
    ])

    # Provide two measurement bitstrings:
    # 1. Higher frequency but sub-optimal tour (c3 -> c2 -> c1)
    # 2. Lower frequency but optimal tour (c1 -> c2 -> c3)
    # 9-qubit representation:
    # c1 at t=0, c2 at t=1, c3 at t=2:
    # c1: 100, c2: 010, c3: 001 -> "100010001"
    # c3 at t=0, c2 at t=1, c1 at t=2:
    # c1: 001, c2: 010, c3: 100 -> "001010100"
    raw_counts = {
        "001010100": 600,  # Worse tour (higher probability)
        "100010001": 400   # Better tour (lower probability)
    }

    eval_res = QuantumCandidateEvaluator.evaluate_all_candidates(
        raw_counts, customers, depot, matrix, loc_map, depot_idx=0
    )

    best_cand = eval_res["best_candidate"]
    # Verify quality-aware selection picked the lower cost tour (c1 -> c2 -> c3)
    assert best_cand["ordered_stops"][0]["id"] == "c1"
    assert best_cand["ordered_stops"][1]["id"] == "c2"
    assert best_cand["ordered_stops"][2]["id"] == "c3"
    assert eval_res["candidates_evaluated"] == 2


def test_adaptive_quantum_influence_model():
    customers = [
        {"id": "c1", "latitude": 40.75, "longitude": -73.98},
        {"id": "c2", "latitude": 40.76, "longitude": -73.97},
        {"id": "c3", "latitude": 40.77, "longitude": -73.96}
    ]
    depot = {"id": "depot", "latitude": 40.74, "longitude": -73.99}
    loc_map = {"depot": 0, "c1": 1, "c2": 2, "c3": 3}

    matrix = np.array([
        [0.0, 2.0, 5.0, 8.0],
        [2.5, 0.0, 2.0, 6.0],
        [5.5, 2.5, 0.0, 2.0],
        [8.5, 6.5, 2.5, 0.0]
    ])

    # Scenario 1: QAOA candidate is strictly worse than spatial order
    worse_candidate = {
        "ordered_stops": [customers[2], customers[0], customers[1]],
        "directed_cost_km": 25.0,
        "crossings": 2
    }
    inf_res1 = AdaptiveQuantumInfluenceModel.compute_quantum_influence(
        worse_candidate, customers, depot, matrix, loc_map, depot_idx=0
    )
    # Must fallback to spatial order
    assert inf_res1["adopted_source"] == "SPATIAL_SWEEP"
    assert inf_res1["lambda_eff"] < 0.50

    # Scenario 2: QAOA candidate is strictly better than spatial order
    better_candidate = {
        "ordered_stops": [customers[0], customers[1], customers[2]],
        "directed_cost_km": 10.0,
        "crossings": 0
    }
    inf_res2 = AdaptiveQuantumInfluenceModel.compute_quantum_influence(
        better_candidate, [customers[2], customers[1], customers[0]], depot, matrix, loc_map, depot_idx=0
    )
    # Must adopt QAOA
    assert inf_res2["adopted_source"] == "QAOA"
    assert inf_res2["lambda_eff"] >= 0.50


def test_qgar_router_end_to_end_preservation():
    ensure_spark_environment()
    router = QuantumGuidedAdaptiveRouter(qaoa_p=1, qaoa_shots=256, use_spark=False)

    depot = {"id": "depot", "latitude": 40.7580, "longitude": -73.9855, "demand": 0}
    customers = [
        {"id": f"c_{i+1}", "latitude": 40.750 + i * 0.005, "longitude": -73.980 + i * 0.003, "demand": 2}
        for i in range(10)
    ]
    loc_map = {"depot": 0}
    for i, c in enumerate(customers):
        loc_map[c["id"]] = i + 1

    # Simple Euclidean distance matrix for sanity
    n_nodes = 11
    matrix = np.zeros((n_nodes, n_nodes))
    nodes = [depot] + customers
    for i in range(n_nodes):
        for j in range(n_nodes):
            if i != j:
                dx = nodes[i]["latitude"] - nodes[j]["latitude"]
                dy = nodes[i]["longitude"] - nodes[j]["longitude"]
                matrix[i, j] = np.sqrt(dx*dx + dy*dy) * 111.0  # approximate km

    res = router.optimize_delivery_campaign(
        customers=customers,
        depot=depot,
        distance_matrix=matrix,
        vehicle_capacity=15.0,
        location_indices=loc_map,
        enable_qaoa=True,
        enable_adaptive_influence=True,
        enable_quality_selection=True
    )

    feas = res["feasibility"]
    tele = res["telemetry"]

    # Invariants
    assert feas["is_feasible"] is True
    assert feas["total_routed_customers"] == 10
    assert feas["unassigned_customers"] == 0
    assert feas["capacity_violations"] == 0
    assert tele["qaoa_subproblems_solved"] > 0
    assert tele["quantum_influence_lambda_mean"] >= 0.0


def test_end_to_end_non_degradation_certification():
    """Verifies that Cost(QGAR) <= Cost(SpatialBaseline) is strictly certified."""
    ensure_spark_environment()
    router = QuantumGuidedAdaptiveRouter(qaoa_p=1, qaoa_shots=256, use_spark=False)

    depot = {"id": "depot", "latitude": 40.7580, "longitude": -73.9855, "demand": 0}
    customers = [
        {"id": f"c_{i+1}", "latitude": 40.750 + (i % 4) * 0.006, "longitude": -73.980 + (i // 4) * 0.005, "demand": 3}
        for i in range(12)
    ]
    loc_map = {"depot": 0}
    for i, c in enumerate(customers):
        loc_map[c["id"]] = i + 1

    n_nodes = 13
    matrix = np.zeros((n_nodes, n_nodes))
    nodes = [depot] + customers
    for i in range(n_nodes):
        for j in range(n_nodes):
            if i != j:
                dx = nodes[i]["latitude"] - nodes[j]["latitude"]
                dy = nodes[i]["longitude"] - nodes[j]["longitude"]
                matrix[i, j] = np.sqrt(dx*dx + dy*dy) * 111.0

    res_spatial = router.optimize_delivery_campaign(
        customers=customers,
        depot=depot,
        distance_matrix=matrix,
        vehicle_capacity=15.0,
        location_indices=loc_map,
        enable_qaoa=False
    )

    res_qgar = router.optimize_delivery_campaign(
        customers=customers,
        depot=depot,
        distance_matrix=matrix,
        vehicle_capacity=15.0,
        location_indices=loc_map,
        enable_qaoa=True,
        enable_adaptive_influence=True,
        enable_quality_selection=True
    )

    # Formal Monotonic Non-Degradation Verification
    assert res_qgar["total_distance_km"] <= res_spatial["total_distance_km"] + 1e-4


