"""
Unit Test: Asynchronous Optimization Job Management Lifecycle & Cancellation
Verifies:
1. POST /api/optimization/jobs returns unique job_id and first feasible route immediately (< 2.0s).
2. Status is initially 'PARTIAL' (or 'COMPLETED' for single solver).
3. GET /api/optimization/jobs/{job_id}/status returns incremental progress.
4. POST /api/optimization/jobs/{job_id}/cancel cancels active job without error.
5. All 18 stops have 100% universal coverage with 0 missing stops.
"""

import asyncio
import pytest
from app.api.routes.optimization import (
    start_optimization_job,
    get_optimization_job_status,
    cancel_optimization_job,
    OptimizationRequest,
    get_delivery_stops,
)
from app.db.session import async_session_factory


@pytest.mark.asyncio
async def test_async_job_immediate_start_and_polling():
    from app.services.road_network_service import road_network_service
    road_network_service.ensure_loaded()

    data = await get_delivery_stops(25)
    stops = data["stops"]
    assert len(stops) == 18

    req = OptimizationRequest(
        selection_mode="compare",
        selected_algorithms=["ortools", "clarke_wright", "two_opt"],
        num_customers=len(stops),
        num_vehicles=6,
        vehicle_capacity=100,
        depot_lat=40.7580,
        depot_lon=-73.8292,
        custom_customers=stops,
    )

    async with async_session_factory() as session:
        # Step 1: Start job - must be instantaneous (< 2s)
        t0 = asyncio.get_event_loop().time()
        start_res = await start_optimization_job(req, session)
        elapsed = asyncio.get_event_loop().time() - t0

        assert elapsed < 2.0, f"Initial job start took {elapsed:.2f}s, expected < 2.0s"
        assert "job_id" in start_res
        job_id = start_res["job_id"]
        assert start_res["status"] == "PARTIAL"
        assert start_res["completed_algorithms"] == 1
        assert start_res["total_algorithms"] == 3
        assert "ortools" in start_res["results"]
        primary_routes = start_res["results"]["ortools"]["routes"]
        assert len(primary_routes) > 0

        # Verify 100% stop coverage for initial feasible route
        visited = set()
        for r in primary_routes:
            for s in r.get("customer_stops", []):
                visited.add(s)
        assert len(visited) == 18, f"Initial feasible route visited {len(visited)}/18 stops"

        # Step 2: Poll status
        await asyncio.sleep(0.5)
        status_res = await get_optimization_job_status(job_id, session)
        assert status_res["job_id"] == job_id
        assert status_res["status"] in ("PARTIAL", "COMPLETED")
        assert status_res["completed_algorithms"] >= 1


@pytest.mark.asyncio
async def test_job_cancellation():
    data = await get_delivery_stops(25)
    stops = data["stops"]

    req = OptimizationRequest(
        selection_mode="compare",
        selected_algorithms=["ortools", "clarke_wright", "two_opt", "tabu_search", "kernighan_lin"],
        num_customers=len(stops),
        num_vehicles=6,
        vehicle_capacity=100,
        depot_lat=40.7580,
        depot_lon=-73.8292,
        custom_customers=stops,
    )

    async with async_session_factory() as session:
        start_res = await start_optimization_job(req, session)
        job_id = start_res["job_id"]

        # Cancel the job
        cancel_res = await cancel_optimization_job(job_id, session)
        assert cancel_res["status"] == "CANCELLED"

        # Verify status endpoint reflects cancellation
        status_res = await get_optimization_job_status(job_id, session)
        assert status_res["status"] == "CANCELLED"
        assert status_res["is_cancelled"] is True
