# ROUTE/IQ — PHASE M: PRIORITIZED MANUSCRIPT CORRECTIONS

**Audit Date:** November 5, 2026  
**Auditor:** Independent Academic Review Team  
**Scope:** Actionable, itemized inventory of prioritized manuscript corrections categorized into Critical, Major, and Minor tiers, with exact textual diffs and file locations.  
**Evaluated Commit:** `a60779d` on branch `research/journal-readiness`  

---

## 1. Classification Framework

- **CRITICAL:** Flaws that risk immediate paper rejection, convey technically false claims, or misrepresent experimental methodology.
- **MAJOR:** Substantial inaccuracies, uncalibrated metrics, numerical discrepancies, or omissions of seminal prior art.
- **MINOR:** Typographical errors, stylistic inflations, citation formatting, and minor wording polish.

---

## 2. Critical Corrections (Tier 1)

### Correction C1: Terminology Error — "Streaming Ingestion" vs. Batch Processing
- **Existing Claim (Abstract, p. 1; Sec 1.2, p. 2; Fig 1, p. 3):**
  > "Spark actively ingests high-volume order streams..."  
  > "Streaming orders (N up to 50,000)..."  
  > "ingests streaming order data..."
- **Evidence:**
  `backend/app/services/spark_routing_preprocessor.py` (lines 81–144) takes a static Pandas DataFrame, calls `spark.createDataFrame(df_customers)`, executes batch SQL/Window transformations, and materializes via `.toPandas()`. There is no Kafka, Spark Structured Streaming, socket feed, or sliding event-time window.
- **Problem:**
  Claiming "streaming ingestion" when the system performs in-memory batch micro-partitioning will be flagged by distributed systems reviewers as a technical misrepresentation.
- **Recommended Replacement:**
  Replace "streaming order streams" and "streaming ingestion" with:
  > *"high-throughput batch order streams"* or *"distributed in-memory batch spatial preprocessing"*.
- **Target Files:**
  - `ROUTE_IQ_FULL_JOURNAL_MANUSCRIPT.md` (Lines 13, 47, 130)
  - `ROUTE_IQ_FULL_JOURNAL_MANUSCRIPT.tex` (Lines 33, 82, Fig 1)
  - `manuscript/ROUTE_IQ_ABSTRACT.md` (Line 14)

---

### Correction C2: Reframing Theorem 1 — Fallback Guardrail vs. Intrinsic Theorem
- **Existing Claim (Sec 5.5, p. 4; Theorem 1):**
  > "Theorem 1 (Campaign-Level Monotonic Non-Degradation): Let $R_{\text{QGAR}}$ be the routing campaign produced by ROUTE/IQ... Then $C(R_{\text{QGAR}}) \le C(R_{\text{spatial}}) + \epsilon$."
- **Evidence:**
  `backend/app/services/optimization/qgar_pipeline.py` (lines 406–415):
  ```python
  if dist_qaoa <= dist_spatial + 1e-4:
      reconstructed_stops = reconstructed_qaoa
  else:
      reconstructed_stops = reconstructed_spatial
  ```
- **Problem:**
  The guarantee is not a mathematical convergence theorem of QAOA or variational quantum states. It is an algorithmic acceptance-rejection check (`if candidate <= baseline else fallback`). Presenting `min(a, b) <= b` as a mathematical theorem of QAOA appears pretentious and risks peer review rejection.
- **Recommended Replacement:**
  Reframe Theorem 1 as:
  > **"Proposition 1 (Non-Degradation via Algorithmic Route Certification Guardrail):** *Let $R_{\text{QGAR}}$ be the delivery campaign produced by ROUTE/IQ, incorporating the End-to-End Route Certification Guardrail that evaluates candidate routes against the classical spatial baseline. Then by algorithmic construction, for all valid CVRP instances: $C(R_{\text{QGAR}}) \le C(R_{\text{spatial}}) + \epsilon$ ($\epsilon = 10^{-4}\text{ km}$)."*
- **Target Files:**
  - `ROUTE_IQ_FULL_JOURNAL_MANUSCRIPT.md` (Section 5.5)
  - `ROUTE_IQ_FULL_JOURNAL_MANUSCRIPT.tex` (Section 5, Theorem 1)

---

### Correction C3: Nature of Planar Crossing Regularization
- **Existing Claim (Sec 5.4, p. 4):**
  > "The number of straight-line 2D planar crossings is computed via line segment intersection: $\text{Cross}(P) = \sum \dots$"
- **Evidence:**
  `backend/app/services/optimization/qgar_pipeline.py` (lines 24–47) evaluates 2D intersections between straight lines connecting `(latitude, longitude)` customer coordinates. It does not evaluate the physical directed centerline paths of Manhattan's 142,123 OSM road segments. In Trial 0, avoiding a straight-line crossing forced a vehicle to circumnavigate a one-way avenue block, causing a $+0.7\%$ detour.
- **Problem:**
  Failing to explicitly disclose that crossings are calculated on Euclidean coordinate proxies rather than full road-network topology leaves the authors open to harsh criticism from transportation reviewers.
- **Recommended Replacement:**
  Add explicit clarification in Section 5.4:
  > *"Note on Geometric Topology: Planar crossings are evaluated on the 2D Euclidean projection of customer geographic coordinates, serving as an empirical geometric inductive bias (demonstrating 96.4% empirical alignment) rather than full street-network centerline tracing. As demonstrated in Section 9.3, on directed street grids with one-way restrictions, physical road paths can occasionally require detour loops that straight-line Euclidean metrics do not capture."*
- **Target Files:**
  - `ROUTE_IQ_FULL_JOURNAL_MANUSCRIPT.md` (Section 5.4)
  - `ROUTE_IQ_FULL_JOURNAL_MANUSCRIPT.tex` (Section 5.4)

---

## 3. Major Corrections (Tier 2)

### Correction M1: Reconcile Table 3 Numerical Discrepancies
- **Existing Values in Table 3:**
  - QGAR vs. Phase H Effect Size: `Effect r_B: +0.942`
  - QGAR vs. OR-Tools Mean Diff: `Mean Diff: +45.241 km` (CI: `[+37.8, +52.6] km`)
  - QGAR vs. Clarke-Wright Mean Diff: `Mean Diff: +45.022 km` (CI: `[+37.5, +52.4] km`)
  - QGAR vs. RB-QCD Mean Diff: `Mean Diff: +26.852 km` (CI: `[+20.1, +33.8] km`)
- **Evidence in Raw Benchmark Data (`reproduction_statistical_tests.csv`):**
  - QGAR vs. Phase H: $W^+ = 194.0, W^- = 16.0 \implies r_B = \frac{194 - 16}{210} = \mathbf{+0.848}$.
  - QGAR vs. OR-Tools: True 20-instance global mean difference is **$+25.684\text{ km}$** ($95\%\text{ CI: } [+18.34, +33.67]\text{ km}$).
  - QGAR vs. Clarke-Wright: True 20-instance global mean difference is **$+26.157\text{ km}$** ($95\%\text{ CI: } [+18.05, +34.84]\text{ km}$).
  - QGAR vs. RB-QCD: True 20-instance global mean difference is **$+17.260\text{ km}$** ($95\%\text{ CI: } [+11.23, +24.03]\text{ km}$).
- **Problem:**
  Publishing numbers that deviate from the raw data files undermines scientific reproducibility.
- **Recommended Replacement:**
  Update Table 3 in both Markdown and LaTeX manuscripts with the exact recomputed raw statistics.
- **Target Files:**
  - `ROUTE_IQ_FULL_JOURNAL_MANUSCRIPT.md` (Table 3)
  - `ROUTE_IQ_FULL_JOURNAL_MANUSCRIPT.tex` (Table 3 / Section 6)

---

### Correction M2: Clarify Single-Host Local Execution (`local[*]`)
- **Existing Text (Abstract, Sec 1.1):**
  Uses phrases like "distributed Big Data computing" without qualifying that all experiments were executed in local multithreaded mode on a single workstation host.
- **Evidence:**
  `SparkRoutingPreprocessor` configures `master="local[*]"` on Windows 11 with OpenJDK 17 and Hadoop 3.3.6 winutils.
- **Problem:**
  Readers and reviewers may assume that multi-node cluster deployment (e.g., AWS EMR or Databricks) was evaluated.
- **Recommended Replacement:**
  In Section 6 (Implementation) and Section 10 (Limitations), add:
  > *"All Apache Spark experiments were executed in local multithreaded mode (`local[*]`) on a single 8-core host. While Catalyst query optimization and distributed RDD operations are exercised, network serialization, distributed shuffle I/O, and node failover across physical cloud clusters remain subjects for future distributed benchmarking."*
- **Target Files:**
  - `ROUTE_IQ_FULL_JOURNAL_MANUSCRIPT.md` (Sections 6, 10)
  - `ROUTE_IQ_FULL_JOURNAL_MANUSCRIPT.tex` (Sections 6, 9)

---

### Correction M3: Bibliographic Expansion — Lucas (2014) and Gillett & Miller (1974)
- **Problem:**
  The manuscript currently omits Andrew Lucas's foundational 2014 paper on Ising formulations of NP problems and Gillett & Miller's 1974 sweep algorithm paper.
- **Recommended Replacement:**
  Add `lucas2014ising`, `gillett1974sweep`, and `voudouris1999guided` to `ROUTE_IQ_REFERENCES.bib`, and cite them in Sections 2, 4, and 5.
- **Target Files:**
  - `ROUTE_IQ_REFERENCES.bib`
  - `ROUTE_IQ_FULL_JOURNAL_MANUSCRIPT.md`
  - `ROUTE_IQ_FULL_JOURNAL_MANUSCRIPT.tex`

---

## 4. Minor Corrections (Tier 3)

### Correction m1: Clarify Percentage Improvement Metric
- **Existing Text:**
  > "...achieves an average route distance reduction of **-1.23%**..."
- **Recommended Replacement:**
  > *"...achieves an average route distance reduction of **-1.23%** (mean of paired instance percentage reductions; -1.34% pooled fleet distance reduction)..."*

### Correction m2: Distinguish "-4.55%" from "-4.10%"
- **Existing Text (Abstract):**
  > "...and completely reverses the **-4.55%** degradation observed in unconditioned hybrid QAOA..."
- **Recommended Replacement:**
  > *"...and eliminates the **-4.55%** degradation observed in unconditioned hybrid QAOA relative to the spatial sweep, achieving a **-4.10%** ($5.78\text{ km}$) distance reduction over Phase H..."*

### Correction m3: Temper Hyperbolic Novelty Phrases
- **Instances:**
  - Replace *"first framework to integrate"* with *"pioneering engineering framework integrating"*.
  - Replace *"completely eliminates"* with *"effectively prevents"*.
  - Replace *"revolutionary bridge"* with *"certified operational bridge"*.

---

*End of Prioritized Corrections Inventory.*

