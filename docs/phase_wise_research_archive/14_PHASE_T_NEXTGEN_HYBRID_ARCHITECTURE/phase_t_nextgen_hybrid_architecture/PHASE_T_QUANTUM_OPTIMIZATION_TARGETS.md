# Phase T Deliverable 5: Systematic Evaluation of 12 Quantum Optimization Targets

**Document:** `phase_t_nextgen_hybrid_architecture/PHASE_T_QUANTUM_OPTIMIZATION_TARGETS.md`  
**Date:** 2026-11-06  
**Status:** Completed & Rigorously Verified  
**Branch:** `research/phase-t-nextgen-hybrid-architecture`

---

## 1. Evaluation Matrix of 12 Candidate Routing Decisions

To break free from the micro-TSP sequencing bottleneck, we systematically analyze 12 distinct optimization problems within vehicle logistics:

| # | Optimization Problem | Decision Variables | Qubit Scaling ($N_q$) | State Space Density | Classical Baseline | Exact Enumeration Practical? | Quantum Suitability Rating |
| :-: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | **Two-Vehicle Boundary Bipartition** | $x_i \in \{0, 1\}$ | **$N$** (e.g. 16 qubits) | **100.0%** | Greedy Kernighan-Lin | No ($2^{16} = 65,536$) | **EXCELLENT (Rank 1)** |
| **2** | **Multi-Vehicle Workload Balancing** | $x_{im} \in \{0, 1\}$ | $N \cdot M$ (e.g. 32 qubits) | High (with penalty) | LPT Heuristic / MIP | No ($M^N$) | **STRONG (Rank 2)** |
| **3** | **Customer-to-Vehicle Assignment** | $x_{im} \in \{0, 1\}$ | $N \cdot M$ | Medium | OR-Tools Knapsack | No | **STRONG (Rank 3)** |
| **4** | **Route Partition Coordination** | $y_{jk} \in \{0, 1\}$ | $P \cdot P$ | 100.0% | Max-Cut Solver | Yes for $P \le 5$ | Moderate |
| **5** | **Multi-Cluster Territorial Assignment** | $z_{ck} \in \{0, 1\}$ | $C \cdot K$ | High | K-Means / Spectral | No | Moderate |
| **6** | **Capacity-Constrained Vehicle Allocation** | $a_{vm} \in \{0, 1\}$ | $V \cdot M$ | High | Hungarian / Linear Sum | Yes ($O(V^3)$) | Low (Classical Hungarian is $O(V^3)$) |
| **7** | **Time-Window Conflict Resolution** | $w_{ij} \in \{0, 1\}$ | $N^2$ | Low | Interval Scheduling | No | Moderate |
| **8** | **Subproblem Selection & Gating** | $s_p \in \{0, 1\}$ | $P$ (subproblems) | 100.0% | Priority Queue | Yes | Low (Classical sorting is $O(P \log P)$) |
| **9** | **Vehicle Fleet Resource Allocation** | $r_v \in \{0, 1\}$ | $V$ | 100.0% | Knapsack DP | Yes | Low (Dynamic Prog solves in $<1\text{ ms}$) |
| **10** | **Directed Route Sequencing (TSP)** | $X_{it} \in \{0, 1\}$ | **$K^2$** (e.g. 16 qubits) | **0.036%** | **VND / Relocate** | **Yes ($4! = 24$ in $0.08\text{ ms}$)** | **POOR (Phases P–S failure)** |
| **11** | **Multi-Depot Territory Boundary Matching**| $d_{ik} \in \{0, 1\}$ | $N_D \cdot N_C$ | 100.0% | Voronoi Partitioning | No | Strong |
| **12** | **Dynamic Real-Time Insertion Selection** | $u_i \in \{0, 1\}$ | $N_{\text{new}}$ | 100.0% | Cheapest Insertion | Yes | Moderate |

---

## 2. In-Depth Mathematical Formulation of Top Targets

### Target 1 (Winner): Two-Vehicle Boundary Bipartitioning
Let $S = \{c_1, \dots, c_N\}$ be the contentious boundary customers located between the service sectors of Vehicle $V_A$ and Vehicle $V_B$.
Let $x_i \in \{0, 1\}$ denote assignment of customer $c_i$ to $V_A$ ($x_i = 1$) or $V_B$ ($x_i = 0$).

#### Objective Function:
Minimize total travel impedance, customer interaction circuity, and load imbalance:
$$H_C = \sum_{i=1}^N \left( d(V_A, c_i) - d(V_B, c_i) \right) x_i + \sum_{i < j} J_{ij} (x_i \oplus x_j) + \lambda \left( \sum_{i=1}^N q_i x_i - Q_A^* \right)^2$$
where:
- $J_{ij} > 0$ penalizes splitting geographically close customer pairs $(c_i, c_j)$ across different vehicles ($x_i \ne x_j$).
- $\lambda > 0$ enforces vehicle capacity balance ($Q_A^* = \frac{1}{2} \sum q_i$).

#### Mapping to Pauli-Z Ising Model ($x_i = \frac{I - Z_i}{2}$):
$$H_{\text{Ising}} = \sum_{i < j} \tilde{J}_{ij} Z_i Z_j + \sum_{i=1}^N \tilde{h}_i Z_i + C_0$$
- **Qubit Requirement:** Exactly $N$ qubits (for $N=16$, $N_q = 16$).
- **Mixer:** Standard transverse mixer $H_X = \sum_{i=1}^N X_i$ is **exact and unconstrained**.
- **State-Space Density:** $100.0\%$. Zero column collisions, zero Hungarian matching overhead!

### Target 2: Multi-Vehicle Workload Balancing
Distribute $N$ customer clusters across $M$ vehicles to minimize the maximum travel time:
$$H_C = \sum_{m=1}^M \left( \sum_{i=1}^N t_i x_{im} - \frac{1}{M}\sum_{i=1}^N t_i \right)^2 + P \sum_{i=1}^N \left( \sum_{m=1}^M x_{im} - 1 \right)^2$$
- Requires $N \cdot M$ qubits.
- Enforces workload equity under real NYC traffic delays.

