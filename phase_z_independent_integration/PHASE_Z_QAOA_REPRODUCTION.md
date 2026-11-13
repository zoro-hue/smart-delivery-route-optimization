# PHASE Z QAOA REPRODUCTION & FORMULATION AUDIT
## Independent Reproduction, Mathematical Analysis, and Boundary Verification
**ROUTE/IQ — Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing**  
**Department of Computer Science and Engineering, SRM University-AP**  
**Supervisor:** Dr. Vishnu Prasad Verma  

---

## 1. RESEARCH MANDATE

Phase Y claimed that the **Continuous Subspace XY-Mixer QAOA (Formulation B)** achieved a raw capacity feasibility rate of **79.9%**, outperforming the standard transverse mixer baseline (**31.5%**) by **+48.4 percentage points**, yielding a complete fleet distance of **545.10 km**.

Phase Z was tasked with independently reproducing these results, evaluating the mathematical properties of the XY mixer, and verifying whether the optimization objective in QAOA aligns with complete vehicle routing.

---

## 2. MATHEMATICAL DECONSTRUCTION OF FEASIBILITY

In vehicle routing and quantum combinatorial optimization, the term "feasibility" is frequently conflated. Phase Z establishes four distinct, hierarchical tiers of validity:

```
+--------------------------------------------------------------------------------------------------+
| TIER 1: Bitstring Validity                                                                       |
| Condition: x in {0, 1}^N                                                                         |
| Satisfied natively by all projective quantum measurements in the computational basis.            |
+--------------------------------------------------------------------------------------------------+
| TIER 2: Non-Trivial Partition Validity                                                           |
| Condition: 0 < sum(x_i) < N                                                                      |
| Both vehicle clusters must receive at least one customer.                                        |
+--------------------------------------------------------------------------------------------------+
| TIER 3: Capacity-Feasible Partition                                                              |
| Condition: sum_{i: x_i=1} q_i <= C_A  AND  sum_{i: x_i=0} q_i <= C_B                            |
| Neither vehicle's parcel load exceeds maximum capacity.                                          |
+--------------------------------------------------------------------------------------------------+
| TIER 4: Complete-Route Feasibility                                                               |
| Condition: Valid, non-overlapping TSP tours starting/ending at depot, covering all customers.   |
| Evaluated by VND / OR-Tools after customer assignment.                                           |
+--------------------------------------------------------------------------------------------------+
```

Phase Y's reported feasibility metric referred strictly to **Tier 3 (Capacity-Feasible Partition)**.

---

## 3. MATHEMATICAL PROOF: DOES THE XY-MIXER CONSERVE NON-UNIFORM DEMANDS?

Phase Y attributed the high feasibility of Formulation B to the XY mixer Hamiltonian:
$$H_{\text{XY}} = \frac{1}{2} \sum_{(i, j) \in E} (X_i X_j + Y_i Y_j) = \sum_{(i, j) \in E} (\sigma_i^+ \sigma_j^- + \sigma_i^- \sigma_j^+)$$

Let the total excitation (Hamming weight) operator be:
$$K = \sum_{i=1}^N \frac{I - Z_i}{2} = \sum_{i=1}^N n_i$$

### Theorem 1: Hamming Weight Conservation
For any graph $E$, the XY mixer strictly commutes with the total particle number operator:
$$[H_{\text{XY}}, K] = 0$$
*Proof:* The ladder operators satisfy $[n_i, \sigma_i^\pm] = \pm \sigma_i^\pm$. Therefore:
$$[n_i + n_j, \sigma_i^+ \sigma_j^- + \sigma_i^- \sigma_j^+] = (+1 - 1)\sigma_i^+ \sigma_j^- + (-1 + 1)\sigma_i^- \sigma_j^+ = 0$$
Summing over all edges yields $[H_{\text{XY}}, K] = 0$. Consequently, unitary evolution $e^{-i \beta H_{\text{XY}}}$ strictly confines state dynamics to the subspace of constant Hamming weight $\sum x_i = k$. $\blacksquare$

### Theorem 2: Non-Conservation of Weighted Demands (Knapsack Constraint)
Let $Q = \sum_{i=1}^N q_i n_i$ be the total vehicle parcel demand operator, where $q_i \in \{1, 2, 3, 4\}$ are non-uniform customer demands.
The commutator is:
$$[H_{\text{XY}}, Q] = \sum_{(i, j) \in E} (q_j - q_i) (\sigma_i^+ \sigma_j^- - \sigma_i^- \sigma_j^+)$$
*Result:*
$$[H_{\text{XY}}, Q] = 0 \iff q_i = q_j \quad \forall (i, j) \in E$$
*Implication:* For heterogeneous customer demands ($q_i \ne q_j$), **the XY mixer does NOT commute with the capacity constraint operator**. State evolution inevitably transitions into states violating $\sum q_i x_i \le C$.

### Why Did Phase Y Obtain 79.9% Feasibility?
In Phase Y's benchmark instances, $N=12$, customer demands were randomly drawn from $q_i \in \{1, 2, 3, 4\}$, and vehicle capacities were set generously to $C_A = C_B = \lceil 0.55 \sum q_i \rceil$.  
Because the XY mixer strictly fixes $\sum x_i = 6$ (allocating exactly 6 customers to vehicle A and 6 to vehicle B), the expected demand assigned to each vehicle is exactly $0.50 \sum q_i$. Because $0.50 < 0.55$, random fluctuations around the mean exceed the $55\%$ capacity ceiling in only $\sim 20\%$ of instances.  
Thus, the 79.9% feasibility was a **cardinality-induced probabilistic artifact** of generous capacity slack ($55\%$), rather than a true quantum proof of knapsack constraint satisfaction.

---

## 4. INDEPENDENT REPRODUCTION EXPERIMENT

We reproduced the Phase Y comparison across 15 benchmark instances ($N=12$ qubits, identical random seeds 100–114) using both the Phase Y heuristic sampler and genuine Qiskit 2.4.1 statevector simulation:

| Formulation | Engine Type | Raw Capacity Feasibility | Complete Route (km) | Total Latency (ms) | Useful Rate vs MLS |
|---|---|---|---|---|---|
| **Kernighan-Lin (Classical)** | Heuristic Local Search | **100.0%** | **542.28** | **3.65** | **40.0%** |
| **Phase Y Formulation A (Transverse)** | Heuristic Sampler | 31.5% | 546.84 | 145.64 | 40.0% |
| **Phase Y Formulation B (XY-Mixer)** | Heuristic Sampler | **79.9%** | **545.10** | 118.29 | 33.3% |
| **Phase Y Formulation F (Fast QAOA)** | Heuristic Sampler | 31.3% | 547.55 | 46.17 | 26.7% |
| **Qiskit Formulation A (Transverse)** | Genuine Statevector | 39.6% | 544.20 | 44.41 | 40.0% |
| **Qiskit Formulation B (XY-Mixer)** | Genuine Statevector | 3.7%* | 547.55 | 46.18 | 40.0% |

*\*Note on Genuine Qiskit XY-Mixer:* Without per-instance variational optimization of $(\gamma, \beta)$ angles, statevector amplitudes spread across the Hilbert space, and quantum measurement collapses into non-uniform states that require classical repair.

---

## 5. OBJECTIVE FUNCTION MISALIGNMENT

A critical finding of Phase Z is the fundamental mathematical divergence between the QAOA objective and the complete vehicle routing objective:

- **QUBO Objective (Subproblem):**
  $$\min_x \sum_{i=1}^N h_i x_i + \sum_{i < j} J_{ij} x_i x_j$$
  This optimizes customer assignment to geographic clusters and penalizes separating neighboring nodes.
- **Complete Route Objective (TSP Tours):**
  $$\min \sum_{r \in \{A, B\}} \text{TSP\_Tour\_Distance}(r)$$
  This depends upon the sequential permutation of stops visited within each vehicle route.

Two partitions with identical QUBO cut values can produce radically different TSP tour distances depending on internal geometry and street traversal ordering. This misalignment proves that QAOA can only serve as a **cooperative candidate generator** within an incumbent-preserving classical VND shell, never as an unassisted end-to-end routing optimizer.

