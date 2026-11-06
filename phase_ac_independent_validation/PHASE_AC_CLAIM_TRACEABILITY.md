# PHASE AC DELIVERABLE 3: CLAIM TRACEABILITY MATRIX

## Project Information
- **Project:** ROUTE/IQ — Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing
- **Institution:** SRM University-AP | **Supervisor:** Dr. Vishnu Prasad Verma
- **Audit Branch:** `research/phase-ac-independent-validation`

---

## 1. Traceability Methodology

Every headline claim in the Phase AB Master Report has been traced to its originating source function, raw experimental data row, reproduction command, and assigned an independent validation label:
- **Verified:** Independently reproduced from source and raw evidence.
- **Partially Verified:** Some components reproduced, but important assumptions or labeling discrepancies remain.
- **Unverified:** Insufficient evidence or unavailable reproduction.
- **Contradicted:** Independent evidence disagrees with the claim.

---

## 2. Complete Traceability Table

| Claim # | Phase AB Claim | Source File & Function | Raw Evidence File | Reproduction Command | Independent Status | Technical Audit Notes |
| :---: | :--- | :--- | :--- | :--- | :---: | :--- |
| **C1** | Config A achieves 1,307.16 km at 0.04 ms latency | `classical_engine.py`<br>`generate_ortools_incumbent()` | `phase_ab_complete_benchmark_raw.csv`<br>(Rows 2, 10, 18, ...) | `python benchmarks/benchmark_complete_system.py` | **Partially Verified** | **Measurement Artifact Discovered:** The function is named `generate_ortools_incumbent`, but its code performs a trivial index split (`ta = 1..half`, `tb = half+1..N`). It does not invoke OR-Tools. The 0.04 ms latency is array slicing, and 1,307 km is sequential coordinate routing. |
| **C2** | Config B (OR-Tools + VND) slashes distance to 621.45 km (-52.46%) in 8.27 ms | `classical_engine.py`<br>`refine_with_vnd()` | `phase_ab_complete_benchmark_raw.csv`<br>(Rows 3, 11, 19, ...) | `python benchmarks/benchmark_complete_system.py` | **Verified** | Verified identical: 621.45 km, 8.27 ms. 4-neighborhood VND successfully untangles greedy ordering. |
| **C3** | Config C (Single KL) achieves 603.72 km at 19.90 ms | `candidate_generators.py`<br>`KernighanLinGenerator.generate()` | `phase_ab_complete_benchmark_raw.csv`<br>(Rows 4, 12, 20, ...) | `python benchmarks/benchmark_complete_system.py` | **Verified** | Verified identical: 603.72 km, 19.90 ms. Acceptance rate was 14/30 (46.7%), slightly higher than reported 40.0%. |
| **C4** | Config D (Tabu Search) achieves 595.45 km at 33.85 ms with 60% acceptance | `candidate_generators.py`<br>`TabuSearchGenerator.generate()` | `phase_ab_complete_benchmark_raw.csv`<br>(Rows 5, 13, 21, ...) | `python benchmarks/benchmark_complete_system.py` | **Verified** | Verified identical: 595.45 km, 33.85 ms, 18/30 accepted (60.0%). Highest route reduction of any standalone generator. |
| **C5** | Config E (Random 512) achieves 602.90 km at 53.00 ms | `candidate_generators.py`<br>`UniformRandomGenerator.generate()` | `phase_ab_complete_benchmark_raw.csv`<br>(Rows 6, 14, 22, ...) | `python benchmarks/benchmark_complete_system.py` | **Verified** | Verified identical: 602.90 km, 53.00 ms, 14/30 accepted (46.7%). Uniform random sampling nearly matches QAOA. |
| **C6** | Config F (Fast QAOA) achieves 606.36 km at 644.85 ms with 30% acceptance | `candidate_generators.py`<br>`QAOACandidateGenerator.generate()` | `phase_ab_complete_benchmark_raw.csv`<br>(Rows 7, 15, 23, ...) | `python benchmarks/benchmark_complete_system.py` | **Verified** | Verified identical: 606.36 km, 644.85 ms, 9/30 accepted (30.0%). 70% of QAOA candidates were rejected by Proposition 1. |
| **C7** | Config G (Adaptive Controller) achieves 597.44 km at 34.87 ms with 63.3% acceptance | `adaptive_controller.py`<br>`select_strategy()` | `phase_ab_complete_benchmark_raw.csv`<br>(Rows 8, 16, 24, ...) | `python benchmarks/benchmark_complete_system.py` | **Partially Verified** | Distance (597.44 km), latency (34.87 ms), and acceptance (19/30 = 63.3%) verified. However, **dispatch narrative differed**: CSV contains 26 Tabu, 2 MSKL, 2 Random, 0 QAOA, whereas report narrative stated 19, 6, 4, 1. |
| **C8** | Config H (Spark Engine) achieves 599.68 km at 504.00 ms | `spark_preprocessor.py`<br>`cooperative_engine.py` | `phase_ab_complete_benchmark_raw.csv`<br>(Rows 9, 17, 25, ...) | `python benchmarks/benchmark_complete_system.py` | **Verified** | Distance (599.68 km) and acceptance (18/30 = 60.0%) verified. Latency includes PySpark DataFrame polar projection. |
| **C9** | Spark 100,000 stops reduced to 16 boundary customers in 837.90 ms | `spark_preprocessor.py`<br>`partition_fleet_workload()` | `phase_ab_spark_scalability_raw.csv` | `python benchmarks/benchmark_spark_scalability_consolidation.py` | **Partially Verified** | **Hardware Scope Downgrade:** Execution verified on single-machine `local[*]` (3.37s in independent test), NOT a multi-node cluster. Semantic equivalence between Spark and NumPy verified (100% boundary customer set identity). |
| **C10** | Proposition 1 guarantees 100% capacity feasibility and 0.00% route degradation | `proposition1_guardrail.py`<br>`validate_and_filter()` | `test_guardrail_adversarial.py` (11 test cases) | `pytest test_guardrail_adversarial.py` | **Verified** | Verified across all 240 benchmark evaluations (0 violations) and all 11 adversarial edge cases. |
| **C11** | No quantum advantage demonstrated; classical metaheuristics are 19.0x faster | `candidate_generators.py`<br>`cooperative_engine.py` | `phase_ac_controller_audit_raw.csv` | `python benchmarks/audit_adaptive_controller.py` | **Verified** | Rigorously verified: QAOA trails Tabu Search by 10.91 km ($p = 0.1020$), and runs 19.05x slower ($644.85\text{ ms}$ vs $33.85\text{ ms}$). |
| **C12** | Complete integration into production REST API | `backend/app/main.py` | Codebase call graph inspection | `Get-ChildItem backend/app -Pattern phase_ab` | **Contradicted** | Phase AB is a standalone research prototype. It is NOT imported into `backend/app/main.py` or exposed via live API routes. |
