# Deliverable 13: Phase U Failed Experiments and Negative Findings

## 1. Scientific Integrity Policy

Scientific integrity requires transparently documenting all negative results, rejected hypotheses, and experimental failures. The following investigations were tested and refuted during Phase U:

---

## 2. Documented Negative Findings

### Negative Finding 1: Unrepaired QAOA Feasibility Fallacy
- **Hypothesis**: Tuning the quadratic capacity penalty $\lambda_C$ to high values ($\lambda_C \ge 10.0$) in the Ising Hamiltonian would allow standard transverse mixer QAOA ($H_M = \sum X_i$) to consistently sample capacity-feasible partitions.
- **Experimental Result**: FAILED. When $\lambda_C$ was increased beyond 5.0, the spectrum of the cost Hamiltonian became dominated by penalty terms, washing out the relative spatial routing signals $w_{ij}$ and $h_i$. The circuit converged to trivial degenerate solutions (e.g., placing all load on one vehicle or stalling in local minima), while raw capacity feasibility remained below 60%.
- **Architectural Decision**: Rejected unconstrained QAOA. Retained classical deterministic capacity repair as mandatory post-processing.

### Negative Finding 2: Full-Fleet Monolithic Quantum Partitioning
- **Hypothesis**: Formulating a single 64-qubit or 128-qubit QUBO to partition all 50 Manhattan customers across 4 vehicles simultaneously.
- **Experimental Result**: FAILED. Classical statevector simulation of 64 qubits is computationally impossible on classical workstations ($2^{64}$ amplitudes require $\approx 1.8 \times 10^{19}$ bytes of RAM). Even shot-based sampling with matrix product states (MPS) resulted in catastrophic optimization failure due to barren plateaus in high-dimensional parameter spaces.
- **Architectural Decision**: Rejected monolithic fleet partitioning. Retained Apache Spark spatial clustering to isolate localized 12–16 customer boundary subproblems.

### Negative Finding 3: Replacing OR-Tools Completely with QAOA
- **Hypothesis**: Using QAOA as a standalone, self-sufficient routing engine without classical warm-start or incumbent guardrails.
- **Experimental Result**: FAILED. Without OR-Tools / Clarke-Wright seeding, raw QAOA produces complete route distances 15%–40% longer than classical baselines, with runtimes 10x–50x slower due to classical variational loop overheads.
- **Architectural Decision**: Enforced the Proposition 1 Guardrail unconditionally.
