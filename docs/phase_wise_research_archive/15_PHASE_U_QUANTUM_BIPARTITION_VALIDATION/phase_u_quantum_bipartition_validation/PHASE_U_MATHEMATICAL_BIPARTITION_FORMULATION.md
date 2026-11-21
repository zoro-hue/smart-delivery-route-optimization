# Phase U Deliverable 2: Formal Mathematical Formulation of Customer Bipartitioning

**Document:** `phase_u_quantum_bipartition_validation/PHASE_U_MATHEMATICAL_BIPARTITION_FORMULATION.md`  
**Date:** 2026-11-06  
**Status:** Completed & Rigorously Verified  
**Branch:** `research/phase-u-quantum-bipartition-validation`

---

## 1. Problem Definition and Decision Variables

Let $\mathcal{B} = \{c_1, c_2, \dots, c_N\}$ be a set of $N$ boundary delivery customers located in the spatial overlap zone between two adjacent vehicle routes $V_A$ and $V_B$.
Each customer $c_i$ has:
- Geographical coordinates $(\text{lat}_i, \text{lon}_i)$.
- Cargo demand $q_i > 0$.
- Directed distance vector $d(u, c_i)$ and $d(c_i, v)$ on the calibrated NYC road network.

Each vehicle $V_k$ ($k \in \{A, B\}$) has maximum cargo carrying capacity $Q_k$ and a core cluster of non-boundary customers with cumulative pre-existing demand $D_k^{\text{core}}$.
The remaining capacity available for the boundary customers is:
$$C_A = Q_A - D_A^{\text{core}}, \quad C_B = Q_B - D_B^{\text{core}}$$

### Decision Variable:
For each customer $c_i \in \mathcal{B}$:
$$x_i = \begin{cases} 1, & \text{if customer } c_i \text{ is assigned to Vehicle } V_A \\ 0, & \text{if customer } c_i \text{ is assigned to Vehicle } V_B \end{cases}$$

---

## 2. Global Fleet Objective vs Quadratic Proxy

The ultimate goal of vehicle routing is minimizing the total reconstructed fleet distance:
$$\min_{\mathbf{x} \in \{0, 1\}^N} \mathcal{F}_{\text{fleet}}(\mathbf{x}) = \text{TSP}\left( \{0\} \cup \mathcal{C}_A^{\text{core}} \cup \{c_i \mid x_i = 1\} \right) + \text{TSP}\left( \{0\} \cup \mathcal{C}_B^{\text{core}} \cup \{c_i \mid x_i = 0\} \right)$$
subject to:
$$\sum_{i=1}^N q_i x_i \le C_A \quad \text{and} \quad \sum_{i=1}^N q_i (1 - x_i) \le C_B$$

Because the $\text{TSP}(\cdot)$ tour length function is non-analytic and NP-hard, it cannot be directly represented as an Ising Hamiltonian. We formulate an **analytic quadratic surrogate objective**:
$$\mathcal{H}_{\text{surrogate}}(\mathbf{x}) = f_{\text{affinity}}(\mathbf{x}) + f_{\text{interaction}}(\mathbf{x}) + f_{\text{capacity}}(\mathbf{x})$$

### 2.1 Vehicle Spatial Affinity ($f_{\text{affinity}}$)
Measures the distance differential between customer $c_i$ and the geometric/temporal centroids of vehicles $V_A$ and $V_B$:
$$f_{\text{affinity}}(\mathbf{x}) = \sum_{i=1}^N \left( d(V_A, c_i) - d(V_B, c_i) \right) x_i = \sum_{i=1}^N h_i^{\text{dist}} x_i$$
- If customer $c_i$ is closer to $V_A$, $h_i^{\text{dist}} < 0$, energetically favoring $x_i = 1$.
- If customer $c_i$ is closer to $V_B$, $h_i^{\text{dist}} > 0$, energetically favoring $x_i = 0$.

### 2.2 Mutual Spatial Interaction & Clustering ($f_{\text{interaction}}$)
Customers that are geographically adjacent should be serviced by the same vehicle to avoid crossing delivery tours:
$$f_{\text{interaction}}(\mathbf{x}) = \sum_{1 \le i < j \le N} J_{ij}^{\text{dist}} \cdot \left[ x_i (1 - x_j) + (1 - x_i) x_j \right]$$
where $J_{ij}^{\text{dist}} = \frac{\kappa}{\max(d_{\text{min}}, d(c_i, c_j))}$ is the spatial attraction coupling. If $x_i \ne x_j$ (customers split across different vehicles), a positive cost penalty $J_{ij}^{\text{dist}}$ is incurred.

### 2.3 Capacity Balance Penalty ($f_{\text{capacity}}$)
To satisfy vehicle capacities $C_A$ and $C_B$, we enforce a target demand threshold $Q_A^* = \frac{C_A}{C_A + C_B} \sum_{i=1}^N q_i$:
$$f_{\text{capacity}}(\mathbf{x}) = \lambda_{\text{cap}} \left( \sum_{i=1}^N q_i x_i - Q_A^* \right)^2$$
Expanding this quadratic penalty yields:
$$f_{\text{capacity}}(\mathbf{x}) = \lambda_{\text{cap}} \sum_{i=1}^N q_i^2 x_i + 2 \lambda_{\text{cap}} \sum_{i < j} q_i q_j x_i x_j - 2 \lambda_{\text{cap}} Q_A^* \sum_{i=1}^N q_i x_i + \text{const}$$

---

## 3. Total QUBO Objective Function

Combining linear and quadratic terms into standard QUBO format $\mathbf{x}^T \mathbf{Q} \mathbf{x}$:
$$Q_{ii} = h_i^{\text{dist}} + \lambda_{\text{cap}} q_i (q_i - 2 Q_A^*) + \sum_{j \ne i} J_{ij}^{\text{dist}}$$
$$Q_{ij} = -2 J_{ij}^{\text{dist}} + 2 \lambda_{\text{cap}} q_i q_j \quad (i < j)$$
The parameter $\lambda_{\text{cap}}$ balances the trade-off between minimizing road travel distance and preventing vehicle overload.
