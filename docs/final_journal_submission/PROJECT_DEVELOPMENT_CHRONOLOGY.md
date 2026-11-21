# ROUTE/IQ Project Development Chronology: Inception to Next-Generation Engine

**Project:** ROUTE/IQ: Intelligent Delivery Route Optimization Using Hybrid Big Data, Quantum Computing, and Cooperative Vehicle Fleet Optimization  
**Institutional Affiliation:** Department of Computer Science and Engineering, SRM University-AP, Amaravati, Andhra Pradesh, India  
**Authors:** J. Jayanth, B. Kaivalya, P. Shyam Sai (Undergraduate Research Scholars)  
**Faculty Research Supervisor:** Dr. Vishnu Prasad Verma  
**Date:** November 21, 2026  

---

## Executive Chronological Overview

The ROUTE/IQ project originated as an undergraduate research initiative (UROP) investigating scalable logistics optimization for high-density metropolitan delivery networks. Over multiple development cycles, the project transformed from an elementary classical heuristic demonstration into an advanced, vehicle-condition-aware cooperative metaheuristic engine combining Apache Spark distributed transformations, variational quantum algorithms, quantum-inspired evolutionary computing, and contextual reinforcement learning.

| Phase | Timeframe | Core Architecture & Paradigm | Key Milestone / Implementation | Forensic Findings & Limitations |
| :--- | :--- | :--- | :--- | :--- |
| **Phase 1: Project Inception** | Initial Phase | Classical CVRP on Open Data | Clarke-Wright savings heuristic, greedy nearest-neighbor, Folium/Leaflet visualization | Basic feasibility established; high route overlaps (>22%); poor vehicle utilization. |
| **Phase 2: Big Data Integration** | Architecture Expansion | Apache Spark Distributed Ingestion | PySpark 4.2.0 integration, RDD spatial bounding-box sweeps, BPR congestion modeling | Successfully ingested >10,000 stops; identified 1.5–2.5s JVM startup bottleneck for small $N$. |
| **Phase 3: Quantum Exploration** | Algorithm Prototyping | Variational Quantum Routing (QAOA) | Qiskit Aer statevector simulation, 2-route QUBO partition, classical 2-opt post-repair | Proved feasibility on subproblems $\le 8$ stops; highlighted exponential statevector simulation cost for $N > 12$. |
| **Phase 4: Quantum-Inspired Search** | Evolutionary Expansion | Quantum-Inspired Genetic Algorithm | Q-bit amplitude representation, dynamic rotation gates directed toward best incumbent | Rapid state exploration; occasional premature convergence to sub-optimal local basins. |
| **Phase 5: Baseline Cooperative Engine** | Multi-Algorithm Assembly | Multi-Solver Candidate Generation | Google OR-Tools, QAOA, QIGA, Tabu Search, Deep VND integrated into single backend | Forensic audit revealed *pseudo-cooperation*: independent execution with zero intermediate cross-algorithm exchange. |
| **Phase 6: Next-Gen Formulation** | Mathematical Realignment | Heterogeneous Fleet Vehicle Condition (HFVRP-VC) | Electrochemical battery fade model ($B_{	ext{usable}} = B_{	ext{nom}} \cdot 	ext{SoH}$), SoC range limits, 15% wear multiplier | Formulated rigorous physics-grounded constraints; addressed critical gap of nominal capacity assumptions. |
| **Phase 7: Next-Gen Implementation** | Algorithmic Innovation | Shared Blackboard & Contextual MAB | Shared candidate pool ($M=16$), Jaccard edge diversity, UCB-1 operator selection with 4-pillar reward | Realized genuine bidirectional co-evolution; enabled operators to mutate and improve each other's candidate solutions. |
| **Phase 8: Guardrail & Empirical Audit** | Hardening & Certification | Proposition 1 Non-Degradation Guardrail | Certified fallback ensuring $\mathcal{D}(S_{	ext{final}}) \le \mathcal{D}(S_{	ext{ortools}})$, comprehensive 9-configuration NYC benchmark suite | Verified $-1.24\%$ fleet distance reduction ($-3.16\%$ at $N=30$), $24.0\%$ latency reduction, and 100% feasibility. |

---

## Detailed Phase Narratives

### Phase 1: Project Inception and Baseline Routing
The project commenced with an investigation of last-mile delivery inefficiencies in urban centers using NYC Open Data. The initial implementation utilized classical heuristics:
- **Algorithms:** Clarke-Wright Savings algorithm and Greedy Nearest Neighbor.
- **Data:** Geocoded customer coordinates in New York City.
- **Outcome:** The engine produced basic valid routes, but routes exhibited severe geometric overlapping, high crossing angles, and uneven vehicle capacity utilization.

### Phase 2: Big Data Architecture and Congestion Modeling
To handle large-scale trip data, the architecture was re-engineered around Apache Spark:
- **Infrastructure:** PySpark 4.2.0 utilizing distributed Resilient Distributed Datasets (RDDs).
- **Traffic Modeling:** Implemented the Bureau of Public Roads (BPR) volume-delay latency function to model congestion dynamics.
- **Key Realization:** While Spark achieved linear throughput scaling for large offline datasets ($>10,000$ points), the JVM startup overhead ($1.5	ext{--}2.5	ext{ s}$) rendered Spark inefficient for sub-second, interactive single-order queries. This led to our architectural separation of batch preprocessing and real-time vectorized routing.

### Phase 3: Variational Quantum Algorithms (QAOA)
Seeking combinatorial search improvements, variational quantum optimization was introduced:
- **Formulation:** Mapped route partitioning to an Ising / QUBO spin glass Hamiltonian.
- **Simulation:** Executed via Qiskit Aer statevector simulation on multi-core CPU.
- **Key Realization:** Directly formulating an entire CVRP graph ($N \ge 30$) requires hundreds of logical qubits, which is intractable on NISQ devices and classical simulators. The breakthrough was designing the *Subproblem Boundary Operator*, which isolates conflict stops ($\le 8$ nodes) along adjacent routes.

### Phase 4: Quantum-Inspired Genetic Algorithm (QIGA)
To explore quantum-style superpositions without the exponential statevector simulation cost:
- **Representation:** Stops encoded as Q-bit probability vectors $|\psi_iangle = lpha_{i0}|0angle + lpha_{i1}|1angle$.
- **Evolution:** Q-gate rotation matrices $U(\Delta 	heta)$ adaptively steer probability amplitudes toward the elite solution.
- **Key Realization:** QIGA exhibited strong global search capabilities but required local intensification operators to polish final permutations.

### Phase 5: The Baseline Cooperative Engine and Forensic Audit
In Phase 5, all solvers were packaged into a unified interface called the "Cooperative Engine". However, our subsequent forensic audit revealed a critical limitation:
- **Pseudo-Cooperation Identified:** Each algorithm (OR-Tools, QAOA, QIGA, Tabu, VND) executed in total isolation. At completion, the engine merely selected the lowest-distance output.
- **Zero Algorithmic Synergy:** QAOA never operated on an OR-Tools candidate; QIGA never refined a Tabu candidate; execution time was the linear sum of all individual solvers.

### Phase 6: Formulation of the HFVRP-VC
Recognizing that real-world commercial fleets are electrifying, we formulated the *Heterogeneous Fleet Vehicle Routing Problem with Vehicle Condition (HFVRP-VC)*:
- Modeled electrochemical battery capacity degradation: $B_{	ext{usable}, k} = B_{	ext{nom}, k} \cdot (	ext{SoH}_k / 100)$.
- Integrated dynamic State of Charge (SoC) and operating range limits.
- Incorporated maintenance condition penalties ($\mu_k = 1.15$ for overdue service).
- Formulated a 4-pillar dimensionless multi-objective scalarization balancing distance, operational cost, energy consumption, and emissions.

### Phase 7: The Next-Generation Cooperative Engine Architecture
To replace pseudo-cooperation with true co-evolution, we developed ROUTE/IQ-NextGen:
- **Shared Candidate Pool Blackboard:** An elite pool ($M=16$) preserving solution ancestry, edge graphs, and multi-objective metrics.
- **Topological Edge Diversity:** A Jaccard edge-distance metric preventing population stagnation.
- **Adaptive Contextual MAB Controller:** A UCB-1 bandit observing problem context and selecting operators dynamically.
- **4-Pillar Multi-Objective Feedback Reward:** Rewarding objective gains, feasibility, and diversity while penalizing execution latency.

### Phase 8: Guardrail Hardening and Publication Validation
To ensure enterprise reliability:
- Formulated and mathematically proved **Proposition 1 (Conditional Non-Degradation Guardrail)**, ensuring by construction that the hybrid cooperative engine never produces a result inferior to Google OR-Tools alone.
- Executed an exhaustive 9-configuration empirical benchmark suite across NYC instances ($N \in [12, 30]$), validating superior routing performance ($-1.24\%$ mean, $-3.16\%$ at $N=30$) and $24.0\%$ lower execution latency.
