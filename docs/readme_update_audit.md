# Audit and Verification Report: Root README Overhaul to ROUTE/IQ-NextGen

**Audit Date:** November 21, 2026<br/>
**Audited Branch:** `research/next-generation-cooperative-engine`<br/>
**Target Document:** `README.md` (Root)<br/>
**Preserved Backup:** `docs/README_ORIGINAL_BACKUP.md` (Verified: 50,681 bytes)<br/>
**Verification Environment:** Python 3.14.2 (`C:\Python314\python.exe`) with PyTorch, Qiskit, OR-Tools, and PySpark

---

## 1. Overview of README Overhaul & Approved Corrections

The root `README.md` has been reviewed, rewritten, and rigorously aligned with the actual implemented codebase, test suite, and reproducible raw JSON benchmark evidence on branch `research/next-generation-cooperative-engine`.

All statements regarding the **ROUTE/IQ-NextGen** flagship cooperative optimization engine adhere to the 28 mandated sections, with strict scientific boundaries, precise mathematical definitions, transparent sample sizes, and honest disclosure of negative findings.

---

## 2. All 28 Required Sections Added or Revised

| # | Section Name in `README.md` | Verification Status | Primary Source Reference |
| :---: | :--- | :---: | :--- |
| **1** | Project Title and Overview | `VERIFIED IN SOURCE` | `backend/app/main.py`, `nextgen_cooperative_engine.py` |
| **2** | Problem Statement and Motivation | `VERIFIED IN SOURCE` | NP-hard CVRPTW formulations |
| **3** | Research Objectives and Contributions | `VERIFIED IN SOURCE` | UROP research package |
| **4** | Key Features | `VERIFIED IN SOURCE` | Full-stack platform capabilities |
| **5** | Overall System Architecture | `VERIFIED IN SOURCE` | Architecture layers & Mermaid flowchart |
| **6** | NextGen Cooperative Engine Architecture | `VERIFIED IN SOURCE` | `nextgen_cooperative_engine.py` & Mermaid sequence |
| **7** | Shared Candidate Pool / Blackboard | `VERIFIED IN SOURCE` | `backend/app/services/optimization/candidate_pool.py` |
| **8** | Adaptive UCB-1 Operator Controller | `VERIFIED IN SOURCE` | `backend/app/services/optimization/adaptive_mab.py` |
| **9** | Cooperative Optimization Operators (QAOA, QIGA, Tabu, Kernighan-Lin, Deep VND, ALNS, OR-Tools, CW, Polar) | `VERIFIED IN SOURCE` | `qaoa_cooperative_operator.py`, `qiga_cooperative_operator.py`, `neighborhood_search.py`, `classical_solver.py`, `construction_heuristics.py` |
| **10** | Vehicle-Condition-Aware Optimization | `VERIFIED IN SOURCE` | `backend/app/services/optimization/vehicle_condition_evaluator.py` |
| **11** | Big Data Processing with Apache Spark | `VERIFIED IN SOURCE` | `bigdata_pipeline.py`, `spark_routing_preprocessor.py` |
| **12** | Quantum Computing and Simulation Methodology | `VERIFIED IN SOURCE` | Qiskit Aer statevector simulation boundaries |
| **13** | Proposition 1: Monotonic Acceptance Guardrail | `VERIFIED IN SOURCE` | `nextgen_cooperative_engine.py` lines 516–530 |
| **14** | Dataset Descriptions and Provenance | `VERIFIED IN SOURCE` | `docs/benchmarks/nextgen_30_instances_report.json` |
| **15** | Technology Stack | `VERIFIED IN SOURCE` | `requirements.txt`, `package.json` |
| **16** | Experimental Methodology | `VERIFIED IN EXPERIMENTS` | Separation of 30-instance and 6-instance suites |
| **17** | Benchmark Results (30-Instance Suite) | `VERIFIED IN EXPERIMENTS` | `nextgen_30_instances_report.json` |
| **18** | Component Ablation Results (6-Instance Suite) | `VERIFIED IN EXPERIMENTS` | `scripts/benchmark_nextgen_results.json` |
| **19** | Frontend Features and Dashboard | `VERIFIED IN SOURCE` | React 18, Leaflet, `ResultsView.tsx`, `routeColors.ts` |
| **20** | Backend Architecture and API | `VERIFIED IN SOURCE` | `backend/app/api/endpoints/` |
| **21** | Installation and Local Setup | `VERIFIED IN TESTS` | Virtualenv, npm, dependency installation |
| **22** | Running the Application | `VERIFIED IN TESTS` | Uvicorn and Vite dev scripts |
| **23** | Running Tests and Benchmarks | `VERIFIED IN TESTS` | Pytest and benchmark script invocations |
| **24** | Deployment Architecture | `VERIFIED IN SOURCE` | `render.yaml`, Vercel config |
| **25** | Limitations and Research Boundaries | `VERIFIED IN SOURCE` | CPU simulation, Spark JVM, parameter assumptions |
| **26** | Future Work | `DOCUMENTED` | NISQ hardware, RL controller, dynamic topologies |
| **27** | Team, Supervisor and Institutional Information | `VERIFIED IN SOURCE` | SRM University-AP UROP research team |
| **28** | Publications and Citation | `VERIFIED IN SOURCE` | Manuscript in preparation (target: IEEE T-ITS); not yet submitted |

---

## 3. Files Inspected

1. **Source Code Files:**
   - `backend/app/services/optimization/nextgen_cooperative_engine.py` (lines 70–535)
   - `backend/app/services/optimization/candidate_pool.py` (CandidatePool, Jaccard diversity, Pareto admission)
   - `backend/app/services/optimization/adaptive_mab.py` (AdaptiveCooperativeController, UCB-1 with context bonus)
   - `backend/app/services/optimization/qaoa_cooperative_operator.py` (Qiskit Aer statevector simulation)
   - `backend/app/services/optimization/qiga_cooperative_operator.py` (Qubit evolutionary rotation gates)
   - `backend/app/services/optimization/neighborhood_search.py` (deep_vnd, alns_ruin_and_recreate)
   - `backend/app/services/optimization/classical_solver.py` (solve_ortools, solve_clarke_wright, solve_tabu_search)
   - `backend/app/services/optimization/construction_heuristics.py` (clarke_wright_savings_pool, spark_polar_sweep, regret_k_construction)
   - `backend/app/services/optimization/vehicle_condition_evaluator.py` (SoH decay, dynamic range, maintenance wear factor)
   - `backend/app/services/bigdata_pipeline.py` & `spark_routing_preprocessor.py` (PySpark BPR pipeline)
   - `frontend/src/pages/ResultsView.tsx` & `frontend/src/utils/routeColors.ts` (Distinct vehicle palette)

2. **Benchmark Raw JSON Files:**
   - `nextgen_30_instances_report.json` / `docs/benchmarks/nextgen_30_instances_report.json`
   - `baseline_30_instances_report.json` / `docs/benchmarks/baseline_30_instances_report.json`
   - `scripts/benchmark_nextgen_results.json`
   - `ablation_study_report.json`

3. **Academic Documents:**
   - `CONFERENCE/main.tex` & `CONFERENCE_PAPER.pdf`
   - `JOURNAL/main.tex` & `JOURNAL_PAPER.pdf`
   - `docs/final_journal_submission/ROUTE_IQ_COMPLETE_JOURNAL_PAPER.pdf`
   - Uploaded B.Tech Final Project Report (`media_1795279691967_3972873a.pdf`, page 53)

---

## 4. Benchmark Figures & Statistical Rigor Independently Verified

### 4.1 30-Instance Statistical Validation Suite
Cross-checked directly from `nextgen_30_instances_report.json`:
- **Total Instances:** 30 paired instances.
- **Feasibility:** 30 / 30 feasible solutions (100.0%).
- **Google OR-Tools Cumulative Distance:** $3,161.10\text{ km}$.
- **ROUTE/IQ-NextGen Cumulative Distance:** $3,134.23\text{ km}$.
- **Total Distance Savings:** $26.87\text{ km}$ ($0.85\%$ overall reduction).
- **Outcome Distribution:**
  - **Wins (NextGen strictly shorter):** 12 instances.
  - **Ties (Identical distance within $10^{-4}\text{ km}$):** 18 instances.
  - **Losses:** 0 instances (guaranteed by Proposition 1).
- **Mean Execution Runtime:**
  - Google OR-Tools: $506.2\text{ ms}$.
  - ROUTE/IQ-NextGen: $1,618.9\text{ ms}$.
- **Statistical Significance & Sample Size Disclosures:**
  - **Wilcoxon Signed-Rank Test on Non-Zero Pairs:** Evaluated on the **12 non-zero paired differences** (standard tie-dropping convention):
    $$W = 0.0, \quad p = 2^{-11} = 0.00048828 \quad (p < 0.001)$$
    (Across all 30 instances with Pratt tie handling: $W = 0.0, p = 0.000603$).
  - **Paired $t$-Test on Non-Zero Pairs:** Evaluated on the 12 non-zero winning pairs:
    $$t = -3.8801 \approx -3.89, \quad p = 0.00256$$
  - **Paired $t$-Test on Full Sample (30 Instances):** Evaluated across all 30 paired instances (including the 18 ties of $0.0\text{ km}$ delta):
    $$t = -2.9525, \quad p = 0.00619$$

### 4.2 Six-Instance NextGen Cooperative and Ablation Suite
Cross-checked directly from `scripts/benchmark_nextgen_results.json`:
- **Google OR-Tools Alone:** Mean Distance: $181.57\text{ km}$, Runtime: $516.1\text{ ms}$.
- **Full Proposed NextGen:** Mean Distance: $179.31\text{ km}$, Runtime: $1,219.2\text{ ms}$, Improvement vs. OR-Tools: $1.24\%$, $p = 0.1862$.
- **Baseline Cooperative Engine:** Mean Distance: $179.43\text{ km}$, Runtime: $1,604.0\text{ ms}$.
- **Runtime Reduction:** $(1,604.0 - 1,219.2) / 1,604.0 = 23.99\% \approx 24.0\%$ relative to Baseline Cooperative Engine.
- **Ablated Variants:**
  - `NextGen_No_QAOA`: $181.26\text{ km}$, $1,236.7\text{ ms}$, $p = 0.8004$.
  - `NextGen_No_QIGA`: $181.26\text{ km}$, $1,263.0\text{ ms}$, $p = 0.8004$.
  - `NextGen_No_Exchange`: $181.26\text{ km}$, $841.2\text{ ms}$, $p = 0.8004$.
  - `NextGen_No_MAB`: $181.26\text{ km}$, $1,044.0\text{ ms}$, $p = 0.8004$.

---

## 5. Approved Corrections Applied to Documentation

1. **Publication Status Clarified:**
   - Previous draft referred to the conference manuscript as "Submitted / Under Review".
   - **Correction Applied:** In accordance with repository evidence and page 53 of the academic report, Section 28 and citation blocks now accurately read:
     *"Manuscript in preparation (target venue: IEEE Transactions on Intelligent Transportation Systems); not yet submitted."*
2. **Maintenance Wear Modeling Precision:**
   - Previous draft described `wear_factor = 1.15` colloquially as a "15% range reduction".
   - **Correction Applied:** Section 10.2 now precisely specifies that `wear_factor = 1.15` multiplies `base_consumption_per_100km` and `cost_per_km_usd` when `maintenance_status == "service_recommended"`. This represents a **15% maintenance-related consumption and operating-cost penalty**. Because range is inversely proportional to consumption ($R \propto 1 / (1.15 \cdot c)$), this corresponds to an implied operational range reduction of approximately **13.04%** ($1 - 1/1.15 \approx 0.1304$).
3. **Statistical Sample Transparency:**
   - Previous draft presented $t = -3.89$ alongside 30-instance totals without detailing the tie-dropping subset.
   - **Correction Applied:** Section 17.1 now explicitly distinguishes between the 12 non-zero winning pairs ($t = -3.8801, p = 0.00256; W = 0.0, p = 0.000488$) and the full 30-instance paired sample ($t = -2.9525, p = 0.00619$).
4. **Six-Instance Ablation Limitations & Plateau Disclosure:**
   - **Correction Applied:** Section 18.2 explicitly discloses that per-instance ablation logs were not individually serialized to `benchmark_nextgen_results.json`, and the QAOA ablation hook in `scripts/benchmark_nextgen_cooperative_suite.py` line 169 contains a `pass` stub. The identical 181.26 km score across all 4 ablations is documented as an empirical plateau rather than proven independent convergence, and claims of causal necessity or proven synergy are explicitly disclaimed.
5. **Exact Cross-Platform Test Command:**
   - **Correction Applied:** Section 23.1 now provides the verified executing command:
     `$env:PYTHONPATH="backend"; python -m pytest backend/tests/test_nextgen_cooperative_engine.py backend/tests/test_vehicle_condition_optimization.py -v`
     and documents the exact verified result: **Exit code 0, 10 passed, 0 failed, 0 skipped in 8.71s**.

---

## 6. Legacy Telemetry Test Investigation: `test_cooperative_flagship_superiority.py`

During verification, running the entire test directory revealed that `backend/tests/test_cooperative_flagship_superiority.py` failed at line 111:
```python
telemetry = res_coop.get("cooperative_telemetry", {})
assert telemetry.get("proposition1_guaranteed") is True
assert "spark_mode" in telemetry  # <-- Fails here
```
### Forensic Assessment:
- **Optimization Assertions:** Passed completely (`coop_dist <= ort_dist + 1e-4`, `is_feasible == True`, `capacity_violations == 0`, `unserved_customers == 0`, `proposition1_guaranteed == True`).
- **Failure Cause:** In Phase AB, the legacy solver returned a dictionary key `'spark_mode'` inside `cooperative_telemetry`. NextGen updated the `cooperative_telemetry` dictionary schema to NextGen metrics (`candidate_pool_stats`, `adaptive_controller_stats`, `solution_origin`), exposing `'compute_type'` and `'spark_mode'` at the top-level response payload.
- **Maintenance Status:** This is a legacy schema incompatibility in an obsolete test file, NOT an optimization or algorithmic regression. Per project constraints, neither source code nor test files were modified; this issue is documented for separate test maintenance.

---

## 7. Git Branch and Working-Tree Safeguards

- **Active Branch:** `research/next-generation-cooperative-engine`
- **Tracked Modified Files:**
  - `README.md` (Updated with approved corrections)
  - `frontend/src/pages/ResultsView.tsx` (Pre-existing UI vehicle route color palette update)
  - `frontend/src/utils/routeColors.ts` (Pre-existing UI vehicle route color palette definitions)
- **Untracked Working-Tree Files:**
  - `docs/readme_update_audit.md` (This document)
  - `docs/README_ORIGINAL_BACKUP.md` (Original 50,681-byte backup)
  - Pre-existing research audit scripts (`scripts/audit_*.py`, `scripts/analyze_git_history.py`)
  - Pre-existing benchmark JSON result files (`nextgen_30_instances_report.json`, `baseline_30_instances_report.json`, `ablation_study_report.json`)
  - Pre-existing conference submission materials (`CONFERENCE/`, `CONFERENCE.zip`, `docs/final_conference_submission/`)
- **Safety Policy Confirmed:**
  - Zero commits created.
  - Zero pushes executed.
  - Zero branch resets, rebases, merges, or deletions.
  - Zero deployments triggered.
  - All unrelated research artifacts preserved intact.

---

## 8. NextGen Cooperative Optimization Engine Documentation Expansion Audit

**Audit Date:** November 22, 2026<br/>
**Audited Document:** `README.md` (Section 6 & Section 7)<br/>
**Verification Scope:** Comprehensive documentation of the NextGen Cooperative Optimization Engine architecture, cooperative mechanics, workflow diagrams, vehicle condition integration, Proposition 1 guardrail, big data/quantum boundaries, and verified experimental findings.

### 8.1 Added Documentation Subsections

The root `README.md` Section 6 was extensively expanded from a brief sequence diagram into a complete architectural reference containing seven dedicated subsections:

1. **Section 6.1 — Architectural Philosophy: What Makes the Engine Cooperative?**
   - Contrasts traditional winner-takes-all portfolio solvers and sequential pipelines against NextGen's blackboard-based cooperative architecture.
   - Explains in-memory candidate exchange via `CandidatePool`, continuous structural feature sharing across heterogeneous heuristics, adaptive effort routing via MAB, and the synergistic interplay between exploratory operators ("trap evaders") and exploitative operators ("neighborhood consolidators").
   - Discloses the single-threaded, deterministic sequential execution model (eliminating concurrency race conditions).

2. **Section 6.2 — End-to-End Architectural Dataflow and Control Loop:**
   - Added a comprehensive 7-phase Mermaid flowchart (`flowchart TD`) mapping raw problem inputs (stops, demands, fleet telemetry, PySpark BPR travel time matrices) through multi-start seeding, candidate blackboard, adaptive controller, operator pool, vehicle condition evaluation, admission filtering, final Deep VND polish, Proposition 1 guardrail, and telemetry assembly.
   - Preserved and synchronized the synchronous message-passing sequence diagram (`sequenceDiagram`).

3. **Section 6.3 — The Four Cooperating Pillars of NextGen:**
   - Structured ASCII architecture diagram and detailed technical specifications for:
     - *Pillar 1 (Blackboard):* `CandidatePool` with $M=16, k_{\mathrm{elite}}=4$, Jaccard edge-distance diversity metric, and duplicate rejection ($\Delta_{\mathrm{edge}} < 10^{-4}$).
     - *Pillar 2 (Adaptive MAB Controller):* `AdaptiveCooperativeController` implementing UCB-1 with state-dependent heuristic context bias ($\beta_{\mathrm{ctx}}=0.25, c_{\mathrm{expl}}=\sqrt{2}$) and four-pillar scalarized feedback reward ($0.50$ cost, $0.25$ feas, $0.20$ div, $0.05$ latency).
     - *Pillar 3 (Operator Suite):* 8 search heuristics split into exploratory (QAOA subproblem simulation, QIGA qubit rotation, Spark polar sweep, Clarke-Wright pool) and exploitative (Deep VND 5 neighborhoods, ALNS ruin-and-recreate, Tabu search 7-tenure inter-route swap, OR-Tools local repair).
     - *Pillar 4 (Vehicle Condition):* `VehicleConditionEvaluator` integrating battery SoH cycle decay ($\alpha_c = 1.2 \times 10^{-4}$), thermal stress ($\alpha_t = 3.5 \times 10^{-4}$), instantaneous usable energy $E_{\mathrm{usable}} = C_{\mathrm{rated}} \cdot \mathrm{SoH} \cdot \mathrm{SoC}$, operational range $R_{\mathrm{eff}}$, maintenance wear penalty (`wear_factor = 1.15` as a 15% consumption penalty implying ~13.04% range reduction), and multi-objective penalties ($\mu_{\mathrm{feas}} = 1000.0, \mu_{\mathrm{risk}} = 25.0$).

4. **Section 6.4 — Algorithmic Lifecycle of a Candidate Solution:**
   - Traces candidate generation, dimensionless multi-objective normalization against OR-Tools baseline values, blackboard admission filtering, tournament parent selection, iterative perturbation, incumbent polishing, and Proposition 1 certification.

5. **Section 6.5 — Certified Monotonic Non-Degradation (Proposition 1):**
   - Documents the centralized guardrail at lines 516–530 of `nextgen_cooperative_engine.py`, guaranteeing $D(S^*) \le D(S_{\mathrm{base}})$, zero feasibility regressions, and defining its boundary as an incumbent safety guardrail rather than a proof of global optimality.

6. **Section 6.6 — Hardware & Deployment Grounding:**
   - Grounding disclosures: single-node PySpark (`local[*]`) for offline/large batch processing; Qiskit Aer statevector CPU emulation; classical nature of QIGA; zero physical QPU deployment; zero quantum supremacy claim.

7. **Section 6.7 — Summary of Verified Experimental Findings:**
   - Clear side-by-side contrast between the 30-instance statistical superiority benchmark (12 wins, 18 ties, 0 losses, $0.85\%$ cumulative distance reduction, $W=0.0, p=0.000488$, $t=-2.9525, p=0.00619$) and the 6-instance ablation study ($1.24\%$ distance reduction, $p=0.1862$, $24.0\%$ runtime reduction vs baseline coop, candid disclosure of the 181.26 km plateau across 4 ablations and pass stub in QAOA hook).

8. **Section 7 Parameter Alignment:**
   - Corrected candidate pool default capacity and elitism to $M = 16, k_{\mathrm{elite}} = 4$, exactly matching `nextgen_cooperative_engine.py` and `candidate_pool.py`.

### 8.2 Code and Artifact Mapping

| Concept in README Section 6 | Implementation File | Verified Code Construct |
| :--- | :--- | :--- |
| Candidate Blackboard | `backend/app/services/optimization/candidate_pool.py` | `CandidatePool`, `select_parent`, `add_candidate`, `_compute_edge_jaccard_distance` |
| Adaptive Controller | `backend/app/services/optimization/adaptive_mab.py` | `AdaptiveCooperativeController`, `select_operator`, `update_reward` |
| Cooperative Engine | `backend/app/services/optimization/nextgen_cooperative_engine.py` | `NextGenCooperativeEngine.solve` (lines 70–535) |
| QAOA Subproblem Operator | `backend/app/services/optimization/qaoa_cooperative_operator.py` | `QAOACooperativeOperator.execute`, `AerSimulator`, `COBYLA` |
| QIGA Operator | `backend/app/services/optimization/qiga_cooperative_operator.py` | `QIGACooperativeOperator.execute`, qubit angle rotation |
| Deep VND (5 neighborhoods) | `backend/app/services/optimization/neighborhood_search.py` | `AdvancedNeighborhoodSearch.deep_vnd` |
| ALNS Ruin-and-Recreate | `backend/app/services/optimization/neighborhood_search.py` | `AdvancedNeighborhoodSearch.alns_ruin_and_recreate` |
| Vehicle Condition Evaluator | `backend/app/services/optimization/vehicle_condition_evaluator.py` | `VehicleConditionEvaluator.evaluate_candidate`, `wear_factor = 1.15` |
| Proposition 1 Guardrail | `backend/app/services/optimization/nextgen_cooperative_engine.py` | Lines 516–530 (`guardrail_status`) |
| Production Solver Entrypoint | `backend/app/services/optimization/cooperative_solver.py` | `CooperativeVRPSolver.solve` initializing `NextGenCooperativeEngine` |
