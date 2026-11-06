# ROUTE/IQ: Research Paper Abstract

**Title Proposal**:  
**ROUTE/IQ: A Cooperative Big Data and Quantum-Assisted Architecture for Capacitated Vehicle Routing**

**Authors**:  
Research Team, SRM University-AP  
Supervisor: Dr. Vishnu Prasad Verma, Department of Computer Science and Engineering, SRM University-AP

---

### Abstract

The Capacitated Vehicle Routing Problem (CVRP) is a fundamental $\mathcal{NP}$-hard combinatorial optimization challenge central to urban freight logistics. While classical metaheuristics scale effectively to thousands of delivery nodes, recent advances in quantum computing have prompted interest in applying the Quantum Approximate Optimization Algorithm (QAOA) to vehicle routing. However, direct quantum formulations suffer from severe qubit overhead, invalid permutation states, and poor constraint satisfaction. In this work, we present **ROUTE/IQ**, a cooperative hybrid architecture built upon two principal computational pillars: **Apache Spark 4.2.0** for large-scale geospatial ingestion, spatial clustering, and boundary subproblem isolation; and **QAOA / Qiskit 2.4.1** for optimizing two-vehicle boundary customer trade-offs mapped to 16-qubit Ising Hamiltonians. To address the physical realities of quantum sampling, the architecture integrates a **deterministic classical capacity repair operator** and an **incumbent-preserving acceptance guardrail** (Proposition 1) that unconditionally certifies non-degradation against classical baselines. 

Through rigorous, multi-phase experimental benchmarks across 150 evaluations, we independently audit and causally decompose the system's performance. Our results establish that: (1) downstream algorithmic Variable Neighborhood Descent (VND) accounts for 87.3% of the total route distance reduction ($p = 0.000015$); (2) QAOA exhibits conditional candidate-generation utility, discovering advantageous non-convex boundary cuts in 10.0% to 26.7% of instances; (3) however, QAOA's incremental improvement beyond classical VND fails to achieve statistical significance ($t = 1.8266, p = 0.089152$); and (4) classical Kernighan-Lin graph bisection achieves superior complete fleet distances (540.07 km vs 544.20 km) while running $19.7\times$ faster. On held-out instances, running QAOA on every subproblem yielded only a 0.11% distance reduction while nearly doubling runtime. We provide a transparent, scientifically honest assessment of NISQ quantum optimization for logistics, establishing a reproducible cooperative baseline that eliminates commercial degradation risk while delineating the exact boundaries of practical quantum utility.
