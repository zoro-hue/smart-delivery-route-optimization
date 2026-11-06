"""
Prototype 1: Classical-Seeded Warm-Start QAOA with XY Mixers (Architecture 1).
Implements exact permutation encoding into Qiskit Aer statevectors, XY hopping mixers,
and Kuhn-Munkres post-measurement Hungarian projection.
"""

import sys
import os
import time
import math
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
from scipy.optimize import linear_sum_assignment

import qiskit
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.circuit.library import XXPlusYYGate
from qiskit_aer import AerSimulator

# Add backend to path for classical solver imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend")))
from app.services.optimization.classical_solver import ClassicalVRPSolver
from phase_p_autonomous_research.prototypes.common_evaluator import (
    ProblemInstance, audit_solution_feasibility
)


class ClassicalSeededQAOASolver:
    """
    Architecture 1: Classical-Seeded Warm-Start QAOA Solver.
    """

    def __init__(self, p: int = 1, shots: int = 1024):
        self.p = p
        self.shots = shots
        self.simulator = AerSimulator()
        self.classical_solver = ClassicalVRPSolver()

    def solve_microcluster_warm_start(
        self,
        sub_nodes: List[Dict[str, Any]],
        entry_node: Dict[str, Any],
        exit_node: Dict[str, Any],
        dist_matrix: np.ndarray,
        loc_indices: Dict[str, int],
        classical_seed_order: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Executes warm-start QAOA on K=4 subproblem using XY hopping mixers.
        """
        K = len(sub_nodes)
        if K <= 1:
            return {"ordered_nodes": sub_nodes, "qaoa_used": False, "cost_delta": 0.0}

        t0 = time.perf_counter()
        entry_idx = loc_indices[entry_node["id"]]
        exit_idx = loc_indices[exit_node["id"]]
        sub_locs = [loc_indices[n["id"]] for n in sub_nodes]

        # 1. Classical seed permutation
        if classical_seed_order is None:
            # Default identity order
            seed_perm = list(range(K))
        else:
            seed_perm = classical_seed_order

        # 2. Build QUBO / Ising Hamiltonian for ATSP
        num_qubits = K * K
        def q_idx(i: int, p: int) -> int:
            return i * K + p

        qubo = {}
        # Entry cost to step 0
        for i in range(K):
            u = q_idx(i, 0)
            qubo[(u, u)] = qubo.get((u, u), 0.0) + dist_matrix[entry_idx, sub_locs[i]]

        # Exit cost from step K-1
        for i in range(K):
            u = q_idx(i, K - 1)
            qubo[(u, u)] = qubo.get((u, u), 0.0) + dist_matrix[sub_locs[i], exit_idx]

        # Inter-node directed transitions step p -> p+1
        for p in range(K - 1):
            for i in range(K):
                for j in range(K):
                    if i != j:
                        u = q_idx(i, p)
                        v = q_idx(j, p + 1)
                        cost = dist_matrix[sub_locs[i], sub_locs[j]]
                        key = (min(u, v), max(u, v))
                        qubo[key] = qubo.get(key, 0.0) + cost

        # Degree constraint penalty
        penalty = float(np.max(dist_matrix) * 1.5)
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

        # 3. Build Quantum Circuit with Warm-Start Initialization
        qc = QuantumCircuit(num_qubits)
        gammas = [Parameter(f"gamma_{l}") for l in range(self.p)]
        betas = [Parameter(f"beta_{l}") for l in range(self.p)]

        # Prepare Warm-Start state |x_seed>
        for i in range(K):
            p_seed = seed_perm[i]
            qubit_to_flip = q_idx(i, p_seed)
            qc.x(qubit_to_flip)

        # Alternating QAOA Layers with XY hopping mixer
        for l in range(self.p):
            # Problem Unitary e^{-i gamma H_C}
            for (u, v), weight in qubo.items():
                if abs(weight) < 1e-9:
                    continue
                if u == v:
                    qc.rz(2.0 * gammas[l] * weight, u)
                else:
                    qc.rzz(2.0 * gammas[l] * weight, u, v)

            # XY Hopping Mixer on adjacent step qubits within each customer row
            for i in range(K):
                for p in range(K - 1):
                    q0 = q_idx(i, p)
                    q1 = q_idx(i, p + 1)
                    qc.append(XXPlusYYGate(2.0 * betas[l], 0.0), [q0, q1])

        qc.measure_all()

        # 4. Bind parameters and execute on Qiskit Aer
        from qiskit import transpile
        bound_qc = qc.assign_parameters({
            gammas[0]: 0.15 * math.pi / max(1.0, float(np.max(dist_matrix))),
            betas[0]: 0.35 * math.pi
        })
        transpiled_qc = transpile(bound_qc, self.simulator)

        t_sim_start = time.perf_counter()
        job = self.simulator.run(transpiled_qc, shots=self.shots)
        result = job.result()
        counts = result.get_counts()
        t_sim_ms = (time.perf_counter() - t_sim_start) * 1000.0

        # 5. Decode bitstrings and apply Hungarian projection
        best_bitstring = max(counts.items(), key=lambda kv: kv[1])[0]
        # Qiskit bitstring order is reversed: bit 0 is at right end
        raw_bits = [int(b) for b in reversed(best_bitstring)]

        # Reshape to K x K matrix
        mat = np.zeros((K, K), dtype=float)
        for i in range(K):
            for p in range(K):
                mat[i, p] = raw_bits[q_idx(i, p)]

        # Hungarian projection
        cost_mat = 1.0 - mat
        row_ind, col_ind = linear_sum_assignment(cost_mat)
        # col_ind[i] is the position assigned to node i
        # Invert to get node at position p
        perm = [0] * K
        for i, p in zip(row_ind, col_ind):
            perm[p] = i

        ordered_nodes = [sub_nodes[idx] for idx in perm]
        total_time_ms = (time.perf_counter() - t0) * 1000.0

        # Calculate tour cost of seed vs QAOA
        def eval_cost(nodes_list):
            c = dist_matrix[entry_idx, loc_indices[nodes_list[0]["id"]]]
            for idx in range(len(nodes_list) - 1):
                c += dist_matrix[loc_indices[nodes_list[idx]["id"]], loc_indices[nodes_list[idx+1]["id"]]]
            c += dist_matrix[loc_indices[nodes_list[-1]["id"]], exit_idx]
            return c

        seed_nodes = [sub_nodes[i] for i in seed_perm]
        seed_cost = eval_cost(seed_nodes)
        qaoa_cost = eval_cost(ordered_nodes)

        # Monotonic check
        if qaoa_cost <= seed_cost:
            final_nodes = ordered_nodes
            final_cost = qaoa_cost
            improved = (qaoa_cost < seed_cost - 1e-4)
        else:
            final_nodes = seed_nodes
            final_cost = seed_cost
            improved = False

        return {
            "ordered_nodes": final_nodes,
            "qaoa_used": True,
            "seed_cost_km": round(seed_cost, 3),
            "final_cost_km": round(final_cost, 3),
            "improved": improved,
            "sim_time_ms": round(t_sim_ms, 2),
            "total_time_ms": round(total_time_ms, 2),
            "shots": self.shots,
            "qubits": num_qubits
        }

    def solve_instance(self, instance: ProblemInstance) -> Dict[str, Any]:
        """
        Solves complete delivery instance using Architecture 1:
        Classical OR-Tools initial solution -> QAOA warm-start optimization on sub-tours.
        """
        t_global_start = time.perf_counter()

        # Step 1: Classical OR-Tools solution
        res_class = self.classical_solver.solve_ortools(
            distance_matrix=instance.distance_matrix,
            num_vehicles=instance.num_vehicles,
            depot=0,
            demands=[int(instance.depot["demand"])] + [int(c["demand"]) for c in instance.customers],
            vehicle_capacities=[int(instance.vehicle_capacity)] * instance.num_vehicles,
            time_limit_sec=10
        )

        routes = res_class.get("routes", [])
        t_class_ms = res_class.get("execution_time_sec", 0.0) * 1000.0

        # Step 2: Convert node index routes to customer object routes
        all_nodes = [instance.depot] + instance.customers
        customer_routes = []
        qaoa_calls = 0
        qaoa_improvements = 0
        total_qaoa_time_ms = 0.0

        for r_entry in routes:
            if isinstance(r_entry, dict):
                inner_indices = [int(idx) for idx in r_entry.get("customer_stops", []) if int(idx) != 0]
            else:
                inner_indices = [int(idx) for idx in r_entry if int(idx) != 0]

            if not inner_indices:
                continue

            route_customers = [all_nodes[idx] for idx in inner_indices]

            # If route length >= 4, extract K=4 bottleneck subproblem
            if len(route_customers) >= 4:
                sub = route_customers[:4]
                rest = route_customers[4:]
                entry = instance.depot
                exit_node = rest[0] if rest else instance.depot

                q_res = self.solve_microcluster_warm_start(
                    sub_nodes=sub,
                    entry_node=entry,
                    exit_node=exit_node,
                    dist_matrix=instance.distance_matrix,
                    loc_indices=instance.location_indices
                )
                qaoa_calls += 1
                total_qaoa_time_ms += q_res["total_time_ms"]
                if q_res["improved"]:
                    qaoa_improvements += 1

                route_customers = q_res["ordered_nodes"] + rest

            customer_routes.append(route_customers)

        total_wall_ms = (time.perf_counter() - t_global_start) * 1000.0
        feasibility = audit_solution_feasibility(instance, customer_routes)

        return {
            "prototype": "Proto_1_Classical_Seeded_QAOA",
            "is_feasible": feasibility["is_feasible"],
            "total_distance_km": feasibility["total_distance_km"],
            "classical_initial_distance_km": round(res_class.get("total_distance_km", 0.0), 3),
            "improvement_over_classical_pct": round(
                (res_class.get("total_distance_km", 0.0) - feasibility["total_distance_km"]) /
                max(1e-4, res_class.get("total_distance_km", 1.0)) * 100.0, 3
            ),
            "qaoa_calls": qaoa_calls,
            "qaoa_improvements": qaoa_improvements,
            "total_qaoa_time_ms": round(total_qaoa_time_ms, 2),
            "classical_time_ms": round(t_class_ms, 2),
            "total_wall_ms": round(total_wall_ms, 2)
        }
