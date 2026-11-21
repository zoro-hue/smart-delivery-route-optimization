# Phase S Deliverable 11: Rigorous Statistical Analysis & Hypothesis Testing

**Document:** `phase_s_asymmetric_quantum_neighborhoods/PHASE_S_STATISTICAL_ANALYSIS.md`  
**Date:** 2026-11-06  
**Status:** Completed & Rigorously Verified  
**Branch:** `research/phase-s-asymmetric-quantum-neighborhoods`

---

## 1. Formal Hypotheses

We conduct formal statistical hypothesis testing on the performance of QAOA versus Classical Directed Search across the 20 asymmetric instances ($N=20$, $\alpha \in [0.24, 0.56]$):

### Hypothesis Test 1 (QAOA vs Directed 2-opt):
- **$H_0^{(1)}$:** There is no difference in solution quality between QAOA and Directed 2-opt ($\mu_{\text{diff}} = 0$).
- **$H_1^{(1)}$:** QAOA produces lower route distance than Directed 2-opt ($\mu_{\text{diff}} < 0$).

### Hypothesis Test 2 (Classical VND vs QAOA):
- **$H_0^{(2)}$:** There is no difference in solution quality between Classical VND and QAOA.
- **$H_1^{(2)}$:** Classical VND produces statistically significantly lower route distance than QAOA ($\mu_{\text{VND}} < \mu_{\text{QAOA}}$).

Significance threshold: $\alpha = 0.05$.

---

## 2. Statistical Test Results

| Test Pair | Mean Paired Difference ($\bar{D}$) | Wilcoxon Signed-Rank Statistic ($W$) | $p$-value | Statistical Significance |
| :--- | :---: | :---: | :---: | :---: |
| **QAOA vs Directed 2-opt** | $-2.835\text{ km}$ | 11.0 | $p = 0.327$ | Not Significant ($p > 0.05$) |
| **Classical VND vs QAOA** | **$-10.419\text{ km}$** | **0.0** | **$p = 0.0038$** | **Statistically Significant ($p < 0.01$)** |

---

## 3. Vargha-Delaney Effect Size ($\hat{A}_{12}$)

The non-parametric Vargha-Delaney effect size measure $\hat{A}_{12}$ evaluates the probability that algorithm 1 yields a better solution than algorithm 2:
- $\hat{A}_{12} = 0.50$: Exactly equal performance.
- $\hat{A}_{12} > 0.50$: Algorithm 1 is superior.

Comparing Classical VND to QAOA:
$$\hat{A}_{\text{VND, QAOA}} = \frac{R_{\text{VND}} - \frac{n(n+1)}{2}}{n^2} = \mathbf{0.725}$$
This indicates a **large, statistically significant effect size** favoring Classical Variable Neighborhood Descent over QAOA.

---

## 4. Scientific Verdict

1. **Failure to reject $H_0^{(1)}$:** QAOA does not achieve a statistically significant overall advantage over Directed 2-opt ($p = 0.327$). While QAOA beats 2-opt on 4 asymmetric trapped seeds, 2-opt beats QAOA on 4 other seeds due to quantum sampling noise.
2. **Rejection of $H_0^{(2)}$ ($p = 0.0038 < 0.01$):** Classical VND is statistically significantly superior to QAOA, achieving an average cost reduction of $10.42\text{ km}$ with $p < 0.005$ and a large effect size ($\hat{A}_{12} = 0.725$).

