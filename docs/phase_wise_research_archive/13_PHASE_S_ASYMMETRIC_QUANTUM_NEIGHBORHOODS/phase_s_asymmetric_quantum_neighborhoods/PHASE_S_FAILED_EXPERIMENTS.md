# Phase S Deliverable 12: Documentation of Failed Hypotheses & Negative Results

**Document:** `phase_s_asymmetric_quantum_neighborhoods/PHASE_S_FAILED_EXPERIMENTS.md`  
**Date:** 2026-11-06  
**Status:** Completed & Rigorously Verified  
**Branch:** `research/phase-s-asymmetric-quantum-neighborhoods`

---

## 1. Scientific Integrity Statement

In adherence to rigorous academic research standards, this document records all refuted hypotheses, negative findings, and mathematical limitations discovered during Phase S.

---

## 2. Refuted Hypotheses & Forensic Post-Mortem

### 2.1 Refuted Hypothesis 1: "QAOA Has a Quantum Advantage in Asymmetric Routing"
- **Hypothesis:** Because QAOA beat 2-opt in $25.0\%$ of Phase R instances, QAOA was hypothesized to provide an optimization capability that classical algorithms could not match in asymmetric landscapes.
- **Experimental Verdict:** **REFUTED.**
- **Forensic Discovery:** The advantage was an artifact of comparing QAOA against a structurally handicapped classical baseline (symmetric 2-opt edge inversion). When compared against standard directed classical operators (Relocate, Swap, VND), classical local search found the exact global optimum in **100.0% of cases in 0.10 ms**, whereas QAOA achieved only a $50.0\%$ discovery rate in $618.9\text{ ms}$.

### 2.2 Refuted Hypothesis 2: "XY-Mixers Confine Evolution to the Permutation Subspace"
- **Hypothesis:** Planar continuous XY-mixers ($U_{\text{XY}}(\beta)$) restrict quantum state evolution strictly to feasible traveling salesperson permutations.
- **Experimental Verdict:** **MATHEMATICALLY & EMPIRICALLY REFUTED.**
- **Forensic Discovery:** While row-wise XY-mixers preserve the row one-hot sum $\sum_t X_{i, t} = 1$, they commute with neither column one-hot constraints nor inter-row particle counts. Physical simulation on Qiskit Aer revealed that **68.85% of sampled bitstrings violate the permutation constraint** due to multiple nodes occupying identical time slots, necessitating classical Hungarian bipartite projection.

### 2.3 Refuted Hypothesis 3: "QIGA + QAOA Yields Quantum-Classical Synergy"
- **Hypothesis:** Coupling QIGA and QAOA produces a cooperative optimization engine superior to either algorithm alone.
- **Experimental Verdict:** **REFUTED (Free-Rider Artifact).**
- **Forensic Discovery:** QIGA alone achieved a $0.00\%$ optimality gap in $12.4\text{ ms}$. Coupling QIGA with QAOA produced the exact same $0.00\%$ gap, but increased execution time to $631.3\text{ ms}$ ($50\times$ slowdown). QAOA contributed zero net improvement to the hybrid pipeline.

### 2.4 Refuted Hypothesis 4: "Local Asymmetric Improvements Translate to Full Fleet Routes"
- **Hypothesis:** Applying directed local search or QAOA to sub-routes will reduce total fleet delivery kilometers after Google OR-Tools finishes.
- **Experimental Verdict:** **REFUTED (0.00 km Net Improvement).**
- **Forensic Discovery:** Industrial OR-Tools GLS operates across all routes globally. By the time it finishes, every individual sub-route is already at a stationary local minimum under single-route exchanges ($\Delta = 0.00\text{ km}$ across $N = 10, 25, 50, 100$).

