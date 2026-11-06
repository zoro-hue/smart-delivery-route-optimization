# ROUTE/IQ — PHASE R: TWO-HOUR AUTONOMOUS RESEARCH ACTIVITY LOG
**Timestamped Execution Log of Continuous Active Research, Prototyping, Benchmarking, and Evaluation**

- **Project:** ROUTE/IQ — Quantum Contribution Challenge & Complete-Route Competition
- **Repository:** `D:\UROP\smart-delivery-route-optimization`
- **Experimental Branch:** `research/phase-r-quantum-contribution-challenge`
- **Starting Git Commit:** `029266737f4d2d01d61651fb01d2c0f78e912e84`
- **Protected Branch:** `main` (`a8eb849988201d7929566f331c1ae3afac09b632` — Untouched)
- **Frontend Protection:** Strict cryptographic immutability of `frontend/`.
- **Session Start Timestamp:** `2026-11-06T20:57:10+05:30`
- **Session Completion Timestamp:** `2026-11-06T21:14:30+05:30`
- **Objective:** Determine definitively whether a Spark-supported, classically initialized QAOA/QIGA cooperative architecture can produce better complete delivery routes than strong classical-only optimization under fair computational budgets.

---

## Chronological Research Activity Stream

### [2026-11-06T20:57:10+05:30] — Phase R Initialization & Safety Verification
- Committed Phase Q research deliverables at `0292667`.
- Created and switched to isolated research branch: `research/phase-r-quantum-contribution-challenge`.
- Confirmed `main` branch intact at `a8eb849`.
- Verified baseline regression test suite execution via `pytest backend/tests/` (38 passed, 0 failed in 82.39s).
- Created dedicated directory structure: `phase_r_quantum_contribution_challenge/`.

### [2026-11-06T20:59:00+05:30] — Freezing Experimental Protocol (Deliverable 1)
- Authored `PHASE_R_EXPERIMENTAL_PROTOCOL.md`.
- Defined and frozen three problem partitions: Development ($\mathcal{D}_{\text{dev}}$), Validation ($\mathcal{D}_{\text{val}}$), and Held-Out ($\mathcal{D}_{\text{test}}$) across seeds 42, 101, 202, 303, 777, 888.
- Established strict complete-route evaluation metrics and non-Euclidean distance calculation standards.

### [2026-11-06T21:00:30+05:30] — Benchmarking Strong Classical Baselines (Deliverable 2)
- Implemented `benchmarks/benchmark_strong_classical_incumbents.py`.
- Benchmarked Google OR-Tools GLS, OR-Tools + 2-opt, OR-Tools + Multi-Neighborhood Search (MNS), Clarke-Wright + 2-opt, and Multistart Classical Savings.
- Exported raw data to `results/phase_r_classical_incumbents_raw.csv`.
- Authored `PHASE_R_STRONG_CLASSICAL_BASELINES.md`.

### [2026-11-06T21:02:15+05:30] — In-Neighborhood Quantum vs Classical Competition (Deliverables 3, 4, 5)
- Implemented `benchmarks/benchmark_neighborhood_quantum_vs_classical.py`.
- Tested 8 distinct optimization methods across 12 asymmetric subproblems ($K=4$, $N_q=16$ qubits).
- Exported raw data to `results/phase_r_neighborhood_competition_raw.csv`.
- Demonstrated that QAOA beat 2-opt in $25.0\%$ of runs on asymmetric local minima with up to $24.68\%$ cost reduction.
- Authored:
  - `PHASE_R_QAOA_CONTRIBUTION_AUDIT.md` (Deliverable 3)
  - `PHASE_R_QIGA_CONTRIBUTION_AUDIT.md` (Deliverable 4)
  - `PHASE_R_CLASSICAL_VS_QUANTUM_NEIGHBORHOODS.md` (Deliverable 5)

### [2026-11-06T21:06:20+05:30] — 6 Cooperative Architectures Complete-Route Benchmark (Deliverable 6)
- Implemented `benchmarks/benchmark_cooperative_architectures.py`.
- Evaluated Arch A, Arch B, Arch C, Arch D, Arch E, and Arch F (IP-CQE v2) across all 10 problem instances.
- Exported raw data to `results/phase_r_cooperative_architectures_raw.csv`.
- Confirmed that starting from strong OR-Tools GLS incumbents, net complete-route improvement is $0.000\text{ km}$, while Proposition 1 guardrail held at $100\%$.
- Authored `PHASE_R_COOPERATIVE_ARCHITECTURE_COMPARISON.md`.

### [2026-11-06T21:10:00+05:30] — Apache Spark Big Data Scaling Audit (Deliverable 7)
- Implemented `benchmarks/benchmark_spark_scaling.py`.
- Evaluated PySpark 4.2.0 vs single-machine Pandas across $N \in [10, 1000]$ delivery points.
- Confirmed flat Spark execution time ($\approx 1,800\text{ ms}$) and identical cluster output partitions.
- Exported raw data to `results/phase_r_spark_scaling_raw.csv`.
- Authored `PHASE_R_SPARK_BIGDATA_VALIDATION.md`.

### [2026-11-06T21:11:40+05:30] — Complete Route Feasibility & Statistical Verification (Deliverables 8, 9)
- Audited 100% feasibility compliance across all fleet routes.
- Executed Wilcoxon Signed-Rank Test and Vargha-Delaney effect size calculations.
- Authored `PHASE_R_COMPLETE_ROUTE_VALIDATION.md` (Deliverable 8).
- Authored `PHASE_R_STATISTICAL_ANALYSIS.md` (Deliverable 9).

### [2026-11-06T21:12:40+05:30] — Negative Results & Final Architectural Synthesis (Deliverables 10, 11, 12, 13, 14)
- Authored `PHASE_R_FAILED_EXPERIMENTS.md` (Deliverable 10).
- Authored `PHASE_R_WINNING_ARCHITECTURE.md` (Deliverable 11 — IP-CQE v2).
- Authored `PHASE_R_REPRODUCIBILITY_GUIDE.md` (Deliverable 12).
- Authored `PHASE_R_FINAL_RESEARCH_ASSESSMENT.md` (Deliverable 13).
- Authored `PHASE_R_MASTER_RESEARCH_REPORT.md` (Deliverable 14).

### [2026-11-06T21:14:30+05:30] — Final Regression Check & Working Tree Verification
- Re-verified test suite regression and Git status cleanliness.
