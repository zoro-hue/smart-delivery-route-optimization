# Deliverable 10: Phase V Statistical Significance Analysis

## 1. Statistical Methodology & Protocol

In accordance with strict scientific testing standards:
- **Unit of Statistical Analysis**: The paired independent benchmark instance ($N = 15$ pairs).
- **Hypothesis Testing**: Paired two-tailed Student's $t$-test (parametric) and Wilcoxon signed-rank test (non-parametric).
- **Effect Size Metric**: Cohen's $d$ for paired samples:
  $$d = \frac{\bar{x}_1 - \bar{x}_2}{s_D}$$
- **Family-Wise Error Rate Correction**: Holm-Bonferroni step-down procedure applied across all pairwise comparisons.

---

## 2. Comprehensive Pairwise Statistical Matrix

| Comparison Pair | Mean $\Delta$ (km) | Rel $\Delta$ (%) | Paired $t$-stat | Raw $p$-value | Holm-Bonferroni Critical $\alpha$ | Wilcoxon $W$ | Wilcoxon $p$-val | Cohen's $d$ | Statistically Significant? |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **A vs B (ORTools vs ORTools+VND)** | -108.17 km | -16.19% | 6.4430 | **$0.000015$** | $0.0083$ | 0.0 | **$0.00006$** | 1.66 | **YES (Definitive)** |
| **A vs D (ORTools vs Hybrid+VND)** | -123.88 km | -18.54% | 6.7071 | **$0.000010$** | $0.0071$ | 0.0 | **$0.00006$** | 1.73 | **YES (Definitive)** |
| **B vs D (ORTools+VND vs Hybrid+VND)** | **-15.72 km** | **-2.81%** | **1.8266** | **$0.089152$** | $0.0100$ | 18.0 | **$0.02740$** | **0.47** | **NO ($p > 0.05$ Parametric)** |
| **D vs E (Hybrid+VND vs KL+VND)** | +4.13 km | +0.76% | 1.1245 | 0.2798 | 0.0125 | 32.0 | 0.1820 | 0.29 | **NO (Classical wins)** |
| **D vs F (Hybrid+VND vs Random+VND)** | -1.20 km | -0.22% | 0.4210 | 0.6802 | 0.0500 | 45.0 | 0.5420 | 0.11 | **NO (Indistinguishable)** |
| **D vs H (Hybrid+VND vs Exact+VND)** | +4.13 km | +0.76% | 1.1245 | 0.2798 | 0.0167 | 32.0 | 0.1820 | 0.29 | **NO (Exact wins)** |

---

## 3. Critical Statistical Insights

1. **Downstream VND Accounts for the Bulk of the Effect**:
   - The contrast between A (OR-Tools alone) and B (OR-Tools + VND) has $p = 0.000015$ and an enormous effect size ($d = 1.66$).
2. **QAOA's Incremental Contribution is Statistically Inconclusive**:
   - When isolating QAOA's contribution by comparing B (OR-Tools + VND) directly against D (OR-Tools + QAOA + VND), the paired $t$-test yields $p = 0.0892$, which **fails to reach statistical significance** at the standard threshold $\alpha = 0.05$.
3. **No Advantage Over Classical Kernighan-Lin or Exact Methods**:
   - Comparing QAOA against classical Kernighan-Lin or Exact Enumeration shows no quantum advantage ($p = 0.280$); in fact, classical partitioning yields slightly better mean distances.
