"""
Phase K: Quantum Attribution Controlled Experiment Script for ROUTE/IQ.

Evaluates 6 controlled regimes on identical instances:
  Regime A: Spatial baseline only.
  Regime B: QGAR with genuine QAOA samples.
  Regime C: QGAR with uniformly random bitstring samples.
  Regime D: QGAR with shuffled QAOA probabilities.
  Regime E: QGAR with quantum-derived transitions disabled.
  Regime F: QGAR with classical candidate generation (classical 2-opt perturbations).

Records:
  - QAOA circuit executions
  - Total measurement shots
  - Unique measured bitstrings
  - Unique valid permutations
  - Candidate evaluation count
  - Accepted quantum-derived transitions
  - Final routes changed by quantum decisions
  - Distance improvement caused by accepted decisions
  - Rejected quantum candidates
  - Spatial fallback count
  - Unbundled runtimes (Spark, QAOA circuit, classical COBYLA, reconstruction)
"""

import os
import sys
import time
import math
import random
import itertools
from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd

# Set environment
os.environ["PYTHONPATH"] = "backend"
sys.path.insert(0, "backend")

from app.services.bigdata_pipeline import ensure_spark_environment
from app.services.road_network_service import RoadNetworkService
from app.services.spark_routing_preprocessor import SparkRoutingPreprocessor, CalibratedTrafficImpedanceModel
from app.services.optimization.qaoa_subproblem_optimizer import QAOASubproblemOptimizer
from app.services.optimization.qgar_pipeline import (
    QuantumGuidedAdaptiveRouter,
    QuantumCandidateEvaluator,
    AdaptiveQuantumInfluenceModel,
    count_tour_crossings
)


import pickle
import networkx as nx

def load_manhattan_network():
    p_graph = 'backend/data/processed/road_graph_manhatten.pickle'
    with open(p_graph, 'rb') as f:
        G = pickle.load(f)

    for u, v, k, d in G.edges(keys=True, data=True):
        d['length'] = float(d.get('length', 1.0))

    largest_scc_nodes = max(nx.strongly_connected_components(G), key=len)
    G_scc = G.subgraph(largest_scc_nodes).copy()
    scc_nodes_list = list(G_scc.nodes())
    return G_scc, scc_nodes_list

def build_instance_matrix(G: nx.DiGraph, node_list: List[int]) -> np.ndarray:
    K = len(node_list)
    matrix = np.zeros((K, K), dtype=float)
    for i, src in enumerate(node_list):
        lengths = nx.single_source_dijkstra_path_length(G, src, weight='length')
        for j, dst in enumerate(node_list):
            if i != j:
                matrix[i, j] = lengths.get(dst, 100000.0) / 1000.0
    return matrix

def generate_manhattan_instance(
    G_scc: nx.DiGraph,
    scc_nodes_list: List[int],
    num_orders: int,
    seed: int
) -> Tuple[List[Dict[str, Any]], Dict[str, Any], np.ndarray, Dict[str, int]]:
    rng = np.random.default_rng(seed)
    chosen_nodes = rng.choice(scc_nodes_list, size=num_orders + 1, replace=False)
    depot_node = chosen_nodes[0]
    cust_nodes = chosen_nodes[1:]
    all_nodes = [depot_node] + list(cust_nodes)
    matrix = build_instance_matrix(G_scc, all_nodes)

    depot = {
        "id": "depot",
        "customer_id": "depot",
        "latitude": float(G_scc.nodes[depot_node].get('y', 40.7580)),
        "longitude": float(G_scc.nodes[depot_node].get('x', -73.9855)),
        "demand": 0.0
    }
    customers = []
    location_indices = {"depot": 0}
    for idx, node in enumerate(cust_nodes):
        cid = f"cust_{idx + 1}"
        dem = float(rng.integers(1, 4))
        customers.append({
            "id": cid,
            "customer_id": cid,
            "latitude": float(G_scc.nodes[node].get('y', 40.7580)),
            "longitude": float(G_scc.nodes[node].get('x', -73.9855)),
            "demand": dem
        })
        location_indices[cid] = idx + 1
    return customers, depot, matrix, location_indices


def run_attribution_on_cluster(
    cluster_custs: List[Dict[str, Any]],
    depot: Dict[str, Any],
    distance_matrix: np.ndarray,
    location_indices: Dict[str, int],
    depot_idx: int,
    qaoa_optimizer: QAOASubproblemOptimizer,
    regime: str,
    seed: int
) -> Dict[str, Any]:
    """Evaluates a single microcluster under the specified regime with granular telemetry."""
    m = min(4, len(cluster_custs))
    core_custs = cluster_custs[:m]
    boundary_custs = cluster_custs[m:]

    # Base spatial ordering
    spatial_stops = list(core_custs)
    spatial_indices = [depot_idx] + [location_indices[c["id"]] for c in spatial_stops] + [depot_idx]
    spatial_core_cost = sum(distance_matrix[u, v] for u, v in zip(spatial_indices[:-1], spatial_indices[1:]))

    # Telemetry accumulators
    did_qaoa = False
    qaoa_circ_ms = 0.0
    qaoa_opt_ms = 0.0
    circuit_depth = 0
    logical_qubits = 0
    total_shots = 2048
    unique_bstrs = 0
    unique_perms = 0
    cand_eval_count = 0
    raw_counts = {}

    if len(core_custs) <= 1 or regime == "A_SPATIAL_ONLY":
        adopted_backbone = spatial_stops
        adopted_source = "SPATIAL_SWEEP"
        accepted_transition = False
        lambda_eff = 0.0
        qaoa_core_cost = spatial_core_cost
    else:
        # Run QAOA circuit to obtain quantum counts
        did_qaoa = True
        qaoa_res = qaoa_optimizer.solve_microcluster_tour(
            core_custs, depot, distance_matrix, location_indices, strict=True
        )
        qaoa_circ_ms = qaoa_res["runtime_circuit_ms"]
        qaoa_opt_ms = qaoa_res["runtime_opt_ms"]
        circuit_depth = qaoa_res["circuit_depth"]
        logical_qubits = qaoa_res["logical_qubits"]
        genuine_counts = qaoa_res.get("raw_counts", {qaoa_res["raw_bitstring"]: total_shots})

        # Regime-specific candidate count construction
        if regime == "B_GENUINE_QAOA":
            raw_counts = genuine_counts
        elif regime == "C_UNIFORM_RANDOM":
            # Generate 2,048 uniformly random bitstrings
            raw_counts = {}
            rng = random.Random(seed + 101)
            num_bits = m * m
            for _ in range(total_shots):
                bstr = ''.join(rng.choice(['0', '1']) for _ in range(num_bits))
                raw_counts[bstr] = raw_counts.get(bstr, 0) + 1
        elif regime == "D_SHUFFLED_QAOA":
            # Shuffle keys of genuine counts
            rng = random.Random(seed + 202)
            keys = list(genuine_counts.keys())
            shuffled_keys = list(keys)
            rng.shuffle(shuffled_keys)
            raw_counts = {shuffled_keys[i]: genuine_counts[k] for i, k in enumerate(keys)}
        elif regime == "E_TRANSITIONS_DISABLED":
            raw_counts = genuine_counts
        elif regime == "F_CLASSICAL_CANDIDATES":
            # Classical candidate generation: all permutations of core_custs
            all_perms = list(itertools.permutations(range(m)))
            raw_counts = {}
            for p in all_perms:
                # Encode permutation as one-hot bitstring
                mat_x = np.zeros((m, m), dtype=int)
                for c_idx, step in enumerate(p):
                    mat_x[c_idx, step] = 1
                bstr = ''.join(str(mat_x[i, t]) for i in range(m) for t in range(m))
                raw_counts[bstr] = total_shots // len(all_perms)

        # Evaluate candidate bitstrings
        eval_res = QuantumCandidateEvaluator.evaluate_all_candidates(
            raw_counts, core_custs, depot, distance_matrix, location_indices, depot_idx
        )
        best_cand = eval_res["best_candidate"]
        cand_eval_count = eval_res["candidates_evaluated"]
        unique_perms = eval_res["unique_permutations_sampled"]
        unique_bstrs = len(raw_counts)

        if regime == "E_TRANSITIONS_DISABLED":
            # Quantum transitions disabled: unconditionally retain spatial order
            adopted_backbone = spatial_stops
            adopted_source = "SPATIAL_SWEEP (DISABLED)"
            accepted_transition = False
            lambda_eff = 0.0
            qaoa_core_cost = best_cand["directed_cost_km"]
        else:
            inf_res = AdaptiveQuantumInfluenceModel.compute_quantum_influence(
                best_cand, core_custs, depot, distance_matrix, location_indices, depot_idx
            )
            adopted_backbone = inf_res["adopted_backbone"]
            adopted_source = inf_res["adopted_source"]
            accepted_transition = (adopted_source == "QAOA")
            lambda_eff = inf_res["lambda_eff"]
            qaoa_core_cost = best_cand["directed_cost_km"]

    # Directed DP Reconstruction
    t_r0 = time.perf_counter()
    router = QuantumGuidedAdaptiveRouter(use_spark=False)
    reconstructed_qaoa = router._reconstruct_route_dp_insertion(
        adopted_backbone, boundary_custs, distance_matrix, location_indices, depot_idx
    )
    dist_qaoa = router._calculate_route_distance(
        reconstructed_qaoa, depot_idx, distance_matrix, location_indices
    )

    reconstructed_spatial = router._reconstruct_route_dp_insertion(
        spatial_stops, boundary_custs, distance_matrix, location_indices, depot_idx
    )
    dist_spatial = router._calculate_route_distance(
        reconstructed_spatial, depot_idx, distance_matrix, location_indices
    )

    # End-to-End Route Certification
    final_route_changed = False
    dist_improvement = 0.0
    if accepted_transition and boundary_custs:
        if dist_qaoa <= dist_spatial + 1e-4:
            final_route = reconstructed_qaoa
            final_dist = dist_qaoa
            final_route_changed = (dist_qaoa < dist_spatial - 1e-4)
            dist_improvement = max(0.0, dist_spatial - dist_qaoa)
        else:
            final_route = reconstructed_spatial
            final_dist = dist_spatial
            accepted_transition = False
            adopted_source = "SPATIAL_FALLBACK_CERTIFIED"
    elif accepted_transition:
        final_route = reconstructed_qaoa
        final_dist = dist_qaoa
        final_route_changed = (dist_qaoa < dist_spatial - 1e-4)
        dist_improvement = max(0.0, dist_spatial - dist_qaoa)
    else:
        final_route = reconstructed_spatial
        final_dist = dist_spatial

    t_reconstruct_ms = (time.perf_counter() - t_r0) * 1000.0

    return {
        "did_qaoa": did_qaoa,
        "runtime_circuit_ms": qaoa_circ_ms,
        "runtime_opt_ms": qaoa_opt_ms,
        "runtime_reconstruct_ms": t_reconstruct_ms,
        "circuit_depth": circuit_depth,
        "logical_qubits": logical_qubits,
        "total_shots": total_shots,
        "unique_bitstrings": unique_bstrs,
        "unique_permutations": unique_perms,
        "candidates_evaluated": cand_eval_count,
        "accepted_transition": accepted_transition,
        "adopted_source": adopted_source,
        "lambda_eff": lambda_eff,
        "final_route_changed": final_route_changed,
        "distance_improvement_km": dist_improvement,
        "final_route_dist_km": final_dist,
        "spatial_baseline_dist_km": dist_spatial,
        "stops": final_route
    }


def run_quantum_attribution_experiment(scales: List[int], seeds: List[int], output_csv: str):
    print("=" * 80)
    print("ROUTE/IQ — PHASE K: QUANTUM ATTRIBUTION CONTROLLED EXPERIMENT")
    print(f"Scales: {scales} | Seeds: {seeds}")
    print("=" * 80)

    G_scc, scc_nodes_list = load_manhattan_network()
    ensure_spark_environment()

    qaoa_opt = QAOASubproblemOptimizer(p=1, shots=1024, max_qubits=20)
    preprocessor = SparkRoutingPreprocessor(master="local[*]")
    capacity = 15.0

    regimes = [
        "A_SPATIAL_ONLY",
        "B_GENUINE_QAOA",
        "C_UNIFORM_RANDOM",
        "D_SHUFFLED_QAOA",
        "E_TRANSITIONS_DISABLED",
        "F_CLASSICAL_CANDIDATES"
    ]

    records = []

    for N in scales:
        for seed in seeds:
            print(f"\n---> Instance N={N}, seed={seed}...")
            customers, depot, matrix, loc_map = generate_manhattan_instance(
                G_scc, scc_nodes_list, N, seed=seed
            )
            depot_idx = 0

            df_cust = pd.DataFrame([
                {
                    "order_id": c["id"],
                    "customer_id": c["id"],
                    "latitude": c["latitude"],
                    "longitude": c["longitude"],
                    "demand": c["demand"],
                    "original_dict": c
                }
                for c in customers
            ])

            # Preprocess partitions using Spark
            clusters, t_spark_ms = preprocessor.partition_customers_spark(
                df_cust, float(depot["latitude"]), float(depot["longitude"]), capacity
            )

            for regime in regimes:
                t0 = time.perf_counter()
                total_campaign_dist = 0.0
                total_circ_ms = 0.0
                total_opt_ms = 0.0
                total_recon_ms = 0.0
                qaoa_subproblems = 0
                total_accepted = 0
                total_rejected = 0
                total_routes_changed = 0
                total_improvement_km = 0.0
                total_unique_bstrs = 0
                total_unique_perms = 0
                total_cands_eval = 0
                lambda_list = []

                for k, cluster in enumerate(clusters):
                    cluster_custs = [c["original_dict"] for c in cluster["customers"]]
                    if not cluster_custs:
                        continue

                    payload = preprocessor.extract_quantum_subproblem_payload(
                        cluster_custs, depot, matrix, loc_map, core_budget=4
                    )
                    core_c = payload["core_customers"]
                    boundary_c = payload["boundary_customers"]
                    combined_custs = core_c + boundary_c

                    res = run_attribution_on_cluster(
                        combined_custs, depot, matrix, loc_map, depot_idx,
                        qaoa_opt, regime, seed=seed + k * 17
                    )

                    total_campaign_dist += res["final_route_dist_km"]
                    total_circ_ms += res["runtime_circuit_ms"]
                    total_opt_ms += res["runtime_opt_ms"]
                    total_recon_ms += res["runtime_reconstruct_ms"]
                    if res["did_qaoa"]:
                        qaoa_subproblems += 1
                        total_unique_bstrs += res["unique_bitstrings"]
                        total_unique_perms += res["unique_permutations"]
                        total_cands_eval += res["candidates_evaluated"]
                        lambda_list.append(res["lambda_eff"])

                    if res["accepted_transition"]:
                        total_accepted += 1
                    else:
                        total_rejected += 1

                    if res["final_route_changed"]:
                        total_routes_changed += 1
                    total_improvement_km += res["distance_improvement_km"]

                t_total_ms = (time.perf_counter() - t0) * 1000.0
                mean_lambda = float(np.mean(lambda_list)) if lambda_list else 0.0

                record = {
                    "N": N,
                    "seed": seed,
                    "regime": regime,
                    "campaign_distance_km": round(total_campaign_dist, 3),
                    "qaoa_subproblems": qaoa_subproblems,
                    "accepted_transitions": total_accepted,
                    "rejected_transitions": total_rejected,
                    "final_routes_changed": total_routes_changed,
                    "distance_improvement_km": round(total_improvement_km, 4),
                    "mean_lambda_eff": round(mean_lambda, 3),
                    "total_unique_bitstrings": total_unique_bstrs,
                    "total_unique_permutations": total_unique_perms,
                    "total_candidates_evaluated": total_cands_eval,
                    "runtime_spark_ms": round(t_spark_ms, 2),
                    "runtime_qaoa_circuit_ms": round(total_circ_ms, 2),
                    "runtime_qaoa_opt_ms": round(total_opt_ms, 2),
                    "runtime_reconstruction_ms": round(total_recon_ms, 2),
                    "runtime_total_ms": round(t_total_ms, 2)
                }
                records.append(record)
                print(f"  [{regime:23s}] Dist: {total_campaign_dist:7.3f} km | Acc: {total_accepted:2d} | Rej: {total_rejected:2d} | Chg: {total_routes_changed:2d} | Imp: {total_improvement_km:6.3f} km | Time: {t_total_ms:6.1f} ms", flush=True)

                # Incremental write
                df_out = pd.DataFrame(records)
                df_out.to_csv(output_csv, index=False)

    print(f"\nQuantum attribution experiment successfully saved to {output_csv}")


if __name__ == "__main__":
    out_dir = r"scratch/phase_k_reproduction"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "quantum_attribution_experiment.csv")

    # Run on N=10, 25, 50 across 3 representative seeds (107, 207, 307)
    run_quantum_attribution_experiment(scales=[10, 25, 50], seeds=[107, 207, 307], output_csv=out_path)
