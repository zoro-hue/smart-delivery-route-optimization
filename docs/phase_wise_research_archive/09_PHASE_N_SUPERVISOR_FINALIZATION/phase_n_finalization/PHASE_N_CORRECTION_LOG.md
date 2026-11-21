# ROUTE/IQ — PHASE N: MANUSCRIPT CORRECTION LOG

**Date:** November 5, 2026  
**Auditor / Implementation Engineer:** Finalization & Quality Assurance Team  
**Starting Commit:** `22c3a27` on branch `research/journal-readiness`  
**Scope:** Exhaustive itemized record of every textual, numerical, mathematical, and bibliographic correction applied to the ROUTE/IQ journal manuscript package in accordance with Phase M peer-review requirements.

---

## 1. Summary of Applied Corrections

All corrections identified in `phase_m_review/PHASE_M_PRIORITIZED_CORRECTIONS.md` have been fully implemented across both Markdown and LaTeX manuscripts and their supporting artifacts. Zero technical claims were altered without empirical or code-level justification.

---

## 2. Detailed Itemized Log of Corrections

### Correction C1: Spark Terminology — Removal of "Streaming Ingestion" Overstatement
- **Target Files:**
  - `manuscript/ROUTE_IQ_FULL_JOURNAL_MANUSCRIPT.md` (Abstract, Sec 1.2, Sec 4, Fig 1)
  - `manuscript/ROUTE_IQ_FULL_JOURNAL_MANUSCRIPT.tex` (Abstract, Sec 1, Sec 4, Fig 1)
  - `manuscript/ROUTE_IQ_ABSTRACT.md`
  - `manuscript/ROUTE_IQ_CONTRIBUTIONS_AND_NOVELTY.md`
- **Previous Claim:**
  *"Spark actively ingests high-volume order streams..."* / *"Streaming orders (N up to 50,000)..."*
- **Applied Replacement:**
  *"Spark actively executes high-throughput batch order ingestion, computes calibrated traffic volume delays using a Bureau of Public Roads (BPR) impedance model mapped to OpenStreetMap road networks, and partitions delivery territories via capacity-constrained polar sweeps into compact microclusters."*
- **Justification:**
  Reflects actual PySpark DataFrame creation from in-memory batch collections via `spark.createDataFrame()`, avoiding misleading claims of Kafka or Spark Structured Streaming.

---

### Correction C2: Reframe Theorem 1 to Proposition 1 (Algorithmic Guardrail)
- **Target Files:**
  - `manuscript/ROUTE_IQ_FULL_JOURNAL_MANUSCRIPT.md` (Sec 5.5, Abstract, Sec 11)
  - `manuscript/ROUTE_IQ_FULL_JOURNAL_MANUSCRIPT.tex` (Sec 5.2, Abstract, Sec 10)
  - `manuscript/ROUTE_IQ_CONTRIBUTIONS_AND_NOVELTY.md`
- **Previous Claim:**
  *"Theorem 1 (Campaign-Level Monotonic Non-Degradation): Let $R_{\text{QGAR}}$ be the routing campaign... Then $C(R_{\text{QGAR}}) \le C(R_{\text{spatial}}) + \epsilon$."*
- **Applied Replacement:**
  **"Proposition 1 (Non-Degradation via Algorithmic Route Certification Guardrail):**
  *Let $R_{\text{QGAR}}$ be the delivery campaign produced by ROUTE/IQ, incorporating the End-to-End Route Certification Guardrail that evaluates candidate routes against the classical spatial baseline. Then by algorithmic construction, for all valid CVRP instances $\mathcal{I} = (G, \mathcal{C}, c_0, Q, D)$:*
  $$C(R_{\text{QGAR}}) \le C(R_{\text{spatial}}) + \epsilon \quad (\epsilon = 10^{-4}\text{ km})$$"*
- **Justification:**
  Correctly clarifies that non-degradation is an algorithmic property guaranteed by the dual-evaluation acceptance-rejection fallback filter (`if dist_qaoa <= dist_spatial + 1e-4: accept else: fallback`), preventing misinterpretation as an intrinsic convergence theorem of QAOA.

---

### Correction C3: Clarification of Planar Crossing Regularizer Topology
- **Target Files:**
  - `manuscript/ROUTE_IQ_FULL_JOURNAL_MANUSCRIPT.md` (Sec 5.4, Sec 8.6, Sec 9.3)
  - `manuscript/ROUTE_IQ_FULL_JOURNAL_MANUSCRIPT.tex` (Sec 4.3, Sec 7.4, Sec 8.3)
- **Previous Claim:**
  Described crossing detection without specifying that it operates on straight-line customer coordinates.
- **Applied Replacement:**
  Added explicit note:
  > *"Note on Geometric Topology: Planar crossings are evaluated on the 2D Euclidean projection of customer geographic coordinates, serving as an empirical geometric inductive bias (demonstrating 96.4% empirical alignment) rather than full street-network centerline tracing. On directed street grids with one-way restrictions, physical road paths can occasionally require detour loops that straight-line Euclidean metrics do not capture (e.g., Trial 0, where avoiding a 2D Euclidean crossing caused a $+0.7\%$ detour)."*
- **Justification:**
  Accurately characterizes the 2D Euclidean coordinate proxy and transparently documents the Trial 0 counterexample.

---

### Correction M1: Reconcile Table 3 / Table 9 Statistical Discrepancies
- **Target Files:**
  - `manuscript/ROUTE_IQ_FULL_JOURNAL_MANUSCRIPT.md` (Table 9)
  - `manuscript/ROUTE_IQ_FULL_JOURNAL_MANUSCRIPT.tex` (Table III / Section 7)
- **Previous Values:**
  - QGAR vs. Phase H Effect Size: `+0.942`
  - QGAR vs. OR-Tools Mean Diff: `+45.241 km` (CI: `[+37.8, +52.6] km`)
  - QGAR vs. Clarke-Wright Mean Diff: `+45.022 km` (CI: `[+37.5, +52.4] km`)
  - QGAR vs. RB-QCD Mean Diff: `+26.852 km` (CI: `[+20.1, +33.8] km`)
- **Applied Replacement:**
  - QGAR vs. Phase H Effect Size: **`+0.848`** ($W^+ = 194.0, W^- = 16.0 \implies \frac{194 - 16}{210} = 0.8476$).
  - QGAR vs. OR-Tools Mean Diff: **`+25.684 km`** (95% CI: `[+18.34, +33.67] km`, $W = 0.0, p = 0.000002, r_B = -1.000$).
  - QGAR vs. Clarke-Wright Mean Diff: **`+26.157 km`** (95% CI: `[+18.05, +34.84] km`, $W = 0.0, p = 0.000002, r_B = -1.000$).
  - QGAR vs. RB-QCD Mean Diff: **`+17.260 km`** (95% CI: `[+11.23, +24.03] km`, $W = 3.0, p = 0.000010, r_B = -0.971$).
- **Justification:**
  Eliminates outdated placeholder values and restores 100% exact numerical agreement with raw benchmark records (`reproduction_statistical_tests.csv`).

---

### Correction M2: Explicit Declaration of Single-Node Local Execution (`local[*]`)
- **Target Files:**
  - `manuscript/ROUTE_IQ_FULL_JOURNAL_MANUSCRIPT.md` (Sec 6, Sec 10)
  - `manuscript/ROUTE_IQ_FULL_JOURNAL_MANUSCRIPT.tex` (Sec 4.1, Sec 6, Sec 9)
  - `manuscript/ROUTE_IQ_LIMITATIONS_AND_RESEARCH_INTEGRITY.md`
- **Applied Replacement:**
  Added explicit clarification that Spark was executed in local multithreaded mode (`master("local[*]")`) on an 8-core host, and that multi-node cluster network shuffle overhead remains future work.

---

### Correction M3: Bibliographic Additions
- **Target Files:**
  - `manuscript/ROUTE_IQ_REFERENCES.bib` (and root copy)
  - `manuscript/ROUTE_IQ_FULL_JOURNAL_MANUSCRIPT.md`
  - `manuscript/ROUTE_IQ_FULL_JOURNAL_MANUSCRIPT.tex`
- **Added Citations:**
  1. `lucas2014ising`: Andrew Lucas, "Ising formulations of many NP problems," *Frontiers in Physics*, 2014. (Cited in Sec 2.2 and Sec 5.1).
  2. `gillett1974sweep`: Billy E. Gillett and Leland R. Miller, "A Heuristic Algorithm for the Vehicle-Dispatch Problem," *Operations Research*, 1974. (Cited in Sec 1, Sec 2.1, and Sec 4.1).
  3. `voudouris1999guided`: Christos Voudouris and Edward Tsang, "Guided local search and its application to the traveling salesman problem," *European Journal of Operational Research*, 1999. (Cited in Sec 1, Sec 6, and Sec 7).

---

### Correction M4: Empirical QAOA Circuit Resources and Feasibility Reporting
- **Target Files:**
  - `manuscript/ROUTE_IQ_FULL_JOURNAL_MANUSCRIPT.md` (Sec 8.2)
  - `manuscript/ROUTE_IQ_FULL_JOURNAL_MANUSCRIPT.tex` (Sec 7.3)
- **Applied Replacement:**
  Incorporated raw subproblem telemetry from `qaoa_subproblem_ablation_results.csv`:
  - $m=3$ stops (9 qubits): Circuit depth = 15 gates, COBYLA iterations = 25, Hungarian projection required in 93.3% of shots, approximation ratio = 0.9079.
  - $m=4$ stops (16 qubits): Circuit depth = 24 gates, COBYLA iterations = 25, Hungarian projection required in 100.0% of shots, approximation ratio = 0.8435.

---

### Minor Corrections (m1–m3): Rhetorical and Metric Polishing
- Clarified that $-1.23\%$ represents the mean of instance percentage reductions, while $-1.34\%$ represents the pooled distance reduction across the 20 instances.
- Distinguished the $-4.55\%$ degradation of Phase H relative to the spatial sweep from the $-4.10\%$ ($5.78\text{ km}$) improvement of QGAR over Phase H.
- Removed hyperbolic language ("completely eliminates", "first framework").

---

*End of Phase N Correction Log.*

