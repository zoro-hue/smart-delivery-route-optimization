# PHASE AB DELIVERABLE 1: BASELINE AUDIT & RESEARCH CONTINUITY

## Project Information
- **Project:** ROUTE/IQ — Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing
- **Repository:** `D:\UROP\smart-delivery-route-optimization`
- **Supervisor:** Dr. Vishnu Prasad Verma, SRM University-AP
- **Branch:** `research/phase-ab-cooperative-optimization-engine`
- **Base Phase AA Commit:** `8d7622e`
- **Protected Main Baseline:** `a8eb849`

---

## 1. Executive Summary & Objective

Phase AB represents the synthesis and final engineering consolidation of the entire ROUTE/IQ research trajectory. Across Phases P through AA, the research team conducted systematic investigations into quantum-classical hybrid optimization for Capacitated Vehicle Routing Problems (CVRP).

The objective of Phase AB is **not** to manufacture artificial quantum speedups or claim an unsubstantiated quantum advantage. Instead, Phase AB builds a production-grade, scientifically defensible **Cooperative Optimization Engine** that synthesizes the validated strengths of each computational pillar:
1. **Big Data Pillar (Apache Spark 4.2.0):** Distributed customer order ingestion, schema validation, geospatial polar wedge clustering, and inter-cluster boundary subproblem extraction.
2. **Quantum Computing Pillar (QAOA / Qiskit 2.4.1):** High-interaction Ising bipartition candidate generation via Subspace XY-Mixer and Transverse Hamiltonians, coupled with hardware transpilation targets.
3. **Classical Optimization Foundation:** High-speed incumbent generation (Google OR-Tools), advanced metaheuristic candidate exploration (Kernighan-Lin, Tabu Search, Uniform Random Feasible), and multi-neighborhood tour refinement (Algorithmic Variable Neighborhood Descent).
4. **Adaptive Cooperative Controller:** Multi-Armed Bandit with feature-conditioned gating that dynamically routes subproblems based on interaction density, capacity slack, search stagnation, and remaining compute budget.
5. **Proposition 1 Centralized Guardrail:** Mathematical incumbent-preserving safety filter guaranteeing 100% capacity feasibility and 0.00% route degradation unconditionally.

---

## 2. Verification of Phase AA Scientific Baseline

The Phase AA investigation (`commit 8d7622e`) performed rigorous causal ablation and equal-budget benchmarking of simulated QAOA against classical partitioners. The key findings established:

1. **Statistical Equivalence in Route Quality:**
   Under strictly equal candidate budgets ($B = 512$ evaluations) and identical Algorithmic VND local search:
   - Multistart Kernighan-Lin + VND: **588.63 km** (accepted 46.7%, 30 ms)
   - Tabu Search + VND: **583.56 km** (accepted 63.3%, 45 ms)
   - Fast QAOA + VND: **593.18 km** (accepted 33.3%, 128 ms)
   - Paired t-test between QAOA and Multistart KL: $p = 0.5372$ ($p > 0.05$), Cohen's $d = 0.12$ (negligible).
   - Paired t-test between QAOA and Tabu Search: $p = 0.1841$ ($p > 0.05$).

2. **Classical Runtime Superiority:**
   Classical metaheuristics ran $2.57\times$ to $4.27\times$ faster than statevector-simulated QAOA per boundary subproblem.

3. **Causal Origin of Apparent Phase Z "Advantage":**
   Phase AA proved that the 20.0 km difference in Phase Z was an artifact of:
   - Unequal candidate sampling budgets (512 quantum samples vs single deterministic classical pass).
   - The classical fallback mechanism in Proposition 1 masking quantum infeasibility.
   - When given identical evaluation budgets, classical algorithms perform identically or superiorly to QAOA.

---

## 3. Scope and Research Integrity Guardrails

To preserve scientific rigor throughout Phase AB:
- **No Fabricated Claims:** Quantum computing is explicitly presented as an exploratory candidate generator, not a proven advantage mechanism.
- **Strict Budget Equality:** Every candidate generation strategy operates under identical sampling budgets and standardized interfaces.
- **Repository Safety:** The protected `main` branch (`a8eb849`), frontend UI, and backend API contracts (`backend/app/main.py`) remain completely untouched.
- **Canonical Dashboard Alignment:** All fleet metrics maintain conceptual alignment with the canonical four-tier dashboard baseline:
  - Phase 1 Baseline: **219.7 km**
  - Phase 2 Classical (OR-Tools): **218.2 km**
  - Phase 3 Classical + VND: **217.6 km**
  - Phase 4 Cooperative Multi-Pillar: **217.3 km**
