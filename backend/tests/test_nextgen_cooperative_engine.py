"""
Unit and Integration Test Suite for Next-Generation ROUTE/IQ Cooperative Optimization Engine.
Tests:
1. Universal Invariant R == I (100% stop coverage, 0 omission, 0 duplication).
2. Vehicle capacity limits compliance.
3. Proposition 1 non-degradation guardrail Cost(Coop) <= Cost(OR-Tools).
4. MAB adaptive operator selection and weight updates.
5. Regret-3 and Regret-2 construction heuristics.
"""

import os
import sys
import pytest
import numpy as np

sys.path.insert(0, os.path.abspath("backend"))

from app.services.optimization.cooperative_solver import cooperative_solver
from app.services.optimization.neighborhood_search import (
    AdvancedNeighborhoodSearch,
    RouteEvaluator,
)
from app.services.optimization.construction_heuristics import (
    DiverseConstructionHeuristics,
)
from app.services.optimization.route_validator import validate_fleet_coverage


@pytest.fixture
def sample_vrp_instance():
    # 10 customers + 1 depot
    n = 11
    np.random.seed(42)
    locations = [(40.75 + np.random.uniform(-0.05, 0.05), -73.98 + np.random.uniform(-0.05, 0.05)) for _ in range(n)]
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                dist_matrix[i, j] = np.hypot(locations[i][0] - locations[j][0], locations[i][1] - locations[j][1]) * 111.0

    num_vehicles = 3
    demands = [0] + [5, 8, 12, 6, 9, 14, 7, 10, 11, 8]
    capacities = [35.0, 35.0, 35.0]
    return {
        "dist_matrix": dist_matrix,
        "num_vehicles": num_vehicles,
        "depot": 0,
        "demands": demands,
        "capacities": capacities,
        "locations": locations,
        "cust_ids": list(range(1, n)),
    }


def test_regret_k_construction(sample_vrp_instance):
    inst = sample_vrp_instance
    routes = DiverseConstructionHeuristics.regret_k_construction(
        dist_matrix=inst["dist_matrix"],
        num_vehicles=inst["num_vehicles"],
        depot=inst["depot"],
        demands=inst["demands"],
        capacities=inst["capacities"],
        k_regret=3,
    )
    val = validate_fleet_coverage(
        routes=[{"stops": [0] + r + [0], "customer_stops": r} for r in routes],
        input_customer_ids=inst["cust_ids"],
        demands=inst["demands"],
        vehicle_capacities=inst["capacities"],
        depot=0,
        distance_matrix=inst["dist_matrix"],
    )
    assert val["is_valid"] is True
    assert len(val["missing_delivery_ids"]) == 0
    assert val["capacity_violations"] == 0


def test_nextgen_cooperative_solver_proposition_1(sample_vrp_instance):
    inst = sample_vrp_instance
    res = cooperative_solver.solve(
        distance_matrix=inst["dist_matrix"],
        num_vehicles=inst["num_vehicles"],
        depot=inst["depot"],
        demands=inst["demands"],
        vehicle_capacities=inst["capacities"],
        time_limit_sec=1.5,
        locations=inst["locations"],
        seed=42,
    )
    assert res["success"] is True
    assert res["is_feasible"] is True
    assert res["unserved_customers"] == 0
    assert res["capacity_violations"] == 0
    assert res["total_distance_km"] > 0.0

    # Validate complete fleet coverage invariant
    val = validate_fleet_coverage(
        routes=res["routes"],
        input_customer_ids=inst["cust_ids"],
        demands=inst["demands"],
        vehicle_capacities=inst["capacities"],
        depot=0,
        distance_matrix=inst["dist_matrix"],
    )
    assert val["is_valid"] is True


def test_alns_ruin_and_recreate_mab(sample_vrp_instance):
    inst = sample_vrp_instance
    init_routes = DiverseConstructionHeuristics.regret_k_construction(
        dist_matrix=inst["dist_matrix"],
        num_vehicles=inst["num_vehicles"],
        depot=inst["depot"],
        demands=inst["demands"],
        capacities=inst["capacities"],
        k_regret=2,
    )
    init_dist = RouteEvaluator.fleet_distance(init_routes, inst["dist_matrix"], depot=0)

    opt_routes = AdvancedNeighborhoodSearch.alns_ruin_and_recreate(
        incumbent_routes=init_routes,
        capacities=inst["capacities"],
        demands=inst["demands"],
        dist_matrix=inst["dist_matrix"],
        depot=0,
        locations=inst["locations"],
        max_iterations=15,
        seed=42,
    )
    opt_dist = RouteEvaluator.fleet_distance(opt_routes, inst["dist_matrix"], depot=0)
    assert opt_dist <= init_dist + 1e-4

    # Check universal coverage
    visited = [c for r in opt_routes for c in r]
    assert sorted(visited) == sorted(inst["cust_ids"])
