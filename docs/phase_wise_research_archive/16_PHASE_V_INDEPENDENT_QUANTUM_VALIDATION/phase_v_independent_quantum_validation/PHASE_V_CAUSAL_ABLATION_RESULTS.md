# Deliverable 3: Phase V Critical Causal Ablation Results

## 1. Executive Summary & Core Experimental Matrix

To definitively determine whether QAOA itself causes route improvements, Phase V executed a controlled 10-configuration causal ablation study ($N=150$ total evaluations across 15 benchmark instances) using **real algorithmic Variable Neighborhood Descent (VND)** (2-opt, relocate, and swap) without synthetic percentage approximations.

| Config ID | Description | Mean Distance (km) | Min Distance (km) | Max Distance (km) | Mean Runtime (ms) | QAOA Useful Call Rate | Prop 1 Acceptance |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Config A** | OR-Tools Alone | 668.09 km | 494.78 | 862.20 | 8.21 ms | 0.0% | 100.0% |
| **Config B** | OR-Tools + Algorithmic VND | 559.92 km | 419.50 | 717.01 | 12.71 ms | 0.0% | 100.0% |
| **Config C** | OR-Tools + QAOA (Alone) | 638.60 km | 476.14 | 862.20 | 129.09 ms | 0.0% | 100.0% |
| **Config D** | OR-Tools + QAOA + VND | 544.20 km | 419.50 | 639.90 | 133.59 ms | 26.7% | 100.0% |
| **Config E** | OR-Tools + Classical Part (KL) + VND | **540.07 km** | 419.50 | 639.90 | **5.65 ms** | 0.0% | 100.0% |
| **Config F** | OR-Tools + Random Feasible Part + VND | 545.40 km | 419.50 | 639.90 | 5.20 ms | 0.0% | 100.0% |
| **Config G** | OR-Tools + QIGA + VND | 558.80 km | 418.66 | 715.58 | 125.00 ms | 0.0% | 100.0% |
| **Config H** | OR-Tools + Exact Part + VND | **540.07 km** | 419.50 | 639.90 | 81.83 ms | 0.0% | 100.0% |
| **Config I** | Spark + OR-Tools + VND | 559.92 km | 419.50 | 717.01 | 23.21 ms | 0.0% | 100.0% |
| **Config J** | Spark + OR-Tools + QAOA + VND | 544.20 km | 419.50 | 639.90 | 148.59 ms | 26.7% | 100.0% |

---

## 2. Essential Scientific Comparisons

### Comparison 1: Classical VND vs Standalone OR-Tools (Config B vs Config A)
- Distance reduction: $\Delta = -108.17\text{ km}$ ($-16.19\%$).
- Paired Student's $t$-test: $t = 6.4430, p = 0.000015$ (Extremely statistically significant).
- **Finding**: Downstream algorithmic VND accounts for **87.3%** of the total distance reduction observed in the hybrid pipeline.

### Comparison 2: Incremental Contribution of QAOA (Config D vs Config B)
- Distance reduction: $\Delta = -15.72\text{ km}$ ($-2.81\%$).
- Paired Student's $t$-test: $t = 1.8266, p = 0.089152$.
- **Finding**: At standard significance threshold $\alpha = 0.05$, **the incremental contribution of QAOA beyond classical VND is NOT statistically significant** ($p = 0.0892 > 0.05$).

### Comparison 3: QAOA vs Strong Classical Partitioning (Config D vs Config E & H)
- Distance: Classical Kernighan-Lin + VND achieved **540.07 km**, beating QAOA + VND (**544.20 km**) by $4.13\text{ km}$.
- Runtime: Classical Kernighan-Lin took **5.65 ms**, which is **$23.6\times$ faster** than simulated QAOA (**133.59 ms**).
- **Finding**: Strong classical partitioning heuristics outperform simulated QAOA both in solution quality and computational efficiency.

### Comparison 4: QAOA vs Random Feasible Partitioning (Config D vs Config F)
- Distance: Random Feasible + VND achieved **545.40 km**.
- QAOA + VND achieved **544.20 km** ($\Delta = -1.20\text{ km}$, a difference of only $0.22\%$).
- **Finding**: When followed by real VND, even randomly generated partitions that are repaired for capacity achieve near-identical fleet distances to QAOA.
