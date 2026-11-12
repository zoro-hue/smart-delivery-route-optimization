# ROUTE/IQ — RESEARCH CONTRIBUTIONS, ENGINEERING ACHIEVEMENTS & SCIENTIFIC LIMITATIONS
**Objective Demarcation of Scientific Novelty, Negative Results & Operational Boundaries**
**Repository:** `D:\UROP\smart-delivery-route-optimization`  
**Current Branch:** `research/phase-ae-backend-integration`  
**Baseline Main:** `a8eb849988201d7929566f331c1ae3afac09b632`

---

## 1. Demarcation: Research Contributions vs Engineering Contributions

To maintain academic integrity during viva and peer review, ROUTE/IQ strictly distinguishes scientific contributions from software engineering improvements:

| Dimension / Area | Genuine Scientific / Methodological Contribution | Software Engineering & Integration Achievement |
|---|---|---|
| **Hybrid Classical-Quantum Optimization** | Formulating the **Cooperative Optimization Paradigm** with the **Proposition 1 Non-Degradation Guardrail**, proving mathematically that experimental quantum heuristics can be integrated into production routing without operational degradation risk ($C(S_{\text{coop}}) \le C(S_{\text{incumbent}})$). | Integrating PySpark 4.2.0, Qiskit 2.4.1, and Google OR-Tools 9.15 into a single asynchronous FastAPI service running on Python 3.14.2. |
| **Spatial Graph Decomposition** | Developing the **Centroid Polar-Angle Partitioning with Boundary Interface Extraction** to reduce large-scale road routing instances into NISQ-compatible subproblems ($|B| \le 8$) specifically targeting route-crossing inefficiencies. | Loading OpenStreetMap GraphML (54,128 nodes) into NetworkX with an $O(1)$ spatial coordinate snapping cache. |
| **Adaptive Solver Selection** | Applying Multi-Armed Bandit (MAB UCB-1) credit assignment to dynamically allocate search iterations between quantum variational circuits, Tabu search, and stochastic operators based on empirical boundary improvement deltas. | Implementing parallel execution of multiple solvers via Python's `ThreadPoolExecutor` and formatting uniform JSON response schemas. |
| **Fleet Feasibility & Invariants** | Formalizing the **Universal Delivery Coverage Invariant ($R == I$)** and proving the **Fleet Feasibility Lower Bound ($K_{\min} \ge \lceil D/Q \rceil$)** to prevent partial solutions from reporting artificially low objective costs. | Implementing the deterministic capacity-aware cheapest-insertion repair function in `route_validator.py`. |
| **Operational Resource Tracking** | Formalizing the distinction between theoretical asymptotic complexity ($\mathcal{O}$) and empirical multi-core process profiling. | Implementing concurrent runtime sampling using `psutil.Process().memory_info().rss`, `tracemalloc`, and high-resolution monotonic clocks. |
| **Dashboard & UI Experience** | Validating that complex dual-pillar telemetry can be communicated clearly to logistics dispatchers through side-by-side scorecard comparisons. | Building the dark glassmorphic React 19 / Vite / TailwindCSS / Leaflet interface with dynamic light/dark theme persistence. |

---

## 2. Comparison with Conventional Route Optimization Systems

| Workflow Dimension | Conventional Commercial / Open-Source System (e.g. standard OR-Tools / VROOM / OSRM) | ROUTE/IQ Hybrid Big Data + Quantum Cooperative Architecture (Phase AE) |
|---|---|---|
| **Data Ingestion** | Reads CSV/JSON customer orders; relies on pre-computed distance matrices or simple routing engines. | Ingests multi-source urban big data (traffic volume, historical weather, road graphs, FHV active fleets) with clean schema validation (0% missing). |
| **Spatial Scaling** | Solves CVRP globally on the full customer graph; computation scales quadratically $\mathcal{O}(N^2)$ or cubically with $N$. | Decomposes large instances via Apache Spark polar-angle spatial cuts, extracting localized boundary interfaces for focused combinatorial search. |
| **Solver Selection** | Dispatches a single chosen engine (e.g. pure Clarke-Wright or pure Guided Local Search). | Adaptive portfolio selection: Multi-Armed Bandit (MAB UCB-1) dynamically distributes search effort among classical metaheuristics and quantum variational circuits. |
| **Quantum Capability** | None. Standard commercial routing systems do not include quantum circuit formulations. | Includes parameterized QAOA with cost Hamiltonian $H_C$ and XY mixers formulated on boundary subproblems (classically simulated via Qiskit 2.4.1). |
| **Safety Guardrail** | If a stochastic heuristic gets stuck in a poor local minimum, the inferior route is returned. | **Proposition 1 Guardrail:** Compares candidate against verified classical incumbent; automatically rejects any degrading or invalid candidate. |
| **Coverage Integrity** | Standard solvers enforce constraints internally, but third-party heuristic plugins frequently drop unassigned stops. | **Universal Coverage Invariant ($R == I$):** Strict centralized validation ensures every input stop is served exactly once; missing stops are deterministically repaired. |
| **Resource Transparency** | Usually reports only wall-clock execution time. | Transparently reports process resident RAM (`psutil`), heap allocation/peak (`tracemalloc`), CPU core time ratio, and theoretical Big-O complexity. |

---

## 3. Scientific Evidence, Empirical Observations & Negative Results

ROUTE/IQ is grounded in transparent empirical evidence, including critical negative findings that contradict popular quantum marketing claims:

### Finding 1: Absence of Demonstrated Quantum Advantage on CVRP
- **Empirical Observation:** Across extensive benchmark instances evaluated in Phase AA, Phase AC, and Phase AE, **QAOA executed alone does not outperform Google OR-Tools or Guided Local Search on CVRP**.
- **Root Cause:** Vehicle routing problems involve complex inequality constraints (capacity limits, time windows, and subtour elimination). Embedding these constraints into quantum Hamiltonians requires substantial penalty terms ($P \gg \max d_{ij}$), which distorts the energy landscape and traps variational optimizers (COBYLA/SLSQP) in suboptimal classical states.
- **Scientific Takeaway:** Claims that near-term quantum algorithms (QAOA) provide superior routing solutions on NISQ hardware are unsubstantiated. The true value of QAOA in ROUTE/IQ is providing an **orthogonal, non-classical exploration mechanism** for boundary permutations within a safe, guardrailed cooperative portfolio.

### Finding 2: The Critical Role of Classical VND Refinement
- **Empirical Observation:** Raw bitstrings sampled from QAOA circuits frequently contain local topological defects (e.g. self-intersecting loops between neighboring vertices).
- **Ablation Finding:** When Variable Neighborhood Descent (VND) was removed in ablation experiments (Phase AA), the acceptance rate of QAOA candidates under Proposition 1 dropped from $\approx 28\%$ to below $4\%$.
- **Scientific Takeaway:** Quantum variational outputs on routing problems require classical local search refinement (VND) to achieve competitive solution quality.

### Finding 3: Classical Simulation vs Physical QPU Execution
- **Operational Reality:** All quantum circuits in ROUTE/IQ are executed via **Qiskit 2.4.1 Statevector Simulator on host CPU**, not on physical dilution-refrigerated quantum processors (such as IBM Quantum Eagle/Heron).
- **Qubit Limitation:** Statevector simulation scales exponentially as $2^q$ complex amplitudes. Consequently, boundary subproblems are strictly bounded to $q \le 8$ qubits ($\approx 256$ statevector entries), preventing RAM overflow on standard host hardware.

### Finding 4: Embedded Apache Spark (`local[*]`) vs Distributed Cluster
- **Operational Reality:** Apache Spark 4.2.0 runs as an embedded PySpark session using the `local[*]` master, utilizing local CPU cores and JVM threads.
- **Architectural Boundary:** While the PySpark code uses standard distributed abstractions (`DataFrame`, `RDD`, spatial transformations) ready for cluster deployment (`spark://` or YARN/Kubernetes), all tests and benchmarks were executed on a single host machine.

### Finding 5: Heuristic Nature of the Route Repair Mechanism
- **Operational Reality:** The route repair mechanism (`repair_fleet_coverage`) is a **deterministic greedy heuristic (cheapest capacity-aware insertion)**, not an exact algorithm.
- **Limitation:** If total customer demand exceeds total fleet capacity ($D > K \cdot Q$), the repair operator inserts all stops to ensure customer visibility ($R == I$), but accurately flags capacity violations ($L_k > Q$). It cannot miraculously satisfy impossible physical constraints, and honestly marks solutions as `PENALIZED`.

### Finding 6: Adaptive Controller (MAB UCB-1) Held-Out Generalization
- **Operational Reality:** The Multi-Armed Bandit controller updates arm weights during execution based on observed boundary improvements.
- **Limitation:** While effective within an active optimization run, learned arm weights are instance-dependent and do not automatically transfer to unseen geographic distributions without retraining.
