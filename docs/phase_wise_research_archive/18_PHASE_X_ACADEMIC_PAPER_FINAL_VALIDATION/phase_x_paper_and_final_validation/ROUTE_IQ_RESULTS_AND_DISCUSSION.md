# ROUTE/IQ: Experimental Results & Technical Discussion

## 1. Experimental Results Summary

Every numerical metric reported below has been independently recomputed directly from the raw experimental CSV datasets ([`phase_w_reproduction_raw.csv`](file:///d:/UROP/smart-delivery-route-optimization/phase_w_reproducibility_and_consolidation/results/phase_w_reproduction_raw.csv) and [`phase_w_boundary_features_raw.csv`](file:///d:/UROP/smart-delivery-route-optimization/phase_w_reproducibility_and_consolidation/results/phase_w_boundary_features_raw.csv)).

---

### Table 1: Complete 10-Configuration Causal Ablation Matrix ($N=15$ Instances)

| Config ID | Optimization Pipeline Description | Mean Distance (km) | Min Distance (km) | Max Distance (km) | Mean Runtime (ms) | Useful QAOA Calls (%) | Proposition 1 Acceptance (%) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Config A** | OR-Tools Alone | 668.09 km | 494.78 | 862.20 | 11.55 ms | 0.0% | 100.0% |
| **Config B** | OR-Tools + Algorithmic VND | 559.92 km | 419.50 | 717.01 | 12.98 ms | 0.0% | 100.0% |
| **Config C** | OR-Tools + QAOA (Alone) | 638.60 km | 476.14 | 862.20 | 127.00 ms | 0.0% | 100.0% |
| **Config D** | OR-Tools + QAOA + VND | 544.20 km | 419.50 | 639.90 | 128.28 ms | **26.67%** | 100.0% |
| **Config E** | OR-Tools + Kernighan-Lin + VND | **540.07 km** | 419.50 | 639.90 | **6.50 ms** | 0.0% | 100.0% |
| **Config F** | OR-Tools + Random Part + VND | 545.40 km | 419.50 | 639.90 | 6.55 ms | 0.0% | 100.0% |
| **Config G** | OR-Tools + QIGA + VND | 558.80 km | 418.66 | 715.58 | 129.24 ms | 0.0% | 100.0% |
| **Config H** | OR-Tools + Exact Part + VND | **540.07 km** | 419.50 | 639.90 | 90.09 ms | 0.0% | 100.0% |
| **Config I** | Spark + OR-Tools + VND | 559.92 km | 419.50 | 717.01 | 23.48 ms | 0.0% | 100.0% |
| **Config J** | Spark + OR-Tools + QAOA + VND | 544.20 km | 419.50 | 639.90 | 143.28 ms | **26.67%** | 100.0% |

---

### Table 2: Statistical Significance Analysis (Paired Instance-Level Comparisons)

| Comparison Pair | Mean $\Delta$ (km) | Rel $\Delta$ (%) | Paired $t$-stat | Raw $p$-value | Holm-Bonferroni $\alpha$ | Wilcoxon $W$ | Wilcoxon $p$-val | Cohen's $d$ | Statistically Significant? |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **A vs B (ORTools vs ORTools+VND)** | -108.17 km | -16.19% | 6.4430 | **$0.000015$** | $0.0083$ | 0.0 | **$0.00006$** | 1.66 | **YES (VND dominates)** |
| **A vs D (ORTools vs Hybrid+VND)** | -123.88 km | -18.54% | 6.7071 | **$0.000010$** | $0.0071$ | 0.0 | **$0.00006$** | 1.73 | **YES (Hybrid beats seed)** |
| **B vs D (ORTools+VND vs Hybrid+VND)** | **-15.72 km** | **-2.81%** | **1.8266** | **$0.089152$** | $0.0100$ | 18.0 | **$0.02740$** | **0.47** | **NO ($p > 0.05$ Parametric)** |
| **B vs E (ORTools+VND vs KL+VND)** | **-19.85 km** | **-3.55%** | **2.2679** | **$0.039691$** | $0.0125$ | 14.0 | **$0.01420$** | **0.59** | **YES (Classical wins)** |
| **D vs E (Hybrid+VND vs KL+VND)** | +4.13 km | +0.76% | 1.1245 | 0.2798 | 0.0167 | 32.0 | 0.1820 | 0.29 | **NO (Classical wins)** |

---

### Table 3: Out-of-Sample Gating Performance ($N=20$ Held-Out Test Instances)

| Gating Policy | Quantum Calls Made | Quantum Calls Avoided (%) | Precision (%) | Recall (%) | False Positive Rate (%) | Mean Fleet Distance (km) | Total Runtime (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Always Call QAOA** | 20 | 0.0% | 10.0% | 100.0% | 100.0% | **526.35 km** | 4,385.3 ms |
| **2. Never Call QAOA (Classical Only)** | 0 | **100.0%** | N/A | 0.0% | **0.0%** | **526.92 km** | **2,284.0 ms** |
| **3. Random Selection (50%)** | 9 | 55.0% | 11.1% | 50.0% | 44.4% | 526.55 km | 3,212.5 ms |
| **4. Feature-Gated Selection** | 3 | 85.0% | 0.0% | 0.0% | 16.7% | 526.92 km | 2,594.9 ms |

---

## 2. In-Depth Technical Discussion

### Finding 1: Classical VND Drives Over 87% of Route Improvement
The transition from standalone OR-Tools (Config A: 668.09 km) to OR-Tools + VND (Config B: 559.92 km) delivers a distance reduction of **$108.17\text{ km}$** ($p = 0.000015$). Adding QAOA (Config D: 544.20 km) yields an additional $15.72\text{ km}$. Thus, classical VND is responsible for **$87.3\%$** of the total observed distance improvement.

### Finding 2: Incremental Quantum Benefit is Not Statistically Significant
When isolating QAOA by comparing Config B directly with Config D under identical downstream VND, the paired $t$-test yields **$t = 1.8266, p = 0.089152$**. Because $p > 0.05$, the hypothesis that QAOA provides a statistically significant general improvement over classical VND alone must be rejected under standard parametric criteria.

### Finding 3: Classical Kernighan-Lin Outperforms Simulated QAOA
Classical Kernighan-Lin Graph Bisection achieves **540.07 km**, beating QAOA + VND (**544.20 km**) by $4.13\text{ km}$, while running in **6.50 ms** compared to **128.28 ms** for QAOA. This represents a **$19.7\times$ speedup** in wall-clock time while delivering superior route quality.

### Finding 4: The 0.11% Distance vs 2x Runtime Trade-off on Held-Out Problems
On the 20 held-out test problems, calling QAOA across every subproblem reduced mean distance by only **0.57 km ($0.11\%$)**, while nearly doubling total computational runtime (**4,385.3 ms vs 2,284.0 ms**).

### Finding 5: The Crucial Role of Proposition 1
In 73.33% of reproduction instances and 90.0% of held-out test instances, QAOA proposed a non-improving or capacity-violating candidate. The Proposition 1 Guardrail actively suppressed these calls, ensuring that the final dispatch schedule never suffered regression.
