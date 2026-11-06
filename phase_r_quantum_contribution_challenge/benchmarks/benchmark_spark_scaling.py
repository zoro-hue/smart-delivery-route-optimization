"""
Phase R: Spark Big Data Scaling & Distributed Acceleration Audit.
Compares:
1. PySpark Distributed Processing (Polar Angle Partitioning, Demand Binning, Subproblem Extraction).
2. Single-Machine Pandas Baseline.

Evaluated across problem sizes: N = 10, 25, 50, 100, 250, 500, 1000.
Measures:
- Wall-clock execution time (ms).
- Throughput (points processed / second).
- Speedup ratio (T_single / T_spark).
- Identifies the empirical crossover point.
"""

import sys
import os
import time
import math
import numpy as np
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app.services.spark_routing_preprocessor import SparkRoutingPreprocessor


def generate_synthetic_orders(n: int, seed: int = 42) -> pd.DataFrame:
    np.random.seed(seed)
    depot_lat, depot_lon = 40.7580, -73.9855
    lats = depot_lat + np.random.uniform(-0.08, 0.08, n)
    lons = depot_lon + np.random.uniform(-0.08, 0.08, n)
    demands = np.random.randint(1, 10, n)
    ids = [f"c_{i}" for i in range(n)]

    return pd.DataFrame({
        "id": ids,
        "order_id": ids,
        "customer_id": ids,
        "latitude": lats,
        "longitude": lons,
        "demand": demands
    })


def main():
    print("=" * 80)
    print("PHASE R: SPARK BIG DATA SCALING AUDIT (N = 10 to 1,000)")
    print("=" * 80)

    preprocessor = SparkRoutingPreprocessor(master="local[*]")
    depot_lat, depot_lon = 40.7580, -73.9855
    vehicle_capacity = 35.0

    problem_sizes = [10, 25, 50, 100, 250, 500, 1000]
    records = []

    # Warmup Spark Session
    print("Warming up Apache Spark engine...")
    df_warm = generate_synthetic_orders(10, seed=1)
    preprocessor.partition_customers_spark(df_warm, depot_lat, depot_lon, vehicle_capacity)
    print("Spark engine warmed up.")

    for n in problem_sizes:
        print(f"\nBenchmarking problem size N = {n}...")
        df_orders = generate_synthetic_orders(n, seed=42 + n)

        # 1. Single-Machine Pandas Baseline
        t0_single = time.perf_counter()
        clusters_single, _ = preprocessor.partition_customers_single_machine(
            df_orders, depot_lat, depot_lon, vehicle_capacity
        )
        t_single_ms = (time.perf_counter() - t0_single) * 1000.0
        single_throughput = n / max(1e-4, t_single_ms / 1000.0)

        # 2. PySpark Distributed Processing
        t0_spark = time.perf_counter()
        clusters_spark, t_spark_internal_ms = preprocessor.partition_customers_spark(
            df_orders, depot_lat, depot_lon, vehicle_capacity
        )
        t_spark_ms = (time.perf_counter() - t0_spark) * 1000.0
        spark_throughput = n / max(1e-4, t_spark_ms / 1000.0)

        speedup = t_single_ms / max(1e-4, t_spark_ms)

        print(f"  Single-Machine: {t_single_ms:.2f} ms ({single_throughput:.1f} pts/sec)")
        print(f"  Spark 4.2.0:    {t_spark_ms:.2f} ms ({spark_throughput:.1f} pts/sec, internal: {t_spark_internal_ms:.2f} ms)")
        print(f"  Speedup Ratio:  {speedup:.3f}x")

        records.append({
            "N": n,
            "single_machine_ms": round(t_single_ms, 2),
            "spark_total_ms": round(t_spark_ms, 2),
            "spark_internal_ms": round(t_spark_internal_ms, 2),
            "single_throughput_pts_sec": round(single_throughput, 1),
            "spark_throughput_pts_sec": round(spark_throughput, 1),
            "speedup_ratio": round(speedup, 3),
            "num_clusters_single": len(clusters_single),
            "num_clusters_spark": len(clusters_spark)
        })

    df_res = pd.DataFrame(records)
    out_csv = os.path.join(os.path.dirname(__file__), "..", "results", "phase_r_spark_scaling_raw.csv")
    df_res.to_csv(out_csv, index=False)
    print(f"\nSpark Scaling results exported to: {out_csv}")


if __name__ == "__main__":
    main()

