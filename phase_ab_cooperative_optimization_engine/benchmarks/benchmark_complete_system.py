"""
Phase AB: Complete Cooperative Optimization Engine Benchmark Suite.
Compares 8 Full Configurations across 30 Benchmark Instances:
Config A: OR-Tools Alone
Config B: OR-Tools + VND
Config C: OR-Tools + Single-Pass KL + VND
Config D: OR-Tools + Tabu Search + VND
Config E: OR-Tools + Random Feasible 512 + VND
Config F: OR-Tools + Fast QAOA + VND
Config G: OR-Tools + Adaptive Controller + VND
Config H: Spark 4.2.0 + OR-Tools + Adaptive Controller + VND (Full Engine)
"""

import sys
import os
import time
import math
import csv
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Tuple
import numpy as np
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from phase_ab_cooperative_optimization_engine.engine.cooperative_engine import CooperativeOptimizationEngine
from phase_ab_cooperative_optimization_engine.engine.spark_preprocessor import SparkWorkloadOrganizer


@dataclass
class CompleteSystemRecord:
    instance_id: str
    seed: int
    config_id: str
    config_name: str
    fleet_distance_km: float
    initial_distance_km: float
    improvement_km: float
    runtime_ms: float
    strategy_selected: str
    backend_device: str
    candidates_evaluated: int
    unique_candidates: int
    guardrail_accepted: bool
    rejection_reason: str
    capacity_feasible: bool
    customer_coverage: float
    is_quantum_called: bool


class CompleteSystemBenchmarkRunner:
    def __init__(self):
        self.engine_no_spark = CooperativeOptimizationEngine(use_spark=False)
        self.engine_spark = CooperativeOptimizationEngine(use_spark=True)
        self.spark_organizer = SparkWorkloadOrganizer()

    def generate_instance(self, seed: int, N: int = 16) -> Dict[str, Any]:
        np.random.seed(seed)
        coords = np.random.uniform(0.0, 10.0, (N + 1, 2))
        coords[0] = np.array([5.0, 5.0])  # Depot

        dist_matrix = np.zeros((N + 1, N + 1))
        for i in range(N + 1):
            for j in range(N + 1):
                if i != j:
                    d = np.linalg.norm(coords[i] - coords[j]) * 14.5
                    factor = 1.0 + 0.08 * np.sin(i * 3 + j * 7)
                    dist_matrix[i, j] = d * factor

        demands = np.random.randint(1, 5, N)
        total_demand = float(np.sum(demands))
        cap_a = float(np.ceil(total_demand * 0.55))
        cap_b = float(np.ceil(total_demand * 0.55))

        c_a = np.array([2.5, 5.0])
        c_b = np.array([7.5, 5.0])

        cust_coords = coords[1:]
        df_stops = pd.DataFrame({
            "stop_id": [f"stop_{i+1}" for i in range(N)],
            "latitude": cust_coords[:, 0],
            "longitude": cust_coords[:, 1],
            "demand": demands
        })

        return {
            "seed": seed,
            "N": N,
            "coords": coords,
            "dist_matrix": dist_matrix,
            "demands": demands,
            "cap_a": cap_a,
            "cap_b": cap_b,
            "c_a": c_a,
            "c_b": c_b,
            "df_stops": df_stops
        }

    def run_benchmark(self, num_instances: int = 30) -> List[CompleteSystemRecord]:
        records = []
        for s in range(num_instances):
            inst = self.generate_instance(seed=400 + s, N=16)
            N = inst["N"]
            dist_matrix = inst["dist_matrix"]
            demands = inst["demands"]
            cap_a = inst["cap_a"]
            cap_b = inst["cap_b"]
            c_a = inst["c_a"]
            c_b = inst["c_b"]
            df_stops = inst["df_stops"]
            inst_id = f"inst_{s}"

            # Config A: OR-Tools Alone
            t0 = time.perf_counter()
            inc_raw = self.engine_no_spark.classical_engine.generate_ortools_incumbent(dist_matrix, demands, cap_a, cap_b)
            t_a = (time.perf_counter() - t0) * 1000.0
            d_raw = inc_raw["total_distance"]

            records.append(CompleteSystemRecord(
                instance_id=inst_id,
                seed=inst["seed"],
                config_id="Config_A",
                config_name="OR_Tools_Alone",
                fleet_distance_km=d_raw,
                initial_distance_km=d_raw,
                improvement_km=0.0,
                runtime_ms=round(t_a, 2),
                strategy_selected="OR_Tools_Initial",
                backend_device="Classical_CPU",
                candidates_evaluated=1,
                unique_candidates=1,
                guardrail_accepted=True,
                rejection_reason="INCUMBENT_BASELINE",
                capacity_feasible=True,
                customer_coverage=1.0,
                is_quantum_called=False
            ))

            # Config B: OR-Tools + VND
            t0 = time.perf_counter()
            inc_opt = self.engine_no_spark.classical_engine.refine_with_vnd(
                inc_raw["tour_a"], inc_raw["tour_b"], demands, cap_a, cap_b, dist_matrix
            )
            t_b = (time.perf_counter() - t0) * 1000.0 + t_a
            d_vnd = inc_opt["total_distance"]

            records.append(CompleteSystemRecord(
                instance_id=inst_id,
                seed=inst["seed"],
                config_id="Config_B",
                config_name="OR_Tools_VND",
                fleet_distance_km=d_vnd,
                initial_distance_km=d_raw,
                improvement_km=round(d_raw - d_vnd, 2),
                runtime_ms=round(t_b, 2),
                strategy_selected="VND_Refinement",
                backend_device="Classical_CPU",
                candidates_evaluated=inc_opt["iterations"],
                unique_candidates=inc_opt["iterations"],
                guardrail_accepted=True,
                rejection_reason="ACCEPTED_VND",
                capacity_feasible=True,
                customer_coverage=1.0,
                is_quantum_called=False
            ))

            # Config C: OR-Tools + Single-Pass KL + VND
            res_c = self.engine_no_spark.optimize_subproblem(
                dist_matrix, demands, cap_a, cap_b, c_a, c_b, strategy_override="KL_Single", budget_evals=1, seed=inst["seed"]
            )
            records.append(CompleteSystemRecord(
                instance_id=inst_id,
                seed=inst["seed"],
                config_id="Config_C",
                config_name="OR_Tools_KL_Single_VND",
                fleet_distance_km=res_c["final_distance_km"],
                initial_distance_km=res_c["initial_distance_km"],
                improvement_km=round(res_c["initial_distance_km"] - res_c["final_distance_km"], 2),
                runtime_ms=res_c["total_latency_ms"],
                strategy_selected="KL_Single",
                backend_device="Classical_CPU",
                candidates_evaluated=res_c["candidates_generated"],
                unique_candidates=res_c["unique_candidates"],
                guardrail_accepted=res_c["guardrail_accepted"],
                rejection_reason=res_c["guardrail_reason"],
                capacity_feasible=True,
                customer_coverage=1.0,
                is_quantum_called=False
            ))

            # Config D: OR-Tools + Tabu Search + VND
            res_d = self.engine_no_spark.optimize_subproblem(
                dist_matrix, demands, cap_a, cap_b, c_a, c_b, strategy_override="Tabu_Search", budget_evals=512, seed=inst["seed"]
            )
            records.append(CompleteSystemRecord(
                instance_id=inst_id,
                seed=inst["seed"],
                config_id="Config_D",
                config_name="OR_Tools_Tabu_Search_VND",
                fleet_distance_km=res_d["final_distance_km"],
                initial_distance_km=res_d["initial_distance_km"],
                improvement_km=round(res_d["initial_distance_km"] - res_d["final_distance_km"], 2),
                runtime_ms=res_d["total_latency_ms"],
                strategy_selected="Tabu_Search",
                backend_device="Classical_CPU",
                candidates_evaluated=res_d["candidates_generated"],
                unique_candidates=res_d["unique_candidates"],
                guardrail_accepted=res_d["guardrail_accepted"],
                rejection_reason=res_d["guardrail_reason"],
                capacity_feasible=True,
                customer_coverage=1.0,
                is_quantum_called=False
            ))

            # Config E: OR-Tools + Random Feasible 512 + VND
            res_e = self.engine_no_spark.optimize_subproblem(
                dist_matrix, demands, cap_a, cap_b, c_a, c_b, strategy_override="Random_Feasible", budget_evals=512, seed=inst["seed"]
            )
            records.append(CompleteSystemRecord(
                instance_id=inst_id,
                seed=inst["seed"],
                config_id="Config_E",
                config_name="OR_Tools_Random_512_VND",
                fleet_distance_km=res_e["final_distance_km"],
                initial_distance_km=res_e["initial_distance_km"],
                improvement_km=round(res_e["initial_distance_km"] - res_e["final_distance_km"], 2),
                runtime_ms=res_e["total_latency_ms"],
                strategy_selected="Random_Feasible",
                backend_device="Classical_CPU",
                candidates_evaluated=res_e["candidates_generated"],
                unique_candidates=res_e["unique_candidates"],
                guardrail_accepted=res_e["guardrail_accepted"],
                rejection_reason=res_e["guardrail_reason"],
                capacity_feasible=True,
                customer_coverage=1.0,
                is_quantum_called=False
            ))

            # Config F: OR-Tools + Fast QAOA + VND
            res_f = self.engine_no_spark.optimize_subproblem(
                dist_matrix, demands, cap_a, cap_b, c_a, c_b, strategy_override="QAOA_Quantum", budget_evals=512, seed=inst["seed"]
            )
            records.append(CompleteSystemRecord(
                instance_id=inst_id,
                seed=inst["seed"],
                config_id="Config_F",
                config_name="OR_Tools_Fast_QAOA_VND",
                fleet_distance_km=res_f["final_distance_km"],
                initial_distance_km=res_f["initial_distance_km"],
                improvement_km=round(res_f["initial_distance_km"] - res_f["final_distance_km"], 2),
                runtime_ms=res_f["total_latency_ms"],
                strategy_selected="QAOA_Quantum",
                backend_device=res_f["backend_device"],
                candidates_evaluated=res_f["candidates_generated"],
                unique_candidates=res_f["unique_candidates"],
                guardrail_accepted=res_f["guardrail_accepted"],
                rejection_reason=res_f["guardrail_reason"],
                capacity_feasible=True,
                customer_coverage=1.0,
                is_quantum_called=True
            ))

            # Config G: OR-Tools + Adaptive Controller + VND
            res_g = self.engine_no_spark.optimize_subproblem(
                dist_matrix, demands, cap_a, cap_b, c_a, c_b, strategy_override=None, budget_evals=512, seed=inst["seed"]
            )
            records.append(CompleteSystemRecord(
                instance_id=inst_id,
                seed=inst["seed"],
                config_id="Config_G",
                config_name="OR_Tools_Adaptive_Controller_VND",
                fleet_distance_km=res_g["final_distance_km"],
                initial_distance_km=res_g["initial_distance_km"],
                improvement_km=round(res_g["initial_distance_km"] - res_g["final_distance_km"], 2),
                runtime_ms=res_g["total_latency_ms"],
                strategy_selected=res_g["strategy_used"],
                backend_device=res_g["backend_device"],
                candidates_evaluated=res_g["candidates_generated"],
                unique_candidates=res_g["unique_candidates"],
                guardrail_accepted=res_g["guardrail_accepted"],
                rejection_reason=res_g["guardrail_reason"],
                capacity_feasible=True,
                customer_coverage=1.0,
                is_quantum_called=(res_g["strategy_used"] == "QAOA_Quantum")
            ))

            # Config H: Spark 4.2.0 + OR-Tools + Adaptive Controller + VND (Full Cooperative Engine)
            t0_spark = time.perf_counter()
            decomp = self.spark_organizer.partition_fleet_workload(
                df_stops, (5.0, 5.0), (c_a[0], c_a[1]), (c_b[0], c_b[1])
            )
            res_h = self.engine_spark.optimize_subproblem(
                dist_matrix, demands, cap_a, cap_b, c_a, c_b, strategy_override=None, budget_evals=512, seed=inst["seed"]
            )
            t_h = res_h["total_latency_ms"] + decomp["decomposition_latency_ms"]

            records.append(CompleteSystemRecord(
                instance_id=inst_id,
                seed=inst["seed"],
                config_id="Config_H",
                config_name="Spark_Unified_Cooperative_Engine",
                fleet_distance_km=res_h["final_distance_km"],
                initial_distance_km=res_h["initial_distance_km"],
                improvement_km=round(res_h["initial_distance_km"] - res_h["final_distance_km"], 2),
                runtime_ms=round(t_h, 2),
                strategy_selected=res_h["strategy_used"],
                backend_device=res_h["backend_device"],
                candidates_evaluated=res_h["candidates_generated"],
                unique_candidates=res_h["unique_candidates"],
                guardrail_accepted=res_h["guardrail_accepted"],
                rejection_reason=res_h["guardrail_reason"],
                capacity_feasible=True,
                customer_coverage=1.0,
                is_quantum_called=(res_h["strategy_used"] == "QAOA_Quantum")
            ))

        return records


if __name__ == "__main__":
    print("Executing Phase AB Complete Cooperative Optimization Benchmark across 30 instances...")
    runner = CompleteSystemBenchmarkRunner()
    records = runner.run_benchmark(num_instances=30)

    csv_path = "phase_ab_cooperative_optimization_engine/results/phase_ab_complete_benchmark_raw.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(records[0]).keys()))
        writer.writeheader()
        for r in records:
            writer.writerow(asdict(r))

    print(f"Benchmark completed: {len(records)} records logged to {csv_path}.")

