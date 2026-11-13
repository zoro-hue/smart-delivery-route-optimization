"""
Phase Q: Comprehensive Investigation of QAOA Improvement Potential.
Tests whether Variational QAOA (V-QAOA) with classical outer-loop optimization
can discover superior permutations over suboptimal classical heuristics on asymmetric road subproblems,
and whether reconstructed complete routes achieve measurable improvements.
"""

import sys
import os
import time
import math
import itertools
from typing import Dict, Any, List, Tuple
import numpy as np
from scipy.optimize import minimize, linear_sum_assignment

import qiskit
from qiskit import QuantumCircuit, transpile
from qiskit.circuit import Parameter
from qiskit.circuit.library import XXPlusYYGate
from qiskit_aer import AerSimulator

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app.services.optimization.classical_solver import ClassicalVRPSolver
from phase_p_autonomous_research.prototypes.common_evaluator import (
    generate_benchmark_instance, audit_solution_feasibility, ProblemInstance
)


class VariationalQAOASubproblemOptimizer:
    """
    True Variational QAOA (V-QAOA) Subproblem Optimizer with outer-loop parameter training.
    """

    def __init__(self, p: int = 1, shots: int = 1024, max_iter: int = 15):
        self.p = p
        self.shots = shots
        self.max_iter = max_iter
        self.simulator = AerSimulator()

    def build_circuit(self, K: int, qubo: dict, seed_perm: list):
        num_qubits = K * K
        qc = QuantumCircuit(num_qubits)
        gammas = [Parameter(f"gamma_{l}") for l in range(self.p)]
        betas = [Parameter(f"beta_{l}") for l in range(self.p)]

        def q_idx(i: int, p: int) -> int: return i * K + p

        # Prepare classical seed state
        for i in range(K):
            qc.x(q_idx(i, seed_perm[i]))

        # QAOA layers
        for l in range(self.p):
            for (u, v), w in qubo.items():
                if abs(w) < 1e-9: continue
                if u == v:
                    qc.rz(2.0 * gammas[l] * w, u)
                else:
                    qc.rzz(2.0 * gammas[l] * w, u, v)

            for i in range(K):
                for pos in range(K - 1):
                    q0 = q_idx(i, pos)
                    q1 = q_idx(i, pos + 1)
                    qc.append(XXPlusYYGate(2.0 * betas[l], 0.0), [q0, q1])

        qc.measure_all()
        return qc, gammas, betas

    def solve_subproblem_variational(
        self,
        cost_matrix: np.ndarray,
        entry_idx: int,
        exit_idx: int,
        sub_locs: List[int],
        seed_perm: List[int]
    ) -> Dict[str, Any]:
        """
        Executes full Variational QAOA with COBYLA/Nelder-Mead outer loop.
        """
        K = len(sub_locs)
        num_qubits = K * K
        def q_idx(i, p): return i * K + p

        # 1. Build QUBO
        qubo = {}
        penalty = float(np.max(cost_matrix) * 1.5)

        for i in range(K):
            u = q_idx(i, 0)
            qubo[(u, u)] = qubo.get((u, u), 0.0) + cost_matrix[entry_idx, sub_locs[i]]

        for i in range(K):
            u = q_idx(i, K - 1)
            qubo[(u, u)] = qubo.get((u, u), 0.0) + cost_matrix[sub_locs[i], exit_idx]

        for p in range(K - 1):
            for i in range(K):
                for j in range(K):
                    if i != j:
                        u = q_idx(i, p)
                        v = q_idx(j, p + 1)
                        key = (min(u, v), max(u, v))
                        qubo[key] = qubo.get(key, 0.0) + cost_matrix[sub_locs[i], sub_locs[j]]

        for i in range(K):
            for p in range(K):
                u = q_idx(i, p)
                qubo[(u, u)] = qubo.get((u, u), 0.0) - penalty
                for q in range(p + 1, K):
                    v = q_idx(i, q)
                    key = (min(u, v), max(u, v))
                    qubo[key] = qubo.get(key, 0.0) + 2.0 * penalty

        for p in range(K):
            for i in range(K):
                u = q_idx(i, p)
                qubo[(u, u)] = qubo.get((u, u), 0.0) - penalty
                for j in range(i + 1, K):
                    v = q_idx(j, p)
                    key = (min(u, v), max(u, v))
                    qubo[key] = qubo.get(key, 0.0) + 2.0 * penalty

        # Exact Classical Brute Force Ground Truth
        all_perms = list(itertools.permutations(range(K)))
        def perm_cost(p_list):
            c = cost_matrix[entry_idx, sub_locs[p_list[0]]]
            for idx in range(len(p_list) - 1):
                c += cost_matrix[sub_locs[p_list[idx]], sub_locs[p_list[idx+1]]]
            c += cost_matrix[sub_locs[p_list[-1]], exit_idx]
            return c

        all_costs = [(p, perm_cost(p)) for p in all_perms]
        exact_opt_perm, exact_opt_cost = min(all_costs, key=lambda kv: kv[1])
        exact_max_perm, exact_max_cost = max(all_costs, key=lambda kv: kv[1])
        seed_cost = perm_cost(seed_perm)

        # Build QAOA circuit
        qc, gammas, betas = self.build_circuit(K, qubo, seed_perm)
        transpiled_qc = transpile(qc, self.simulator)

        # Classical objective for COBYLA optimizer: expected Hamiltonian energy
        eval_counts = {"evals": 0}

        def energy_obj(params):
            eval_counts["evals"] += 1
            param_dict = {}
            for l in range(self.p):
                param_dict[gammas[l]] = params[2 * l]
                param_dict[betas[l]] = params[2 * l + 1]

            bound = transpiled_qc.assign_parameters(param_dict)
            job = self.simulator.run(bound, shots=256)
            counts = job.result().get_counts()

            # Compute expected energy
            total_e = 0.0
            for bstr, cnt in counts.items():
                rb = [int(b) for b in reversed(bstr)]
                # decode permutation via Hungarian
                mat = np.zeros((K, K))
                for i in range(K):
                    for p in range(K):
                        mat[i, p] = rb[q_idx(i, p)]
                r_ind, c_ind = linear_sum_assignment(1.0 - mat)
                decoded_perm = [0] * K
                for r, c in zip(r_ind, c_ind):
                    decoded_perm[c] = r
                total_e += perm_cost(decoded_perm) * cnt

            return total_e / 256.0

        # Run variational optimization
        init_params = [0.15 * math.pi / max(1.0, float(np.max(cost_matrix))), 0.35 * math.pi]
        res_opt = minimize(energy_obj, init_params, method="COBYLA", options={"maxiter": self.max_iter})
        optimal_params = res_opt.x

        # Final high-shot measurement with optimal parameters
        final_dict = {gammas[0]: optimal_params[0], betas[0]: optimal_params[1]}
        final_bound = transpiled_qc.assign_parameters(final_dict)
        final_job = self.simulator.run(final_bound, shots=self.shots)
        final_counts = final_job.result().get_counts()

        # Extract best candidate sampled
        best_sampled_perm = None
        best_sampled_cost = float("inf")

        for bstr, cnt in final_counts.items():
            rb = [int(b) for b in reversed(bstr)]
            mat = np.zeros((K, K))
            for i in range(K):
                for p in range(K):
                    mat[i, p] = rb[q_idx(i, p)]
            r_ind, c_ind = linear_sum_assignment(1.0 - mat)
            cand_perm = [0] * K
            for r, c in zip(r_ind, c_ind):
                cand_perm[c] = r
            c_cost = perm_cost(cand_perm)
            if c_cost < best_sampled_cost:
                best_sampled_cost = c_cost
                best_sampled_perm = cand_perm

        improved = (best_sampled_cost < seed_cost - 1e-4)
        found_global_opt = (abs(best_sampled_cost - exact_opt_cost) < 1e-4)

        return {
            "seed_perm": seed_perm,
            "seed_cost": round(seed_cost, 3),
            "exact_opt_perm": list(exact_opt_perm),
            "exact_opt_cost": round(exact_opt_cost, 3),
            "qaoa_perm": best_sampled_perm,
            "qaoa_cost": round(best_sampled_cost, 3),
            "improved": improved,
            "found_global_opt": found_global_opt,
            "improvement_km": round(seed_cost - best_sampled_cost, 3),
            "variational_evals": eval_counts["evals"],
            "optimal_gamma": round(float(optimal_params[0]), 5),
            "optimal_beta": round(float(optimal_params[1]), 5)
        }


def run_controlled_subproblem_benchmark():
    print("=" * 80)
    print("PHASE Q: CONTROLLED SUBPROBLEM BENCHMARK (SUBOPTIMAL HEURISTIC SEEDS)")
    print("=" * 80)

    optimizer = VariationalQAOASubproblemOptimizer(p=1, shots=1024, max_iter=12)
    records = []

    # Test 10 distinct asymmetric instances with intentionally suboptimal starting seeds
    for test_id in range(1, 11):
        np.random.seed(100 + test_id)
        # Create asymmetric Manhattan-like cost matrix for 6 nodes (depot, 4 customers, return)
        cost_mat = np.random.uniform(5.0, 30.0, (6, 6))
        # Add strong asymmetry to simulate one-way traffic
        for i in range(6):
            for j in range(6):
                if i != j:
                    cost_mat[i, j] += np.random.uniform(-5.0, 15.0)
                    cost_mat[i, j] = max(2.0, cost_mat[i, j])
        np.fill_diagonal(cost_mat, 0.0)

        entry = 0
        exit_n = 5
        sub_locs = [1, 2, 3, 4]

        # Generate a naive/suboptimal starting order (e.g. reverse or worst-fit)
        all_perms = list(itertools.permutations(range(4)))
        def perm_cost(p):
            c = cost_mat[entry, sub_locs[p[0]]]
            for idx in range(len(p) - 1):
                c += cost_mat[sub_locs[p[idx]], sub_locs[p[idx+1]]]
            c += cost_mat[sub_locs[p[-1]], exit_n]
            return c

        sorted_perms = sorted(all_perms, key=perm_cost)
        # Select a suboptimal seed (e.g. the 15th to 20th worst permutation)
        suboptimal_seed = list(sorted_perms[min(18, len(sorted_perms) - 1)])

        res = optimizer.solve_subproblem_variational(
            cost_matrix=cost_mat,
            entry_idx=entry,
            exit_idx=exit_n,
            sub_locs=sub_locs,
            seed_perm=suboptimal_seed
        )

        records.append({
            "test_id": test_id,
            "seed_cost_km": res["seed_cost"],
            "exact_opt_cost_km": res["exact_opt_cost"],
            "qaoa_cost_km": res["qaoa_cost"],
            "improved": res["improved"],
            "found_global_opt": res["found_global_opt"],
            "improvement_km": res["improvement_km"],
            "pct_improved": round((res["seed_cost"] - res["qaoa_cost"]) / res["seed_cost"] * 100.0, 2)
        })

        print(f"Test {test_id:2d}: Seed Cost = {res['seed_cost']:6.2f} km | QAOA Cost = {res['qaoa_cost']:6.2f} km | Exact Opt = {res['exact_opt_cost']:6.2f} km | Improved: {res['improved']} | Found Global Opt: {res['found_global_opt']}")

    import pandas as pd
    df = pd.DataFrame(records)
    csv_file = os.path.join(os.path.dirname(__file__), "..", "results", "phase_q_subproblem_improvement_raw.csv")
    os.makedirs(os.path.dirname(csv_file), exist_ok=True)
    df.to_csv(csv_file, index=False)
    print(f"\n[OK] Raw results saved to: {csv_file}")
    print(f"Overall Improvement Rate: {df['improved'].mean() * 100:.1f}%")
    print(f"Global Optimum Discovery Rate: {df['found_global_opt'].mean() * 100:.1f}%")
    print(f"Mean Cost Reduction: {df['improvement_km'].mean():.2f} km ({df['pct_improved'].mean():.2f}%)")


if __name__ == "__main__":
    run_controlled_subproblem_benchmark()

