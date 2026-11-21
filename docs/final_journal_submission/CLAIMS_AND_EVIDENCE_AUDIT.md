# Claims and Evidence Audit Matrix

**Project:** ROUTE/IQ: Intelligent Delivery Route Optimization Using Hybrid Big Data, Quantum Computing, and Cooperative Vehicle Fleet Optimization  
**Institutional Affiliation:** Department of Computer Science and Engineering, SRM University-AP, Amaravati, Andhra Pradesh, India  
**Authors:** J. Jayanth, B. Kaivalya, P. Shyam Sai (Undergraduate Research Scholars)  
**Faculty Research Supervisor:** Dr. Vishnu Prasad Verma  
**Date:** November 21, 2026  

---

## Forensic Traceability Matrix

Every scientific claim made in the ROUTE/IQ journal paper is verified against its exact implementation file, code line numbers, and experimental records.

| Scientific Claim | Implementation Source File | Function / Class | Verification Evidence & Test Record |
| :--- | :--- | :--- | :--- |
| **Claim 1: HFVRP-VC Usable Battery Capacity & Range** | `backend/app/services/optimization/vehicle_condition_evaluator.py` | `evaluate_vehicle_condition()` | Lines 72–115: Computes $B_{	ext{usable}} = B_{	ext{nom}} \cdot 	ext{SoH}$, enforces $R_k$ range boundaries, and applies 15% wear multiplier. Verified across all EV dispatches with 100% feasibility. |
| **Claim 2: Shared Candidate Blackboard & Jaccard Diversity** | `backend/app/services/optimization/candidate_pool.py` | `CandidatePool`, `edge_jaccard_distance()` | Lines 30–120: Maintains pool $M=16$, elite $k=4$, and evaluates $	ext{Dist}(S_a, S_b) = 1 - rac{\|E_a \cap E_b\|}{\|E_a \cup E_b\|}$. Redundant candidates rejected ($	ext{Dist} < 10^{-4}$). |
| **Claim 3: Contextual MAB UCB-1 Operator Selection** | `backend/app/services/optimization/adaptive_mab.py` | `AdaptiveContextualMAB.select_operator()` | Lines 45–98: Observes state vector $(N, K, H, \mathcal{D}, \sigma)$ and balances exploration/exploitation via UCB-1. Verified to reduce latency by 24.0% ($1219.2	ext{ ms}$ vs $1604.0	ext{ ms}$). |
| **Claim 4: 4-Pillar Multi-Objective Feedback Reward** | `backend/app/services/optimization/adaptive_mab.py` | `compute_reward()` | Lines 110–145: Implements $R(o) = 0.5\Delta + 0.25\mathbb{I}_{	ext{feas}} + 0.2	ext{Div} - 0.05(t/t_{	ext{budget}})$, penalizing runtime and rewarding diversity. |
| **Claim 5: Simulated QAOA Subproblem Operator** | `backend/app/services/optimization/qaoa_cooperative_operator.py` | `QAOACooperativeOperator.solve_subproblem()` | Lines 50–165: Extracts boundary conflict stops ($K_{	ext{sub}} \le 8$), executes depth $p=1$ statevector circuit via Qiskit Aer, and returns candidate to pool. |
| **Claim 6: QIGA Rotation Gate Mutation** | `backend/app/services/optimization/qiga_cooperative_operator.py` | `QIGACooperativeOperator.mutate()` | Lines 40–120: Represents stops via quantum probability amplitudes $|\psi_iangle$ and applies dynamic rotation gates $U(\Delta 	heta)$ directed toward elite incumbent. |
| **Claim 7: Proposition 1 Certified Non-Degradation** | `backend/app/services/optimization/nextgen_cooperative_engine.py` | `NextGenCooperativeEngine.run_cooperative_search()` | Lines 180–215: Centralized Proposition 1 Guardrail asserts $\mathcal{D}(S_{	ext{final}}) \le \mathcal{D}(S_{	ext{ortools}}) + 10^{-4}$. Fallback executed if candidate degrades. 100% pass rate. |
| **Claim 8: Mean Distance Reduction ($-1.24\%$)** | `scripts/benchmark_nextgen_results.json` | Benchmark suite summary | 6 instances, 9 configurations: Baseline OR-Tools $181.57	ext{ km}$; Proposed Next-Gen $179.31	ext{ km}$ ($-1.24\%$). $N=30$ node instance achieves $250.76	ext{ km}$ vs $258.95	ext{ km}$ ($-3.16\%$). |
| **Claim 9: Full Production API Integration** | `backend/app/services/optimization/cooperative_solver.py` | `CooperativeVRPBackend.solve()` | Production integration with provenance logging, telemetry, and backward-compatible REST API response schemas. |
