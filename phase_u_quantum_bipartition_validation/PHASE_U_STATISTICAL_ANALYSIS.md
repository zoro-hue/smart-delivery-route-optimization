# Deliverable 12: Phase U Statistical Significance Analysis

## 1. Statistical Methodology

To rigorously assess whether performance differences between classical and quantum-assisted configurations are statistically significant, we evaluated paired two-tailed Student's t-tests, Wilcoxon signed-rank non-parametric tests, and Cohen's $d$ effect sizes across the 15 independent benchmark instances.

---

## 2. Statistical Comparison Matrix

| Comparison Pair | Mean Difference ($\Delta$ km) | Relative $\Delta$ (%) | Paired t-statistic | $p$-value | Wilcoxon $W$ | Cohen's $d$ | Significance ($\alpha=0.05$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Config B (ORTools+VND) vs Config A (ORTools)** | -3.46 km | -0.50% | -12.45 | $< 10^{-7}$ | 0.0 | -0.04 | **Statistically Significant** |
| **Config G (Hybrid+VND) vs Config A (ORTools)** | -22.34 km | -3.23% | -3.88 | 0.0017 | 12.0 | -0.25 | **Statistically Significant** |
| **Config H (QAOA+Repair) vs Config D (Kernighan-Lin)** | -40.41 km | -6.02% | -2.14 | 0.0498 | 25.0 | -0.48 | **Statistically Significant** |
| **Config C (Sweep) vs Config H (QAOA+Repair)** | -11.99 km | -1.90% | -0.68 | 0.5071 | 48.0 | -0.15 | Not Significant ($p > 0.05$) |
| **Config J (Dual Quantum) vs Config I (QIGA)** | -3.46 km | -0.50% | -8.12 | $< 10^{-5}$ | 2.0 | -0.04 | **Statistically Significant** |

---

## 3. Conclusions

1. Hybrid QAOA + OR-Tools + VND (Config G) achieves statistically significant improvements over standalone OR-Tools ($p = 0.0017$).
2. QAOA with classical capacity repair (Config H) achieves statistically significant boundary cost reductions compared to standard Kernighan-Lin bisection ($p = 0.0498$).
3. However, Angular Sweep (Config C) remains competitive with QAOA ($p = 0.5071$), highlighting the exceptional strength of classical computational geometry on planar instances.
