# Phase S Deliverable 9: Complete-Route Reconstruction & Full Fleet Validation

**Document:** `phase_s_asymmetric_quantum_neighborhoods/PHASE_S_COMPLETE_ROUTE_VALIDATION.md`  
**Date:** 2026-11-06  
**Status:** Completed & Rigorously Verified  
**Branch:** `research/phase-s-asymmetric-quantum-neighborhoods`

---

## 1. Complete Fleet Route Integration

To determine whether local asymmetric improvements survive full-fleet route reconstruction, we evaluated complete delivery schedules across customer scales $N \in \{10, 25, 50, 100\}$ and fleet sizes $M \in \{2, 3, 6, 12\}$ on calibrated NYC road networks with asymmetric impedance $\alpha = 0.35$.

Every candidate modification was audited against:
1. **Depot Boundary Invariance:** Route begins and ends at depot (index 0).
2. **Customer Conservation:** Every customer visited exactly once.
3. **Vehicle Capacity Feasibility:** Cumulative route demand $\le Q_{\text{vehicle}} = 30.0$ units.
4. **Directed Edge Re-evaluation:** Travel distance computed via the exact directed distance matrix.

---

## 2. Quantitative Complete-Route Benchmark Table

Data source: `phase_s_complete_routes_raw.csv`:

| Scale ($N$) | Vehicles ($M$) | Certified OR-Tools Incumbent (km) | Post-VND Complete Route (km) | Post-QAOA Complete Route (km) | Complete Feasibility | Net Fleet Gain (km) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **10** | 2 | 39.92 km | 39.92 km | 39.92 km | **PASS (100%)** | **0.00 km (0.0%)** |
| **25** | 3 | 88.70 km | 88.70 km | 88.70 km | **PASS (100%)** | **0.00 km (0.0%)** |
| **50** | 6 | 139.81 km | 139.81 km | 139.81 km | **PASS (100%)** | **0.00 km (0.0%)** |
| **100** | 12 | 276.91 km | 276.91 km | 276.91 km | **PASS (100%)** | **0.00 km (0.0%)** |

---

## 3. Scientific Analysis: The Macro Optimality Trap

Why do directed local operators (VND, Relocate) and QAOA both produce **0.00 km** net complete-route improvement when post-processing OR-Tools solutions?

1. **Google OR-Tools GLS Operates Globally:**  
   OR-Tools does not just optimize sequence within individual routes; it executes inter-route relocations, exchanges, and CROSS-neighborhood moves across the entire fleet simultaneously while applying metaheuristic penalties to escape local minima.
2. **Sub-Route Convergence:**  
   By the time OR-Tools completes its 5-second search budget, each individual vehicle tour is already a local minimum under Relocate, Swap, and 2-opt. Consequently, extracting an internal 4-customer subproblem and attempting to reorder it yields the identical sequence that OR-Tools already selected.
3. **The Proposition 1 Guardrail:**  
   In all scales, Proposition 1 verified $100\%$ non-degradation:
   $$\text{Cost}(R_{\text{final}}) = \min \{ \text{Cost}(R_{\text{incumbent}}), \text{Cost}(R_{\text{candidate}}) \} = \text{Cost}(R_{\text{incumbent}})$$

