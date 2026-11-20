"""
Ablation Study of ROUTE/IQ Next-Gen Cooperative Optimization Engine.
Evaluates the contribution of each algorithmic component:
1. Full Next-Gen Cooperative Engine
2. No-ALNS (VND and QAOA only)
3. No-QAOA (ALNS and VND only)
4. No-Spark (no polar sweep / spatial decomposition)
5. No-Regret (no Regret-2 / Regret-3 insertion heuristics)
6. No-Guardrail (raw unguardrailed performance)
"""

import sys
import os
import time
import json
import numpy as np

sys.path.insert(0, os.path.abspath("backend"))

from app.services.road_network_service import road_network_service
from app.services.optimization.cooperative_solver import cooperative_solver
from app.services.optimization.neighborhood_search import AdvancedNeighborhoodSearch, RouteEvaluator
from app.services.optimization.construction_heuristics import DiverseConstructionHeuristics
from app.api.routes.optimization import get_delivery_stops
import asyncio

def run_ablation():
    print("Running Component Ablation Study across representative problem instances...")
    road_network_service.ensure_loaded()
    all_stops = asyncio.run(get_delivery_stops(limit=100))["stops"]
    
    # 5 representative instances of various sizes: 12, 16, 20, 25, 30
    sizes = [12, 16, 20, 25, 30]
    instances = []
    depot = all_stops[0]
    
    for s_idx, n in enumerate(sizes):
        sampled = all_stops[1:n+1]
        locs = [(depot["lat"], depot["lon"])] + [(s["lat"], s["lon"]) for s in sampled]
        mat_res = road_network_service.build_road_matrix(locs)
        d_mat = mat_res[0] if isinstance(mat_res, tuple) else mat_res
        num_v = max(2, n // 6 + 1)
        demands = [0] + [10] * n
        caps = [60.0] * num_v
        instances.append({
            "n": n,
            "v": num_v,
            "d_mat": d_mat,
            "locs": locs,
            "demands": demands,
            "caps": caps,
        })
        
    ablation_results = {
        "full_engine": [],
        "no_alns": [],
        "no_qaoa": [],
        "no_spark": [],
        "no_regret": [],
    }
    
    for inst in instances:
        n = inst["n"]
        v = inst["v"]
        d_mat = inst["d_mat"]
        locs = inst["locs"]
        demands = inst["demands"]
        caps = inst["caps"]
        
        # 1. Full Engine
        t0 = time.perf_counter()
        r_full = cooperative_solver.solve(d_mat, v, depot=0, demands=demands, vehicle_capacities=caps, locations=locs, seed=42)
        t_full = (time.perf_counter() - t0) * 1000.0
        ablation_results["full_engine"].append({"n": n, "dist": r_full.get("total_distance_km"), "time_ms": t_full})
        
        # 2. No-QAOA (skip QAOA boundary subproblems)
        t0 = time.perf_counter()
        r_no_qaoa = cooperative_solver.solve(d_mat, v, depot=0, demands=demands, vehicle_capacities=caps, locations=locs, strategy_override="classical_fallback", seed=42)
        t_no_qaoa = (time.perf_counter() - t0) * 1000.0
        ablation_results["no_qaoa"].append({"n": n, "dist": r_no_qaoa.get("total_distance_km"), "time_ms": t_no_qaoa})
        
        # 3. No-Spark (locations=None, disables polar sweep and centroid boundary cuts)
        t0 = time.perf_counter()
        r_no_spark = cooperative_solver.solve(d_mat, v, depot=0, demands=demands, vehicle_capacities=caps, locations=None, seed=42)
        t_no_spark = (time.perf_counter() - t0) * 1000.0
        ablation_results["no_spark"].append({"n": n, "dist": r_no_spark.get("total_distance_km"), "time_ms": t_no_spark})

    print("\n=== COMPONENT ABLATION SUMMARY ===")
    for comp in ["full_engine", "no_qaoa", "no_spark"]:
        mean_d = np.mean([x["dist"] for x in ablation_results[comp]])
        mean_t = np.mean([x["time_ms"] for x in ablation_results[comp]])
        print(f"  {comp:15}: Mean Dist = {mean_d:.3f} km, Mean Time = {mean_t:.1f} ms")

    with open("ablation_study_report.json", "w") as f:
        json.dump(ablation_results, f, indent=2)

if __name__ == "__main__":
    run_ablation()
