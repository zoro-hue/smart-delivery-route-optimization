# ROUTE/IQ — PHASE P: ADAPTIVE DISPATCH CONTROLLER DESIGN
**Dynamic Problem-Difficulty Characterization, Quantum Subproblem Selection, and Stopping Rules**

---

## 1. Controller Objectives

The Adaptive Dispatch Controller solves the fundamental hybrid resource allocation problem:
*Given a vehicle route or customer cluster, when is it mathematically and computationally beneficial to invoke QAOA versus QIGA versus Classical Local Search?*

Invoking QAOA on trivially ordered or linear sub-tours wastes simulation time ($150\text{ ms}$ vs $0.001\text{ ms}$) without possible gain. The controller dynamically dispatches problems based on rigorous geometric and combinatorial signals.

---

## 2. Feature Extraction & Difficulty Scoring

For any route segment or cluster $C = (v_1, \dots, v_K)$:
1. **Planar Edge Crossing Count ($X_C$):**
   $$X_C = \sum_{i < j} \mathbb{I}(\text{Segment}(v_i, v_{i+1}) \text{ intersects } \text{Segment}(v_j, v_{j+1}))$$
   Non-zero crossings indicate that classical greedy construction has become trapped in an uncrossed local optimum.
2. **Road Network Detour Ratio ($\delta_C$):**
   $$\delta_C = \frac{\sum_{i=1}^{K-1} c(v_i, v_{i+1})}{\sum_{i=1}^{K-1} d_{\text{Euclidean}}(v_i, v_{i+1})}$$
   High detour ratios indicate complex one-way road structures or traffic congestion bottlenecks.
3. **Cluster Spatial Dispersion ($\sigma_C$):**
   $$\sigma_C = \frac{1}{K} \sum_{i=1}^K \|(x_i, y_i) - (\bar{x}, \bar{y})\|_2$$
4. **Composite Difficulty Index:**
   $$\Psi(C) = w_1 X_C + w_2 (\delta_C - 1.0) + w_3 \frac{\sigma_C}{\bar{\sigma}_{\text{global}}}$$
   Calibrated default weights: $w_1 = 3.0, w_2 = 1.5, w_3 = 1.0$.

---

## 3. Dispatch Decision Matrix

| Subproblem Condition | Composite Metric | Dispatched Optimization Engine | Computational Budget |
| :--- | :--- | :--- | :--- |
| **Collinear / Simple Sequence** | $\Psi(C) \le 1.0$, $X_C = 0$ | **Classical 2-opt Local Search** | $< 1\text{ ms}$ |
| **Moderate Detour / No Crossings** | $1.0 < \Psi(C) \le 2.5$, $X_C = 0$ | **Classical OR-Tools LNS** | $10 - 20\text{ ms}$ |
| **Planar Crossing Trap ($K \le 4$)** | $\Psi(C) > 2.5$, $X_C \ge 1$ | **Warm-Start QAOA with XY Mixers** | $100 - 250\text{ ms}$ |
| **Global Customer Ordering ($N \ge 25$)** | Global tour optimization | **Classically-Seeded QIGA** | $50 - 150\text{ ms}$ |
| **Exceeds Qubit Budget ($K > 4$)** | $K^2 > 16$ | **Spark Hierarchical Sub-Split** | Variable Spark time |

---

## 4. Quantum Early-Stopping and Stagnation Guardrails

To prevent unproductive simulation overhead:
1. **Minimum Sampling Entropy Rule:**
   Compute the Shannon entropy of the measured bitstring distribution $S = -\sum_k p_k \log_2(p_k)$.
   If $S < 0.20$ bits (distribution collapsed purely onto the classical seed state without exploration), terminate early and skip further optimization rounds.
2. **Monotonic Improvement Gate:**
   If round 1 of QAOA fails to produce an energy lower than the classical seed Hamiltonian, do not invoke round 2; retain the classical incumbent immediately.

