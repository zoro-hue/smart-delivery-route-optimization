# PHASE AB DELIVERABLE 4: PILLAR 2 — QUANTUM COMPUTING OPTIMIZATION ENGINE

## Project: ROUTE/IQ — Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing
**Institution:** SRM University-AP | **Supervisor:** Dr. Vishnu Prasad Verma

---

## 1. Role of Quantum Computing in ROUTE/IQ

The Quantum Computing Pillar within ROUTE/IQ implements the **Quantum Approximate Optimization Algorithm (QAOA)** using Qiskit 2.4.1.

In the unified cooperative architecture, QAOA is positioned as a **stochastic partition candidate generator**. It explores non-local bipartition cuts across the 16-qubit boundary Ising state space that might be overlooked by greedy local hill-climbing heuristics.

---

## 2. Mathematical Formulation & Quantum Circuits

### Boundary Ising Hamiltonian
Given $N$ boundary customers with symmetric affinity weights $W_{ij} = \frac{5.0}{D_{ij} + 0.5}$, centroid distance offsets $h_i$, and payload demands $d_i$:
$$H_C = \sum_{i < j} J_{ij} Z_i Z_j + \sum_i h_i Z_i + \lambda_C \left( \sum_i d_i Z_i - \Delta Q \right)^2$$
Where $Z_i$ is the Pauli-$Z$ operator acting on qubit $i$.

### Mixer Hamiltonians
1. **Transverse-Field Mixer ($H_M = \sum_i X_i$):**
   Standard unconstrained mixer exploring the complete Hilbert space $\mathcal{H} = (\mathbb{C}^2)^{\otimes N}$ of dimension $2^N = 65,536$.
2. **Subspace XY-Mixer ($H_M = \sum_{(i,j) \in E} (X_i X_j + Y_i Y_j)$):**
   Preserves total Hamming weight $\sum_i s_i = K_{\text{target}}$, restricting evolution to the subspace of balanced bipartitions and dramatically boosting capacity feasibility from $41.2\%$ to $89.5\%$.

### Circuit Execution Modes
- **Statevector Simulation Mode:**
  Exact quantum state evolution $|\psi(\vec{\gamma}, \vec{\beta})\rangle = e^{-i\beta H_M} e^{-i\gamma H_C} |+\rangle^{\otimes N}$ computed via Qiskit's `Statevector` class, providing noise-free probability distribution sampling.
- **Fast Mode:**
  Evaluates diagonal phase operators directly using vectorized NumPy state array exponentiation, accelerating simulated QAOA execution from $644.85\text{ ms}$ down to $3.34\text{ ms}$ per 512 samples.
- **Hardware Circuit Preparation:**
  Compiles circuits to IBM Eagle/Heron Heavy-Hex coupling graphs using basis gates $\{CZ, \sqrt{X}, X, RZ\}$, complete with dynamic decoupling pulses and readout error mitigation filters ready for real QPU job submission.

---

## 3. Standardized Candidate Generation Interface

Implemented in [`QAOACandidateGenerator`](file:///d:/UROP/smart-delivery-route-optimization/phase_ab_cooperative_optimization_engine/engine/candidate_generators.py):

```python
class QAOACandidateGenerator(BaseCandidateGenerator):
    """QAOA candidate generator operating under strict candidate budget rules."""
    
    def generate(
        self,
        Q: np.ndarray,
        demands: np.ndarray,
        h_diff: np.ndarray,
        cap_a: float,
        cap_b: float,
        budget_evals: int = 512,
        time_budget_ms: float = 50.0,
        seed: int = 42
    ) -> CandidateGenerationResult:
        ...
```

### Key Performance Telemetry (Phase AB Benchmark)
- **Total Candidates Evaluated:** 512 per subproblem instance.
- **Candidate Diversity:** 8 to 22 unique bitstrings per sampling batch.
- **Capacity Compliance (XY-Mixer):** 89.5% initial compliance.
- **Proposition 1 Acceptance Rate:** **30.0%** (9 of 30 subproblems accepted; 70% rejected due to classical incumbent superiority).
- **Average Fleet Distance (OR-Tools + QAOA + VND):** **606.36 km** (vs OR-Tools + Tabu + VND: **595.45 km**).
