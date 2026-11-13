"""RB-QCD Scientific Ablation Study for ROUTE/IQ.

Investigates:
1. Core Kernel Impact:
   - RB-QCD with QAOA kernel (Aer simulator)
   - RB-QCD with Exact Classical Brute-Force kernel
   - RB-QCD with No Core Optimization (Greedy / Identity)
2. Subproblem Qubit Budget:
   - m=2 nodes (4 logical qubits)
   - m=3 nodes (9 logical qubits)
   - m=4 nodes (16 logical qubits)
3. Boundary Reconstruction Strategy:
   - DP Minimum Incremental Cost Insertion (Proposed)
   - Greedy Boundary Append (Ablated)

Evaluates on Manhattan road network across scales N in [20, 50, 100] with 5 random seeds.
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

from app.services.optimization.quantum_solver import QuantumVRPSolver
from app.services.optimization.rb_qcd_decomposer import RBQCDDecomposer


class AblationRBQCDDecomposer(RBQCDDecomposer):
    """Subclass of RBQCDDecomposer allowing ablation switches for insertion and core solver."""

    def __init__(self, max_qubits: int = 16, core_kernel: str = "qaoa", insertion_mode: str = "dp"):
        super().__init__(max_qubits=max_qubits)
        self.core_kernel = core_kernel  # "qaoa", "exact_classical", "none"
        self.insertion_mode = insertion_mode  # "dp", "append"

    def _solve_core_tsp(
        self,
        sub_customers: List[Dict[str, Any]],
        depot: Dict[str, Any],
        matrix: np.ndarray,
        location_indices: Dict[str, int],
        depot_idx: int
    ) -> Tuple[List[Dict[str, Any]], bool, int, int]:
        m = len(sub_customers)
        if m <= 1:
            return sub_customers, False, 0, 0

        qubits = m * m
        depth = 2

        if self.core_kernel == "none":
            # Baseline: no optimization on core cluster
            return list(sub_customers), False, 0, 0

        if self.core_kernel == "exact_classical":
            # Exact classical brute force
            best_perm = None
            best_cost = float("inf")
            for perm in itertools.permutations(sub_customers):
                c0_loc = location_indices[perm[0]["user_id"]]
                cost = matrix[depot_idx, c0_loc]
                for i in range(len(perm) - 1):
                    u_loc = location_indices[perm[i]["user_id"]]
                    v_loc = location_indices[perm[i + 1]["user_id"]]
                    cost += matrix[u_loc, v_loc]
                cost += matrix[location_indices[perm[-1]["user_id"]], depot_idx]
                if cost < best_cost:
                    best_cost = cost
                    best_perm = list(perm)
            return (best_perm if best_perm is not None else sub_customers), False, 0, 0

        # Default: QAOA
        return super()._solve_core_tsp(sub_customers, depot, matrix, location_indices, depot_idx)

    def _optimize_single_route(
        self,
        cluster: List[Dict[str, Any]],
        depot: Dict[str, Any],
        matrix: np.ndarray,
        vehicle_capacity: float,
        location_indices: Dict[str, int],
        depot_idx: int,
        vehicle_idx: int
    ) -> Tuple[Dict[str, Any], bool, int, int]:
        m = len(cluster)
        did_qaoa = False
        qubits = 0
        depth = 0

        if m <= self.max_qaoa_nodes:
            optimized_stops, did_qaoa, qubits, depth = self._solve_core_tsp(
                cluster, depot, matrix, location_indices, depot_idx
            )
        else:
            core_cluster, remaining_custs = self._extract_core_cluster(
                cluster, matrix, location_indices, self.max_qaoa_nodes
            )

            core_stops, did_qaoa, qubits, depth = self._solve_core_tsp(
                core_cluster, depot, matrix, location_indices, depot_idx
            )

            if self.insertion_mode == "append":
                # Ablated mode: naive append
                optimized_stops = list(core_stops) + list(remaining_custs)
            else:
                # Proposed mode: DP insertion
                optimized_stops = self._reconstruct_route_dp_insertion(
                    core_stops, remaining_custs, matrix, location_indices, depot_idx
                )

        full_internal_stops = [{"internal_idx": -1, "user_id": depot.get("id", "depot"), "is_depot": True}]
        full_internal_stops.extend(optimized_stops)
        full_internal_stops.append({"internal_idx": -1, "user_id": depot.get("id", "depot"), "is_depot": True})

        full_stops = [depot] + [c["original_dict"] for c in optimized_stops] + [depot]
        total_dist = self._calculate_route_distance(optimized_stops, depot, matrix, location_indices, depot_idx)
        total_load = sum(c["demand"] for c in cluster)

        route_dict = {
            "vehicle_id": vehicle_idx,
            "stops": full_stops,
            "internal_stops": full_internal_stops,
            "total_distance": round(total_dist, 2),
            "total_load": round(total_load, 2),
            "customer_count": m
        }
        return route_dict, did_qaoa, qubits, depth


def run_ablation_study():
    p_graph = 'backend/data/processed/road_graph_manhatten.pickle'
    with open(p_graph, 'rb') as f:
        G = pickle.load(f)
    for u, v, k, d in G.edges(keys=True, data=True):
        d['length'] = float(d.get('length', 1.0))
    largest_scc_nodes = max(nx.strongly_connected_components(G), key=len)
    G_scc = G.subgraph(largest_scc_nodes).copy()
    scc_nodes_list = sorted(list(G_scc.nodes()))

    scales = [20, 50, 100]
    seeds = [101, 202, 303, 404, 505]
    vehicle_capacity = 15.0

    target_dir = r"C:\Users\DELL\.gemini\antigravity\brain\aba14f7b-722c-4648-8da1-214dc979ac26\scratch\phase6_benchmark"
    os.makedirs(target_dir, exist_ok=True)

    # Define ablation variants:
    # 1. Full Proposed RB-QCD (QAOA kernel, m=4 [16 qubits], DP insertion)
    # 2. Classical Exact Kernel (Exact brute-force kernel, m=4, DP insertion)
    # 3. No Core Opt (Kernel=none, m=4, DP insertion)
    # 4. Budget m=2 (QAOA kernel, m=2 [4 qubits], DP insertion)
    # 5. Budget m=3 (QAOA kernel, m=3 [9 qubits], DP insertion)
    # 6. Naive Reconstruction (QAOA kernel, m=4, Append insertion)

    variants = [
        {"name": "Full RB-QCD (QAOA, m=4, DP)", "qubits": 16, "kernel": "qaoa", "insertion": "dp"},
        {"name": "Classical Exact Kernel (Exact, m=4, DP)", "qubits": 16, "kernel": "exact_classical", "insertion": "dp"},
        {"name": "No Core Opt (Identity, m=4, DP)", "qubits": 16, "kernel": "none", "insertion": "dp"},
        {"name": "Budget m=2 (4 Qubits, DP)", "qubits": 4, "kernel": "qaoa", "insertion": "dp"},
        {"name": "Budget m=3 (9 Qubits, DP)", "qubits": 9, "kernel": "qaoa", "insertion": "dp"},
        {"name": "Naive Insertion (QAOA, m=4, Append)", "qubits": 16, "kernel": "qaoa", "insertion": "append"},
    ]

    records = []
    print("=================================================================")
    print("Starting RB-QCD Scientific Ablation Campaign")
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

            for var in variants:
                decomposer = AblationRBQCDDecomposer(
                    max_qubits=var["qubits"],
                    core_kernel=var["kernel"],
                    insertion_mode=var["insertion"]
                )
                t0 = time.perf_counter()
                res = decomposer.decompose_and_solve(
                    depot=depot,
                    customers=customers,
                    matrix=matrix,
                    num_vehicles=num_vehicles,
                    vehicle_capacity=vehicle_capacity,
                    location_indices=location_indices
                )
                t_ms = (time.perf_counter() - t0) * 1000.0
                dist = res["total_distance"]
                feas = res["feasibility"]["is_feasible"]
                unassigned = res["feasibility"]["unassigned_customers"]

                records.append({
                    "N": N,
                    "seed": seed,
                    "variant": var["name"],
                    "qubits": var["qubits"],
                    "kernel": var["kernel"],
                    "insertion": var["insertion"],
                    "total_distance_km": dist,
                    "runtime_ms": round(t_ms, 2),
                    "is_feasible": feas,
                    "unassigned_customers": unassigned
                })

            print(f"  [N={N:3d}, Seed={seed}] Ablation variants completed.")

    df_abl = pd.DataFrame(records)
    out_csv = os.path.join(target_dir, "rbqcd_ablation_results.csv")
    df_abl.to_csv(out_csv, index=False)
    print(f"\nAblation study completed. Saved to {out_csv}")


if __name__ == "__main__":
    run_ablation_study()

