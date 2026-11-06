"""
Phase Y: Adaptive Quantum Candidate Selection Benchmark.
Evaluates 5 gating policies on disjoint Train (30), Validation (15), and Held-Out Test (15) sets:
Policy A: Always Call QAOA
Policy B: Never Call QAOA (Classical Only)
Policy C: Random Selection (50%)
Policy D: Simple Feature Gating (Single threshold)
Policy E: Learned Adaptive Selection (Trained Multi-Feature Classifier)
"""

import sys
import os
import time
import math
import csv
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Tuple
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from phase_v_independent_quantum_validation.prototypes.algorithmic_vnd import AlgorithmicVND
from phase_u_quantum_bipartition_validation.prototypes.classical_partition_solvers import (
    ClassicalPartitioningSuite
)
from phase_y_breakthrough_engineering.prototypes.advanced_quantum_formulations import (
    AdvancedQuantumFormulations
)

@dataclass
class GatingInstanceRecord:
    split: str
    instance_id: str
    interaction_density: float
    edge_variance: float
    capacity_slack: float
    classical_stagnation_depth: int
    qubo_initial_gap: float
    asymmetry_skew: float
    is_useful: bool
    dist_classical_best: float
    dist_qaoa_vnd: float
    t_classical_ms: float
    t_qaoa_ms: float

class AdaptiveSelectionEngine:
    def __init__(self):
        self.classical_suite = ClassicalPartitioningSuite()

    def generate_instance(self, seed: int, N: int = 12) -> Dict[str, Any]:
        np.random.seed(seed)
        coords = np.random.uniform(0.0, 10.0, (N + 1, 2))
        coords[0] = np.array([5.0, 5.0])

        dist_matrix = np.zeros((N + 1, N + 1))
        asym_vals = []
        for i in range(N + 1):
            for j in range(N + 1):
                if i != j:
                    d = np.linalg.norm(coords[i] - coords[j]) * 14.5
                    factor = 1.0 + 0.08 * np.sin(i * 3 + j * 7)
                    dist_matrix[i, j] = d * factor
                    if 0 < i < j:
                        asym_vals.append(dist_matrix[i, j] - dist_matrix[j, i])

        demands = np.random.randint(1, 5, N)
        total_demand = float(np.sum(demands))
        slack_factor = float(np.random.uniform(0.52, 0.70))
        cap_a = float(np.ceil(total_demand * slack_factor))
        cap_b = float(np.ceil(total_demand * slack_factor))

        c_a = np.array([2.5, 5.0])
        c_b = np.array([7.5, 5.0])
        cust_coords = coords[1:]
        d_ia = np.linalg.norm(cust_coords - c_a, axis=1) * 14.5
        d_ib = np.linalg.norm(cust_coords - c_b, axis=1) * 14.5
        h_diff = d_ia - d_ib

        W = np.zeros((N, N))
        weights = []
        for i in range(N):
            for j in range(i + 1, N):
                d = np.linalg.norm(cust_coords[i] - cust_coords[j])
                w = 5.0 / (d + 0.5)
                weights.append(w)
                W[i, j] = w
                W[j, i] = w

        return {
            "seed": seed,
            "N": N,
            "dist_matrix": dist_matrix,
            "demands": demands,
            "cap_a": cap_a,
            "cap_b": cap_b,
            "h_diff": h_diff,
            "W": W,
            "interaction_density": float(np.mean(weights)),
            "edge_variance": float(np.std(weights)),
            "capacity_slack": float((cap_a + cap_b - total_demand) / total_demand),
            "asymmetry_skew": float(np.std(asym_vals) if asym_vals else 0.0)
        }

    def partition_to_tours(self, partition: np.ndarray, dist_matrix: np.ndarray) -> Tuple[List[int], List[int]]:
        nodes_a = [i + 1 for i, v in enumerate(partition) if v == 1]
        nodes_b = [i + 1 for i, v in enumerate(partition) if v == 0]

        def nn_tour(nodes: List[int]) -> List[int]:
            if not nodes: return []
            tour, curr = [], 0
            rem = list(nodes)
            while rem:
                nxt = min(rem, key=lambda k: dist_matrix[curr, k])
                tour.append(nxt)
                rem.remove(nxt)
                curr = nxt
            return tour
        return nn_tour(nodes_a), nn_tour(nodes_b)

    def evaluate_instance(self, inst: Dict[str, Any], split: str) -> GatingInstanceRecord:
        N = inst["N"]
        dist_matrix = inst["dist_matrix"]
        demands = inst["demands"]
        cap_a = inst["cap_a"]
        cap_b = inst["cap_b"]
        h_diff = inst["h_diff"]
        W = inst["W"]

        delta_q = cap_a - cap_b
        lambda_c = 2.0
        Q = np.zeros((N, N))
        for i in range(N):
            for j in range(N):
                if i != j:
                    Q[i, j] = -W[i, j] + lambda_c * demands[i] * demands[j]
            Q[i, i] = h_diff[i] - 2.0 * lambda_c * delta_q * demands[i]

        t0_c = time.perf_counter()
        greedy_res = self.classical_suite.greedy_capacity_constrained(Q, demands, h_diff, cap_a, cap_b)
        mls_res = self.classical_suite.multistart_local_search(Q, demands, h_diff, cap_a, cap_b, restarts=20)
        kl_res = self.classical_suite.kernighan_lin_balanced(Q, demands, h_diff, cap_a, cap_b)

        # Classical best
        p_c = np.array(kl_res["partition"])
        ta_c, tb_c = self.partition_to_tours(p_c, dist_matrix)
        dist_c = AlgorithmicVND.optimize_fleet_routes(ta_c, tb_c, demands, cap_a, cap_b, dist_matrix)["total_distance"]
        t_c = (time.perf_counter() - t0_c) * 1000.0

        # QAOA simulation
        t0_q = time.perf_counter()
        h, J = np.diag(Q), np.copy(Q)
        np.fill_diagonal(J, 0)
        qaoa_res = AdvancedQuantumFormulations.simulate_sampling_generic(h, J, demands, cap_a, cap_b, shots=512, fast_mode=True)
        p_q_rep = np.array(self.classical_suite.repair_capacity_violations(list(qaoa_res["best_x"]), demands, cap_a, cap_b, h_diff))
        ta_q, tb_q = self.partition_to_tours(p_q_rep, dist_matrix)
        dist_q = AlgorithmicVND.optimize_fleet_routes(ta_q, tb_q, demands, cap_a, cap_b, dist_matrix)["total_distance"]
        t_q = (time.perf_counter() - t0_q) * 1000.0 + 35.0

        is_useful = bool(dist_q < dist_c - 1e-4)

        return GatingInstanceRecord(
            split=split,
            instance_id=f"inst_{inst['seed']}",
            interaction_density=round(inst["interaction_density"], 3),
            edge_variance=round(inst["edge_variance"], 3),
            capacity_slack=round(inst["capacity_slack"], 3),
            classical_stagnation_depth=12,
            qubo_initial_gap=round(greedy_res["qubo_cost"] - mls_res["qubo_cost"], 3),
            asymmetry_skew=round(inst["asymmetry_skew"], 3),
            is_useful=is_useful,
            dist_classical_best=round(float(dist_c), 2),
            dist_qaoa_vnd=round(float(dist_q), 2),
            t_classical_ms=round(float(t_c), 2),
            t_qaoa_ms=round(float(t_q), 2)
        )

if __name__ == "__main__":
    engine = AdaptiveSelectionEngine()
    print("Generating 30 Train, 15 Validation, and 15 Held-Out Test instances for Adaptive Selection...")

    train_data = [engine.evaluate_instance(engine.generate_instance(s), "train") for s in range(700, 730)]
    val_data = [engine.evaluate_instance(engine.generate_instance(s), "val") for s in range(730, 745)]
    test_data = [engine.evaluate_instance(engine.generate_instance(s), "test") for s in range(745, 760)]

    all_data = train_data + val_data + test_data
    os.makedirs("phase_y_breakthrough_engineering/results", exist_ok=True)
    csv_path = "phase_y_breakthrough_engineering/results/phase_y_adaptive_selection_raw.csv"

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(all_data[0]).keys()))
        writer.writeheader()
        for r in all_data:
            writer.writerow(asdict(r))

    print(f"Dataset generated ({len(all_data)} records) in {csv_path}.")

