# ROUTE/IQ — ALGORITHM RESOURCE API CONTRACTS & SCHEMAS
**Phase AE API Specification**
**Repository:** `D:\UROP\smart-delivery-route-optimization`
**Endpoint:** `POST /api/optimization/run`

---

## 1. Request Schema

```json
{
  "dataset_id": "optional-dataset-uuid",
  "num_vehicles": 3,
  "vehicle_capacity": 100.0,
  "weight_distance": 0.7,
  "weight_travel_time": 0.3,
  "selection_mode": "compare",
  "selected_algorithms": [
    "routeiq_cooperative",
    "ortools",
    "clarke_wright",
    "two_opt",
    "qiga",
    "qaoa"
  ],
  "depot": {
    "lat": 40.7769,
    "lon": -73.8740,
    "name": "Origin Depot Hub (D)"
  },
  "customer_stops": [
    {"lat": 40.7128, "lon": -74.0060, "demand": 10.0, "time_window_start": 480, "time_window_end": 720}
  ]
}
```

---

## 2. Response Schema & Resource Metrics Contract

```json
{
  "experiment_id": "6732cb48-b4b1-4f32-9df7-28e46f63412a",
  "status": "completed",
  "execution_time_sec": 0.284,
  "selection_mode": "compare",
  "selected_algorithms": ["routeiq_cooperative", "ortools", "qaoa"],
  "problem": {
    "n_customers": 18,
    "num_vehicles": 3,
    "vehicle_capacity": 100.0,
    "locations": [[40.7769, -73.8740], [40.7128, -74.0060]]
  },
  "results": {
    "routeiq_cooperative": {
      "success": true,
      "algorithm": "routeiq_cooperative",
      "algorithm_name": "ROUTE/IQ Cooperative Engine",
      "category": "cooperative",
      "category_label": "Cooperative Hybrid",
      "compute_type": "Hybrid (Spark + Adaptive + QAOA/Tabu + VND)",
      "status": "OPTIMAL",
      "execution_time_sec": 0.033,
      "total_distance_km": 83.89,
      "total_travel_time_min": 125.8,
      "total_objective_cost": 83.89,
      "is_feasible": true,
      "capacity_violations": 0,
      "unserved_customers": 0,
      "served_customers": 18,
      "routes": [
        {
          "vehicle_id": 1,
          "distance_km": 41.25,
          "load": 90.0,
          "capacity": 100.0,
          "utilization_pct": 90.0,
          "stops": [0, 6, 18, 16, 12, 14, 10, 0],
          "customer_stops": [6, 18, 16, 12, 14, 10],
          "waypoints": [
            {"lat": 40.7769, "lon": -73.8740, "type": "depot", "index": 0, "is_stop": true}
          ]
        }
      ],
      "resource_metrics": {
        "runtime_ms": 32.8,
        "cpu_time_ms": 31.2,
        "cpu_utilization_percent": 95.1,
        "memory_used_mb": 0.84,
        "peak_memory_mb": 3.12,
        "time_complexity": "O(N log N + K·B^2 + 2^p)",
        "space_complexity": "O(N + K·B)",
        "measurement_available": true,
        "measurement_method": "tracemalloc + high-res OS process timers"
      },
      "validation_report": {
        "is_complete": true,
        "is_valid": true,
        "capacity_feasible": true,
        "capacity_violations": 0,
        "input_delivery_count": 18,
        "visited_delivery_count": 18,
        "missing_delivery_ids": [],
        "duplicate_delivery_ids": [],
        "unknown_delivery_ids": []
      }
    }
  },
  "comparison_summary": {
    "best_algorithm": "routeiq_cooperative",
    "best_algorithm_name": "ROUTE/IQ Cooperative Engine",
    "best_reason": "Lowest route distance (83.89 km) with 100% stop coverage and 0 constraint violations",
    "best_feasible_distance_km": 83.89,
    "items": [
      {
        "id": "routeiq_cooperative",
        "name": "ROUTE/IQ Cooperative Engine",
        "category": "cooperative",
        "category_label": "Cooperative Hybrid",
        "compute_type": "Hybrid (Spark + Adaptive + QAOA/Tabu + VND)",
        "status": "OPTIMAL",
        "execution_time_sec": 0.033,
        "total_distance_km": 83.89,
        "total_travel_time_min": 125.8,
        "total_objective_cost": 83.89,
        "is_feasible": true,
        "capacity_violations": 0,
        "unserved_customers": 0,
        "served_customers": 18,
        "vehicles_used": 2,
        "cpu_utilization_percent": 95.1,
        "memory_used_mb": 0.84,
        "peak_memory_mb": 3.12,
        "time_complexity": "O(N log N + K·B^2 + 2^p)",
        "space_complexity": "O(N + K·B)",
        "is_best": true
      }
    ]
  }
}
```

