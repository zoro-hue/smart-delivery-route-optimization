# Phase T Deliverable 10: Frozen Experimental Protocol & Benchmark Specifications

**Document:** `phase_t_nextgen_hybrid_architecture/PHASE_T_EXPERIMENTAL_PROTOCOL.md`  
**Date:** 2026-11-06  
**Status:** Completed & Rigorously Verified  
**Branch:** `research/phase-t-nextgen-hybrid-architecture`

---

## 1. Frozen Problem Instances & Scale Hierarchy

To evaluate scalability from micro-subproblems up to enterprise fleet operations, Phase T freezes the following problem scales:

| Scale ID | Customers ($N$) | Fleet Size ($M$) | Vehicle Capacity ($Q$) | Network Type | Random Seeds |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **Scale 1: Micro** | 10 | 2 | 15.0 | NYC Manhattan Core ($\alpha = 0.35$) | 42, 101 |
| **Scale 2: Small** | 25 | 4 | 30.0 | NYC Midtown / Queens ($\alpha = 0.30$) | 42, 101 |
| **Scale 3: Medium** | 50 | 6 | 35.0 | NYC Manhattan / Brooklyn ($\alpha = 0.32$) | 202, 303 |
| **Scale 4: Large** | 100 | 10 | 40.0 | Multi-Borough Arterial ($\alpha = 0.28$) | 404, 505 |
| **Scale 5: Enterprise-1** | 250 | 25 | 50.0 | Metropolitan Full Network ($\alpha = 0.25$) | 777 |
| **Scale 6: Enterprise-2** | 500 | 50 | 50.0 | Metropolitan Full Network ($\alpha = 0.25$) | 888 |
| **Scale 7: Enterprise-3** | 1,000 | 100 | 50.0 | Five-Borough Mega-Fleet ($\alpha = 0.25$) | 999 |

---

## 2. Ten Competitive Architectures Evaluated

Every instance is evaluated under identical road distance matrices, vehicle capacities, and objective functions across ten distinct methods:

1. **Method 1: OR-Tools GLS Baseline:** Google OR-Tools Guided Local Search (5s budget).
2. **Method 2: OR-Tools + Classical 2-opt:** OR-Tools followed by pairwise edge uncrossing.
3. **Method 3: Directed VND:** Variable Neighborhood Descent (Relocate $\to$ Swap $\to$ Or-opt $\to$ Directed 2-opt).
4. **Method 4: Directed VNS / ILS:** Variable Neighborhood Search with random shaking.
5. **Method 5: QIGA:** Standalone Quantum-Inspired Genetic Algorithm.
6. **Method 6: QAOA Alone:** Standalone QAOA subproblem dispatch.
7. **Method 7: Spark + Classical:** PySpark 4.2.0 polar partitioning followed by classical OR-Tools & VND.
8. **Method 8: Spark + QAOA:** PySpark polar partitioning with QAOA boundary bisection.
9. **Method 9: Spark + QAOA + Classical:** Full IP-CQE v2 cooperative architecture.
10. **Method 10: Full NextGen Tripartite Engine (IP-CQE v3):** Spark 4.2.0 Big Data Engine + QAOA Boundary Bipartition + QIGA Stochastic Diversification + Classical VND Foundation + Proposition 1 Guardrail.

---

## 3. Evaluation Metrics

For each run, the following metrics are recorded:
- Total complete-route distance ($C_{\text{final}}$ in km).
- Physical feasibility ($100\%$ check on capacity, visits, depot).
- Wall-clock runtime breakdown: $T_{\text{spark}}$, $T_{\text{classical}}$, $T_{\text{quantum}}$, $T_{\text{total}}$.
- Quantum improvement rate ($\Delta C > 0$).
- Guardrail activation frequency.

