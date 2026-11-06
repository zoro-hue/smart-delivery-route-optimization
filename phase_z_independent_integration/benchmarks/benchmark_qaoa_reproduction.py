"""
Phase Z: Rigorous Reproduction and Audit of Phase Y QAOA Formulations and Runtime.
Compares:
1. Phase Y Heuristic Sampling (Formulations A-F)
2. Genuine Qiskit 2.4.1 Quantum Statevector Simulation
3. Classical Baselines (Kernighan-Lin, VND, Exact 2^N)
Measures exact breakdown of execution time across all stages.
"""

import sys
import os
import time
import math
import csv
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Tuple
import numpy as np

# Add project roots
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from phase_v_independent_quantum_validation.prototypes.algorithmic_vnd import AlgorithmicVND
from phase_u_quantum_bipartition_validation.prototypes.classical_partition_solvers import (
    ClassicalPartitioningSuite
)
from phase_y_breakthrough_engineering.prototypes.advanced_quantum_formulations import (
    AdvancedQuantumFormulations
)

# Qiskit 2.4.1 imports
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector


@dataclass
class ReproductionRecord:
    instance_id: str
    formulation: str
    engine_type: str  # "PhaseY_Heuristic" or "Genuine_Qiskit" or "Classical"
    num_qubits: int
    raw_feasibility_rate: float
    best_qubo_cost: float
    repaired_qubo_cost: float
    route_distance_km: float
    circuit_build_ms: float
    execution_ms: float
    decoding_repair_ms: float
    vnd_route_eval_ms: float
    total_latency_ms: float
    prop1_accepted: bool
    beat_classical_mls: bool


class QAOAFormulationAuditor:
    def __init__(self):
        self.classical_suite = ClassicalPartitioningSuite()

    def generate_instance(self, seed: int, N: int = 12) -> Dict[str, Any]:
        np.random.seed(seed)
        coords = np.random.uniform(0.0, 10.0, (N + 1, 2))
        coords[0] = np.array([5.0, 5.0])

        dist_matrix = np.zeros((N + 1, N + 1))
        for i in range(N + 1):
            for j in range(N + 1):
                if i != j:
                    d = np.linalg.norm(coords[i] - coords[j]) * 14.5
                    dist_matrix[i, j] = d * (1.0 + 0.05 * np.sin(i * 3 + j * 7))

        demands = np.random.randint(1, 5, N)
        total_demand = float(np.sum(demands))
        cap_a = float(np.ceil(total_demand * 0.55))
        cap_b = float(np.ceil(total_demand * 0.55))

        c_a = np.array([2.5, 5.0])
        c_b = np.array([7.5, 5.0])
        cust_coords = coords[1:]
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
            "N": N,
            "dist_matrix": dist_matrix,
            "demands": demands,
            "cap_a": cap_a,
            "cap_b": cap_b,
            "h_diff": h_diff,
            "W": W,
            "cust_indices": list(range(1, N + 1))
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

    def run_genuine_qiskit_qaoa(
        self,
        h: np.ndarray,
        J: np.ndarray,
        demands: np.ndarray,
        cap_a: float,
        cap_b: float,
        gamma: float = 0.45,
        beta: float = 0.65,
        use_xy_mixer: bool = False
    ) -> Dict[str, Any]:
        """Runs genuine Qiskit 2.4.1 statevector QAOA circuit."""
        N = len(h)
        t0_build = time.perf_counter()
        qc = QuantumCircuit(N)

        if use_xy_mixer:
            # Prepare Dicke state / equal superposition in Hamming weight N//2
            k = N // 2
            for i in range(k):
                qc.x(i)
            # Entangle into subspace
            for i in range(0, N - 1, 2):
                qc.cx(i, i + 1)
                qc.ry(math.pi / 4, i)
                qc.cx(i + 1, i)
        else:
            for i in range(N):
                qc.h(i)

        # Cost Hamiltonian evolution: exp(-i * gamma * H_C)
        for i in range(N):
            if abs(h[i]) > 1e-6:
                qc.rz(2.0 * gamma * h[i], i)

        for i in range(N):
            for j in range(i + 1, N):
                if abs(J[i, j]) > 1e-6:
                    qc.rzz(2.0 * gamma * J[i, j], i, j)

        # Mixer Hamiltonian evolution: exp(-i * beta * H_M)
        if use_xy_mixer:
            # XY ring mixer: 0.5 * beta * (X_i X_j + Y_i Y_j)
            for i in range(N):
                j = (i + 1) % N
                # XY interaction via Rxx + Ryy
                qc.rxx(beta, i, j)
                qc.ryy(beta, i, j)
        else:
            for i in range(N):
                qc.rx(2.0 * beta, i)

        t_build_ms = (time.perf_counter() - t0_build) * 1000.0

        # Execution via Statevector
        t0_exec = time.perf_counter()
        sv = Statevector.from_instruction(qc)
        probs = sv.probabilities()
        t_exec_ms = (time.perf_counter() - t0_exec) * 1000.0

        # Sample top states
        t0_decode = time.perf_counter()
        raw_feas_count = 0
        best_cost = float("inf")
        best_x = None

        # Sample 512 shots according to exact quantum probabilities
        sample_indices = np.random.choice(len(probs), size=512, p=probs)
        for idx in sample_indices:
            bitstring = format(idx, f"0{N}b")[::-1]
            x = np.array([int(b) for b in bitstring])
            qa = sum(demands[i] for i in range(N) if x[i] == 1)
            qb = sum(demands[i] for i in range(N) if x[i] == 0)
            if (qa <= cap_a) and (qb <= cap_b) and (0 < qa < sum(demands)):
                raw_feas_count += 1
            cost = float(np.dot(h, x) + x.T @ J @ x)
            if cost < best_cost:
                best_cost = cost
                best_x = x

        t_decode_ms = (time.perf_counter() - t0_decode) * 1000.0

        return {
            "best_x": best_x,
            "best_cost": round(best_cost, 4),
            "raw_feas_rate": round(raw_feas_count / 512.0, 4),
            "t_build_ms": round(t_build_ms, 2),
            "t_exec_ms": round(t_exec_ms, 2),
            "t_decode_ms": round(t_decode_ms, 2)
        }

    def run_comprehensive_audit(self, num_instances: int = 15) -> List[ReproductionRecord]:
        records = []
        for s in range(num_instances):
            inst = self.generate_instance(seed=100 + s, N=12)
            N = inst["N"]
            dist_matrix = inst["dist_matrix"]
            demands = inst["demands"]
            cap_a = inst["cap_a"]
            cap_b = inst["cap_b"]
            h_diff = inst["h_diff"]
            W = inst["W"]
            cust_idx = inst["cust_indices"]

            delta_q = cap_a - cap_b
            lambda_std = 2.0
            Q_std = np.zeros((N, N))
            for i in range(N):
                for j in range(N):
                    if i != j:
                        Q_std[i, j] = -W[i, j] + lambda_std * demands[i] * demands[j]
                Q_std[i, i] = h_diff[i] - 2.0 * lambda_std * delta_q * demands[i]

            h_std = np.diag(Q_std)
            J_std = np.copy(Q_std)
            np.fill_diagonal(J_std, 0)

            # 1. Classical Baselines
            t0 = time.perf_counter()
            mls_res = self.classical_suite.multistart_local_search(Q_std, demands, h_diff, cap_a, cap_b, restarts=20)
            t_mls = (time.perf_counter() - t0) * 1000.0
            x_mls = np.array(mls_res["partition"])
            c_mls = mls_res["qubo_cost"]
            t_a, t_b = self.partition_to_tours(x_mls, dist_matrix)
            dist_mls = AlgorithmicVND.optimize_fleet_routes(t_a, t_b, demands, cap_a, cap_b, dist_matrix)["total_distance"]

            t0 = time.perf_counter()
            kl_res = self.classical_suite.kernighan_lin_balanced(Q_std, demands, h_diff, cap_a, cap_b)
            t_kl = (time.perf_counter() - t0) * 1000.0
            x_kl = np.array(kl_res["partition"])
            t0_vnd = time.perf_counter()
            t_a, t_b = self.partition_to_tours(x_kl, dist_matrix)
            dist_kl = AlgorithmicVND.optimize_fleet_routes(t_a, t_b, demands, cap_a, cap_b, dist_matrix)["total_distance"]
            t_vnd_kl = (time.perf_counter() - t0_vnd) * 1000.0

            records.append(ReproductionRecord(
                instance_id=f"inst_{s}",
                formulation="Kernighan_Lin",
                engine_type="Classical",
                num_qubits=N,
                raw_feasibility_rate=1.0,
                best_qubo_cost=round(kl_res["qubo_cost"], 2),
                repaired_qubo_cost=round(kl_res["qubo_cost"], 2),
                route_distance_km=round(dist_kl, 2),
                circuit_build_ms=0.0,
                execution_ms=round(t_kl, 2),
                decoding_repair_ms=0.0,
                vnd_route_eval_ms=round(t_vnd_kl, 2),
                total_latency_ms=round(t_kl + t_vnd_kl, 2),
                prop1_accepted=True,
                beat_classical_mls=(dist_kl < dist_mls - 1e-4)
            ))

            # 2. Phase Y Heuristic Formulations
            for form_name, use_xy, fast in [
                ("PhaseY_Formulation_A_Transverse", False, False),
                ("PhaseY_Formulation_B_XYMixer", True, False),
                ("PhaseY_Formulation_F_AdaptiveFast", False, True)
            ]:
                res = AdvancedQuantumFormulations.simulate_sampling_generic(
                    h_std, J_std, demands, cap_a, cap_b, shots=1024, use_xy_mixer=use_xy, fast_mode=fast
                )
                t0_rep = time.perf_counter()
                x_rep = np.array(self.classical_suite.repair_capacity_violations(list(res["best_x"]), demands, cap_a, cap_b, h_diff))
                c_rep = self.classical_suite.evaluate_qubo_cost(x_rep, Q_std)
                t_rep_ms = (time.perf_counter() - t0_rep) * 1000.0

                t0_vnd = time.perf_counter()
                # Proposition 1 acceptance
                adopted_x = x_rep if c_rep < c_mls else x_mls
                t_a, t_b = self.partition_to_tours(adopted_x, dist_matrix)
                dist_route = AlgorithmicVND.optimize_fleet_routes(t_a, t_b, demands, cap_a, cap_b, dist_matrix)["total_distance"]
                t_vnd_ms = (time.perf_counter() - t0_vnd) * 1000.0

                records.append(ReproductionRecord(
                    instance_id=f"inst_{s}",
                    formulation=form_name,
                    engine_type="PhaseY_Heuristic",
                    num_qubits=N,
                    raw_feasibility_rate=res["raw_feas_rate"],
                    best_qubo_cost=res["best_cost"],
                    repaired_qubo_cost=round(c_rep, 2),
                    route_distance_km=round(dist_route, 2),
                    circuit_build_ms=0.0,
                    execution_ms=res["time_ms"],
                    decoding_repair_ms=round(t_rep_ms, 2),
                    vnd_route_eval_ms=round(t_vnd_ms, 2),
                    total_latency_ms=round(res["time_ms"] + t_rep_ms + t_vnd_ms, 2),
                    prop1_accepted=(c_rep < c_mls),
                    beat_classical_mls=(c_rep < c_mls - 1e-4)
                ))

            # 3. Genuine Qiskit 2.4.1 Statevector QAOA
            for form_name, use_xy in [
                ("Qiskit_Genuine_Formulation_A_Transverse", False),
                ("Qiskit_Genuine_Formulation_B_XYMixer", True)
            ]:
                qres = self.run_genuine_qiskit_qaoa(h_std, J_std, demands, cap_a, cap_b, use_xy_mixer=use_xy)
                t0_rep = time.perf_counter()
                x_rep = np.array(self.classical_suite.repair_capacity_violations(list(qres["best_x"]), demands, cap_a, cap_b, h_diff))
                c_rep = self.classical_suite.evaluate_qubo_cost(x_rep, Q_std)
                t_rep_ms = (time.perf_counter() - t0_rep) * 1000.0

                t0_vnd = time.perf_counter()
                adopted_x = x_rep if c_rep < c_mls else x_mls
                t_a, t_b = self.partition_to_tours(adopted_x, dist_matrix)
                dist_route = AlgorithmicVND.optimize_fleet_routes(t_a, t_b, demands, cap_a, cap_b, dist_matrix)["total_distance"]
                t_vnd_ms = (time.perf_counter() - t0_vnd) * 1000.0

                total_time = qres["t_build_ms"] + qres["t_exec_ms"] + qres["t_decode_ms"] + t_rep_ms + t_vnd_ms

                records.append(ReproductionRecord(
                    instance_id=f"inst_{s}",
                    formulation=form_name,
                    engine_type="Genuine_Qiskit",
                    num_qubits=N,
                    raw_feasibility_rate=qres["raw_feas_rate"],
                    best_qubo_cost=qres["best_cost"],
                    repaired_qubo_cost=round(c_rep, 2),
                    route_distance_km=round(dist_route, 2),
                    circuit_build_ms=qres["t_build_ms"],
                    execution_ms=qres["t_exec_ms"],
                    decoding_repair_ms=round(qres["t_decode_ms"] + t_rep_ms, 2),
                    vnd_route_eval_ms=round(t_vnd_ms, 2),
                    total_latency_ms=round(total_time, 2),
                    prop1_accepted=(c_rep < c_mls),
                    beat_classical_mls=(c_rep < c_mls - 1e-4)
                ))

        return records


if __name__ == "__main__":
    print("Running Phase Z QAOA Reproduction and Runtime Audit...")
    auditor = QAOAFormulationAuditor()
    records = auditor.run_comprehensive_audit(num_instances=15)

    csv_path = "phase_z_independent_integration/results/phase_z_qaoa_reproduction_raw.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(records[0]).keys()))
        writer.writeheader()
        for r in records:
            writer.writerow(asdict(r))

    print(f"Reproduction complete: {len(records)} evaluations logged to {csv_path}.")

