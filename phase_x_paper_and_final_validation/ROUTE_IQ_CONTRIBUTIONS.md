# ROUTE/IQ: Research Novelty and Scientific Contributions

## 1. Summary of Scientific Contributions

This paper makes four verifiable, technically implemented contributions to the field of hybrid big data and quantum-classical combinatorial optimization:

### Contribution 1: Scalable Dual-Pillar Cooperative Architecture
We design and implement a formal two-pillar framework combining **Apache Spark 4.2.0** and **QAOA / Qiskit 2.4.1**. Instead of attempting a monolithic, computationally intractable quantum routing circuit, Apache Spark decomposes large delivery graphs into localized, capacity-aware two-vehicle boundary customer subproblems ($N \le 16$), mapping them onto parameterized Ising Hamiltonians suitable for NISQ quantum co-processors.

### Contribution 2: Exact Ising Derivation and The Feasibility Gap Discovery
We provide a term-by-term derivation from binary decision variables to Pauli-$Z$ spin operators ($Z_i \in \{-1, +1\}$), incorporating mutual spatial affinity and quadratic load balance penalties. Crucially, we identify and experimentally document the **Capacity Feasibility Gap**: while 100% of sampled computational bitstrings represent valid binary set partitions, **55.08% of raw sampled states violate physical vehicle capacity bounds ($Q > C$)**. We resolve this by designing a **deterministic classical capacity repair operator** that guarantees 100% physical feasibility with minimal cost penalty.

### Contribution 3: The Incumbent-Preserving Guardrail (Proposition 1)
We formulate and mathematically prove the **Proposition 1 Monotonic Guardrail**, establishing that candidate quantum routes are only committed to the final dispatch schedule if their fully sequenced distance strictly improves or matches the classical incumbent ($\text{Cost}(R_{\text{final}}) \le \text{Cost}(R_{\text{incumbent}})$). This architecture eliminates all commercial regression risk, transforming stochastic quantum exploration into an unconditionally safe enterprise asset.

### Contribution 4: Exhaustive Causal Ablation and Boundary Analysis
Through 150 controlled evaluations and 40 out-of-sample boundary experiments, we provide the first rigorous, unvarnished causal decomposition of simulated QAOA in vehicle routing:
- Proving that downstream classical VND accounts for **87.3%** of total route distance shortening.
- Showing that QAOA provides **conditional candidate-generation value** in 10.0%–26.7% of problem instances, but that its incremental contribution beyond strong classical VND fails to reach parametric statistical significance ($p = 0.0892$).
- Demonstrating that classical Kernighan-Lin graph bisection outperforms simulated QAOA in solution quality while executing **$19.7\times$ faster**.
