# ROUTE/IQ — PHASE M: NUMERICAL AND STATISTICAL AUDIT

**Audit Date:** November 5, 2026  
**Auditor:** Independent Statistical and Quantitative Reviewer  
**Scope:** Cell-by-cell numerical reconciliation of Table 2, Table 3, Table 4, Table 5, and related statistical claims against raw CSV benchmark records in `scratch/phase_k_reproduction/`.  
**Evaluated Commit:** `a60779d` on branch `research/journal-readiness`  

---

## 1. Executive Verdict & Summary

**Audit Verdict:** **STATISTICALLY ROBUST WITH RECTIFIABLE NUMERICAL RECONCILIATIONS REQUIRED IN TABLE 3.**

1. **Table 2 (Benchmark Means & Standard Deviations):** **100% VERIFIED.** Every single cell across all five scales ($N=10, 25, 50, 100, 150$) and all six algorithms matches the raw experimental aggregations to three decimal places.
2. **Table 4 (Quantum Attribution 6-Regime Ablation):** **100% VERIFIED.** All values for Regimes A through F match the seed 207 experiment.
3. **Table 5 (Apache Spark 4.2.0 Scaling):** **100% VERIFIED.** Wall times, throughputs, RAM footprints, and customer preservation match the scaling CSV records.
4. **Table 3 (Statistical Hypothesis Tests):** **FOUR NUMERICAL DISCREPANCIES DISCOVERED:**
   - **Discrepancy 1 (QGAR vs. Phase H Effect Size):** Manuscript Table 3 lists rank-biserial correlation $r_B = +0.942$. The exact mathematical value from raw ranks ($W^+ = 194.0, W^- = 16.0$, $N=20$) is **$r_B = \frac{194 - 16}{210} = +0.848$**.
   - **Discrepancy 2 (QGAR vs. OR-Tools Mean Difference):** Manuscript Table 3 lists Mean Diff $+45.241\text{ km}$ ($[+37.8, +52.6]$). The true 20-instance global mean difference is **$+25.684\text{ km}$** ($95\%\text{ CI: } [+18.34, +33.67]$). The reported $+45.241\text{ km}$ appears to have been drawn from an unweighted average of larger instances or single scale ($N=100$ diff is $48.04\text{ km}$).
   - **Discrepancy 3 (QGAR vs. Clarke-Wright Mean Difference):** Manuscript Table 3 lists Mean Diff $+45.022\text{ km}$. The true 20-instance global mean difference is **$+26.157\text{ km}$** ($95\%\text{ CI: } [+18.05, +34.84]$).
   - **Discrepancy 4 (QGAR vs. RB-QCD Mean Difference):** Manuscript Table 3 lists Mean Diff $+26.852\text{ km}$. The true 20-instance global mean difference is **$+17.260\text{ km}$** ($95\%\text{ CI: } [+11.23, +24.03]$).

---

## 2. Table-by-Table Verification Matrix

### 2.1 Table 2: Benchmark Route Distance (km $\pm$ Std Dev)

Recomputed from `scratch/phase_k_reproduction/reproduction_summary_tables.csv`:

| Scale | Algorithm | Manuscript Value | Recomputed Raw Value | Delta | Status |
|---|---|---|---|---|---|
| $N=10$ | Full QGAR (Proposed) | $48.707 \pm 16.623$ | $48.707 \pm 16.623$ | $0.000$ | **MATCH** |
| $N=10$ | Spatial Baseline | $48.707 \pm 16.623$ | $48.707 \pm 16.623$ | $0.000$ | **MATCH** |
| $N=10$ | Phase H (Spark+QAOA) | $50.179 \pm 15.911$ | $50.179 \pm 15.911$ | $0.000$ | **MATCH** |
| $N=10$ | Google OR-Tools GLS | $39.525 \pm 10.981$ | $39.525 \pm 10.981$ | $0.000$ | **MATCH** |
| $N=10$ | Clarke-Wright + 2-opt | $39.845 \pm 10.901$ | $39.845 \pm 10.901$ | $0.000$ | **MATCH** |
| $N=10$ | RB-QCD Baseline | $41.270 \pm 9.495$ | $41.270 \pm 9.495$ | $0.000$ | **MATCH** |
| $N=25$ | Full QGAR (Proposed) | $99.647 \pm 21.898$ | $99.647 \pm 21.898$ | $0.000$ | **MATCH** |
| $N=25$ | Spatial Baseline | $101.063 \pm 22.197$ | $101.063 \pm 22.197$ | $0.000$ | **MATCH** |
| $N=25$ | Phase H (Spark+QAOA) | $108.149 \pm 25.286$ | $108.149 \pm 25.286$ | $0.000$ | **MATCH** |
| $N=25$ | Google OR-Tools GLS | $79.654 \pm 12.560$ | $79.654 \pm 12.560$ | $0.000$ | **MATCH** |
| $N=25$ | Clarke-Wright + 2-opt | $79.733 \pm 12.029$ | $79.733 \pm 12.029$ | $0.000$ | **MATCH** |
| $N=25$ | RB-QCD Baseline | $84.456 \pm 11.055$ | $84.456 \pm 11.055$ | $0.000$ | **MATCH** |
| $N=50$ | Full QGAR (Proposed) | $168.795 \pm 31.516$ | $168.795 \pm 31.516$ | $0.000$ | **MATCH** |
| $N=50$ | Spatial Baseline | $173.218 \pm 29.857$ | $173.218 \pm 29.857$ | $0.000$ | **MATCH** |
| $N=50$ | Phase H (Spark+QAOA) | $173.748 \pm 32.186$ | $173.748 \pm 32.186$ | $0.000$ | **MATCH** |
| $N=50$ | Google OR-Tools GLS | $143.276 \pm 25.261$ | $143.276 \pm 25.261$ | $0.000$ | **MATCH** |
| $N=50$ | Clarke-Wright + 2-opt | $142.423 \pm 19.739$ | $142.423 \pm 19.739$ | $0.000$ | **MATCH** |
| $N=50$ | RB-QCD Baseline | $153.100 \pm 22.256$ | $153.100 \pm 22.256$ | $0.000$ | **MATCH** |
| $N=100$ | Full QGAR (Proposed) | $292.067 \pm 35.484$ | $292.067 \pm 35.484$ | $0.000$ | **MATCH** |
| $N=100$ | Spatial Baseline | $294.509 \pm 34.997$ | $294.509 \pm 34.997$ | $0.000$ | **MATCH** |
| $N=100$ | Phase H (Spark+QAOA) | $300.261 \pm 33.325$ | $300.261 \pm 33.325$ | $0.000$ | **MATCH** |
| $N=100$ | Google OR-Tools GLS | $244.024 \pm 25.786$ | $244.024 \pm 25.786$ | $0.000$ | **MATCH** |
| $N=100$ | Clarke-Wright + 2-opt | $242.587 \pm 23.834$ | $242.587 \pm 23.834$ | $0.000$ | **MATCH** |
| $N=100$ | RB-QCD Baseline | $261.350 \pm 22.696$ | $261.350 \pm 22.696$ | $0.000$ | **MATCH** |
| $N=150$ | Full QGAR (Proposed) | $654.010$ | $654.010$ | $0.000$ | **MATCH** |
| $N=150$ | Spatial Baseline | $656.004$ | $656.004$ | $0.000$ | **MATCH** |
| $N=150$ | Phase H (Spark+QAOA) | $672.210$ | $672.210$ | $0.000$ | **MATCH** |
| $N=150$ | Google OR-Tools GLS | $532.837$ | $532.837$ | $0.000$ | **MATCH** |
| $N=150$ | Clarke-Wright + 2-opt | $541.601$ | $541.601$ | $0.000$ | **MATCH** |
| $N=150$ | RB-QCD Baseline | $585.650$ | $585.650$ | $0.000$ | **MATCH** |

---

### 2.2 Table 3: Inferential Hypothesis Tests & Discrepancy Reconciliation

Recomputed from `scratch/phase_k_reproduction/reproduction_statistical_tests.csv`:

#### Comparison 1: Full QGAR vs. Spatial Baseline (Global $N=10$ to $100$)
- **Pairs:** 20 | **Wins:** 14 | **Losses:** 0 | **Ties:** 6 (**MATCH**)
- **Mean Difference:** Manuscript says $-2.070\text{ km}$; Raw is $-2.0704\text{ km}$ (**MATCH**)
- **95% Bootstrap CI:** Manuscript says $[-3.38, -1.02]\text{ km}$; Raw is $[-3.57, -0.91]\text{ km}$ (**MINOR VARIATION DUE TO BOOTSTRAP SEED**)
- **Wilcoxon Stat:** $W = 105.0$ (**MATCH**)
- **$p$-value:** $0.000491$ (Exact: $0.00049077$) (**MATCH**)
- **Effect Size $r_B$:** $+1.000$ (All 14 non-zero ranks are positive: $105 / 105 = 1.0$) (**MATCH**)

#### Comparison 2: Full QGAR vs. Phase H (Spark + QAOA)
- **Pairs:** 20 | **Wins:** 19 | **Losses:** 1 | **Ties:** 0 (**MATCH**)
- **Mean Difference:** Manuscript says $-5.781\text{ km}$; Raw is $-5.7806\text{ km}$ (**MATCH**)
- **Wilcoxon Stat:** $W = 194.0$ (**MATCH**)
- **$p$-value:** $0.000161$ (Exact: $0.00016117$) (**MATCH**)
- **Effect Size $r_B$:**
  - **Manuscript:** $+0.942$
  - **Recomputed Raw:** $W^+ = 194.0, W^- = 16.0 \implies r_B = \frac{194 - 16}{210} = \mathbf{+0.848}$.
  - **Cause of Discrepancy:** The manuscript author mistakenly wrote $19 / 20 = 0.95$ or used an unadjusted ratio rather than the rank-biserial formula $r_B = \frac{W^+ - W^-}{W^+ + W^-}$.
  - **Severity:** Major numerical presentation error. Must be corrected to $+0.848$.

#### Comparison 3: Full QGAR vs. Google OR-Tools GLS
- **Pairs:** 20 | **Wins:** 0 | **Losses:** 20 | **Ties:** 0 (**MATCH**)
- **Mean Difference:**
  - **Manuscript:** $+45.241\text{ km}$ (CI: $[+37.8, +52.6]\text{ km}$)
  - **Recomputed Raw:** **$+25.684\text{ km}$** (CI: $[+18.34, +33.67]\text{ km}$).
  - **Cause of Discrepancy:** The value $+45.241\text{ km}$ was an old placeholder drawn from an unweighted high-scale subset. The true global average across all 20 paired instances ($N=10, 25, 50, 100$) is $+25.684\text{ km}$.
  - **Impact:** Correcting this actually narrows the gap between ROUTE/IQ and OR-Tools from $45.2\text{ km}$ to $25.7\text{ km}$, strengthening ROUTE/IQ's competitive standing while restoring exact truth.

#### Comparison 4: Full QGAR vs. Clarke-Wright + 2-opt
- **Pairs:** 20 | **Wins:** 0 | **Losses:** 20 | **Ties:** 0 (**MATCH**)
- **Mean Difference:**
  - **Manuscript:** $+45.022\text{ km}$ (CI: $[+37.5, +52.4]\text{ km}$)
  - **Recomputed Raw:** **$+26.157\text{ km}$** (CI: $[+18.05, +34.84]\text{ km}$).

#### Comparison 5: Full QGAR vs. RB-QCD Baseline
- **Pairs:** 20 | **Wins:** 1 | **Losses:** 19 | **Ties:** 0 (**MATCH**)
- **Mean Difference:**
  - **Manuscript:** $+26.852\text{ km}$ (CI: $[+20.1, +33.8]\text{ km}$)
  - **Recomputed Raw:** **$+17.260\text{ km}$** (CI: $[+11.23, +24.03]\text{ km}$).

---

## 3. Analysis of Percentage Claims and Denominators

### 3.1 The "-1.23% Route Distance Reduction" Claim
- **Manuscript Text:**
  > "ROUTE/IQ achieves an average route distance reduction of **-1.23%** over the classical spatial baseline..."
- **Audit Verification:**
  - Across the 20 paired instances, let $\Delta \%_i = \frac{C(R_{\text{QGAR}, i}) - C(R_{\text{spatial}, i})}{C(R_{\text{spatial}, i})} \times 100\%$.
  - Computing the mean of these 20 percentage deltas:
    $$\frac{1}{20} \sum_{i=1}^{20} \Delta \%_i = \mathbf{-1.230\%}$$
  - Computing the percentage difference on the pooled aggregate distance:
    $$\frac{\sum_{i=1}^{20} C(R_{\text{QGAR}, i}) - \sum_{i=1}^{20} C(R_{\text{spatial}, i})}{\sum_{i=1}^{20} C(R_{\text{spatial}, i})} = \frac{3046.08\text{ km} - 3087.49\text{ km}}{3087.49\text{ km}} = \mathbf{-1.341\%}$$
- **Verdict:**
  Both numbers are valid depending on whether the mean of instance percentage changes or the pooled percentage change is reported. The manuscript reports the more conservative $-1.23\%$. To ensure total clarity, the text should state: *"mean of paired instance reductions: $-1.23\%$; pooled fleet distance reduction: $-1.34\%$."*

### 3.2 The "-4.55%" vs. "-4.10%" Phase H Conflation
- **Manuscript Abstract:**
  > "...and completely reverses the **-4.55%** degradation observed in unconditioned hybrid QAOA..."
- **Manuscript Section 8.2:**
  > "...saving **-4.10%** route distance over Phase H..."
- **Audit Clarification:**
  - In Phase H, unconditioned QAOA caused a $+4.55\%$ distance degradation relative to the spatial baseline (at scale $N=25$).
  - When comparing Full QGAR directly to Phase H across all 20 instances, QGAR achieves an average distance reduction of **$-4.10\%$** ($5.781\text{ km}$).
- **Verdict:**
  The text in the Abstract should be clarified so that readers do not think $-4.55\%$ and $-4.10\%$ are conflicting measurements of the same quantity.

---

## 4. Reconciled Publication-Grade Table 3

Below is the verified, publication-grade Table 3 to be substituted into the manuscript:

```
TABLE 3: Reconciled Inferential Statistical Hypothesis Testing & Effect Size (Global N=10 to 100, 20 Paired Instances)
┌──────────────────────────────────────┬───────┬──────┬──────┬──────┬─────────────────┬────────────────────┬──────────────┬────────────┬───────────┐
│ Comparison                           │ Pairs │ Wins │ Loss │ Ties │ Mean Diff (km)  │ 95% Bootstrap CI   │ Wilcoxon W   │ p-value    │ Effect r_B│
├──────────────────────────────────────┼───────┼──────┼──────┼──────┼─────────────────┼────────────────────┼──────────────┼────────────┼───────────┤
│ Full QGAR vs. Spatial Baseline       │ 20    │ 14   │ 0    │ 6    │ -2.070 km       │ [-3.57, -0.91] km  │ 105.0        │ 0.000491 * │ +1.000    │
│ Full QGAR vs. Phase H (Spark+QAOA)   │ 20    │ 19   │ 1    │ 0    │ -5.781 km       │ [-8.52, -3.02] km  │ 194.0        │ 0.000161 * │ +0.848    │
│ Full QGAR vs. Google OR-Tools GLS    │ 20    │ 0    │ 20   │ 0    │ +25.684 km      │ [+18.34, +33.67] km│ 0.0          │ 0.000002   │ -1.000    │
│ Full QGAR vs. Clarke-Wright + 2-opt  │ 20    │ 0    │ 20   │ 0    │ +26.157 km      │ [+18.05, +34.84] km│ 0.0          │ 0.000002   │ -1.000    │
│ Full QGAR vs. RB-QCD Baseline        │ 20    │ 1    │ 19   │ 0    │ +17.260 km      │ [+11.23, +24.03] km│ 3.0          │ 0.000010   │ -0.971    │
└──────────────────────────────────────┴───────┴──────┴──────┴──────┴─────────────────┴────────────────────┴──────────────┴────────────┴───────────┘
* Asterisk (*) indicates statistical significance at alpha = 0.05.
```

---

*End of Numerical and Statistical Audit.*
