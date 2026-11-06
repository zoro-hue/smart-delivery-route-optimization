# ROUTE/IQ — PHASE P: ADAPTIVE FEEDBACK CONTROLLER & SUBPROBLEM DISPATCH
**Decision Policies, State Machine, and Resource Accounting for Cooperative Optimization**

---

## 1. Problem Statement

A naive hybrid architecture that indiscriminately executes quantum circuit simulations on every route segment is computationally catastrophic:
- Simulating a 16-qubit QAOA circuit takes ~100–300 ms on CPU.
- If a delivery network contains 50 micro-clusters, unguided quantum simulation consumes 10–15 seconds of CPU time—often on simple, linear route segments where classical greedy heuristics already found the strictly optimal path.

The **Adaptive Feedback Controller (AFC)** serves as the central brain of ROUTE/IQ. It monitors the state of classical and quantum candidate solutions, measures topological bottleneck signals, and selectively routes subproblems to the most effective computational engine.

---

## 2. Testable Selection Signals

The controller evaluates four real-time quantitative signals for every route segment \(S\):

### Signal 1: Planar Edge Crossing Density (\(\mathcal{X}(S)\))
Measures the number of pairwise line-segment intersections within the vehicle tour segment using geometric orientation cross-products:
\[
\mathcal{X}(S) = \sum_{(u, v) < (w, z) \in \mathcal{E}(S)} \mathbb{I}\Big[\text{intersect}((u, v), (w, z))\Big]
\]
- **Interpretation:** If \(\mathcal{X}(S) > 0\), the classical heuristic is trapped in a topological twist. High-priority candidate for combinatorial exploration.

### Signal 2: Classical Stagnation Index (\(\sigma(S)\))
Measures the rate of improvement over recent local search iterations:
\[
\sigma(S) = \frac{\text{Cost}^{(t - \Delta t)}(S) - \text{Cost}^{(t)}(S)}{\text{Cost}^{(t - \Delta t)}(S)}
\]
- **Interpretation:** If \(\sigma(S) < 10^{-4}\) over \(\Delta t \ge 5\) local search attempts, the classical solver has stagnated in a local minimum.

### Signal 3: Impedance Detour Ratio (\(\Delta_{\text{BPR}}(S)\))
Measures the discrepancy between actual BPR-congested road impedance and straight-line Euclidean distance:
\[
\Delta_{\text{BPR}}(S) = \frac{\sum_{(u, v) \in S} t_{uv}^{\text{BPR}}}{\sum_{(u, v) \in S} \text{Haversine}(u, v) / v_{\text{free}}}
\]
- **Interpretation:** High values (\(\Delta_{\text{BPR}} > 1.8\)) indicate severe congestion bottlenecks where standard distance-minimizing heuristics fail.

### Signal 4: Subproblem Cardinality (\(K = |S|\))
Counts the number of internal customer stops within the candidate segment:
- \(K \le 4\): Feasible for QAOA on Qiskit Aer (\(N_q = K^2 \le 16\) logical qubits).
- \(5 \le K \le 30\): Exceeds direct statevector simulation; routed to QIGA.
- \(K > 30\): Routed to Apache Spark distributed partitioning.

---

## 3. Dispatch Decision Matrix

Based on the quantitative signals, the AFC executes the following deterministic policy:

```
                          Route Segment Candidate (S)
                                       │
                         Is Size K <= 4 Customers?
                                ├── Yes ──► Check: X(S) > 0 OR σ(S) < 1e-4?
                                │                 ├── Yes ──► Dispatch to QAOA (Qiskit Aer)
                                │                 └── No  ──► Retain Classical Route (Fast)
                                │
                                └── No  ──► Is Size K in 5..30 Customers?
                                                  ├── Yes ──► Dispatch to QIGA (CPU Evolutionary)
                                                  └── No  ──► Dispatch to Spark Partitioning (Pillar 1)
```

| Subproblem Type | Cardinality | Trigger Condition | Dispatched Engine | Target Objective |
| :--- | :---: | :--- | :--- | :--- |
| **Micro-Bottleneck** | \(K \le 4\) | \(\mathcal{X}(S) > 0\) or \(\sigma(S) < 10^{-4}\) | **QAOA (Qiskit Aer)** | Non-local sequence uncrossing via quantum interference |
| **Simple Micro-Tour** | \(K \le 4\) | \(\mathcal{X}(S) = 0\) and \(\Delta_{\text{BPR}} \le 1.2\) | **Classical 2-opt** | Instant local polish (0.1 ms) |
| **Meso-Cluster** | \(5 \le K \le 30\) | \(\sigma(S) < 10^{-3}\) | **Classically-Seeded QIGA** | Broad combinatorial basin search via Q-bits |
| **Macro-Fleet** | \(K > 30\) | Global order set | **Apache Spark 4.2.0** | Big data polar angle capacity partitioning |

---

## 4. Candidate Dispatch State Machine

```
      ┌────────────────────────────────────────────────────────┐
      │                   STATE: INITIALIZATION                │
      │  - Spark computes polar partition                      │
      │  - Classical heuristics build initial incumbent R_0    │
      └───────────────────────────┬────────────────────────────┘
                                  │
                                  ▼
      ┌────────────────────────────────────────────────────────┐
      │                  STATE: BOTTLENECK SCAN                │
      │  - AFC evaluates X(S), σ(S), Δ_BPR(S) for all routes   │
      │  - Rank candidate subproblems by potential gain        │
      └───────────────────────────┬────────────────────────────┘
                                  │
         ┌────────────────────────┴────────────────────────┐
         ▼                                                 ▼
┌─────────────────────────────────┐       ┌─────────────────────────────────┐
│     STATE: QAOA EXECUTION       │       │      STATE: QIGA EXECUTION      │
│ - Initialize state |π_class>    │       │ - Seed Q-bits from classical R_0│
│ - Run p-layer QAOA on Aer       │       │ - Run rotation gate updates     │
│ - Hungarian permutation decode  │       │ - Apply catastrophe operator    │
└────────────────┬────────────────┘       └────────────────┬────────────────┘
                 │                                         │
                 └────────────────────────┬────────────────┘
                                          │ Candidate Sequences
                                          ▼
      ┌────────────────────────────────────────────────────────┐
      │                 STATE: COOPERATIVE SYNTHESIS           │
      │  - QGAR multi-fragment tour stitching                  │
      │  - Apply cooperative 2-opt polish                      │
      │  - Validate capacity and completeness                  │
      └───────────────────────────┬────────────────────────────┘
                                  │
                                  ▼
      ┌────────────────────────────────────────────────────────┐
      │                STATE: INCUMBENT AUDIT                  │
      │  - If Cost(R_hybrid) < Cost(R_incumbent):              │
      │      Accept R_hybrid as new incumbent                  │
      │  - Else:                                               │
      │      Retain existing classical incumbent               │
      └───────────────────────────┬────────────────────────────┘
                                  │
                                  ▼
      ┌────────────────────────────────────────────────────────┐
      │                  STATE: TERMINATION                    │
      │  - Stop if time budget reached or convergence reached   │
      │  - Emit final certified delivery routes                │
      └────────────────────────────────────────────────────────┘
```

---

## 5. Stopping Criteria & Simulator Protection Rules

To prevent simulator lockup and unnecessary runtime:

1. **Max Quantum Subproblems per Request:**
   \[
   N_{\text{QAOA}}^{\max} = \min(M, 4)
   \]
   At most 4 micro-clusters are evaluated by QAOA per optimization request, bounding quantum simulation wall-clock time to \(\le 1.2\text{ s}\).

2. **Negative Return Cooling:**
   If 2 consecutive QAOA subproblem evaluations yield candidates that do not improve upon the classical sub-tour, the AFC engages a **Quantum Cooling Freeze**:
   - Quantum calls are suspended for the remainder of the optimization campaign.
   - The remaining budget is redirected to classical 2-opt refinement.

3. **Total Optimization Time Budget:**
   - Default budget: \(T_{\max} = 15.0\text{ s}\).
   - If elapsed time exceeds \(0.80 \cdot T_{\max}\), all quantum simulations are immediately aborted, and the controller proceeds to final classical reconstruction.

---

## 6. Verification Verdict

The Adaptive Feedback Controller eliminates unguided quantum execution. By using testable topological and classical stagnation signals, it directs quantum resources strictly to combinatorial bottlenecks where classical heuristics fail, while enforcing strict time-budget caps.

