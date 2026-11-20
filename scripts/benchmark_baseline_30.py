"""
Baseline Profiling Script for ROUTE/IQ Cooperative Engine and 10 Comparison Solvers.
Evaluates 30 reproducible instances across different problem sizes and random seeds.
Saves exact baseline metrics before next-gen algorithmic enhancements.
"""

import sys
import os
import time
import json
import math
import random
import numpy as np

sys.path.insert(0, os.path.abspath("backend"))

from app.core.config import get_settings
from app.services.road_network_service import road_network_service
from app.services.optimization.classical_solver import classical_solver
from app.services.optimization.cooperative_solver import cooperative_solver
from app.services.optimization.qiga_solver import qiga_solver
from app.services.optimization.quantum_solver import quantum_solver, _check_qiskit_available
from app.services.optimization.route_validator import validate_fleet_coverage

import asyncio
from app.api.routes.optimization import get_delivery_stops

def generate_instances(num_instances=30):
    road_network_service.ensure_loaded()
    all_stops = asyncio.run(get_delivery_stops(limit=150))["stops"]
    nyc_nodes = [
        s for s in all_stops
        if 40.65 <= s["lat"] <= 40.85 and -74.05 <= s["lon"] <= -73.85
    ]
    if len(nyc_nodes) < 50:
        nyc_nodes = all_stops[:100]
        
    depot_node = nyc_nodes[0]
    candidate_stops = nyc_nodes[1:]

    instances = []
    # Mix of problem sizes: small (8, 12), medium (15, 18, 20), larger (25, 30)
    sizes = [8, 10, 12, 14, 15, 16, 18, 20, 22, 25, 28, 30]
    
    for idx in range(num_instances):
        seed = 1000 + idx * 37
        rng = random.Random(seed)
        n = sizes[idx % len(sizes)]
        sampled = rng.sample(candidate_stops, n)
        
        # Vehicle configuration
        num_vehicles = max(2, math.ceil(n / 6))
        demands = [0] + [rng.randint(5, 20) for _ in range(n)]
        total_demand = sum(demands)
        cap = float(math.ceil((total_demand / num_vehicles) * 1.35))
        capacities = [cap] * num_vehicles
        
        locations = [(depot_node["lat"], depot_node["lon"])] + [(s["lat"], s["lon"]) for s in sampled]
        
        # Build distance matrix via road network service
        mat_res = road_network_service.build_road_matrix(locations)
        dist_matrix = mat_res[0] if isinstance(mat_res, tuple) else mat_res
                    
        instances.append({
            "instance_id": idx + 1,
            "seed": seed,
            "num_customers": n,
            "num_vehicles": num_vehicles,
            "capacities": capacities,
            "demands": demands,
            "locations": locations,
            "distance_matrix": dist_matrix,
        })
    return instances

def check_val(routes, cust_ids, dems, caps, d_mat):
    return validate_fleet_coverage(
        routes=routes,
        input_customer_ids=cust_ids,
        demands=dems,
        vehicle_capacities=caps,
        depot=0,
        distance_matrix=d_mat,
    )

def run_baseline():
    print("Generating 30 reproducible benchmark instances...")
    instances = generate_instances(30)
    print(f"Generated {len(instances)} instances.")
    
    solvers = [
        "routeiq_cooperative",
        "ortools",
        "clarke_wright",
        "two_opt",
        "dijkstra",
        "astar",
        "tabu_search",
        "kernighan_lin",
        "vnd",
        "qiga",
        "qaoa",
    ]
    
    results = []
    qiskit_avail, _ = _check_qiskit_available()
    
    for inst in instances:
        iid = inst["instance_id"]
        n = inst["num_customers"]
        num_v = inst["num_vehicles"]
        caps = inst["capacities"]
        dems = inst["demands"]
        locs = inst["locations"]
        d_mat = inst["distance_matrix"]
        cust_ids = list(range(1, n + 1))
        
        inst_res = {
            "instance_id": iid,
            "n": n,
            "vehicles": num_v,
            "seed": inst["seed"],
            "solvers": {},
        }
        print(f"\n--- Instance {iid}/30 (n={n}, v={num_v}) ---")
        
        # 1. OR-Tools
        t0 = time.perf_counter()
        ort_res = classical_solver.solve_ortools(
            d_mat, num_v, depot=0, demands=dems, vehicle_capacities=caps, time_limit_sec=0.5
        )
        t_ort = (time.perf_counter() - t0) * 1000.0
        ort_val = check_val(ort_res.get("routes", []), cust_ids, dems, caps, d_mat)
        ort_dist = ort_res.get("total_distance_km") or ort_res.get("total_distance", float("inf"))
        inst_res["solvers"]["ortools"] = {
            "distance_km": ort_dist,
            "time_ms": t_ort,
            "feasible": ort_val["is_valid"],
        }
        
        # 2. ROUTE/IQ Cooperative Engine
        t0 = time.perf_counter()
        coop_res = cooperative_solver.solve(
            distance_matrix=d_mat,
            num_vehicles=num_v,
            depot=0,
            demands=dems,
            vehicle_capacities=caps,
            time_limit_sec=1.5,
            locations=locs,
            seed=inst["seed"],
        )
        t_coop = (time.perf_counter() - t0) * 1000.0
        coop_val = check_val(coop_res.get("routes", []), cust_ids, dems, caps, d_mat)
        coop_dist = coop_res.get("total_distance_km") or coop_res.get("total_distance", float("inf"))
        inst_res["solvers"]["routeiq_cooperative"] = {
            "distance_km": coop_dist,
            "time_ms": t_coop,
            "feasible": coop_val["is_valid"],
            "improvement_over_ortools": ort_dist - coop_dist,
            "improvement_pct": ((ort_dist - coop_dist) / ort_dist * 100.0) if ort_dist > 0 else 0.0,
        }
        
        # 3. Clarke-Wright
        t0 = time.perf_counter()
        cw_res = classical_solver.solve_clarke_wright(d_mat, num_v, depot=0, demands=dems, vehicle_capacities=caps)
        t_cw = (time.perf_counter() - t0) * 1000.0
        cw_val = check_val(cw_res.get("routes", []), cust_ids, dems, caps, d_mat)
        inst_res["solvers"]["clarke_wright"] = {
            "distance_km": cw_res.get("total_distance_km") or cw_res.get("total_distance", float("inf")),
            "time_ms": t_cw,
            "feasible": cw_val["is_valid"],
        }
        
        # 4. 2-Opt
        t0 = time.perf_counter()
        to_res = classical_solver.solve_two_opt(d_mat, num_v, depot=0, demands=dems, vehicle_capacities=caps)
        t_to = (time.perf_counter() - t0) * 1000.0
        to_val = check_val(to_res.get("routes", []), cust_ids, dems, caps, d_mat)
        inst_res["solvers"]["two_opt"] = {
            "distance_km": to_res.get("total_distance_km") or to_res.get("total_distance", float("inf")),
            "time_ms": t_to,
            "feasible": to_val["is_valid"],
        }
        
        # 5. Dijkstra
        t0 = time.perf_counter()
        dijk_res = classical_solver.solve_dijkstra(d_mat, num_v, depot=0, demands=dems, vehicle_capacities=caps)
        t_dijk = (time.perf_counter() - t0) * 1000.0
        dijk_val = check_val(dijk_res.get("routes", []), cust_ids, dems, caps, d_mat)
        inst_res["solvers"]["dijkstra"] = {
            "distance_km": dijk_res.get("total_distance_km") or dijk_res.get("total_distance", float("inf")),
            "time_ms": t_dijk,
            "feasible": dijk_val["is_valid"],
        }
        
        # 6. A*
        t0 = time.perf_counter()
        astar_res = classical_solver.solve_astar(d_mat, num_v, depot=0, demands=dems, vehicle_capacities=caps, locations=locs)
        t_astar = (time.perf_counter() - t0) * 1000.0
        astar_val = check_val(astar_res.get("routes", []), cust_ids, dems, caps, d_mat)
        inst_res["solvers"]["astar"] = {
            "distance_km": astar_res.get("total_distance_km") or astar_res.get("total_distance", float("inf")),
            "time_ms": t_astar,
            "feasible": astar_val["is_valid"],
        }
        
        # 7. Tabu Search
        t0 = time.perf_counter()
        tabu_res = classical_solver.solve_tabu_search(d_mat, num_v, depot=0, demands=dems, vehicle_capacities=caps, max_iterations=25)
        t_tabu = (time.perf_counter() - t0) * 1000.0
        tabu_val = check_val(tabu_res.get("routes", []), cust_ids, dems, caps, d_mat)
        inst_res["solvers"]["tabu_search"] = {
            "distance_km": tabu_res.get("total_distance_km") or tabu_res.get("total_distance", float("inf")),
            "time_ms": t_tabu,
            "feasible": tabu_val["is_valid"],
        }
        
        # 8. Kernighan-Lin
        t0 = time.perf_counter()
        kl_res = classical_solver.solve_kernighan_lin(d_mat, num_v, depot=0, demands=dems, vehicle_capacities=caps, max_passes=2)
        t_kl = (time.perf_counter() - t0) * 1000.0
        kl_val = check_val(kl_res.get("routes", []), cust_ids, dems, caps, d_mat)
        inst_res["solvers"]["kernighan_lin"] = {
            "distance_km": kl_res.get("total_distance_km") or kl_res.get("total_distance", float("inf")),
            "time_ms": t_kl,
            "feasible": kl_val["is_valid"],
        }
        
        # 9. VND
        t0 = time.perf_counter()
        vnd_res = classical_solver.solve_vnd(d_mat, num_v, depot=0, demands=dems, vehicle_capacities=caps)
        t_vnd = (time.perf_counter() - t0) * 1000.0
        vnd_val = check_val(vnd_res.get("routes", []), cust_ids, dems, caps, d_mat)
        inst_res["solvers"]["vnd"] = {
            "distance_km": vnd_res.get("total_distance_km") or vnd_res.get("total_distance", float("inf")),
            "time_ms": t_vnd,
            "feasible": vnd_val["is_valid"],
        }
        
        # 10. QIGA
        t0 = time.perf_counter()
        qiga_res = qiga_solver.solve(d_mat, num_v, depot=0, demands=dems, vehicle_capacities=caps)
        t_qiga = (time.perf_counter() - t0) * 1000.0
        qiga_val = check_val(qiga_res.get("routes", []), cust_ids, dems, caps, d_mat)
        inst_res["solvers"]["qiga"] = {
            "distance_km": qiga_res.get("total_distance_km") or qiga_res.get("total_distance", float("inf")),
            "time_ms": t_qiga,
            "feasible": qiga_val["is_valid"],
        }
        
        # 11. QAOA (subproblem or <= 8)
        if qiskit_avail and n <= 8:
            t0 = time.perf_counter()
            qaoa_res = quantum_solver.solve(d_mat, num_v, depot=0, demands=dems, vehicle_capacity=caps[0], p=1, shots=100, max_iter=2)
            t_qaoa = (time.perf_counter() - t0) * 1000.0
            qaoa_val = check_val(qaoa_res.get("routes", []), cust_ids, dems, caps, d_mat)
            inst_res["solvers"]["qaoa"] = {
                "distance_km": qaoa_res.get("total_distance_km") or qaoa_res.get("total_distance", float("inf")),
                "time_ms": t_qaoa,
                "feasible": qaoa_val["is_valid"],
            }
        else:
            inst_res["solvers"]["qaoa"] = {
                "distance_km": float("inf"),
                "time_ms": 0.0,
                "feasible": False,
                "note": "Skipped because n > 8",
            }
            
        print(f"  OR-Tools:            {inst_res['solvers']['ortools']['distance_km']:.3f} km ({t_ort:.1f} ms)")
        print(f"  ROUTE/IQ Coop:       {inst_res['solvers']['routeiq_cooperative']['distance_km']:.3f} km ({t_coop:.1f} ms) [Imp: {inst_res['solvers']['routeiq_cooperative']['improvement_pct']:.2f}%]")
        print(f"  Clarke-Wright:       {inst_res['solvers']['clarke_wright']['distance_km']:.3f} km")
        print(f"  VND:                 {inst_res['solvers']['vnd']['distance_km']:.3f} km")
        print(f"  Tabu Search:         {inst_res['solvers']['tabu_search']['distance_km']:.3f} km")
        
        results.append(inst_res)
        
    with open("baseline_30_instances_report.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nBaseline profiling complete! Saved to baseline_30_instances_report.json")

if __name__ == "__main__":
    run_baseline()
