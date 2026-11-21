# PHASE AE: API CONTRACTS & INTERFACE SPECIFICATIONS
## ROUTE/IQ — Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing
**Repository:** `D:\UROP\smart-delivery-route-optimization`  
**Branch:** `research/phase-ae-backend-integration`  
**Protected Main Baseline:** `a8eb849988201d7929566f331c1ae3afac09b632`  
**Date:** November 2026  
**Institution:** Department of Computer Science and Engineering, SRM University-AP  
**Supervisor:** Dr. Vishnu Prasad Verma  
**Investigators:** J. Jayanth, B. Kaivalya, P. Shyam Sai

---

## 1. Overview & Backward Compatibility

Phase AE integrates the ROUTE/IQ Cooperative Engine without breaking or modifying existing API contracts. The API preserves complete backward compatibility for:
1. Legacy single-algorithm requests (`algorithm: "classical" | "qaoa" | "both"`).
2. Advanced multi-algorithm comparison requests (`selection_mode: "compare" | "custom"`).
3. The newly supported `"routeiq_cooperative"` algorithm ID.

---

## 2. Endpoint Specification

### 2.1 GET `/api/optimization/algorithms`
Returns the operational capabilities and compute metadata of all registered algorithms.

#### Response Schema:
```json
{
  "status": "success",
  "count": 8,
  "algorithms": [
    {
      "id": "routeiq_cooperative",
      "name": "ROUTE/IQ Cooperative Engine",
      "category": "cooperative",
      "category_label": "Cooperative Hybrid (Big Data + Quantum)",
      "tag": "Spark + Adaptive + QAOA/Tabu + VND",
      "description": "End-to-end cooperative optimization unifying Spark spatial decomposition, Multi-Armed Bandit adaptive control, QAOA/Tabu candidate generation, VND refinement, and Proposition 1 non-degradation guardrail.",
      "operational": true,
      "max_customers": 200,
      "is_primary": false,
      "compute_type": "Hybrid (Spark + Classical CPU + Simulated QPU)"
    },
    {
      "id": "ortools",
      "name": "OR-Tools",
      "category": "classical",
      "category_label": "Classical",
      "tag": "Exact / Local Search",
      "operational": true,
      "max_customers": 200,
      "is_primary": true,
      "compute_type": "Classical CPU"
    },
    {
      "id": "clarke_wright",
      "name": "Clarke–Wright Savings",
      "category": "classical",
      "category_label": "Classical",
      "tag": "Construction Heuristic",
      "operational": true,
      "max_customers": 200,
      "is_primary": false,
      "compute_type": "Classical CPU"
    },
    {
      "id": "two_opt",
      "name": "2-opt",
      "category": "classical",
      "category_label": "Classical",
      "tag": "Improvement Heuristic",
      "operational": true,
      "max_customers": 200,
      "is_primary": false,
      "compute_type": "Classical CPU"
    },
    {
      "id": "dijkstra",
      "name": "Dijkstra",
      "category": "classical",
      "category_label": "Classical",
      "tag": "Shortest-Path Baseline",
      "operational": true,
      "max_customers": 200,
      "is_primary": false,
      "compute_type": "Classical CPU"
    },
    {
      "id": "astar",
      "name": "A*",
      "category": "classical",
      "category_label": "Classical",
      "tag": "Heuristic Search",
      "operational": true,
      "max_customers": 200,
      "is_primary": false,
      "compute_type": "Classical CPU"
    },
    {
      "id": "qaoa",
      "name": "QAOA",
      "category": "quantum_hybrid",
      "category_label": "Quantum / Quantum-Classical",
      "tag": "Hybrid Quantum-Classical",
      "operational": true,
      "max_customers": 8,
      "is_primary": false,
      "compute_type": "Classical Statevector Simulation (Qiskit)"
    },
    {
      "id": "qiga",
      "name": "Quantum-Inspired Genetic Algorithm (QIGA/IQGA)",
      "category": "quantum_inspired",
      "category_label": "Quantum / Quantum-Classical",
      "tag": "Quantum-Inspired",
      "operational": true,
      "max_customers": 50,
      "is_primary": false,
      "compute_type": "Classically Simulated Q-Bits"
    }
  ]
}
```

---

### 2.2 POST `/api/optimization/run`
Executes vehicle routing optimization across specified algorithms.

#### Request Schema:
```json
{
  "selection_mode": "custom",
  "selected_algorithms": ["routeiq_cooperative", "ortools"],
  "num_customers": 10,
  "num_vehicles": 3,
  "vehicle_capacity": 100,
  "depot_lat": 40.7580,
  "depot_lon": -73.8292,
  "weight_distance": 1.0,
  "weight_travel_time": 0.5,
  "weight_congestion": 0.3,
  "weight_fuel": 0.2,
  "weight_late_penalty": 0.5,
  "traffic_scenario": "normal",
  "weather_scenario": "clear",
  "classical_time_limit_sec": 30,
  "qaoa_depth": 1,
  "qaoa_shots": 1024,
  "random_seed": 42
}
```

#### Response Structure:
```json
{
  "status": "completed",
  "experiment_id": "9618b76c-31a3-4a15-b778-43952d43d1a8",
  "selected_algorithms": ["routeiq_cooperative", "ortools"],
  "primary_algorithm": "routeiq_cooperative",
  "best_feasible_algorithm": "routeiq_cooperative",
  "results": {
    "routeiq_cooperative": {
      "success": true,
      "algorithm": "routeiq_cooperative",
      "algorithm_name": "ROUTE/IQ Cooperative Engine",
      "category": "cooperative",
      "category_label": "Cooperative Hybrid",
      "compute_type": "Hybrid (Spark + Adaptive + QAOA/Tabu + VND)",
      "status": "OPTIMAL",
      "execution_time_sec": 0.048,
      "routes": [
        {
          "vehicle_id": 1,
          "stops": [0, 1, 3, 5, 0],
          "customer_stops": [1, 3, 5],
          "load": 25,
          "capacity": 100,
          "distance_km": 14.82,
          "travel_time_min": 22.23,
          "utilization_pct": 25.0
        }
      ],
      "total_distance_km": 38.45,
      "total_travel_time_min": 57.68,
      "is_feasible": true,
      "capacity_violations": 0,
      "unserved_customers": 0,
      "served_customers": 10,
      "cooperative_telemetry": {
        "spark_mode": "Apache_Spark_4.2.0_local[*]",
        "initial_incumbent_distance_km": 39.12,
        "final_distance_km": 38.45,
        "distance_improvement_km": 0.67,
        "subproblems_evaluated": 1,
        "primary_strategy": "Tabu_Search",
        "proposition1_guaranteed": true
      }
    }
  }
}
```

---

## 3. Data Integrity & Invariants

1. **Route Continuity:** Each route starts and terminates at the depot index `0`:
   $$\text{stops}[0] = 0 \quad \text{and} \quad \text{stops}[-1] = 0$$
2. **Customer Partitioning:** Every customer $c \in \{1, \dots, N\}$ is visited exactly once across all active vehicle routes:
   $$\bigcup_{k=1}^M \text{customer\_stops}_k = \{1, \dots, N\} \quad \text{and} \quad \text{customer\_stops}_j \cap \text{customer\_stops}_k = \emptyset \; (j \ne k)$$
3. **Fleet Capacity Feasibility:**
   $$\forall k \in \{1, \dots, M\}, \quad \sum_{i \in \text{customer\_stops}_k} q_i \le Q_k$$
4. **Monotonic Non-Degradation:**
   $$\text{total\_distance\_km}(\text{routeiq\_cooperative}) \le \text{initial\_incumbent\_distance\_km}$$

