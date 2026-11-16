import sys, os, time, json
sys.path.insert(0, '.')
sys.path.insert(0, 'backend')
from app.services.road_network_service import road_network_service
from app.services.optimization.cooperative_solver import cooperative_solver
import asyncio
from app.api.routes.optimization import get_delivery_stops
import numpy as np

road_network_service.ensure_loaded()
stops = asyncio.run(get_delivery_stops(limit=25))['stops']
depot = (40.7128, -74.0060)
locations = [depot] + [(s['lat'], s['lon']) for s in stops]
demands = [0] + [max(1, int(round(s.get('demand', 10)))) for s in stops]

d_mat, _, _ = road_network_service.build_road_matrix(locations)

# Run with 6 vehicles and capacity 100 so multiple routes with active spatial boundaries exist
caps = [100] * 6
t0 = time.perf_counter()
res = cooperative_solver.solve(d_mat, 6, 0, demands, caps, 0.25, locations=locations)
t_dur = time.perf_counter() - t0

print(f"Status: {res['status']}, Dist: {res['total_distance_km']} km, Time: {t_dur:.3f} s")
print("\nProfiling Breakdown:")
for k, v in res['cooperative_telemetry']['profiling_breakdown'].items():
    print(f"  {k:<35}: {v} ms")

print("\nSubproblem Details:")
for s in res['cooperative_telemetry']['subproblem_details']:
    print(f"  Pair {s['route_pair']}: size={s['subproblem_size']}, strat={s['strategy']}, accepted={s['accepted']}, latency={s['latency_ms']} ms")
