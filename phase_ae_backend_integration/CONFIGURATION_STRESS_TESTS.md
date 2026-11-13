# ROUTE/IQ — DYNAMIC CONFIGURATION & FLEET STRESS TEST SUITE
**Phase AE Empirical Verification & Robustness Protocol**
**Repository:** `D:\UROP\smart-delivery-route-optimization`
**Branch:** `research/phase-ae-backend-integration`

---

## 1. Test Matrix Overview

To verify that the system maintains dynamic fleet consistency and never omits customer stops ($R == I$) under arbitrary user inputs, the following stress testing matrix is executed across all solvers.

| Scenario ID | Test Case Description | Invariant Tested | Stress Parameter | Expected Result | Pass/Fail |
|---|---|---|---|---|---|
| **ST-01** | Vehicle fleet reduced ($K=5 \to K=2$) | Lower bound $K_{\min} \ge \lceil D/Q \rceil$ | Demand = 250, Cap = 100 | Dynamic capacity scaling; 100% stop coverage | **PASS** |
| **ST-02** | Capacity reduced below individual stop demand | Capacity Feasibility | Stop demand = 15, Cap = 10 | Capacity guardrail adjusts $Q_{\text{eff}} \ge d_{\max}$; 100% coverage | **PASS** |
| **ST-03** | Stop count increased ($N=8 \to N=25$) | Universal Coverage $R == I$ | Stops = 25 | All 25 stops visited; 0 unserved stops | **PASS** |
| **ST-04** | Stop count reduced ($N=18 \to N=4$) | Empty vehicle pruning | Stops = 4, Vehicles = 6 | Empty routes pruned cleanly; remaining routes feasible | **PASS** |
| **ST-05** | QAOA with $N > 8$ customers | Quantum Subproblem Decoding | Stops = 18 | QAOA optimizes 8-qubit boundary; repair integrates all 18 | **PASS** |
| **ST-06** | Zero/Negative demand inputs | Input Validation Guard | Demand = 0.0 | Demand clamped to minimum 1.0 unit | **PASS** |
| **ST-07** | Extreme distance disparity (Manhattan to Bronx) | Road Network Snapping | Coordinate span > 20 km | Real road Dijkstra waypoints reconstructed | **PASS** |
| **ST-08** | Rapid algorithm switching & concurrent requests | Thread Pool Stability | 8 algorithms in parallel | ThreadPoolExecutor completes with unique canonical keys | **PASS** |

---

## 2. Invariant Verification Results

### Stress Case 1: Invariant $R == I$ Across 8 Algorithms
- Input Stops: 18 customer delivery locations
- Evaluated Algorithms:
  1. `routeiq_cooperative`: Visited = 18, Unserved = 0, Duplicates = 0 -> **VALID**
  2. `ortools`: Visited = 18, Unserved = 0, Duplicates = 0 -> **VALID**
  3. `clarke_wright`: Visited = 18, Unserved = 0, Duplicates = 0 -> **VALID**
  4. `two_opt`: Visited = 18, Unserved = 0, Duplicates = 0 -> **VALID**
  5. `dijkstra`: Visited = 18, Unserved = 0, Duplicates = 0 -> **VALID**
  6. `astar`: Visited = 18, Unserved = 0, Duplicates = 0 -> **VALID**
  7. `qiga`: Visited = 18, Unserved = 0, Duplicates = 0 -> **VALID**
  8. `qaoa`: Visited = 18, Unserved = 0, Duplicates = 0 -> **VALID**

### Stress Case 2: Best Feasible Determination
- No algorithm with unserved stops ($M > 0$) can receive the "Best Feasible" badge.
- Solutions with constraint violations are marked "Penalized".
- Lowest distance among feasible solutions (`routeiq_cooperative` / `ortools`) is awarded Best Feasible.

