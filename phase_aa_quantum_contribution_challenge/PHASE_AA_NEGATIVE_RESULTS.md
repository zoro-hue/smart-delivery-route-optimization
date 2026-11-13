# PHASE AA NEGATIVE RESULTS
## Exhaustive Documentation of Disproved Hypotheses, Negative Findings, and Algorithmic Realities
**ROUTE/IQ — Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing**  
**Department of Computer Science and Engineering, SRM University-AP**  
**Supervisor:** Dr. Vishnu Prasad Verma  

---

## 1. SCIENTIFIC COMMITMENT TO HONEST REPORTING

A core tenet of the ROUTE/IQ research initiative is the preservation of scientific integrity. Negative results are as vital to the scientific literature as positive breakthroughs. This document catalogs all negative findings and disproved claims identified during the Phase AA challenge.

---

## 2. FORMAL CATALOG OF NEGATIVE FINDINGS

### Negative Finding 1: Quantum Advantage Disappears Under Equal Wall-Clock Budgets
- **Hypothesis:** QAOA provides a superior optimization trajectory compared to classical search running for the same duration.
- **Empirical Reality:** When classical Multistart Kernighan-Lin was given the same $\sim 34\text{ ms}$ that QAOA required, it achieved **$588.69\text{ km}$** compared to QAOA's **$576.32\text{ km}$**. The paired difference yields:
  $$p = 0.2529 \quad (> 0.05)$$
- **Status:** **DISPROVED**. Under equal execution budgets, simulated QAOA provides no statistically significant advantage.

### Negative Finding 2: Quantum Advantage Disappears Under Equal Candidate Evaluations
- **Hypothesis:** A quantum ansatz explores the configuration space more efficiently than classical local search operators.
- **Empirical Reality:** When classical Tabu Search was restricted to the same 512 candidate evaluations as QAOA, it achieved **$582.61\text{ km}$** in only **$12.90\text{ ms}$** ($2.57\times$ faster than QAOA). The paired difference yields:
  $$p = 0.1263 \quad (> 0.05)$$
- **Status:** **DISPROVED**. Classical Tabu Search achieves statistical parity in a fraction of the time.

### Negative Finding 3: Standalone QAOA Fails Without Classical Incumbent Fallback
- **Hypothesis:** QAOA produces high-quality standalone vehicle bipartitions.
- **Empirical Reality:** In **55% of benchmark instances**, QAOA proposed partitions that were inferior to the initial classical incumbent. When evaluated without Proposition 1 fallback (Variant 3), raw QAOA achieved **$582.42\text{ km}$** ($p = 0.2327$ vs. Single-Pass KL).
- **Status:** **DISPROVED**. QAOA cannot operate reliably as a standalone solver; its apparent success in Phase Z was an artifact of classical fallback absorbing 55% of its failures.

### Negative Finding 4: Pure Classical Random Sampling Replicates QAOA Quality
- **Hypothesis:** The quantum statevector generates unique, non-classical cut configurations that cannot be found by stochastic exploration.
- **Empirical Reality:** Replacing the quantum circuit with pure classical uniform random sampling of 512 feasible cuts followed by Proposition 1 and VND achieved **$576.40\text{ km}$**, within **$0.66\text{ km}$** of QAOA ($575.74\text{ km}$):
  $$t = 0.244, \quad p = 0.8101$$
- **Status:** **DISPROVED**. QAOA's performance is statistically indistinguishable from classical random diversity generation coupled with the Proposition 1 ratchet.

### Negative Finding 5: Out-of-Sample Generalization Fails
- **Hypothesis:** The Phase Z reported $p = 0.0100$ generalizes across diverse logistics landscapes.
- **Empirical Reality:** On a separate held-out test suite of 20 diverse instances, QAOA with Proposition 1 achieved $p = 0.0708$ vs. Single-Pass KL, $p = 0.4450$ vs. Tabu Search, and $p = 0.5903$ vs. Multistart KL.
- **Status:** **DISPROVED**. The $p < 0.05$ result did not replicate out-of-sample.

### Negative Finding 6: The QUBO Ground State Does Not Minimize Complete Route Distance
- **Hypothesis:** Minimizing the boundary QUBO Hamiltonian directly minimizes fleet delivery distance.
- **Empirical Reality:** Evaluating all $65{,}536$ states to find the exact global minimum cut of the QUBO produced a complete route distance of **$581.96\text{ km}$**, which was worse than slightly suboptimal QUBO states sampled by QAOA ($575.74\text{ km}$).
- **Status:** **DISPROVED**. The QUBO surrogate cut cost is fundamentally misaligned with sequential TSP routing distances.

