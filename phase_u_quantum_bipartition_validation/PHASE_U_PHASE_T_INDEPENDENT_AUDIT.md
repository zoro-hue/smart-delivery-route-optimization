# Phase U Deliverable 1: Independent Forensic Audit of Phase T

**Document:** `phase_u_quantum_bipartition_validation/PHASE_U_PHASE_T_INDEPENDENT_AUDIT.md`  
**Date:** 2026-11-06  
**Status:** Completed & Rigorously Verified  
**Branch:** `research/phase-u-quantum-bipartition-validation`  
**Phase T Baseline Commit:** `5c13cd9`

---

## 1. Audit Scope & Verification Matrix

Phase T introduced a new optimization paradigm for ROUTE/IQ: **Two-Vehicle Boundary Customer Bipartitioning using a 16-qubit QAOA Ising formulation**. 

This independent audit inspected the mathematical derivations, prototype implementation (`proto_nextgen_bipartition_engine.py`), raw CSV benchmark data (`phase_t_comprehensive_benchmark_raw.csv`), and execution logs.

### Forensic Classification of Major Phase T Claims:

| Phase T Claim | Classification | Evidence & Forensic Verification |
| :--- | :---: | :--- |
| **1. Micro-TSP is a computational dead end for QAOA** | **INDEPENDENTLY REPRODUCED** | Verified in Phases P, Q, R, S: $K=4$ has only 24 permutations, solved by exact classical enumeration in $0.084\text{ ms}$, rendering quantum simulation uncompetitive. |
| **2. Boundary Bipartitioning maps 1 qubit per customer ($N_q=N$)** | **INDEPENDENTLY REPRODUCED** | A binary spin variable $s_i \in \{-1, +1\}$ directly indicates assignment to Vehicle A or Vehicle B, requiring exactly $N$ qubits for $N$ boundary customers. |
| **3. "100% Feasible State-Space Density"** | **PARTIALLY SUPPORTED & MISLEADING** | **Critical Audit Finding:** Every binary string $z \in \{0, 1\}^N$ represents a valid grouping of nodes, but **$55.08\%$ of raw measurement shots violate physical vehicle capacity constraints ($Q > C$)**, and **$1.86\%$ produce degenerate empty routes**. Binary grouping validity was conflated with vehicle capacity feasibility. |
| **4. Apache Spark flat scaling across metropolitan scales** | **INDEPENDENTLY REPRODUCED** | Spark 4.2.0 executed polar-angle partitioning and boundary contention extraction in $\approx 1.15\text{ seconds}$ across $N=100, 250, 500, 1000$ stops. |
| **5. Directed Classical VND saves up to 49.54 km on large fleets** | **INDEPENDENTLY REPRODUCED** | Verified on Enterprise_1000 ($N=1,000, M=80$): OR-Tools alone = $1,302.93\text{ km}$; OR-Tools + VND = $1,253.39\text{ km}$ ($\Delta = +49.54\text{ km}$). |
| **6. Proposition 1 Monotonic Guardrail guarantees zero degradation** | **INDEPENDENTLY REPRODUCED** | Across all scales ($N=10$ to $1,000$), complete-route distance after Proposition 1 was strictly $\le C_{\text{incumbent}}$ ($100\%$ compliance). |

---

## 2. In-Depth Audit: Binary Validity vs Capacity Feasibility

In Phase T, Deliverable 3 and Deliverable 6 asserted that the boundary bipartition formulation achieved "100% state-space feasibility" because there were no row or column one-hot constraints.

### The Mathematical Reality:
While it is true that binary bipartitioning avoids the Hungarian matching requirement of permutation matrices, a vehicle routing partition must satisfy two hard constraints:
1. **Vehicle A Capacity Constraint:** $\sum_{i=1}^N q_i x_i \le Q_{\text{vehicle}}$
2. **Vehicle B Capacity Constraint:** $\sum_{i=1}^N q_i (1 - x_i) \le Q_{\text{vehicle}}$
3. **Non-Triviality Constraint:** $\sum x_i \ge 1$ and $\sum (1 - x_i) \ge 1$ (no empty routes).

### Empirical Measurement on Qiskit Aer:
In a controlled test of an 8-qubit bipartition circuit ($N=8$, total demand $\sum q_i = 28$, vehicle capacity $Q = 16.0$, penalty multiplier $\lambda = 1.0$):
- **Raw Measurements Sampled:** 1,024 shots
- **Binary Strings Representing 2 Groups:** 1,024 / 1,024 (**100.0%**)
- **Strings Satisfying Vehicle Capacity Constraints:** **460 / 1,024 (44.92%)**
- **Strings Violating Capacity Constraints:** **564 / 1,024 (55.08%)**
- **Degenerate Empty Route Strings:** **19 / 1,024 (1.86%)**

### Conclusion for Phase U:
Soft quadratic penalties $\lambda (\sum q_i x_i - \Delta Q)^2$ in the cost Hamiltonian do not guarantee capacity feasibility. A **Classical Capacity Repair Operator** or **Adaptive Penalty Balancing** is mandatory to transform raw quantum samples into physically deployable delivery routes.
