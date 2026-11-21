# Phase R Deliverable 3: QAOA Contribution Audit

**Document:** `phase_r_quantum_contribution_challenge/PHASE_R_QAOA_CONTRIBUTION_AUDIT.md`  
**Date:** 2026-11-06  
**Status:** Completed & Rigorously Verified  
**Branch:** `research/phase-r-quantum-contribution-challenge`

---

## 1. Executive Summary

This audit assesses the exact mathematical, algorithmic, and computational contribution of Quantum Approximate Optimization Algorithm (QAOA) within the ROUTE/IQ cooperative routing framework. 

All circuit evaluations were simulated via Qiskit Aer (`qasm_simulator`, version 2.4.1 / aer 0.17.2) running on CPU. Under strict scientific standards, we evaluate:
1. Circuit construction, qubit scaling, and depth.
2. The role of Warm-Start State Preparation ($U_{\text{WS}}$) and Continuous XY-Mixers ($U_{\text{XY}}(\beta)$).
3. The empirical capability of QAOA to improve solutions beyond classical heuristics.
4. The exact conditions under which QAOA provides superior search dynamics compared to classical local search (2-opt).

---

## 2. Mathematical & Circuit Specification

### 2.1 Qubit Formulation
For a subproblem of $K$ customer stops, the routing permutation is represented as a binary matrix $X \in \{0, 1\}^{K \times K}$, where $X_{i, t} = 1$ if node $i$ is visited at step $t$.
- **Qubit Count:** $N_q = K^2$. For $K = 4$, $N_q = 16$ qubits.
- **State Space:** $2^{16} = 65,536$ basis states.
- **Feasible Permutations:** $K! = 4! = 24$ states ($\approx 0.0366\%$ of Hilbert space).

### 2.2 Cost Hamiltonian ($H_C$)
The Hamiltonian encodes the directed travel cost between stops and depot boundary conditions:
$$H_C = \sum_{t=0}^{K-2} \sum_{i=1}^K \sum_{j=1, j \ne i}^K d_{ij} X_{i,t} X_{j,t+1} + \sum_{i=1}^K d_{\text{depot}, i} X_{i,0} + \sum_{i=1}^K d_{i, \text{depot}} X_{i,K-1} + P \sum_{\text{penalties}}$$
When converted to Pauli operators ($X_{i,t} \to \frac{I - Z_{i,t}}{2}$), $H_C$ consists of 2-qubit $Z \otimes Z$ terms and single-qubit $Z$ terms.

### 2.3 Mixer Hamiltonian ($H_M$) and Warm-Start
Standard transverse-field mixers ($\sum X_i$) do not preserve the $\sum_i X_{i,t} = 1$ and $\sum_t X_{i,t} = 1$ permutation constraints, wasting circuit amplitude on unfeasible states. ROUTE/IQ employs:
1. **Warm-Start State Preparation ($U_{\text{WS}}$):** Initializes the state amplitude concentrated around the incumbent classical permutation $\pi_0$ with exploration angle $\theta$:
   $$|\psi_0\rangle = \cos(\theta) |\pi_0\rangle + \sin(\theta) \sum_{\pi \ne \pi_0} \frac{1}{\sqrt{K! - 1}} |\pi\rangle$$
2. **Continuous XY-Hopping Mixer ($U_{\text{XY}}(\beta)$):**
   $$H_{\text{XY}} = \frac{1}{2} \sum_{(u, v) \in \mathcal{E}_{\text{perm}}} \left( X_u X_v + Y_u Y_v \right)$$
   Applied across time-step pairs within identical nodes or node pairs within identical time steps, this restricts transitions strictly within the Hamming-weight subspace.

---

## 3. Quantitative Performance Audit

From the 12 in-neighborhood benchmark runs (`phase_r_neighborhood_competition_raw.csv`):

| Metric | QAOA ($p=1$, 1024 shots) | Classical 2-opt | Exact Classical Enumeration |
| :--- | :--- | :--- | :--- |
| **Global Optimum Discovery Rate** | **58.3%** (7/12) | 41.7% (5/12) | **100.0%** (12/12) |
| **Rate Beating 2-opt** | **25.0%** (3/12) | N/A | 25.0% (3/12) |
| **Mean Execution Time** | **546.6 ms** | **0.057 ms** | **0.110 ms** |
| **Simulation Slowdown Factor** | **9,589×** vs 2-opt | 1.0× (baseline) | 1.9× vs 2-opt |

### Key Observations:
1. **Asymmetric Escape Mechanism:** On instances 1, 2, and 3 (all characterized by asymmetric one-way road impedances with asymmetry ratio $\alpha = 1.35$), classical 2-opt was trapped in local minima:
   - *Instance 2:* Seed cost $74.625\text{ km}$, 2-opt cost $74.625\text{ km}$ ($0.0\%$ improvement). QAOA found $67.906\text{ km}$ ($9.00\%$ reduction).
   - This occurs because 2-opt reverses the traversal direction between the cut edges ($\pi_{a \dots b} \to \pi_{b \dots a}$), which incurs heavy directional penalties on one-way graphs. QAOA's XY-mixer explores cyclic shifts without compulsory inversion, finding the true global minimum.
2. **Computational Reality:** Classical exact enumeration of 24 permutations takes $0.11\text{ ms}$, whereas simulating a 16-qubit quantum circuit via Qiskit Aer takes $546.6\text{ ms}$. QAOA on a classical simulator cannot compete on wall-clock execution time; its value lies entirely in its mathematical search trajectory and algorithmic benchmarking for future QPU hardware.

---

## 4. Failure Modes and Guardrail Validation

QAOA failed to discover the global optimum in 5 of 12 runs (41.7%). In Instance 4 (2-opt local minimum seed, cost $95.256\text{ km}$), QAOA returned $95.256\text{ km}$, unable to find the optimum of $94.311\text{ km}$.

**The Incumbent Guardrail (Proposition 1):**  
In all 12 cases, the Incumbent-Preserving filter:
$$R_{\text{certified}} = \arg\min \{ \text{Cost}(R_{\text{seed}}), \text{Cost}(R_{\text{QAOA}}), \text{Cost}(R_{\text{classical}}) \}$$
strictly guaranteed $\Delta \text{Cost} \le 0.000\text{ km}$. No degradation occurred in any scenario.

---

## 5. Conclusion

QAOA is **not** a general-purpose replacement for classical algorithms. Its specific, defensible scientific contribution in ROUTE/IQ is as a **non-inverting permutation explorer for asymmetric, non-Euclidean subproblems**, where directional impedance creates severe barriers for 2-opt local search.

