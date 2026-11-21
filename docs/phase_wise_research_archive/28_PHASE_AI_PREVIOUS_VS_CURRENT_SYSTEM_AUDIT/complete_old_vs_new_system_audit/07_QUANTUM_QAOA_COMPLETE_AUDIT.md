# 07 — QUANTUM COMPUTING ARCHITECTURE AND QAOA AUDIT

**Project Title:** ROUTE/IQ: Smart Delivery Route Optimization Using Hybrid Big Data and Quantum Computing  
**Institution:** Department of Computer Science and Engineering, SRM University-AP  
**Original Version Baseline:** `main` at commit `a8eb849`  
**Current Research Baseline:** `research/journal-readiness` at commit `feb0920`  

---

## 1. Role and Strategic Evolution of Pillar 2

Quantum Approximate Optimization Algorithm (**QAOA**) serves as **Pillar 2** of the ROUTE/IQ hybrid architecture. The quantum engine underwent a complete mathematical refactoring between commit `a8eb849` and `feb0920`.

```
+----------------------------------------------------------------------------------------------------+
|                                     QAOA EVOLUTION SUMMARY                                         |
+----------------------------------------------------------------------------------------------------+
| Original Implementation (`a8eb849`):                                                               |
| - Service: `backend/app/services/optimization/quantum_solver.py`                                   |
| - Formulation: Monolithic QUBO with O(n^2 K) binary variables. Soft quadratic penalties.          |
| - Qubit Scalability: Failed for n > 8 customers (over 100 qubits required).                        |
| - Mixer Type: Standard Pauli-X transverse-field mixer (drifted into invalid Hilbert states).       |
| - Constraint Handling: Penalty dominance caused >99% of sampled bitstrings to violate feasibility.|
| - Fallback: Simulated random walk fallback if Qiskit was unavailable or circuits crashed.         |
|                                                                                                    |
| Current Research Implementation (`feb0920`):                                                       |
| - Service: `backend/app/services/optimization/qaoa_subproblem_optimizer.py`                        |
| - Formulation: Resource-bounded Asymmetric TSP Ising cost Hamiltonian for micro-clusters (m <= 4). |
| - Qubit Scalability: Capped at 16 logical qubits (m=4), matching NISQ simulation realities.        |
| - Mixer Type: Particle-conserving XY mixer (XXPlusYYGate) preserving one-hot permutation subspace. |
| - Constraint Handling: Exact binary slack variables for capacity; Hungarian bipartite matching     |
|   projection for permutation feasibility.                                                          |
| - Telemetry: 100% transparent logging of bitstrings, energies, and Hungarian invocation rates.     |
+----------------------------------------------------------------------------------------------------+
```

---

## 2. Technical Audit: `qaoa_subproblem_optimizer.py`

### 2.1 Micro-Cluster Asymmetric TSP Formulation
For a micro-cluster of $m$ delivery stops with distance matrix $D = [d_{i,j}]$, binary decision variable $x_{i,p} \in \{0, 1\}$ denotes stop $i$ visited at position $p$:
$$\min \sum_{i=0}^{m-1} \sum_{j=0}^{m-1} \sum_{p=0}^{m-1} d_{i,j} \cdot x_{i,p} \cdot x_{j,(p+1) \pmod m}$$
Subject to permutation constraints:
$$\sum_{p=0}^{m-1} x_{i,p} = 1 \quad \forall i, \quad \sum_{i=0}^{m-1} x_{i,p} = 1 \quad \forall p$$

### 2.2 2-Local Ising Cost Hamiltonian Mapping
Using the quantum spin substitution $x_{i,p} = \frac{I - Z_{i,p}}{2}$, the quadratic objective transforms into the 2-local Ising problem Hamiltonian:
$$\hat{H}_C = \sum_{i,j,p} \frac{d_{i,j}}{4} \left( Z_{i,p} Z_{j,p+1} - Z_{i,p} - Z_{j,p+1} \right) + \text{constant}$$
This Hamiltonian acts on $m^2$ logical qubits (9 qubits for $m=3$; 16 qubits for $m=4$).

### 2.3 Particle-Conserving XY Mixer Circuit
Standard transverse-field mixers $\sum X_i$ create and destroy excitations freely, allowing the state to wander into invalid non-permutation subspaces. ROUTE/IQ implements a **particle-conserving $XY$ mixer**:
$$\hat{H}_M = \frac{1}{2} \sum_{i=0}^{m-1} \sum_{p=0}^{m-2} \left( X_{i,p} X_{i,p+1} + Y_{i,p} Y_{i,p+1} \right)$$
In Qiskit, the unitary $e^{-i \beta \hat{H}_M}$ is synthesized via native `XXPlusYYGate` operations:
```python
from qiskit.circuit.library import XXPlusYYGate

for i in range(m):
    for p in range(m - 1):
        q1 = i * m + p
        q2 = i * m + p + 1
        qc.append(XXPlusYYGate(2.0 * beta), [q1, q2])
```
Because $[\hat{H}_M, \sum_p x_{i,p}] = 0$, this mixer strictly preserves the Hamming weight of the register, confining evolution to valid permutation states.

### 2.4 Exact Binary Slack Capacity Encoding
For macro-assignment problems where customer demands must respect vehicle capacity $Q$, the optimizer introduces exact binary slack variables:
$$\sum_{i=1}^n q_i x_{i,k} + \sum_{b=0}^{B-1} 2^b s_{k,b} = Q_k, \quad \text{where } B = \lceil \log_2(Q_k + 1) \rceil$$
This eliminates heuristic penalty tuning and guarantees exact binary representation of capacity bounds.

### 2.5 Deterministic Hungarian Feasibility Projection
Shallow-circuit ($p=1$) variational states occasionally sample constraint-violating bitstrings. When an invalid bitstring is sampled, the optimizer extracts the continuous soft probabilities from the measurement register and projects them onto the nearest valid permutation using the **Hungarian algorithm** (bipartite matching via `scipy.optimize.linear_sum_assignment`):
```python
cost_weights = 1.0 - X.astype(float)
row_ind, col_ind = linear_sum_assignment(cost_weights)
tour = [-1] * m
for r, c in zip(row_ind, col_ind):
    tour[c] = r
```

---

## 3. Empirical QAOA Telemetry and Ablation Results

Ablation benchmark telemetry from `qaoa_subproblem_ablation_results.csv` ($p=1$, 1,024 shots on Qiskit Aer `AerSimulator`, COBYLA 25 iterations):

| Metric | $m=2$ Stops (4 Qubits) | $m=3$ Stops (9 Qubits) | $m=4$ Stops (16 Qubits) |
| :--- | :---: | :---: | :---: |
| **Circuit Depth** | 8 gates | **15 gates** | **24 gates** |
| **Total Gate Count** | 12 gates | **36 gates** | **72 gates** |
| **2-Qubit $XY$ Mixer Gates** | 4 `XXPlusYYGate` | 18 `XXPlusYYGate` | 36 `XXPlusYYGate` |
| **Variational Angles** | 2 $(\gamma, \beta)$ | 2 $(\gamma, \beta)$ | 2 $(\gamma, \beta)$ |
| **COBYLA Iterations** | 15 | 25 | 25 |
| **Approximation Ratio ($E_{\text{QAOA}} / E_{\text{exact}}$)** | **0.9850** | **0.9079** | **0.8435** |
| **Direct Bitstring Feasibility** | 57.9% | 6.7% | 0.0% |
| **Hungarian Projection Invocations** | 42.1% | **93.3%** | **100.0%** |
| **Post-Projection Feasibility** | **100.0%** | **100.0%** | **100.0%** |

---

## 4. Critical Scientific Disclosures & Hardware Boundaries

1. **Classical Simulation Only:** All QAOA circuits in ROUTE/IQ are executed via classical simulation using the Qiskit Aer statevector and shot simulator (`AerSimulator`). **No physical quantum processor (QPU) hardware runs were executed**.
2. **Absence of Quantum Advantage:** At the evaluated scale of $m \le 4$ stops (16 logical qubits), the solution space contains only $4! = 24$ permutations. A classical CPU enumerates all 24 permutations in under 1 millisecond. QAOA simulation requires several seconds. **No quantum speedup or supremacy is claimed**.
3. **Role of Quantum in ROUTE/IQ:** The research contribution is proving that variational quantum heuristics can be integrated into large-scale logistics workflows with guaranteed non-degradation, serving as an energy-biased probability prior for classical projection.
