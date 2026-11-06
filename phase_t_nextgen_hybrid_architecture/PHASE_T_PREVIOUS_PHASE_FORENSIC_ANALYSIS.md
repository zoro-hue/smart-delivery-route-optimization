# Phase T Deliverable 2: Forensic Analysis of Previous Research Phases (P through S)

**Document:** `phase_t_nextgen_hybrid_architecture/PHASE_T_PREVIOUS_PHASE_FORENSIC_ANALYSIS.md`  
**Date:** 2026-11-06  
**Status:** Completed & Rigorously Verified  
**Branch:** `research/phase-t-nextgen-hybrid-architecture`

---

## 1. Evolution and Findings Across Prior Phases

| Research Phase | Focus & Central Objective | Key Findings & Discoveries | Critical Limitation Identified |
| :--- | :--- | :--- | :--- |
| **Phase P** | Autonomous exploration of 15 hybrid architectures. | Discovered IP-CQE (Incumbent-Preserving Cooperative Quantum Engine). Verified that warm-start XY-mixer QAOA outperformed standard transverse QAOA on suboptimal seeds. | Micro-improvements were evaluated in isolation; complete-route integration was unverified. |
| **Phase Q** | Independent scientific reproduction of IP-CQE v2. | Confirmed that QAOA improved suboptimal heuristic seeds by $6.8\%$ to $14.2\%$. Proved Proposition 1 Monotonic Guardrail prevented degradation. | Benchmark seeds were artificially degraded; performance against converged classical solvers was unmeasured. |
| **Phase R** | Quantum Contribution Challenge on complete routes. | Tested 6 cooperative architectures across 10 problem instances. Confirmed that net complete-route gain over OR-Tools GLS was $0.000\text{ km}$ ($p = 1.000$). However, noted QAOA beat 2-opt in $25.0\%$ of asymmetric neighborhoods. | Attributed the $25\%$ win rate to quantum advantage in asymmetric spaces without testing directed classical local search. |
| **Phase S** | Asymmetric Quantum Neighborhood Optimization. | Forensic audit proved the Phase R $25\%$ win rate was a **baseline artifact**: 2-opt reverses edges and suffers one-way penalties, whereas Classical Relocate & VND reach the exact optimum in **$100\%$ of cases in $0.10\text{ ms}$**. QAOA simulation takes $619\text{ ms}$ and column collisions occur in $68.85\%$ of raw shots. | Conclusively proved that **micro-route sequencing ($K \le 5$) is the WRONG problem for quantum computing**. |

---

## 2. Root Cause Analysis: The Three Fatal Bottlenecks

### Bottleneck 1: The Dimensional Mismatch of Micro-TSP
In all prior phases, quantum computing was tasked with ordering $K=4$ delivery stops. 
- Permutation space dimension: $|\mathcal{S}_4| = 4! = 24$ states.
- Exact Classical Enumeration evaluates all 24 permutations in **$0.084\text{ ms}$**.
- Classical Variable Neighborhood Descent (VND) finds the optimum in **$0.192\text{ ms}$**.
- Simulating a 16-qubit QAOA circuit requires **$618.9\text{ ms}$** and suffers from an average optimality gap of **$20.72\%$**.
- **Conclusion:** Small TSP tours are computationally trivial for classical computers. Deploying quantum computing here is mathematically wasteful.

### Bottleneck 2: Pre-Converged Classical Sub-Routes
When Google OR-Tools Guided Local Search (GLS) solves CVRP with a 5-second budget, it executes inter-route and intra-route exchanges across all vehicles. By the time it finishes, each individual vehicle tour is already a local minimum under Relocate, Swap, and 2-opt. Consequently, extracting an internal 4-customer subproblem and attempting to reorder it yields the identical sequence that OR-Tools already selected ($\Delta = 0.000\text{ km}$).

### Bottleneck 3: Rigid Cluster Boundaries & Missing Global Reallocation
Apache Spark partitioned customer points using static polar-angle bins. Once partitioned, vehicles were locked into their clusters. What was NEVER optimized by quantum was **Inter-Route Combinatorial Reallocation**—deciding which vehicle should service boundary customers when cluster overlaps occur.

---

## 3. Scientific Imperative for Phase T

To achieve genuine algorithmic utility, ROUTE/IQ must:
1. **Abandon micro-route TSP sequencing as the quantum optimization target.**
2. **Elevate Quantum Computing to Combinatorial Assignment & Multi-Vehicle Partition Coordination**, where the search space is exponential ($2^N$ or $M^N$) and classical combinatorial explosion occurs.
3. **Reposition Apache Spark** to dynamically identify boundary-overlap contention zones and generate quadratic assignment payloads.
4. **Retain Classical Solvers** for high-speed deterministic intra-route sequencing where they excel ($<1\text{ ms}$).

