# Phase S Deliverable 4: Asymmetric Directed QAOA Formulation

**Document:** `phase_s_asymmetric_quantum_neighborhoods/PHASE_S_QAOA_FORMULATION.md`  
**Date:** 2026-11-06  
**Status:** Completed & Rigorously Verified  
**Branch:** `research/phase-s-asymmetric-quantum-neighborhoods`

---

## 1. Problem Formulation and Hamiltonian Encoding

For a directed delivery subproblem of $K$ customer stops $S = \{s_0, s_1, \dots, s_{K-1}\}$ bounded by entry node $e$ and exit node $x$, we map the tour to a binary matrix $X \in \{0, 1\}^{K \times K}$:
$$X_{i, t} = 1 \iff \text{customer } s_i \text{ is visited at time step } t \in \{0, \dots, K-1\}$$

- **Qubit Allocation:** $N_q = K^2$ qubits.
- **Qubit Index Mapping:** $q(i, t) = i \cdot K + t$.
- **Hilbert Space Dimension:** $\mathcal{H} = \mathbb{C}^{2^{K^2}}$ (for $K=4$, $\dim(\mathcal{H}) = 2^{16} = 65,536$).
- **Permutation Subspace:** $|\mathcal{S}_K| = K! = 24$ states ($0.0366\%$ of full Hilbert space).

### 1.1 Asymmetric Cost Hamiltonian ($H_C$)
The Cost Hamiltonian explicitly incorporates directed arc impedances without symmetric averaging:
$$H_C = \sum_{i=0}^{K-1} d(e, s_i) X_{i, 0} + \sum_{t=0}^{K-2} \sum_{i=0}^{K-1} \sum_{j=0, j \ne i}^{K-1} d(s_i, s_j) X_{i, t} X_{j, t+1} + \sum_{i=0}^{K-1} d(s_i, x) X_{i, K-1} + H_{\text{penalty}}$$

Mapping binary variables to Pauli-$Z$ operators via $X_{i, t} = \frac{I - Z_{i, t}}{2}$, $H_C$ maps to a diagonal operator comprising:
- $K \cdot (K-1) \cdot (K-1)$ two-body interaction terms: $Z_{i, t} \otimes Z_{j, t+1}$.
- $K \cdot K$ single-qubit longitudinal field terms: $Z_{i, t}$.
- An energy offset constant $E_0$.

### 1.2 Penalty Hamiltonian ($H_{\text{penalty}}$)
To penalize constraint violations during evolution:
$$H_{\text{penalty}} = P_{\text{row}} \sum_{i=0}^{K-1} \left( \sum_{t=0}^{K-1} X_{i, t} - 1 \right)^2 + P_{\text{col}} \sum_{t=0}^{K-1} \left( \sum_{i=0}^{K-1} X_{i, t} - 1 \right)^2$$
where $P_{\text{row}}, P_{\text{col}} > \max_{(u, v)} d(u, v)$ ensures that unfeasible states are energetically penalized.

---

## 2. Mixer Hamiltonian ($H_M$) and Warm-Start State

### 2.1 Classical Warm-Start Initialization ($|\psi_0\rangle$)
Rather than preparing an unconstrained equal superposition ($H^{\otimes N_q} |0\rangle^{\otimes N_q}$ which places $99.96\%$ of amplitude on non-permutation states), ROUTE/IQ prepares a computational basis state corresponding to the incumbent classical sequence $\pi_{\text{seed}}$:
$$|\psi_0\rangle = |\pi_{\text{seed}}\rangle = \bigotimes_{i=0}^{K-1} |e_{\pi_{\text{seed}}(i)}\rangle$$
where $|e_t\rangle$ has qubit $i \cdot K + t$ in state $|1\rangle$ and all other time slots for node $i$ in state $|0\rangle$.

### 2.2 Continuous XY-Mixer ($U_{\text{XY}}(\beta)$)
Transitions between adjacent time slots are driven by the continuous planar XY hopping Hamiltonian:
$$H_{\text{XY}} = \frac{1}{2} \sum_{i=0}^{K-1} \sum_{t=0}^{K-2} \left( X_{i, t} X_{i, t+1} + Y_{i, t} Y_{i, t+1} \right)$$
Implemented via Qiskit's `XXPlusYYGate(2 * beta, 0.0)`.

---

## 3. Variational Quantum Circuit Execution

For depth $p=1$, the trial state is:
$$|\psi(\gamma, \beta)\rangle = e^{-i \beta H_{\text{XY}}} e^{-i \gamma H_C} |\psi_0\rangle$$
1. **Transpilation:** Optimized for `qiskit_aer.AerSimulator` targeting CPU execution.
2. **Classical Parameter Optimization:** COBYLA optimizer tunes $(\gamma, \beta)$ with objective:
   $$\min_{\gamma, \beta} \langle \psi(\gamma, \beta) | H_C | \psi(\gamma, \beta) \rangle$$
3. **Sampling:** 1024 measurement shots sampled from the optimized circuit.
4. **Post-Measurement Hungarian Bipartite Projection:** Because the row-wise XY-mixer allows column collisions (measured in Section 5), every measured matrix is decoded into a valid permutation via the Kuhn-Munkres algorithm.

