import sys, os, time, json
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

seeds = [42, 101, 202, 303, 404]
num_vehicles = 6
caps = [100] * num_vehicles

solvers_to_test = [
    ("routeiq_cooperative", "ROUTE/IQ Cooperative Engine"),
    ("ortools", "OR-Tools (CVRP)"),
    ("tabu_search", "Tabu Search Metaheuristic"),
    ("vnd", "Variable Neighborhood Descent (VND)"),
    ("kernighan_lin", "Kernighan–Lin Bipartition"),
]

results = {s_id: {"distances": [], "times": [], "feasible": []} for s_id, _ in solvers_to_test}

print(f"Running Multi-Seed Benchmark across {len(seeds)} independent seeds on canonical 18-stop NYC problem...")
print(f"Depot: {depot}, Vehicles: {num_vehicles}, Capacities: {caps[0]} each\n")

for seed in seeds:
    print(f"--- Testing Seed {seed} ---")
    
    # 1. OR-Tools
    t0 = time.perf_counter()
    res_ort = classical_solver.solve_ortools(d_mat, num_vehicles, 0, demands, caps, 0.25)
    t_ort = time.perf_counter() - t0
    results["ortools"]["distances"].append(res_ort.get("total_distance_km", 0.0))
    results["ortools"]["times"].append(t_ort)
    results["ortools"]["feasible"].append(res_ort.get("success", False))

    # 2. ROUTE/IQ Cooperative
    t0 = time.perf_counter()
    res_coop = cooperative_solver.solve(d_mat, num_vehicles, 0, demands, caps, 0.25, locations=locations, seed=seed)
    t_coop = time.perf_counter() - t0
    results["routeiq_cooperative"]["distances"].append(res_coop.get("total_distance_km", 0.0))
    results["routeiq_cooperative"]["times"].append(t_coop)
    results["routeiq_cooperative"]["feasible"].append(res_coop.get("is_feasible", False))

    # 3. Tabu Search
    t0 = time.perf_counter()
    res_tabu = classical_solver.solve_tabu_search(d_mat, num_vehicles, 0, demands, caps, max_iterations=25)
    t_tabu = time.perf_counter() - t0
    results["tabu_search"]["distances"].append(res_tabu.get("total_distance_km", 0.0))
    results["tabu_search"]["times"].append(t_tabu)
    results["tabu_search"]["feasible"].append(res_tabu.get("success", False))

    # 4. VND
    t0 = time.perf_counter()
    res_vnd = classical_solver.solve_vnd(d_mat, num_vehicles, 0, demands, caps)
    t_vnd = time.perf_counter() - t0
    results["vnd"]["distances"].append(res_vnd.get("total_distance_km", 0.0))
    results["vnd"]["times"].append(t_vnd)
    results["vnd"]["feasible"].append(res_vnd.get("success", False))

    # 5. Kernighan-Lin
    t0 = time.perf_counter()
    res_kl = classical_solver.solve_kernighan_lin(d_mat, num_vehicles, 0, demands, caps)
    t_kl = time.perf_counter() - t0
    results["kernighan_lin"]["distances"].append(res_kl.get("total_distance_km", 0.0))
    results["kernighan_lin"]["times"].append(t_kl)
    results["kernighan_lin"]["feasible"].append(res_kl.get("success", False))

    print(f"  Cooperative : {results['routeiq_cooperative']['distances'][-1]:.3f} km | {t_coop:.3f} s")
    print(f"  OR-Tools    : {results['ortools']['distances'][-1]:.3f} km | {t_ort:.3f} s")
    print(f"  Tabu Search : {results['tabu_search']['distances'][-1]:.3f} km | {t_tabu:.3f} s")
    print(f"  VND         : {results['vnd']['distances'][-1]:.3f} km | {t_vnd:.3f} s")
    print(f"  KL          : {results['kernighan_lin']['distances'][-1]:.3f} km | {t_kl:.3f} s")

print("\n==================== MULTI-SEED STATISTICAL SUMMARY ====================")
summary_table = []
for s_id, s_name in solvers_to_test:
    dists = results[s_id]["distances"]
    times = results[s_id]["times"]
    feas = results[s_id]["feasible"]
    
    mean_d = float(np.mean(dists))
    std_d = float(np.std(dists))
    mean_t = float(np.mean(times))
    std_t = float(np.std(times))
    feas_pct = float(sum(feas) / len(feas) * 100.0)
    
    summary_table.append({
        "id": s_id,
        "name": s_name,
        "mean_dist_km": round(mean_d, 3),
        "std_dist_km": round(std_d, 3),
        "mean_time_s": round(mean_t, 3),
        "std_time_s": round(std_t, 3),
        "feasibility_pct": feas_pct
    })
    print(f"{s_name:<35}: Dist = {mean_d:.3f} +/- {std_d:.3f} km | Time = {mean_t:.3f} +/- {std_t:.3f} s | Feasible = {feas_pct:.1f}%")

out_file = r"C:\Users\DELL\.gemini\antigravity\brain\aba14f7b-722c-4648-8da1-214dc979ac26\production_evidence\multi_seed_benchmark_results.json"
with open(out_file, "w") as f:
    json.dump({"seeds": seeds, "summary": summary_table, "raw": results}, f, indent=2)
print(f"\nSaved statistical benchmark data to: {out_file}")
