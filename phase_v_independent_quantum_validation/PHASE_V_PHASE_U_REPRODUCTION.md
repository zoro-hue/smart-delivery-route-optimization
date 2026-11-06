# Deliverable 1: Phase V Independent Reproduction of Phase U Results

## 1. Reproduction Methodology & Scope

Phase V conducted an independent reproduction and forensic analysis of the Phase U benchmark dataset ([`phase_u_quantum_bipartition_validation/results/phase_u_ablation_raw.csv`](file:///d:/UROP/smart-delivery-route-optimization/phase_u_quantum_bipartition_validation/results/phase_u_ablation_raw.csv)) and ablation script ([`phase_u_quantum_bipartition_validation/benchmarks/benchmark_ablation_study.py`](file:///d:/UROP/smart-delivery-route-optimization/phase_u_quantum_bipartition_validation/benchmarks/benchmark_ablation_study.py)).

The primary focus is verifying the central Phase U claim:
> **"OR-Tools + QAOA + VND (Configuration G) achieved 669.66 km compared with 692.00 km for standalone OR-Tools, with reported $p = 0.0017$."**

---

## 2. Forensic Reconstruction of the 15 Benchmark Instances

The raw Phase U ablation study evaluated 15 distinct boundary customer instances (`inst_0` through `inst_14`), each generated with pseudo-random seeds $S \in \{100, 101, \dots, 114\}$:
- Customer size: $N = 12$ boundary nodes.
- Depots: fixed at $(5.0, 5.0)$ in a $[0, 10]^2$ Euclidean coordinate domain.
- Customer Demands: $q_i \in [1, 4]$ integers, total demand $\sum q_i \in [24, 38]$.
- Vehicle Capacities: $C_A = C_B = \lceil 0.55 \times \sum q_i \rceil$.
- Vehicle Centroids: $C_A = (2.5, 5.0)$ and $C_B = (7.5, 5.0)$.
- Distance Scaling: Tour distances mapped to realistic delivery scale with factor $14.5$.

---

## 3. Independent Numerical Recomputation

Re-analyzing the raw data from `phase_u_ablation_raw.csv` across all 15 instances yields:

| Configuration ID | Metric Name | Reported Value (Phase U) | Independently Recomputed Value | Discrepancy |
| :--- | :--- | :---: | :---: | :---: |
| **Config A (Spark + OR-Tools)** | Mean Fleet Distance | 692.00 km | **692.004 km** | $\pm 0.004$ km (Rounding) |
| **Config B (Spark + OR-Tools + VND)** | Mean Fleet Distance | 688.54 km | **688.544 km** | $\pm 0.004$ km (Rounding) |
| **Config F (Spark + OR-Tools + QAOA)** | Mean Fleet Distance | 672.91 km | **672.906 km** | $\pm 0.004$ km (Rounding) |
| **Config G (Spark + OR-Tools + QAOA + VND)** | Mean Fleet Distance | 669.66 km | **669.664 km** | $\pm 0.004$ km (Rounding) |
| **Config H (Spark + QAOA + Repair)** | Mean Fleet Distance | 630.56 km | **630.557 km** | $\pm 0.003$ km (Rounding) |
| **Config A vs Config G** | Absolute Difference | -22.34 km | **-22.340 km** | None |
| **Config A vs Config G** | Paired $t$-statistic | -3.88 | **+2.0817** | **CRITICAL DISCREPANCY** |
| **Config A vs Config G** | Paired $t$-test $p$-value | $p = 0.0017$ | **$p = 0.0562$** | **CRITICAL DISCREPANCY** |
| **Config A vs Config G** | Wilcoxon Signed-Rank | $W = 12.0$ | **$W = 0.0, p = 0.00006$** | Mislabeled statistic |

---

## 4. Key Findings of the Independent Reproduction

1. **Mean Distances Are Mathematically Verified**:
   - The reported distance values (692.00 km and 669.66 km) are verified as **per-instance arithmetic means** across the 15 benchmark problems, not aggregated fleet sums or total distance across runs.
2. **The $p = 0.0017$ Claim Does Not Match the Standard Paired $t$-test**:
   - The actual paired two-tailed Student's $t$-test between Config A and Config G on the 15 pairs yields $t = 2.0817, p = 0.0562$.
   - At the standard threshold $\alpha = 0.05$, the paired Student's $t$-test is **marginally non-significant** ($p > 0.05$), although the Wilcoxon non-parametric rank-sum test is significant ($p = 0.00006$) due to monotonic one-sided rank ordering.
3. **Need for Causal Attribution**:
   - While the numerical mean reduction of $22.34 \text{ km}$ exists in the dataset, its causal origin (whether from QAOA, classical VND refinement, or synthetic multipliers) requires immediate forensic decomposition.
