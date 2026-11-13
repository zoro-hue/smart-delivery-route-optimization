"""
Phase AA: Generalization and Robustness Benchmark on Held-Out Test Set.
Evaluates across 20 new held-out instances (seeds 800-819) featuring:
- Asymmetric travel impedance
- Variable spatial clustering and density
- Tight (45%) and generous (65%) capacity slacks
Compares:
1. Single-Pass KL + VND
2. Strong Classical: Tabu Search + VND (Equal Evals)
3. Strong Classical: Multistart KL + VND (Equal Time)
4. Fast QAOA + Prop 1 + VND
5. Raw QAOA (Without Prop 1) + VND
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
from phase_aa_quantum_contribution_challenge.benchmarks.benchmark_strong_classical_challenge import (
    StrongClassicalSuite
)


@dataclass
class GeneralizationRecord:
    instance_id: str
    seed: int
    slack_level: str
    spatial_layout: str
    dist_single_kl: float
    dist_tabu_evals: float
    dist_mskl_time: float
    dist_qaoa_prop1: float
    dist_qaoa_raw: float
    t_tabu_ms: float
    t_mskl_ms: float
    t_qaoa_ms: float
    tabu_beat_qaoa: bool
    mskl_beat_qaoa: bool
    qaoa_beat_single_kl: bool


class GeneralizationEngine:
    def __init__(self):
        self.classical_suite = ClassicalPartitioningSuite()
        self.strong_classical = StrongClassicalSuite()

    def generate_diverse_instance(self, seed: int, N: int = 16) -> Dict[str, Any]:
        np.random.seed(seed)
        # Variable spatial layout: clustered vs dispersed
        layout = "clustered" if seed % 2 == 0 else "dispersed"
        if layout == "clustered":
            c1 = np.random.normal(loc=2.5, scale=1.0, size=(N // 2, 2))
            c2 = np.random.normal(loc=7.5, scale=1.0, size=(N - N // 2, 2))
            cust_coords = np.vstack([c1, c2])
        else:
            cust_coords = np.random.uniform(0.0, 10.0, (N, 2))

        coords = np.vstack([[5.0, 5.0], cust_coords])

        dist_matrix = np.zeros((N + 1, N + 1))
        for i in range(N + 1):
            for j in range(N + 1):
                if i != j:
                    d = np.linalg.norm(coords[i] - coords[j]) * 14.5
                    factor = 1.0 + 0.12 * np.sin(i * 3 + j * 7)
                    dist_matrix[i, j] = d * factor

        demands = np.random.randint(1, 5, N)
        total_demand = float(np.sum(demands))
        # Variable slack: tight (52%) vs loose (65%)
        slack_ratio = 0.52 if seed % 3 == 0 else 0.65
        slack_label = "tight" if slack_ratio < 0.55 else "loose"
        cap_a = float(np.ceil(total_demand * slack_ratio))
        cap_b = float(np.ceil(total_demand * slack_ratio))

        c_a = np.array([2.5, 5.0])
        c_b = np.array([7.5, 5.0])

        d_ia = np.linalg.norm(cust_coords - c_a, axis=1) * 14.5
        d_ib = np.linalg.norm(cust_coords - c_b, axis=1) * 14.5
        h_diff = d_ia - d_ib

        W = np.zeros((N, N))
        for i in range(N):
            for j in range(i + 1, N):
                d = np.linalg.norm(cust_coords[i] - cust_coords[j])
                w = 5.0 / (d + 0.5)
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
            "slack_label": slack_label,
            "layout": layout
        }

    def run_generalization(self, num_instances: int = 20) -> List[GeneralizationRecord]:
        records = []
        for s in range(num_instances):
            inst = self.generate_diverse_instance(seed=800 + s, N=16)
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
            h, J = np.diag(Q), np.copy(Q)
            np.fill_diagonal(J, 0)

            # 1. Single-Pass KL
            kl_single = self.classical_suite.kernighan_lin_balanced(Q, demands, h_diff, cap_a, cap_b)
            p_kl = np.array(kl_single["partition"])
            ta_c, tb_c = self.strong_classical.partition_to_tours(p_kl, dist_matrix)
            opt_c = AlgorithmicVND.optimize_fleet_routes(ta_c, tb_c, demands, cap_a, cap_b, dist_matrix)
            dist_single_kl = opt_c["total_distance"]

            # 2. Fast QAOA (with and without Prop 1)
            t0 = time.perf_counter()
            qres = AdvancedQuantumFormulations.simulate_sampling_generic(h, J, demands, cap_a, cap_b, shots=512, fast_mode=True)
            p_q_rep = np.array(self.classical_suite.repair_capacity_violations(list(qres["best_x"]), demands, cap_a, cap_b, h_diff))
            ta_q, tb_q = self.strong_classical.partition_to_tours(p_q_rep, dist_matrix)
            opt_q = AlgorithmicVND.optimize_fleet_routes(ta_q, tb_q, demands, cap_a, cap_b, dist_matrix)
            dist_qaoa_raw = opt_q["total_distance"]
            dist_qaoa_prop1 = dist_single_kl if dist_qaoa_raw >= dist_single_kl - 1e-4 else dist_qaoa_raw
            t_qaoa = (time.perf_counter() - t0) * 1000.0 + 15.0

            # 3. Tabu Search (Equal Evals = 512)
            t0 = time.perf_counter()
            p_ts, _, _ = self.strong_classical.tabu_search_partition(Q, demands, h_diff, cap_a, cap_b, max_evals=512)
            ta_ts, tb_ts = self.strong_classical.partition_to_tours(p_ts, dist_matrix)
            opt_ts = AlgorithmicVND.optimize_fleet_routes(ta_ts, tb_ts, demands, cap_a, cap_b, dist_matrix)
            dist_tabu_raw = opt_ts["total_distance"]
            dist_tabu = dist_single_kl if dist_tabu_raw >= dist_single_kl - 1e-4 else dist_tabu_raw
            t_tabu = (time.perf_counter() - t0) * 1000.0

            # 4. Multistart KL (Equal Time ~ t_qaoa)
            t0 = time.perf_counter()
            p_ms, _, _ = self.strong_classical.multistart_kernighan_lin(Q, demands, h_diff, cap_a, cap_b, max_restarts=50, time_budget_ms=t_qaoa)
            ta_ms, tb_ms = self.strong_classical.partition_to_tours(p_ms, dist_matrix)
            opt_ms = AlgorithmicVND.optimize_fleet_routes(ta_ms, tb_ms, demands, cap_a, cap_b, dist_matrix)
            dist_ms_raw = opt_ms["total_distance"]
            dist_ms = dist_single_kl if dist_ms_raw >= dist_single_kl - 1e-4 else dist_ms_raw
            t_mskl = (time.perf_counter() - t0) * 1000.0

            records.append(GeneralizationRecord(
                instance_id=f"inst_diverse_{s}",
                seed=inst["seed"],
                slack_level=inst["slack_label"],
                spatial_layout=inst["layout"],
                dist_single_kl=round(dist_single_kl, 2),
                dist_tabu_evals=round(dist_tabu, 2),
                dist_mskl_time=round(dist_ms, 2),
                dist_qaoa_prop1=round(dist_qaoa_prop1, 2),
                dist_qaoa_raw=round(dist_qaoa_raw, 2),
                t_tabu_ms=round(t_tabu, 2),
                t_mskl_ms=round(t_mskl, 2),
                t_qaoa_ms=round(t_qaoa, 2),
                tabu_beat_qaoa=(dist_tabu < dist_qaoa_prop1 - 1e-4),
                mskl_beat_qaoa=(dist_ms < dist_qaoa_prop1 - 1e-4),
                qaoa_beat_single_kl=(dist_qaoa_prop1 < dist_single_kl - 1e-4)
            ))

        return records


if __name__ == "__main__":
    print("Executing Phase AA Generalization & Robustness Benchmark across 20 held-out diverse instances...")
    engine = GeneralizationEngine()
    records = engine.run_generalization(num_instances=20)

    csv_path = "phase_aa_quantum_contribution_challenge/results/phase_aa_generalization_robustness_raw.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(records[0]).keys()))
        writer.writeheader()
        for r in records:
            writer.writerow(asdict(r))

    print(f"Generalization benchmark completed: {len(records)} records logged to {csv_path}.")

