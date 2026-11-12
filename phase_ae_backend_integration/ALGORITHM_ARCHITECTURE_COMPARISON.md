# ROUTE/IQ — ALGORITHM ARCHITECTURE COMPARISON
**Detailed Algorithmic Mechanics: Independent Baselines vs Cooperative Search**
**Repository:** `D:\UROP\smart-delivery-route-optimization`  
**Current Branch:** `research/phase-ae-backend-integration`  
**Baseline Main:** `a8eb849988201d7929566f331c1ae3afac09b632`

---

## 1. Algorithmic Paradigm Shift: Siloed Execution vs Cooperative Search

The fundamental difference between the original ROUTE/IQ implementation and the Phase AE architecture lies in **how algorithms interact**:

- **Previous Baseline Paradigm (Siloed Execution):**
  Algorithms ran in complete isolation. The user selected a solver (e.g. OR-Tools or QAOA), the backend executed that solver on the input customer stops, and returned whatever route was produced. QAOA was limited to 8 nodes, dropping any remaining stops without mechanism for reintegration.
- **Current Phase AE Paradigm (Cooperative Search with Deterministic Guardrails):**
  ROUTE/IQ implements a **two-tier execution architecture**:
  1. *Independent Execution Tier:* All 8 solvers can still run independently in parallel via `ThreadPoolExecutor` for fair, unbiased benchmarking.
  2. *Cooperative Execution Tier (ROUTE/IQ Cooperative Engine):* Solvers do not operate in silos; they operate cooperatively within a closed feedback loop governed by an adaptive controller, local refinement filters, deterministic coverage repair, and a non-degradation theorem.

---

## 2. Step-by-Step Cooperative Execution Workflow

When the ROUTE/IQ Cooperative Engine is executed (`algorithm = "routeiq_cooperative"`), the backend executes the following algorithmic steps:

```
[Input Customer Stops (N) + Depot (0)]
                 │
                 ▼
     [1. Big Data Preprocessor (Spark 4.2.0)]
     - Centroid Polar-Angle Sorting: theta_i = atan2(y_i - y0, x_i - x0)
     - Contiguous Wedge Cuts into K Clusters (P_1, ..., P_K)
     - Boundary Interface Extraction: B_k = boundary vertices at cluster cuts
                 │
                 ▼
     [2. Classical Incumbent Generation (OR-Tools CVRP)]
     - High-speed Guided Local Search (sub-second limit)
     - Initial full-fleet incumbent: S_incumbent
     - Guaranteed 100% stop coverage (R == I)
     - Initial fleet cost: C(S_incumbent)
                 │
                 ▼
     [3. Adaptive Solver Controller (MAB UCB-1)]
     - Evaluates Arm Scores: UCB_a = Q(a) + c * sqrt(ln(t) / N(a))
     - Selects Candidate Generator for boundary vertices B:
       ├── Arm 1: QAOA Variational Circuit (Qiskit Statevector)
       ├── Arm 2: Tabu Search (Short-term memory vertex swaps)
       ├── Arm 3: Kernighan-Lin (2-way partition swap)
       └── Arm 4: Random Walk (Stochastic boundary permutation)
                 │
                 ▼
     [4. Candidate Re-ordering & Splicing]
     - Candidate permutation pi replaces boundary sequence in S_incumbent
     - Produces perturbed fleet candidate: S_candidate
                 │
                 ▼
     [5. Variable Neighborhood Descent (VND) Refinement]
     - Neighborhood 1: Intra-route 2-opt edge inversions
     - Neighborhood 2: Inter-route customer relocations
     - Neighborhood 3: Inter-route customer swaps
     - Locally optimized candidate: S_refined
                 │
                 ▼
     [6. Deterministic Feasibility & Coverage Repair (R == I)]
     - Verifies Universal Coverage Invariant: R == I
     - If any stops were dropped by candidate generator:
       -> Deterministic cheapest capacity-aware insertion places them into fleet
     - Preserves user-specified vehicle capacities strictly
                 │
                 ▼
     [7. Proposition 1 Non-Degradation Guardrail]
     - Evaluates: Is C(S_refined) < C(S_incumbent) AND Feasible(S_refined)?
       ├── YES -> Accept: S_coop = S_refined (Improvement realized)
       │          Update MAB Reward: r = C(S_incumbent) - C(S_refined) > 0
       └── NO  -> Reject: S_coop = S_incumbent (Rollback to Incumbent)
                  Update MAB Reward: r = 0 (No penalty transferred to user)
                 │
                 ▼
     [8. Road Network Snapping & Waypoint Reconstruction]
     - Snaps all stops to OSM Manhattan road graph (54,128 nodes) via cache
     - Reconstructs turn-by-turn driving polylines via Dijkstra
                 │
                 ▼
     [9. Process Resource Profiling & Telemetry Return]
     - Collects psutil RSS, tracemalloc heap delta/peak, and CPU process time
     - Packages telemetry and returns validated JSON response to frontend
```

---

## 3. What Happens Under Specific Solver Selection?

### Case A: QAOA Candidate Generation
1. The boundary extraction module identifies boundary vertices between adjacent vehicle clusters (e.g. vertices at the interface between Route 1 and Route 2).
2. The boundary vertices ($|B| \le 8$) are formulated into a quadratic unconstrained binary optimization (QUBO) problem.
3. Cost Hamiltonian $H_C$ encodes the road distance matrix between boundary nodes.
4. An XY mixer Hamiltonian preserves the constraint that each position in the boundary sequence is occupied by exactly one customer.
5. Qiskit 2.4.1 statevector simulator executes parameterized variational ansatz with depth $p=1$ or $p=2$.
6. Optimal measurement bitstrings are decoded into boundary sequence permutations.
7. The permutation is spliced into the fleet routes, refined via VND, repaired for $100\%$ customer coverage, and passed to Proposition 1.

### Case B: Tabu Search Candidate Generation
1. Tabu Search operates on boundary vertices using 2-opt edge swap moves.
2. A short-term recency-based tabu tenure prevents reversing recently swapped edges for $\theta$ iterations.
3. Aspiration criteria allow a tabu move if it yields a boundary cost strictly better than the current best.
4. Produces a candidate permutation $\pi_{\text{tabu}}$ that competes directly with QAOA under the MAB controller.

### Case C: Variable Neighborhood Descent (VND) Refinement
1. Raw outputs from stochastic, heuristic, or quantum generators often contain minor local defects (e.g. self-intersecting loops between neighboring nodes).
2. VND deterministically tests three neighborhood operators in strict succession:
   - $N_1$: 2-Opt (edge inversions within each route).
   - $N_2$: Relocation (moving a single customer to an alternate insertion point).
   - $N_3$: Swap (exchanging two customers between routes).
3. If an improvement is found in $N_k$, VND loops back to $N_1$; it terminates only when a local minimum across all three neighborhoods is reached.

### Case D: Deterministic Feasibility Repair & Invariant Enforcement ($R == I$)
1. If a candidate generator drops customer stops (e.g. QAOA optimizing only an 8-qubit boundary subset), the repair operator identifies the missing set $M = I \setminus R$.
2. For each missing stop $u \in M$, it computes the marginal insertion cost across all vehicle routes and positions:
   $$\Delta c = d(i, u) + d(u, j) - d(i, j)$$
3. Priority 1: Capacity-feasible insertion ($L_k + d_u \le Q_k$) with minimal $\Delta c$.
4. Priority 2: Minimal $\Delta c$ if total demand exceeds fleet capacity.
5. Inaccessible stops ($d = \infty$) are **not** inserted, and are reported honestly as unserved.
6. User-specified vehicle capacities are **never** silently inflated.

---

## 4. Why This Differs from Simply Running Algorithms in Parallel

A common naive baseline is "algorithm racing" (running OR-Tools, Clarke-Wright, and QAOA in parallel and picking the shortest). ROUTE/IQ Cooperative Engine is fundamentally different:

1. **Subproblem Synergy:** No single algorithm solves the entire problem alone. PySpark handles large-scale spatial partitioning ($N \approx 54,000$ road nodes); OR-Tools generates the high-quality global routing skeleton; QAOA, Tabu Search, and Kernighan-Lin explore localized combinatorial boundary permutations ($|B| \le 8$); and VND performs deterministic local cleaning.
2. **Cross-Algorithmic Feedback:** The candidate generated by QAOA or Tabu is spliced directly into the global solution produced by OR-Tools. The algorithms actively modify each other's partial structures.
3. **Adaptive Credit Assignment:** The Multi-Armed Bandit tracks which solver successfully finds improvements at which cluster boundaries, learning over successive iterations where quantum vs classical search is most effective.
4. **Contractual Zero-Risk Safety:** By enforcing Proposition 1, the cooperative engine guarantees that the final output is mathematically no worse than the proven classical baseline, enabling risk-free exploration of experimental algorithms.
