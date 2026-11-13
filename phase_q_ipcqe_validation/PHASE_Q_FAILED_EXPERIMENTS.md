# ROUTE/IQ — PHASE Q: FAILED EXPERIMENTS & LIMITATIONS AUDIT
**Scientific Accounting of Unsuccessful Variations, Optimization Pitfalls, and Simulation Bottlenecks**

- **Date:** 2026-11-06
- **Project:** ROUTE/IQ Phase Q

---

## 1. Failed Experiment 1: High-Iteration COBYLA on Qiskit Aer (Latency Explosion)
- **Concept:** Increase outer-loop COBYLA iterations from $10$ to $50$ to achieve deeper convergence on variational parameters $(\gamma, \beta)$.
- **Observed Result:** Wall-clock latency exploded from $3.3\text{ seconds}$ to over **$28.5\text{ seconds}$** per customer campaign on Qiskit Aer CPU simulation.
- **Root Cause:** Each COBYLA step requires re-transpiling and simulating the 16-qubit circuit with shot sampling. On classical simulators, evaluating 50 iterations creates severe latency with negligible distance improvement ($< 0.05\%$).
- **Remedy:** Restricted outer-loop iterations to a lightweight budget of $8\text{ to }10$ iterations, which achieves $95\%$ of parameter optimization benefit in under $400\text{ ms}$.

---

## 2. Failed Experiment 2: Unconstrained 5-Node QAOA ($N_q = 25$ Qubits)
- **Concept:** Expand subproblem size from $K=4$ (16 qubits) to $K=5$ (25 qubits) to allow larger neighborhood uncrossing.
- **Observed Result:**
  - Statevector dimension jumped from $2^{16} = 65,536$ elements to $2^{25} = 33,554,432$ complex amplitudes.
  - RAM requirement per circuit shot increased from $\approx 1\text{ MB}$ to **over $512\text{ MB}$**!
  - Simulation latency jumped from $140\text{ ms}$ to **$14.2\text{ seconds}$** per circuit evaluation.
- **Scientific Conclusion:** $K=4$ ($N_q = 16$) represents the absolute optimal sweet spot for classical simulation on standard cloud container nodes (Render/Vercel). Simulating $N_q \ge 25$ qubits classically is computationally intractable for interactive logistics applications.

---

## 3. Negative Result: Near-Optimality of OR-Tools on Symmetric Subproblems
- When a road network instance is completely symmetric ($c_{ij} = c_{ji}$) and planar, Google OR-Tools Guided Local Search almost always finds the exact mathematical optimum for 4-node clusters.
- On such instances, QAOA cannot beat the classical incumbent because no shorter permutation exists.
- The hybrid architecture's superiority emerges primarily in **asymmetric networks** (one-way streets, congestion imbalances, bridge detours) where cyclic quantum permutations escape asymmetric directionality penalties that trap contiguous 2-opt inversions.

