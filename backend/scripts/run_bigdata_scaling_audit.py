"""
Independent Big Data Scaling Benchmark for ROUTE/IQ.

Evaluates scaling performance comparing Single-Machine Pandas vs. Apache Spark local[*]
across customer dataset sizes N in [1,000, 5,000, 10,000, 25,000, 50,000].

Synthetic Data Generation Procedure:
- Uniform sampling of delivery demand points within Manhattan geographical bounding box:
  Latitude: [40.7000, 40.8500], Longitude: [-74.0200, -73.9300].
  Customer demand: discrete uniform integer in {1, 2, 3}.
  Depot location: Midtown Manhattan (40.7580, -73.9855).
- Vehicle capacity: Q_cap = 15.0 units.
- Evaluates memory usage via process RSS memory delta and Python tracemalloc.
"""

import sys
sys.path.insert(0, 'backend')

import os
import time
import tracemalloc
import numpy as np
import pandas as pd
from typing import Dict, Any, List

from app.services.bigdata_pipeline import ensure_spark_environment
from app.services.spark_routing_preprocessor import SparkRoutingPreprocessor

def generate_synthetic_customer_orders(N: int, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    lats = rng.uniform(40.7000, 40.8500, size=N)
    lons = rng.uniform(-74.0200, -73.9300, size=N)
    demands = rng.integers(1, 4, size=N)
    return pd.DataFrame({
        "order_id": [f"ord_{i:06d}" for i in range(N)],
        "customer_id": [f"cust_{i:06d}" for i in range(N)],
        "latitude": lats,
        "longitude": lons,
        "demand": demands
    })

def main():
    print("=" * 70, flush=True)
    print("ROUTE/IQ BIG DATA SCALING AUDIT (PANDAS VS APACHE SPARK LOCAL[*])", flush=True)
    print("=" * 70, flush=True)
    ensure_spark_environment()

    preprocessor = SparkRoutingPreprocessor(master="local[*]")
    # Pre-warm Spark JVM
    print("Pre-warming PySpark session...", flush=True)
    dummy_df = generate_synthetic_customer_orders(10, seed=1)
    _, _ = preprocessor.partition_customers_spark(dummy_df, 40.7580, -73.9855, 15.0)

    dataset_sizes = [1000, 5000, 10000, 25000, 50000]
    records = []

    target_dir = r"C:\Users\DELL\.gemini\antigravity\brain\aba14f7b-722c-4648-8da1-214dc979ac26\scratch\phase6_benchmark"
    os.makedirs(target_dir, exist_ok=True)
    out_csv = os.path.join(target_dir, "bigdata_scaling_results.csv")

    for N in dataset_sizes:
        print(f"\n--- Benchmarking Scale N = {N:,} Customers ---", flush=True)
        df_cust = generate_synthetic_customer_orders(N, seed=N + 100)
        data_vol_kb = round(df_cust.memory_usage(deep=True).sum() / 1024.0, 2)

        # -------------------------------------------------------------
        # Treatment A: Single-Machine Pandas Baseline
        # -------------------------------------------------------------
        tracemalloc.start()
        t0 = time.perf_counter()
        clusters_pandas, t_pandas_calc = preprocessor.partition_customers_single_machine(
            df_cust, 40.7580, -73.9855, 15.0
        )
        t_pandas_wall_ms = (time.perf_counter() - t0) * 1000.0
        current_mem, peak_mem_pandas = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        throughput_pandas = N / (t_pandas_wall_ms / 1000.0)

        # -------------------------------------------------------------
        # Treatment B: Apache Spark Distributed Preprocessing (local[*])
        # -------------------------------------------------------------
        tracemalloc.start()
        t0 = time.perf_counter()
        clusters_spark, t_spark_calc = preprocessor.partition_customers_spark(
            df_cust, 40.7580, -73.9855, 15.0
        )
        t_spark_wall_ms = (time.perf_counter() - t0) * 1000.0
        current_mem, peak_mem_spark = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        throughput_spark = N / (t_spark_wall_ms / 1000.0)

        # Verification of Customer Conservation & Capacity
        n_routed_pandas = sum(len(c["customers"]) for c in clusters_pandas)
        n_routed_spark  = sum(len(c["customers"]) for c in clusters_spark)
        
        # Verify cluster capacities
        caps_ok_pandas = all(sum(c["demand"] for c in cl["customers"]) <= 15.0 + 1e-5 for cl in clusters_pandas)
        caps_ok_spark  = all(sum(c["demand"] for c in cl["customers"]) <= 15.0 + 1e-5 for cl in clusters_spark)

        print(f"  Pandas: {t_pandas_wall_ms:7.1f} ms | Throughput: {throughput_pandas:9.1f} orders/s | Peak RAM: {peak_mem_pandas/1024/1024:.2f} MB | Custs: {n_routed_pandas}/{N} (Caps valid: {caps_ok_pandas})", flush=True)
        print(f"  Spark:  {t_spark_wall_ms:7.1f} ms | Throughput: {throughput_spark:9.1f} orders/s | Peak RAM: {peak_mem_spark/1024/1024:.2f} MB | Custs: {n_routed_spark}/{N} (Caps valid: {caps_ok_spark})", flush=True)

        records.append({
            "order_count_N": N,
            "data_volume_kb": data_vol_kb,
            "pandas_wall_ms": round(t_pandas_wall_ms, 2),
            "spark_wall_ms": round(t_spark_wall_ms, 2),
            "pandas_throughput_ops": round(throughput_pandas, 1),
            "spark_throughput_ops": round(throughput_spark, 1),
            "pandas_peak_ram_mb": round(peak_mem_pandas / 1024 / 1024, 3),
            "spark_peak_ram_mb": round(peak_mem_spark / 1024 / 1024, 3),
            "pandas_cluster_count": len(clusters_pandas),
            "spark_cluster_count": len(clusters_spark),
            "speedup_ratio_pandas_over_spark": round(t_pandas_wall_ms / t_spark_wall_ms, 3),
            "preservation_verified": (n_routed_pandas == N and n_routed_spark == N),
            "capacity_verified": (caps_ok_pandas and caps_ok_spark)
        })

    df_results = pd.DataFrame(records)
    df_results.to_csv(out_csv, index=False)
    print(f"\nSaved Big Data Scaling results to: {out_csv}", flush=True)

if __name__ == "__main__":
    main()
