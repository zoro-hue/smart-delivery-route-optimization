# ROUTE/IQ: Mathematical Formulations & Formal Proofs
**Problem Formulation:** Capacitated Vehicle Routing Problem (CVRP) with Real-World Road Network Constraints  
**Impedance Model:** Bureau of Public Roads (BPR) Volume-Delay Congestion  
**Quantum Formulation:** Quadratic Unconstrained Binary Optimization (QUBO) & Ising Mapping  
**Formal Invariant:** Proposition 1 Monotonic Acceptance Guardrail `[VERIFIED]`

---

## 1. Mixed-Integer Linear Programming (MILP) Formulation for CVRP

### 1.1 Graph & Index Sets
Let $G = (V, A)$ be a directed graph where:
- $V = \{0\} \cup V_C$ is the set of all vertices, with $0$ denoting the central municipal distribution depot and $V_C = \{1, 2, \dots, N\}$ denoting customer delivery stops.
- $A = \{(i, j) : i, j \in V, i \neq j\}$ is the set of directed road-network arcs.
- $K = \{1, 2, \dots, |K|\}$ is the set of available delivery vehicles, each possessing maximum payload capacity $Q_k$.
- $q_i > 0$ represents the parcel demand of customer $i \in V_C$ (with $q_0 = 0$).
- $c_{ij} \ge 0$ is the non-negative traversal cost (distance or travel time) along arc $(i, j) \in A$.

### 1.2 Decision Variables
- $x_{ijk} \in \{0, 1\}$: Binary variable equal to $1$ if vehicle $k \in K$ traverses directed arc $(i, j) \in A$, and $0$ otherwise.
- $u_{ik} \ge 0$: Continuous auxiliary variable representing the cumulative load carried by vehicle $k$ after visiting customer $i \in V_C$ (used for Miller-Tucker-Zemlin subtour elimination).

### 1.3 Objective Function
Minimize total fleet operational cost across all traversed road arcs:

$$\min \sum_{k \in K} \sum_{i \in V} \sum_{j \in V, j \neq i} c_{ij} x_{ijk}$$

### 1.4 Operational Constraints
1. **Universal Customer Visit (Exactly Once):**
   $$\sum_{k \in K} \sum_{j \in V, j \neq i} x_{ijk} = 1, \quad \forall i \in V_C$$

2. **Depot Departure Conservation:**
   $$\sum_{j \in V_C} x_{0jk} \le 1, \quad \forall k \in K$$

3. **Flow Conservation at Intermediate Stops:**
   $$\sum_{i \in V, i \neq p} x_{ipk} - \sum_{j \in V, j \neq p} x_{pjk} = 0, \quad \forall p \in V_C, \forall k \in K$$

4. **Vehicle Capacity Ceiling:**
   $$\sum_{i \in V_C} q_i \left( \sum_{j \in V, j \neq i} x_{ijk} \right) \le Q_k, \quad \forall k \in K$$

5. **Subtour Elimination (Miller-Tucker-Zemlin Formulation):**
   $$u_{ik} - u_{jk} + Q_k x_{ijk} \le Q_k - q_j, \quad \forall i, j \in V_C, i \neq j, \forall k \in K$$
   $$q_i \le u_{ik} \le Q_k, \quad \forall i \in V_C, \forall k \in K$$

---

## 2. Dynamic Road Travel Time & Congestion Modeling

In realistic metropolitan traffic, edge traversal costs are non-linear functions of road volume, capacity, and weather. ROUTE/IQ models travel time using the **Bureau of Public Roads (BPR)** formulation:

$$t_e = t_e^0 \left[ 1 + \alpha \left( \frac{V_e}{C_e} \right)^\beta \right] \cdot W_{\text{weather}}$$

Where:
- $t_e^0 = \frac{L_e}{v_e^{\text{free}}}$ is the free-flow traversal time across road segment $e$ of length $L_e$ at free-flow speed $v_e^{\text{free}}$.
- $V_e$ is the instantaneous vehicle traffic volume derived from NYC DOT sensor counts.
- $C_e$ is the practical hourly design capacity of the roadway.
- $\alpha = 0.15$ and $\beta = 4.0$ are standard federal BPR calibration parameters.
- $W_{\text{weather}}$ is an empirical meteorological impairment multiplier ($W_{\text{clear}} = 1.0$, $W_{\text{rain}} = 1.15$, $W_{\text{snow}} = 1.35$).

---

## 3. Quantum Subproblem Formulation: QUBO to Ising Mapping

For boundary customer reassignment between vehicle pair $(A, B)$, the assignment is formulated as a Quadratic Unconstrained Binary Optimization (QUBO) problem:

$$f(\mathbf{x}) = \sum_{i=1}^n c_i x_i + \sum_{i=1}^n \sum_{j > i}^n J_{ij} x_i x_j + \lambda_A \left( \sum_{i=1}^n q_i x_i - \Delta Q_A \right)^2$$

Where $x_i \in \{0, 1\}$ denotes assigning stop $i$ to Vehicle $A$ ($x_i = 1$) or Vehicle $B$ ($x_i = 0$).

### 3.1 Transformation to Ising Spin Hamiltonian
Using the standard spin variable transformation $x_i = \frac{1 - \sigma_i^z}{2}$, where $\sigma_i^z \in \{+1, -1\}$ is the Pauli-$Z$ observable:

$$H_P = \sum_{i=1}^n h_i \sigma_i^z + \sum_{i < j} J_{ij}' \sigma_i^z \sigma_j^z + C_{\text{offset}}$$

Where:
$$h_i = -\frac{c_i}{2} - \sum_{j \neq i} \frac{J_{ij}}{4} + \lambda_A q_i \left( \sum_{k=1}^n \frac{q_k}{2} - \Delta Q_A \right)$$
$$J_{ij}' = \frac{J_{ij}}{4} + \lambda_A \frac{q_i q_j}{2}$$

---

## 4. Formal Proof: Proposition 1 Monotonic Acceptance Guardrail

### 4.1 Proposition Statement
Let $\mathcal{S}$ denote the set of all vehicle routing configurations for instance $(V, K, Q)$, and let $\mathcal{S}_{\text{feas}} \subset \mathcal{S}$ denote the subset of configurations satisfying constraints (1)–(5).
Let $\text{Cost}: \mathcal{S} \to \mathbb{R}^+$ evaluate the total road-network travel distance.
Given an initial feasible solution $S_0 \in \mathcal{S}_{\text{feas}}$ and a sequence of candidate generators $\mathcal{M}_t: \mathcal{S}_{\text{feas}} \to \mathcal{S}$ for iterations $t = 1, \dots, T$:

The acceptance rule defined by:
$$S_t = \begin{cases} 
S_{\text{cand}} & \text{if } S_{\text{cand}} \in \mathcal{S}_{\text{feas}} \land \text{Cost}(S_{\text{cand}}) < \text{Cost}(S_{t-1}) \\
S_{t-1} & \text{otherwise}
\end{cases}$$
where $S_{\text{cand}} = \mathcal{M}_t(S_{t-1})$, guarantees that:
1. **Feasibility Invariant:** $S_t \in \mathcal{S}_{\text{feas}}$ for all $t \ge 0$.
2. **Monotonic Non-Degradation:** $\text{Cost}(S_t) \le \text{Cost}(S_{t-1}) \le \dots \le \text{Cost}(S_0)$ for all $t \ge 0$.

### 4.2 Formal Proof
- **Claim 1 (Feasibility):** By definition of $S_0$, $S_0 \in \mathcal{S}_{\text{feas}}$. Assume inductively that $S_{t-1} \in \mathcal{S}_{\text{feas}}$. At iteration $t$, $S_t$ can take one of two values:
  - Case 1: $S_t = S_{\text{cand}}$. This occurs only if the condition $S_{\text{cand}} \in \mathcal{S}_{\text{feas}}$ evaluates to True. Hence, $S_t \in \mathcal{S}_{\text{feas}}$.
  - Case 2: $S_t = S_{t-1}$. By the inductive hypothesis, $S_{t-1} \in \mathcal{S}_{\text{feas}}$. Hence, $S_t \in \mathcal{S}_{\text{feas}}$.
  Thus, by mathematical induction, $S_t \in \mathcal{S}_{\text{feas}}$ for all $t \ge 0$. $\blacksquare$

- **Claim 2 (Monotonicity):** Assume inductively that $\text{Cost}(S_{t-1}) \le \text{Cost}(S_0)$.
  - Case 1: $S_{\text{cand}}$ satisfies the acceptance condition. Then $\text{Cost}(S_{\text{cand}}) < \text{Cost}(S_{t-1})$. Thus $\text{Cost}(S_t) < \text{Cost}(S_{t-1}) \le \text{Cost}(S_0)$.
  - Case 2: $S_{\text{cand}}$ violates feasibility or $\text{Cost}(S_{\text{cand}}) \ge \text{Cost}(S_{t-1})$. Then $S_t = S_{t-1}$, so $\text{Cost}(S_t) = \text{Cost}(S_{t-1}) \le \text{Cost}(S_0)$.
  In all cases, $\text{Cost}(S_t) \le \text{Cost}(S_{t-1})$. Thus the sequence of solution costs $\{\text{Cost}(S_t)\}_{t=0}^T$ is monotonically non-increasing. $\blacksquare$
