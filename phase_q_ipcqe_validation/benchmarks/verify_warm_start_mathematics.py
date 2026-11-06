"""
Phase Q: Mathematical Audit of Warm-Start QAOA & XY Mixers.
Empirically tests the valid permutation yield, row/column constraint preservation,
and Hungarian projection behavior across initial states, beta angles, and random seeds.
"""

import sys
import os
import time
import math
import numpy as np
from scipy.optimize import linear_sum_assignment

import qiskit
from qiskit import QuantumCircuit, transpile
from qiskit.circuit import Parameter
from qiskit.circuit.library import XXPlusYYGate
from qiskit_aer import AerSimulator


def build_audit_circuit(
    K: int,
    qubo: dict,
    initial_state_type: str,
    seed_perm: list,
    p: int = 1,
    mixer_type: str = "xy"
) -> Tuple[QuantumCircuit, list, list]:
    num_qubits = K * K
    qc = QuantumCircuit(num_qubits)
    gammas = [Parameter(f"gamma_{l}") for l in range(p)]
    betas = [Parameter(f"beta_{l}") for l in range(p)]

    def q_idx(i: int, p: int) -> int:
        return i * K + p

    # State Preparation
    if initial_state_type == "classical_seed":
        for i in range(K):
            pos = seed_perm[i]
            qc.x(q_idx(i, pos))
    elif initial_state_type == "perturbed_seed":
        # Swap first two elements of seed
        pert_perm = list(seed_perm)
        pert_perm[0], pert_perm[1] = pert_perm[1], pert_perm[0]
        for i in range(K):
            pos = pert_perm[i]
            qc.x(q_idx(i, pos))
    elif initial_state_type == "uniform":
        qc.h(range(num_qubits))

    # Alternating QAOA Layers
    for l in range(p):
        # Cost Hamiltonian
        for (u, v), weight in qubo.items():
            if abs(weight) < 1e-9:
                continue
            if u == v:
                qc.rz(2.0 * gammas[l] * weight, u)
            else:
                qc.rzz(2.0 * gammas[l] * weight, u, v)

        # Mixer
        if mixer_type == "xy":
            # Phase P XY hopping mixer on adjacent positions
            for i in range(K):
                for pos in range(K - 1):
                    q0 = q_idx(i, pos)
                    q1 = q_idx(i, pos + 1)
                    qc.append(XXPlusYYGate(2.0 * betas[l], 0.0), [q0, q1])
        elif mixer_type == "transverse":
            for q in range(num_qubits):
                qc.rx(2.0 * betas[l], q)

    qc.measure_all()
    return qc, gammas, betas


def audit_permutations():
    print("=" * 80)
    print("PHASE Q: AUDIT OF WARM-START QAOA & XY MIXER MATHEMATICAL PRESERVATION")
    print("=" * 80)

    K = 4
    simulator = AerSimulator()
    seed_perm = [0, 1, 2, 3]

    # Generate synthetic 4x4 ATSP cost matrix
    np.random.seed(42)
    dist = np.random.uniform(5.0, 25.0, (K, K))
    np.fill_diagonal(dist, 0.0)

    # Build standard QUBO
    qubo = {}
    penalty = 40.0
    def q_idx(i, p): return i * K + p

    for p in range(K - 1):
        for i in range(K):
            for j in range(K):
                if i != j:
                    u = q_idx(i, p)
                    v = q_idx(j, p + 1)
                    key = (min(u, v), max(u, v))
                    qubo[key] = qubo.get(key, 0.0) + dist[i, j]

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

    test_configs = [
        {"state": "uniform", "mixer": "transverse", "beta_frac": 0.35, "desc": "Standard Uniform + Transverse"},
        {"state": "classical_seed", "mixer": "transverse", "beta_frac": 0.35, "desc": "Classical Seed + Transverse"},
        {"state": "classical_seed", "mixer": "xy", "beta_frac": 0.05, "desc": "Classical Seed + XY (Beta=0.05pi - Near Identity)"},
        {"state": "classical_seed", "mixer": "xy", "beta_frac": 0.20, "desc": "Classical Seed + XY (Beta=0.20pi)"},
        {"state": "classical_seed", "mixer": "xy", "beta_frac": 0.35, "desc": "Classical Seed + XY (Beta=0.35pi - Phase P Default)"},
        {"state": "classical_seed", "mixer": "xy", "beta_frac": 0.50, "desc": "Classical Seed + XY (Beta=0.50pi - Strong Mixing)"},
        {"state": "perturbed_seed", "mixer": "xy", "beta_frac": 0.35, "desc": "Perturbed Seed + XY (Beta=0.35pi)"}
    ]

    gamma_val = 0.15 * math.pi / float(np.max(dist))
    shots = 2048
    results_table = []

    for cfg in test_configs:
        beta_val = cfg["beta_frac"] * math.pi
        qc, gammas, betas = build_audit_circuit(
            K=K, qubo=qubo, initial_state_type=cfg["state"],
            seed_perm=seed_perm, p=1, mixer_type=cfg["mixer"]
        )

        bound_qc = qc.assign_parameters({gammas[0]: gamma_val, betas[0]: beta_val})
        transpiled_qc = transpile(bound_qc, simulator)
        job = simulator.run(transpiled_qc, shots=shots)
        counts = job.result().get_counts()

        total_shots = shots
        row_valid_count = 0
        col_valid_count = 0
        both_valid_count = 0
        projection_deltas = []

        for bitstr, cnt in counts.items():
            raw_bits = [int(b) for b in reversed(bitstr)]
            mat = np.zeros((K, K), dtype=int)
            for i in range(K):
                for p in range(K):
                    mat[i, p] = raw_bits[q_idx(i, p)]

            # Row check (each customer has exactly 1 visit)
            row_sums = mat.sum(axis=1)
            is_row_valid = np.all(row_sums == 1)

            # Column check (each step has exactly 1 customer)
            col_sums = mat.sum(axis=0)
            is_col_valid = np.all(col_sums == 1)

            is_both = is_row_valid and is_col_valid

            if is_row_valid:
                row_valid_count += cnt
            if is_col_valid:
                col_valid_count += cnt
            if is_both:
                both_valid_count += cnt

            # Hungarian projection delta
            cost_mat = 1.0 - mat.astype(float)
            r_ind, c_ind = linear_sum_assignment(cost_mat)
            proj_mat = np.zeros((K, K), dtype=int)
            for r, c in zip(r_ind, c_ind):
                proj_mat[r, c] = 1

            delta = np.sum(np.abs(mat - proj_mat)) // 2
            projection_deltas.extend([delta] * cnt)

        pct_row = (row_valid_count / total_shots) * 100.0
        pct_col = (col_valid_count / total_shots) * 100.0
        pct_both = (both_valid_count / total_shots) * 100.0
        avg_delta = float(np.mean(projection_deltas))

        results_table.append({
            "config": cfg["desc"],
            "state": cfg["state"],
            "mixer": cfg["mixer"],
            "beta": cfg["beta_frac"],
            "row_valid_pct": round(pct_row, 2),
            "col_valid_pct": round(pct_col, 2),
            "strict_perm_valid_pct": round(pct_both, 2),
            "avg_proj_delta": round(avg_delta, 3)
        })

        print(f"\n[{cfg['desc']}]")
        print(f"  Row Valid (sum_p x_ip = 1):      {pct_row:6.2f}%")
        print(f"  Col Valid (sum_i x_ip = 1):      {pct_col:6.2f}%")
        print(f"  Strict Valid Permutations:       {pct_both:6.2f}%")
        print(f"  Avg Hungarian Projection Delta:  {avg_delta:6.3f} bits")

    # Save results
    import pandas as pd
    csv_path = os.path.join(os.path.dirname(__file__), "..", "results", "phase_q_warm_start_audit_raw.csv")
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    pd.DataFrame(results_table).to_csv(csv_path, index=False)
    print(f"\n[OK] Raw audit results saved to: {csv_path}")


if __name__ == "__main__":
    audit_permutations()

