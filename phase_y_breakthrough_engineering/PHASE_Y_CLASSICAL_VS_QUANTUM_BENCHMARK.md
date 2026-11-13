# Deliverable 8: Phase Y Classical versus Quantum Benchmark

## 1. Fair Benchmarking Standards

All quantum and classical algorithms were evaluated under identical problem instances, objective functions ($H_C$), vehicle capacity limits ($C_A, C_B$), and downstream tour sequencing (algorithmic Variable Neighborhood Descent):

---

## 2. Head-to-Head Performance Matrix ($N=15$ Instances)

| Algorithm Pipeline | Algorithm Nature | Mean Route Distance (km) | Mean Runtime (ms) | Capacity Feasibility Rate (%) | Incumbent Improvement Rate (%) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Kernighan-Lin Graph Bisection** | Classical Deterministic | **542.28 km** | **1.06 ms** | **100.0%** | **40.0%** |
| **Multistart Local Search (MLS)** | Classical Metaheuristic | 546.84 km | 8.21 ms | **100.0%** | Baseline Incumbent |
| **Exact Enumeration ($2^N$)** | Classical Ground Truth | **542.28 km** | 81.83 ms | **100.0%** | **40.0%** (Optimal) |
| **Continuous XY-Mixer QAOA (Form. B)**| Quantum Variational | 545.10 km | 84.19 ms | 79.9% (Raw) / 100% (Repaired) | 33.3% |
| **Standard Transverse QAOA (Form. A)**| Quantum Variational | 546.84 km | 121.58 ms | 31.5% (Raw) / 100% (Repaired) | 40.0% |
| **Adaptive Fast QAOA (Form. F)** | Quantum Variational | 546.84 km | 39.84 ms | 31.3% (Raw) / 100% (Repaired) | 33.3% |
| **Random Feasible Control** | Stochastic Baseline | 548.15 km | 5.20 ms | 100.0% (Repaired) | 0.0% |

---

## 3. Honest Scientific Conclusions

1. **Classical Superiority on Current Hardware**:
   - Classical Kernighan-Lin achieved **542.28 km**, outperforming all simulated quantum formulations while executing **$37.6\times$ faster** than Adaptive Fast QAOA (1.06 ms vs 39.84 ms) and **$114.7\times$ faster** than standard QAOA (121.58 ms).
2. **Success Criterion Outcome**:
   - QAOA demonstrated conditional capability by proposing improving candidates in 33.3%–40.0% of instances over the initial seed, but **did not achieve statistically significant superiority over the strongest classical competitor (Kernighan-Lin)**.

