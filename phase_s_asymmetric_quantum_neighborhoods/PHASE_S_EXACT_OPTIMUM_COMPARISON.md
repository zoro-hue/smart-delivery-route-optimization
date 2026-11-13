# Phase S Deliverable 6: Exact Optimum Validation & Optimality Gap Analysis

**Document:** `phase_s_asymmetric_quantum_neighborhoods/PHASE_S_EXACT_OPTIMUM_COMPARISON.md`  
**Date:** 2026-11-06  
**Status:** Completed & Rigorously Verified  
**Branch:** `research/phase-s-asymmetric-quantum-neighborhoods`

---

## 1. Executive Summary

This deliverable evaluates 20 independently generated asymmetric directed routing subproblems ($K=4$, $N_q=16$ qubits) with asymmetry ratios spanning $\alpha \in [0.24, 0.56]$.

Every method was compared directly against the certified **Exact Global Optimum** ($C_{\text{opt}}$) determined by exhaustive permutation enumeration ($4! = 24$ states).

### The Optimality Gap Metric:
$$\text{Gap}(\%) = 100 \times \frac{C_{\text{method}} - C_{\text{opt}}}{C_{\text{opt}}}$$

---

## 2. Quantitative Performance Table ($N=20$)

Aggregated results from `phase_s_asymmetric_neighborhoods_raw.csv`:

| Algorithm | Optimum Discovery Rate | Mean Optimality Gap | Max Optimality Gap | Mean Execution Time | Relative Speed vs QAOA |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Exact Enumeration ($4!$)** | **100.0%** (20/20) | **0.00%** | **0.00%** | **0.084 ms** | **7,369× faster** |
| **Variable Neighborhood Search (VNS)** | **100.0%** (20/20) | **0.00%** | **0.00%** | **0.285 ms** | **2,171× faster** |
| **Variable Neighborhood Descent (VND)** | **95.0%** (19/20) | **0.33%** | 6.56% | **0.192 ms** | **3,219× faster** |
| **Directed Relocate (1-0 Insertion)** | 75.0% (15/20) | 4.43% | 36.17% | 0.098 ms | 6,316× faster |
| **Directed 2-opt (Edge Inversion)** | 60.0% (12/20) | 15.25% | 193.89% | 0.061 ms | 10,146× faster |
| **Directed Swap (1-1 Exchange)** | 60.0% (12/20) | 15.94% | 134.23% | 0.071 ms | 8,717× faster |
| **Or-opt (Block len=2)** | 45.0% (9/20) | 23.83% | 138.79% | 0.094 ms | 6,584× faster |
| **QAOA ($p=1$, XY-Mixer + Hungarian)** | 50.0% (10/20) | 20.72% | 156.48% | **618.95 ms** | **1.0× (baseline)** |

---

## 3. Head-to-Head Pairwise Analysis

### 3.1 QAOA vs Directed 2-opt
- **QAOA Beat 2-opt:** **4 / 20 instances (20.0%)** (Tests 3, 6, 8, 17).
- In these 4 instances, the initial seed was trapped in an edge-inversion minimum. Because the road network had severe directional impedance ($\alpha > 0.35$), 2-opt could not flip the intermediate edges without incurring extreme penalties. QAOA's XY-mixer escaped via non-inverting cyclic shifts.
- **2-opt Beat QAOA:** **4 / 20 instances (20.0%)** (Tests 5, 7, 9, 19).
- **Ties:** 12 / 20 instances (60.0%).

### 3.2 QAOA vs Variable Neighborhood Descent (VND)
- **QAOA Beat VND:** **0 / 20 instances (0.0%)**.
- In **ZERO** instances did QAOA produce a lower routing cost than Classical VND.
- **VND Beat QAOA:** **9 / 20 instances (45.0%)**.
- In 9 instances, VND successfully found the global optimum while QAOA remained trapped or produced a suboptimal measurement.
- **Ties:** 11 / 20 instances (55.0%).

---

## 4. Scientific Verdict

QAOA's apparent success in Phase R was an artifact of comparing it solely against 2-opt. When compared against appropriate directed classical search (VND, Relocate, VNS), **classical local search strictly dominates QAOA in both solution quality ($0.33\%$ gap vs $20.72\%$ gap) and execution speed ($3,219\times$ faster)**.

