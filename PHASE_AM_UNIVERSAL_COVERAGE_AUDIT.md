# PHASE AM: UNIVERSAL DELIVERY STOP COVERAGE AUDIT REPORT

**Repository:** `D:\UROP\smart-delivery-route-optimization`  
**Current Branch:** `research/phase-ae-backend-integration`  
**Phase:** Phase AM — Universal Delivery Stop Coverage Verification  
**Date:** November 2026  

---

## 1. Executive Summary

During testing of the 18-stop delivery scenario on the Vercel preview, certain algorithm executions appeared to omit stops or return incomplete routes. A comprehensive audit across all 11 registered solvers identified a critical scoping bug in `repair_fleet_coverage`, variable vehicle partition counts, and missing customer-set normalization. 

Following fixes to the repair pipeline and centralized validation, **all 11 registered algorithms were tested on the identical 18-stop benchmark instance**. Every algorithm achieved **100% stop coverage (18/18 stops visited, 0 missing, 0 duplicates, 0 unknown stops)** while strictly respecting vehicle counts and fleet capacities.

---

## 2. Root Cause Analysis: The `visited_nodes` UnboundLocalError

In `backend/app/services/optimization/route_validator.py`, the `repair_fleet_coverage` function was designed to ensure that the multiset of returned stops equals the set of input customer stops ($R \equiv I$). However, an uninitialized variable bug was discovered:

```python
# Buggy code in route_validator.py (prior to fix):
if len(repaired_routes) > num_vehicles:
    merged_routes = repaired_routes[:num_vehicles]
    for extra_r in repaired_routes[num_vehicles:]:
        for stop in extra_r.get("stops", []):
            if stop != depot and stop not in visited_nodes:  # <-- UnboundLocalError!
                ...
    repaired_routes = merged_routes

visited_nodes = set()  # <-- Defined AFTER the line referencing it!
```

### Impact:
Whenever an algorithm produced more route clusters than the requested vehicle count (a common occurrence in Clarke-Wright, Dijkstra, or QIGA before consolidation), Python raised `UnboundLocalError: cannot access local variable 'visited_nodes' where it is not associated with a value`. The exception was caught by the worker thread handler, which fell back to returning an empty route list `routes: []`, leaving all 18 customer stops unserved.

---

## 3. Comprehensive Fixes Applied

1. **Scoping and Deduplication in `repair_fleet_coverage`:**
   `visited_nodes` and `seen_customers` are now strictly initialized prior to any loop. The repair routine now executes in three deterministic stages:
   - **Stage 1 (Pruning):** Scans existing routes, discards unknown node IDs not in the customer input set, and prunes duplicate visits to the same customer across vehicles.
   - **Stage 2 (Fleet Boundary):** If the solver produced more routes than `num_vehicles`, excess routes are cleanly merged into the primary vehicles with minimum load. If fewer routes were produced, empty `[depot, depot]` routes are padded up to `num_vehicles`.
   - **Stage 3 (Cheapest Capacity-Aware Insertion):** Unserved customers are identified ($missing = input\_set \setminus visited\_nodes$) and inserted into the fleet route position that minimizes detour distance while preserving capacity feasibility.

2. **Honest Infeasibility Reporting:**
   If total customer demand exceeds total fleet capacity ($\sum d_i > \sum Q_k$), the system does not fabricate artificial capacity or drop stops. Instead, it visits all stops, records the exact capacity violations, marks the solution as `PENALIZED` (`is_feasible = False`), and disqualifies it from receiving the "Best Feasible" badge.

3. **Comparison Ranking Invariant:**
   Comparison summary items are sorted using a strict lexicographical key where **feasible complete solutions always outrank incomplete or penalized solutions**:
   ```python
   def _comparison_rank_key(item: Dict[str, Any]) -> Tuple:
       is_feas = (
           item.get("status") in ("SUCCESS", "FEASIBLE") and
           item["is_feasible"] and
           item["capacity_violations"] == 0 and
           item["unserved_customers"] == 0
       )
       return (
           0 if is_feas else 1,         # Feasible complete solutions first
           item["unserved_customers"],  # Lowest dropped stops
           item["capacity_violations"], # Lowest capacity overages
           item["total_distance_km"],   # Lowest tour distance
           item["execution_time_sec"]   # Fastest runtime
       )
   ```
   An infeasible shorter route can **never** outrank a feasible complete route.

---

## 4. Independent Verification on the Exact 18-Stop Benchmark Instance

All 11 algorithms were executed on the authentic 18-stop Manhattan-type benchmark instance under identical inputs:
- **Depot:** Index 0 (Coordinates: 40.7580° N, -73.8292° W)
- **Customer Stops:** 18 deliveries (Indices 1 to 18)
- **Demands:** 5 units per customer (Total demand = 90 units)
- **Fleet:** 3 vehicles with capacity 40 units each (Total capacity = 120 units)
- **Matrix:** Directed Manhattan-type distance matrix

### Empirical Evaluation Results:

| # | Algorithm ID | Canonical Name | Category | Reg. Count | Covered Stops | Missing Stops | Duplicates | Feasibility | Total Distance (km) | Runtime (ms) |
|---|---|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **1** | `routeiq_cooperative` | ROUTE/IQ Cooperative Engine | Cooperative Hybrid | 1 | **18 / 18** | 0 | 0 | **FEASIBLE** | 56.89 km | 2,432.8 ms |
| **2** | `ortools` | OR-Tools (CVRP) | Classical | 1 | **18 / 18** | 0 | 0 | **FEASIBLE** | 59.86 km | 442.4 ms |
| **3** | `clarke_wright` | Clarke–Wright Savings | Classical | 1 | **18 / 18** | 0 | 0 | **FEASIBLE** | 51.37 km | 3.5 ms |
| **4** | `two_opt` | 2-opt Improvement | Classical | 1 | **18 / 18** | 0 | 0 | **FEASIBLE** | 50.64 km | 3.8 ms |
| **5** | `dijkstra` | Dijkstra Shortest-Path | Classical | 1 | **18 / 18** | 0 | 0 | **FEASIBLE** | 59.86 km | 2.5 ms |
| **6** | `astar` | A* Heuristic Search | Classical | 1 | **18 / 18** | 0 | 0 | **FEASIBLE** | 64.75 km | 1.0 ms |
| **7** | `tabu_search` | Tabu Search Metaheuristic | Classical | 1 | **18 / 18** | 0 | 0 | **FEASIBLE** | 48.57 km | 780.7 ms |
| **8** | `kernighan_lin` | Kernighan–Lin Bipartition | Classical | 1 | **18 / 18** | 0 | 0 | **FEASIBLE** | 53.26 km | 90.6 ms |
| **9** | `vnd` | Variable Neighborhood Descent (VND) | Classical | 1 | **18 / 18** | 0 | 0 | **FEASIBLE** | 52.81 km | 76.2 ms |
| **10** | `qaoa` | QAOA Hybrid | Quantum / Variational | 1 | **18 / 18** | 0 | 0 | **FEASIBLE** | 92.99 km | 1,396.0 ms |
| **11** | `qiga` | Quantum-Inspired GA (QIGA/IQGA) | Quantum-Inspired | 1 | **18 / 18** | 0 | 0 | **FEASIBLE** | 95.07 km | 563.1 ms |

---

## 5. Verification Conclusion

- **100% Customer Coverage Invariant:** Satisfied across all 11 algorithms ($R \equiv I$).
- **Zero Duplicates & Zero Dropped Stops:** Verified across every route.
- **Fleet Constraints:** Vehicle count $\le 3$ and vehicle load $\le 40$ respected by all solutions.
- **Deduplication:** Every registered algorithm appears exactly once with unique ID and name.

