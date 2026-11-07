"""
Unit and integration test suite for Universal Stop Coverage (R == I),
Dynamic Fleet Consistency, Resource Profiling, and Invariant Verification.
"""

import pytest
import numpy as np
from app.services.optimization.route_validator import (
    validate_fleet_coverage,
    repair_fleet_coverage,
    profile_algorithm_execution,
    ALGORITHM_COMPLEXITIES,
)


def test_universal_coverage_invariant_validator():
    """Verify validate_fleet_coverage detects missing, duplicate, and unknown stops."""
    input_customers = [1, 2, 3, 4, 5]
    demands = [0.0, 10.0, 10.0, 10.0, 10.0, 10.0]
    caps = [30.0, 30.0]

    # Partial route missing stops 4 and 5
    partial_routes = [
        {"vehicle_id": 1, "stops": [0, 1, 2, 0]},
        {"vehicle_id": 2, "stops": [0, 3, 0]},
    ]
    report = validate_fleet_coverage(partial_routes, input_customers, demands, caps)
    assert not report["is_complete"]
    assert report["missing_delivery_ids"] == [4, 5]
    assert report["visited_delivery_count"] == 3

    # Complete route
    complete_routes = [
        {"vehicle_id": 1, "stops": [0, 1, 2, 4, 0]},
        {"vehicle_id": 2, "stops": [0, 3, 5, 0]},
    ]
    report2 = validate_fleet_coverage(complete_routes, input_customers, demands, caps)
    assert report2["is_complete"]
    assert report2["missing_delivery_ids"] == []
    assert report2["visited_delivery_count"] == 5
    assert report2["is_valid"]


def test_deterministic_repair_guarantees_coverage():
    """Verify repair_fleet_coverage deterministically restores 100% stop coverage."""
    input_customers = [1, 2, 3, 4, 5, 6]
    demands = [0.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0]
    caps = [20.0, 20.0]

    # Synthetic distance matrix
    dist_mat = np.ones((7, 7), dtype=float) * 10.0
    np.fill_diagonal(dist_mat, 0.0)

    # Incomplete initial routes (only stops 1 and 2 visited)
    incomplete_routes = [
        {"vehicle_id": 1, "stops": [0, 1, 0], "distance_km": 20.0},
        {"vehicle_id": 2, "stops": [0, 2, 0], "distance_km": 20.0},
    ]

    repaired, report = repair_fleet_coverage(
        incomplete_routes,
        input_customers,
        dist_mat,
        demands,
        caps,
        num_vehicles=2,
        depot=0,
    )

    assert report["is_complete"]
    assert report["visited_delivery_count"] == 6
    assert len(report["missing_delivery_ids"]) == 0
    all_stops = []
    for r in repaired:
        all_stops.extend([s for s in r["stops"] if s != 0])
    assert sorted(all_stops) == input_customers


def test_resource_profiling_measurement():
    """Verify tracemalloc and CPU process timers produce realistic measurements."""
    def dummy_solver():
        # Allocate some memory and do CPU work
        data = [i ** 2 for i in range(100000)]
        return {"status": "SUCCESS", "data_len": len(data)}

    result, metrics = profile_algorithm_execution(dummy_solver, "routeiq_cooperative")
    assert result["status"] == "SUCCESS"
    assert metrics["runtime_ms"] > 0.0
    assert metrics["cpu_time_ms"] >= 0.0
    assert metrics["memory_used_mb"] >= 0.0
    assert metrics["peak_memory_mb"] > 0.0
    assert "time_complexity" in metrics
    assert "space_complexity" in metrics
    assert metrics["measurement_available"] is True


@pytest.mark.asyncio
async def test_end_to_end_coverage_all_solvers():
    """Verify POST /api/optimization/run enforces R == I across all solvers."""
    from app.api.routes.optimization import run_optimization, OptimizationRequest
    from app.db.session import async_session_factory

    req = OptimizationRequest(
        algorithm="classical",
        selection_mode="compare",
        selected_algorithms=["routeiq_cooperative", "ortools", "clarke_wright", "two_opt", "qiga"],
        num_customers=5,
        num_vehicles=2,
        vehicle_capacity=50,
        depot_lat=40.7580,
        depot_lon=-73.9855,
        custom_customers=[
            {"id": "1", "name": "Stop 1", "lat": 40.7484, "lon": -73.9857, "demand": 10},
            {"id": "2", "name": "Stop 2", "lat": 40.7306, "lon": -73.9352, "demand": 10},
            {"id": "3", "name": "Stop 3", "lat": 40.7128, "lon": -74.0060, "demand": 10},
            {"id": "4", "name": "Stop 4", "lat": 40.7589, "lon": -73.9851, "demand": 10},
            {"id": "5", "name": "Stop 5", "lat": 40.7282, "lon": -73.7949, "demand": 10},
        ],
    )

    async with async_session_factory() as db:
        res = await run_optimization(req, db)

    assert res["status"] == "completed"
    for algo_key, algo_data in res["results"].items():
        assert algo_data.get("unserved_customers") == 0, f"{algo_key} has unserved customers"
        assert algo_data.get("served_customers") == 5, f"{algo_key} did not serve 5 customers"
        val = algo_data.get("validation_report", {})
        assert val.get("is_complete") is True, f"{algo_key} coverage is incomplete"
        assert len(val.get("missing_delivery_ids", [])) == 0, f"{algo_key} missing IDs: {val.get('missing_delivery_ids')}"

