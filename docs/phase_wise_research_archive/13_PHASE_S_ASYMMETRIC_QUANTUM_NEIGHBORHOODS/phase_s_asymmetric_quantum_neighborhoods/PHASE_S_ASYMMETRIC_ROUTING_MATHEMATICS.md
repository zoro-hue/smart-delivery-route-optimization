# Phase S Deliverable 2: Asymmetric Directed Routing Mathematics

**Document:** `phase_s_asymmetric_quantum_neighborhoods/PHASE_S_ASYMMETRIC_ROUTING_MATHEMATICS.md`  
**Date:** 2026-11-06  
**Status:** Completed & Rigorously Verified  
**Branch:** `research/phase-s-asymmetric-quantum-neighborhoods`

---

## 1. Mathematical Formulation of Directed Asymmetric Routing

Let $G = (V, A)$ be a strongly connected directed graph representing an urban road network, where $V = \{0, 1, \dots, N\}$ represents delivery nodes (0 is depot) and $A \subseteq V \times V$ represents directed road links.
The cost function $d: A \to \mathbb{R}^+$ satisfies:
$$d(u, v) \ne d(v, u) \quad \text{for general } (u, v) \in A$$
due to one-way street geometry, turn restrictions, and dynamic traffic congestion.

### 1.1 Degree of Graph Asymmetry ($\alpha$)
We quantify graph asymmetry using the normalized Frobenius-norm asymmetry ratio:
$$\alpha(D) = \frac{\sum_{u \ne v} |d_{uv} - d_{vu}|}{\sum_{u \ne v} (d_{uv} + d_{vu})} \in [0, 1]$$
- $\alpha = 0.00$: Perfectly symmetric Euclidean space.
- $\alpha \in [0.10, 0.25]$: Typical grid urban network (Manhattan avenues and streets).
- $\alpha \ge 0.35$: Heavily constrained arterial one-way network with bridge/tunnel impedances.

### 1.2 Bounded Subproblem Cost Objective
For a neighborhood of $K$ customer nodes $S = \{s_0, s_1, \dots, s_{K-1}\} \subset V$, ordered by permutation $\pi \in \mathcal{S}_K$, with preceding route boundary $e$ (entry) and subsequent boundary $x$ (exit), the exact directed traversal cost is:
$$C(\pi) = d(e, s_{\pi(0)}) + \sum_{t=0}^{K-2} d(s_{\pi(t)}, s_{\pi(t+1)}) + d(s_{\pi(K-1)}, x)$$

---

## 2. Failure Mechanism of Symmetric 2-opt on Asymmetric Graphs

In standard symmetric routing, a 2-opt move cuts edges $(\pi_{i-1}, \pi_i)$ and $(\pi_j, \pi_{j+1})$ and reconnects $(\pi_{i-1}, \pi_j)$ and $(\pi_i, \pi_{j+1})$. The cost delta on a symmetric graph is simply:
$$\Delta C_{\text{sym}} = d(\pi_{i-1}, \pi_j) + d(\pi_i, \pi_{j+1}) - d(\pi_{i-1}, \pi_i) - d(\pi_j, \pi_{j+1})$$

### The Directed Reversal Penalty:
On a directed graph, reconnecting $\pi_{i-1} \to \pi_j$ forces the intermediate path $[\pi_i, \dots, \pi_j]$ to be traversed in reverse order:
$$(\pi_i \to \pi_{i+1} \to \dots \to \pi_j) \longrightarrow (\pi_j \to \dots \to \pi_{i+1} \to \pi_i)$$
The true directed cost delta is:
$$\Delta C_{\text{asym}} = \Delta C_{\text{sym}} + \sum_{k=i}^{j-1} \left[ d(\pi_{k+1}, \pi_k) - d(\pi_k, \pi_{k+1}) \right]$$

If the segment contains one-way streets, $d(\pi_{k+1}, \pi_k) \gg d(\pi_k, \pi_{k+1})$. The internal penalty $\sum [d(\pi_{k+1}, \pi_k) - d(\pi_k, \pi_{k+1})]$ becomes heavily positive, forcing $\Delta C_{\text{asym}} > 0$. **Symmetric 2-opt is mathematically blind to moves that require non-inverting node displacement**, becoming trapped in severe local minima.

---

## 3. Directed Classical Search Operators

To optimize asymmetric graphs, classical algorithms must use operators that do not invert intermediate paths:

### 3.1 Directed Relocate (1-0 Insertion)
Extracts node $\pi_i$ and inserts it at position $j$:
$$\text{Relocate}(\pi, i, j): \quad (\dots, \pi_{i-1}, \pi_i, \pi_{i+1}, \dots, \pi_j, \dots) \longrightarrow (\dots, \pi_{i-1}, \pi_{i+1}, \dots, \pi_j, \pi_i, \dots)$$
- **Forward Invariance:** All nodes between $i$ and $j$ retain their relative forward traversal order. No edges are inverted!
- **Delta Cost:** Only 3 directed arcs are removed and 3 added:
  $$\Delta C = d(\pi_{i-1}, \pi_{i+1}) + d(\pi_j, \pi_i) + d(\pi_i, \pi_{j+1}) - d(\pi_{i-1}, \pi_i) - d(\pi_i, \pi_{i+1}) - d(\pi_j, \pi_{j+1})$$

### 3.2 Directed Node Swap (1-1 Exchange)
Exchanges the positions of two distinct nodes $\pi_i$ and $\pi_j$ ($i < j$):
$$\text{Swap}(\pi, i, j): \quad (\dots, \pi_{i-1}, \pi_i, \pi_{i+1}, \dots, \pi_{j-1}, \pi_j, \pi_{j+1}, \dots) \longrightarrow (\dots, \pi_{i-1}, \pi_j, \pi_{i+1}, \dots, \pi_{j-1}, \pi_i, \pi_{j+1}, \dots)$$
- Intermediate nodes between $i+1$ and $j-1$ remain completely untouched and un-reversed.

### 3.3 Or-opt (Segment Relocation)
Relocates a block of 2 or 3 consecutive nodes $(\pi_i, \pi_{i+1})$ to position $j$ without reversing their internal relative order:
$$(\pi_i, \pi_{i+1}) \longrightarrow \text{moved intact to position } j$$

### 3.4 Variable Neighborhood Descent (VND)
Chains the directed operators in order of computational complexity:
$$\mathcal{N}_1 (\text{Relocate}) \longrightarrow \mathcal{N}_2 (\text{Swap}) \longrightarrow \mathcal{N}_3 (\text{Or-opt}) \longrightarrow \mathcal{N}_4 (\text{Directed 2-opt})$$
Whenever a neighborhood yields an improvement ($\Delta C < 0$), VND immediately returns to $\mathcal{N}_1$, ensuring that simple non-inverting shifts are exhausted before any path reversals are evaluated.

