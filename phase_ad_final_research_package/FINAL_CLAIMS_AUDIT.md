# ROUTE/IQ: FINAL SCIENTIFIC CLAIMS AUDIT & EVIDENCE MATRIX

**Project:** Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing  
**Institution:** SRM University-AP, Amaravati, Andhra Pradesh  
**Supervisor:** Dr. Vishnu Prasad Verma  
**Team:** J. Jayanth, B. Kaivalya, P. Shyam Sai  
**Scope:** Definitive Classification of All Major Project Claims with Evidence Links  

---

## 1. Classification Framework

Every research claim within the ROUTE/IQ project is classified into one of four standard scientific audit categories:
- **Verified:** Independently reproduced from committed source code and raw CSV/log evidence.
- **Partially Verified:** Component reproduced, but requires explicit qualification regarding assumptions or execution scope.
- **Unverified:** Insufficient raw data or computational resources to confirm the claim.
- **Contradicted:** Disproved by independent empirical evidence or codebase inspection.

---

## 2. Complete Scientific Claims Audit Matrix

| Claim ID | Formal Research Claim | Audit Status | Evidence Path & Reproduction Command | Required Qualification / Scientific Reality |
| :---: | :--- | :---: | :--- | :--- |
| **CLM-01** | **Quantum Advantage in Route Distance:** QAOA achieves superior complete fleet routes compared to strong classical optimization. | **CONTRADICTED** | `phase_ab_complete_benchmark_raw.csv`<br>`phase_ac_controller_audit_raw.csv`<br>`pytest phase_ac_independent_validation/tests/` | **Definitively Disproved:** Across 60 evaluations, Fast QAOA achieved 604.26 km, trailing Tabu Search (595.29 km) by 8.97 km ($p = 0.1020$). Tabu defeated QAOA in 14 of 30 instances (10 ties, 6 QAOA wins). There is zero empirical quantum advantage. |
| **CLM-02** | **Quantum Execution Speed:** QAOA accelerates fleet route solving compared to classical metaheuristics. | **CONTRADICTED** | `phase_ab_complete_benchmark_raw.csv`<br>`phase_ac_independent_validation/PHASE_AC_COMPLETE_BENCHMARK_REPRODUCTION.md` | **Definitively Disproved:** Simulated QAOA requires 644.85 ms, compared to 33.85 ms for Tabu Search. Classical search is **$19.05\times\text{ to }22.88\times$ faster** on classical CPU architectures. |
| **CLM-03** | **Execution on Physical Quantum QPUs:** QAOA was executed on real physical superconducting quantum hardware. | **CONTRADICTED / UNVERIFIED** | Codebase inspection (`candidate_generators.py`) | **Simulated Only:** No IBM Quantum job IDs, calibration data, or QPU execution timestamps exist. Qiskit circuits were transpiled to IBM Heavy-Hex graphs, but executed via classical CPU statevector simulation. |
| **CLM-04** | **Proposition 1 Feasibility & Non-Degradation:** Centralized guardrail guarantees 100% capacity feasibility and 0.00% route degradation. | **VERIFIED** | `proposition1_guardrail.py`<br>`phase_ac_independent_validation/tests/test_guardrail_adversarial.py` | **100% Verified:** Guardrail passed all 11 adversarial stress tests (0 failures, 0 bypasses) and maintained 0 violations across 240 benchmark evaluations. Holds conditionally on a feasible initial incumbent. |
| **CLM-05** | **High Quantum Candidate Rejection Rate:** Up to 70% of QAOA candidate bipartitions degrade route quality and are rejected by Proposition 1. | **VERIFIED** | `phase_ab_complete_benchmark_raw.csv`<br>`phase_ac_independent_validation/PHASE_AC_QUANTUM_CONTRIBUTION_AUDIT.md` | **100% Verified:** 21 of 30 QAOA candidates (70.0%) were rejected in Phase AB; 15 of 30 (50.0%) were rejected in Phase AC. Pooled rejection rate is 60.0%. QAOA frequently degrades classical incumbents. |
| **CLM-06** | **Subspace XY-Mixer Feasibility:** XY-Mixer elevates initial candidate capacity feasibility from 41.2% to 89.5%. | **VERIFIED** | `candidate_generators.py`<br>`phase_ab_cooperative_optimization_engine/PHASE_AB_QUANTUM_ENGINE.md` | **100% Verified:** Conserving total Hamming weight restricts quantum state evolution strictly to balanced bipartition subspaces, substantially boosting capacity compliance. |
| **CLM-07** | **Spark 100,000-Stop Boundary Reduction:** Spark reduces 100,000 delivery orders to 16 boundary customers in under 4 seconds (99.984% reduction). | **PARTIALLY VERIFIED** | `spark_preprocessor.py`<br>`phase_ac_spark_scalability_reproduced.csv`<br>`python benchmarks/reproduce_spark_scalability.py` | **Single-Machine Qualification:** Verified at 3.37s on single-machine `local[*]`, NOT on a multi-node physical cluster. Spark and in-memory NumPy extracted 100% identical boundary stops. NumPy is faster on single-machine RAM. |
| **CLM-08** | **Spark Distributed Multi-Node Scaling:** Spark demonstrated linear speedup across a multi-node distributed cluster. | **CONTRADICTED / UNVERIFIED** | `cluster/docker-compose.yml`<br>`benchmark_spark_scalability_consolidation.py` | **Not Deployed:** Docker Compose cluster configuration was written, but benchmarks were executed exclusively in single-machine `local[*]` mode. Multi-node cluster scaling was not performed. |
| **CLM-09** | **Algorithmic VND Primary Optimization Driver:** 4-neighborhood VND delivers the largest route reduction in the entire pipeline. | **VERIFIED** | `classical_engine.py`<br>`phase_ab_complete_benchmark_raw.csv` | **100% Verified:** Applying VND to initial greedy routing slashes distance from 1,307.16 km to 621.45 km (-52.46% / 685.71 km cut) in 8.27 ms. VND is the true workhorse of the system. |
| **CLM-10** | **Tabu Search Superiority:** Tabu Search + VND is the highest-performing standalone optimization configuration. | **VERIFIED** | `phase_ab_complete_benchmark_raw.csv`<br>`phase_ac_controller_audit_raw.csv` | **100% Verified:** Achieved 595.45 km (33.85 ms, 60.0% acceptance), outperforming all other standalone generators (KL, Random, QAOA). |
| **CLM-11** | **Adaptive Controller Performance:** Multi-Armed Bandit achieves near-optimal distance with superior operational flexibility. | **PARTIALLY VERIFIED** | `adaptive_controller.py`<br>`phase_ab_complete_benchmark_raw.csv`<br>`phase_ac_controller_audit_raw.csv` | **Dispatch Corrected:** Controller achieved 597.44 km at 34.87 ms (63.3% acceptance). Narrative report stated 19 Tabu / 1 QAOA, but raw CSV had 26 Tabu / 0 QAOA due to constant slack ($\sigma \le 0.15$). Held-out audit with variable slack verified mixed dispatches. Zero data leakage confirmed. |
| **CLM-12** | **Original Config A "OR-Tools Alone" Baseline:** Initial route of 1,307.16 km at 0.04 ms represents Google OR-Tools. | **CONTRADICTED** | `classical_engine.py`<br>`generate_ortools_incumbent()` | **Measurement Artifact Discovered:** Code executes a sequential list slice (`ta = 1..half`, `tb = half+1..N`), not Google OR-Tools. Re-labeled "Trivial Sequential Incumbent". True optimization baseline is Config B (OR-Tools + VND: 621.45 km). |
| **CLM-13** | **Live Production API Integration:** The Cooperative Optimization Engine is deployed and live in the FastAPI/React application. | **CONTRADICTED** | `backend/app/main.py`<br>`frontend/src/` | **Decoupled Research Package:** `phase_ab/` and `phase_ac/` are self-contained standalone research packages. They are NOT imported by `backend/app/main.py`. This intentionally preserved the protected `main` baseline (`a8eb849`). |
| **CLM-14** | **100% Deterministic Reproducibility:** Every reported number in the raw CSVs can be reproduced bit-for-bit from source. | **VERIFIED** | `phase_ac_independent_validation/benchmarks/reproduce_complete_benchmark.py` | **100% Verified:** Re-running the 240 benchmark evaluations yielded a maximum deviation of $0.000000\text{ km}$. All 57 tests pass cleanly. |

---

## 3. Summary of Narrative Consistency

All deliverables in Phase AD (`ROUTE_IQ_FINAL_RESEARCH_PAPER.md`, `SUPERVISOR_BRIEFING.md`, `ROUTE_IQ_FINAL_PRESENTATION.md`, and `VIVA_QUESTIONS_AND_ANSWERS.md`) strictly adhere to the audited classifications above. No unsubstantiated claims of quantum advantage or multi-node cluster scaling are made anywhere in this package.
