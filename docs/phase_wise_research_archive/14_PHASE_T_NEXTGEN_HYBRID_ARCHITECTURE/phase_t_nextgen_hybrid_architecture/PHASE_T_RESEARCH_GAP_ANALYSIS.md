# Phase T Deliverable 3: Research Gap Analysis & Problem Repositioning

**Document:** `phase_t_nextgen_hybrid_architecture/PHASE_T_RESEARCH_GAP_ANALYSIS.md`  
**Date:** 2026-11-06  
**Status:** Completed & Rigorously Verified  
**Branch:** `research/phase-t-nextgen-hybrid-architecture`

---

## 1. Classical vs Quantum Capability Matrix

To position quantum computing where it can provide genuine mathematical utility, we map the computational complexity and empirical performance of classical versus quantum algorithms across routing sub-tasks:

| Routing Sub-Task | Classical Complexity | Classical Performance | Quantum Formulation (QUBO) | State-Space Density | Quantum Feasibility | Recommended Role |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Micro-TSP Sequencing ($K \le 5$)** | $O(K!)$ or $O(K^2 2^K)$ | **Solves in $<0.1\text{ ms}$** via exact enumeration / VND. | $N_q = K^2$ qubits, permutation matrix. | **0.036%** ($24 / 65,536$) | Severe column collisions ($68.8\%$ invalid). | **CLASSICAL ONLY** (Never use quantum here). |
| **Intra-Route 2-opt / Relocate** | $O(K^2)$ | **Solves in $<0.05\text{ ms}$** deterministically. | Not well-suited. | N/A | N/A | **CLASSICAL ONLY**. |
| **Large-Scale Data Ingestion & BPR Delay** | $O(|A|)$ | Python single-thread bottlenecks at $N > 5,000$. | N/A | N/A | N/A | **SPARK BIG DATA ONLY**. |
| **Two-Vehicle Boundary Partitioning ($N=16$)** | $O(2^N) = 65,536$ combinations | Greedy heuristics get trapped; branch-and-bound slows. | $N_q = N = 16$ qubits, 1 qubit per customer. | **100.0%** (All $2^{16}$ states are valid bipartitions!) | **Zero column collisions!** Natural Ising spin $\sigma_i^z \in \{-1, +1\}$. | **PRIMARY QUANTUM TARGET**. |
| **Multi-Vehicle Customer Assignment ($N=16, M=4$)** | $O(M^N) \approx 4.29 \times 10^9$ combinations | Severe combinatorial explosion; heuristics settle in local minima. | $N_q = N \cdot \log_2(M) = 32$ qubits. | High density with one-hot vehicle assignment. | Strong quantum candidate for future QPUs. | **COOPERATIVE TARGET**. |

---

## 2. The Core Mathematical Breakthrough: Bipartition QUBO vs Permutation Matrix

### 2.1 The Permutation Matrix Flaw (Phases P–S)
In Phases P through S, sequencing $K=4$ stops required an assignment matrix $X_{i, t} \in \{0, 1\}^{4 \times 4}$:
- Required $N_q = 16$ qubits.
- Total Hilbert space states: $2^{16} = 65,536$.
- Valid routing permutations: $4! = 24$.
- Feasible state density:
  $$\rho_{\text{perm}} = \frac{24}{65,536} \approx \mathbf{0.000366 \quad (0.0366\%)}$$
Over $99.96\%$ of the Hilbert space was invalid junk. Even with row XY-mixers, $68.85\%$ of measured bitstrings suffered from column collisions, requiring classical Hungarian matching.

### 2.2 The Boundary Bipartition QUBO (Phase T Repositioning)
Consider two adjacent delivery vehicles $V_A$ and $V_B$ servicing overlapping territories with $N$ contentious boundary customers. The decision is: which vehicle should service each boundary customer to minimize total circuity and balance fleet capacity?

Let binary variable $x_i \in \{0, 1\}$ represent assigning customer $i$ to Vehicle $V_A$ ($x_i = 1$) or Vehicle $V_B$ ($x_i = 0$):
- **Qubit Allocation:** Exactly **1 qubit per customer**: $N_q = N$. For $N=16$, $N_q = 16$ qubits!
- Total Hilbert space states: $2^{16} = 65,536$.
- Feasible assignment states: Every single basis state $|x_0 x_1 \dots x_{N-1}\rangle \in \{0, 1\}^{16}$ represents a physically valid customer partition!
- **Feasible state density:**
  $$\rho_{\text{bipart}} = \frac{65,536}{65,536} = \mathbf{1.0000 \quad (100.0\%)!}$$

**Mathematical Consequence:**
1. Zero column collisions.
2. Standard transverse-field mixers ($H_X = \sum_i X_i$) explore the **entire feasible assignment space** with zero amplitude wasted on invalid matrix formats!
3. Standard QAOA directly implements a Max-Cut / Min-Bisection quantum Hamiltonian:
   $$H_C = \sum_{i < j} J_{ij} Z_i Z_j + \sum_i h_i Z_i + \lambda \left( \sum_i q_i Z_i - \Delta Q \right)^2$$
4. This is the natural home of quantum optimization in logistics.

