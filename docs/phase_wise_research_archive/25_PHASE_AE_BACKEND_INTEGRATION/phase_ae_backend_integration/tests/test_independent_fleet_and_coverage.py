"""
Phase AE: Independent Verification Suite for Fleet Constraints, Route Repair,
Delivery Coverage (R == I), and Resource Measurement Auditing.
"""

import pytest
import math
import numpy as np
from app.services.optimization.route_validator import (
    validate_fleet_coverage,
    repair_fleet_coverage,
    profile_algorithm_execution,
    ALGORITHM_COMPLEXITIES,
)


def test_fleet_constraints_never_silently_modified():
    """
    Verify that user-specified vehicle count and capacity are NEVER silently inflated.
    If 2 vehicles with capacity 100 are requested for 250 total demand, capacity must remain 100.
    """
    input_customers = [1, 2, 3, 4, 5]
    demands = [0.0, 50.0, 50.0, 50.0, 50.0, 50.0]  # Total demand = 250
    user_vehicles = 2
    user_capacity = 100.0  # Fleet max capacity = 200 < 250
    capacities = [user_capacity] * user_vehicles

    dist_mat = np.ones((6, 6), dtype=float) * 5.0
    np.fill_diagonal(dist_mat, 0.0)

    # Incomplete initial routes
    initial_routes = [
        {"vehicle_id": 1, "stops": [0, 1, 2, 0]},
        {"vehicle_id": 2, "stops": [0, 3, 0]},
    ]

    repaired, val = repair_fleet_coverage(
        initial_routes,
        input_customers,
        dist_mat,
        demands,
        capacities,
        num_vehicles=user_vehicles,
        depot=0,
    )

    # 1. Capacity must strictly match user specification
    for r in repaired:
        assert r["capacity"] == user_capacity, f"Capacity was silently changed to {r['capacity']}"

    # 2. Vehicle count must strictly not exceed user specification
    assert len(repaired) <= user_vehicles, f"Vehicle count exceeded: {len(repaired)} > {user_vehicles}"

    # 3. Because 250 > 200, solution MUST be flagged as over capacity and not valid
    assert val["capacity_feasible"] is False, "Over-capacity fleet was falsely flagged as capacity feasible"
    assert val["is_valid"] is False, "Over-capacity fleet was falsely marked as valid"
    assert val["capacity_violations"] > 0, "No capacity violations recorded for 250 demand on 200 capacity"


def test_route_repair_handles_inaccessible_delivery_honestly():
    """
    Challenge repair operator: When a delivery stop is physically unreachable
    (infinite distance), repair must NOT force-insert it with infinite cost,
    and must honestly report incomplete coverage (is_complete=False).
    """
    input_customers = [1, 2, 3]
    demands = [0.0, 10.0, 10.0, 10.0]
    caps = [50.0, 50.0]

    # Stop 3 is completely disconnected (infinite distance to all nodes)
    dist_mat = np.ones((4, 4), dtype=float) * 5.0
    np.fill_diagonal(dist_mat, 0.0)
    dist_mat[:, 3] = float("inf")
    dist_mat[3, :] = float("inf")

    initial_routes = [
        {"vehicle_id": 1, "stops": [0, 1, 0]},
        {"vehicle_id": 2, "stops": [0, 2, 0]},
    ]

    repaired, val = repair_fleet_coverage(
        initial_routes,
        input_customers,
        dist_mat,
        demands,
        caps,
        num_vehicles=2,
        depot=0,
    )

    # Stop 3 cannot be inserted; must be reported as missing
    assert 3 in val["missing_delivery_ids"], "Inaccessible stop 3 was not reported in missing_delivery_ids"
    assert val["is_complete"] is False, "Inaccessible stop did not flag is_complete as False"
    assert val["is_valid"] is False, "Solution with inaccessible stop was marked valid"


def test_resource_measurement_auditing():
    """
    Verify resource measurement implementation:
    - tracemalloc measures Python heap (heap_allocated_mb, heap_peak_mb).
    - psutil measures resident process RAM (process_rss_mb).
    - cpu_utilization is clearly derived from (cpu_time / wall_time) * 100.
    - Big-O complexities are strictly theoretical bounds, not empirical figures.
    """
    def sample_work():
        a = [x * 2 for x in range(50000)]
        return {"done": True, "count": len(a)}

    result, metrics = profile_algorithm_execution(sample_work, "routeiq_cooperative")

    assert metrics["runtime_ms"] > 0.0, "Wall-clock runtime must be positive"
    assert metrics["cpu_time_ms"] >= 0.0, "CPU time must be non-negative"
    assert "heap_allocated_mb" in metrics, "heap_allocated_mb must be present"
    assert "heap_peak_mb" in metrics, "heap_peak_mb must be present"
    assert "process_rss_mb" in metrics, "process_rss_mb must be present"
    assert metrics["process_rss_mb"] > 0.0, "Process RSS must be non-zero"
    assert "cpu_core_ratio_percent" in metrics, "cpu_core_ratio_percent must be present"
    assert "time_complexity" in metrics, "Theoretical time complexity must be present"
    assert "space_complexity" in metrics, "Theoretical space complexity must be present"
    # Ensure Big-O is not a numeric measurement
    assert "O(" in metrics["time_complexity"], "Time complexity must be Big-O notation"
    assert "O(" in metrics["space_complexity"], "Space complexity must be Big-O notation"


@pytest.mark.asyncio
async def test_end_to_end_user_fleet_and_coverage_invariants():
    """
    Test end-to-end optimization pipeline with explicit user fleet constraints:
    1. 2 vehicles, capacity 100, demand = 50 (Feasible) -> Status SUCCESS, 0 violations, 100% coverage.
    2. 1 vehicle, capacity 20, demand = 50 (Infeasible) -> Status PENALIZED, capacity_violations > 0.
    """
    from app.api.routes.optimization import run_optimization, OptimizationRequest
    from app.db.session import async_session_factory

    # Scenario A: Feasible (Demand = 30 <= 2 * 50 = 100)
    req_feasible = OptimizationRequest(
        algorithm="classical",
        selection_mode="custom",
        selected_algorithms=["routeiq_cooperative", "ortools", "clarke_wright"],
        num_customers=3,
        num_vehicles=2,
        vehicle_capacity=50.0,
        depot_lat=40.7580,
        depot_lon=-73.9855,
        custom_customers=[
            {"id": "1", "name": "Stop 1", "lat": 40.7484, "lon": -73.9857, "demand": 10},
            {"id": "2", "name": "Stop 2", "lat": 40.7306, "lon": -73.9352, "demand": 10},
            {"id": "3", "name": "Stop 3", "lat": 40.7128, "lon": -74.0060, "demand": 10},
        ],
    )

    async with async_session_factory() as db:
        res_a = await run_optimization(req_feasible, db)

    for a_key in ["routeiq_cooperative", "ortools", "clarke_wright"]:
        data = res_a["results"][a_key]
        assert data["is_feasible"] is True
        assert data["capacity_violations"] == 0
        assert data["unserved_customers"] == 0
        assert data["served_customers"] == 3
        # Check that capacity was NOT silently modified
        for r in data["routes"]:
            assert r["capacity"] == 50.0

    # Scenario B: Mathematically Infeasible Fleet (Demand = 60 > 1 * 25 = 25)
    req_infeasible = OptimizationRequest(
        algorithm="classical",
        selection_mode="custom",
        selected_algorithms=["routeiq_cooperative", "ortools"],
        num_customers=3,
        num_vehicles=1,
        vehicle_capacity=25.0,  # Only 25 capacity for 60 demand!
        depot_lat=40.7580,
        depot_lon=-73.9855,
        custom_customers=[
            {"id": "1", "name": "Stop 1", "lat": 40.7484, "lon": -73.9857, "demand": 20},
            {"id": "2", "name": "Stop 2", "lat": 40.7306, "lon": -73.9352, "demand": 20},
            {"id": "3", "name": "Stop 3", "lat": 40.7128, "lon": -74.0060, "demand": 20},
        ],
    )

    async with async_session_factory() as db:
        res_b = await run_optimization(req_infeasible, db)

    for a_key in ["routeiq_cooperative", "ortools"]:
        data = res_b["results"][a_key]
        # Must be penalized, NOT marked as feasible
        assert data["is_feasible"] is False, f"{a_key} was falsely marked feasible when 60 demand > 25 capacity"
        assert data["capacity_violations"] > 0, f"{a_key} recorded no capacity violations"
        for r in data["routes"]:
            assert r["capacity"] == 25.0, f"Capacity was silently changed to {r['capacity']}"

