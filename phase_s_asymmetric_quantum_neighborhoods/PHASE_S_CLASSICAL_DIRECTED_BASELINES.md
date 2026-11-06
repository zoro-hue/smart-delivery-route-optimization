# Phase S Deliverable 3: Strong Asymmetric Classical Routing Baselines

**Document:** `phase_s_asymmetric_quantum_neighborhoods/PHASE_S_CLASSICAL_DIRECTED_BASELINES.md`  
**Date:** 2026-11-06  
**Status:** Completed & Rigorously Verified  
**Branch:** `research/phase-s-asymmetric-quantum-neighborhoods`

---

## 1. Overview & Baseline Specifications

To ensure an unyielding, scientifically sound standard of comparison, Phase S developed and verified an industrial suite of classical metaheuristics engineered specifically for directed routing on asymmetric graphs:

1. **Directed 2-opt:** Pairwise edge exchange with full directed-arc recalculation.
2. **Directed Relocate (1-0 Insertion):** Moves a single customer stop to an alternative position without reversing the remaining tour.
3. **Directed Swap (1-1 Exchange):** Exchanges two non-adjacent nodes without reversing intermediate sub-paths.
4. **Or-opt (Block Relocation):** Relocates consecutive sequences of 2 or 3 stops without internal path reversal.
5. **Variable Neighborhood Descent (VND):** Successively executes Relocate $\to$ Swap $\to$ Or-opt $\to$ Directed 2-opt with eager restart upon any improvement.
6. **Variable Neighborhood Search (VNS) / ILS:** Combines random perturbation (shaking) with VND descent to escape higher-order local minima.
7. **Exact Permutation Enumeration:** Evaluates all $K!$ candidates for small subproblems ($K \le 8$), providing an undeniable ground-truth cost floor.

---

## 2. Comparative Benchmark on Asymmetric Test Instances

Benchmarked on the 12 frozen Phase R asymmetric subproblems:

| Algorithm | Mean Cost (km) | Global Optimum Discovery Rate | Mean Runtime (ms) | Speedup vs QAOA Simulation |
| :--- | :---: | :---: | :---: | :---: |
| **Symmetric 2-opt (Phase R baseline)** | $85.05\text{ km}$ | 41.7% (5/12) | **0.057 ms** | 9,589× |
| **Directed 2-opt** | $85.05\text{ km}$ | 41.7% (5/12) | **0.059 ms** | 9,264× |
| **Directed Swap** | $84.28\text{ km}$ | 50.0% (6/12) | **0.068 ms** | 8,038× |
| **Directed Relocate** | **$81.18\text{ km}$** | **100.0% (12/12)** | **0.082 ms** | 6,665× |
| **Variable Neighborhood Descent (VND)** | **$81.18\text{ km}$** | **100.0% (12/12)** | **0.108 ms** | 5,061× |
| **VNS / Iterated Local Search** | **$81.18\text{ km}$** | **100.0% (12/12)** | **0.345 ms** | 1,584× |
| **Exact Enumeration ($4! = 24$)** | **$81.18\text{ km}$** | **100.0% (12/12)** | **0.110 ms** | 4,969× |
| *QAOA ($p=1$, Phase R)* | *$87.04\text{ km}$* | *58.3% (7/12)* | *546.600 ms* | *1.0× (reference)* |

---

## 3. Scientific Conclusions

1. **Relocate and VND are Dominant:** On $K=4$ asymmetric routing subproblems, Classical Relocate and VND achieve a **100.0% optimal discovery rate** across all instances, completely bypassing the local minimum traps that defeated 2-opt.
2. **Speed Disparity:** Classical VND reaches the certified global optimum in **$0.108\text{ ms}$**, whereas Qiskit Aer simulation requires **$546.6\text{ ms}$**—a $5,061\times$ computational overhead.
3. **Fair Evaluation Standard:** Any subsequent claim of quantum contribution in Phase S must be benchmarked against **VND and Relocate**, not merely 2-opt.

