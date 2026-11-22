"""
Phase I Comprehensive Benchmark: Evaluating QGAR against Baselines & Ablations.

Evaluates 8 distinct algorithmic configurations on the directed Manhattan SCC graph:
1. Phase H Baseline (Spark + QAOA, unconditioned)
2. Spatial Baseline (Spark + Classical DP, No QAOA)
3. Ablation 1: QAOA + Quality Selection only (unconditioned adoption)
4. Ablation 2: QAOA + Adaptive Influence only (greedy candidate)
5. Full Proposed QGAR (Quality Selection + Adaptive Influence + Crossing Avoidance)
6. RB-QCD Baseline Decomposer
7. Google OR-Tools Guided Local Search (GLS)
8. Clarke-Wright + 2-opt

Telemetry captured per instance:
- Directed route distance (km), feasibility, capacity violations, customer preservation (0 drop).
- Unbundled timings: Spark, QAOA circuit, QAOA optimizer, Reconstruction, Total wall-clock time.
- Quantum metrics: Subproblems solved, qubits, circuit depth, lambda_eff, crossings prevented, candidate diversity.
"""

import sys
sys.path.insert(0, 'backend')

import os
import time
import json
import itertools
import numpy as np
import pandas as pd
import networkx as nx
from typing import List, Dict, Any
import pickle

from app.services.optimization.classical_solver import ClassicalVRPSolver
from app.services.optimization.quantum_solver import QuantumVRPSolver
from app.services.optimization.rb_qcd_decomposer import RBQCDDecomposer
from app.services.optimization.qgar_pipeline import QuantumGuidedAdaptiveRouter
from app.services.bigdata_pipeline import ensure_spark_environment

def load_manhattan_network():
    p_graph = 'backend/data/processed/road_graph_manhatten.pickle'
    with open(p_graph, 'rb') as f:
        G = pickle.load(f)

    for u, v, k, d in G.edges(keys=True, data=True):
        d['length'] = float(d.get('length', 1.0))

    largest_scc_nodes = max(nx.strongly_connected_components(G), key=len)
    G_scc = G.subgraph(largest_scc_nodes).copy()

    p_cust = 'backend/data/processed/customers_processed.csv'
    df_cust = pd.read_csv(p_cust)

    return G_scc, df_cust

def build_instance_matrix(G: nx.DiGraph, node_list: List[int]) -> np.ndarray:
    K = len(node_list)
    matrix = np.zeros((K, K), dtype=float)
    for i, src in enumerate(node_list):
        lengths = nx.single_source_dijkstra_path_length(G, src, weight='length')
        for j, dst in enumerate(node_list):
            if i != j:
                matrix[i, j] = lengths.get(dst, 100000.0) / 1000.0
    return matrix

def run_single_instance(
    N: int,
    seed: int,
    G_scc: nx.DiGraph,
    scc_nodes_list: List[int],
    classical_solver: ClassicalVRPSolver,
    rbqcd_decomposer: RBQCDDecomposer,
    qgar_router: QuantumGuidedAdaptiveRouter,
) -> List[Dict[str, Any]]:
    rng = np.random.default_rng(seed)

    chosen_nodes = rng.choice(scc_nodes_list, size=N + 1, replace=False)
    depot_node = chosen_nodes[0]
    cust_nodes = chosen_nodes[1:]

    all_nodes = [depot_node] + list(cust_nodes)
    matrix = build_instance_matrix(G_scc, all_nodes)

    depot = {
        "id": "depot",
        "latitude": float(G_scc.nodes[depot_node].get('y', 40.7580)),
        "longitude": float(G_scc.nodes[depot_node].get('x', -73.9855)),
        "demand": 0
    }
    customers = []
    location_indices = {"depot": 0}
    demands_list = [0]

    for idx, node in enumerate(cust_nodes):
        cid = f"cust_{idx + 1}"
        dem = int(rng.integers(1, 4))
        customers.append({
            "id": cid,
            "customer_id": cid,
            "latitude": float(G_scc.nodes[node].get('y', 40.7580)),
            "longitude": float(G_scc.nodes[node].get('x', -73.9855)),
            "demand": dem
        })
        location_indices[cid] = idx + 1
        demands_list.append(dem)

    capacity_per_veh = 15
    total_demand = sum(demands_list)
    num_vehicles = max(2, int(np.ceil(total_demand / capacity_per_veh * 1.25)))
    capacities_list = [int(capacity_per_veh)] * num_vehicles

    results = []

    # -------------------------------------------------------------
    # 1. Full Proposed QGAR (Quality Selection + Adaptive Influence + Crossing Avoidance)
    # -------------------------------------------------------------
    t0 = time.perf_counter()
    res_qgar = qgar_router.optimize_delivery_campaign(
        customers=customers, depot=depot, distance_matrix=matrix,
        vehicle_capacity=float(capacity_per_veh), location_indices=location_indices,
        enable_qaoa=True, enable_adaptive_influence=True, enable_quality_selection=True
    )
    t_qgar = (time.perf_counter() - t0) * 1000.0
    tele_qgar = res_qgar["telemetry"]
    feas_qgar = res_qgar["feasibility"]

    results.append({
        "N": N, "seed": seed, "algorithm": "Full QGAR (Proposed)",
        "total_distance_km": res_qgar["total_distance_km"],
        "is_feasible": feas_qgar["is_feasible"],
        "routed_customers": feas_qgar["total_routed_customers"],
        "unassigned_customers": feas_qgar["unassigned_customers"],
        "capacity_violations": feas_qgar["capacity_violations"],
        "num_vehicles": res_qgar["num_vehicles"],
        "runtime_total_ms": round(t_qgar, 2),
        "runtime_spark_ms": tele_qgar["runtime_spark_ms"],
        "runtime_qaoa_circuit_ms": tele_qgar["runtime_qaoa_circuit_ms"],
        "runtime_qaoa_opt_ms": tele_qgar["runtime_qaoa_opt_ms"],
        "runtime_reconstruction_ms": tele_qgar["runtime_reconstruction_ms"],
        "qaoa_subproblems": tele_qgar["qaoa_subproblems_solved"],
        "logical_qubits": tele_qgar["max_logical_qubits_used"],
        "circuit_depth": tele_qgar["total_circuit_depth"],
        "lambda_mean": tele_qgar["quantum_influence_lambda_mean"],
        "qaoa_accepted": tele_qgar["qaoa_backbones_accepted"],
        "spatial_retained": tele_qgar["spatial_backbones_retained"],
        "diversity_mean": tele_qgar["candidate_diversity_mean"],
        "crossings_prevented": tele_qgar["crossings_prevented_total"]
    })

    # -------------------------------------------------------------
    # 2. Phase H Baseline (Spark + QAOA, unconditioned adoption)
    # -------------------------------------------------------------
    t0 = time.perf_counter()
    res_phase_h = qgar_router.optimize_delivery_campaign(
        customers=customers, depot=depot, distance_matrix=matrix,
        vehicle_capacity=float(capacity_per_veh), location_indices=location_indices,
        enable_qaoa=True, enable_adaptive_influence=False, enable_quality_selection=False
    )
    t_phase_h = (time.perf_counter() - t0) * 1000.0
    tele_ph = res_phase_h["telemetry"]
    feas_ph = res_phase_h["feasibility"]

    results.append({
        "N": N, "seed": seed, "algorithm": "Phase H (Spark + QAOA)",
        "total_distance_km": res_phase_h["total_distance_km"],
        "is_feasible": feas_ph["is_feasible"],
        "routed_customers": feas_ph["total_routed_customers"],
        "unassigned_customers": feas_ph["unassigned_customers"],
        "capacity_violations": feas_ph["capacity_violations"],
        "num_vehicles": res_phase_h["num_vehicles"],
        "runtime_total_ms": round(t_phase_h, 2),
        "runtime_spark_ms": tele_ph["runtime_spark_ms"],
        "runtime_qaoa_circuit_ms": tele_ph["runtime_qaoa_circuit_ms"],
        "runtime_qaoa_opt_ms": tele_ph["runtime_qaoa_opt_ms"],
        "runtime_reconstruction_ms": tele_ph["runtime_reconstruction_ms"],
        "qaoa_subproblems": tele_ph["qaoa_subproblems_solved"],
        "logical_qubits": tele_ph["max_logical_qubits_used"],
        "circuit_depth": tele_ph["total_circuit_depth"],
        "lambda_mean": 1.0, "qaoa_accepted": tele_ph["qaoa_subproblems_solved"],
        "spatial_retained": 0, "diversity_mean": 1.0, "crossings_prevented": 0
    })

    # -------------------------------------------------------------
    # 3. Spatial Baseline (Spark + Classical DP, No QAOA)
    # -------------------------------------------------------------
    t0 = time.perf_counter()
    res_spatial = qgar_router.optimize_delivery_campaign(
        customers=customers, depot=depot, distance_matrix=matrix,
        vehicle_capacity=float(capacity_per_veh), location_indices=location_indices,
        enable_qaoa=False
    )
    t_spatial = (time.perf_counter() - t0) * 1000.0
    tele_sp = res_spatial["telemetry"]
    feas_sp = res_spatial["feasibility"]

    results.append({
        "N": N, "seed": seed, "algorithm": "Spatial Baseline (No QAOA)",
        "total_distance_km": res_spatial["total_distance_km"],
        "is_feasible": feas_sp["is_feasible"],
        "routed_customers": feas_sp["total_routed_customers"],
        "unassigned_customers": feas_sp["unassigned_customers"],
        "capacity_violations": feas_sp["capacity_violations"],
        "num_vehicles": res_spatial["num_vehicles"],
        "runtime_total_ms": round(t_spatial, 2),
        "runtime_spark_ms": tele_sp["runtime_spark_ms"],
        "runtime_qaoa_circuit_ms": 0.0,
        "runtime_qaoa_opt_ms": 0.0,
        "runtime_reconstruction_ms": tele_sp["runtime_reconstruction_ms"],
        "qaoa_subproblems": 0, "logical_qubits": 0, "circuit_depth": 0,
        "lambda_mean": 0.0, "qaoa_accepted": 0, "spatial_retained": res_spatial["num_vehicles"],
        "diversity_mean": 0.0, "crossings_prevented": 0
    })

    # -------------------------------------------------------------
    # 4. Ablation 1: QAOA + Quality Selection Only (Unconditioned)
    # -------------------------------------------------------------
    t0 = time.perf_counter()
    res_qual = qgar_router.optimize_delivery_campaign(
        customers=customers, depot=depot, distance_matrix=matrix,
        vehicle_capacity=float(capacity_per_veh), location_indices=location_indices,
        enable_qaoa=True, enable_adaptive_influence=False, enable_quality_selection=True
    )
    t_qual = (time.perf_counter() - t0) * 1000.0
    tele_q = res_qual["telemetry"]

    results.append({
        "N": N, "seed": seed, "algorithm": "Ablation: Quality-Selection Only",
        "total_distance_km": res_qual["total_distance_km"],
        "is_feasible": res_qual["feasibility"]["is_feasible"],
        "routed_customers": res_qual["feasibility"]["total_routed_customers"],
        "unassigned_customers": res_qual["feasibility"]["unassigned_customers"],
        "capacity_violations": res_qual["feasibility"]["capacity_violations"],
        "num_vehicles": res_qual["num_vehicles"],
        "runtime_total_ms": round(t_qual, 2),
        "runtime_spark_ms": tele_q["runtime_spark_ms"],
        "runtime_qaoa_circuit_ms": tele_q["runtime_qaoa_circuit_ms"],
        "runtime_qaoa_opt_ms": tele_q["runtime_qaoa_opt_ms"],
        "runtime_reconstruction_ms": tele_q["runtime_reconstruction_ms"],
        "qaoa_subproblems": tele_q["qaoa_subproblems_solved"],
        "logical_qubits": tele_q["max_logical_qubits_used"],
        "circuit_depth": tele_q["total_circuit_depth"],
        "lambda_mean": 1.0, "qaoa_accepted": tele_q["qaoa_subproblems_solved"],
        "spatial_retained": 0, "diversity_mean": tele_q["candidate_diversity_mean"],
        "crossings_prevented": 0
    })

    # -------------------------------------------------------------
    # 5. Ablation 2: QAOA + Adaptive Influence Only (Greedy Bitstring)
    # -------------------------------------------------------------
    t0 = time.perf_counter()
    res_adapt = qgar_router.optimize_delivery_campaign(
        customers=customers, depot=depot, distance_matrix=matrix,
        vehicle_capacity=float(capacity_per_veh), location_indices=location_indices,
        enable_qaoa=True, enable_adaptive_influence=True, enable_quality_selection=False
    )
    t_adapt = (time.perf_counter() - t0) * 1000.0
    tele_a = res_adapt["telemetry"]

    results.append({
        "N": N, "seed": seed, "algorithm": "Ablation: Adaptive-Influence Only",
        "total_distance_km": res_adapt["total_distance_km"],
        "is_feasible": res_adapt["feasibility"]["is_feasible"],
        "routed_customers": res_adapt["feasibility"]["total_routed_customers"],
        "unassigned_customers": res_adapt["feasibility"]["unassigned_customers"],
        "capacity_violations": res_adapt["feasibility"]["capacity_violations"],
        "num_vehicles": res_adapt["num_vehicles"],
        "runtime_total_ms": round(t_adapt, 2),
        "runtime_spark_ms": tele_a["runtime_spark_ms"],
        "runtime_qaoa_circuit_ms": tele_a["runtime_qaoa_circuit_ms"],
        "runtime_qaoa_opt_ms": tele_a["runtime_qaoa_opt_ms"],
        "runtime_reconstruction_ms": tele_a["runtime_reconstruction_ms"],
        "qaoa_subproblems": tele_a["qaoa_subproblems_solved"],
        "logical_qubits": tele_a["max_logical_qubits_used"],
        "circuit_depth": tele_a["total_circuit_depth"],
        "lambda_mean": tele_a["quantum_influence_lambda_mean"],
        "qaoa_accepted": tele_a["qaoa_backbones_accepted"],
        "spatial_retained": tele_a["spatial_backbones_retained"],
        "diversity_mean": 1.0,
        "crossings_prevented": tele_a["crossings_prevented_total"]
    })

    # -------------------------------------------------------------
    # 6. RB-QCD Baseline Decomposer
    # -------------------------------------------------------------
    t0 = time.perf_counter()
    rb_res = rbqcd_decomposer.decompose_and_solve(
        customers=customers, depot=depot, matrix=matrix,
        num_vehicles=num_vehicles, vehicle_capacity=float(capacity_per_veh),
        location_indices=location_indices
    )
    t_rbqcd = (time.perf_counter() - t0) * 1000.0

    results.append({
        "N": N, "seed": seed, "algorithm": "RB-QCD Baseline",
        "total_distance_km": round(float(rb_res.get("total_distance", 0.0)), 3),
        "is_feasible": bool(rb_res["feasibility"]["is_feasible"]),
        "routed_customers": int(rb_res["feasibility"]["total_routed_customers"]),
        "unassigned_customers": int(rb_res["feasibility"]["unassigned_customers"]),
        "capacity_violations": int(rb_res["feasibility"]["capacity_violations"]),
        "num_vehicles": int(rb_res["audit"]["num_routes"]),
        "runtime_total_ms": round(t_rbqcd, 2),
        "runtime_spark_ms": 0.0, "runtime_qaoa_circuit_ms": 0.0, "runtime_qaoa_opt_ms": 0.0,
        "runtime_reconstruction_ms": 0.0, "qaoa_subproblems": 0, "logical_qubits": 0, "circuit_depth": 0,
        "lambda_mean": 0.0, "qaoa_accepted": 0, "spatial_retained": 0, "diversity_mean": 0.0, "crossings_prevented": 0
    })

    # -------------------------------------------------------------
    # 7. Google OR-Tools GLS (Classical Baseline)
    # -------------------------------------------------------------
    t0 = time.perf_counter()
    ort_res = classical_solver.solve_ortools(
        distance_matrix=matrix, num_vehicles=num_vehicles, depot=0,
        demands=demands_list, vehicle_capacities=capacities_list, time_limit_sec=2
    )
    t_ort = (time.perf_counter() - t0) * 1000.0

    results.append({
        "N": N, "seed": seed, "algorithm": "OR-Tools GLS",
        "total_distance_km": round(float(ort_res.get("total_distance_km", 0.0)), 3),
        "is_feasible": bool(ort_res.get("is_feasible", False)),
        "routed_customers": int(ort_res.get("served_customers", 0)),
        "unassigned_customers": max(0, N - int(ort_res.get("served_customers", 0))),
        "capacity_violations": int(ort_res.get("capacity_violations", 0)),
        "num_vehicles": len(ort_res.get("routes", [])),
        "runtime_total_ms": round(t_ort, 2),
        "runtime_spark_ms": 0.0, "runtime_qaoa_circuit_ms": 0.0, "runtime_qaoa_opt_ms": 0.0,
        "runtime_reconstruction_ms": 0.0, "qaoa_subproblems": 0, "logical_qubits": 0, "circuit_depth": 0,
        "lambda_mean": 0.0, "qaoa_accepted": 0, "spatial_retained": 0, "diversity_mean": 0.0, "crossings_prevented": 0
    })

    # -------------------------------------------------------------
    # 8. Clarke-Wright + 2-opt
    # -------------------------------------------------------------
    t0 = time.perf_counter()
    cw_res = classical_solver.solve_two_opt(
        distance_matrix=matrix, num_vehicles=num_vehicles, depot=0,
        demands=demands_list, vehicle_capacities=capacities_list
    )
    t_cw = (time.perf_counter() - t0) * 1000.0

    results.append({
        "N": N, "seed": seed, "algorithm": "Clarke-Wright + 2-opt",
        "total_distance_km": round(float(cw_res.get("total_distance_km", 0.0)), 3),
        "is_feasible": bool(cw_res.get("is_feasible", False)),
        "routed_customers": int(cw_res.get("served_customers", 0)),
        "unassigned_customers": max(0, N - int(cw_res.get("served_customers", 0))),
        "capacity_violations": int(cw_res.get("capacity_violations", 0)),
        "num_vehicles": len(cw_res.get("routes", [])),
        "runtime_total_ms": round(t_cw, 2),
        "runtime_spark_ms": 0.0, "runtime_qaoa_circuit_ms": 0.0, "runtime_qaoa_opt_ms": 0.0,
        "runtime_reconstruction_ms": 0.0, "qaoa_subproblems": 0, "logical_qubits": 0, "circuit_depth": 0,
        "lambda_mean": 0.0, "qaoa_accepted": 0, "spatial_retained": 0, "diversity_mean": 0.0, "crossings_prevented": 0
    })

    return results

def main():
    print("=" * 70, flush=True)
    print("ROUTE/IQ PHASE I BENCHMARK: QGAR ADAPTIVE RECONSTRUCTION", flush=True)
    print("=" * 70, flush=True)
    ensure_spark_environment()

    print("Loading Manhattan road network...", flush=True)
    G_scc, df_cust = load_manhattan_network()
    scc_nodes_list = list(G_scc.nodes())
    print(f"Road Graph: {len(scc_nodes_list)} nodes, {G_scc.number_of_edges()} directed arcs.", flush=True)

    classical_solver = ClassicalVRPSolver()
    rbqcd_decomposer = RBQCDDecomposer(max_qubits=16)
    qgar_router = QuantumGuidedAdaptiveRouter(qaoa_p=1, qaoa_shots=512, use_spark=True, strict_quantum=True)

    scales = [10, 25, 50, 100, 150, 200]
    seeds = [107, 207, 307, 407, 507]

    all_records = []
    target_dir = r"C:\Users\DELL\.gemini\antigravity\brain\aba14f7b-722c-4648-8da1-214dc979ac26\scratch\phase6_benchmark"
    os.makedirs(target_dir, exist_ok=True)
    raw_path = os.path.join(target_dir, "phase_i_qgar_benchmark_raw.csv")

    total_runs = len(scales) * len(seeds)
    run_idx = 0
    t_global_start = time.perf_counter()

    for n in scales:
        print(f"\n=======================================================", flush=True)
        print(f"Running Scale N = {n} across {len(seeds)} random seeds...", flush=True)
        print(f"=======================================================", flush=True)
        for s in seeds:
            run_idx += 1
            t_inst = time.perf_counter()
            inst_results = run_single_instance(
                n, s, G_scc, scc_nodes_list,
                classical_solver, rbqcd_decomposer, qgar_router
            )
            all_records.extend(inst_results)
            pd.DataFrame(all_records).to_csv(raw_path, index=False)
            inst_time = time.perf_counter() - t_inst
            print(f"  [{run_idx:02d}/{total_runs}] N={n:3d}, Seed={s} completed in {inst_time:.2f}s", flush=True)

    t_global_total = time.perf_counter() - t_global_start
    print(f"\nPhase I Benchmark completed successfully in {t_global_total:.1f}s.", flush=True)

    df_raw = pd.DataFrame(all_records)
    summary = df_raw.groupby(["N", "algorithm"]).agg({
        "total_distance_km": ["mean", "std"],
        "runtime_total_ms": ["mean", "std"],
        "runtime_spark_ms": "mean",
        "runtime_qaoa_circuit_ms": "mean",
        "runtime_qaoa_opt_ms": "mean",
        "runtime_reconstruction_ms": "mean",
        "is_feasible": "mean",
        "lambda_mean": "mean",
        "qaoa_accepted": "mean",
        "spatial_retained": "mean",
        "diversity_mean": "mean",
        "crossings_prevented": "mean"
    }).reset_index()

    summary_path = os.path.join(target_dir, "phase_i_qgar_benchmark_summary.csv")
    summary.to_csv(summary_path, index=False)
    print(f"Saved summary results to: {summary_path}", flush=True)

if __name__ == "__main__":
    main()

