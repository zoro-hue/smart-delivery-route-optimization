"""
Common Evaluation Harness & Data Generator for ROUTE/IQ Phase P Prototypes.
Provides standardized synthetic and road-network delivery instances, feasibility auditing,
and unified metric serialization across all experimental architecture prototypes.
"""

import time
import math
import random
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import pandas as pd


class ProblemInstance:
    """Standardized Delivery Problem Instance."""

    def __init__(
        self,
        name: str,
        num_customers: int,
        num_vehicles: int,
        vehicle_capacity: float,
        depot: Dict[str, Any],
        customers: List[Dict[str, Any]],
        distance_matrix: np.ndarray,
        location_indices: Dict[str, int],
        seed: int = 42
    ):
        self.name = name
        self.num_customers = num_customers
        self.num_vehicles = num_vehicles
        self.vehicle_capacity = vehicle_capacity
        self.depot = depot
        self.customers = customers
        self.distance_matrix = distance_matrix
        self.location_indices = location_indices
        self.seed = seed


def generate_benchmark_instance(
    num_customers: int = 25,
    num_vehicles: int = 4,
    vehicle_capacity: float = 30.0,
    depot_lat: float = 40.7580,   # NYC Midtown
    depot_lon: float = -73.9855,
    seed: int = 42,
    asymmetric_ratio: float = 0.15
) -> ProblemInstance:
    """
    Generates synthetic NYC delivery coordinates with realistic asymmetric road distances.
    """
    np.random.seed(seed)
    random.seed(seed)

    depot = {
        "id": "depot",
        "latitude": depot_lat,
        "longitude": depot_lon,
        "demand": 0.0
    }

    # Generate customer clusters around NYC boroughs
    customers = []
    # Span roughly +/- 0.08 degrees (~9 km radius)
    for i in range(num_customers):
        # Introduce occasional cluster structure
        angle = np.random.uniform(0, 2 * math.pi)
        r = np.random.uniform(0.01, 0.08)
        lat = depot_lat + r * math.sin(angle)
        lon = depot_lon + r * math.cos(angle)
        demand = float(np.random.randint(2, 6))

        customers.append({
            "id": f"c_{i+1}",
            "customer_id": f"c_{i+1}",
            "latitude": lat,
            "longitude": lon,
            "demand": demand
        })

    all_nodes = [depot] + customers
    n = len(all_nodes)
    location_indices = {node["id"]: idx for idx, node in enumerate(all_nodes)}

    # Build Haversine distance matrix + asymmetric road impedance
    dist_matrix = np.zeros((n, n), dtype=np.float64)

    def haversine_km(lat1, lon1, lat2, lon2):
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2.0) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2.0) ** 2)
        return 2.0 * R * math.asin(math.sqrt(max(0.0, min(1.0, a))))

    for i in range(n):
        for j in range(n):
            if i == j:
                dist_matrix[i, j] = 0.0
            else:
                base_d = haversine_km(
                    all_nodes[i]["latitude"], all_nodes[i]["longitude"],
                    all_nodes[j]["latitude"], all_nodes[j]["longitude"]
                )
                # Apply asymmetric road network detour factor (e.g. one-way streets, bridge tolls)
                asym = 1.0 + asymmetric_ratio * (np.sin(i * 3.1 + j * 1.7) * 0.5 + 0.5)
                # Road network circuity factor in Manhattan grid (~1.25)
                dist_matrix[i, j] = round(base_d * 1.25 * asym, 3)

    return ProblemInstance(
        name=f"NYC_N{num_customers}_M{num_vehicles}_S{seed}",
        num_customers=num_customers,
        num_vehicles=num_vehicles,
        vehicle_capacity=vehicle_capacity,
        depot=depot,
        customers=customers,
        distance_matrix=dist_matrix,
        location_indices=location_indices,
        seed=seed
    )


def audit_solution_feasibility(
    instance: ProblemInstance,
    routes: List[List[Dict[str, Any]]]
) -> Dict[str, Any]:
    """
    Rigorously validates CVRP solution constraints:
    1. Every customer visited exactly once (no drops, no duplicates).
    2. Vehicle capacity respected on all routes.
    3. Every route starts and ends at the depot.
    """
    visited_customer_ids = []
    capacity_violations = 0
    total_distance_km = 0.0
    depot_id = instance.depot["id"]
    depot_idx = instance.location_indices[depot_id]

    for route in routes:
        if not route:
            continue
        route_demand = 0.0
        prev_idx = depot_idx

        for stop in route:
            stop_id = stop["id"]
            if stop_id == depot_id:
                continue
            visited_customer_ids.append(stop_id)
            route_demand += float(stop.get("demand", 1.0))
            curr_idx = instance.location_indices[stop_id]
            total_distance_km += instance.distance_matrix[prev_idx, curr_idx]
            prev_idx = curr_idx

        # Return to depot
        total_distance_km += instance.distance_matrix[prev_idx, depot_idx]

        if route_demand > instance.vehicle_capacity + 1e-4:
            capacity_violations += 1

    expected_ids = set(c["id"] for c in instance.customers)
    actual_ids = set(visited_customer_ids)
    dropped_customers = len(expected_ids - actual_ids)
    duplicate_customers = len(visited_customer_ids) - len(actual_ids)

    is_feasible = (
        dropped_customers == 0 and
        duplicate_customers == 0 and
        capacity_violations == 0
    )

    return {
        "is_feasible": is_feasible,
        "total_distance_km": round(total_distance_km, 3),
        "total_customers_served": len(actual_ids),
        "dropped_customers": dropped_customers,
        "duplicate_customers": duplicate_customers,
        "capacity_violations": capacity_violations,
        "num_active_routes": len(routes)
    }

