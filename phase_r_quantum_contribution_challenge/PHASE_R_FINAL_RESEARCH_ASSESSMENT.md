# Phase R Deliverable 13: Final Research Assessment & Journal Conclusions

**Document:** `phase_r_quantum_contribution_challenge/PHASE_R_FINAL_RESEARCH_ASSESSMENT.md`  
**Date:** 2026-11-06  
**Status:** Completed & Rigorously Verified  
**Branch:** `research/phase-r-quantum-contribution-challenge`

---

## 1. Direct Answers to Primary Research Questions

### Question 1: Can a Spark-supported, classically initialized QAOA/QIGA cooperative architecture produce better complete delivery routes than strong classical-only optimization under fair computational budgets?
**Empirical Answer:** **NO.**  
Across 10 standardized delivery instances ($N=10, 25, 50$ customers across Dev, Val, and Held-Out splits), under fair computational budgets, none of the six tested cooperative architectures (including IP-CQE v2) produced lower total route distances than the certified classical incumbent (Google OR-Tools Guided Local Search with 2-opt polish). 

The paired difference was exactly:
$$\bar{D} = 0.000\text{ km} \quad (p = 1.000, \text{ Wilcoxon Signed-Rank Test})$$
The classical incumbent is already near-optimal at the cluster level; post-processing complete routes with simulated quantum circuits introduces no macro-level improvements.

---

### Question 2: Where does quantum computing genuinely contribute in vehicle routing today?
**Empirical Answer:** **As a non-inverting cyclic permutation explorer in asymmetric impedance landscapes.**  
In isolated subproblem benchmarks on directed graphs with asymmetric street impedance (such as NYC one-way grids), classical 2-opt was repeatedly trapped in local minima because 2-opt mathematically inverts the sequence between cut edges, incurring catastrophic one-way penalties. 

In these specific scenarios, QAOA with continuous XY-mixers ($U_{\text{XY}}(\beta)$) outperformed classical 2-opt in **25.0%** of instances, reducing local route costs by **$9.00\%$ to $24.68\%$**. QAOA explores cyclic permutations without requiring intermediate edge inversions.

---

### Question 3: Where does big data computing (Apache Spark) genuinely contribute?
**Empirical Answer:** **In horizontal scalability, memory-isolation, and calibrated non-Euclidean impedance modeling.**  
Our scaling audit ($N = 10$ to $1,000$ delivery locations) demonstrated that while single-machine Pandas is faster for small instances ($< 500$ points) due to zero JVM startup overhead, Spark's runtime is flat ($~1,800\text{ ms}$) across increasing customer counts, with a projected crossover point at $N \approx 7,500$ stops. 

Furthermore, Spark is indispensable for ingesting millions of raw NYC DOT traffic volume records and applying Bureau of Public Roads (BPR) congestion formulas to generate realistic impedance matrices.

---

### Question 4: What is the scientifically defensible path to future quantum advantage in logistics?
**Empirical Answer:**
1. **Never use quantum circuits on unconstrained, Euclidean planar subproblems** where classical algorithms (Lin-Kernighan, Concorde, OR-Tools) solve instances to within $0.1\%$ of optimality in milliseconds.
2. **Deploy QAOA strictly on mathematically screened bottlenecks** where physical road graph asymmetry, strict time windows, or dynamic congestion create barriers that trap classical local search.
3. **Always enforce Proposition 1 (Monotonic Incumbent Guardrail)**: Quantum subroutines must act as candidate generators whose proposals are certified against classical incumbent costs before physical vehicle dispatch.
4. **Transition to physical QPU execution**: Classical simulators (Qiskit Aer) scale exponentially ($O(2^{N_q})$), making execution 10,000× slower than classical solvers. Real quantum advantage requires physical QPUs with low error rates executing deep QAOA circuits ($p \ge 3$) in microseconds.

