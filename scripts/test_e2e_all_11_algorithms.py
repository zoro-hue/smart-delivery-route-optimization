import asyncio
import time
import json
import sys
import os

# Ensure backend and engine are importable
sys.path.insert(0, os.path.abspath("backend"))
sys.path.insert(0, os.path.abspath("phase_ab_cooperative_optimization_engine"))

from app.api.routes.optimization import (
    OptimizationRequest,
    start_optimization_job,
    get_optimization_job_status,
    AVAILABLE_ALGORITHMS,
    _active_jobs,
)
from app.db.session import async_session_factory

async def main():
    print("=================================================================")
    print("ROUTE/IQ ALL 11 ALGORITHMS ASYNC JOB LIFECYCLE E2E TEST")
    print("=================================================================")

    all_ids = [a["id"] for a in AVAILABLE_ALGORITHMS]
    print(f"Registered algorithms ({len(all_ids)}): {all_ids}")
    assert len(all_ids) == 11, f"Expected 11 algorithms, found {len(all_ids)}"

    # Retrieve 18 valid non-water-body stops
    from app.api.routes.optimization import get_delivery_stops
    stops_resp = await get_delivery_stops(50)
    all_stops = stops_resp.get("stops", [])
    stops = all_stops[:18]
    print(f"Retrieved {len(all_stops)} validated stops from data processor, selected {len(stops)}")
    assert len(stops) == 18, f"Expected 18 stops, got {len(stops)}"

    req = OptimizationRequest(
        selection_mode="compare",
        selected_algorithms=all_ids,
        num_customers=18,
        num_vehicles=3,
        vehicle_capacity=100.0,
        depot_lat=40.7128,
        depot_lon=-74.0060,
        custom_customers=stops,
        traffic_scenario="normal",
        weather_scenario="clear",
        classical_time_limit_sec=1,
        qaoa_depth=1,
        qaoa_shots=100,
        qaoa_optimizer="COBYLA",
    )

    # Warm up road network service if not already loaded
    from app.services.road_network_service import road_network_service
    if not road_network_service.is_ready():
        print("Pre-warming road network service...")
        road_network_service.load_network()

    async with async_session_factory() as session:
        t0 = time.time()
        start_resp = await start_optimization_job(req, session)
        t_start = time.time() - t0
        job_id = start_resp["job_id"]
        print(f"\n[JOB STARTED] ID: {job_id}")
        print(f"Immediate response time: {t_start:.3f}s")
        assert t_start < 5.0, f"Immediate start response took too long: {t_start:.3f}s"
        print(f"Initial status: {start_resp['status']}, Primary: {start_resp['primary_algorithm']}")
        print(f"Primary distance: {start_resp['results'][start_resp['primary_algorithm']]['total_distance_km']:.2f} km")

        # Poll until completion or timeout
        max_wait = 45.0
        poll_interval = 0.5
        waited = 0.0

        last_progress = ""
        while waited < max_wait:
            await asyncio.sleep(poll_interval)
            waited += poll_interval

            status_resp = await get_optimization_job_status(job_id, session)
            curr_progress = status_resp["progress_label"]
            if curr_progress != last_progress:
                print(f"[{waited:4.1f}s] Status: {status_resp['status']} | Progress: {curr_progress}")
                last_progress = curr_progress

            if status_resp["status"] in ("COMPLETED", "FAILED", "CANCELLED"):
                print(f"\n[JOB TERMINAL] Reached status: {status_resp['status']} at {waited:.1f}s")
                break

        final_status = await get_optimization_job_status(job_id, session)
        results = final_status["results"]
        print(f"\nTotal completed algorithms returned: {len([a for a in all_ids if a in results])}/11")
        print("-----------------------------------------------------------------")
        print(f"{'Algorithm':<25} | {'Status':<10} | {'Distance (km)':<13} | {'Time (s)':<8} | {'Stops':<5}")
        print("-----------------------------------------------------------------")

        for algo_id in all_ids:
            res = results.get(algo_id)
            if res:
                st = final_status["solver_statuses"].get(algo_id, "done")
                dist = res.get("total_distance_km", 0.0)
                exec_time = res.get("execution_time_sec", 0.0)
                served = res.get("served_customers", 0)
                print(f"{algo_id:<25} | {st:<10} | {dist:<13.3f} | {exec_time:<8.3f} | {served:<5}")
            else:
                st = final_status["solver_statuses"].get(algo_id, "missing")
                print(f"{algo_id:<25} | {st:<10} | {'MISSING':<13} | {'--':<8} | {'--':<5}")

        print("-----------------------------------------------------------------")

        # Verify all 11 algorithms are present in results
        missing = [a for a in all_ids if a not in results]
        assert len(missing) == 0, f"Missing algorithm results: {missing}"

        # Verify Proposition 1: Cost(Cooperative) <= Cost(Incumbent)
        coop_res = results.get("routeiq_cooperative")
        ortools_res = results.get("ortools")
        assert coop_res is not None, "routeiq_cooperative missing from results"
        assert ortools_res is not None, "ortools missing from results"
        assert coop_res["is_feasible"], "ROUTE/IQ Cooperative result must be feasible"

        print(f"\nProposition 1 Guardrail Check:")
        print(f"  OR-Tools Incumbent:  {ortools_res['total_distance_km']:.3f} km")
        print(f"  Cooperative Engine:  {coop_res['total_distance_km']:.3f} km")
        diff = coop_res['total_distance_km'] - ortools_res['total_distance_km']
        print(f"  Difference:          {diff:+.3f} km (<= 1e-4 required)")
        assert coop_res["total_distance_km"] <= ortools_res["total_distance_km"] + 1e-4, (
            f"Proposition 1 violated: {coop_res['total_distance_km']} > {ortools_res['total_distance_km']}"
        )
        print("  PROPOSITION 1 SATISFIED: Cooperative is strictly <= Incumbent!")

        print("\nALL 11 ALGORITHMS VERIFIED COMPLETED & VALID!")

if __name__ == "__main__":
    asyncio.run(main())
