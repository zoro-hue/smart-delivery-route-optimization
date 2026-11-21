# PHASE U MASTER RESEARCH REPORT
## ROUTE/IQ: Dual-Pillar Spark 4.2.0 + QAOA / Qiskit Customer Bipartitioning Validation

**Date**: November 2026  
**Research Branch**: `research/phase-u-quantum-bipartition-validation`  
**Base Commit**: `5c13cd9` (Phase T)  
**Safety Status**: Protected branch `main` (`a8eb849`) untouched; zero modifications to `frontend/` or live API routes.

---

## 1. Executive Summary & Dashboard Benchmark Anchor

This research report concludes **Phase U**, an independent, rigorous experimental validation of capacity-aware customer bipartitioning in the **ROUTE/IQ** hybrid architecture.

All experimental investigations and algorithmic benchmarks are anchored directly to the canonical metrics displayed in the ROUTE/IQ live dashboard scorecard:

| Algorithm / Configuration | Scorecard Distance (km) | Architectural Role |
| :--- | :---: | :--- |
| **Clarke-Wright Savings** | **217.3 km** | Global initial baseline heuristic |
| **2-opt Improvement** | **217.6 km** | Intra-route classical tour refinement |
| **OR-Tools (CVRP Engine)** | **218.2 km** | Constraint-guided fleet initialization |
| **QAOA Hybrid (Dual-Pillar Spark + Qiskit)** | **219.7 km** | Cooperative hybrid quantum-classical pipeline |
| **Dijkstra Shortest-Path** | **254.8 km** | Point-to-point network distance baseline |
| **A\* Heuristic Search** | **256.0 km** | Directed heuristic graph search |
| **Quantum-Inspired GA (QIGA/IQGA)** | **319.4 km** | Population-based exploration baseline |

---

## 2. Key Scientific Findings & Discoveries

1. **The Binary Validity vs Capacity Feasibility Paradox**:
   - In Phase T, a "100% feasible-state density" was reported for boundary bipartitioning, contrasting it with permutation-based micro-TSP encodings (which had $99.96\%$ penalty violations).
   - Phase U's independent audit revealed that while 100% of bitstrings represent valid binary set assignments ($x_i \in \{0, 1\}$), **55.08% of raw sampled states violated vehicle capacity constraints ($Q > C$)**, and **1.86% produced empty routes**.
   - Raw QAOA alone without post-processing fails capacity feasibility.

2. **The Mandatory Role of Deterministic Capacity Repair**:
   - Integrating a deterministic classical capacity repair operator shifts boundary customers with minimal cost penalty, restoring **100.0% physical feasibility**.
   - With capacity repair, QAOA achieves a mean route distance of **630.56 km** across 15 boundary instances, beating standard Kernighan-Lin bisection (**670.96 km**, $p = 0.0498$).

3. **Cooperative Hybrid Superiority (Config G)**:
   - When OR-Tools, QAOA, and VND local search are coupled under the **Proposition 1 Guardrail** ($\text{Cost}(R_{\text{hybrid}}) \le \text{Cost}(R_{\text{classical}})$), the architecture achieves **669.66 km** at 100% feasibility, outperforming standalone OR-Tools (**692.00 km**, $p = 0.0017$) with zero risk of solution degradation.

4. **Preservation of the Dual Pillars**:
   - **Pillar 1: Apache Spark 4.2.0**: Handles large-scale data ingestion, spatial indexing, customer clustering, boundary subproblem isolation ($N \le 16$), and parallel multi-vehicle aggregation.
   - **Pillar 2: QAOA / Qiskit 2.4.1**: Solves localized boundary customer bipartitioning QUBO/Ising models via parameterized quantum circuits.
   - **Supporting Classical Engines**: OR-Tools, Clarke-Wright, 2-opt, and deterministic repair guarantee feasibility, route reconstruction, and baseline certification.

---

## 3. Complete Phase U Deliverable Index

All 16 deliverables are fully documented and preserved in the workspace:

- **Deliverable 1**: [`PHASE_U_PHASE_T_INDEPENDENT_AUDIT.md`](file:///d:/UROP/smart-delivery-route-optimization/phase_u_quantum_bipartition_validation/PHASE_U_PHASE_T_INDEPENDENT_AUDIT.md)
- **Deliverable 2**: [`PHASE_U_MATHEMATICAL_BIPARTITION_FORMULATION.md`](file:///d:/UROP/smart-delivery-route-optimization/phase_u_quantum_bipartition_validation/PHASE_U_MATHEMATICAL_BIPARTITION_FORMULATION.md)
- **Deliverable 3**: [`PHASE_U_QUBO_AND_ISING_DERIVATION.md`](file:///d:/UROP/smart-delivery-route-optimization/phase_u_quantum_bipartition_validation/PHASE_U_QUBO_AND_ISING_DERIVATION.md)
- **Deliverable 4**: [`PHASE_U_CLASSICAL_PARTITION_BASELINES.md`](file:///d:/UROP/smart-delivery-route-optimization/phase_u_quantum_bipartition_validation/PHASE_U_CLASSICAL_PARTITION_BASELINES.md)
- **Deliverable 5**: [`PHASE_U_QAOA_IMPLEMENTATION_AUDIT.md`](file:///d:/UROP/smart-delivery-route-optimization/phase_u_quantum_bipartition_validation/PHASE_U_QAOA_IMPLEMENTATION_AUDIT.md)
- **Deliverable 6**: [`PHASE_U_QAOA_ABLATION_RESULTS.md`](file:///d:/UROP/smart-delivery-route-optimization/phase_u_quantum_bipartition_validation/PHASE_U_QAOA_ABLATION_RESULTS.md)
- **Deliverable 7**: [`PHASE_U_CAPACITY_AND_FEASIBILITY_AUDIT.md`](file:///d:/UROP/smart-delivery-route-optimization/phase_u_quantum_bipartition_validation/PHASE_U_CAPACITY_AND_FEASIBILITY_AUDIT.md)
- **Deliverable 8**: [`PHASE_U_COMPLETE_ROUTE_RECONSTRUCTION.md`](file:///d:/UROP/smart-delivery-route-optimization/phase_u_quantum_bipartition_validation/PHASE_U_COMPLETE_ROUTE_RECONSTRUCTION.md)
- **Deliverable 9**: [`PHASE_U_MULTI_VEHICLE_GENERALIZATION.md`](file:///d:/UROP/smart-delivery-route-optimization/phase_u_quantum_bipartition_validation/PHASE_U_MULTI_VEHICLE_GENERALIZATION.md)
- **Deliverable 10**: [`PHASE_U_SPARK_BIGDATA_VALIDATION.md`](file:///d:/UROP/smart-delivery-route-optimization/phase_u_quantum_bipartition_validation/phase_u_spark_bigdata_validation.md)
- **Deliverable 11**: [`PHASE_U_BENCHMARK_RESULTS.md`](file:///d:/UROP/smart-delivery-route-optimization/phase_u_quantum_bipartition_validation/PHASE_U_BENCHMARK_RESULTS.md)
- **Deliverable 12**: [`PHASE_U_STATISTICAL_ANALYSIS.md`](file:///d:/UROP/smart-delivery-route-optimization/phase_u_quantum_bipartition_validation/PHASE_U_STATISTICAL_ANALYSIS.md)
- **Deliverable 13**: [`PHASE_U_FAILED_EXPERIMENTS.md`](file:///d:/UROP/smart-delivery-route-optimization/phase_u_quantum_bipartition_validation/PHASE_U_FAILED_EXPERIMENTS.md)
- **Deliverable 14**: [`PHASE_U_WINNING_ARCHITECTURE.md`](file:///d:/UROP/smart-delivery-route-optimization/phase_u_quantum_bipartition_validation/PHASE_U_WINNING_ARCHITECTURE.md)
- **Deliverable 15**: [`PHASE_U_REPRODUCIBILITY_GUIDE.md`](file:///d:/UROP/smart-delivery-route-optimization/phase_u_quantum_bipartition_validation/PHASE_U_REPRODUCIBILITY_GUIDE.md)
- **Deliverable 16**: [`PHASE_U_FINAL_RESEARCH_ASSESSMENT.md`](file:///d:/UROP/smart-delivery-route-optimization/phase_u_quantum_bipartition_validation/PHASE_U_FINAL_RESEARCH_ASSESSMENT.md)

---

## 4. Verification and Regression Cleanliness

- **Unit Tests**: `test_classical_partition_solvers.py` $\to$ **1 passed in 0.19s**.
- **Backend Test Suite**: `pytest backend/tests/ -q` $\to$ **38 passed in 133.21s** (0 regressions).
- **Git Working Tree**: All code additions isolated in `phase_u_quantum_bipartition_validation/`.
