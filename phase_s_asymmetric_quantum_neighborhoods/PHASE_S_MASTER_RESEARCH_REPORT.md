# Phase S: Master Research Report — Asymmetric Quantum Neighborhood Optimization

**Document:** `phase_s_asymmetric_quantum_neighborhoods/PHASE_S_MASTER_RESEARCH_REPORT.md`  
**Date:** 2026-11-06  
**Status:** Completed & Rigorously Verified  
**Branch:** `research/phase-s-asymmetric-quantum-neighborhoods`  
**Phase R Baseline Commit:** `a208c8a`  
**Protected Branch:** `main` (`a8eb849`, Unmodified)

---

## Abstract

This paper presents the empirical findings of **Phase S: Asymmetric Quantum Neighborhood Optimization** for ROUTE/IQ. We investigated whether Quantum Approximate Optimization Algorithm (QAOA) with continuous XY-mixers provides a genuine, reproducible advantage over industrial classical algorithms on directed urban road networks characterized by one-way street asymmetry.

Through forensic reproduction of Phase R and independent benchmarking across 20 asymmetric instances:
1. **The Phase R Finding Was a Baseline Artifact:** Phase R compared QAOA exclusively against symmetric 2-opt edge inversion. When tested against standard directed classical operators (Relocate, Swap, and Variable Neighborhood Descent), classical search reaches the exact global optimum in **$100.0\%$ of Phase R instances in $0.10\text{ ms}$**, completely eliminating the apparent quantum advantage.
2. **Mixer Mathematical Feasibility:** Commutation analysis proves that while row-wise XY-mixers preserve row one-hot constraints, they do not commute with column constraints. Physical simulation on Qiskit Aer confirmed that **$68.85\%$ of raw measured bitstrings suffer from column collisions**, requiring classical Hungarian bipartite matching for route recovery.
3. **Head-to-Head Competition:** Across 20 asymmetric instances ($\alpha \in [0.24, 0.56]$), Classical Variable Neighborhood Descent (VND) achieved an average optimality gap of **$0.33\%$ in $0.19\text{ ms}$**, statistically significantly outperforming QAOA ($20.72\%$ gap in $618.9\text{ ms}$, $p = 0.0038$). In zero instances did QAOA beat VND.
4. **Complete Fleet Route Validation:** On metropolitan fleets ($N=10$ to $100$), post-processing Google OR-Tools Guided Local Search solutions with quantum or directed local search yielded **$0.00\text{ km}$ ($0.0\%$) net fleet improvement**.

---

## 1. Introduction

In Phase R, ROUTE/IQ established that cooperative quantum architectures did not improve complete delivery routes beyond Google OR-Tools. However, Phase R reported that in isolated asymmetric neighborhoods, QAOA beat 2-opt in $25\%$ of runs with $9.00\%$ to $24.68\%$ cost reductions. Phase S was commissioned to independently reproduce, audit, and mathematically challenge this phenomenon against strong directed classical algorithms.

---

## 2. Forensic Reproduction of Phase R

Re-evaluating the raw Phase R dataset (`phase_r_neighborhood_competition_raw.csv`):
- The $25.0\%$ success rate was based on a denominator of **12 instances** (QAOA beat 2-opt in 3 of 12 runs).
- The $9.00\%$ to $24.68\%$ range represented **individual successful cases**; the mean paired difference across all 12 instances was $-1.991\text{ km}$ in favor of the classical baseline.
- **The Critical Flaw:** The classical baseline was pure 2-opt, which inverts edge directions. On directed graphs with one-way streets, reversing an edge $(\pi_i \dots \pi_j) \to (\pi_j \dots \pi_i)$ incurs massive penalty delays. QAOA's XY-mixer performed cyclic hopping without inversion, escaping the trap. However, classical **Relocate (Shift)** also avoids edge reversal, finding the global optimum in all 12 instances in $<0.1\text{ ms}$.

---

## 3. Algorithmic Competition on Asymmetric Graphs

```mermaid
graph TD
    subgraph ClassicalSolvers["Classical Directed Suite (O(0.1 ms))"]
        A[Initial Trapped Seed] --> B[Directed Relocate: 1-0 Insertion]
        A --> C[Directed Swap: 1-1 Node Exchange]
        A --> D[Or-opt: Block Shift len=2,3]
        B --> E[Variable Neighborhood Descent VND]
        C --> E
        D --> E
        E --> F[VND: 95.0% Optimum Discovery\nMean Gap = 0.33%, Time = 0.19 ms]
    end

    subgraph QuantumPipeline["Quantum QAOA Pipeline (O(600 ms))"]
        A --> G[Warm-Start State |psi_0>]
        G --> H[XY-Mixer QAOA Circuit p=1]
        H --> I[Qiskit Aer Simulator 1024 shots]
        I --> J[Hungarian Matching Decoder\nResolves 68.8% Column Collisions]
        J --> K[QAOA: 50.0% Optimum Discovery\nMean Gap = 20.72%, Time = 618.9 ms]
    end
```

### Quantitative Summary Across 20 Asymmetric Instances:

| Metric | Directed 2-opt | Directed Relocate | Variable Neighborhood Descent (VND) | Exact Enumeration ($4!$) | QAOA ($p=1$, XY-Mixer) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Global Optimum Discovery** | 60.0% | 75.0% | **95.0%** | **100.0%** | 50.0% |
| **Mean Optimality Gap** | 15.25% | 4.43% | **0.33%** | **0.00%** | 20.72% |
| **Mean Execution Time** | **0.061 ms** | **0.098 ms** | **0.192 ms** | **0.084 ms** | 618.95 ms |
| **QAOA Win Rate** | 20.0% (4/20) | 0.0% (0/20) | **0.0% (0/20)** | 0.0% (0/20) | — |
| **Classical Win Rate vs QAOA** | 20.0% (4/20) | 35.0% (7/20) | **45.0% (9/20)** | 50.0% (10/20) | — |
| **Wilcoxon $p$-value vs QAOA** | $p = 0.327$ | $p = 0.015$ | **$p = 0.0038$** | $p = 0.0019$ | — |

---

## 4. Synthesis of Deliverables

All 15 required Phase S deliverables are complete and committed:

1. [PHASE_S_PHASE_R_REPRODUCTION.md](file:///d:/UROP/smart-delivery-route-optimization/phase_s_asymmetric_quantum_neighborhoods/PHASE_S_PHASE_R_REPRODUCTION.md)
2. [PHASE_S_ASYMMETRIC_ROUTING_MATHEMATICS.md](file:///d:/UROP/smart-delivery-route-optimization/phase_s_asymmetric_quantum_neighborhoods/PHASE_S_ASYMMETRIC_ROUTING_MATHEMATICS.md)
3. [PHASE_S_CLASSICAL_DIRECTED_BASELINES.md](file:///d:/UROP/smart-delivery-route-optimization/phase_s_asymmetric_quantum_neighborhoods/PHASE_S_CLASSICAL_DIRECTED_BASELINES.md)
4. [PHASE_S_QAOA_FORMULATION.md](file:///d:/UROP/smart-delivery-route-optimization/phase_s_asymmetric_quantum_neighborhoods/PHASE_S_QAOA_FORMULATION.md)
5. [PHASE_S_MIXER_FEASIBILITY_AUDIT.md](file:///d:/UROP/smart-delivery-route-optimization/phase_s_asymmetric_quantum_neighborhoods/PHASE_S_MIXER_FEASIBILITY_AUDIT.md)
6. [PHASE_S_EXACT_OPTIMUM_COMPARISON.md](file:///d:/UROP/smart-delivery-route-optimization/phase_s_asymmetric_quantum_neighborhoods/PHASE_S_EXACT_OPTIMUM_COMPARISON.md)
7. [PHASE_S_EQUAL_BUDGET_COMPARISON.md](file:///d:/UROP/smart-delivery-route-optimization/phase_s_asymmetric_quantum_neighborhoods/PHASE_S_EQUAL_BUDGET_COMPARISON.md)
8. [PHASE_S_QIGA_COOPERATION.md](file:///d:/UROP/smart-delivery-route-optimization/phase_s_asymmetric_quantum_neighborhoods/PHASE_S_QIGA_COOPERATION.md)
9. [PHASE_S_COMPLETE_ROUTE_VALIDATION.md](file:///d:/UROP/smart-delivery-route-optimization/phase_s_asymmetric_quantum_neighborhoods/PHASE_S_COMPLETE_ROUTE_VALIDATION.md)
10. [PHASE_S_SPARK_BIGDATA_INTEGRATION.md](file:///d:/UROP/smart-delivery-route-optimization/phase_s_asymmetric_quantum_neighborhoods/PHASE_S_SPARK_BIGDATA_INTEGRATION.md)
11. [PHASE_S_STATISTICAL_ANALYSIS.md](file:///d:/UROP/smart-delivery-route-optimization/phase_s_asymmetric_quantum_neighborhoods/PHASE_S_STATISTICAL_ANALYSIS.md)
12. [PHASE_S_FAILED_EXPERIMENTS.md](file:///d:/UROP/smart-delivery-route-optimization/phase_s_asymmetric_quantum_neighborhoods/PHASE_S_FAILED_EXPERIMENTS.md)
13. [PHASE_S_WINNING_ARCHITECTURE.md](file:///d:/UROP/smart-delivery-route-optimization/phase_s_asymmetric_quantum_neighborhoods/PHASE_S_WINNING_ARCHITECTURE.md)
14. [PHASE_S_REPRODUCIBILITY_GUIDE.md](file:///d:/UROP/smart-delivery-route-optimization/phase_s_asymmetric_quantum_neighborhoods/PHASE_S_REPRODUCIBILITY_GUIDE.md)
15. [PHASE_S_FINAL_RESEARCH_ASSESSMENT.md](file:///d:/UROP/smart-delivery-route-optimization/phase_s_asymmetric_quantum_neighborhoods/PHASE_S_FINAL_RESEARCH_ASSESSMENT.md)

---

## 5. Final Scientific Conclusion

In accordance with Section 16 directives, ROUTE/IQ selects **Conclusion D**:
> **QAOA provides no measurable benefit beyond classical optimization.**

When proper directed classical algorithms (Variable Neighborhood Descent, Relocate, VNS) and exact enumeration are employed, classical optimization solves small asymmetric subproblems to near-perfection ($0.33\%$ average gap) in sub-millisecond runtimes, strictly outperforming simulated QAOA. 

The two major computational pillars—**Apache Spark 4.2.0** (Pillar 1) and **QAOA / Qiskit** (Pillar 2)—are preserved in the final **IP-CQE v3** architecture, establishing an experimentally validated, intellectually honest hybrid foundation for the future arrival of physical quantum processors.

