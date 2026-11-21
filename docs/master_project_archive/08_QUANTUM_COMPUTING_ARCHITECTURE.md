# ROUTE/IQ: Quantum Computing Architecture & Qiskit Aer Simulation
**Quantum Simulation SDK:** Qiskit 2.4.1 (Qiskit Aer Statevector Engine)  
**Quantum Algorithmic Primitives:** Gate-Based QAOA, XY-Mixer Ansätze, QIGA  
**Hardware Reality:** Classical CPU Statevector Simulation (No Physical QPU)  
**Audit Standard:** Quantum Mechanics & Variational Algorithms Forensic Review `[VERIFIED]`

---

## 1. Quantum Computing Reality & Terminology Standards

### 1.1 Academic Integrity Statement `[VERIFIED]`
ROUTE/IQ explicitly affirms that **all quantum algorithms described herein are executed via classical mathematical simulation of quantum statevectors on local CPU hardware**.
- The project does **not** claim physical quantum supremacy on hardware QPUs (such as IBM Quantum Eagle/Heron or Google Sycamore).
- Classical statevector simulation computes the full $2^n$-dimensional complex amplitude statevector $\lvert \psi(\boldsymbol{\gamma}, \boldsymbol{\beta}) \rangle$. Due to exponential memory scaling ($O(2^n)$), simulation is strictly bounded to subproblems with $n \le 16$ qubits ($65,536$ complex amplitudes), consuming $\approx 1$ MB of RAM.
- Simulated QAOA functions within ROUTE/IQ as a **heuristic candidate generator** for localized combinatorial subproblems, protected by classical feasibility guardrails.

---

## 2. Quantum Approximate Optimization Algorithm (QAOA) Formulation

QAOA is a variational quantum algorithm designed to find approximate solutions to combinatorial optimization problems mapped onto Ising spin glasses.

### 2.1 Problem Hamiltonian Formulation ($H_P$)
Consider a boundary bipartition problem where a subset of $n$ boundary customer stops must be assigned to either Vehicle $A$ ($s_i = +1$, bit $0$) or Vehicle $B$ ($s_i = -1$, bit $1$).
The objective is to minimize total insertion cost while penalizing capacity imbalance:

$$H_P = \sum_{i=1}^n c_i \sigma_i^z + \sum_{i < j} J_{ij} \sigma_i^z \sigma_j^z + \lambda \left( \sum_{i=1}^n q_i \sigma_i^z - \Delta Q \right)^2$$

Where:
- $\sigma_i^z$ is the Pauli-$Z$ operator acting on qubit $i$.
- $c_i$ represents the differential cost of assigning stop $i$ to Vehicle $A$ versus Vehicle $B$.
- $J_{ij}$ is the interaction coupling representing spatial proximity between stops $i$ and $j$.
- $\lambda$ is the penalty multiplier for vehicle capacity violation.
- $\Delta Q = Q_A - Q_B$ is the capacity headroom differential.

### 2.2 Quantum Alternating Operator Ansatz & XY-Mixers
Standard QAOA utilizes a transverse magnetic field mixer $H_M = \sum_{i=1}^n \sigma_i^x$. However, transverse mixers cause quantum state transitions that alter the total Hamming weight of the register, frequently driving the quantum state into infeasible subspaces where vehicle capacities are drastically exceeded.

To preserve vehicle capacity parity, ROUTE/IQ incorporates the **XY-mixer Alternating Operator Ansatz** (Hadfield et al., 2019; Wang et al., 2020):

$$H_{\text{XY}} = \frac{1}{2} \sum_{(i,j) \in E_{\text{boundary}}} \left( \sigma_i^x \sigma_j^x + \sigma_i^y \sigma_j^y \right)$$

The XY-mixer acts as a particle-conserving hop operator:
$$\frac{1}{2} (\sigma_i^x \sigma_j^x + \sigma_i^y \sigma_j^y) \lvert 01 \rangle = \lvert 10 \rangle, \quad \frac{1}{2} (\sigma_i^x \sigma_j^x + \sigma_i^y \sigma_j^y) \lvert 10 \rangle = \lvert 01 \rangle$$
This preserves the exact number of customers assigned to each vehicle throughout the parameterized circuit evolution, restricting quantum exploration strictly to the feasible assignment manifold.

### 2.3 Variational Circuit Architecture
The parameterized state is evolved through $p$ alternating layers ($p=1$ or $p=2$ in production):
$$\lvert \psi(\boldsymbol{\gamma}, \boldsymbol{\beta}) \rangle = \prod_{l=1}^p \exp\left( -i \beta_l H_{\text{XY}} \right) \exp\left( -i \gamma_l H_P \right) \lvert \psi_0 \rangle$$
Where $\lvert \psi_0 \rangle$ is a uniform superposition of valid Hamming weight basis states prepared via Dicke state synthesis.
Variational parameters $(\boldsymbol{\gamma}, \boldsymbol{\beta})$ are classically optimized using COBYLA with a calibrated budget of 32 function evaluations.

---

## 3. Quantum-Inspired Genetic Algorithm (QIGA)

In addition to gate-based QAOA, ROUTE/IQ implements a **Quantum-Inspired Genetic Algorithm (QIGA)** for intermediate-scale boundary problems ($16 < n \le 32$):
- **Qubit Chromosome Representation:** Individual $j$ is represented as a string of $n$ quantum bits:
  $$q_j = \left[ \begin{array}{c|c|c|c} \alpha_1 & \alpha_2 & \dots & \alpha_n \\ \beta_1 & \beta_2 & \dots & \beta_n \end{array} \right], \quad |\alpha_i|^2 + |\beta_i|^2 = 1$$
- **Measurement:** Binary candidate solutions are sampled by observing each qubit with probability $|\beta_i|^2$.
- **Quantum Rotation Gate Update:** Amplitudes are updated toward the current best individual using quantum rotation gates:
  $$\begin{bmatrix} \alpha_i' \\ \beta_i' \end{bmatrix} = \begin{bmatrix} \cos(\Delta \theta_i) & -\sin(\Delta \theta_i) \\ \sin(\Delta \theta_i) & \cos(\Delta \theta_i) \end{bmatrix} \begin{bmatrix} \alpha_i \\ \beta_i \end{bmatrix}$$
  Where rotation angle $\Delta \theta_i$ is determined from a lookup table comparing the sampled bit with the best individual's bit.
