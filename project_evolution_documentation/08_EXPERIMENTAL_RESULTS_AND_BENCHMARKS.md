# 08 — COMPREHENSIVE EXPERIMENTAL RESULTS AND BENCHMARKS

**Project:** ROUTE/IQ — Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing  
**Institution:** SRM University-AP, Department of Computer Science and Engineering  
**Authors:** J. Jayanth, B. Kaivalya, P. Shyam Sai  
**Faculty Supervisor:** Dr. Vishnu Prasad Verma (`vishnu.v@srmap.edu.in`)  
**Git Baseline Commit (`main`):** `a8eb849`  
**Current Research Branch:** `research/journal-readiness` (Commit: `960dfdb`)  
**Target Journal:** *IEEE Transactions on Quantum Engineering*  

---

## 1. Experimental Methodology & Rigor

All experimental data in ROUTE/IQ are derived from reproducible benchmark scripts executing against authentic New York City geospatial datasets. The evaluation suite enforces:
1. **Paired Statistical Testing:** Exactly identical customer stop locations, parcel demands, and origin depots are evaluated across all comparative solvers within each trial.
2. **Non-Parametric Hypothesis Testing:** Two-tailed Wilcoxon signed-rank tests ($W, p$) are computed because route length differences across urban networks deviate from normal distributions.
3. **Effect Size Quantification:** Rank-biserial correlation ($r_B \in [-1.0, +1.0]$) quantifies the magnitude and consistency of paired improvements.
4. **Multiple Testing Correction:** Benjamini-Hochberg False Discovery Rate (FDR) adjustments $(\alpha = 0.05)$ ensure that reported significance is statistically sound.
5. **Bootstrap Confidence Intervals:** 95% confidence intervals are computed via 2,000 bootstrap resamples.

```
+---------------------------------------------------------------------------------------+
| RESEARCH CANDOR & EMPIRICAL INTEGRITY:                                                |
| 1. Google OR-Tools GLS produces significantly shorter routes than QGAR (-21.02%).     |
| 2. Clarke-Wright + 2-opt also outperforms QGAR in raw travel distance (-21.35%).      |
| 3. RB-QCD outperforms QGAR in raw travel distance (-14.77%).                          |
| 4. The research achievement of ROUTE/IQ is NOT classical superiority, but proving that |
|    QAOA variational guidance can be integrated into large-scale logistics workflows   |
|    with guaranteed non-degradation and statistically verified subproblem impact.      |
+---------------------------------------------------------------------------------------+
```

---

## 2. Chronological Experimental History (Phases 6 through N)

| Research Phase | Focus & Objective | Dataset & Scale | Primary Algorithms Evaluated | Key Findings & Metric Outcomes | Reproducibility Script |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Phase 6 / 6C** | Manhattan Journal Benchmark & Exact Validation | 15 synthetic instances ($N=10, 20$) on Manhattan OSM | OR-Tools, Clarke-Wright, Classical Solver, Early QAOA | Identified classical solver superiority; discovered that monolithic QUBO was unscalable for $N > 8$. | `backend/scripts/run_journal_benchmark.py` |
| **Phase G** | Dual-Pillar Verification & Performance Audit | 10 trials ($N=25, 50, 100$) | Spark Preprocessor + QAOA Subproblem Optimizer vs Ablation | Proved Spark batch partitioning scalability; confirmed QAOA subproblem improvement over random baseline. | `backend/scripts/run_dual_pillar_benchmark.py` |
| **Phase H** | Independent Reproducibility & Scaling Audit | Spark scaling up to 50k orders; 15 routing trials | Spark `local[*]` + Phase H Hybrid Pipeline | Spark partitioned 50k orders in 22.04s; reported 3.5–4.4% QAOA improvement, but identified potential degradation edge cases. | `backend/scripts/run_bigdata_scaling_audit.py` |
| **Phase I** | Quantum-Guided Adaptive Reconstruction (QGAR) | 20 paired trials ($N=25, 50, 100$) on NYC 5-Boroughs | QGAR vs Phase H vs Spatial Baseline vs OR-Tools | QGAR achieved $4.10\%$ distance reduction over Phase H and $-1.230\%$ vs Spatial Baseline; introduced crossing regularizer. | `backend/scripts/run_phase_i_qgar_benchmark.py` |
| **Phase J** | Independent Scientific Verification & Guardrail Audit | 20 paired trials | QGAR with Guardrail vs Spatial Baseline | Discovered Trial 0 crossing counterexample; certified End-to-End Route Certification Guardrail ($C_{\text{QGAR}} \le C_{\text{spatial}}$). | `phase_i_qgar_benchmark_raw.csv` |
| **Phase K** | Adversarial Audit & Quantum Attribution | Micro-clusters ($m=3, 4$) and fleet routing | QAOA with Hungarian Projection vs No-QAOA Ablation | Verified quantum attribution: QAOA improves micro-cluster tour quality; measured Hungarian projection rates (93.3% and 100%). | `backend/scripts/run_phase_k_quantum_attribution.py` |
| **Phase L** | Complete Journal Manuscript Preparation | Comprehensive dataset synthesis | All baseline & proposed models | Formulated IEEE LaTeX manuscript and structured academic documentation. | `ROUTE_IQ_FULL_JOURNAL_MANUSCRIPT.tex` |
| **Phase M** | Independent Critical Peer Review | Systematic manuscript & telemetry audit | Full system | Issued 13 prioritized corrections; identified Table 3/9 statistical discrepancy ($r_B = +0.848$ vs $1.00$). | `phase_m_review/` (9 audit reports) |
| **Phase N** | Manuscript Correction & Telemetry Harmonization | Reconciled telemetry from raw CSVs | Full system | Applied all 13 corrections; harmonized Markdown & LaTeX; verified 38/38 unit tests passing. | `phase_n_finalization/` (6 dossiers) |

---

## 3. Pillar 1: Big Data Scaling Benchmark (Apache Spark 4.2.0)

Executed via `backend/scripts/run_bigdata_scaling_audit.py` on workstation hardware (`local[*]`, OpenJDK 17, 8 GB JVM heap):

| Batch Size ($N$) | Number of Vehicles ($K$) | Total Processing Time (s) | Ingestion & Partitioning Throughput | Memory Footprint (JVM Heap) |
| :---: | :---: | :---: | :---: | :---: |
| **100** | 4 | 0.82 s | 121.9 orders/s | ~420 MB |
| **500** | 18 | 1.15 s | 434.8 orders/s | ~450 MB |
| **1,000** | 35 | 1.48 s | 675.7 orders/s | ~480 MB |
| **5,000** | 172 | 3.24 s | 1,543.2 orders/s | ~580 MB |
| **10,000** | 344 | 5.86 s | 1,706.5 orders/s | ~720 MB |
| **25,000** | 860 | 12.18 s | 2,052.5 orders/s | ~1,100 MB |
| **50,000** | 1,720 | **22.04 s** | **2,268.6 orders/s** | ~1,680 MB |

*Analysis:* Runtime scales near-linearly ($O(N \log N)$), processing 50,000 orders into 1,720 capacity-compliant routes in 22 seconds with zero memory overflow.

---

## 4. Pillar 2: Micro-Cluster QAOA Telemetry & Ablation

Telemetry extracted from `qaoa_subproblem_ablation_results.csv` ($p=1$, 1,024 shots on Qiskit Aer `AerSimulator`, COBYLA 25 iterations):

| Metric | $m=2$ Stops (4 Qubits) | $m=3$ Stops (9 Qubits) | $m=4$ Stops (16 Qubits) |
| :--- | :---: | :---: | :---: |
| **Circuit Depth** | 8 gates | **15 gates** | **24 gates** |
| **2-Qubit $XY$ Mixer Gates** | 4 `XXPlusYYGate` | 18 `XXPlusYYGate` | 36 `XXPlusYYGate` |
| **Variational Parameters** | 2 $(\gamma, \beta)$ | 2 $(\gamma, \beta)$ | 2 $(\gamma, \beta)$ |
| **COBYLA Optimization Iterations** | 15 | 25 | 25 |
| **Approximation Ratio ($E_{\text{QAOA}} / E_{\text{exact}}$)** | **0.9850** | **0.9079** | **0.8435** |
| **Raw Bitstring Feasibility Rate** | 57.9% | 6.7% | 0.0% |
| **Hungarian Projection Required** | 42.1% | **93.3%** | **100.0%** |
| **Feasible Tours After Projection** | **100.0%** | **100.0%** | **100.0%** |

*Analysis:* Hungarian projection is invoked in 93.3% of shots for $m=3$ and 100.0% for $m=4$. This demonstrates that QAOA at NISQ depth acts as an **energy-biased probability prior** rather than a direct discrete permutation generator.

---

## 5. Master Comparative Routing Benchmark (Table 3 / Table 9 Reconciled)

Comprehensive evaluation across **20 paired trials** ($N=25, 50, 100$ stops across Manhattan, Brooklyn, and Queens) from `phase_i_qgar_benchmark_raw.csv`. All comparisons measure **QGAR minus Baseline** (negative $\Delta$ indicates QGAR produces shorter travel distance):

| Comparative Baseline | Mean Baseline Distance (km) | Mean QGAR Distance (km) | Paired Diff $\Delta$ (km) | Paired % Reduction | 95% Bootstrap CI (km) | Wilcoxon Signed-Rank ($W, p$) | Rank-Biserial Effect Size ($r_B$) | Outcome (Wins / Losses / Ties) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Deterministic Spatial Baseline** | 154.340 km | 152.270 km | **-2.070 km** | **-1.230%** | $[-3.57, -0.91]$ km | $W = 105.0, p = 0.000491$ | $\mathbf{+1.000}$ | 14 Wins / 0 Losses / 6 Ties |
| **Phase H Hybrid Pipeline** | 158.051 km | 152.270 km | **-5.781 km** | **-4.10%** | $[-8.52, -3.02]$ km | $W = 194.0, p = 0.000161$ | $\mathbf{+0.848}$ | 19 Wins / 1 Loss / 0 Ties |
| **Google OR-Tools GLS** | 126.586 km | 152.270 km | **+25.684 km** | **+21.02%** | $[+18.34, +33.67]$ km | $W = 0.0, p = 0.000002$ | $\mathbf{-1.000}$ | 0 Wins / 20 Losses / 0 Ties |
| **Clarke-Wright + 2-opt** | 126.113 km | 152.270 km | **+26.157 km** | **+21.35%** | $[+18.05, +34.84]$ km | $W = 0.0, p = 0.000002$ | $\mathbf{-1.000}$ | 0 Wins / 20 Losses / 0 Ties |
| **RB-QCD Decomposition** | 135.010 km | 152.270 km | **+17.260 km** | **+14.77%** | $[+11.23, +24.03]$ km | $W = 3.0, p = 0.000010$ | $\mathbf{-0.971}$ | 1 Win / 19 Losses / 0 Ties |

### 5.1 Categorization of Values
- **Measured Values:** Raw distances (km), vehicle counts, execution times (s), Qiskit shot counts, and Hungarian invocation percentages directly logged in CSV experiment files.
- **Derived Values:** Mean paired differences, percentage reductions, bootstrap 95% confidence intervals, Wilcoxon test statistics ($W$), $p$-values, and rank-biserial correlations ($r_B$) computed via SciPy and NumPy.
- **Reported Values:** The tabulated summaries presented in manuscript Tables 3 and 9, now fully reconciled with raw data.
- **Unverified Claims (Rejected):** Earlier claims of quantum advantage, real-time Kafka streaming, and $r_B = +1.000$ for Phase H have been definitively excised.

---

## 6. Synthesis of Empirical Findings

1. **Non-Degradation Confirmed:** Across all 20 paired trials, QGAR achieved 14 wins and 6 ties (0 losses) against the Deterministic Spatial Baseline, confirming Proposition 1 ($C(R_{\text{QGAR}}) \le C(R_{\text{spatial}}) + 10^{-4}\text{ km}$).
2. **Phase H Superiority:** QGAR outperforms the earlier Phase H pipeline with $r_B = +0.848$ ($p = 0.000161$), delivering an average distance reduction of $5.78\text{ km}$ ($4.10\%$).
3. **Honest Classical Perspective:** Google OR-Tools GLS and Clarke-Wright + 2-opt significantly outperform QGAR by approximately $21\%$. This performance gap is expected given that classical metaheuristics optimize across the entire combinatorial space simultaneously, whereas ROUTE/IQ constrains quantum subproblems to $m \le 4$ stops to respect NISQ realities.
4. **Feasibility Adherence:** 100% of generated routes across all models strictly satisfied vehicle capacity constraints ($\sum q_i \le Q$) and visited all delivery locations exactly once.
