"""
PHASE AE: Backend Integration and Mathematical Guarantee Tests.
Verifies:
1. ROUTE/IQ Cooperative Optimization Solver direct execution.
2. Proposition 1 Non-Degradation Guardrail enforcement.
3. Capacity feasibility and customer coverage invariants.
4. FastAPI endpoints (/api/optimization/algorithms and /api/optimization/run).
5. Independent execution of all 5 classical and 2 quantum baselines.
"""

import os
import sys

sys.path.insert(0, os.path.abspath("backend"))
sys.path.insert(0, os.path.abspath("."))

import pytest
import numpy as np
import httpx
from fastapi.testclient import TestClient

from app.main import app
from app.services.optimization.cooperative_solver import cooperative_solver
from app.services.optimization.classical_solver import classical_solver
from app.services.optimization.quantum_solver import quantum_solver
from app.services.optimization.qiga_solver import qiga_solver


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
def sample_problem():
    """Generates a reproducible 10-node CVRP distance matrix and demands."""
    np.random.seed(42)
    n = 10
    coords = np.random.uniform(10.0, 50.0, size=(n, 2))
    coords[0] = [30.0, 30.0]  # Depot at center

    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                dist_matrix[i, j] = float(np.linalg.norm(coords[i] - coords[j]))

    demands = [0] + [5] * (n - 1)
    capacities = [30, 30, 30]
    return {
        "n": n,
        "dist_matrix": dist_matrix,
        "demands": demands,
        "capacities": capacities,
        "num_vehicles": 3,
        "coords": coords,
    }


def test_cooperative_solver_direct(sample_problem):
    """Test that cooperative_solver executes and produces valid, feasible CVRP routes."""
    res = cooperative_solver.solve(
        distance_matrix=sample_problem["dist_matrix"],
        num_vehicles=sample_problem["num_vehicles"],
        depot=0,
        demands=sample_problem["demands"],
        vehicle_capacities=sample_problem["capacities"],
        seed=42,
    )

    assert res["success"] is True
    assert res["algorithm"] == "routeiq_cooperative"
    assert res["category"] == "cooperative"
    assert "routes" in res
    assert len(res["routes"]) <= sample_problem["num_vehicles"]
    assert res["is_feasible"] is True
    assert res["capacity_violations"] == 0
    assert res["unserved_customers"] == 0
    assert res["total_distance_km"] > 0

    # Verify Proposition 1 Non-Degradation Guardrail
    telemetry = res["cooperative_telemetry"]
    assert telemetry["proposition1_guaranteed"] is True
    assert res["total_distance_km"] <= telemetry["initial_incumbent_distance_km"] + 1e-4

    # Verify customer coverage
    all_served = []
    for r in res["routes"]:
        all_served.extend(r.get("customer_stops", []))
    assert set(all_served) == set(range(1, sample_problem["n"]))


def test_cooperative_solver_single_vehicle():
    """Edge case: Single vehicle handling a small subproblem."""
    dist_matrix = np.array([
        [0.0, 5.0, 7.0, 4.0],
        [5.0, 0.0, 3.0, 6.0],
        [7.0, 3.0, 0.0, 5.0],
        [4.0, 6.0, 5.0, 0.0],
    ])
    demands = [0, 5, 5, 5]
    capacities = [20]

    res = cooperative_solver.solve(
        distance_matrix=dist_matrix,
        num_vehicles=1,
        depot=0,
        demands=demands,
        vehicle_capacities=capacities,
        seed=100,
    )

    assert res["success"] is True
    assert res["is_feasible"] is True
    assert len(res["routes"]) == 1
    assert set(res["routes"][0]["customer_stops"]) == {1, 2, 3}


def test_api_get_algorithms(test_client):
    """Verify GET /api/optimization/algorithms returns all algorithms including cooperative."""
    response = test_client.get("/api/optimization/algorithms")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

    algo_ids = [a["id"] for a in data["algorithms"]]
    assert "routeiq_cooperative" in algo_ids
    assert "ortools" in algo_ids
    assert "clarke_wright" in algo_ids
    assert "two_opt" in algo_ids
    assert "dijkstra" in algo_ids
    assert "astar" in algo_ids
    assert "qaoa" in algo_ids
    assert "qiga" in algo_ids
    assert len(algo_ids) >= 8


def test_api_run_cooperative_endpoint(test_client):
    """Verify POST /api/optimization/run with routeiq_cooperative produces complete response."""
    payload = {
        "selection_mode": "custom",
        "selected_algorithms": ["routeiq_cooperative"],
        "num_customers": 6,
        "num_vehicles": 2,
        "vehicle_capacity": 50,
        "depot_lat": 40.7580,
        "depot_lon": -73.8292,
        "random_seed": 42,
    }

    response = test_client.post("/api/optimization/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("completed", "success")
    assert "routeiq_cooperative" in data["results"]

    coop_res = data["results"]["routeiq_cooperative"]
    assert coop_res["success"] is True
    assert coop_res["is_feasible"] is True
    assert len(coop_res["routes"]) >= 1
    assert coop_res["total_distance_km"] > 0
    assert "cooperative_telemetry" in coop_res


def test_independent_baselines_remain_operational(test_client):
    """Verify all 5 classical and 2 quantum baselines still execute independently without regressions."""
    algorithms_to_test = [
        "ortools",
        "clarke_wright",
        "two_opt",
        "dijkstra",
        "astar",
        "qiga",
        "qaoa",
    ]

    payload = {
        "selection_mode": "custom",
        "selected_algorithms": algorithms_to_test,
        "num_customers": 5,
        "num_vehicles": 2,
        "vehicle_capacity": 50,
        "depot_lat": 40.7580,
        "depot_lon": -73.8292,
        "random_seed": 42,
    }

    response = test_client.post("/api/optimization/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("completed", "success")

    for algo in algorithms_to_test:
        assert algo in data["results"], f"Missing algorithm result for {algo}"
        res = data["results"][algo]
        assert res["success"] is True, f"Algorithm {algo} failed: {res.get('error')}"
        assert res["total_distance_km"] > 0, f"Algorithm {algo} returned invalid distance"
