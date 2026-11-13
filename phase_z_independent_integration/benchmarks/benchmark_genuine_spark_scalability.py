"""
Phase Z: Genuine Apache Spark 4.2.0 Distributed Scalability Benchmark.
Audits Phase Y claims and benchmarks real PySpark execution across:
- Pandas In-Memory
- PySpark local[1] (Single Core)
- PySpark local[2] (Dual Core)
- PySpark local[4] (Quad Core)
Datasets: N in [1,000, 10,000, 50,000, 100,000] stops.
"""

import sys
import os
import time
import csv
from dataclasses import dataclass, asdict
from typing import List, Dict, Any
import numpy as np
import pandas as pd

# Setup PySpark environment with local OpenJDK 17
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend")))
from app.services.bigdata_pipeline import ensure_spark_environment
ensure_spark_environment()

from pyspark.sql import SparkSession
import pyspark.sql.functions as F


@dataclass
class GenuineSparkRecord:
    dataset_size: int
    engine_mode: str
    num_cores: int
    df_creation_time_ms: float
    transformation_time_ms: float
    action_collect_time_ms: float
    total_latency_ms: float
    throughput_records_per_sec: float
    boundary_nodes_extracted: int


def run_genuine_spark_benchmark():
    print("Executing Genuine Apache Spark 4.2.0 Scalability Benchmark...")
    scales = [1000, 10000, 50000, 100000]
    records = []

    # Initialize Spark Sessions per core configuration
    sessions = {}
    for cores in [1, 2, 4]:
        sessions[cores] = SparkSession.builder \
            .appName(f"PhaseZ_Scalability_local_{cores}") \
            .master(f"local[{cores}]") \
            .config("spark.ui.enabled", "false") \
            .config("spark.driver.host", "127.0.0.1") \
            .config("spark.driver.bindAddress", "127.0.0.1") \
            .config("spark.sql.shuffle.partitions", str(cores * 2)) \
            .getOrCreate()

    depot_lat, depot_lon = 40.75, -73.98
    c_a = np.array([40.73, -73.99])
    c_b = np.array([40.79, -73.95])

    for N in scales:
        np.random.seed(42)
        lats = np.random.uniform(40.70, 40.85, N)
        lons = np.random.uniform(-74.02, -73.93, N)
        demands = np.random.randint(1, 5, N)
        stop_ids = [f"stop_{i}" for i in range(N)]

        df_raw = pd.DataFrame({
            "stop_id": stop_ids,
            "latitude": lats,
            "longitude": lons,
            "demand": demands
        })

        # 1. Pandas In-Memory Baseline
        t0 = time.perf_counter()
        pts = df_raw[["latitude", "longitude"]].values
        da = np.linalg.norm(pts - c_a, axis=1)
        db = np.linalg.norm(pts - c_b, axis=1)
        diff = np.abs(da - db)
        mask = diff < 0.02
        boundary_stops = df_raw[mask]["stop_id"].tolist()[:16]
        t_pandas_total = (time.perf_counter() - t0) * 1000.0

        records.append(GenuineSparkRecord(
            dataset_size=N,
            engine_mode="Pandas_In_Memory",
            num_cores=1,
            df_creation_time_ms=0.0,
            transformation_time_ms=round(t_pandas_total, 2),
            action_collect_time_ms=0.0,
            total_latency_ms=round(t_pandas_total, 2),
            throughput_records_per_sec=round(N / max(t_pandas_total / 1000.0, 1e-4), 1),
            boundary_nodes_extracted=len(boundary_stops)
        ))

        # 2. Genuine PySpark execution across cores
        for cores in [1, 2, 4]:
            spark = sessions[cores]

            # Ingestion / DataFrame creation
            t0_create = time.perf_counter()
            sdf = spark.createDataFrame(df_raw)
            t_create_ms = (time.perf_counter() - t0_create) * 1000.0

            # Transformation
            t0_trans = time.perf_counter()
            sdf_calc = sdf \
                .withColumn("d_lat_a", F.col("latitude") - F.lit(c_a[0])) \
                .withColumn("d_lon_a", F.col("longitude") - F.lit(c_a[1])) \
                .withColumn("dist_a", F.sqrt(F.col("d_lat_a")**2 + F.col("d_lon_a")**2)) \
                .withColumn("d_lat_b", F.col("latitude") - F.lit(c_b[0])) \
                .withColumn("d_lon_b", F.col("longitude") - F.lit(c_b[1])) \
                .withColumn("dist_b", F.sqrt(F.col("d_lat_b")**2 + F.col("d_lon_b")**2)) \
                .withColumn("diff_ab", F.abs(F.col("dist_a") - F.col("dist_b"))) \
                .filter(F.col("diff_ab") < 0.02)
            t_trans_ms = (time.perf_counter() - t0_trans) * 1000.0

            # Action: collect top 16 boundary stops
            t0_act = time.perf_counter()
            res_rows = sdf_calc.limit(16).collect()
            t_act_ms = (time.perf_counter() - t0_act) * 1000.0

            total_spark_ms = t_create_ms + t_trans_ms + t_act_ms

            records.append(GenuineSparkRecord(
                dataset_size=N,
                engine_mode=f"PySpark_local[{cores}]",
                num_cores=cores,
                df_creation_time_ms=round(t_create_ms, 2),
                transformation_time_ms=round(t_trans_ms, 2),
                action_collect_time_ms=round(t_act_ms, 2),
                total_latency_ms=round(total_spark_ms, 2),
                throughput_records_per_sec=round(N / max(total_spark_ms / 1000.0, 1e-4), 1),
                boundary_nodes_extracted=len(res_rows)
            ))

    # Clean up Spark sessions
    for cores in [1, 2, 4]:
        sessions[cores].stop()

    return records


if __name__ == "__main__":
    records = run_genuine_spark_benchmark()
    csv_path = "phase_z_independent_integration/results/phase_z_genuine_spark_scalability_raw.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(records[0]).keys()))
        writer.writeheader()
        for r in records:
            writer.writerow(asdict(r))

    print(f"Genuine Spark benchmark completed: {len(records)} records logged to {csv_path}.")

