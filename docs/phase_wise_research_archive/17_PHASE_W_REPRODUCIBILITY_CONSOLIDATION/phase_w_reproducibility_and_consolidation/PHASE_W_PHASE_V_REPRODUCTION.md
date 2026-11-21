# Deliverable 2: Phase W Independent Reproduction of Phase V Causal Ablation

## 1. Reproduction Methodology & Benchmark Protocol

Phase W independently re-implemented and re-executed the complete causal ablation suite across all 10 configurations (A through J) using the exact random seeds ($S \in \{100, \dots, 114\}$), coordinates, customer demands, and directed asymmetric cost matrices as Phase V.

Timing telemetry was comprehensively decoupled into 5 distinct pipeline stages:
1. $t_{\text{prep}}$: Preprocessing, coordinate transformation, and distance matrix construction.
2. $t_{\text{part}}$: Partitioning algorithm execution (MLS, KL, Exact, or Random).
3. $t_{\text{qaoa}}$: Quantum variational circuit compilation, parameter optimization, and measurement sampling.
4. $t_{\text{repair}}$: Deterministic classical capacity repair.
5. $t_{\text{vnd}}$: Algorithmic Variable Neighborhood Descent (2-opt, relocate, and swap).

---

## 2. Independent Numerical Recomputation Matrix

Recomputed across all 15 instances ($N=150$ total evaluations) in [`phase_w_reproduction_raw.csv`](file:///d:/UROP/smart-delivery-route-optimization/phase_w_reproducibility_and_consolidation/results/phase_w_reproduction_raw.csv):

| Configuration ID | Pipeline Description | Phase V Reported Distance | Phase W Recomputed Distance | Recomputed Total Runtime | Useful QAOA Calls | Prop 1 Acceptance |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Config A** | OR-Tools Alone | 668.09 km | **668.087 km** | 11.55 ms | 0.0% | 100.0% |
| **Config B** | OR-Tools + Algorithmic VND | 559.92 km | **559.921 km** | 12.98 ms | 0.0% | 100.0% |
| **Config C** | OR-Tools + QAOA | 638.60 km | **638.601 km** | 127.00 ms | 0.0% | 100.0% |
| **Config D** | OR-Tools + QAOA + VND | 544.20 km | **544.202 km** | 128.28 ms | **26.67%** | 100.0% |
| **Config E** | OR-Tools + Kernighan-Lin + VND | **540.07 km** | **540.071 km** | **6.50 ms** | 0.0% | 100.0% |
| **Config F** | OR-Tools + Random Part + VND | 545.40 km | **545.402 km** | 6.55 ms | 0.0% | 100.0% |
| **Config G** | OR-Tools + QIGA + VND | 558.80 km | **558.801 km** | 129.24 ms | 0.0% | 100.0% |
| **Config H** | OR-Tools + Exact Part + VND | **540.07 km** | **540.071 km** | 90.09 ms | 0.0% | 100.0% |
| **Config I** | Spark + OR-Tools + VND | 559.92 km | **559.921 km** | 23.48 ms | 0.0% | 100.0% |
| **Config J** | Spark + OR-Tools + QAOA + VND | 544.20 km | **544.202 km** | 143.28 ms | **26.67%** | 100.0% |

---

## 3. Statistical Verification of Phase V Claims

1. **Re-Verification of B vs D (QAOA Incremental Contribution)**:
   - Distance difference: $\Delta = -15.719\text{ km}$ ($-2.81\%$).
   - Paired Student's $t$-test: **$t = 1.826619, p = 0.089152$**.
   - **Verdict**: Exact mathematical reproduction. Confirms that QAOA's contribution beyond classical VND **fails to reach statistical significance** at $\alpha = 0.05$.
2. **Re-Verification of B vs E (Classical Kernighan-Lin vs Baseline)**:
   - Distance difference: $\Delta = -19.849\text{ km}$ ($-3.55\%$).
   - Paired Student's $t$-test: **$t = 2.267890, p = 0.039691$** ($p < 0.05$).
   - **Verdict**: Statistically significant. Classical Kernighan-Lin provides a larger and more statistically reliable improvement than QAOA, at **$19.7\times$ lower computational runtime** ($6.50\text{ ms}$ vs $128.28\text{ ms}$).
3. **Re-Verification of Useful Call Rate**:
   - Useful call rate: **26.67%** (4 out of 15 instances).
   - In 73.33% of instances, QAOA produced no route improvement.
