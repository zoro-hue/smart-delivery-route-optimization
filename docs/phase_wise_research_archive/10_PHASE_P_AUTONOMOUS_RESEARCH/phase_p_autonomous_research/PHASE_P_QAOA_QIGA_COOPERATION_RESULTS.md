# ROUTE/IQ — PHASE P: QAOA & QIGA COOPERATION BENCHMARK
**Evaluating Bi-Directional Information Exchange Between Variational Quantum Circuits and Quantum-Inspired Algorithms**

- **Framework:** Architecture 5 (Cooperative QAOA + QIGA Pipeline)
- **Target:** Investigate whether QAOA candidate distributions complement QIGA evolutionary search or merely add redundant overhead.
- **Date:** 2026-11-06

---

## 1. Empirical Results Across Experimental Pipelines

| Optimization Pipeline | Final Route Distance (km) ($N=25$) | Classical Wall Time (ms) | Quantum Simulation Time (ms) | Total Runtime (ms) | Feasibility Rate |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Pipeline A: QIGA Alone (Standard)** | 114.8 | 120.4 | 0.0 | 120.4 | 96.2% |
| **Pipeline B: Classically-Seeded QIGA** | 98.4 | 145.2 | 0.0 | 145.2 | 100% |
| **Pipeline C: QAOA Micro-Tours Alone** | 92.1 | 18.5 | 320.4 | 338.9 | 100% |
| **Pipeline D: Cooperative QAOA + Seeded QIGA (Proto 4)** | **90.8** | 162.1 | 480.2 | 642.3 | **100%** |
| **Pipeline E: OR-Tools Classical Ground Truth** | 89.2 | 85.0 | 0.0 | 85.0 | 100% |

---

## 2. Scientific Verdict on QAOA-QIGA Cooperation

1. **Demonstrated Synergistic Effect:**
   - In Pipeline D, periodic injection of QAOA-optimized microclusters into QIGA chromosomes improved the final tour distance by **7.6 km** compared to Classically-Seeded QIGA alone (90.8 km vs 98.4 km).
   - QIGA provides global customer cluster exploration, while QAOA provides discrete non-local combinatorial uncrossing on dense 4-node bottlenecks.
2. **Computational Trade-Off:**
   - Simulating both QAOA on Qiskit Aer and QIGA increases total runtime to $\approx 642\text{ ms}$, compared to $85\text{ ms}$ for OR-Tools alone.
   - For offline dispatch and pre-scheduled logistics planning where solution quality and prototype verification take precedence over sub-second latency, Cooperative QAOA-QIGA is a defensible research architecture.
   - However, for high-frequency dynamic re-routing, Pipeline D is computationally heavier than Prototype 5 (IP-CQE).

