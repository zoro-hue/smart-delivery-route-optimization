"""
Unit and regression tests for ROUTE/IQ Route Identity and Comparative Diagnostics.
"""
import uuid
import pytest
from app.services.optimization.route_identity import (
    extract_directed_edges,
    extract_undirected_edges,
    extract_vehicle_allocations,
    compute_route_identity_diagnostics,
)


def test_extract_edges_directed_and_undirected():
    routes = [
        {"stops": [0, 1, 2, 0]},
        {"stops": [0, 3, 4, 0]},
    ]
    directed = extract_directed_edges(routes)
    assert directed == {(0, 1), (1, 2), (2, 0), (0, 3), (3, 4), (4, 0)}

    undirected = extract_undirected_edges(routes)
    assert undirected == {(0, 1), (1, 2), (0, 2), (0, 3), (3, 4), (0, 4)}


def test_extract_vehicle_allocations():
    routes = [
        {"stops": [0, 1, 2, 0]},
        {"stops": [0, 3, 4, 5, 0]},
    ]
    allocs = extract_vehicle_allocations(routes)
    assert allocs == [{1, 2}, {3, 4, 5}]


def test_diagnostics_supremacy_winner():
    res_coop = {
        "execution_id": str(uuid.uuid4()),
        "total_distance_km": 32.500,
        "is_supremacy_winner": True,
        "solution_origin": "SUPREMACY_IMPROVED",
        "routes": [{"stops": [0, 1, 3, 2, 0]}],
    }
    res_ort = {
        "execution_id": str(uuid.uuid4()),
        "total_distance_km": 34.160,
        "routes": [{"stops": [0, 1, 2, 3, 0]}],
    }
    diag = compute_route_identity_diagnostics(res_coop, res_ort)
    assert diag["relationship_code"] == "SUPREMACY_IMPROVED"
    assert diag["distance_delta_km"] == pytest.approx(1.660, abs=1e-3)
    assert diag["is_separate_memory_objects"] is True
    assert diag["execution_id_coop"] != diag["execution_id_ortools"]


def test_diagnostics_independent_alternative_optimum():
    res_coop = {
        "execution_id": str(uuid.uuid4()),
        "total_distance_km": 34.160,
        "is_supremacy_winner": False,
        "solution_origin": "INDEPENDENT_ALTERNATIVE_OPTIMUM",
        "routes": [{"stops": [0, 2, 1, 3, 0]}],
    }
    res_ort = {
        "execution_id": str(uuid.uuid4()),
        "total_distance_km": 34.160,
        "routes": [{"stops": [0, 1, 2, 3, 0]}],
    }
    diag = compute_route_identity_diagnostics(res_coop, res_ort)
    assert diag["relationship_code"] == "INDEPENDENT_ALTERNATIVE_OPTIMUM"
    assert diag["is_same_distance"] is True
    assert diag["is_identical_route"] is False
    assert diag["directed_edge_overlap_pct"] < 100.0


def test_diagnostics_independent_identical_convergence():
    res_coop = {
        "execution_id": str(uuid.uuid4()),
        "total_distance_km": 34.160,
        "is_supremacy_winner": False,
        "solution_origin": "INDEPENDENT_IDENTICAL_CONVERGENCE",
        "routes": [{"stops": [0, 1, 2, 3, 0]}],
    }
    res_ort = {
        "execution_id": str(uuid.uuid4()),
        "total_distance_km": 34.160,
        "routes": [{"stops": [0, 1, 2, 3, 0]}],
    }
    diag = compute_route_identity_diagnostics(res_coop, res_ort)
    assert diag["relationship_code"] == "INDEPENDENT_IDENTICAL_CONVERGENCE"
    assert diag["is_same_distance"] is True
    assert diag["is_identical_route"] is True
    assert diag["directed_edge_overlap_pct"] == 100.0


def test_diagnostics_proven_optimal_incumbent_retained():
    res_coop = {
        "execution_id": str(uuid.uuid4()),
        "total_distance_km": 34.160,
        "is_supremacy_winner": False,
        "solution_origin": "INHERITED_INCUMBENT_BASELINE",
        "routes": [{"stops": [0, 1, 2, 3, 0]}],
    }
    res_ort = {
        "execution_id": str(uuid.uuid4()),
        "total_distance_km": 34.160,
        "routes": [{"stops": [0, 1, 2, 3, 0]}],
    }
    diag = compute_route_identity_diagnostics(res_coop, res_ort)
    assert diag["relationship_code"] == "PROVEN_OPTIMAL_INCUMBENT_RETAINED"
    assert "Proposition 1 Guardrail" in diag["explanation"]
