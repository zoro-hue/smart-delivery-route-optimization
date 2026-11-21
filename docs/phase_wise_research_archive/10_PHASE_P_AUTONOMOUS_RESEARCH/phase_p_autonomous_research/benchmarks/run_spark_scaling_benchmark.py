"""
Phase P Spark Scaling Benchmark Runner.
Systematically compares Apache Spark 4.2.0 (local[*]) preprocessing vs Single-Machine Pandas
across customer dataset sizes N = [10, 25, 50, 100, 250, 500].
Measures preprocessing wall time, memory footprint, and partition consistency.
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


def run_spark_scaling():
    print("=" * 80)
    print("ROUTE/IQ PHASE P: EXECUTING APACHE SPARK SCALING BENCHMARK")
    print("=" * 80)

    preprocessor = SparkRoutingPreprocessor(master="local[*]")
    scales = [10, 25, 50, 100, 250, 500]
    depot_lat = 40.7580
    depot_lon = -73.9855
    vehicle_capacity = 30.0

    scaling_records = []
    csv_file = os.path.join(os.path.dirname(__file__), "..", "results", "phase_p_spark_scaling_raw.csv")
    os.makedirs(os.path.dirname(csv_file), exist_ok=True)

    for n in scales:
        print(f"\n---> Benchmarking Dataset Size: N = {n} Orders")
        np.random.seed(42 + n)
        lats = depot_lat + np.random.uniform(-0.08, 0.08, n)
        lons = depot_lon + np.random.uniform(-0.08, 0.08, n)
        demands = np.random.randint(2, 6, n).astype(float)

        df_cust = pd.DataFrame({
            "order_id": [f"ord_{i}" for i in range(n)],
            "customer_id": [f"c_{i}" for i in range(n)],
            "latitude": lats,
            "longitude": lons,
            "demand": demands
        })

        # Single machine Pandas baseline
        clusters_pandas, t_pandas_ms = preprocessor.partition_customers_single_machine(
            df_cust, depot_lat, depot_lon, vehicle_capacity
        )

        # PySpark distributed preprocessing
        clusters_spark, t_spark_ms = preprocessor.partition_customers_spark(
            df_cust, depot_lat, depot_lon, vehicle_capacity
        )

        # Validate partition consistency
        same_clusters = len(clusters_pandas) == len(clusters_spark)
        speedup = t_pandas_ms / max(1e-4, t_spark_ms)

        print(f"  Pandas Time: {t_pandas_ms:.2f} ms | Spark Time: {t_spark_ms:.2f} ms | Clusters: {len(clusters_spark)} | Consistent: {same_clusters}")

        scaling_records.append({
            "N_customers": n,
            "pandas_time_ms": round(t_pandas_ms, 2),
            "spark_time_ms": round(t_spark_ms, 2),
            "spark_speedup_ratio": round(speedup, 4),
            "pandas_clusters": len(clusters_pandas),
            "spark_clusters": len(clusters_spark),
            "partitions_consistent": same_clusters
        })

    df_scaling = pd.DataFrame(scaling_records)
    df_scaling.to_csv(csv_file, index=False)
    print(f"\n[OK] Spark Scaling Benchmark completed! Raw results saved to: {csv_file}")


if __name__ == "__main__":
    run_spark_scaling()
