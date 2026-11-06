# PHASE AB DELIVERABLE 11: LIMITATIONS & NEGATIVE RESULTS

## Project: ROUTE/IQ — Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing
**Institution:** SRM University-AP | **Supervisor:** Dr. Vishnu Prasad Verma

---

## 1. Transparency & Scientific Integrity

True scientific progress requires honest documentation of hypotheses that failed under rigorous empirical scrutiny. In accordance with UROP standards, this deliverable catalog's all negative results and operational boundaries encountered in Phase AB.

---

## 2. Documented Negative Findings

### 1. No Quantum Route Advantage Over Classical Metaheuristics
- **Empirical Evidence:** In head-to-head 30-instance evaluation under equal evaluation budgets ($B = 512$), QAOA achieved a mean fleet distance of **606.36 km**, trailing Tabu Search (**595.45 km**) by 10.91 km and Random Feasible sampling (**602.90 km**) by 3.46 km.
- **Statistical Significance:** Paired t-test between QAOA and classical methods yielded $p > 0.05$ across all configurations.

### 2. High Quantum Rejection Rate (70.0%)
- **Empirical Evidence:** Out of 30 subproblems evaluated with QAOA, **21 candidates (70.0%) were rejected by Proposition 1** because they produced higher tour distances than the classical incumbent.
- **Root Cause:** QAOA optimizes a discrete 1D Ising Hamiltonian with quadratic penalty approximations. It cannot natively perceive continuous 2D Euclidean Euclidean TSP tour dynamics or edge cross-intersections.

### 3. Simulation Latency Dominance
- **Empirical Evidence:** Simulating a 16-qubit QAOA statevector requires $644.85\text{ ms}$ on classical CPU hardware, compared to $19.90\text{ ms}$ for Kernighan-Lin and $33.85\text{ ms}$ for Tabu Search.
- **Impact:** On simulated hardware, QAOA is **19.0x slower** than classical heuristics.

### 4. Uniform Random Sampling Matches Quantum Performance
- **Empirical Evidence:** Generating 512 uniform random capacity-feasible bitstrings and applying Algorithmic VND achieves **602.90 km** ($p = 0.4910$ vs QAOA).
- **Theoretical Insight:** This proves that the solution quality observed in hybrid quantum pipelines is largely driven by classical post-processing (VND) and Proposition 1 incumbent preservation, not quantum superposition.

---

## 3. Engineering Limitations

1. **Physical QPU Noise:** While circuits have been transpiled for IBM Heavy-Hex architectures, running on noisy intermediate-scale quantum (NISQ) hardware introduces depolarizing gate noise and readout errors that degrade raw bitstring fidelity without error suppression.
2. **Py4J IPC Overhead:** For small instances ($N < 1,000$), PySpark inter-process communication adds $\approx 40\text{ ms}$ overhead, necessitating the in-memory NumPy fallback for micro-batches.
