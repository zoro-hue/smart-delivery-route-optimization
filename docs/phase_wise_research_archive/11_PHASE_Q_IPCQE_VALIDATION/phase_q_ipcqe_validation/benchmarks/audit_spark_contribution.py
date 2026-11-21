"""
Phase Q: Comprehensive Apache Spark Contribution Audit.
Measures the end-to-end impact of PySpark 4.2.0 vs Single-Machine Pandas
across preprocessing latency, memory usage, cluster balance, and quantum payload generation.
"""

import sys
import os
import time
import math
import psutil
import numpy as np
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app.services.spark_routing_preprocessor import SparkRoutingPreprocessor


def audit_spark():
    print("=" * 80)
    print("PHASE Q: INDEPENDENT AUDIT OF APACHE SPARK BIG DATA CONTRIBUTION")
    print("=" * 80)

    preprocessor = SparkRoutingPreprocessor(master="local[*]")
    scales = [25, 50, 100, 250, 500]
    depot_lat, depot_lon = 40.7580, -73.9855
    vehicle_capacity = 30.0

    process = psutil.Process()
    records = []

    for n in scales:
        print(f"\n---> Auditing Scale N = {n} Orders")
        np.random.seed(42 + n)
        lats = depot_lat + np.random.uniform(-0.08, 0.08, n)
        lons = depot_lon + np.random.uniform(-0.08, 0.08, n)
        demands = np.random.randint(2, 6, n).astype(float)

        df_cust = pd.DataFrame({
            "id": [f"c_{i}" for i in range(n)],
            "order_id": [f"ord_{i}" for i in range(n)],
            "customer_id": [f"c_{i}" for i in range(n)],
            "latitude": lats,
            "longitude": lons,
            "demand": demands
        })

        # 1. Single-Machine Pandas Baseline
        mem_before_pandas = process.memory_info().rss / (1024 * 1024)
        t0 = time.perf_counter()
        clusters_pandas, t_pandas_ms = preprocessor.partition_customers_single_machine(
            df_cust, depot_lat, depot_lon, vehicle_capacity
        )
        total_pandas_ms = (time.perf_counter() - t0) * 1000.0
        mem_after_pandas = process.memory_info().rss / (1024 * 1024)

        # 2. PySpark Preprocessing
        mem_before_spark = process.memory_info().rss / (1024 * 1024)
        t0 = time.perf_counter()
        clusters_spark, t_spark_ms = preprocessor.partition_customers_spark(
            df_cust, depot_lat, depot_lon, vehicle_capacity
        )
        total_spark_ms = (time.perf_counter() - t0) * 1000.0
        mem_after_spark = process.memory_info().rss / (1024 * 1024)

        # Cluster Balance Metric (std dev of cluster size)
        sizes_pandas = [c["customer_count"] for c in clusters_pandas]
        sizes_spark = [c["customer_count"] for c in clusters_spark]
        balance_pandas = float(np.std(sizes_pandas))
        balance_spark = float(np.std(sizes_spark))

        # Quantum Payload Generation Time for first 3 clusters
        matrix = np.random.uniform(5.0, 30.0, (n + 1, n + 1))
        loc_indices = {f"c_{i}": i + 1 for i in range(n)}
        loc_indices["depot"] = 0

        t_payload0 = time.perf_counter()
        for cl in clusters_spark[:3]:
            preprocessor.extract_quantum_subproblem_payload(
                cluster_customers=[row["original_dict"] if "original_dict" in row else row for row in cl["customers"]],
                depot={"id": "depot", "latitude": depot_lat, "longitude": depot_lon},
                matrix=matrix,
                location_indices=loc_indices,
                core_budget=4
            )
        t_payload_ms = (time.perf_counter() - t_payload0) * 1000.0

        print(f"  Pandas Time: {t_pandas_ms:6.2f} ms | Spark Time: {t_spark_ms:6.2f} ms | Clusters: {len(clusters_spark)} | Balance: {balance_spark:.2f}")

        records.append({
            "N": n,
            "pandas_time_ms": round(t_pandas_ms, 2),
            "spark_time_ms": round(t_spark_ms, 2),
            "clusters_count": len(clusters_spark),
            "cluster_balance_std": round(balance_spark, 2),
            "payload_gen_time_ms": round(t_payload_ms, 2),
            "pandas_mem_mb": round(mem_after_pandas, 1),
            "spark_mem_mb": round(mem_after_spark, 1),
            "clusters_identical": (sizes_pandas == sizes_spark)
        })

    csv_file = os.path.join(os.path.dirname(__file__), "..", "results", "phase_q_spark_audit_raw.csv")
    os.makedirs(os.path.dirname(csv_file), exist_ok=True)
    pd.DataFrame(records).to_csv(csv_file, index=False)
    print(f"\n[OK] Spark Audit completed! Raw data saved to: {csv_file}")


if __name__ == "__main__":
    audit_spark()
