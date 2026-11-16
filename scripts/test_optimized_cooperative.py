import sys, os, time, json
sys.path.insert(0, '.')
sys.path.insert(0, 'backend')

from app.services.road_network_service import road_network_service
from app.services.optimization.cooperative_solver import cooperative_solver
import asyncio
from app.api.routes.optimization import get_delivery_stops
import numpy as np

print("Initializing test environment...")
road_network_service.ensure_loaded()
stops = asyncio.run(get_delivery_stops(limit=25))['stops']
depot = (40.7128, -74.0060)
locations = [depot] + [(s['lat'], s['lon']) for s in stops]
demands = [0] + [max(1, int(round(s.get('demand', 10)))) for s in stops]
num_vehicles = 3
capacities = [1000] * 3

print("Building road network distance matrix...")
d_mat, _, _ = road_network_service.build_road_matrix(locations)

print("\n--- Running Optimized ROUTE/IQ Cooperative Solver ---")
t0 = time.perf_counter()
res = cooperative_solver.solve(
    distance_matrix=d_mat,
    num_vehicles=num_vehicles,
    depot=0,
    demands=demands,
    vehicle_capacities=capacities,
    time_limit_sec=0.25,
    locations=locations,
)
t_elapsed = time.perf_counter() - t0

print(f"Solver Status: {res['status']}")
print(f"Feasible: {res['is_feasible']}")
print(f"Total Distance: {res['total_distance_km']} km")
print(f"Total Execution Time (wall clock): {t_elapsed:.4f} s (reported: {res['execution_time_sec']} s)")

telemetry = res.get("cooperative_telemetry", {})
print("\n--- Profiling Breakdown ---")
for k, v in telemetry.get("profiling_breakdown", {}).items():
    print(f"  {k:<35}: {v} ms")

print("\n--- Categorized Timings ---")
for k, v in telemetry.get("timings", {}).items():
    print(f"  {k:<35}: {v} s")

# Second run (warm start with matrix cache)
print("\n--- Second Run (Warm Start & Cache Verification) ---")
t0_warm = time.perf_counter()
d_mat_cached, _, _ = road_network_service.build_road_matrix(locations)
res_warm = cooperative_solver.solve(
    distance_matrix=d_mat_cached,
    num_vehicles=num_vehicles,
    depot=0,
    demands=demands,
    vehicle_capacities=capacities,
    time_limit_sec=0.25,
    locations=locations,
)
t_warm_total = time.perf_counter() - t0_warm
print(f"Warm Start Total End-to-End Time: {t_warm_total:.4f} s | Dist: {res_warm['total_distance_km']} km")
print(f"Warm Start Target < 2.0s achieved: {t_warm_total < 2.0}")
