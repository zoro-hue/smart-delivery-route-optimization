# Deliverable 7: Phase U Capacity and Feasibility Audit

## 1. Mathematical Feasibility Conditions

For a two-vehicle customer bipartition $\mathbf{x} \in \{0, 1\}^N$, physical validity requires four simultaneous conditions:

1. **Domain Validity**: $x_i \in \{0, 1\} \quad \forall i \in \{1, \dots, N\}$.
2. **Vehicle A Capacity**: $\sum_{i=1}^N q_i x_i \le C_A$.
3. **Vehicle B Capacity**: $\sum_{i=1}^N q_i (1 - x_i) \le C_B$.
4. **Non-Triviality (Both Vehicles Utilized)**: $0 < \sum_{i=1}^N x_i < N$.

---

## 2. Empirical Verification Across 15 Instances

Using the 150 benchmark executions from `phase_u_ablation_raw.csv`:

| Partitioning Method | Evaluated States | Raw Feasible (%) | Repaired Feasible (%) | Mean Load Imbalance $|\sum q_A - \sum q_B|$ |
| :--- | :---: | :---: | :---: | :---: |
| **Exact Enumeration** | 61,440 | 100.0% | N/A (Directly constrained) | 1.8 kg |
| **Kernighan-Lin** | 15 instances | 100.0% | N/A (Feasible swap) | 2.1 kg |
| **Angular Sweep** | 15 instances | 100.0% | 100.0% | 2.4 kg |
| **Raw QAOA (Unconstrained)** | 15,360 shots | **0.0% (Worst-case)** / **44.9% (Average)** | N/A | 7.9 kg (Significant overflow) |
| **QAOA + Classical Repair** | 15,360 shots | N/A | **100.0%** | 2.3 kg |

---

## 3. The Capacity Feasibility Gap

- In unconstrained quantum sampling, the standard transverse-field mixer $H_M = \sum X_i$ allows transitions between any of the $2^N$ Hilbert space states regardless of Hamming weight or total demand.
- Therefore, QAOA must be paired with either **domain-wall/XY mixers** that conserve total Hamming weight or **classical deterministic capacity repair** during post-processing.
- In ROUTE/IQ, the **Dual-Pillar architecture** solves this by assigning capacity repair and Proposition 1 certification to the classical engine, ensuring that zero capacity-violating routes ever reach the final dispatch plan or UI dashboard.
