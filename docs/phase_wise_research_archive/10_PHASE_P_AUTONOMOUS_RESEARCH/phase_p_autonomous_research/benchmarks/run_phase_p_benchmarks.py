"""
Phase P Master Benchmarking & Experimental Evaluation Runner.
Executes systematic, reproducible benchmarks across multiple customer scales and random seeds.
Compares Classical Baselines (OR-Tools, Clarke-Wright, 2-opt) against all 5 Hybrid Prototypes.
Saves raw measurements to CSV and prints structured markdown tables.
"""

import sys
import os
import time
import math
import csv
from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app.services.optimization.classical_solver import ClassicalVRPSolver
from phase_p_autonomous_research.prototypes.common_evaluator import (
    generate_benchmark_instance, audit_solution_feasibility, ProblemInstance
)
from phase_p_autonomous_research.prototypes.proto_1_classical_seeded_qaoa import ClassicalSeededQAOASolver
from phase_p_autonomous_research.prototypes.proto_2_spark_hierarchical_qaoa import SparkHierarchicalQAOASolver
from phase_p_autonomous_research.prototypes.proto_3_adaptive_neighborhood_qaoa import AdaptiveNeighborhoodQAOASolver
from phase_p_autonomous_research.prototypes.proto_4_cooperative_qaoa_qiga import CooperativeQAOAQIGASolver
from phase_p_autonomous_research.prototypes.proto_5_iterative_feedback_controller import IncumbentPreservingCooperativeEngine


def run_comprehensive_benchmark():
    print("=" * 80)
    print("ROUTE/IQ PHASE P: EXECUTING COMPREHENSIVE MULTI-SCALE BENCHMARK SUITE")
    print("=" * 80)

    scales = [
        {"name": "Micro", "N": 10, "M": 2, "cap": 25.0, "seeds": [42, 101]},
        {"name": "Small", "N": 25, "M": 4, "cap": 30.0, "seeds": [42, 101]},
        {"name": "Medium", "N": 50, "M": 5, "cap": 40.0, "seeds": [42]}
    ]

    classical_solver = ClassicalVRPSolver()
    p1_solver = ClassicalSeededQAOASolver(p=1, shots=512)
    p2_solver = SparkHierarchicalQAOASolver(p=1, shots=512)
    p3_solver = AdaptiveNeighborhoodQAOASolver(p=1, shots=512)
    p4_solver = CooperativeQAOAQIGASolver(pop_size=15, generations=10, qaoa_interval=5, shots=256)
    p5_solver = IncumbentPreservingCooperativeEngine(qaoa_p=1, qaoa_shots=512)

    results_records = []
    csv_file = os.path.join(os.path.dirname(__file__), "..", "results", "phase_p_benchmark_raw.csv")
    os.makedirs(os.path.dirname(csv_file), exist_ok=True)

    for scale in scales:
        for seed in scale["seeds"]:
            print(f"\n---> Evaluating Scale: {scale['name']} (N={scale['N']}, M={scale['M']}, Seed={seed})")
            instance = generate_benchmark_instance(
                num_customers=scale["N"],
                num_vehicles=scale["M"],
                vehicle_capacity=scale["cap"],
                seed=seed
            )

            # 1. Classical Baseline: OR-Tools
            t0 = time.perf_counter()
            res_ortools = classical_solver.solve_ortools(
                distance_matrix=instance.distance_matrix,
                num_vehicles=instance.num_vehicles,
                depot=0,
                demands=[int(instance.depot["demand"])] + [int(c["demand"]) for c in instance.customers],
                vehicle_capacities=[int(instance.vehicle_capacity)] * instance.num_vehicles,
                time_limit_sec=10
            )
            ortools_ms = (time.perf_counter() - t0) * 1000.0
            ortools_dist = float(res_ortools.get("total_distance_km", 0.0))
            ortools_feas = bool(res_ortools.get("is_feasible", True))

            results_records.append({
                "scale": scale["name"], "N": scale["N"], "M": scale["M"], "seed": seed,
                "algorithm": "Classical_ORTools", "distance_km": ortools_dist,
                "is_feasible": ortools_feas, "wall_time_ms": round(ortools_ms, 2),
                "qaoa_calls": 0, "qaoa_ms": 0.0, "improvement_vs_ortools_pct": 0.0
            })
            print(f"  [OR-Tools]        Distance: {ortools_dist:.3f} km | Time: {ortools_ms:.1f} ms | Feasible: {ortools_feas}")

            # 2. Classical Baseline: Clarke-Wright
            t0 = time.perf_counter()
            res_cw = classical_solver.solve_clarke_wright(
                distance_matrix=instance.distance_matrix,
                num_vehicles=instance.num_vehicles,
                depot=0,
                demands=[int(instance.depot["demand"])] + [int(c["demand"]) for c in instance.customers],
                vehicle_capacities=[int(instance.vehicle_capacity)] * instance.num_vehicles
            )
            cw_ms = (time.perf_counter() - t0) * 1000.0
            cw_dist = float(res_cw.get("total_distance_km", 0.0))
            cw_feas = bool(res_cw.get("is_feasible", True))

            results_records.append({
                "scale": scale["name"], "N": scale["N"], "M": scale["M"], "seed": seed,
                "algorithm": "Classical_ClarkeWright", "distance_km": cw_dist,
                "is_feasible": cw_feas, "wall_time_ms": round(cw_ms, 2),
                "qaoa_calls": 0, "qaoa_ms": 0.0,
                "improvement_vs_ortools_pct": round((ortools_dist - cw_dist) / max(1e-4, ortools_dist) * 100.0, 2)
            })
            print(f"  [Clarke-Wright]   Distance: {cw_dist:.3f} km | Time: {cw_ms:.1f} ms | Feasible: {cw_feas}")

            # 3. Proto 1: Classical-Seeded Warm-Start QAOA
            res_p1 = p1_solver.solve_instance(instance)
            p1_dist = float(res_p1["total_distance_km"])
            results_records.append({
                "scale": scale["name"], "N": scale["N"], "M": scale["M"], "seed": seed,
                "algorithm": "Proto_1_CS_QAOA", "distance_km": p1_dist,
                "is_feasible": res_p1["is_feasible"], "wall_time_ms": res_p1["total_wall_ms"],
                "qaoa_calls": res_p1["qaoa_calls"], "qaoa_ms": res_p1["total_qaoa_time_ms"],
                "improvement_vs_ortools_pct": round((ortools_dist - p1_dist) / max(1e-4, ortools_dist) * 100.0, 2)
            })
            print(f"  [Proto 1 CS-QAOA] Distance: {p1_dist:.3f} km | Time: {res_p1['total_wall_ms']:.1f} ms | QAOA Calls: {res_p1['qaoa_calls']}")

            # 4. Proto 2: Spark Hierarchical QAOA (Single machine mode for repeatable test)
            res_p2 = p2_solver.solve_instance(instance, use_spark=False)
            p2_dist = float(res_p2["total_distance_km"])
            results_records.append({
                "scale": scale["name"], "N": scale["N"], "M": scale["M"], "seed": seed,
                "algorithm": "Proto_2_Spark_HQD", "distance_km": p2_dist,
                "is_feasible": res_p2["is_feasible"], "wall_time_ms": res_p2["total_wall_ms"],
                "qaoa_calls": res_p2["qaoa_calls"], "qaoa_ms": res_p2["qaoa_time_ms"],
                "improvement_vs_ortools_pct": round((ortools_dist - p2_dist) / max(1e-4, ortools_dist) * 100.0, 2)
            })
            print(f"  [Proto 2 Spark]   Distance: {p2_dist:.3f} km | Time: {res_p2['total_wall_ms']:.1f} ms | QAOA Calls: {res_p2['qaoa_calls']}")

            # 5. Proto 3: Adaptive Neighborhood QAOA
            res_p3 = p3_solver.solve_instance(instance)
            p3_dist = float(res_p3["total_distance_km"])
            results_records.append({
                "scale": scale["name"], "N": scale["N"], "M": scale["M"], "seed": seed,
                "algorithm": "Proto_3_AQNS", "distance_km": p3_dist,
                "is_feasible": res_p3["is_feasible"], "wall_time_ms": res_p3["total_wall_ms"],
                "qaoa_calls": res_p3.get("crossings_resolved_by_qaoa", 0), "qaoa_ms": res_p3["qaoa_time_ms"],
                "improvement_vs_ortools_pct": round((ortools_dist - p3_dist) / max(1e-4, ortools_dist) * 100.0, 2)
            })
            print(f"  [Proto 3 AQNS]    Distance: {p3_dist:.3f} km | Time: {res_p3['total_wall_ms']:.1f} ms | Crossings: {res_p3['crossings_detected']}")

            # 6. Proto 4: Cooperative QAOA + QIGA
            res_p4 = p4_solver.solve_instance(instance)
            p4_dist = float(res_p4["total_distance_km"])
            results_records.append({
                "scale": scale["name"], "N": scale["N"], "M": scale["M"], "seed": seed,
                "algorithm": "Proto_4_Coop_QIGA", "distance_km": p4_dist,
                "is_feasible": res_p4["is_feasible"], "wall_time_ms": res_p4["total_wall_ms"],
                "qaoa_calls": res_p4["qaoa_calls"], "qaoa_ms": res_p4["qaoa_time_ms"],
                "improvement_vs_ortools_pct": round((ortools_dist - p4_dist) / max(1e-4, ortools_dist) * 100.0, 2)
            })
            print(f"  [Proto 4 Coop-Q]  Distance: {p4_dist:.3f} km | Time: {res_p4['total_wall_ms']:.1f} ms | Generations: {res_p4['generations']}")

            # 7. Proto 5: Incumbent-Preserving Cooperative Engine (Master Architecture)
            res_p5 = p5_solver.solve_instance(instance, use_spark=False)
            p5_dist = float(res_p5["total_distance_km"])
            results_records.append({
                "scale": scale["name"], "N": scale["N"], "M": scale["M"], "seed": seed,
                "algorithm": "Proto_5_IP_CQE_Master", "distance_km": p5_dist,
                "is_feasible": res_p5["is_feasible"], "wall_time_ms": res_p5["total_wall_ms"],
                "qaoa_calls": res_p5["qaoa_calls"], "qaoa_ms": res_p5["qaoa_time_ms"],
                "improvement_vs_ortools_pct": res_p5["improvement_over_ortools_pct"]
            })
            print(f"  [Proto 5 IP-CQE]  Distance: {p5_dist:.3f} km | Time: {res_p5['total_wall_ms']:.1f} ms | Guardrail Triggered: {res_p5['guardrail_triggered']}")

    # Save to CSV
    df_results = pd.DataFrame(results_records)
    df_results.to_csv(csv_file, index=False)
    print(f"\n[OK] Benchmark completed! Raw results saved to: {csv_file}")


if __name__ == "__main__":
    run_comprehensive_benchmark()
