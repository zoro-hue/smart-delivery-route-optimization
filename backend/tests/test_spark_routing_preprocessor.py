"""
Unit tests for SparkRoutingPreprocessor and Calibrated Traffic Impedance Model.
Verifies:
1. BPR calibrated volume-delay impedance calculations.
2. Spatial polar partitioning consistency between PySpark and Single-Machine baseline.
3. Zero customer dropping in quantum subproblem payload extraction.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import numpy as np
import pandas as pd
from app.services.spark_routing_preprocessor import (
    CalibratedTrafficImpedanceModel,
    SparkRoutingPreprocessor
)


def test_bpr_calibrated_traffic_impedance():
    """Verify BPR volume-delay formula behavior under congested and uncongested conditions."""
    model = CalibratedTrafficImpedanceModel(capacity_per_lane=1000.0, alpha=0.15, beta=4.0)

    length_m = 500.0  # 500 meters
    # Free-flow time = 500 / 11.176 = 44.739s

    # Uncongested volume = 200 veh/hr (V/C = 0.2)
    t_uncong = model.compute_edge_impedance(length_m, hourly_volume=200.0, precipitation_mm=0.0)
    # Peak congested volume = 1400 veh/hr (V/C = 1.4)
    t_cong = model.compute_edge_impedance(length_m, hourly_volume=1400.0, precipitation_mm=0.0)
    # Rain penalty = 5mm rain
    t_rain = model.compute_edge_impedance(length_m, hourly_volume=200.0, precipitation_mm=5.0)

    assert t_uncong > 44.0 and t_uncong < 45.0
    assert t_cong > t_uncong * 1.5  # Congestion elevates travel time significantly
    assert t_rain > t_uncong  # Weather precipitation adds friction


def test_spark_vs_single_machine_partitioning_consistency():
    """Verify that PySpark distributed partitioning matches single-machine baseline."""
    preprocessor = SparkRoutingPreprocessor(master="local[1]")

    # Create synthetic customer dataset
    rng = np.random.default_rng(42)
    data = []
    for i in range(20):
        data.append({
            "order_id": f"ord_{i}",
            "customer_id": f"cust_{i}",
            "latitude": 40.75 + rng.uniform(-0.05, 0.05),
            "longitude": -73.98 + rng.uniform(-0.05, 0.05),
            "demand": rng.integers(1, 4)
        })
    df_cust = pd.DataFrame(data)

    depot_lat, depot_lon = 40.7580, -73.9855
    capacity = 10.0

    # Run Single-Machine Baseline
    clusters_base, t_base = preprocessor.partition_customers_single_machine(
        df_cust, depot_lat, depot_lon, capacity
    )
    # Run PySpark Distributed Partitioning
    clusters_spark, t_spark = preprocessor.partition_customers_spark(
        df_cust, depot_lat, depot_lon, capacity
    )

    # Verify identical total customer count across clusters
    tot_base = sum(c["customer_count"] for c in clusters_base)
    tot_spark = sum(c["customer_count"] for c in clusters_spark)
    assert tot_base == 20
    assert tot_spark == 20
    assert len(clusters_base) == len(clusters_spark)

    # Verify no customer dropped
    cust_ids_base = set(c["order_id"] for cl in clusters_base for c in cl["customers"])
    cust_ids_spark = set(c["order_id"] for cl in clusters_spark for c in cl["customers"])
    assert cust_ids_base == set(df_cust["order_id"])
    assert cust_ids_spark == set(df_cust["order_id"])


def test_quantum_subproblem_payload_extraction():
    """Verify that subproblem payload extracts core <= 4 nodes and preserves boundary nodes."""
    preprocessor = SparkRoutingPreprocessor()

    customers = [{"id": f"c_{i}", "demand": 1} for i in range(7)]
    depot = {"id": "depot", "demand": 0}
    loc_indices = {"depot": 0}
    for i in range(7):
        loc_indices[f"c_{i}"] = i + 1

    matrix = np.random.default_rng(123).uniform(1.0, 10.0, (8, 8))
    np.fill_diagonal(matrix, 0.0)

    payload = preprocessor.extract_quantum_subproblem_payload(
        customers, depot, matrix, loc_indices, core_budget=4
    )

    assert payload["core_size"] == 4
    assert payload["boundary_size"] == 3
    assert payload["core_size"] + payload["boundary_size"] == 7

    all_ids = set(c["id"] for c in payload["core_customers"] + payload["boundary_customers"])
    assert all_ids == set(f"c_{i}" for i in range(7))

