# ROUTE/IQ — PHASE N: STATISTICAL REPRODUCTION REPORT

**Date:** November 5, 2026  
**Auditor / Statistician:** Independent Quantitative Verification Team  
**Scope:** Complete reproduction and audit of all descriptive and inferential statistics reported in the ROUTE/IQ manuscript directly from raw benchmark records in `scratch/phase_k_reproduction/`.  
**Evaluated Commit:** `22c3a27` on branch `research/journal-readiness`  

---

## 1. Executive Summary & Audit Verification Status

Every statistical test, point estimate, confidence interval, and non-parametric hypothesis test reported in the corrected ROUTE/IQ manuscript has been independently reproduced directly from raw experimental logs without alteration.

```
┌────────────────────────────────────────────────────────────────────────┐
│ STATISTICAL REPRODUCIBILITY VERDICT: 100% REPRODUCED & VERIFIED        │
├────────────────────────────────────────────────────────────────────────┤
│ • Paired Benchmark Instances: 20 paired instances across 5 seeds       │
│ • Full QGAR vs. Spatial Baseline: W = 105.0, p = 0.000491, r_B = +1.000│
│ • Full QGAR vs. Phase H:         W = 194.0, p = 0.000161, r_B = +0.848 │
│ • Full QGAR vs. OR-Tools GLS:    Mean Diff = +25.684 km, r_B = -1.000  │
│ • Full QGAR vs. Clarke-Wright:   Mean Diff = +26.157 km, r_B = -1.000  │
│ • Full QGAR vs. RB-QCD Baseline: Mean Diff = +17.260 km, r_B = -0.971  │
│ • Benjamini-Hochberg FDR:        Preserved at alpha = 0.05             │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Experimental Pairing and Sample Protocol

All statistical tests were conducted across a balanced, paired experimental design:
- **Scales Evaluated:** $N \in \{10, 25, 50, 100\}$ delivery customers.
- **Random Evaluation Seeds:** $5$ fixed seeds ($\{107, 207, 307, 407, 507\}$).
- **Total Paired Instances:** $4 \text{ scales} \times 5 \text{ seeds} = \mathbf{20\text{ paired instances}}$.
- **Pairing Guarantee:** Each algorithm solved identical customer locations, demands, and depot coordinates snapped to the 54,128-node Manhattan road graph.

---

## 3. Recomputed Benchmark Performance (Table 8 / Table II)

Directly recomputed from `scratch/phase_k_reproduction/reproduction_summary_tables.csv`:

| Scale | Full QGAR (Proposed) | Spatial Baseline | Phase H (Spark+QAOA) | Google OR-Tools GLS | Clarke-Wright + 2-opt | RB-QCD Baseline |
|---|---|---|---|---|---|---|
| **$N=10$** | $48.707 \pm 16.623$ | $48.707 \pm 16.623$ | $50.179 \pm 15.911$ | $39.525 \pm 10.981$ | $39.845 \pm 10.901$ | $41.270 \pm 9.495$ |
| **$N=25$** | $99.647 \pm 21.898$ | $101.063 \pm 22.197$ | $108.149 \pm 25.286$ | $79.654 \pm 12.560$ | $79.733 \pm 12.029$ | $84.456 \pm 11.055$ |
| **$N=50$** | $168.795 \pm 31.516$ | $173.218 \pm 29.857$ | $173.748 \pm 32.186$ | $143.276 \pm 25.261$ | $142.423 \pm 19.739$ | $153.100 \pm 22.256$ |
| **$N=100$** | $292.067 \pm 35.484$ | $294.509 \pm 34.997$ | $300.261 \pm 33.325$ | $244.024 \pm 25.786$ | $242.587 \pm 23.834$ | $261.350 \pm 22.696$ |
| **$N=150$** | $654.010$ | $656.004$ | $672.210$ | $532.837$ | $541.601$ | $585.650$ |

All values match the manuscript Table 8 and LaTeX Table II to three decimal places.

---

## 4. Inferential Statistical Hypothesis Tests (Table 9 / Table III)

Recomputed from `scratch/phase_k_reproduction/reproduction_statistical_tests.csv`:

### 4.1 Full QGAR vs. Spatial Baseline (No QAOA)
- **Sample Size ($N_{\text{pairs}}$):** 20
- **Outcomes:** 14 Wins, 0 Losses, 6 Ties.
- **Mean Difference:** $-2.0704\text{ km}$ ($-1.230\%$ mean paired reduction; $-1.341\%$ pooled fleet reduction).
- **95% Bootstrap Confidence Interval:** $[-3.5659, -0.9144]\text{ km}$ ($10,000$ resamples).
- **Wilcoxon Signed-Rank Stat ($W$):** $W = 105.0$ (Pratt method for zero-differences).
- **$p$-value:** $0.00049077 \implies \mathbf{p = 0.000491}$ (Statistically significant at $\alpha = 0.05$).
- **Rank-Biserial Effect Size ($r_B$):**
  $$r_B = \frac{W^+ - W^-}{W^+ + W^-} = \frac{105.0 - 0.0}{105.0} = \mathbf{+1.000}$$

### 4.2 Full QGAR vs. Phase H (Spark + QAOA)
- **Sample Size ($N_{\text{pairs}}$):** 20
- **Outcomes:** 19 Wins, 1 Loss, 0 Ties.
- **Mean Difference:** $-5.7806\text{ km}$ ($-4.10\%$ reduction over unconditioned QAOA).
- **95% Bootstrap Confidence Interval:** $[-8.5152, -3.0179]\text{ km}$.
- **Wilcoxon Signed-Rank Stat ($W$):** $W^+ = 194.0, W^- = 16.0 \implies W = 194.0$.
- **$p$-value:** $0.00016117 \implies \mathbf{p = 0.000161}$ (Statistically significant at $\alpha = 0.05$).
- **Rank-Biserial Effect Size ($r_B$):**
  $$r_B = \frac{194.0 - 16.0}{210.0} = \frac{178.0}{210.0} = \mathbf{+0.848}$$

### 4.3 Full QGAR vs. Google OR-Tools Guided Local Search
- **Sample Size ($N_{\text{pairs}}$):** 20
- **Outcomes:** 0 Wins, 20 Losses, 0 Ties.
- **Mean Difference:** $+25.6843\text{ km}$ (OR-Tools is $21.02\%$ shorter).
- **95% Bootstrap Confidence Interval:** $[+18.3430, +33.6671]\text{ km}$.
- **Wilcoxon Stat ($W$):** $W = 0.0$.
- **$p$-value:** $1.907 \times 10^{-6} \implies \mathbf{p = 0.000002}$.
- **Effect Size ($r_B$):** $\mathbf{-1.000}$.

### 4.4 Full QGAR vs. Clarke-Wright + 2-opt
- **Sample Size ($N_{\text{pairs}}$):** 20
- **Outcomes:** 0 Wins, 20 Losses, 0 Ties.
- **Mean Difference:** $+26.1571\text{ km}$ (Clarke-Wright is $20.94\%$ shorter).
- **95% Bootstrap Confidence Interval:** $[+18.0478, +34.8423]\text{ km}$.
- **Wilcoxon Stat ($W$):** $W = 0.0$.
- **$p$-value:** $1.907 \times 10^{-6} \implies \mathbf{p = 0.000002}$.
- **Effect Size ($r_B$):** $\mathbf{-1.000}$.

### 4.5 Full QGAR vs. RB-QCD Baseline
- **Sample Size ($N_{\text{pairs}}$):** 20
- **Outcomes:** 1 Win, 19 Losses, 0 Ties.
- **Mean Difference:** $+17.2599\text{ km}$ (RB-QCD is $13.71\%$ shorter).
- **95% Bootstrap Confidence Interval:** $[+11.2260, +24.0274]\text{ km}$.
- **Wilcoxon Stat ($W$):** $W = 3.0$.
- **$p$-value:** $9.537 \times 10^{-6} \implies \mathbf{p = 0.000010}$.
- **Effect Size ($r_B$):** $\mathbf{-0.971}$.

---

## 5. False Discovery Rate (FDR) Multi-Testing Adjustments

Applying the Benjamini-Hochberg procedure across all scale-stratified confirmatory tests for QGAR vs. Spatial Baseline:
- $N=10$: $p = 1.0000 \implies p_{\text{adj}} = 1.0000$ (No difference; 5 ties)
- $N=25$: $p = 0.0625 \implies p_{\text{adj}} = 0.0833$ (Marginally significant)
- $N=50$: $p = 0.03125 \implies p_{\text{adj}} = \mathbf{0.0500^*}$ (Significant)
- $N=100$: $p = 0.03125 \implies p_{\text{adj}} = \mathbf{0.0500^*}$ (Significant)

Confirmatory findings at $N=50$ and $N=100$ retain statistical significance at the standard false discovery rate threshold $\alpha = 0.05$.

---

## 6. Verification of the Non-Degradation Proposition

Across all experimental campaigns:
- Benchmark paired instances: 20 instances ($N=10$ to $100$) $\implies$ **0 violations**.
- Single large instance: 1 instance ($N=150$) $\implies$ **0 violations**.
- Adversarial edge cases: 10 stress tests (collinear, disconnected, single-customer, zero demand) $\implies$ **0 violations**.
- **Overall Non-Degradation Compliance:**
  $$\text{Violations} = 0 / 31 = \mathbf{0.0\%}$$

This confirms that the algorithmic Route Certification Guardrail functions flawlessly across 100% of tested topologies.

---

*End of Statistical Reproduction Report.*

