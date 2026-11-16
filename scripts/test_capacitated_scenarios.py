import sys, os, time
sys.path.insert(0, '.')
sys.path.insert(0, 'backend')
from app.services.road_network_service import road_network_service
from app.services.optimization.classical_solver import classical_solver
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

print(f"Total customer demand: {sum(demands)} units")

for cap in [1000, 100, 85]:
    caps = [cap] * 3
    print(f"\n--- Capacity per vehicle = {cap} (Fleet: 3 vehicles) ---")
    t0 = time.time()
    res_ort = classical_solver.solve_ortools(d_mat, 3, 0, demands, caps, 0.25)
    t_ort = time.time() - t0
    d_ort = res_ort.get("total_distance_km")
    v_ort = len([r for r in res_ort.get("routes", []) if r.get("customer_stops")])
    print(f"OR-Tools: {d_ort} km in {t_ort:.3f}s (active vehicles: {v_ort})")

    t0 = time.time()
    res_coop = cooperative_solver.solve(d_mat, 3, 0, demands, caps, 0.25, locations=locations)
    t_coop = time.time() - t0
    d_coop = res_coop.get("total_distance_km")
    v_coop = len([r for r in res_coop.get("routes", []) if r.get("customer_stops")])
    print(f"Cooperative: {d_coop} km in {t_coop:.3f}s (active vehicles: {v_coop})")
