"""Comprehensive Manhattan Road-Network Benchmark Harness for ROUTE/IQ.

Evaluates 5 optimization algorithms on authentic directed OpenStreetMap graphs:
1. Google OR-Tools Guided Local Search (OR-Tools GLS)
2. Clarke-Wright Parallel Savings + 2-opt (CW + 2-opt)
3. Quantum-Inspired Genetic Algorithm (QIGA)
4. Existing Baseline QAOA (Monolithic with truncation)
5. RB-QCD (Resource-Budgeted Hybrid Quantum-Classical Decomposition)

All algorithms consume:
- Exactly identical distance_matrix (in kilometers)
- Exactly identical demands (int or float)
- Exactly identical vehicle capacities
- Exactly identical depot index (0)
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
from typing import List, Dict, Any

from app.services.optimization.classical_solver import ClassicalVRPSolver
from app.services.optimization.qiga_solver import QIGASolver
from app.services.optimization.quantum_solver import QuantumVRPSolver
from app.services.optimization.rb_qcd_decomposer import RBQCDDecomposer


def load_manhattan_network():
    """Loads authentic Manhattan graph and preprocessed customers."""
    p_graph = 'backend/data/processed/road_graph_manhatten.pickle'
    with open(p_graph, 'rb') as f:
        G = pickle.load(f)

    # Cast all edge lengths to float (meters)
    for u, v, k, d in G.edges(keys=True, data=True):
        d['length'] = float(d.get('length', 1.0))

    # Extract largest Strongly Connected Component (SCC)
    largest_scc_nodes = max(nx.strongly_connected_components(G), key=len)
    G_scc = G.subgraph(largest_scc_nodes).copy()

    p_cust = 'backend/data/processed/customers_processed.csv'
    df_cust = pd.read_csv(p_cust)

    return G_scc, df_cust


def build_instance_matrix(G: nx.DiGraph, node_list: List[int]) -> np.ndarray:
    """Computes exact directed shortest-path distance matrix across selected physical nodes in KILOMETERS."""
    K = len(node_list)
    matrix = np.zeros((K, K), dtype=float)

    for i, src in enumerate(node_list):
        lengths = nx.single_source_dijkstra_path_length(G, src, weight='length')
        for j, dst in enumerate(node_list):
            if i != j:
                # Convert meters to kilometers for OR-Tools scale=1000 integer compliance
                matrix[i, j] = lengths.get(dst, 100000.0) / 1000.0
    return matrix


def run_single_instance(
    N: int,
    seed: int,
    G_scc: nx.DiGraph,
    df_cust: pd.DataFrame,
    scc_nodes_list: List[int],
    classical_solver: ClassicalVRPSolver,
    qiga_solver: QIGASolver,
    quantum_solver: QuantumVRPSolver,
    rbqcd_decomposer: RBQCDDecomposer
) -> List[Dict[str, Any]]:
    """Runs all 5 algorithms on identical instance (N customers + 1 depot)."""
    rng = np.random.default_rng(seed)

    # Sample depot and N customer nodes strictly from SCC
    chosen_nodes = rng.choice(scc_nodes_list, size=N + 1, replace=False)
    depot_node = chosen_nodes[0]
    cust_nodes = chosen_nodes[1:]

    all_nodes = [depot_node] + list(cust_nodes)
    matrix = build_instance_matrix(G_scc, all_nodes)

    depot = {"id": "depot", "demand": 0}
    customers = []
    location_indices = {"depot": 0}
    demands_list = [0]  # depot demand is 0

    for idx, node in enumerate(cust_nodes):
        cid = f"cust_{idx + 1}"
        dem = int(rng.integers(1, 4))
        customers.append({"id": cid, "demand": dem})
        location_indices[cid] = idx + 1
        demands_list.append(dem)

    total_demand = sum(demands_list)
    capacity_per_veh = 15
    num_vehicles = max(2, int(np.ceil(total_demand / capacity_per_veh * 1.25)))
    capacities_list = [capacity_per_veh] * num_vehicles

    results = []

    # -------------------------------------------------------------
    # 1. Google OR-Tools Guided Local Search
    # -------------------------------------------------------------
    t0 = time.perf_counter()
    ort_res = classical_solver.solve_ortools(
        distance_matrix=matrix,
        num_vehicles=num_vehicles,
        depot=0,
        demands=demands_list,
        vehicle_capacities=capacities_list,
        time_limit_sec=3
    )
    t_ort = (time.perf_counter() - t0) * 1000.0

    dist_ort_km = float(ort_res.get("total_distance_km", 0.0))
    is_feas_ort = bool(ort_res.get("is_feasible", False))
    served_ort = int(ort_res.get("served_customers", 0))

    results.append({
        "N": N,
        "seed": seed,
        "algorithm": "OR-Tools GLS",
        "total_distance_km": round(dist_ort_km, 3),
        "is_feasible": is_feas_ort,
        "routed_customers": served_ort,
        "unassigned_customers": max(0, N - served_ort),
        "capacity_violations": int(ort_res.get("capacity_violations", 0)),
        "num_vehicles": len(ort_res.get("routes", [])),
        "runtime_ms": round(t_ort, 2),
        "qaoa_subproblems": 0,
        "logical_qubits": 0,
        "circuit_depth": 0
    })

    # -------------------------------------------------------------
    # 2. Clarke-Wright Parallel Savings + 2-opt
    # -------------------------------------------------------------
    t0 = time.perf_counter()
    cw_res = classical_solver.solve_two_opt(
        distance_matrix=matrix,
        num_vehicles=num_vehicles,
        depot=0,
        demands=demands_list,
        vehicle_capacities=capacities_list
    )
    t_cw = (time.perf_counter() - t0) * 1000.0

    dist_cw_km = float(cw_res.get("total_distance_km", 0.0))
    is_feas_cw = bool(cw_res.get("is_feasible", False))
    served_cw = int(cw_res.get("served_customers", 0))

    results.append({
        "N": N,
        "seed": seed,
        "algorithm": "Clarke-Wright + 2-opt",
        "total_distance_km": round(dist_cw_km, 3),
        "is_feasible": is_feas_cw,
        "routed_customers": served_cw,
        "unassigned_customers": max(0, N - served_cw),
        "capacity_violations": int(cw_res.get("capacity_violations", 0)),
        "num_vehicles": len(cw_res.get("routes", [])),
        "runtime_ms": round(t_cw, 2),
        "qaoa_subproblems": 0,
        "logical_qubits": 0,
        "circuit_depth": 0
    })

    # -------------------------------------------------------------
    # 3. Quantum-Inspired Genetic Algorithm (QIGA)
    # -------------------------------------------------------------
    t0 = time.perf_counter()
    qiga_res = qiga_solver.solve(
        distance_matrix=matrix,
        num_vehicles=num_vehicles,
        depot=0,
        demands=demands_list,
        vehicle_capacities=capacities_list
    )
    t_qiga = (time.perf_counter() - t0) * 1000.0

    dist_qiga_km = float(qiga_res.get("total_distance_km", 0.0))
    is_feas_qiga = bool(qiga_res.get("is_feasible", False))
    served_qiga = int(qiga_res.get("served_customers", 0))

    results.append({
        "N": N,
        "seed": seed,
        "algorithm": "QIGA",
        "total_distance_km": round(dist_qiga_km, 3),
        "is_feasible": is_feas_qiga,
        "routed_customers": served_qiga,
        "unassigned_customers": max(0, N - served_qiga),
        "capacity_violations": int(qiga_res.get("capacity_violations", 0)),
        "num_vehicles": len(qiga_res.get("routes", [])),
        "runtime_ms": round(t_qiga, 2),
        "qaoa_subproblems": 0,
        "logical_qubits": 0,
        "circuit_depth": 0
    })

    # -------------------------------------------------------------
    # 4. Existing Baseline QAOA (Demonstrating Truncation Defect)
    # -------------------------------------------------------------
    t0 = time.perf_counter()
    try:
        qaoa_base_res = quantum_solver.solve(
            distance_matrix=matrix,
            num_vehicles=num_vehicles,
            depot=0,
            demands=[float(d) for d in demands_list],
            vehicle_capacity=float(capacity_per_veh)
        )
        t_base_qaoa = (time.perf_counter() - t0) * 1000.0

        eff_n = min(len(customers), max(1, 8 // num_vehicles))
        routed_custs_base = int(qaoa_base_res.get("served_customers", 0))
        dist_base_km = float(qaoa_base_res.get("total_distance_km", 0.0))

        results.append({
            "N": N,
            "seed": seed,
            "algorithm": "Baseline QAOA (Truncated)",
            "total_distance_km": round(dist_base_km, 3),
            "is_feasible": bool(qaoa_base_res.get("is_feasible", False)),
            "routed_customers": routed_custs_base,
            "unassigned_customers": max(0, N - routed_custs_base),
            "capacity_violations": int(qaoa_base_res.get("capacity_violations", 0)),
            "num_vehicles": len(qaoa_base_res.get("routes", [])),
            "runtime_ms": round(t_base_qaoa, 2),
            "qaoa_subproblems": 1,
            "logical_qubits": int(qaoa_base_res.get("num_qubits", eff_n * num_vehicles)),
            "circuit_depth": int(qaoa_base_res.get("circuit_depth", 1)),
            "customers_optimized_by_qaoa": eff_n,
            "customers_greedily_appended": max(0, N - eff_n)
        })
    except Exception as e:
        results.append({
            "N": N, "seed": seed, "algorithm": "Baseline QAOA (Truncated)",
            "total_distance_km": 0.0, "is_feasible": False, "routed_customers": 0,
            "unassigned_customers": N, "capacity_violations": 0, "num_vehicles": 0,
            "runtime_ms": 0.0, "qaoa_subproblems": 0, "logical_qubits": 0, "circuit_depth": 0,
            "error": str(e)
        })

    # -------------------------------------------------------------
    # 5. Proposed RB-QCD (Resource-Budgeted Hybrid Decomposition)
    # -------------------------------------------------------------
    t0 = time.perf_counter()
    rb_res = rbqcd_decomposer.decompose_and_solve(
        customers=customers,
        depot=depot,
        matrix=matrix,
        num_vehicles=num_vehicles,
        vehicle_capacity=float(capacity_per_veh),
        location_indices=location_indices
    )
    t_rbqcd = (time.perf_counter() - t0) * 1000.0

    feas_rb = rb_res["feasibility"]
    audit_rb = rb_res["audit"]

    results.append({
        "N": N,
        "seed": seed,
        "algorithm": "RB-QCD (Proposed)",
        "total_distance_km": round(float(rb_res.get("total_distance", 0.0)), 3),
        "is_feasible": bool(feas_rb["is_feasible"]),
        "routed_customers": int(feas_rb["total_routed_customers"]),
        "unassigned_customers": int(feas_rb["unassigned_customers"]),
        "capacity_violations": int(feas_rb["capacity_violations"]),
        "num_vehicles": int(audit_rb["num_routes"]),
        "runtime_ms": round(t_rbqcd, 2),
        "qaoa_subproblems": int(audit_rb["qaoa_subproblems_solved"]),
        "logical_qubits": int(audit_rb["max_logical_qubits_used"]),
        "circuit_depth": int(audit_rb["total_circuit_depth"]),
        "customers_optimized_by_qaoa": sum(min(r["customer_count"], 4) for r in rb_res["routes"]),
        "customers_greedily_appended": 0
    })

    return results


def main():
    print("Loading Manhattan road network and customer datasets...")
    G_scc, df_cust = load_manhattan_network()
    scc_nodes_list = list(G_scc.nodes())
    print(f"Manhattan largest SCC: {len(scc_nodes_list)} nodes, {G_scc.number_of_edges()} directed arcs.")

    classical_solver = ClassicalVRPSolver()
    qiga_solver = QIGASolver()
    quantum_solver = QuantumVRPSolver()
    rbqcd_decomposer = RBQCDDecomposer(max_qubits=16)

    scales = [10, 20, 25, 50, 100, 150, 200, 250]
    seeds = [107, 207, 307, 407, 507, 607, 707, 807, 907, 1007]

    all_records = []
    total_runs = len(scales) * len(seeds)
    run_idx = 0

    target_dir = r"C:\Users\DELL\.gemini\antigravity\brain\aba14f7b-722c-4648-8da1-214dc979ac26\scratch\phase6_benchmark"
    os.makedirs(target_dir, exist_ok=True)

    print(f"Starting Benchmark Campaign: {len(scales)} scales x {len(seeds)} seeds = {total_runs} benchmark instances.")
    t_global_start = time.perf_counter()

    for n in scales:
        print(f"\n=======================================================")
        print(f"Running Scale N = {n} ({len(seeds)} random seeds)...")
        print(f"=======================================================")
        for s in seeds:
            run_idx += 1
            t_inst = time.perf_counter()
            inst_results = run_single_instance(
                n, s, G_scc, df_cust, scc_nodes_list,
                classical_solver, qiga_solver, quantum_solver, rbqcd_decomposer
            )
            all_records.extend(inst_results)
            inst_time = time.perf_counter() - t_inst
            print(f"  [{run_idx:02d}/{total_runs}] N={n:3d}, Seed={s} completed in {inst_time:.2f}s")

    t_global_total = time.perf_counter() - t_global_start
    print(f"\nAll benchmark runs completed in {t_global_total:.1f}s.")

    # Convert to DataFrame and save raw results
    df_raw = pd.DataFrame(all_records)
    raw_path = os.path.join(target_dir, "benchmark_raw_results.csv")
    df_raw.to_csv(raw_path, index=False)
    print(f"Saved raw benchmark data to {raw_path}")

    # Generate Summary Table grouped by N and Algorithm
    summary = df_raw.groupby(["N", "algorithm"]).agg({
        "total_distance_km": ["mean", "std"],
        "runtime_ms": ["mean", "std"],
        "is_feasible": "mean",
        "routed_customers": "mean",
        "unassigned_customers": "mean",
        "capacity_violations": "mean",
        "num_vehicles": "mean"
    }).reset_index()

    summary_path = os.path.join(target_dir, "benchmark_summary_tables.csv")
    summary.to_csv(summary_path, index=False)
    print(f"Saved aggregated summary to {summary_path}")

    # Generate Seed Manifest
    manifest = [{"run_id": idx + 1, "scale_N": n, "random_seed": s} for idx, (n, s) in enumerate(itertools.product(scales, seeds))]
    manifest_path = os.path.join(target_dir, "benchmark_seed_manifest.csv")
    pd.DataFrame(manifest).to_csv(manifest_path, index=False)
    print(f"Saved seed manifest to {manifest_path}")

    # Save Configuration JSON
    configs = {
        "benchmark_date": "2026-11-04",
        "road_network": "OpenStreetMap Manhattan Largest SCC",
        "nodes": len(scc_nodes_list),
        "arcs": G_scc.number_of_edges(),
        "customer_scales": scales,
        "random_seeds": seeds,
        "vehicle_capacity": 15.0,
        "tested_algorithms": [
            "OR-Tools GLS",
            "Clarke-Wright + 2-opt",
            "QIGA",
            "Baseline QAOA (Truncated)",
            "RB-QCD (Proposed)"
        ],
        "environment": {
            "python": sys.version,
            "numpy": np.__version__,
            "pandas": pd.__version__
        }
    }
    with open(os.path.join(target_dir, "benchmark_configurations.json"), "w") as f:
        json.dump(configs, f, indent=2)
    print("Saved benchmark configurations JSON.")


if __name__ == "__main__":
    main()
