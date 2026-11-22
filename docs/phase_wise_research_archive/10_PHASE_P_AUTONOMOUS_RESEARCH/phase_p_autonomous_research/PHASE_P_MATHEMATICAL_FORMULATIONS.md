# ROUTE/IQ — PHASE P: MATHEMATICAL FORMULATIONS OF HYBRID ARCHITECTURES
**Rigorous Mathematical Formulations, Objective Hamiltonians, Penalty Bounds, and Complexity Analysis**

- **Scope:** Complete mathematical derivation of the Capacitated Vehicle Routing Problem (CVRP), Asymmetric TSP (ATSP) subproblem formulation, Ising mapping, XY mixer Hamiltonians, and QIGA probability dynamics.

---

## 1. Global Optimization Problem Formulation (Directed CVRP)

Let $G = (V, E)$ be a directed road graph where:
- $V = \{0\} \cup \{1, \dots, n\}$ is the set of nodes, with $0$ representing the central distribution depot.
- $E = \{(i, j) : i, j \in V, i \ne j\}$ is the set of directed road segments.
- $c_{ij} > 0$ is the calibrated travel impedance from node $i$ to node $j$ computed via the BPR volume-delay model.
- $d_i \ge 0$ is the delivery demand of customer $i$ ($d_0 = 0$).
- $M$ is the available vehicle fleet size.
- $Q$ is the uniform vehicle capacity constraint.

### Global Integer Linear Programming (ILP) Formulation:
$$\min \sum_{k=1}^M \sum_{i \in V} \sum_{j \in V} c_{ij} x_{ijk}$$
Subject to:
1. **Customer Visit Invariant:** Exactly one vehicle visits each customer:
   $$\sum_{k=1}^M \sum_{j \in V, j \ne i} x_{ijk} = 1, \quad \forall i \in \{1, \dots, n\}$$
2. **Depot Flow Balance:** Each vehicle departs and returns to depot:
   $$\sum_{j \in \{1, \dots, n\}} x_{0jk} = \sum_{i \in \{1, \dots, n\}} x_{i0k} \le 1, \quad \forall k \in \{1, \dots, M\}$$
3. **Route Continuity:** Inflow equals outflow at every customer node:
   $$\sum_{i \in V, i \ne p} x_{ipk} - \sum_{j \in V, j \ne p} x_{pjk} = 0, \quad \forall p \in \{1, \dots, n\}, \forall k \in \{1, \dots, M\}$$
4. **Capacity Feasibility:** Cumulative vehicle load does not exceed $Q$:
   $$\sum_{i=1}^n d_i \sum_{j \in V, j \ne i} x_{ijk} \le Q, \quad \forall k \in \{1, \dots, M\}$$
5. **Sub-tour Elimination (MTZ formulation):**
   $$u_{ik} - u_{jk} + Q x_{ijk} \le Q - d_j, \quad \forall 1 \le i \ne j \le n, \forall k \in \{1, \dots, M\}$$

---

## 2. Microcluster Subproblem Decomposition & ATSP Ising Mapping

When Spark or classical local search isolates a microcluster of size $K = 4$ nodes $\{v_1, v_2, v_3, v_4\}$ with fixed entry node $v_{\text{entry}}$ and exit node $v_{\text{exit}}$, the internal ordering is formulated as an Asymmetric Traveling Salesperson Problem (ATSP).

### Position-Based Binary Variables:
Let $x_{ip} \in \{0, 1\}$ represent whether customer node $i \in \{1, \dots, K\}$ is visited at position $p \in \{0, \dots, K-1\}$.
Total required qubits: $N_q = K \times K = 16$.

### Objective Function:
$$C_{\text{ATSP}}(\mathbf{x}) = \sum_{p=0}^{K-2} \sum_{i=1}^K \sum_{j \ne i}^K c(v_i, v_j) x_{ip} x_{j, p+1} + \sum_{i=1}^K c(v_{\text{entry}}, v_i) x_{i, 0} + \sum_{i=1}^K c(v_i, v_{\text{exit}}) x_{i, K-1}$$

### Constraint Penalties:
1. Row constraint (every customer visited once): $P_1 = \lambda_1 \sum_{i=1}^K \left(\sum_{p=0}^{K-1} x_{ip} - 1\right)^2$
2. Column constraint (every step visited once): $P_2 = \lambda_2 \sum_{p=0}^{K-1} \left(\sum_{i=1}^K x_{ip} - 1\right)^2$

### Penalty Multiplier Lower Bound Theorem:
**Theorem 1:** To guarantee that every ground state of $H = C_{\text{ATSP}} + P_1 + P_2$ represents a valid permutation, the penalty multiplier must satisfy:
$$\lambda_1, \lambda_2 > \max_{(i, j) \in E} c(v_i, v_j)$$
*Proof:* Suppose a bitstring violates the permutation constraint by dropping node $i$ (setting $\sum_p x_{ip} = 0$). The constraint penalty increases by $\lambda_1$. The maximum travel cost that could be saved by omitting node $i$ is at most the maximum edge cost connecting into and out of $i$, bounded by $\max c_{ij}$. Thus, if $\lambda_1 > \max c_{ij}$, the penalized energy strictly exceeds any valid permutation energy, preventing false minima. $\blacksquare$

---

## 3. Quantum Operator Derivations

### Mapping to Pauli-Z Spin Operators:
Substituting binary variables $x_{ip} = \frac{1 - Z_{ip}}{2}$ into the quadratic terms:
$$x_{ip} x_{j, p+1} = \frac{1 - Z_{ip} - Z_{j, p+1} + Z_{ip} Z_{j, p+1}}{4}$$
The problem Hamiltonian becomes:
$$H_C = \sum_{ip} h_{ip} Z_{ip} + \sum_{(ip), (jq)} J_{ip, jq} Z_{ip} Z_{jq} + E_{\text{offset}} I$$

### Feasibility-Preserving XY Mixers:
To eliminate the penalty terms $P_1$ and restrict quantum evolution strictly within the valid permutation subspace, we deploy continuous XY hopping mixers:
$$H_M^{(XY)} = \frac{1}{2} \sum_{i=1}^K \sum_{p=0}^{K-2} \left(X_{ip} X_{i, p+1} + Y_{ip} Y_{i, p+1}\right)$$
**Subspace Invariance Property:**
$$[H_M^{(XY)}, \sum_{p=0}^{K-1} Z_{ip}] = 0, \quad \forall i \in \{1, \dots, K\}$$
This ensures that if the register is initialized in a state with $\sum_p x_{ip} = 1$, the mixer unitary $e^{-i \beta H_M^{(XY)}}$ maintains Hamming weight 1 per row for all parameter values $\beta$.

---

## 4. QIGA Quantum Rotation Dynamics

For quantum-inspired genetic optimization, chromosome state is represented as a tensor of Q-bits:
$$|\mathbf{q}_k\rangle = \begin{bmatrix} \alpha_{k1} & \alpha_{k2} & \dots & \alpha_{kn} \\ \beta_{k1} & \beta_{k2} & \dots & \beta_{kn} \end{bmatrix}$$
Subject to normalization $|\alpha_{ki}|^2 + |\beta_{ki}|^2 = 1$.

### Quantum Rotation Gate:
$$U(\Delta\theta_{ki}) = \begin{bmatrix} \cos(\Delta\theta_{ki}) & -\sin(\Delta\theta_{ki}) \\ \sin(\Delta\theta_{ki}) & \cos(\Delta\theta_{ki}) \end{bmatrix}$$
Where rotation angle $\Delta\theta_{ki} = s(\alpha_{ki}, \beta_{ki}) \cdot \theta_0$:
- $\theta_0 = 0.02\pi$
- $s(\alpha, \beta)$ sign lookup table directs the probability distribution towards the best incumbent solution $x^*$.

---

## 5. Computational Complexity Analysis

| Algorithmic Stage | Classical Complexity | Quantum Circuit Complexity | Space / Qubit Complexity |
| :--- | :--- | :--- | :--- |
| **Spark Polar Sweep Partitioning** | $\mathcal{O}(N \log N)$ distributed | None | $\mathcal{O}(N)$ memory |
| **OR-Tools CVRP Global Solve** | $\mathcal{O}(N^2 \cdot M)$ heuristics | None | $\mathcal{O}(N^2)$ distance matrix |
| **QAOA Subproblem Formulation** | $\mathcal{O}(K^3)$ classical setup | Depth $\mathcal{O}(p \cdot K^2)$ | $N_q = K^2 = 16$ qubits |
| **Qiskit Aer Statevector Simulation** | $\mathcal{O}(p \cdot 2^{N_q}) = \mathcal{O}(p \cdot 65,536)$ | Physical: $\mathcal{O}(p)$ time | $2^{16} \times 16 \text{ bytes} \approx 1 \text{ MB}$ RAM |
| **Hungarian Projection Matching** | $\mathcal{O}(K^3) = 64$ operations | None | $\mathcal{O}(K^2)$ |
| **QIGA Population Evolution** | $\mathcal{O}(G \cdot P \cdot N \log N)$ | Classical emulation | $\mathcal{O}(P \cdot N)$ memory |
| **Incumbent Route Verification** | $\mathcal{O}(N)$ validation checks | None | $\mathcal{O}(1)$ overhead |

This formal analysis confirms that for $K=4$, the quantum subproblem requires exactly 16 qubits and $\approx 1\text{ MB}$ of statevector memory, guaranteeing that Qiskit Aer simulation executes with zero memory risk on standard nodes.
