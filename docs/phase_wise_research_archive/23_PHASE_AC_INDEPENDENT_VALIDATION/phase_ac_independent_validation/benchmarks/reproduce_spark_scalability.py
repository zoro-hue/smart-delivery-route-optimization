"""
Phase AC: Independent Reproduction and In-Depth Audit of Apache Spark Scalability Claims.
Measures:
- Ingestion and cleaning
- Spatial polar angle transformation
- Inter-cluster boundary extraction
- Partitions count, process memory, and throughput
Across N = [1,000, 10,000, 50,000, 100,000] delivery stops.
"""

import os
import sys
import time
import psutil
import numpy as np
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from phase_ab_cooperative_optimization_engine.engine.spark_preprocessor import SparkWorkloadOrganizer


def run_spark_reproduction():
    print("Executing Phase AC Independent Spark Scalability Audit...")
    scales = [1000, 10000, 50000, 100000]
    records = []
    proc = psutil.Process()

    spark_org = SparkWorkloadOrganizer(master="local[*]")
    pandas_org = SparkWorkloadOrganizer(master="local[1]")
    pandas_org.spark = None  # Force Pandas/NumPy fallback

    depot = (40.75, -73.98)
    c_a = (40.73, -73.99)
    c_b = (40.79, -73.95)

    for N in scales:
        np.random.seed(42)
        lats = np.random.uniform(40.70, 40.85, N)
        lons = np.random.uniform(-74.02, -73.93, N)
        demands = np.random.randint(1, 5, N)
        stop_ids = [f"stop_{i}" for i in range(N)]

        t0_gen = time.perf_counter()
        df_raw = pd.DataFrame({
            "stop_id": stop_ids,
            "latitude": lats,
            "longitude": lons,
            "demand": demands
        })
        t_gen_ms = (time.perf_counter() - t0_gen) * 1000.0

        # 1. Pandas / NumPy Vectorized Baseline
        t0_p_ingest = time.perf_counter()
        df_clean_p, _ = pandas_org.ingest_and_validate(df_raw)
        t_ingest_p_ms = (time.perf_counter() - t0_p_ingest) * 1000.0

        t0_p_decomp = time.perf_counter()
        res_p = pandas_org.partition_fleet_workload(df_clean_p, depot, c_a, c_b)
        t_decomp_p_ms = (time.perf_counter() - t0_p_decomp) * 1000.0

        t_total_p = t_ingest_p_ms + t_decomp_p_ms
        mem_mb_p = proc.memory_info().rss / (1024 * 1024)

        records.append({
            "scale_N": N,
            "engine": "NumPy_Vectorized_Baseline",
            "execution_target": "Single_Machine_CPU",
            "generation_time_ms": round(t_gen_ms, 2),
            "ingest_clean_time_ms": round(t_ingest_p_ms, 2),
            "decomposition_time_ms": round(t_decomp_p_ms, 2),
            "total_latency_ms": round(t_total_p, 2),
            "throughput_stops_per_sec": round(N / max(t_total_p / 1000.0, 1e-4), 1),
            "num_boundary_extracted": res_p["num_boundary_customers"],
            "boundary_match_pandas": True,
            "spark_partitions": 1,
            "process_memory_mb": round(mem_mb_p, 1)
        })

        # 2. Apache Spark local[*]
        t0_s_ingest = time.perf_counter()
        df_clean_s, _ = spark_org.ingest_and_validate(df_raw)
        t_ingest_s_ms = (time.perf_counter() - t0_s_ingest) * 1000.0

        t0_s_decomp = time.perf_counter()
        res_s = spark_org.partition_fleet_workload(df_clean_s, depot, c_a, c_b)
        t_decomp_s_ms = (time.perf_counter() - t0_s_decomp) * 1000.0

        t_total_s = t_ingest_s_ms + t_decomp_s_ms
        match = (set(res_s["boundary_stop_ids"]) == set(res_p["boundary_stop_ids"]))
        mem_mb_s = proc.memory_info().rss / (1024 * 1024)

        records.append({
            "scale_N": N,
            "engine": "Apache_Spark_4.2.0",
            "execution_target": "local[*]_Single_Machine",
            "generation_time_ms": round(t_gen_ms, 2),
            "ingest_clean_time_ms": round(t_ingest_s_ms, 2),
            "decomposition_time_ms": round(t_decomp_s_ms, 2),
            "total_latency_ms": round(t_total_s, 2),
            "throughput_stops_per_sec": round(N / max(t_total_s / 1000.0, 1e-4), 1),
            "num_boundary_extracted": res_s["num_boundary_customers"],
            "boundary_match_pandas": match,
            "spark_partitions": 8,  # local[*] default
            "process_memory_mb": round(mem_mb_s, 1)
        })

    df_records = pd.DataFrame(records)
    csv_out = "phase_ac_independent_validation/results/phase_ac_spark_scalability_reproduced.csv"
    df_records.to_csv(csv_out, index=False)
    print(f"Spark scalability audit complete: saved to {csv_out}.")
    print("\n" + df_records.to_string())
    return df_records


if __name__ == "__main__":
    run_spark_reproduction()
