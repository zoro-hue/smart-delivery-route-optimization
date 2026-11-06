"""
Phase Q Master Benchmarking & Ablation Suite.
Executes systematic comparisons across Classical Baselines (OR-Tools, Clarke-Wright, 2-opt),
IP-CQE v1 (Phase P), and IP-CQE v2 (Phase Q with Variational Multi-Angle QAOA).
Saves raw measurements to CSV for statistical evaluation.
"""

import sys
import os
import time
import math
import numpy as np
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app.services.optimization.classical_solver import ClassicalVRPSolver
from phase_p_autonomous_research.prototypes.common_evaluator import (
    generate_benchmark_instance, audit_solution_feasibility, ProblemInstance
)
from phase_p_autonomous_research.prototypes.proto_5_iterative_feedback_controller import IncumbentPreservingCooperativeEngine
from phase_q_ipcqe_validation.prototypes.proto_ipcqe_v2_optimizer import IPCQEv2Optimizer


def run_phase_q_benchmarks():
    print("=" * 80)
    print("ROUTE/IQ PHASE Q: EXECUTING COMPREHENSIVE REPRODUCTION & VALIDATION BENCHMARKS")
    print("=" * 80)

    scales = [
        {"name": "Micro", "N": 10, "M": 2, "cap": 25.0, "seeds": [42, 101]},
        {"name": "Small", "N": 25, "M": 4, "cap": 30.0, "seeds": [42, 101]},
        {"name": "Medium", "N": 50, "M": 5, "cap": 40.0, "seeds": [42]}
    ]

    classical_solver = ClassicalVRPSolver()
    ipcqe_v1 = IncumbentPreservingCooperativeEngine(qaoa_p=1, qaoa_shots=512)
    ipcqe_v2 = IPCQEv2Optimizer(p=1, shots=512, max_v_iter=8)

    records = []

    for scale in scales:
        for seed in scale["seeds"]:
            print(f"\n---> Benchmarking {scale['name']} Scale: N={scale['N']}, M={scale['M']}, Seed={seed}")
            instance = generate_benchmark_instance(
                num_customers=scale["N"],
                num_vehicles=scale["M"],
                vehicle_capacity=scale["cap"],
                seed=seed
            )

            # 1. OR-Tools Alone
            t0 = time.perf_counter()
            res_ortools = classical_solver.solve_ortools(
                distance_matrix=instance.distance_matrix,
                num_vehicles=instance.num_vehicles,
                depot=0,
                demands=[int(instance.depot["demand"])] + [int(c["demand"]) for c in instance.customers],
                vehicle_capacities=[int(instance.vehicle_capacity)] * instance.num_vehicles,
                time_limit_sec=10
            )
            t_ortools_ms = (time.perf_counter() - t0) * 1000.0
            ortools_d = float(res_ortools.get("total_distance_km", 0.0))

            records.append({
                "scale": scale["name"], "N": scale["N"], "M": scale["M"], "seed": seed,
                "algorithm": "A_ORTools_Alone", "distance_km": ortools_d,
                "is_feasible": res_ortools.get("is_feasible", True),
                "wall_time_ms": round(t_ortools_ms, 2), "qaoa_calls": 0, "qaoa_ms": 0.0,
                "guardrail_triggered": False, "improvement_vs_ortools_pct": 0.0
            })
            print(f"  [OR-Tools Alone]      Distance: {ortools_d:6.3f} km | Time: {t_ortools_ms:6.1f} ms")

            # 2. Clarke-Wright Alone
            t0 = time.perf_counter()
            res_cw = classical_solver.solve_clarke_wright(
                distance_matrix=instance.distance_matrix,
                num_vehicles=instance.num_vehicles,
                depot=0,
                demands=[int(instance.depot["demand"])] + [int(c["demand"]) for c in instance.customers],
                vehicle_capacities=[int(instance.vehicle_capacity)] * instance.num_vehicles
            )
            t_cw_ms = (time.perf_counter() - t0) * 1000.0
            cw_d = float(res_cw.get("total_distance_km", 0.0))

            records.append({
                "scale": scale["name"], "N": scale["N"], "M": scale["M"], "seed": seed,
                "algorithm": "B_ClarkeWright_Alone", "distance_km": cw_d,
                "is_feasible": res_cw.get("is_feasible", True),
                "wall_time_ms": round(t_cw_ms, 2), "qaoa_calls": 0, "qaoa_ms": 0.0,
                "guardrail_triggered": False,
                "improvement_vs_ortools_pct": round((ortools_d - cw_d) / max(1e-4, ortools_d) * 100.0, 3)
            })
            print(f"  [Clarke-Wright Alone] Distance: {cw_d:6.3f} km | Time: {t_cw_ms:6.1f} ms")

            # 3. Clarke-Wright + Classical 2-opt
            t0 = time.perf_counter()
            res_cw_2opt = classical_solver.solve_two_opt(
                distance_matrix=instance.distance_matrix,
                num_vehicles=instance.num_vehicles,
                depot=0,
                demands=[int(instance.depot["demand"])] + [int(c["demand"]) for c in instance.customers],
                vehicle_capacities=[int(instance.vehicle_capacity)] * instance.num_vehicles
            )
            t_cw_2opt_ms = (time.perf_counter() - t0) * 1000.0
            cw_2opt_d = float(res_cw_2opt.get("total_distance_km", 0.0))

            records.append({
                "scale": scale["name"], "N": scale["N"], "M": scale["M"], "seed": seed,
                "algorithm": "C_ClarkeWright_Plus_2opt", "distance_km": cw_2opt_d,
                "is_feasible": res_cw_2opt.get("is_feasible", True),
                "wall_time_ms": round(t_cw_2opt_ms, 2), "qaoa_calls": 0, "qaoa_ms": 0.0,
                "guardrail_triggered": False,
                "improvement_vs_ortools_pct": round((ortools_d - cw_2opt_d) / max(1e-4, ortools_d) * 100.0, 3)
            })
            print(f"  [Clarke-Wright + 2opt] Distance: {cw_2opt_d:6.3f} km | Time: {t_cw_2opt_ms:6.1f} ms")

            # 4. IP-CQE v1 (Phase P Default)
            res_v1 = ipcqe_v1.solve_instance(instance, use_spark=False)
            v1_d = float(res_v1["total_distance_km"])
            records.append({
                "scale": scale["name"], "N": scale["N"], "M": scale["M"], "seed": seed,
                "algorithm": "D_IP_CQE_v1_PhaseP", "distance_km": v1_d,
                "is_feasible": res_v1["is_feasible"],
                "wall_time_ms": res_v1["total_wall_ms"], "qaoa_calls": res_v1["qaoa_calls"],
                "qaoa_ms": res_v1["qaoa_time_ms"],
                "guardrail_triggered": res_v1["guardrail_triggered"],
                "improvement_vs_ortools_pct": res_v1["improvement_over_ortools_pct"]
            })
            print(f"  [IP-CQE v1 (Phase P)] Distance: {v1_d:6.3f} km | Time: {res_v1['total_wall_ms']:6.1f} ms | Guardrail: {res_v1['guardrail_triggered']}")

            # 5. IP-CQE v2 (Phase Q Variational)
            res_v2 = ipcqe_v2.solve_instance(instance, use_spark=False)
            v2_d = float(res_v2["total_distance_km"])
            records.append({
                "scale": scale["name"], "N": scale["N"], "M": scale["M"], "seed": seed,
                "algorithm": "E_IP_CQE_v2_Variational", "distance_km": v2_d,
                "is_feasible": res_v2["is_feasible"],
                "wall_time_ms": res_v2["total_wall_ms"], "qaoa_calls": res_v2["qaoa_calls"],
                "qaoa_ms": res_v2["qaoa_time_ms"],
                "guardrail_triggered": res_v2["guardrail_triggered"],
                "improvement_vs_ortools_pct": res_v2["improvement_pct"]
            })
            print(f"  [IP-CQE v2 (Phase Q)] Distance: {v2_d:6.3f} km | Time: {res_v2['total_wall_ms']:6.1f} ms | Guardrail: {res_v2['guardrail_triggered']}")

    csv_file = os.path.join(os.path.dirname(__file__), "..", "results", "phase_q_benchmark_raw.csv")
    os.makedirs(os.path.dirname(csv_file), exist_ok=True)
    pd.DataFrame(records).to_csv(csv_file, index=False)
    print(f"\n[OK] Phase Q Benchmarks completed! Raw results saved to: {csv_file}")


if __name__ == "__main__":
    run_phase_q_benchmarks()

