import sys
import time
import json

sys.path.insert(0, 'backend')
from app.services.road_network_service import road_network_service
from app.services.optimization.classical_solver import classical_solver
from app.services.optimization.cooperative_solver import cooperative_solver
import asyncio
from app.api.routes.optimization import get_delivery_stops

road_network_service.ensure_loaded()
stops = asyncio.run(get_delivery_stops(limit=25))['stops']
valid_stops = [s for s in stops if 40.5 <= s['lat'] <= 40.9 and -74.25 <= s['lon'] <= -73.7][:18]
depot = (40.7128, -74.0060)
locations = [depot] + [(s['lat'], s['lon']) for s in valid_stops]
demands = [0] + [max(1, int(round(s.get('demand', 10)))) for s in valid_stops]

d_mat, _, _ = road_network_service.build_road_matrix(locations)
n = len(locations)

print(f"Problem: {n-1} customers, 1 depot, Total Demand: {sum(demands)}")

test_configs = [
    {"num_vehicles": 2, "capacity": 100, "seeds": [42, 101, 202]},
    {"num_vehicles": 3, "capacity": 100, "seeds": [42, 101, 202]},
    {"num_vehicles": 6, "capacity": 100, "seeds": [42, 101, 202]},
]

benchmark_evidence = []
for cfg in test_configs:
    nv = cfg['num_vehicles']
    cap = cfg['capacity']
    caps = [cap] * nv
    print(f"\n--- Configuration: {nv} vehicles, capacity {cap} ---")
    for seed in cfg['seeds']:
        t0 = time.perf_counter()
        res_ort = classical_solver.solve_ortools(d_mat, nv, 0, demands, caps, 1.0)
        t_ort = round(time.perf_counter() - t0, 3)
        dist_ort = res_ort.get('total_distance_km', 0.0)
        
        t0 = time.perf_counter()
        res_coop = cooperative_solver.solve(d_mat, nv, 0, demands, caps, 1.0, locations=locations, seed=seed)
        t_coop = round(time.perf_counter() - t0, 3)
        dist_coop = res_coop.get('total_distance_km', 0.0)
        
        diff_pct = round(((dist_ort - dist_coop) / dist_ort) * 100.0, 2) if dist_ort > 0 else 0.0
        prop_1_holds = dist_coop <= dist_ort + 1e-4
        
        p1_label = "HOLDS" if prop_1_holds else "VIOLATED"
        benchmark_evidence.append({
            'num_vehicles': nv,
            'seed': seed,
            'ortools_dist_km': float(dist_ort),
            'ortools_time_s': float(t_ort),
            'cooperative_dist_km': float(dist_coop),
            'cooperative_time_s': float(t_coop),
            'diff_pct': float(diff_pct),
            'prop_1_holds': bool(prop_1_holds),
        })
        print(f"Seed {seed:<3} | OR-Tools: {dist_ort:.3f} km ({t_ort}s) | Coop: {dist_coop:.3f} km ({t_coop}s) | Diff: {diff_pct:>5.2f}% | Prop 1: {p1_label}")

out_path = r"C:\Users\DELL\.gemini\antigravity\brain\aba14f7b-722c-4648-8da1-214dc979ac26\production_evidence\benchmark_reproducibility.json"
with open(out_path, 'w') as f:
    json.dump(benchmark_evidence, f, indent=2)
print(f"\nSaved benchmark reproducibility data to {out_path}")
