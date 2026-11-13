# Phase R Deliverable 4: QIGA Contribution Audit

**Document:** `phase_r_quantum_contribution_challenge/PHASE_R_QIGA_CONTRIBUTION_AUDIT.md`  
**Date:** 2026-11-06  
**Status:** Completed & Rigorously Verified  
**Branch:** `research/phase-r-quantum-contribution-challenge`

---

## 1. Executive Summary

This audit assesses the role, performance, and scientific standing of the Quantum-Inspired Genetic Algorithm (QIGA / IQGA) in the ROUTE/IQ framework. QIGA operates classically by simulating quantum bit probabilities ($|\psi\rangle = \alpha |0\rangle + \beta |1\rangle$ with $|\alpha|^2 + |\beta|^2 = 1$) updated via quantum rotation gates $R(\Delta \theta)$.

We evaluate whether QIGA provides unique combinatorial search capabilities compared to standard classical genetic algorithms and local search heuristics (2-opt, Lin-Kernighan).

---

## 2. Algorithm Specification

### 2.1 Quantum Register Encoding
Each candidate solution is represented by a register of $m$ Q-bits:
$$q_j = \begin{bmatrix} \alpha_j \\ \beta_j \end{bmatrix}, \quad j = 1, \dots, m$$
A classical chromosome is sampled by measuring each Q-bit: $x_j = 1$ if $\text{rand}() < |\beta_j|^2$, else $0$. For routing permutations, an inverted position-rank decoder maps the measured binary string into a valid sequence of stops.

### 2.2 Quantum Rotation Gate Update
The probability amplitudes are updated toward the incumbent best solution $X^*$ using:
$$\begin{bmatrix} \alpha_j' \\ \beta_j' \end{bmatrix} = \begin{bmatrix} \cos(\Delta \theta_j) & -\sin(\Delta \theta_j) \\ \sin(\Delta \theta_j) & \cos(\Delta \theta_j) \end{bmatrix} \begin{bmatrix} \alpha_j \\ \beta_j \end{bmatrix}$$
where $\Delta \theta_j = s(\alpha_j, \beta_j) \cdot \theta_0$ is looked up based on whether the measured bit $x_j$ agrees with $x^*_j$ and whether fitness improved.

---

## 3. Experimental Evaluation

From the Phase R benchmarks (`phase_r_neighborhood_competition_raw.csv`):

| Characteristic | Classical 2-opt | QIGA ($P=10, G=30$) | QAOA ($p=1$) |
| :--- | :--- | :--- | :--- |
| **Mean Runtime** | **0.057 ms** | **2.74 ms** | 546.6 ms |
| **Optimum Discovery Rate ($K=4$)** | 41.7% | 8.3% (1/12) | **58.3%** |
| **Search Character** | Deterministic local hill-climb | Stochastic probability shift | Quantum state interference |
| **Reversibility Issue** | Trapped by edge inversions | Avoids direct inversion | Cyclic hopping mixer |

### Key Findings:
1. **Low Efficiency on Micro-Subproblems ($K \le 4$):**  
   In tight 4-stop neighborhoods, QIGA's probabilistic decoding requires multiple generations to converge on specific permutations. Classical 2-opt evaluates all 6 2-opt neighbors in $0.05\text{ ms}$, whereas QIGA takes $2.7\text{ ms}$ and only found the true optimum in 1 out of 12 tests when unassisted.
2. **Value as a Global Diversifier:**  
   When coupled with 2-opt (Architecture C/D: QIGA + 2-opt), QIGA serves as an effective stochastic diversification operator, escaping shallow basins before 2-opt performs deterministic downhill descent.
3. **Multi-Route Exchange:**  
   QIGA exhibits stronger utility in inter-route customer reassignments (partition swapping) than intra-route sequence permutations.

---

## 4. Scientific Verdict

QIGA is a valid quantum-inspired classical metaheuristic, but in micro-routing problems ($K \le 6$) it is strictly dominated in speed by exact enumeration and in precision by 2-opt. Its role in ROUTE/IQ is properly positioned at the intermediate cluster level rather than the micro-permutation core.

