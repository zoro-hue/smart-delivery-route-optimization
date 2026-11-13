"""
Phase S: Exhaustive Asymmetric Directed Neighborhood Benchmark.
Benchmarks 20 diverse directed subproblems across varying asymmetry levels (alpha = 0.15 to 0.45):
Evaluates:
- Method 1: Initial Seed
- Method 2: Directed 2-opt
- Method 3: Directed Relocate
- Method 4: Directed Swap
- Method 5: Or-opt (len=2)
- Method 6: Variable Neighborhood Descent (VND)
- Method 7: Variable Neighborhood Search (VNS)
- Method 8: QIGA (Quantum-Inspired Genetic Algorithm)
- Method 9: QAOA with XY-mixer & Hungarian projection
- Method 10: Classical Multistart VNS under Equal Wall-Clock Budget
- Method 11: Exact Enumeration (Ground-Truth Optimum)

Computes exact Optimality Gaps, Discovery Rates, and Runtimes.
"""

import sys
import os
import time
import math
import itertools
from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
from scipy.optimize import minimize, linear_sum_assignment

import qiskit
from qiskit import QuantumCircuit, transpile
from qiskit.circuit import Parameter
from qiskit.circuit.library import XXPlusYYGate
from qiskit_aer import AerSimulator

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from phase_s_asymmetric_quantum_neighborhoods.prototypes.asymmetric_classical_solvers import (
    AsymmetricDirectedLocalSearchSuite
)


class AsymmetricNeighborhoodExhaustiveBenchmark:
    def __init__(self, p: int = 1, shots: int = 512):
        self.p = p
        self.shots = shots
        self.simulator = AerSimulator()
        self.classical_suite = AsymmetricDirectedLocalSearchSuite()

    def build_qaoa_circuit(self, K: int, qubo: dict, seed_perm: list):
        num_qubits = K * K
        qc = QuantumCircuit(num_qubits)
        gammas = [Parameter(f"gamma_{l}") for l in range(self.p)]
        betas = [Parameter(f"beta_{l}") for l in range(self.p)]

        def q_idx(i: int, p_pos: int) -> int: return i * K + p_pos

        # Initialize seed permutation
        for i in range(K):
            qc.x(q_idx(i, seed_perm[i]))

        for l in range(self.p):
            # Cost Hamiltonian
            for (u, v), w in qubo.items():
                if abs(w) < 1e-9: continue
                if u == v:
                    qc.rz(2.0 * gammas[l] * w, u)
                else:
                    qc.rzz(2.0 * gammas[l] * w, u, v)

            # Continuous XY-mixer
            for i in range(K):
                for pos in range(K - 1):
                    q0 = q_idx(i, pos)
                    q1 = q_idx(i, pos + 1)
                    qc.append(XXPlusYYGate(2.0 * betas[l], 0.0), [q0, q1])

        qc.measure_all()
        return qc, gammas, betas

    def run_qaoa(
        self,
        cost_matrix: np.ndarray,
        sub_locs: List[int],
        entry_idx: int,
        exit_idx: int,
        seed_perm: List[int]
    ) -> Dict[str, Any]:
        """Runs QAOA with Hungarian post-projection."""
        t0 = time.perf_counter()
        K = len(seed_perm)

        def q_idx(i: int, p_pos: int) -> int: return i * K + p_pos

        def perm_cost(p):
            c = cost_matrix[entry_idx, sub_locs[p[0]]]
            for idx in range(len(p) - 1):
                c += cost_matrix[sub_locs[p[idx]], sub_locs[p[idx + 1]]]
            c += cost_matrix[sub_locs[p[-1]], exit_idx]
            return float(c)

        seed_cost = perm_cost(seed_perm)

        # Build QUBO
        qubo = {}
        penalty = float(np.max(cost_matrix) * 1.5)

        for i in range(K):
            u = q_idx(i, 0)
            qubo[(u, u)] = qubo.get((u, u), 0.0) + cost_matrix[entry_idx, sub_locs[i]]
            v = q_idx(i, K - 1)
            qubo[(v, v)] = qubo.get((v, v), 0.0) + cost_matrix[sub_locs[i], exit_idx]

        for p_pos in range(K - 1):
            for i in range(K):
                for j in range(K):
                    if i != j:
                        u, v = q_idx(i, p_pos), q_idx(j, p_pos + 1)
                        key = (min(u, v), max(u, v))
                        qubo[key] = qubo.get(key, 0.0) + cost_matrix[sub_locs[i], sub_locs[j]]

        for i in range(K):
            for p_pos in range(K):
                u = q_idx(i, p_pos)
                qubo[(u, u)] = qubo.get((u, u), 0.0) - penalty
                for q_pos in range(p_pos + 1, K):
                    v = q_idx(i, q_pos)
                    key = (min(u, v), max(u, v))
                    qubo[key] = qubo.get(key, 0.0) + 2.0 * penalty

        for p_pos in range(K):
            for i in range(K):
                u = q_idx(i, p_pos)
                qubo[(u, u)] = qubo.get((u, u), 0.0) - penalty
                for j in range(i + 1, K):
                    v = q_idx(j, p_pos)
                    key = (min(u, v), max(u, v))
                    qubo[key] = qubo.get(key, 0.0) + 2.0 * penalty

        qc, gammas, betas = self.build_qaoa_circuit(K, qubo, seed_perm)
        transpiled = transpile(qc, self.simulator)

        # Optimize variational parameters
        def eval_obj(params):
            p_dict = {gammas[0]: params[0], betas[0]: params[1]}
            bound = transpiled.assign_parameters(p_dict)
            job = self.simulator.run(bound, shots=128)
            counts = job.result().get_counts()
            tot = 0.0
            for bstr, cnt in counts.items():
                rb = [int(b) for b in reversed(bstr)]
                mat = np.zeros((K, K))
                for i in range(K):
                    for p_pos in range(K):
                        mat[i, p_pos] = rb[q_idx(i, p_pos)]
                r_ind, c_ind = linear_sum_assignment(1.0 - mat)
                dp = [0] * K
                for r, c in zip(r_ind, c_ind):
                    dp[c] = r
                tot += perm_cost(dp) * cnt
            return tot / 128.0

        init_params = [0.15 * math.pi / max(1.0, float(np.max(cost_matrix))), 0.35 * math.pi]
        res_opt = minimize(eval_obj, init_params, method="COBYLA", options={"maxiter": 8})
        opt_p = res_opt.x

        final_dict = {gammas[0]: opt_p[0], betas[0]: opt_p[1]}
        final_job = self.simulator.run(transpiled.assign_parameters(final_dict), shots=self.shots)
        final_counts = final_job.result().get_counts()

        best_cand_perm = list(seed_perm)
        best_cand_cost = seed_cost

        for bstr, cnt in final_counts.items():
            rb = [int(b) for b in reversed(bstr)]
            mat = np.zeros((K, K))
            for i in range(K):
                for p_pos in range(K):
                    mat[i, p_pos] = rb[q_idx(i, p_pos)]
            r_ind, c_ind = linear_sum_assignment(1.0 - mat)
            cand = [0] * K
            for r, c in zip(r_ind, c_ind):
                cand[c] = r
            c_cost = perm_cost(cand)
            if c_cost < best_cand_cost:
                best_cand_cost = c_cost
                best_cand_perm = cand

        t_ms = (time.perf_counter() - t0) * 1000.0
        return {
            "best_perm": best_cand_perm,
            "cost_km": round(best_cand_cost, 4),
            "time_ms": round(t_ms, 2)
        }

    def run_qiga(
        self,
        cost_matrix: np.ndarray,
        sub_locs: List[int],
        entry_idx: int,
        exit_idx: int,
        seed_perm: List[int],
        generations: int = 20,
        pop_size: int = 12
    ) -> Dict[str, Any]:
        """Runs QIGA on K=4 subproblem."""
        t0 = time.perf_counter()
        K = len(seed_perm)

        def perm_cost(p):
            c = cost_matrix[entry_idx, sub_locs[p[0]]]
            for idx in range(len(p) - 1):
                c += cost_matrix[sub_locs[p[idx]], sub_locs[p[idx + 1]]]
            c += cost_matrix[sub_locs[p[-1]], exit_idx]
            return float(c)

        best_perm = list(seed_perm)
        best_c = perm_cost(best_perm)
        angles = np.full(K, math.pi / 4.0)

        for _ in range(generations):
            for _ in range(pop_size):
                probs = np.sin(angles) ** 2
                cand = list(np.argsort(probs + np.random.normal(0, 0.1, K)))
                c = perm_cost(cand)
                if c < best_c:
                    best_c = c
                    best_perm = cand
                    for idx, pos in enumerate(cand):
                        angles[pos] += 0.05 * math.pi
            angles = np.clip(angles, 0.05 * math.pi, 0.45 * math.pi)

        t_ms = (time.perf_counter() - t0) * 1000.0
        return {"best_perm": best_perm, "cost_km": round(best_c, 4), "time_ms": round(t_ms, 2)}

    def run_multistart_vns_equal_time(
        self,
        cost_matrix: np.ndarray,
        sub_locs: List[int],
        entry_idx: int,
        exit_idx: int,
        target_time_ms: float
    ) -> Dict[str, Any]:
        """Runs Multistart VNS until target wall-clock time budget is exhausted."""
        t0 = time.perf_counter()
        K = len(sub_locs)
        best_cost = float("inf")
        best_perm = list(range(K))
        restarts = 0

        while (time.perf_counter() - t0) * 1000.0 < target_time_ms:
            restarts += 1
            rand_seed = list(np.random.permutation(K))
            vns_res = self.classical_suite.variable_neighborhood_search(
                rand_seed, cost_matrix, sub_locs, entry_idx, exit_idx, max_shaking_iter=5
            )
            if vns_res["cost_km"] < best_cost:
                best_cost = vns_res["cost_km"]
                best_perm = vns_res["best_perm"]

        t_actual_ms = (time.perf_counter() - t0) * 1000.0
        return {
            "best_perm": best_perm,
            "cost_km": round(best_cost, 4),
            "time_ms": round(t_actual_ms, 2),
            "restarts": restarts
        }


def main():
    print("=" * 80)
    print("PHASE S: EXHAUSTIVE ASYMMETRIC NEIGHBORHOOD OPTIMIZATION BENCHMARK")
    print("=" * 80)

    bench = AsymmetricNeighborhoodExhaustiveBenchmark(p=1, shots=512)
    records = []

    # 20 diverse asymmetric subproblems
    for test_idx in range(1, 21):
        np.random.seed(1000 + test_idx)
        # Create asymmetric matrix with controlled alpha
        alpha_target = 0.15 + (test_idx % 4) * 0.10
        dist_mat = np.random.uniform(5.0, 30.0, (6, 6))
        for i in range(6):
            for j in range(6):
                if i != j:
                    diff = np.random.uniform(-15.0, 25.0) * (alpha_target / 0.25)
                    dist_mat[i, j] += diff
                    dist_mat[i, j] = max(1.5, dist_mat[i, j])
        np.fill_diagonal(dist_mat, 0.0)

        # Compute empirical alpha
        sum_abs_diff = np.sum(np.abs(dist_mat - dist_mat.T))
        sum_total = np.sum(dist_mat + dist_mat.T)
        empirical_alpha = sum_abs_diff / max(1e-4, sum_total)

        entry = 0
        exit_n = 5
        sub_locs = [1, 2, 3, 4]
        all_perms = list(itertools.permutations(range(4)))

        def p_cost(p):
            c = dist_mat[entry, sub_locs[p[0]]]
            for k in range(len(p) - 1): c += dist_mat[sub_locs[p[k]], sub_locs[p[k + 1]]]
            c += dist_mat[sub_locs[p[-1]], exit_n]
            return float(c)

        sorted_perms = sorted(all_perms, key=p_cost)
        exact_res = bench.classical_suite.exact_enumeration(dist_mat, sub_locs, entry, exit_n)
        exact_cost = exact_res["cost_km"]

        # Assign seed: alternate between suboptimal heuristic seed and trapped 2-opt seed
        if test_idx % 2 == 1:
            seed = list(sorted_perms[min(16, len(sorted_perms) - 1)])
            seed_type = "Suboptimal_Seed"
        else:
            cur = list(sorted_perms[10])
            improved = True
            while improved:
                improved = False
                for i in range(3):
                    for j in range(i + 1, 4):
                        cand = cur[:i] + cur[i:j + 1][::-1] + cur[j + 1:]
                        if p_cost(cand) < p_cost(cur) - 1e-4:
                            cur = cand
                            improved = True
                            break
                    if improved: break
            seed = cur
            seed_type = "Trapped_2opt_Seed"

        seed_cost = p_cost(seed)

        # 1. Classical Solvers
        res_2opt = bench.classical_suite.directed_2opt(seed, dist_mat, sub_locs, entry, exit_n)
        res_reloc = bench.classical_suite.relocate_search(seed, dist_mat, sub_locs, entry, exit_n)
        res_swap = bench.classical_suite.swap_search(seed, dist_mat, sub_locs, entry, exit_n)
        res_oropt = bench.classical_suite.or_opt_search(seed, dist_mat, sub_locs, entry, exit_n, block_len=2)
        res_vnd = bench.classical_suite.variable_neighborhood_descent(seed, dist_mat, sub_locs, entry, exit_n)
        res_vns = bench.classical_suite.variable_neighborhood_search(seed, dist_mat, sub_locs, entry, exit_n, max_shaking_iter=5)

        # 2. QIGA
        res_qiga = bench.run_qiga(dist_mat, sub_locs, entry, exit_n, seed)

        # 3. QAOA (XY-mixer + Hungarian)
        res_qaoa = bench.run_qaoa(dist_mat, sub_locs, entry, exit_n, seed)

        # 4. Multistart VNS Equal Wall-Clock Budget (given the same execution time as QAOA)
        res_equal_time = bench.run_multistart_vns_equal_time(dist_mat, sub_locs, entry, exit_n, res_qaoa["time_ms"])

        rec = {
            "test_id": test_idx,
            "seed_type": seed_type,
            "empirical_alpha": round(empirical_alpha, 3),
            "seed_cost_km": round(seed_cost, 4),
            "exact_cost_km": exact_cost,
            "exact_time_ms": exact_res["time_ms"],
            "d2opt_cost_km": res_2opt["cost_km"],
            "d2opt_time_ms": res_2opt["time_ms"],
            "reloc_cost_km": res_reloc["cost_km"],
            "reloc_time_ms": res_reloc["time_ms"],
            "swap_cost_km": res_swap["cost_km"],
            "swap_time_ms": res_swap["time_ms"],
            "oropt_cost_km": res_oropt["cost_km"],
            "oropt_time_ms": res_oropt["time_ms"],
            "vnd_cost_km": res_vnd["cost_km"],
            "vnd_time_ms": res_vnd["time_ms"],
            "vns_cost_km": res_vns["cost_km"],
            "vns_time_ms": res_vns["time_ms"],
            "qiga_cost_km": res_qiga["cost_km"],
            "qiga_time_ms": res_qiga["time_ms"],
            "qaoa_cost_km": res_qaoa["cost_km"],
            "qaoa_time_ms": res_qaoa["time_ms"],
            "equal_time_vns_cost_km": res_equal_time["cost_km"],
            "equal_time_vns_restarts": res_equal_time["restarts"],
            "qaoa_found_exact": (abs(res_qaoa["cost_km"] - exact_cost) < 1e-4),
            "vnd_found_exact": (abs(res_vnd["cost_km"] - exact_cost) < 1e-4),
            "reloc_found_exact": (abs(res_reloc["cost_km"] - exact_cost) < 1e-4),
            "d2opt_found_exact": (abs(res_2opt["cost_km"] - exact_cost) < 1e-4),
            "qaoa_beat_2opt": (res_qaoa["cost_km"] < res_2opt["cost_km"] - 1e-4),
            "qaoa_beat_vnd": (res_qaoa["cost_km"] < res_vnd["cost_km"] - 1e-4),
            "vnd_beat_qaoa": (res_vnd["cost_km"] < res_qaoa["cost_km"] - 1e-4)
        }
        records.append(rec)

        print(f"Test {test_idx:2d} (α={empirical_alpha:.2f}, {seed_type[:11]}): Seed={seed_cost:6.2f} | Exact={exact_cost:6.2f} | 2-opt={res_2opt['cost_km']:6.2f} | Reloc={res_reloc['cost_km']:6.2f} | VND={res_vnd['cost_km']:6.2f} | QAOA={res_qaoa['cost_km']:6.2f} ({res_qaoa['time_ms']:.0f}ms)")

    out_csv = os.path.join(os.path.dirname(__file__), "..", "results", "phase_s_asymmetric_neighborhoods_raw.csv")
    df = pd.DataFrame(records)
    df.to_csv(out_csv, index=False)
    print(f"\n[OK] Phase S Asymmetric Benchmark complete! Results exported to: {out_csv}")


if __name__ == "__main__":
    main()

