"""
Phase AN Verification & Adversarial Audit Test Suite:
1. Adversarial Excess Routes & Capacity-Aware Insertion:
   Verify that excess routes (> num_vehicles) do not blindly violate vehicle capacity.
2. Adversarial Unreachable Node & Edge Reachability:
   Verify that nodes or edges with infinite distance yield PARTIAL or INFEASIBLE status.
3. Adversarial Fleet Overload:
   Verify that total demand > fleet capacity yields explicit PENALIZED status (never FEASIBLE).
4. Quantum Terminology Scientific Candor Audit:
   Verify that no algorithm claims physical QPU execution or hardware execution;
   all quantum routines explicitly state classical CPU / statevector simulation.
5. Canonical 11-Algorithm Registry Integrity.
"""

import math
import pytest
import numpy as np
from typing import List, Dict, Any

from app.api.routes.optimization import AVAILABLE_ALGORITHMS
from app.services.optimization.route_validator import (
    validate_fleet_coverage,
    repair_fleet_coverage,
)


def test_adversarial_excess_routes_capacity_preservation():
    """
    Adversarial scenario:
    The solver generates 4 routes for a 2-vehicle fleet.
    Vehicle 1 has load 25 (capacity 50, remaining 25).
    Vehicle 2 has load 45 (capacity 50, remaining 5).
    Excess route 3 has customer 3 (demand 18).
    Excess route 4 has customer 4 (demand 4).

    Blind insertion would append customer 3 to Vehicle 2 (overloading it to 63 > 50).
    Capacity-aware insertion must place customer 3 into Vehicle 1 (25 + 18 = 43 <= 50)
    and customer 4 into Vehicle 2 (45 + 4 = 49 <= 50) or Vehicle 1 (43 + 4 = 47 <= 50).
    Resulting fleet must have len == 2, 0 capacity violations, and 100% stop coverage.
    """
    n = 5  # Depot (0) + 4 customers (1, 2, 3, 4)
    dist_mat = np.ones((n, n), dtype=float) * 2.0
    np.fill_diagonal(dist_mat, 0.0)

    demands = [0.0, 25.0, 45.0, 18.0, 4.0]
    caps = [50.0, 50.0]
    num_vehicles = 2
    input_cust_ids = [1, 2, 3, 4]

    raw_routes = [
        {"vehicle_id": 1, "stops": [0, 1, 0]},
        {"vehicle_id": 2, "stops": [0, 2, 0]},
        {"vehicle_id": 3, "stops": [0, 3, 0]},  # excess route
        {"vehicle_id": 4, "stops": [0, 4, 0]},  # excess route
    ]

    repaired_routes, val_report = repair_fleet_coverage(
        raw_routes,
        input_cust_ids,
        dist_mat,
        demands,
        caps,
        num_vehicles,
        depot=0,
    )

    assert len(repaired_routes) == num_vehicles, f"Expected {num_vehicles} routes, got {len(repaired_routes)}"
    assert val_report["is_complete"] is True, "All 4 customers must be served"
    assert val_report["capacity_violations"] == 0, f"Unexpected capacity violation: {val_report}"
    assert val_report["is_valid"] is True
    assert val_report["status"] == "FEASIBLE"

    for r in repaired_routes:
        assert r["load"] <= 50.0, f"Route {r['vehicle_id']} overloaded: {r['load']} > 50.0"


def test_adversarial_unreachable_node_produces_partial_status():
    """
    Adversarial scenario:
    Customer 3 is completely disconnected on the directed road network (infinite distance from all nodes).
    Repair cannot safely connect customer 3, so customer 3 remains unserved.
    validate_fleet_coverage must report is_complete=False, is_valid=False, status='PARTIAL'.
    """
    n = 4  # Depot 0, Customers 1, 2, 3
    dist_mat = np.ones((n, n), dtype=float) * 5.0
    np.fill_diagonal(dist_mat, 0.0)

    # Make customer 3 unreachable from any node
    dist_mat[:, 3] = float("inf")
    dist_mat[3, :] = float("inf")
    np.fill_diagonal(dist_mat, 0.0)

    demands = [0.0, 10.0, 10.0, 10.0]
    caps = [50.0, 50.0]
    num_vehicles = 2
    input_cust_ids = [1, 2, 3]

    raw_routes = [
        {"vehicle_id": 1, "stops": [0, 1, 0]},
        {"vehicle_id": 2, "stops": [0, 2, 0]},
    ]

    repaired_routes, val_report = repair_fleet_coverage(
        raw_routes,
        input_cust_ids,
        dist_mat,
        demands,
        caps,
        num_vehicles,
        depot=0,
    )

    assert 3 in val_report["missing_delivery_ids"], "Unreachable customer 3 must be detected as missing"
    assert val_report["is_complete"] is False
    assert val_report["is_valid"] is False
    assert val_report["status"] == "PARTIAL", f"Expected PARTIAL status, got {val_report['status']}"


def test_adversarial_unreachable_edge_in_route_produces_infeasible_status():
    """
    Adversarial scenario:
    A route contains an unreachable edge (u, v) where dist_mat[u, v] = inf.
    All customers are present, but the directed road traversal is invalid.
    validate_fleet_coverage must report is_valid=False, unreachable_edge_violations > 0, status='INFEASIBLE'.
    """
    n = 3
    dist_mat = np.ones((n, n), dtype=float) * 5.0
    dist_mat[1, 2] = float("inf")  # disconnected directed edge
    np.fill_diagonal(dist_mat, 0.0)

    demands = [0.0, 10.0, 10.0]
    caps = [50.0]
    input_cust_ids = [1, 2]

    # Route traverses 0 -> 1 -> 2 -> 0, which takes edge (1, 2) = inf
    routes = [
        {"vehicle_id": 1, "stops": [0, 1, 2, 0]}
    ]

    val_report = validate_fleet_coverage(
        routes,
        input_cust_ids,
        demands,
        caps,
        depot=0,
        distance_matrix=dist_mat,
    )

    assert val_report["is_complete"] is True
    assert val_report["unreachable_edge_violations"] >= 1
    assert val_report["is_valid"] is False
    assert val_report["status"] == "INFEASIBLE"


def test_adversarial_fleet_capacity_overload_produces_penalized_status():
    """
    Adversarial scenario:
    Customer demands total 120.0, but total fleet capacity is 100.0 (2 vehicles x 50.0).
    Every customer is covered, but capacity violations cannot be eliminated.
    validate_fleet_coverage must report capacity_violations > 0, is_valid=False, status='PENALIZED'.
    """
    n = 4
    dist_mat = np.ones((n, n), dtype=float) * 2.0
    np.fill_diagonal(dist_mat, 0.0)

    demands = [0.0, 40.0, 40.0, 40.0]  # total demand 120
    caps = [50.0, 50.0]  # total capacity 100
    num_vehicles = 2
    input_cust_ids = [1, 2, 3]

    raw_routes = [
        {"vehicle_id": 1, "stops": [0, 1, 0]},
        {"vehicle_id": 2, "stops": [0, 2, 0]},
    ]

    repaired_routes, val_report = repair_fleet_coverage(
        raw_routes,
        input_cust_ids,
        dist_mat,
        demands,
        caps,
        num_vehicles,
        depot=0,
    )

    assert val_report["is_complete"] is True
    assert val_report["capacity_violations"] >= 1
    assert val_report["is_valid"] is False
    assert val_report["status"] == "PENALIZED"


def test_adversarial_excess_vehicles_unresolvable_produces_infeasible_status():
    """
    Adversarial scenario:
    Validation of a route solution having more routes than vehicle capacities.
    Must flag vehicle_count_violations and set status to INFEASIBLE.
    """
    demands = [0.0, 10.0, 10.0, 10.0]
    caps = [50.0, 50.0]  # max 2 vehicles
    input_cust_ids = [1, 2, 3]

    routes = [
        {"vehicle_id": 1, "stops": [0, 1, 0]},
        {"vehicle_id": 2, "stops": [0, 2, 0]},
        {"vehicle_id": 3, "stops": [0, 3, 0]},  # 3 vehicles > 2 allowed
    ]

    val_report = validate_fleet_coverage(
        routes,
        input_cust_ids,
        demands,
        caps,
        depot=0,
    )

    assert val_report["vehicle_count_violations"] == 1
    assert val_report["is_valid"] is False
    assert val_report["status"] == "INFEASIBLE"


def test_quantum_terminology_scientific_candor_audit():
    """
    Audit all 11 registered algorithms in AVAILABLE_ALGORITHMS:
    1. Confirm NO algorithm references physical QPU hardware or implies physical quantum execution.
    2. Confirm QAOA states 'QAOA with Qiskit Aer/statevector CPU simulation'.
    3. Confirm QIGA states classically simulated Q-bits on classical CPU.
    4. Confirm Cooperative Engine explicitly describes Spark local preprocessing,
       classical optimization, and QAOA CPU simulation.
    """
    assert len(AVAILABLE_ALGORITHMS) == 11

    forbidden_hardware_terms = ["physical qpu", "quantum hardware", "ionq", "rigetti", "dwave", "simulated qpu"]

    for algo in AVAILABLE_ALGORITHMS:
        desc_lower = algo.get("description", "").lower()
        compute_lower = algo.get("compute_type", "").lower()
        cat_lower = algo.get("category_label", "").lower()

        # Check forbidden terms
        for term in forbidden_hardware_terms:
            assert term not in desc_lower, f"Algorithm '{algo['id']}' description contains forbidden term '{term}': {desc_lower}"
            assert term not in compute_lower, f"Algorithm '{algo['id']}' compute_type contains forbidden term '{term}': {compute_lower}"
            assert term not in cat_lower, f"Algorithm '{algo['id']}' category_label contains forbidden term '{term}': {cat_lower}"

    # Specific audits
    qaoa_entry = next(a for a in AVAILABLE_ALGORITHMS if a["id"] == "qaoa")
    assert "qaoa with qiskit aer/statevector cpu simulation" in qaoa_entry["compute_type"].lower()

    qiga_entry = next(a for a in AVAILABLE_ALGORITHMS if a["id"] == "qiga")
    assert "classical" in qiga_entry["compute_type"].lower()

    coop_entry = next(a for a in AVAILABLE_ALGORITHMS if a["id"] == "routeiq_cooperative")
    assert "spark local" in coop_entry["category_label"].lower()
    assert "qaoa cpu sim" in coop_entry["category_label"].lower()
    assert "qaoa statevector cpu simulation" in coop_entry["compute_type"].lower()
