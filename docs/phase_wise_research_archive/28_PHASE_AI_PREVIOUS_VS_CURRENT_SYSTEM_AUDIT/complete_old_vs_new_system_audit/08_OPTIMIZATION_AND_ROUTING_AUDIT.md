# 08 — OPTIMIZATION AND ROUTING ALGORITHMS AUDIT

**Project Title:** ROUTE/IQ: Smart Delivery Route Optimization Using Hybrid Big Data and Quantum Computing  
**Institution:** Department of Computer Science and Engineering, SRM University-AP  
**Original Version Baseline:** `main` at commit `a8eb849`  
**Current Research Baseline:** `research/journal-readiness` at commit `feb0920`  

---

## 1. Algorithmic Overview & Scope

ROUTE/IQ encompasses a rich ecosystem of **13 distinct routing and optimization algorithms** spanning classical graph theory, industrial operations research metaheuristics, quantum-inspired evolutionary algorithms, variational quantum circuits, and hybrid adaptive bridges.

The table below catalogs every algorithm, its mathematical formulation, complexity, strengths, limitations, and exact operational status:

---

## 2. Exhaustive 13-Algorithm Forensic Catalog

| # | Algorithm Name | Mathematical Purpose | Implementation File | Input $\to$ Output | Algorithmic Complexity | Key Strengths | Critical Limitations | Operational Status |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Dijkstra Shortest Path** | Computes exact shortest path on road network graph $\mathcal{G}(V, E)$. | `backend/app/services/road_network_service.py` | Graph $\mathcal{G}$, Origin Node $\to$ Predecessor tree, Distance array | $O(\|E\| + \|V\| \log \|V\|)$ | Exact shortest path across 54k-node NYC street network. | Memory-intensive for dense multi-node matrices. | **Fully Active (Supporting)** |
| **2** | **A\* Search** | Accelerated point-to-point shortest path using Haversine heuristic. | `backend/app/services/road_network_service.py` | Graph $\mathcal{G}$, Start/End Nodes $\to$ Path polyline | $O(\|E\|)$ best case | Faster than Dijkstra for single origin-destination pairs. | Requires admissible Euclidean distance heuristic. | **Fully Active (Supporting)** |
| **3** | **Google OR-Tools GLS** | Classical SOTA Capacitated VRP solver with Guided Local Search. | `backend/app/services/optimization/classical_solver.py` | Distance Matrix, Customer Demands, Capacity $Q \to$ Fleet Routes | Heuristic metaheuristic | Highly optimized C++ engine; produces shortest global routes. | Black-box classical proprietary metaheuristic; no quantum coupling. | **Fully Active (Baseline Upper Bound)** |
| **4** | **Clarke-Wright Savings** | Classical constructive heuristic combining stops by travel savings. | `backend/app/services/optimization/classical_solver.py` | Distance Matrix, Demands, Capacity $Q \to$ Feasible Routes | $O(N^2 \log N)$ | Fast deterministic construction; respects capacity. | Greedy nature traps solution in suboptimal local minima. | **Fully Active (Baseline)** |
| **5** | **2-opt Local Search** | Iterative tour improvement via pairwise edge inversion. | `backend/app/services/optimization/classical_solver.py` | Single Route $\to$ Uncrossed Route | $O(N^2)$ per pass | Eliminates edge crossings in $O(N^2)$ polynomial time. | Single-vehicle tour only; vulnerable to local minima. | **Fully Active (Supporting)** |
| **6** | **QIGA (Quantum-Inspired Genetic Algorithm)** | Classical evolutionary heuristic representing genes on Bloch sphere. | `backend/app/services/optimization/qiga_solver.py` | Qubit Angle Vectors, Demands, Capacity $\to$ Best Route | $O(G \cdot P \cdot N^2)$ | Avoids premature convergence via quantum probability vectors. | Completely classical trigonometric algorithm; no true quantum mechanics. | **Fully Active (Educational)** |
| **7** | **Monolithic QUBO QAOA** | Early prototype mapping full VRP to a single global QUBO. | `backend/app/services/optimization/quantum_solver.py` | Distance Matrix, Penalty Multipliers $\to$ Bitstring | $O(2^{N^2 K})$ | Early conceptual exploration of quantum VRP. | Variables scale as $O(N^2 K)$; fails for $N > 8$; penalty dominance causes 100% invalid states. | **Active in Live API (Legacy Path)** |
| **8** | **RB-QCD Decomposition** | Resource-Budgeted Quantum-Classical Decomposition. | `backend/app/services/optimization/rb_qcd_decomposer.py` | Customer Clusters, Max Qubits $\to$ Fleet Routes | $O(K \cdot N_{\text{sub}}^2)$ | Extracted core stops for quantum; DP insertion for shell. | Classical enumeration can solve small core in $<1\text{ ms}$; core-shell split caused boundary fragmentation. | **Historical Research Baseline** |
| **9** | **H-NOE Screening Engine** | Candidate swap pruning via the theoretical Four-Gamma bound. | `backend/app/services/optimization/hnoe_screening_engine.py` | Customer Pairs, Distance Bounds $\to$ Filtered Swaps | $O(N^2)$ | Attempted to prune candidate search space. | **Mathematically invalid.** Four-Gamma bound pruned optimal routes; formally disabled in commit `37073bc`. | **REJECTED & DISABLED BY DEFAULT** |
| **10** | **QAOA Subproblem Optimizer** | Bounded quantum optimization of micro-clusters ($m \le 4$). | `backend/app/services/optimization/qaoa_subproblem_optimizer.py` | Micro-cluster distance matrix ($m \le 4$), Demands $\to$ Candidate Tours | Variational (25 COBYLA iters, 1024 shots) | Particle-conserving $XY$ mixers; exact binary slack; Hungarian projection. | Limited to $m \le 4$ stops (16 qubits); classical simulation on Qiskit Aer. | **Active in Research Suite (Pillar 2)** |
| **11** | **Capacity-Constrained Polar Sweep** | Distributed spatial decomposition via Spark Windowing. | `backend/app/services/spark_routing_preprocessor.py` | Order DataFrame, Depot Coords, Capacity $Q \to$ Route Clusters | $O(N \log N)$ distributed | Scales to 50k orders; enforces capacity via Spark Window sum. | Angular sweep cannot capture complex obstacle geometries (e.g. river peninsulas). | **Active in Research Suite (Pillar 1)** |
| **12** | **QGAR (Quantum-Guided Adaptive Reconstruction)** | Hybrid quantum-classical integration bridge. | `backend/app/services/optimization/qgar_pipeline.py` | Spark Clusters, QAOA Candidate Tours $\to$ Fleet Routes | $O(K \cdot m \cdot N_{\text{cluster}})$ | Quality-aware candidate sampling; planar crossing regularizer; route assembly. | Dynamic insertion is a greedy heuristic. | **Active in Research Suite (Bridge)** |
| **13** | **Route Certification Guardrail** | Architectural enforcement of Proposition 1. | `backend/app/services/optimization/qgar_pipeline.py` | Candidate Route $R_{\text{QGAR}}$, Spatial Baseline $R_{\text{spatial}} \to$ Certified Route | $O(N)$ evaluation | **Guarantees $C(R_{\text{final}}) \le C(R_{\text{spatial}}) + 10^{-4}$ by construction.** | Reverts to classical baseline when quantum solution degrades. | **Active in Research Suite (Guardrail)** |

---

## 3. Frontend Selection vs. Backend Dispatch Table Reality

When a user interacts with the **Algorithm Picker** in `PlanWorkspace.tsx`, the frontend sends an `algorithm` or `selected_algorithms` list to `POST /api/optimization/run`:

```typescript
// PlanWorkspace.tsx algorithm catalog:
const WORKSPACE_ALGORITHMS = [
  { id: 'dijkstra', name: 'Dijkstra' },
  { id: 'astar', name: 'A*' },
  { id: 'ortools', name: 'OR-Tools' },
  { id: 'clarke_wright', name: 'Clarke–Wright Savings' },
  { id: 'two_opt', name: '2-opt' },
  { id: 'qaoa', name: 'QAOA' },
  { id: 'qiga', name: 'Quantum-Inspired Genetic Algorithm' },
];
```

### Forensic Dispatch Trace in `backend/app/api/routes/optimization.py`
1. If the user selects `ortools` $\to$ Backend invokes `classical_solver.solve_ortools(...)`.
2. If the user selects `clarke_wright` $\to$ Backend invokes `classical_solver.solve_clarke_wright(...)`.
3. If the user selects `two_opt` $\to$ Backend invokes `classical_solver.solve_two_opt(...)`.
4. If the user selects `dijkstra` $\to$ Backend invokes `classical_solver.solve_dijkstra(...)`.
5. If the user selects `astar` $\to$ Backend invokes `classical_solver.solve_astar(...)`.
6. If the user selects `qiga` $\to$ Backend invokes `qiga_solver.solve(...)`.
7. If the user selects `qaoa` $\to$ Backend invokes `quantum_solver.solve(...)` (**the legacy monolithic QUBO**). If customer count $N > 8$, it truncates the problem to 8 customers.
8. If an external client sends `algorithm="qgar"` $\to$ Backend does not recognize the key, logs a warning, and defaults to `classical_solver.solve_ortools(...)`.

**Conclusion:** The live HTTP API executes the legacy solvers (OR-Tools, Clarke-Wright, 2-opt, QIGA, legacy QAOA). The research pipeline (`SparkRoutingPreprocessor` + `QAOASubproblemOptimizer` + `QGAR`) operates through dedicated research harnesses (`backend/scripts/run_phase_i_qgar_benchmark.py`).
