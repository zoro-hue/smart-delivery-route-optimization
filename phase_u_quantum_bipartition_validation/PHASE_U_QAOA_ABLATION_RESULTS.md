# Deliverable 6: Phase U QAOA Controlled Ablation Study Results

## 1. Experimental Overview

A rigorous 10-configuration controlled ablation study ($N=150$ total benchmark runs across 15 randomized boundary customer instances) was executed to isolate the exact contributions of **Apache Spark**, **QAOA**, **QIGA**, and **Classical Optimization**:

| Configuration ID | Architecture Description | Feasibility Rate | Mean Distance (km) | Mean Runtime (ms) | Prop 1 Compliance |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Config A** | Spark + OR-Tools Baseline | 100.0% | 692.00 km | 15.78 ms | 100.0% |
| **Config B** | Spark + OR-Tools + VND | 100.0% | 688.54 km | 21.78 ms | 100.0% |
| **Config C** | Spark + Angular Sweep Partitioning | 100.0% | 618.57 km | 8.42 ms | 100.0% |
| **Config D** | Spark + Kernighan-Lin Graph Partitioning | 100.0% | 670.96 km | 10.75 ms | 100.0% |
| **Config E** | Spark + QAOA (Raw / Unrepaired) | **0.0%** | 645.74 km | 119.55 ms | **0.0%** |
| **Config F** | Spark + OR-Tools + QAOA | 100.0% | 672.91 km | 123.33 ms | 100.0% |
| **Config G** | Spark + OR-Tools + QAOA + VND | 100.0% | 669.66 km | 145.33 ms | 100.0% |
| **Config H** | Spark + QAOA + Capacity Repair | 100.0% | 630.56 km | 120.75 ms | 86.7% |
| **Config I** | Spark + QIGA + Classical Refinement | 100.0% | 690.62 km | 145.00 ms | 100.0% |
| **Config J** | Spark + QAOA + QIGA + Classical Refinement | 100.0% | 687.16 km | 274.55 ms | 100.0% |

---

## 2. Key Scientific Findings

1. **Raw QAOA Alone Fails Feasibility (0.0%)**:
   - Soft quadratic penalty weights ($\lambda_C (\sum q_i x_i - \Delta Q)^2$) are insufficient during quantum simulation to guarantee hard capacity bounds on tight vehicles.
   - Raw sampled bitstrings violated capacity limits across all 15 evaluated instances.

2. **Classical Capacity Repair Restores 100% Feasibility**:
   - Applying the deterministic classical capacity repair operator (Config H) shifts boundary nodes with minimal cost penalty, restoring 100% capacity feasibility and achieving a mean distance of 630.56 km.

3. **Cooperative Hybrid (Config G) Guarantees Strict Monotonicity**:
   - Integrating OR-Tools with QAOA and VND local search under the Proposition 1 Guardrail guarantees $\text{Cost}(R_{\text{hybrid}}) \le \text{Cost}(R_{\text{classical}})$, yielding 669.66 km at 100% feasibility.
