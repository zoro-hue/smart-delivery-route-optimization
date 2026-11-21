# Phase R Deliverable 10: Documentation of Failed Experiments, Rejected Hypotheses & Negative Results

**Document:** `phase_r_quantum_contribution_challenge/PHASE_R_FAILED_EXPERIMENTS.md`  
**Date:** 2026-11-06  
**Status:** Completed & Rigorously Verified  
**Branch:** `research/phase-r-quantum-contribution-challenge`

---

## 1. Scientific Integrity Policy

Scientific progress requires rigorous reporting of what does *not* work, preventing future researchers from pursuing dead ends or overstating quantum advantages. In accordance with Phase R directives, this document records all failed experiments, rejected hypotheses, and engineering bottlenecks.

---

## 2. Failed Experiment Log

### 2.1 Experiment 1: Complete-Route Improvement Over Industrial GLS
- **Hypothesis:** Dispatching QAOA on sub-routes produced by Google OR-Tools Guided Local Search (GLS) would identify hidden non-local improvements and reduce total fleet kilometers.
- **Result:** **REJECTED (0.0% net improvement across 10 instances).**
- **Root Cause:** Industrial GLS uses edge-penalty metaheuristics that already resolve the subproblem sequences into their global minima for $K \le 4$. QAOA cannot improve upon an already-optimal permutation.
- **Remediation / Takeaway:** QAOA should not be deployed uniformly as a post-processor; it must be gated by bottleneck detectors that identify unresolved asymmetric impedance traps.

### 2.2 Experiment 2: Unconstrained Transverse-Field Mixer ($H_M = \sum X_i$)
- **Hypothesis:** Standard QAOA transverse mixers with penalty terms in $H_C$ can explore the permutation space effectively.
- **Result:** **FAILED (99.96% invalid states).**
- **Root Cause:** For $K=4$, the Hilbert space is $2^{16} = 65,536$, but only $4! = 24$ states correspond to valid one-to-one routing permutations. Standard transverse mixers rotate state vectors outside the valid subspace, requiring extreme penalty multipliers that dominate the problem Hamiltonian and destroy optimization gradients.
- **Remediation:** Mandatory adoption of the continuous XY-mixer ($U_{\text{XY}}(\beta)$) and Warm-Start state preparation, which restricts exploration strictly to the Hamming-weight permutation subspace.

### 2.3 Experiment 3: Standalone QIGA for Micro-Subproblems ($K=4$)
- **Hypothesis:** Quantum-inspired bit rotation can replace local 2-opt search on small routing segments.
- **Result:** **FAILED (1/12 optimum discovery rate, 48× slower than 2-opt).**
- **Root Cause:** For $K=4$, deterministic 2-opt evaluates all 6 pairwise reversals in $0.05\text{ ms}$. QIGA's probabilistic angle updates take $2.7\text{ ms}$ and frequently stagnate in suboptimal bit combinations.
- **Remediation:** QIGA is unsuited for micro-permutations; its valid role is in intermediate-scale inter-route customer exchanges.

### 2.4 Experiment 4: Unfiltered Quantum Dispatch (Blind Execution)
- **Hypothesis:** Passing every 4-customer sub-sequence through QAOA maximizes the probability of finding improvements.
- **Result:** **REJECTED (Extreme latency inflation with 0% gain).**
- **Root Cause:** Evaluating QAOA on all sub-sequences inflated total execution time by $>250\%$ without yielding any improvements on planar Euclidean segments.
- **Remediation:** Implemented the Asymmetric Circuity and Edge-Crossing Bottleneck Screener in IP-CQE v2 to gate quantum circuit execution.

---

## 3. Summary of Negative Results for Journal Publication

1. Under fair classical budgets, quantum simulation currently provides **no complete-route distance reduction** over state-of-the-art classical metaheuristics.
2. Quantum simulation on classical hardware is **10,000× slower** than classical local search on equivalent subproblems.
3. The demonstrable scientific value of QAOA in logistics is currently limited to **non-inverting search dynamics in asymmetric impedance landscapes**, pointing the way toward future physical QPU deployments.

