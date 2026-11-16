import time
import os
import sys
import numpy as np
import copy
import logging
import asyncio

# Ensure project root and backend are in sys.path
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("backend"))

from app.api.routes.optimization import get_delivery_stops
from app.services.road_network_service import road_network_service
from app.services.optimization.classical_solver import classical_solver
from app.services.optimization.cooperative_solver import cooperative_solver
from app.services.optimization.route_validator import repair_fleet_coverage
from phase_v_independent_quantum_validation.prototypes.algorithmic_vnd import AlgorithmicVND

logging.basicConfig(level=logging.INFO)

print("Loading road network and canonical 18 stops...")
road_network_service.ensure_loaded()
stops_res = asyncio.run(get_delivery_stops(limit=25))
stops = stops_res["stops"]
print(f"Loaded {len(stops)} stops.")

depot_loc = (40.7128, -74.0060)
locations = [depot_loc] + [(s["lat"], s["lon"]) for s in stops]
n = len(locations)
demands = [0] + [max(1, int(round(s.get("demand", 10)))) for s in stops]
num_vehicles = 3
capacities = [1000] * num_vehicles

print("Building road network distance matrix...")
t0_mat = time.perf_counter()
matrix_res, snapped_nodes, warnings = road_network_service.build_road_matrix(locations)
dist_matrix = matrix_res
t_mat = time.perf_counter() - t0_mat
print(f"Matrix built in {t_mat:.4f}s. Shape: {dist_matrix.shape}")

print("\n================== DETAILED STEP-BY-STEP PROFILING ==================")

# Step 1: OR-Tools Incumbent
t0 = time.perf_counter()
inc_res = classical_solver.solve_ortools(
    distance_matrix=dist_matrix,
    num_vehicles=num_vehicles,
    depot=0,
    demands=demands,
    vehicle_capacities=capacities,
    time_limit_sec=0.25,
)
t_ortools = time.perf_counter() - t0
print(f"1. OR-Tools Incumbent: {t_ortools:.4f} s | Dist: {inc_res.get('total_distance_km')} km")

# Step 2: Multi-Solver Pool (Tabu Search)
t0 = time.perf_counter()
cand_tabu = classical_solver.solve_tabu_search(
    dist_matrix, num_vehicles, 0, demands, capacities, max_iterations=80
)
t_tabu = time.perf_counter() - t0
print(f"2. Multi-Solver Pool (Tabu Search 80 iters): {t_tabu:.4f} s | Dist: {cand_tabu.get('total_distance_km')} km")

# Step 3: Multi-Solver Pool (VND)
t0 = time.perf_counter()
cand_vnd = classical_solver.solve_vnd(
    dist_matrix, num_vehicles, 0, demands, capacities
)
t_vnd = time.perf_counter() - t0
print(f"3. Multi-Solver Pool (VND): {t_vnd:.4f} s | Dist: {cand_vnd.get('total_distance_km')} km")

# Step 4: Spatial Centroids & Pairing
t0 = time.perf_counter()
routes = copy.deepcopy(inc_res["routes"])
route_centroids = []
for r in routes:
    c_nodes = r.get("customer_stops", [])
    if not c_nodes:
        route_centroids.append((0.0, 0.0))
    else:
        avg_lat = float(np.mean([locations[c][0] for c in c_nodes]))
        avg_lon = float(np.mean([locations[c][1] for c in c_nodes]))
        route_centroids.append((avg_lat, avg_lon))

pair_candidates = []
for i in range(len(routes)):
    for j in range(i + 1, len(routes)):
        ci, cj = route_centroids[i], route_centroids[j]
        spatial_dist = np.hypot(ci[0] - cj[0], ci[1] - cj[1])
        pair_candidates.append((spatial_dist, i, j))
pair_candidates.sort(key=lambda x: x[0])
t_spatial = time.perf_counter() - t0
print(f"4. Spatial Centroids & Route Pairing: {t_spatial:.4f} s | Pairs found: {len(pair_candidates)}")

# Step 5: Subproblem Optimization (QAOA + Tabu + KL)
t_subproblems = 0.0
sub_details = []
for p_idx, (_, idx_a, idx_b) in enumerate(pair_candidates[:4]):
    t0_sub = time.perf_counter()
    route_a = routes[idx_a]
    route_b = routes[idx_b]
    stops_a = list(route_a.get("customer_stops", []))
    stops_b = list(route_b.get("customer_stops", []))
    if not stops_a or not stops_b:
        continue
    
    ca_pt = route_centroids[idx_a]
    cb_pt = route_centroids[idx_b]
    def b_dist(c, own_c, other_c):
        loc = locations[c]
        return np.hypot(loc[0] - other_c[0], loc[1] - other_c[1]) - np.hypot(loc[0] - own_c[0], loc[1] - own_c[1])
    sorted_a = sorted(stops_a, key=lambda c: b_dist(c, ca_pt, cb_pt))
    sorted_b = sorted(stops_b, key=lambda c: b_dist(c, cb_pt, ca_pt))
    bound_a = sorted_a[:min(4, len(sorted_a))]
    bound_b = sorted_b[:min(4, len(sorted_b))]
    sub_custs = bound_a + bound_b
    sub_k = len(sub_custs)
    if sub_k < 4:
        continue
    
    sub_to_node = {i + 1: node for i, node in enumerate(sub_custs)}
    sub_dist = np.zeros((sub_k + 1, sub_k + 1))
    for i_sub, orig_i in sub_to_node.items():
        sub_dist[0, i_sub] = dist_matrix[0, orig_i]
        sub_dist[i_sub, 0] = dist_matrix[orig_i, 0]
        for j_sub, orig_j in sub_to_node.items():
            sub_dist[i_sub, j_sub] = dist_matrix[orig_i, orig_j]
    sub_demands = np.array([demands[sub_to_node[i]] for i in range(1, sub_k + 1)], dtype=float)
    cap_a = float(route_a.get("capacity", capacities[idx_a]))
    cap_b = float(route_b.get("capacity", capacities[idx_b]))
    unaffected_a = [c for c in stops_a if c not in sub_custs]
    unaffected_b = [c for c in stops_b if c not in sub_custs]
    sub_cap_a = cap_a - sum(demands[c] for c in unaffected_a)
    sub_cap_b = cap_b - sum(demands[c] for c in unaffected_b)
    
    t_opt_0 = time.perf_counter()
    opt_res = cooperative_solver.engine.optimize_subproblem(
        dist_matrix=sub_dist,
        demands=sub_demands,
        cap_a=sub_cap_a,
        cap_b=sub_cap_b,
        c_a=np.array([ca_pt[0], ca_pt[1]]),
        c_b=np.array([cb_pt[0], cb_pt[1]]),
        seed=42 + p_idx,
    )
    t_sub_opt = time.perf_counter() - t_opt_0
    t_sub_total = time.perf_counter() - t0_sub
    t_subproblems += t_sub_total
    sub_details.append((p_idx, opt_res.get("strategy_used"), t_sub_opt, opt_res.get("guardrail_accepted")))

print(f"5. Boundary Subproblems (up to 4 pairs): {t_subproblems:.4f} s")
for s_idx, strat, s_time, acc in sub_details:
    print(f"   - Pair {s_idx}: Strategy={strat}, Time={s_time:.4f} s, Accepted={acc}")

# Step 6: Inter-Route VND Relocate & Swap
t0 = time.perf_counter()
for i in range(len(routes)):
    for j in range(len(routes)):
        if i == j:
            continue
        r_a, r_b = routes[i], routes[j]
        t_a, t_b = list(r_a.get("customer_stops", [])), list(r_b.get("customer_stops", []))
        cap_a = float(r_a.get("capacity", capacities[i]))
        cap_b = float(r_b.get("capacity", capacities[j]))
        vnd_res = AlgorithmicVND.optimize_fleet_routes(
            t_a, t_b, np.array([demands[k] for k in range(1, n)]), cap_a, cap_b, dist_matrix, depot_idx=0
        )
t_inter_vnd = time.perf_counter() - t0
print(f"6. Inter-Route VND (All pairs): {t_inter_vnd:.4f} s")

# Step 7: Intra-Route 2-Opt
t0 = time.perf_counter()
for r in routes:
    st = r.get("customer_stops", [])
    if len(st) >= 2:
        opt_st = AlgorithmicVND.run_2opt(st, dist_matrix, 0)
t_intra_2opt = time.perf_counter() - t0
print(f"7. Intra-Route 2-Opt: {t_intra_2opt:.4f} s")

# Step 8: Full cooperative_solver.solve call
print("\n--- Running Full cooperative_solver.solve() ---")
t0 = time.perf_counter()
full_res = cooperative_solver.solve(
    distance_matrix=dist_matrix,
    num_vehicles=num_vehicles,
    depot=0,
    demands=demands,
    vehicle_capacities=capacities,
    time_limit_sec=0.25,
    locations=locations,
)
t_full = time.perf_counter() - t0
print(f"TOTAL COOPERATIVE SOLVER RUNTIME: {t_full:.4f} s | Final Dist: {full_res.get('total_distance_km')} km")
