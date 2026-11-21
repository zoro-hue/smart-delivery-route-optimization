# ROUTE/IQ: LIMITATIONS AND RESEARCH INTEGRITY STATEMENT

**Manuscript Title:** ROUTE/IQ: A Big Data–Quantum Hybrid Framework for Directed Urban Vehicle Routing with Quality-Aware QAOA and End-to-End Route Certification  
**Document Purpose:** Transparent documentation of experimental limitations, methodological assumptions, and research integrity boundaries for peer review.

---

## 1. Research Integrity Commitments & Ethical Boundaries

To uphold the highest standards of scientific ethics and peer-review integrity, the authors explicitly affirm the following research boundaries:

1. **NO Claim of Quantum Advantage / Quantum Supremacy:**  
   This paper does **not** claim quantum computational advantage or supremacy over classical algorithms. At the evaluated subproblem scale ($m \le 4$ nodes, $m^2 \le 16$ logical qubits), classical enumeration of the $m! \le 24$ permutations achieves equivalent solution quality in sub-millisecond execution times. ROUTE/IQ is an **architectural framework and algorithmic proof-of-concept** designed to demonstrate how quantum co-processors can be safely integrated into Big Data enterprise pipelines without degrading operational quality.
2. **NO Physical QPU Execution Claimed:**  
   All quantum circuits were executed using classical statevector and shot-based simulation via **Qiskit Aer Simulator 0.17.2**. No physical superconducting, trapped-ion, or neutral-atom quantum processors were utilized in this study.
3. **NO Multi-Node Cluster Scaling Claimed:**  
   Apache Spark 4.2.0 was evaluated in `local[*]` workstation mode using OpenJDK 17 and local worker threads. Multi-node distributed network shuffle latency was not empirically measured.
4. **NO Superiority Claimed Over Mature Classical Solvers:**  
   Mature classical metaheuristics (Google OR-Tools Guided Local Search and Clarke-Wright + 2-opt) achieved approximately **$21\%$ shorter total route distances** than ROUTE/IQ. We do not claim superiority over global classical heuristics on current NISQ simulators.

---

## 2. In-Depth Methodological Limitations

### 2.1 Classical Simulation and Logical-Qubit Boundaries ($m \le 4$)
- **Qubit Scaling Constraint:** Formulating asymmetric TSP with one-hot time-step encoding requires $m^2$ logical qubits for $m$ stops. 
  - $m=3 \implies 9$ qubits
  - $m=4 \implies 16$ qubits
  - $m=5 \implies 25$ qubits (statevector simulation exceeds workstation RAM)
- **Impact:** Due to classical simulation memory bounds ($O(2^n)$ complex amplitudes), microcluster cores were restricted to $m \le 4$ stops. The remaining cluster stops ($\mathcal{B}_k$) were reconstructed classically via directed DP cheapest insertion.
- **Future Direction:** When physical QPUs provide fault-tolerant logical qubits ($> 100$ qubits), microcluster budgets can expand to $m \ge 10$ nodes, where classical brute force becomes computationally intractable ($10! \approx 3.6 \times 10^6$ permutations).

### 2.2 Traffic Volume Data vs. Direct Speed Measurements
- **Data Source Limitation:** The New York City Department of Transportation (NYC DOT) dataset provides automated hourly traffic counts (volumes in vehicles/hour), **not direct vehicle probe speeds (GPS velocities)**.
- **Methodological Solution:** To derive realistic travel delays, we applied the standard Federal Highway Administration (FHWA) Bureau of Public Roads (BPR) volume-delay model:
  $$t_{ij}(V) = t_0 \left[ 1 + 0.15 \left(\frac{V}{C}\right)^4 \right] \cdot W_{\text{friction}}$$
- **Assumption:** Street capacities were modeled at $C = 1,000$ vehicles/hour/lane with an urban free-flow speed of $25\text{ mph}$ ($11.18\text{ m/s}$). While standard in civil engineering, actual congestion in Manhattan is subject to double-parking, pedestrian crossings, and traffic signal timing not fully captured by static volume functions.

### 2.3 Single-Workstation PySpark Overhead
- In single-workstation evaluation, Pandas executed the $50,000$-order scaling task in $29.06\text{ s}$ compared to Spark's $35.21\text{ s}$ (speedup ratio $0.825$).
- This occurs because PySpark incurs inter-process communication (Py4J loopback socket serialization) between the Python driver and the Java Virtual Machine.
- The justification for Spark is architectural: Pandas crashes with `MemoryError` when datasets exceed physical RAM ($> 10^7$ records), whereas Spark seamlessly scales out-of-core and transitions to cloud clusters (AWS EMR / Databricks) without code changes.

### 2.4 Planar Crossing Regularization is an Inductive Bias, Not a Graph Invariant
- On a directed road network with one-way streets, divided avenues, and turn restrictions, a tour with straight-line crossings can occasionally be shorter in actual road distance than an uncrossed tour (confirmed by the Trial 0 counterexample, where avoiding a crossing caused a $+0.7\%$ detour).
- Therefore, crossing avoidance is an **empirical geometric inductive bias** ($96.4\%$ empirical accuracy in Manhattan), not an absolute graph-theoretic invariant.

---

## 3. Epistemic Classification Summary

```
┌────────────────────────────────────────┬────────────────────────────────────────┐
│ WHAT IS MATHEMATICALLY CERTIFIED       │ WHAT IS EMPIRICAL / APPROXIMATE        │
├────────────────────────────────────────┼────────────────────────────────────────┤
│ • Microcluster Core Monotonicity       │ • QAOA Approximation Quality (p=1)     │
│ • Campaign-Level Route Certification   │ • Planar Crossing Regularizer (96.4%)  │
│ • Fleet Capacity Invariant             │ • BPR Volume-Delay Impedance Model     │
│ • Customer Preservation Invariant      │ • Single-Machine Local[*] Spark IPC    │
└────────────────────────────────────────┴────────────────────────────────────────┘
```

By maintaining total transparency regarding these limitations, ROUTE/IQ presents a defensible, peer-review-proof research contribution.
