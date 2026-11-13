"""Exact Small-Instance Global Optimum Validation for ROUTE/IQ.

Computes the mathematically exact global optimum for CVRP on authentic Manhattan
directed road subgraphs using:
1. Held-Karp Dynamic Programming for exact directed TSP sub-tours: O(2^k * k^2)
2. Submask Dynamic Programming for exact Set Partitioning CVRP: O(3^N)

Evaluates:
- Exact Global Optimum (Held-Karp + Set Partition DP)
- Google OR-Tools GLS
- Clarke-Wright + 2-opt
- Quantum-Inspired Genetic Algorithm (QIGA)
- Baseline Monolithic QAOA (truncated)
- RB-QCD (Proposed)

Measures exact approximation ratio alpha = E_algo / E_exact and optimality gaps.
"""

import sys
sys.path.insert(0, 'backend')

import os
import json
import time
import pickle
import itertools
import numpy as np
import pandas as pd
import networkx as nx
from typing import List, Dict, Any, Tuple

from app.services.optimization.classical_solver import ClassicalVRPSolver
from app.services.optimization.qiga_solver import QIGASolver
from app.services.optimization.quantum_solver import QuantumVRPSolver
from app.services.optimization.rb_qcd_decomposer import RBQCDDecomposer


def held_karp_exact_tsp(subset_indices: List[int], matrix: np.ndarray) -> Tuple[float, List[int]]:
    """Computes exact directed TSP tour on depot (0) and subset of customer indices."""
    k = len(subset_indices)
    if k == 0:
        return 0.0, [0, 0]
    if k == 1:
        u = subset_indices[0]
        return matrix[0, u] + matrix[u, 0], [0, u, 0]

    # Map subset indices to 0..k-1
    node_to_idx = {node: i for i, node in enumerate(subset_indices)}
    # dp[mask][i] = min cost to start at 0, visit subset 'mask', ending at subset_indices[i]
    # mask has k bits
    INF = 1e12
    dp = {}
    parent = {}

    for i, node in enumerate(subset_indices):
        mask = 1 << i
        dp[(mask, i)] = matrix[0, node]
        parent[(mask, i)] = -1

    for mask_size in range(2, k + 1):
        for combo in itertools.combinations(range(k), mask_size):
            mask = 0
            for bit in combo:
                mask |= (1 << bit)
            for j in combo:
                prev_mask = mask ^ (1 << j)
                v = subset_indices[j]
                best_cost = INF
                best_p = -1
                for p in combo:
                    if p != j:
                        u = subset_indices[p]
                        c = dp.get((prev_mask, p), INF) + matrix[u, v]
                        if c < best_cost:
                            best_cost = c
                            best_p = p
                if best_cost < INF:
                    dp[(mask, j)] = best_cost
                    parent[(mask, j)] = best_p

    full_mask = (1 << k) - 1
    best_total = INF
    last_node_idx = -1
    for i, node in enumerate(subset_indices):
        c = dp.get((full_mask, i), INF) + matrix[node, 0]
        if c < best_total:
            best_total = c
            last_node_idx = i

    # Reconstruct tour
    curr_mask = full_mask
    curr_i = last_node_idx
    path_rev = []
    while curr_i != -1:
        path_rev.append(subset_indices[curr_i])
        prev_i = parent.get((curr_mask, curr_i), -1)
        curr_mask ^= (1 << curr_i)
        curr_i = prev_i

    tour = [0] + list(reversed(path_rev)) + [0]
    return float(best_total), tour


def exact_cvrp_set_partitioning(
    N: int,
    demands: List[int],
    vehicle_capacity: float,
    num_vehicles: int,
    matrix: np.ndarray
) -> Dict[str, Any]:
    """Computes exact CVRP global optimum using Set Partitioning DP over Held-Karp sub-tour costs."""
    t0 = time.perf_counter()
    customer_indices = list(range(1, N + 1))
    
    # Precompute TSP cost for every feasible subset (demand <= vehicle_capacity)
    INF = 1e12
    subset_costs = {}
    subset_tours = {}

    for r in range(1, N + 1):
        for combo in itertools.combinations(customer_indices, r):
            tot_dem = sum(demands[i] for i in combo)
            if tot_dem <= vehicle_capacity + 1e-6:
                mask = 0
                for c in combo:
                    mask |= (1 << (c - 1))
                cost, tour = held_karp_exact_tsp(list(combo), matrix)
                subset_costs[mask] = cost
                subset_tours[mask] = tour

    # DP over partitions: min_cost[(mask, vehicles_used)]
    full_mask = (1 << N) - 1
    dp_cost = {0: 0.0}
    dp_routes = {0: []}

    for v in range(1, num_vehicles + 1):
        next_dp_cost = dict(dp_cost)
        next_dp_routes = dict(dp_routes)
        for submask, cost in subset_costs.items():
            for state_mask, current_cost in dp_cost.items():
                if (state_mask & submask) == 0:
                    new_mask = state_mask | submask
                    new_cost = current_cost + cost
                    if new_cost < next_dp_cost.get(new_mask, INF):
                        next_dp_cost[new_mask] = new_cost
                        next_dp_routes[new_mask] = dp_routes[state_mask] + [subset_tours[submask]]
        dp_cost = next_dp_cost
        dp_routes = next_dp_routes

    t_elapsed = (time.perf_counter() - t0) * 1000.0
    opt_cost = dp_cost.get(full_mask, None)

    return {
        "optimal_distance_km": round(opt_cost, 4) if opt_cost is not None else None,
        "is_feasible": opt_cost is not None,
        "routes": dp_routes.get(full_mask, []),
        "runtime_ms": t_elapsed
    }


def run_exact_validation():
    """Runs exact benchmark for small scales N in [3, 4, 6, 8, 10]."""
    p_graph = 'backend/data/processed/road_graph_manhatten.pickle'
    with open(p_graph, 'rb') as f:
        G = pickle.load(f)
    for u, v, k, d in G.edges(keys=True, data=True):
        d['length'] = float(d.get('length', 1.0))
    largest_scc_nodes = max(nx.strongly_connected_components(G), key=len)
    G_scc = G.subgraph(largest_scc_nodes).copy()
    scc_nodes_list = sorted(list(G_scc.nodes()))

    classical_solver = ClassicalVRPSolver()
    qiga_solver = QIGASolver(pop_size=30, max_generations=50)
    quantum_solver = QuantumVRPSolver()
    rbqcd_decomposer = RBQCDDecomposer(max_qubits=16)

    scales = [3, 4, 6, 8, 10]
    seeds = [101, 202, 303, 404, 505]
    vehicle_capacity = 10.0

    records = []
    target_dir = r"C:\Users\DELL\.gemini\antigravity\brain\aba14f7b-722c-4648-8da1-214dc979ac26\scratch\phase6_benchmark"
    os.makedirs(target_dir, exist_ok=True)

    print("=================================================================")
    print("Starting Small-Instance Exact Global Optimum Benchmark (Held-Karp)")
    print("=================================================================")

    for N in scales:
        for seed in seeds:
            rng = np.random.default_rng(seed)
            chosen_nodes = rng.choice(scc_nodes_list, size=N + 1, replace=False)
            depot_node = chosen_nodes[0]
            cust_nodes = chosen_nodes[1:]

            all_nodes = [depot_node] + list(cust_nodes)
            K_nodes = len(all_nodes)
            matrix = np.zeros((K_nodes, K_nodes), dtype=float)
            for i, src in enumerate(all_nodes):
                lengths = nx.single_source_dijkstra_path_length(G_scc, src, weight='length')
                for j, dst in enumerate(all_nodes):
                    if i != j:
                        matrix[i, j] = lengths.get(dst, 100000.0) / 1000.0

            depot = {"id": "depot", "demand": 0}
            customers = []
            location_indices = {"depot": 0}
            demands_list = [0]
            for idx, node in enumerate(cust_nodes):
                cid = f"cust_{idx + 1}"
                dem = int(rng.integers(1, 4))
                customers.append({"id": cid, "demand": dem})
                location_indices[cid] = idx + 1
                demands_list.append(dem)

            total_demand = sum(demands_list)
            num_vehicles = max(2, int(np.ceil(total_demand / vehicle_capacity)))

            # 1. Exact Global Optimum
            exact_res = exact_cvrp_set_partitioning(N, demands_list, vehicle_capacity, num_vehicles, matrix)
            E_exact = exact_res["optimal_distance_km"]

            # 2. OR-Tools GLS
            t0 = time.perf_counter()
            ort = classical_solver.solve_ortools(
                distance_matrix=matrix,
                num_vehicles=num_vehicles,
                depot=0,
                demands=demands_list,
                vehicle_capacities=[int(vehicle_capacity)] * num_vehicles
            )
            t_ort = (time.perf_counter() - t0) * 1000.0
            d_ort = ort["total_distance_km"]

            # 3. CW + 2-opt
            t0 = time.perf_counter()
            cw = classical_solver.solve_two_opt(
                distance_matrix=matrix,
                num_vehicles=num_vehicles,
                depot=0,
                demands=demands_list,
                vehicle_capacities=[int(vehicle_capacity)] * num_vehicles
            )
            t_cw = (time.perf_counter() - t0) * 1000.0
            d_cw = cw["total_distance_km"]

            # 4. QIGA
            t0 = time.perf_counter()
            qiga = qiga_solver.solve(
                distance_matrix=matrix,
                num_vehicles=num_vehicles,
                depot=0,
                demands=demands_list,
                vehicle_capacities=[int(vehicle_capacity)] * num_vehicles
            )
            t_qiga = (time.perf_counter() - t0) * 1000.0
            d_qiga = qiga["total_distance_km"]

            # 5. Baseline QAOA (truncated)
            t0 = time.perf_counter()
            qaoa_base = quantum_solver.solve(
                distance_matrix=matrix,
                num_vehicles=num_vehicles,
                depot=0,
                demands=[float(d) for d in demands_list],
                vehicle_capacity=float(vehicle_capacity)
            )
            t_qaoa = (time.perf_counter() - t0) * 1000.0
            d_qaoa = qaoa_base.get("total_distance_km", 0.0)

            # 6. RB-QCD (Proposed)
            t0 = time.perf_counter()
            rbqcd = rbqcd_decomposer.decompose_and_solve(
                depot=depot,
                customers=customers,
                matrix=matrix,
                num_vehicles=num_vehicles,
                vehicle_capacity=vehicle_capacity,
                location_indices=location_indices
            )
            t_rbqcd = (time.perf_counter() - t0) * 1000.0
            d_rbqcd = rbqcd["total_distance"]

            solvers_data = [
                ("Exact Global Optimum", E_exact, exact_res["runtime_ms"], 1.0, 0.0),
                ("OR-Tools GLS", d_ort, t_ort, d_ort / E_exact, (d_ort - E_exact) / E_exact * 100.0),
                ("Clarke-Wright + 2-opt", d_cw, t_cw, d_cw / E_exact, (d_cw - E_exact) / E_exact * 100.0),
                ("QIGA", d_qiga, t_qiga, d_qiga / E_exact, (d_qiga - E_exact) / E_exact * 100.0),
                ("Baseline QAOA", d_qaoa, t_qaoa, d_qaoa / E_exact, (d_qaoa - E_exact) / E_exact * 100.0),
                ("RB-QCD (Proposed)", d_rbqcd, t_rbqcd, d_rbqcd / E_exact, (d_rbqcd - E_exact) / E_exact * 100.0),
            ]

            for s_name, dist, runtime, alpha, gap in solvers_data:
                records.append({
                    "N": N,
                    "seed": seed,
                    "algorithm": s_name,
                    "total_distance_km": round(dist, 4),
                    "runtime_ms": round(runtime, 2),
                    "optimal_distance_km": round(E_exact, 4),
                    "approximation_ratio": round(alpha, 4),
                    "optimality_gap_pct": round(gap, 2)
                })

            print(f"  [N={N:2d}, Seed={seed}] Exact={E_exact:.2f}km | ORT={d_ort:.2f}km (alpha={d_ort/E_exact:.2f}) | RBQCD={d_rbqcd:.2f}km (alpha={d_rbqcd/E_exact:.2f}) | QAOA_Base={d_qaoa:.2f}km (alpha={d_qaoa/E_exact:.2f})")

    df_exact = pd.DataFrame(records)
    out_csv = os.path.join(target_dir, "exact_small_instance_results.csv")
    df_exact.to_csv(out_csv, index=False)
    print(f"\nExact validation completed. Saved to {out_csv}")


if __name__ == "__main__":
    run_exact_validation()

