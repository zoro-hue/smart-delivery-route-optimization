# ROUTE/IQ — PHASE P: CLASSICAL-TO-QIGA SEEDING & EVOLUTIONARY DYNAMICS
**Design of Classically-Initialized Quantum-Inspired Evolutionary Optimization on Classical CPU**

---

## 1. Explicit Scientific Attribution Disclosure

> **MANDATORY DISCLOSURE:**  
> The Quantum-Inspired Genetic Algorithm (QIGA / IQGA) is a **purely classical algorithm executed on standard classical CPUs**. It employs mathematical constructs borrowed from quantum mechanics—specifically state vectors in \(\mathbb{C}^2\), superposition probabilities, and unitary rotation matrices—to maintain a compact probabilistic representation of candidate solutions. It does **not** run on quantum hardware (QPUs), does **not** utilize physical quantum entanglement, and makes **no claim** of quantum physical speedup.

In the ROUTE/IQ cooperative hierarchy, QIGA occupies an essential bridge role:
- **QAOA on Qiskit Aer:** Handles micro-clusters (\(K \le 4\), \(N_q \le 16\)) with statevector simulation.
- **QIGA on CPU:** Handles intermediate-scale subproblems (\(K \in [8, 30]\)) where QAOA's \(K^2\) qubit scaling becomes intractable for classical statevector simulators (\(30^2 = 900\) qubits), but where standard classical genetic algorithms suffer from premature convergence.

---

## 2. Q-Bit Representation & Classical Seeding

### 2.1 Standard Q-Bit Chromosome
A classical candidate tour of length \(L\) is represented by an array of \(L \times L\) Q-bits:
\[
\mathbf{q} = \begin{bmatrix}
\alpha_{11} & \alpha_{12} & \dots & \alpha_{1L} \\
\beta_{11} & \beta_{12} & \dots & \beta_{1L}
\end{bmatrix}, \quad |\alpha_{it}|^2 + |\beta_{it}|^2 = 1
\]
where \(|\beta_{it}|^2\) represents the probability that customer \(i\) is visited at step \(t\) of the tour.

In unseeded QIGA, all Q-bits are initialized in maximum uncertainty:
\[
\alpha_{it}^{(0)} = \frac{1}{\sqrt{2}}, \quad \beta_{it}^{(0)} = \frac{1}{\sqrt{2}} \quad \forall i, t \implies P(x_{it} = 1) = 0.50
\]

### 2.2 Classical Tour Seeding Mechanism
In the cooperative hybrid architecture, we seed the Q-bit population using the best classical solutions obtained from Clarke–Wright, 2-opt, and OR-Tools:

Let \(\pi_{\text{classical}} = (\pi(1), \dots, \pi(L))\) be the classical incumbent tour. We partition the population of \(N_{\text{pop}}\) quantum individuals into three strata:

1. **Elite-Seeded Stratum (30% of population):**
   Q-bits are initialized with high probability biased towards the classical solution:
   \[
   \beta_{it}^{(0)} = \begin{cases}
   \sqrt{0.85}, & \text{if } \pi_{\text{classical}}(t) = i \\
   \sqrt{\frac{0.15}{L - 1}}, & \text{otherwise}
   \end{cases}, \quad \alpha_{it}^{(0)} = \sqrt{1 - |\beta_{it}^{(0)}|^2}
   \]
   This centers the probabilistic search around the classical basin while retaining non-zero variance.

2. **Perturbed Classical Stratum (40% of population):**
   Q-bits are biased towards classical 2-opt edge-swapped variants with moderate bias (\(|\beta|^2 = 0.65\)), encouraging exploration of adjacent topological basins.

3. **Uniform Exploration Stratum (30% of population):**
   Q-bits remain in maximum superposition (\(|\alpha|^2 = |\beta|^2 = 0.50\)), preventing premature convergence and maintaining global exploratory pressure.

---

## 3. Quantum Rotation Gate Update Dynamics

### 3.1 Unitary Rotation Matrix
At each generation \(g\), individual Q-bits are updated using a unitary rotation gate \(U(\Delta \theta_{it})\):
\[
\begin{bmatrix}
\alpha_{it}^{(g+1)} \\
\beta_{it}^{(g+1)}
\end{bmatrix} = \begin{bmatrix}
\cos(\Delta \theta_{it}) & -\sin(\Delta \theta_{it}) \\
\sin(\Delta \theta_{it}) & \cos(\Delta \theta_{it})
\end{bmatrix} \begin{bmatrix}
\alpha_{it}^{(g)} \\
\beta_{it}^{(g)}
\end{bmatrix}
\]

### 3.2 Dynamic Rotation Angle Lookup Table
The rotation step size \(\Delta \theta_{it} = s(\alpha_{it}, \beta_{it}) \cdot \theta_{\text{base}}\) is determined by comparing the sampled bit \(x_{it}\) against the corresponding bit \(b_{it}\) in the current global best tour \(B\):

| \(x_{it}\) | \(b_{it}\) | \(f(x) < f(B)\) | \(\Delta \theta_{it}\) Condition | Sign of \(\Delta \theta\) |
| :---: | :---: | :---: | :---: | :---: |
| 0 | 0 | False | None | 0 |
| 0 | 1 | False | Current bit sub-optimal | \(+ \theta_{\text{base}}\) (increase \(\beta\)) |
| 1 | 0 | False | Current bit sub-optimal | \(- \theta_{\text{base}}\) (decrease \(\beta\)) |
| 1 | 1 | False | Optimal alignment | 0 |
| Any | Any | True (New Best Found) | Current individual becomes new best | Accelerate update |

### 3.3 Adaptive Angular Damping
To ensure fine-grained asymptotic convergence, the base rotation angle decays across generations:
\[
\theta_{\text{base}}^{(g)} = \theta_{\max} \left( \frac{\theta_{\min}}{\theta_{\max}} \right)^{g / G_{\max}}, \quad \theta_{\max} = 0.08\pi, \quad \theta_{\min} = 0.005\pi
\]

---

## 4. Diversity Preservation & Catastrophe Operator

A known failure mode of QIGA on routing problems is **amplitude collapse**, where all Q-bit probabilities approach 1.0 or 0.0 before finding the global optimum.

To counteract this, the ROUTE/IQ cooperative engine deploys a **Quantum Catastrophe Operator**:
1. **Population Entropy Metric:**
   \[
   H_{\text{pop}} = -\frac{1}{L^2} \sum_{i=1}^L \sum_{t=1}^L \Big( |\alpha_{it}|^2 \log_2 |\alpha_{it}|^2 + |\beta_{it}|^2 \log_2 |\beta_{it}|^2 \Big)
   \]
2. **Catastrophe Trigger:** If \(H_{\text{pop}} < H_{\text{threshold}}\) for 15 consecutive generations without cost improvement:
   - The elite incumbent tour is preserved.
   - 70% of the non-elite Q-bit population is reset using quantum Hadamard diffusion:
     \[
     \beta_{it} \leftarrow \sqrt{|\beta_{it}|^2 \cdot (1 - \lambda_{\text{cat}}) + 0.5 \lambda_{\text{cat}}}, \quad \lambda_{\text{cat}} = 0.60
     \]
   - This re-injects quantum exploratory entropy without destroying elite memory.

---

## 5. Permutation Repair & Capacity Feasibility Enforcement

Sampling from an \(L \times L\) Q-bit matrix yields binary bitstrings that frequently violate permutation bi-stochasticity (duplicate customer visits or skipped stops).

ROUTE/IQ applies a deterministic **Order-Based Greedy Repair Operator**:
1. Rank all customers by their sampled amplitude \(\beta_{it}\) at each position \(t\).
2. Sequentially assign unvisited customers with highest probability to open route slots.
3. If an accumulated vehicle load exceeds capacity \(Q\), insert a depot return \((0)\) and instantiate a new vehicle route.
4. Verify that all \(N\) customers appear exactly once.

---

## 6. Integration in the Cooperative Hierarchy

```
       [Classical Solvers: OR-Tools, Clarke-Wright, 2-opt]
                                │
                                ▼
         Classical Incumbent Tour Pool (C_0, Routes_0)
                                │
        ┌───────────────────────┴───────────────────────┐
        ▼                                               ▼
  [Micro-Clusters: K <= 4]                    [Macro-Clusters: K in 8..30]
        │                                               │
        ▼                                               ▼
  QAOA on Qiskit Aer (16 Qubits)              Classically-Seeded QIGA (CPU)
        │                                               │
        └───────────────────────┬───────────────────────┘
                                ▼
         Candidate Synthesis & Cooperative Local Search
```

---

## 7. Verification Verdict

Classically-seeded QIGA provides a computationally lightweight, diversity-preserving global search mechanism on classical CPU hardware. By seeding Q-bit amplitudes with classical tours, it avoids starting from zero and can explore topological variants that greedy heuristics miss.

