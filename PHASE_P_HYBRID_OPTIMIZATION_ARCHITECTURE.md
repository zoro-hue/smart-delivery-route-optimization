# ROUTE/IQ — PHASE P: COOPERATIVE HYBRID OPTIMIZATION ARCHITECTURE
**Rigorous Research Design for Classical-Seeded, Quantum-Assisted Routing Optimization**

---

## 1. Executive Summary & Research Paradigm

The central research hypothesis of ROUTE/IQ is:
> *Can quantum-assisted (QAOA) and quantum-inspired (QIGA) optimization, when cooperatively initialized and guided by classical operations research algorithms and scaled by distributed big data processing (Apache Spark), yield measurable improvements in route quality, constraint satisfaction, or combinatorial solution diversity compared to strong classical-only baselines?*

In previous exploratory phases, quantum algorithms were evaluated largely as standalone solvers on toy subsets or as post-hoc replacements. Phase P formalizes a **Cooperative Hybrid Optimization Architecture** where:
1. **Pillar 1 (Big Data Computing):** Apache Spark 4.2.0 processes large-scale road graphs, traffic congestion impedance (BPR function), and partitions high-dimensional customer demands into capacity-feasible delivery micro-zones.
2. **Classical Supporting Layer:** Industry-standard classical solvers (Google OR-Tools CVRP, Clarke–Wright savings, 2-opt local search, Dijkstra/A* shortest paths) construct high-quality initial feasible tours, extract high-impedance subproblem neighborhoods, and provide strict cost upper bounds.
3. **Pillar 2 (Quantum Computing):** Variational QAOA on Qiskit Aer receives classically-seeded micro-cluster subproblems (\(K \le 4\), \(N_q \le 16\)), exploring non-local combinatorial shortcuts within a constraint-preserving subspace.
4. **Quantum-Inspired Computing:** QIGA leverages classical population-based Q-bit evolutionary dynamics seeded with classical elite tours to balance global exploration and local refinement.
5. **Adaptive Feedback Controller & QGAR:** Synthesizes candidate backbones, applies geometric planar crossing regularization, executes dynamic programming tour assembly, and enforces an Incumbent Management Guardrail guaranteeing monotonic non-degradation:
   \[
   \text{Cost}(R_{\text{final}}) \le \min\Big(\text{Cost}(R_{\text{classical}}), \text{Cost}(R_{\text{spatial}})\Big) + \epsilon
   \]

---

## 2. End-to-End System Architecture

```
                          Large-Scale Customer Orders & NYC Road Network Data
                                                  │
                                                  ▼
                       ┌─────────────────────────────────────────────────────┐
                       │      MAJOR PILLAR 1: BIG DATA COMPUTING (SPARK)     │
                       │  - Ingests NYC 5-Borough Road Graph (54k nodes)     │
                       │  - Computes Dynamic BPR Impedance: t_ij(v, c)       │
                       │  - Capacity-Constrained Polar Angle Partitioning    │
                       └──────────────────────────┬──────────────────────────┘
                                                  │
                                                  ▼
                       ┌─────────────────────────────────────────────────────┐
                       │        CLASSICAL INITIALIZATION & BENCHMARKING      │
                       │  - Fast Heuristics: Clarke–Wright Savings, 2-opt    │
                       │  - Primary Exact/Local Search: Google OR-Tools CVRP │
                       │  - Computes Baseline Route Cost: C_classical_best   │
                       │  - Constructs Initial Incumbent Route Pool          │
                       └──────────────────────────┬──────────────────────────┘
                                                  │
                                                  ▼
                       ┌─────────────────────────────────────────────────────┐
                       │          ADAPTIVE SUBPROBLEM EXTRACTOR              │
                       │  - Computes Sub-tour Impedance & Crossing Index X(S)│
                       │  - Identifies Bottleneck Segments (K <= 4 nodes)    │
                       │  - Evaluates Quantum Improvement Potential          │
                       └──────────────┬───────────────────────────┬──────────┘
                                      │                           │
                                      ▼                           ▼
        ┌────────────────────────────────────────┐  ┌──────────────────────────────────┐
        │   MAJOR PILLAR 2: QAOA OPTIMIZATION    │  │ QUANTUM-INSPIRED GA (QIGA/IQGA)  │
        │ - Classically-Seeded Warm-Start Perms  │  │ - Classical Tour Q-Bit Seeding   │
        │ - Ising ATSP Hamiltonian on Qiskit Aer │  │ - Probability Rotation Gates     │
        │ - XY Mixers (Constraint Preserving)    │  │ - Quantum Catastrophe Diversity │
        │ - Variational Optimization (p=1..3)    │  │ - Dynamic Feasibility Repair     │
        │ - Hungarian Bi-stochastic Projection   │  └────────────────┬─────────────────┘
        └─────────────────────┬──────────────────┘                   │
                              │                                      │
                              └───────────────────┬──────────────────┘
                                                  │ Candidate Tour Backbones
                                                  ▼
                       ┌─────────────────────────────────────────────────────┐
                       │       ADAPTIVE HYBRID CONTROLLER & QGAR ASSEMBLY    │
                       │  - Quality-Aware Candidate Selection (Weight λ)     │
                       │  - Planar Edge Crossing Regularizer Penalty         │
                       │  - Multi-Fragment Dynamic Programming Tour Stitching │
                       │  - Cooperative 2-opt Polish on Reconstructed Tours  │
                       └──────────────────────────┬──────────────────────────┘
                                                  │
                                                  ▼
                       ┌─────────────────────────────────────────────────────┐
                       │        UNIFIED INCUMBENT MANAGEMENT GUARDRAIL       │
                       │  - Check: Cost(R_hybrid) <= Cost(R_classical_best)  │
                       │  - If Hybrid Improves: Accept New Certified Route   │
                       │  - Else: Retain Verified Classical Incumbent        │
                       │  - Strict Guarantee: Cost(R_final) <= Baseline      │
                       └──────────────────────────┬──────────────────────────┘
                                                  │
                                                  ▼
                       ┌─────────────────────────────────────────────────────┐
                       │        ROAD-FOLLOWING WAYPOINT RECONSTRUCTION       │
                       │  - Snapping to NYC Road Graph Nodes via KD-Tree     │
                       │  - Dijkstra Shortest-Path Street Traversal          │
                       │  - Final Output Envelope: GeoJSON / Leaflet Map     │
                       └─────────────────────────────────────────────────────┘
```

---

## 3. Core Architectural Modules & Interfaces

### 3.1 Module 1: Big Data Road-Network & Demand Preprocessor (Spark)
- **Inputs:** Raw customer deliveries \(\mathcal{C} = \{(lat_i, lon_i, d_i)\}_{i=1}^N\), Depot \((lat_0, lon_0)\), Road network \(\mathcal{G} = (\mathcal{V}, \mathcal{E}, W)\), Fleet size \(M\), Capacity \(Q\).
- **Processing:**
  1. Computes free-flow travel time \(t^0_{ij}\) and traffic volume/capacity ratios \(v_{ij}/c_{ij}\).
  2. Evaluates Bureau of Public Roads (BPR) link impedance matrix:
     \[
     t_{ij} = t^0_{ij} \left(1 + \alpha \left(\frac{v_{ij}}{c_{ij}}\right)^\beta\right)
     \]
  3. Computes polar coordinates \(\theta_i = \text{atan2}(y_i - y_0, x_i - x_0)\).
  4. Partitions \(\mathcal{C}\) into \(M\) clusters \(\{\mathcal{S}_m\}_{m=1}^M\) obeying \(\sum_{i \in \mathcal{S}_m} d_i \le Q\).
- **Outputs:** Partitioned clusters \(\{\mathcal{S}_m\}\), Snapped road nodes, BPR travel time matrix \(\mathbf{T}\), Physical road distance matrix \(\mathbf{D}\).

### 3.2 Module 2: Classical Initialization & Benchmark Layer
- **Solvers:**
  - `OR-Tools CVRP`: Guided local search with Path Cheapest Arc initialization.
  - `Clarke–Wright`: Savings-based tour merger heuristic.
  - `2-opt`: Iterative edge-uncrossing local search improvement.
  - `Dijkstra / A*`: Road network shortest-path baseline.
- **Role:** Generates an initial complete feasible solution \(R_0\) with verified objective cost \(C_0 = \sum_{r \in R_0} \text{Cost}(r)\). This establishes the **Incumbent Benchmark**.

### 3.3 Module 3: Adaptive Subproblem Extractor
- Analyzes each vehicle tour \(r \in R_0\).
- Calculates the **Planar Crossing Index** \(\mathcal{X}(r)\) and **Sub-tour Cost Density** \(\rho(r)\).
- Identifies bottleneck segments of size \(K \in [3, 4]\) customers where classical heuristics exhibit local sub-optimality or edge intersections.
- Extracts micro-subproblem distance matrix \(\mathbf{D}_{\text{sub}} \in \mathbb{R}^{(K+1) \times (K+1)}\) including entry/exit boundary nodes.

### 3.4 Module 4: Quantum Subproblem Solver (QAOA)
- Receives \(\mathbf{D}_{\text{sub}}\), entry boundary node \(u_{\text{in}}\), exit boundary node \(u_{\text{out}}\), and classical seed order \(\pi_{\text{seed}}\).
- Encodes subproblem into \(N_q = K^2\) qubits (or \(K(K-1)\) with boundary pinning).
- Executes variational QAOA circuit of depth \(p \in \{1, 2, 3\}\) using Qiskit Aer statevector simulation.
- Applies Hungarian projection to decode valid permutations.
- Emits candidate sequences with statevector probabilities and energies.

### 3.5 Module 5: Quantum-Inspired Evolutionary Solver (QIGA)
- Employs Q-bit representation \([\alpha_i, \beta_i]^T\) for combinatorial routing.
- Seeds probability amplitudes towards the classical initial tours.
- Performs evolutionary search using quantum rotation gates and catastrophe-driven diversity operators.
- Decodes, repairs, and evaluates alternative whole-route candidate permutations.

### 3.6 Module 6: Adaptive Hybrid Controller & QGAR Reconstructor
- Compares quantum candidates against classical sub-tours.
- Evaluates composite score: \(J(S) = \text{Cost}(S) + \mu \cdot \mathcal{X}(S)\).
- Stitches optimal sub-sequences into complete vehicle routes using dynamic programming.
- Applies cooperative 2-opt post-processing on the combined tour.

### 3.7 Module 7: Unified Incumbent Management Guardrail
- Validates structural feasibility (all customers served exactly once, vehicle capacity strictly respected, depot start/end).
- Evaluates total physical road distance and impedance cost.
- **Monotonic Acceptance Filter:**
  \[
  R_{\text{final}} = \begin{cases}
  R_{\text{hybrid}}, & \text{if } \text{Cost}(R_{\text{hybrid}}) < \text{Cost}(R_{\text{incumbent}}) - \delta \\
  R_{\text{incumbent}}, & \text{otherwise}
  \end{cases}
  \]
  where \(\delta \ge 0\) prevents acceptance of marginal rounding artifacts.

---

## 4. Architectural Data Contracts

| Interface | Source | Destination | Data Structure |
| :--- | :--- | :--- | :--- |
| `BigDataPartition` | Spark Engine | Classical & Quantum Layers | `List[Dict[str, Any]]`: `{cluster_id, customer_ids, total_demand, polar_span}` |
| `ClassicalIncumbent` | Classical Solver | Incumbent Manager | `Dict`: `{routes: List[List[int]], total_dist_km: float, total_cost: float, is_feasible: bool}` |
| `QuantumSubproblem` | Subproblem Extractor | QAOA Engine | `Dict`: `{subproblem_id, nodes: List[int], matrix: np.ndarray, entry_node: int, exit_node: int, seed_order: List[int]}` |
| `QuantumCandidate` | QAOA Engine | Hybrid Controller | `Dict`: `{sequence: List[int], energy: float, probability: float, qubits_used: int, circuit_depth: int}` |
| `CertifiedRoute` | Incumbent Manager | Road Snapper | `Dict`: `{routes: List[RouteObject], guardrail_certified: bool, improvement_pct: float}` |

---

## 5. Architectural Verdict

This architecture establishes a genuine, cooperative symbiosis between classical algorithms, big data, and quantum computing. Classical optimization is no longer discarded or merely raced against; it actively seeds, bounds, and certifies quantum candidate generation.

