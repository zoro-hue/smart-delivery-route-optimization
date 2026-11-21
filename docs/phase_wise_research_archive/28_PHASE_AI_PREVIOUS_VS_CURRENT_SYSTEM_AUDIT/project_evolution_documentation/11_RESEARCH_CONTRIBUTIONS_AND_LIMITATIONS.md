# 11 — RESEARCH CONTRIBUTIONS AND SCIENTIFIC LIMITATIONS

**Project:** ROUTE/IQ — Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing  
**Institution:** SRM University-AP, Department of Computer Science and Engineering  
**Authors:** J. Jayanth, B. Kaivalya, P. Shyam Sai  
**Faculty Supervisor:** Dr. Vishnu Prasad Verma (`vishnu.v@srmap.edu.in`)  
**Git Baseline Commit (`main`):** `a8eb849`  
**Current Research Branch:** `research/journal-readiness` (Commit: `960dfdb`)  
**Target Journal:** *IEEE Transactions on Quantum Engineering*  

---

## 1. Context and Objective Academic Framing

The field of quantum computing in operations research frequently suffers from either excessive optimism (unsubstantiated claims of "quantum supremacy" or exponential speedup on NISQ hardware) or dismissive skepticism (arguing that classical heuristics render quantum research irrelevant).

ROUTE/IQ was developed to establish an **objective, scientifically grounded middle ground**. The project demonstrates how quantum variational algorithms can be legitimately integrated into modern enterprise big data architectures today, operating within verified NISQ hardware limits while providing rigorous mathematical guarantees against solution degradation.

---

## 2. Verified Research Contributions

The following six contributions have been independently verified through source code implementation, mathematical proof, and reproducible empirical benchmarking:

### Contribution 1: Dual-Pillar Hybrid Big Data + Quantum Computing Architecture
ROUTE/IQ designs and implements a modular, dual-pillar computational framework that eliminates the disconnect between classical data engineering and quantum optimization. By pairing **Apache Spark 4.2.0** (Pillar 1) for large-scale data ingestion, spatial decomposition, and traffic impedance with **QAOA on Qiskit Aer** (Pillar 2) for combinatorial subproblem exploration, the system provides an end-to-end blueprint for hybrid logistics computing.

### Contribution 2: Active Spark Preprocessing with Calibrated BPR Traffic Impedance
Unlike conventional prototypes where big data tools are relegated to offline storage or omitted entirely during routing, ROUTE/IQ embeds Apache Spark directly into the active runtime routing loop (`SparkRoutingPreprocessor`). The preprocessor ingests empirical NYC DOT hourly traffic volumes across 54,000 road links, applies the non-linear Bureau of Public Roads (BPR) volume-delay formulation, and executes capacity-constrained polar sweep partitioning in $O(N \log N)$ distributed runtime, successfully validated up to 50,000 delivery orders.

### Contribution 3: Resource-Bounded QAOA Micro-Cluster Candidate Generator
To prevent the exponential qubit explosion that cripples monolithic VRP formulations, ROUTE/IQ bounds quantum optimization to structured micro-clusters of $m \le 4$ stops (up to 16 logical qubits). The formulation introduces:
- Mapping of the Asymmetric TSP to a 2-local Ising Cost Hamiltonian.
- Implementation of **particle-conserving $XY$ mixers** (`XXPlusYYGate`) to restrict quantum state evolution to the physical one-hot permutation subspace.
- **Exact binary slack capacity encoding** ($\sum 2^b s_{k,b}$) to eliminate arbitrary penalty parameter tuning.
- Deterministic **Hungarian projection** to guarantee permutation feasibility on shallow variational circuits.

### Contribution 4: Quantum-Guided Adaptive Reconstruction (QGAR)
ROUTE/IQ develops the QGAR bridge (`QuantumGuidedAdaptiveRouter`) to synthesize quantum subproblem candidates into full fleet routes. QGAR introduces:
- **Quality-Aware Candidate Selection:** Scores measurement bitstrings using Boltzmann energy weights ($w_c \propto e^{-\Delta E_c / T}$) rather than raw shot frequency, preventing high-frequency suboptimal states from dominating.
- **Planar Crossing Regularizer:** Employs geometric orientation determinants to eliminate self-intersecting loops from reconstructed vehicle tours.
- Delivers a statistically significant **$4.10\%$ distance reduction** over the earlier Phase H hybrid pipeline ($W = 194.0, p = 0.000161, r_B = +0.848$).

### Contribution 5: Monotonic Non-Degradation Guaranteed by Construction
A fundamental barrier to deploying quantum heuristics in commercial logistics is the risk that stochastic quantum noise or shallow-circuit suboptimality will yield a route significantly worse than a standard deterministic plan. ROUTE/IQ proves and enforces **Proposition 1**: by embedding an **End-to-End Route Certification Guardrail**, the system certifies that:
$$C(R_{\text{final}}) \le C(R_{\text{spatial}}) + 10^{-4}\text{ km}$$
Across all 20 paired benchmark trials, QGAR achieved 14 wins, 6 ties, and **0 losses** against the spatial baseline ($r_B = +1.000, p = 0.000491$).

### Contribution 6: Reproducible, Adversarially Audited Experimental Suite
The codebase includes fully automated, parameter-stable benchmark harnesses (`run_phase_i_qgar_benchmark.py`, `run_bigdata_scaling_audit.py`, `run_qaoa_subproblem_ablation.py`) providing paired non-parametric Wilcoxon tests, bootstrap 95% confidence intervals, rank-biserial effect sizes, and Benjamini-Hochberg FDR adjustments.

---

## 3. Explicit Scientific & Engineering Limitations

In accordance with academic research integrity, the following practical and theoretical limitations are explicitly documented:

### Limitation 1: Classical Simulation of Quantum Circuits (No Physical QPU)
All QAOA circuits in ROUTE/IQ are executed on classical CPU hardware using the Qiskit Aer statevector and shot simulator (`AerSimulator`). While the circuits strictly adhere to physical gate sets and connectivity constraints suitable for IBM Quantum Eagle and Heron processors, **no physical QPU hardware runs have been performed**.

### Limitation 2: Absence of Quantum Advantage or Supremacy
ROUTE/IQ **does not achieve or claim quantum computational advantage or speedup**. At the evaluated scale of $m \le 4$ stops (16 logical qubits), the entire combinatorial state space consists of only $4! = 24$ permutations. A classical CPU can enumerate all 24 permutations in under 1 millisecond, whereas variational QAOA simulation requires several seconds of classical parameter optimization and shot sampling.

### Limitation 3: Superiority of Classical State-of-the-Art Solvers
Empirical benchmarking demonstrates that mature classical optimization engines significantly outperform the current hybrid quantum prototype in raw route distance:
- **Google OR-Tools Guided Local Search** produces routes that are **$21.02\%$ shorter** than QGAR ($W = 0.0, p = 0.000002, r_B = -1.000$).
- **Clarke-Wright + 2-opt** produces routes that are **$21.35\%$ shorter** than QGAR ($r_B = -1.000$).
- **RB-QCD Decomposition** produces routes that are **$14.77\%$ shorter** than QGAR ($r_B = -0.971$).
Classical metaheuristics optimize across the entire multi-vehicle fleet simultaneously, whereas ROUTE/IQ decomposes the problem into localized sectors to accommodate NISQ qubit ceilings.

### Limitation 4: Single-Workstation Spark Execution (`local[*]`)
While Spark batch scaling was validated up to 50,000 orders in 22 seconds, all tests were executed on a single multi-core workstation using `local[*]`. Distributed execution across a multi-node cluster connected via `spark://` has not been benchmarked.

### Limitation 5: High-Throughput Batch Processing vs. Real-Time Streaming
The current preprocessor operates on discrete dispatch batches submitted via REST endpoints. It does **not** implement continuous message streaming via Apache Kafka or Spark Structured Streaming. Real-time dynamic re-routing of in-transit vehicles during delivery execution remains future work.

### Limitation 6: Planar Crossing Regularizer vs. Asymmetric Graph Topology
The planar crossing regularizer is derived from 2D Euclidean geometry. In real-world urban road networks governed by one-way streets, bridge bottlenecks, and non-linear BPR congestion delay, the triangle inequality does not hold. In rare cases, eliminating a 2D crossing can force a vehicle into a congested detour (as observed in Trial 0 where an uncrossed tour was $+0.7\%$ longer in cost).

### Limitation 7: Publication and Intellectual Property Status
The manuscript is currently prepared for faculty supervisor review and planned submission to *IEEE Transactions on Quantum Engineering*. Journal acceptance, formal peer review sign-off, and intellectual property/patentability remain unestablished.
