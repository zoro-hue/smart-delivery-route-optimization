# ROUTE/IQ: Mathematical Formulation & Proofs

## 1. Complete Capacitated Vehicle Routing Problem (CVRP)

Let $G = (V, A)$ be a complete directed graph, where:
- $V = \{0\} \cup V_C$ is the set of nodes, with $0$ representing the central depot and $V_C = \{1, \dots, M\}$ representing delivery customer stops.
- $A = \{(i, j) \mid i, j \in V, i \ne j\}$ is the directed arc set.
- $c_{ij} \ge 0$ is the non-negative directed travel distance (or time) from node $i$ to node $j$.
- $q_i > 0$ is the delivery demand of customer $i \in V_C$ ($q_0 = 0$).
- $K = \{1, \dots, M_{\text{veh}}\}$ is the fleet of homogeneous vehicles, each with maximum capacity $C$.

### Mixed-Integer Linear Program (MILP)
Decision variables:
- $y_{ik} \in \{0, 1\}$: 1 if customer $i$ is serviced by vehicle $k$; 0 otherwise.
- $z_{ijk} \in \{0, 1\}$: 1 if vehicle $k$ travels directly from node $i$ to node $j$; 0 otherwise.

$$\min \sum_{k \in K} \sum_{i \in V} \sum_{j \in V, j \ne i} c_{ij} z_{ijk}$$

Subject to:
1. Every customer visited exactly once:
   $$\sum_{k \in K} y_{ik} = 1 \quad \forall i \in V_C$$
2. Vehicle capacity limit:
   $$\sum_{i \in V_C} q_i y_{ik} \le C \quad \forall k \in K$$
3. Route continuity and depot round-trip:
   $$\sum_{j \in V, j \ne i} z_{ijk} = \sum_{j \in V, j \ne i} z_{jik} = y_{ik} \quad \forall i \in V, \forall k \in K$$
4. Subtour elimination constraints (DFJ / MTZ).

---

## 2. Two-Vehicle Boundary Bipartitioning Subproblem

To scale quantum optimization without intractable qubit overhead, Apache Spark isolates localized boundary customer sets $B_{AB} = \{1, \dots, N\} \subset V_C$ located between two adjacent vehicle routes $A$ and $B$, where $N \le 16$.

### Binary Decision Variable
$$x_i = \begin{cases} 1 & \text{if customer } i \in B_{AB} \text{ is assigned to Vehicle } A \\ 0 & \text{if customer } i \in B_{AB} \text{ is assigned to Vehicle } B \end{cases}$$

### Continuous Quadratic Surrogate Objective
$$H_{\text{QUBO}}(\mathbf{x}) = \sum_{i=1}^N h_i^{\text{dist}} x_i - \sum_{i=1}^N \sum_{j=i+1}^N W_{ij} [x_i x_j + (1 - x_i)(1 - x_j)] + \lambda_C \left( \sum_{i=1}^N q_i x_i - \Delta Q \right)^2$$

Where:
- $h_i^{\text{dist}} = d(i, \text{Centroid}_A) - d(i, \text{Centroid}_B)$ measures spatial preference.
- $W_{ij} = \frac{5.0}{d(i, j) + 0.5}$ rewards co-locating spatially adjacent customers in the same vehicle.
- $\Delta Q = \frac{1}{2} (C_A - C_B + \sum q_i)$ is the target capacity balance point.
- $\lambda_C > 0$ is the quadratic capacity penalty weight.

---

## 3. Derivation of the Ising Spin Hamiltonian

Using the canonical change of basis from binary variables $x_i \in \{0, 1\}$ to Pauli-$Z$ spin operators $Z_i \in \{+1, -1\}$:
$$x_i = \frac{I - Z_i}{2}$$

Substituting into each component:

### Linear Terms
$$\sum_i h_i^{\text{dist}} \left( \frac{I - Z_i}{2} \right) = \frac{1}{2} \sum_i h_i^{\text{dist}} I - \frac{1}{2} \sum_i h_i^{\text{dist}} Z_i$$

### Quadratic Spatial Interaction Terms
$$x_i x_j + (1 - x_i)(1 - x_j) = 2 x_i x_j - x_i - x_j + 1 = \frac{1}{2} (I + Z_i Z_j)$$
$$- \sum_{i < j} W_{ij} \left( \frac{I + Z_i Z_j}{2} \right) = - \frac{1}{2} \sum_{i < j} W_{ij} Z_i Z_j + \text{const}$$

### Quadratic Capacity Penalty Terms
$$\left( \sum_i q_i x_i - \Delta Q \right)^2 = \left( \frac{1}{2} \sum_i q_i (I - Z_i) - \Delta Q \right)^2 = \left( \Delta Q_{\text{eff}} - \frac{1}{2} \sum_i q_i Z_i \right)^2$$
$$= \frac{1}{4} \sum_{i \ne j} q_i q_j Z_i Z_j - \Delta Q_{\text{eff}} \sum_i q_i Z_i + \text{const}$$

### Standard Ising Form
$$H_C = \sum_{i=1}^N h_i Z_i + \sum_{i < j}^N J_{ij} Z_i Z_j + C_0$$
Where:
- $h_i = - \frac{1}{2} h_i^{\text{dist}} - \lambda_C \Delta Q_{\text{eff}} q_i$
- $J_{ij} = - \frac{1}{2} W_{ij} + \frac{\lambda_C}{2} q_i q_j$

---

## 4. Deterministic Classical Capacity Repair Algorithm

Given an unconstrained sampled bitstring $\mathbf{x} \in \{0, 1\}^N$:
1. Compute vehicle loads:
   $$Q_A = \sum_{i=1}^N q_i x_i, \quad Q_B = \sum_{i=1}^N q_i (1 - x_i)$$
2. If $Q_A > C_A$:
   - Identify nodes currently in $A$: $V_A = \{i \mid x_i = 1\}$.
   - Sort $V_A$ in descending order of transfer preference for $B$: $\nabla_i = h_i^{\text{dist}}$.
   - Iteratively shift node $i^* = \arg\max \nabla_i$ from $A$ to $B$ ($x_{i^*} \leftarrow 0$) until $Q_A \le C_A$.
3. If $Q_B > C_B$:
   - Symmetrically shift nodes from $B$ to $A$ until $Q_B \le C_B$.
4. **Feasibility Guarantee**: Terminates in at most $N$ steps with $Q_A \le C_A$ and $Q_B \le C_B$, provided total demand $\sum q_i \le C_A + C_B$.

---

## 5. Proposition 1: Incumbent-Preserving Monotonic Guardrail

### Proposition 1 (Monotonic Acceptance Guarantee)
Let $R_{\text{incumbent}}$ be the certified incumbent delivery schedule with total network routing cost $\text{Cost}(R_{\text{incumbent}})$. Let $\mathbf{x}_{\text{qaoa}}$ be a candidate boundary partition sampled from the QAOA variational circuit, repaired to strict capacity feasibility by the deterministic repair operator, and fully sequenced via Variable Neighborhood Descent to produce complete fleet route $R_{\text{candidate}}$.

Define the dispatch acceptance rule:
$$R_{\text{final}} = \begin{cases} R_{\text{candidate}} & \text{if } \text{Cost}(R_{\text{candidate}}) \le \text{Cost}(R_{\text{incumbent}}) \\ R_{\text{incumbent}} & \text{otherwise} \end{cases}$$

Then:
$$\text{Cost}(R_{\text{final}}) \le \text{Cost}(R_{\text{incumbent}})$$
unconditionally across all executions.

### Proof
Directly follows from the piecewise definition of the acceptance rule:
- Case 1: If $\text{Cost}(R_{\text{candidate}}) \le \text{Cost}(R_{\text{incumbent}})$, then $R_{\text{final}} = R_{\text{candidate}}$, satisfying $\text{Cost}(R_{\text{final}}) \le \text{Cost}(R_{\text{incumbent}})$.
- Case 2: If $\text{Cost}(R_{\text{candidate}}) > \text{Cost}(R_{\text{incumbent}})$, then $R_{\text{final}} = R_{\text{incumbent}}$, yielding $\text{Cost}(R_{\text{final}}) = \text{Cost}(R_{\text{incumbent}})$.

Thus, $\text{Cost}(R_{\text{final}}) \le \text{Cost}(R_{\text{incumbent}})$ holds universally. $\blacksquare$
