# PHASE AB DELIVERABLE 10: RIGOROUS STATISTICAL ANALYSIS

## Project: ROUTE/IQ — Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing
**Institution:** SRM University-AP | **Supervisor:** Dr. Vishnu Prasad Verma

---

## 1. Statistical Methodology

To provide rigorous, defensible validation of the differences observed across the 8 configurations, we performed:
1. **Paired Two-Tailed Student's t-Tests:** Testing null hypothesis $H_0: \mu_{\text{diff}} = 0$.
2. **Wilcoxon Signed-Rank Tests:** Non-parametric evaluation verifying robustness against non-normal variance.
3. **Cohen's $d$ Effect Size:** Quantifying standardized mean differences ($d < 0.2$ negligible, $0.2 \le d < 0.5$ small, $0.5 \le d < 0.8$ medium, $d \ge 0.8$ large).
4. **95% Confidence Intervals:** Computed via bootstrapping with $B = 10,000$ resamples.

---

## 2. Hypothesis Testing Matrix (vs Baseline Config B: OR-Tools + VND)

| Comparison Pair | Mean Difference ($\Delta$ km) | Paired t-statistic | Paired $p$-value | Wilcoxon $W$ | Wilcoxon $p$-value | Cohen's $d$ | Statistical Significance ($\alpha = 0.05$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Config C (KL) vs Config B** | -17.73 km | -3.68 | 0.0010 | 48.0 | 0.0015 | 0.48 | **Statistically Significant** |
| **Config D (Tabu) vs Config B** | -26.00 km | -4.52 | 0.0001 | 32.0 | 0.0002 | 0.71 | **Statistically Significant** |
| **Config E (Random) vs Config B** | -18.55 km | -3.21 | 0.0032 | 55.0 | 0.0041 | 0.50 | **Statistically Significant** |
| **Config F (QAOA) vs Config B** | -15.09 km | -2.48 | 0.0192 | 68.0 | 0.0224 | 0.41 | **Statistically Significant** |
| **Config G (Adaptive) vs Config B** | -24.01 km | -4.81 | 0.00003 | 25.0 | 0.00008 | 0.68 | **Statistically Significant** |
| **Config H (Spark) vs Config B** | -21.77 km | -4.15 | 0.0003 | 36.0 | 0.0004 | 0.60 | **Statistically Significant** |

---

## 3. Direct Head-to-Head: QAOA vs Classical Metaheuristics

| Head-to-Head Pair | Mean Difference ($\Delta$ km) | Paired $p$-value | Cohen's $d$ | Conclusion |
| :--- | :---: | :---: | :---: | :--- |
| **QAOA (Config F) vs Tabu Search (Config D)** | +10.91 km (QAOA is worse) | **0.0842** | 0.31 | No Quantum Advantage ($p > 0.05$) |
| **QAOA (Config F) vs Single KL (Config C)** | +2.64 km (QAOA is worse) | **0.5821** | 0.08 | Statistically Indistinguishable |
| **QAOA (Config F) vs Random 512 (Config E)** | +3.46 km (QAOA is worse) | **0.4910** | 0.10 | Statistically Indistinguishable |
| **Adaptive (Config G) vs Tabu (Config D)** | +1.99 km | **0.5210** | 0.06 | Parity with Superior Flexibility |

### Statistical Conclusions
1. **Classical Equivalence Confirmed:** Fast QAOA demonstrates no statistically significant superiority over any classical generator ($p > 0.05$ across all head-to-head comparisons).
2. **Tabu Search Superiority:** Tabu Search provides the highest empirical route reduction (-26.00 km vs Config B, $p = 0.0001$, $d = 0.71$).
3. **Random Sampling Matches QAOA:** Uniform random sampling with Proposition 1 filtering achieves 602.90 km, outperforming QAOA's 606.36 km ($p = 0.4910$), confirming that Proposition 1 guardrailing—not quantum coherence—drives solution quality.
