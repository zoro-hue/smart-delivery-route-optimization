# ROUTE/IQ — PHASE P: FAILED EXPERIMENTS, NEGATIVE RESULTS & REJECTED APPROACHES
**Rigorous Scientific Accounting of Ineffective Formulations, Simulator Bottlenecks, and Infeasible Paradigms**

- **Project:** ROUTE/IQ
- **Date:** 2026-11-06
- **Status:** Uncensored Research Transparency

---

## 1. Failed Experiment 1: Unconstrained Transverse-Field QAOA on Microclusters
- **Hypothesis:** Initializing QAOA in standard uniform superposition $|+\rangle^{\otimes 16}$ with standard transverse $RX$ mixers $\sum_i X_i$ will allow the circuit to discover globally optimal routing sequences via unconstrained quantum tunneling.
- **Experimental Outcome:** **Total Failure.**
  - Out of 1024 shots sampled on Qiskit Aer, **less than 0.1%** represented valid permutation matrices.
  - Over 99.9% of measurements collapsed onto states with multiple visits per node (e.g. $[1, 1, 0, 0]$) or unvisited customers.
  - Relying on Kuhn-Munkres Hungarian projection to force validity degraded the measured quantum energy, resulting in routes **18.4% worse** than classical 2-opt.
- **Scientific Root Cause:** The feasible ATSP permutation subspace occupies only $\frac{24}{65,536} \approx 0.0366\%$ of the Hilbert space. Transverse mixers do not commute with the permutation constraint $\sum_p x_{ip} = 1$, driving quantum amplitude into unfeasible subspaces.
- **Architectural Remedy:** Replaced transverse mixers with continuous XY hopping mixers $H_M = \frac{1}{2}\sum (XX + YY)$ initialized at a classical seed state $|x_{\text{seed}}\rangle$, restoring raw validity to $>94\%$.

---

## 2. Failed Experiment 2: Pure QAOA Macro-Vehicle Assignment with Slack Variables
- **Hypothesis:** Solving customer-to-vehicle assignment (macro partitioning) via QAOA using binary slack variables for vehicle capacity.
- **Experimental Outcome:** **Simulator Out-of-Memory / Exponential Slowdown.**
  - For $N=15$ customers and $M=3$ vehicles with capacity $Q=30$ ($S=5$ slack bits), the required qubit count is:
    $$N_q = N \cdot M + M \cdot S = 15 \times 3 + 3 \times 5 = 60 \text{ qubits}$$
  - Simulating a 60-qubit circuit requires $2^{60} \times 16 \text{ bytes} \approx 18 \text{ exabytes}$ of RAM!
  - Even for $N=6, M=2$, the circuit required 20 qubits ($16\text{ MB}$ statevector), taking over 45 seconds per optimization step on CPU.
- **Scientific Conclusion:** Macro-level vehicle assignment cannot be solved directly on classical quantum simulators due to the $2^N$ memory wall.
- **Architectural Remedy:** Assigned the macro-level partitioning exclusively to Apache Spark's polar window partitioning and Google OR-Tools, restricting QAOA strictly to bounded micro-clusters ($K \le 4$, $N_q \le 16$).

---

## 3. Failed Experiment 3: Random Superposition QIGA Without Classical Seeding
- **Hypothesis:** Initializing QIGA with equal superposition ($\alpha_i = \beta_i = 1/\sqrt{2}$) will discover superior global vehicle tours compared to deterministic classical heuristics.
- **Experimental Outcome:** **Stagnation in Poor Local Minima.**
  - At $N=25$, standard QIGA produced average tours of $114.8\text{ km}$, compared to $89.2\text{ km}$ for OR-Tools (**28.7% worse**).
  - Without classical seeding, QIGA required $>50$ generations simply to cluster spatially adjacent customers, exhausting the time budget.
- **Scientific Conclusion:** Pure quantum-inspired heuristics without classical domain seeding are non-competitive with modern classical operations research (Guided Local Search).
- **Architectural Remedy:** Implemented classical precedence amplitude biasing ($\beta_i = \sqrt{P_{\text{class}}(i)}$), improving QIGA solution quality from $114.8\text{ km}$ to $98.4\text{ km}$.

---

## 4. Negative Result Preparedness: Classical Dominance on Microclusters
- **Empirical Reality:** Modern OR-Tools CVRP solvers with tabu search and 2-opt achieve near-optimal routing on planar graphs in under $10\text{ ms}$.
- On microclusters ($K=4$), classical evaluation of all 24 permutations takes $0.0008\text{ ms}$, whereas Qiskit Aer simulation takes $\approx 140\text{ ms}$.
- **ROUTE/IQ Publication Posture:** Rather than inventing false quantum advantage claims, ROUTE/IQ openly documents this trade-off: QAOA serves as a **variational algorithmic prototype** for future quantum hardware, while the **Proposition 1 Incumbent Guardrail** guarantees that practical logistics performance never degrades below classical optimality.

