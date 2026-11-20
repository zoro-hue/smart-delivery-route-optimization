import sys
import os
import time
import json
import numpy as np

# Add backend to path
sys.path.insert(0, os.path.abspath("backend"))

from app.services.road_network_service import road_network_service
from app.api.routes.optimization import _prepare_optimization_problem, _solve_single_algo, OptimizationRequest, AVAILABLE_ALGORITHMS

print("=" * 70, flush=True)
print("PROFILING ALL 11 ALGORITHMS INDEPENDENTLY (18 STOPS)", flush=True)
print("=" * 70, flush=True)

import asyncio
from app.api.routes.optimization import get_delivery_stops
stops_res = asyncio.run(get_delivery_stops(18))
stops = stops_res.get("stops", [])
print(f"Loaded {len(stops)} validated land delivery stops from get_delivery_stops.", flush=True)

req = OptimizationRequest(
    selection_mode="compare",
    selected_algorithms=[a["id"] for a in AVAILABLE_ALGORITHMS],
    custom_customers=stops,
    num_customers=len(stops),
    num_vehicles=3,
    vehicle_capacity=1000.0,
    depot_lat=40.7128,
    depot_lon=-74.0060,
    classical_time_limit_sec=1,
)

# Benchmark Preprocessing & Distance Matrix
t0_prep = time.time()
(
    locations, demands, n, adjusted_matrix, snapped_node_ids,
    road_warnings, physical_matrix, objective_weights, demands_int,
    total_cust_demand, total_fleet_capacity, capacities,
    traffic_factor, weather_factor
) = _prepare_optimization_problem(req)
prep_time = round(time.time() - t0_prep, 3)
print(f"Road Graph Preprocessing & Matrix Construction: {prep_time}s (Matrix shape: {adjusted_matrix.shape})", flush=True)

route_geometry_cache = {}

results = []
for algo_info in AVAILABLE_ALGORITHMS:
    algo_id = algo_info["id"]
    t0 = time.time()
    try:
        res = _solve_single_algo(
            algo_id, n, req.num_vehicles, req.vehicle_capacity,
            req.classical_time_limit_sec, req.qaoa_depth, req.qaoa_shots,
            req.qaoa_optimizer, req.qaoa_penalty, req.random_seed,
            locations, demands_int, capacities, adjusted_matrix,
            objective_weights, snapped_node_ids, road_warnings,
            route_geometry_cache
        )
        wall_time = round(time.time() - t0, 3)
        dist = res.get("total_distance_km", 0.0)
        feasible = res.get("is_feasible", False)
        status = res.get("status", "SUCCESS")
        metrics = res.get("resource_metrics", {})
        solver_time = round(metrics.get("runtime_ms", 0.0) / 1000.0, 3)
        
        results.append({
            "id": algo_id,
            "name": res.get("algorithm_name", algo_id),
            "distance_km": dist,
            "wall_time_sec": wall_time,
            "solver_time_sec": solver_time,
            "is_feasible": feasible,
            "status": status,
        })
        print(f"[{algo_id:22}] Dist: {dist:8.3f} km | Wall: {wall_time:6.3f}s | Solver: {solver_time:6.3f}s | Feasible: {feasible} | Status: {status}", flush=True)
    except Exception as e:
        wall_time = round(time.time() - t0, 3)
        print(f"[{algo_id:22}] ERROR in {wall_time}s: {e}", flush=True)
        results.append({
            "id": algo_id,
            "name": algo_info["name"],
            "distance_km": 0.0,
            "wall_time_sec": wall_time,
            "solver_time_sec": 0.0,
            "is_feasible": False,
            "status": "FAILED",
            "error": str(e)
        })

print("\n" + "=" * 70, flush=True)
print(f"TOTAL COMPARISON RUNTIME: {sum(r['wall_time_sec'] for r in results):.3f}s", flush=True)
print("=" * 70, flush=True)
