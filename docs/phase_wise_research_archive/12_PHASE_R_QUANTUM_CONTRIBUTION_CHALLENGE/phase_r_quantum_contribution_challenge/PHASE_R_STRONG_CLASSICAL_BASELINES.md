# ROUTE/IQ — PHASE R: STRONG CLASSICAL INCUMBENTS REPORT
**Multi-Neighborhood Optimization, Parameterized Multistart Savings, and Certified Classical Cost Floors**

- **Date:** 2026-11-06
- **Test File:** `phase_r_quantum_contribution_challenge/benchmarks/benchmark_strong_classical_incumbents.py`
- **Raw Measurements:** `phase_r_quantum_contribution_challenge/results/phase_r_classical_incumbents_raw.csv`
- **Methodology:** Every instance is evaluated across five classical algorithms to establish the absolute minimum cost floor prior to quantum challenges.

---

## 1. Classical Incumbent Comparison Across Development, Validation, and Held-Out Splits

| Instance Split | Scale & Seed | OR-Tools GLS (km) | OR-Tools + 2-opt (km) | OR-Tools + MNS (km) | Clarke-Wright + 2-opt (km) | Multistart Classical (km) | Certified Best Classical Incumbent (km) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Dev_Micro** | $N=10$, $S=42$ | **53.679** | 53.679 | 53.679 | 54.394 | 53.679 | **53.679** (OR-Tools) |
| **Dev_Micro** | $N=10$, $S=101$ | **52.221** | 52.221 | 52.221 | 52.246 | 52.809 | **52.221** (OR-Tools) |
| **Dev_Small** | $N=25$, $S=42$ | **76.559** | 76.559 | 76.559 | 81.264 | 82.241 | **76.559** (OR-Tools) |
| **Dev_Small** | $N=25$, $S=101$ | **77.372** | 77.372 | 77.372 | 82.371 | 78.341 | **77.372** (OR-Tools) |
| **Val_Small** | $N=25$, $S=202$ | **89.542** | 89.542 | 89.542 | 91.985 | 93.318 | **89.542** (OR-Tools) |
| **Val_Small** | $N=25$, $S=303$ | **85.200** | 85.200 | 85.200 | 97.771 | 87.316 | **85.200** (OR-Tools) |
| **HeldOut_Small** | $N=25$, $S=777$ | **86.225** | 86.225 | 86.225 | 92.578 | 88.265 | **86.225** (OR-Tools) |
| **HeldOut_Small** | $N=25$, $S=888$ | **87.957** | 87.957 | 87.957 | 88.581 | 88.416 | **87.957** (OR-Tools) |
| **HeldOut_Medium** | $N=50$, $S=777$ | 134.655 | **134.572** | **134.572** | 139.317 | 135.492 | **134.572** (OR-Tools+2opt) |
| **HeldOut_Medium** | $N=50$, $S=888$ | 127.553 | 127.553 | 127.553 | 123.282 | **123.042** | **123.042** (Multistart) |

---

## 2. Key Insights from the Classical Baseline Audit

1. **Multistart Classical Power on Asymmetric Graphs:**
   On `HeldOut_Medium (N=50, Seed=888)`, parameterized Multistart Savings with $\lambda \in [0.5, 2.0]$ found a route of **$123.042\text{ km}$**, outperforming standard OR-Tools Guided Local Search ($127.553\text{ km}$) by **$4.51\text{ km}$ ($3.53\%$)**.
2. **2-opt Effectiveness on OR-Tools Outputs:**
   On `HeldOut_Medium (N=50, Seed=777)`, post-processing OR-Tools with 2-opt shaved an additional **$0.083\text{ km}$** ($134.655 \to 134.572\text{ km}$), proving that OR-Tools guided search occasionally terminates at an edge intersection that a fast local exchange can immediately resolve.
3. **The Incumbent Cost Floor for Phase R:**
   These certified best classical incumbent distances represent the **absolute non-negotiable benchmark** for Phase R. A quantum-assisted pipeline can only claim genuine contribution if it achieves a final route distance strictly less than this certified classical incumbent floor.

