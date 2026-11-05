# 10 — END-TO-END RUNTIME EXECUTION AUDIT

**Project Title:** ROUTE/IQ: Smart Delivery Route Optimization Using Hybrid Big Data and Quantum Computing  
**Institution:** Department of Computer Science and Engineering, SRM University-AP  
**Original Version Baseline:** `main` at commit `a8eb849`  
**Current Research Baseline:** `research/journal-readiness` at commit `feb0920`  

---

## 1. Dual Runtime Reality Discovery

A fundamental finding of this forensic audit is that the ROUTE/IQ codebase currently contains **two distinct, parallel execution paths**:

1. **Path A: The Live Web Application Runtime:** The user-facing REST API path running via FastAPI, Uvicorn, and React 19. It dispatches to classical solvers (Google OR-Tools GLS, Clarke-Wright, 2-opt), QIGA, and the original monolithic QAOA solver capped at 8 customers.
2. **Path B: The Scientific Research Benchmark Runtime:** The dual-pillar research pipeline executing via automated Python benchmark harnesses. It connects Apache Spark 4.2.0 (`SparkRoutingPreprocessor`) with QAOA on Qiskit Aer (`QAOASubproblemOptimizer`) and the QGAR bridge with the Route Certification Guardrail (`QuantumGuidedAdaptiveRouter`).

```mermaid
flowchart TD
    subgraph PathA ["Path A: Live Web Application Runtime (FastAPI HTTP API)"]
        UI_User["Dispatcher in React PlanWorkspace.tsx"] -->|HTTP POST| API_Run["/api/optimization/run"]
        API_Run --> Geo_Val["geo_validation.py (NYC Bounds & Water)"]
        Geo_Val --> Road_Snap["road_network_service.py (KD-Tree Snap & Dijkstra)"]
        Road_Snap --> Solver_Dispatch{"optimization.py Dispatcher"}
        Solver_Dispatch -->|algo='ortools'| Solver_OR["classical_solver.solve_ortools()"]
        Solver_Dispatch -->|algo='clarke_wright'| Solver_CW["classical_solver.solve_clarke_wright()"]
        Solver_Dispatch -->|algo='qiga'| Solver_QIGA["qiga_solver.solve()"]
        Solver_Dispatch -->|algo='qaoa'| Solver_LegacyQAOA["quantum_solver.solve() (Monolithic QUBO, <= 8 stops)"]
        Solver_Dispatch -->|algo='qgar'| Fallback_Warn["Logs Warning: Defaults to OR-Tools"]
        Solver_OR --> DB_Write["Persist to SQLite / Postgres (app.db)"]
        Solver_CW --> DB_Write
        Solver_QIGA --> DB_Write
        Solver_LegacyQAOA --> DB_Write
        Fallback_Warn --> DB_Write
        DB_Write --> UI_Results["Render in ResultsView.tsx Map"]
    end

    subgraph PathB ["Path B: Scientific Research Benchmark Runtime (Batch Scripts)"]
        Script_Bench["run_phase_i_qgar_benchmark.py"] --> Spark_Pre["SparkRoutingPreprocessor (Pillar 1)"]
        Spark_Pre -->|BPR Impedance & Polar Sweep O(N log N)| Clusters["Capacity-Compliant Route Clusters"]
        Clusters --> Extract_Sub["extract_quantum_subproblem_payload()"]
        Extract_Sub -->|Micro-Clusters m <= 4| QAOA_Opt["QAOASubproblemOptimizer (Pillar 2)"]
        QAOA_Opt -->|Ising ATSP + XY Mixers + Hungarian| Candidates["Quantum Candidate Tours & Energy"]
        Candidates --> QGAR_Bridge["QuantumGuidedAdaptiveRouter (Bridge)"]
        QGAR_Bridge --> Boltzmann["Quality-Aware Boltzmann Sampling"]
        Boltzmann --> DP_Insert["Dynamic DP Tour Insertion"]
        DP_Insert --> Cross_Reg["Planar Crossing Regularizer (2-opt)"]
        Cross_Reg --> Guardrail{"Proposition 1 Route Certification Guardrail"}
        Guardrail -->|Cost(QGAR) <= Cost(Spatial)| Cert_QGAR["Certified QGAR Routes"]
        Guardrail -->|Cost(QGAR) > Cost(Spatial)| Cert_Spatial["Certified Spatial Baseline Routes"]
        Cert_QGAR --> CSV_Log["Log to phase_i_qgar_benchmark_raw.csv"]
        Cert_Spatial --> CSV_Log
    end
```

---

## 2. Step-by-Step Code Trace: Path A (Live Web Application Runtime)

| Step # | Executing File | Class / Function | Data Input | Data Output | Downstream Component |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **A1** | `frontend/src/pages/PlanWorkspace.tsx` | `handleRunOptimization()` | User clicks "Run Optimization" with stops, capacity $Q$, and algorithm. | Serialized JSON payload matching `OptimizationRequest`. | `services/api.ts` |
| **A2** | `frontend/src/services/api.ts` | `api.runOptimization(params)` | JavaScript object | HTTP POST request to `/api/optimization/run` with 120s timeout. | FastAPI ASGI Server |
| **A3** | `backend/app/api/routes/optimization.py` | `run_optimization()` | Incoming JSON body | Validated `OptimizationRequest` Pydantic model. | `geo_validation.py` |
| **A4** | `backend/app/services/geo_validation.py` | `validate_nyc_coordinate()` | Depot and customer coordinates `(lat, lon)` | Boolean `is_valid` and error string if point falls in water or outside city. | `road_network_service.py` |
| **A5** | `backend/app/services/road_network_service.py` | `snap_coordinate()` | Raw GPS coordinates | Snapped OpenStreetMap node IDs and snapped road coordinates. | `road_network_service.py` |
| **A6** | `backend/app/services/road_network_service.py` | `build_road_matrix()` | Snapped node IDs, traffic factor, weather factor | Asymmetric Dijkstra travel time matrix ($n \times n$) and predecessor paths. | `optimization.py` |
| **A7** | `backend/app/api/routes/optimization.py` | Solver Dispatch Loop | Algorithm key (`ortools`, `clarke_wright`, `qiga`, `qaoa`) | Dispatches to corresponding solver module. | Target Solver Class |
| **A8** | `backend/app/services/optimization/classical_solver.py` | `solve_ortools()` | Matrix, demands, vehicle count, capacity $Q$ | Computed vehicle routes, travel distance, leg distances, travel times. | `optimization.py` |
| **A9** | `backend/app/services/road_network_service.py` | `reconstruct_vehicle_road_route()` | Stop node sequence | Turn-by-turn road polyline coordinate arrays extracted from predecessor tree. | `optimization.py` |
| **A10** | `backend/app/api/routes/optimization.py` | `session.commit()` | Experiment results, metrics, and polylines | Persisted rows in `experiments` and `experiment_results` tables. | HTTP ASGI Response |
| **A11** | `frontend/src/pages/ResultsView.tsx` | React Component Mount | `OptimizationResponse` JSON | Renders Leaflet turn-by-turn road map, vehicle cards, and summary stats. | User Display |

---

## 3. Step-by-Step Code Trace: Path B (Scientific Research Benchmark Runtime)

| Step # | Executing File | Class / Function | Data Input | Data Output | Downstream Component |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **B1** | `backend/scripts/run_phase_i_qgar_benchmark.py` | `main()` | Benchmark configuration: 20 trials across $N=25, 50, 100$. | Synthetic delivery locations and parcel demands on NYC street graph. | `spark_routing_preprocessor.py` |
| **B2** | `backend/app/services/spark_routing_preprocessor.py` | `partition_customers_spark()` | Order locations, demands, vehicle capacity $Q$ | PySpark Catalyst Windowing calculates polar angle $\theta$ and partitions clusters in $O(N \log N)$. | `spark_routing_preprocessor.py` |
| **B3** | `backend/app/services/spark_routing_preprocessor.py` | `extract_quantum_subproblem_payload()` | Partitioned vehicle cluster | Micro-cluster payload dictionary ($m \le 4$, distance matrix, demands). | `qaoa_subproblem_optimizer.py` |
| **B4** | `backend/app/services/optimization/qaoa_subproblem_optimizer.py` | `solve_microcluster_tour()` | $m \times m$ distance matrix, depth $p=2$, shots 1024 | Parameterized circuit with $XY$ mixers (`XXPlusYYGate`) simulated on Qiskit Aer. | `qaoa_subproblem_optimizer.py` |
| **B5** | `backend/app/services/optimization/qaoa_subproblem_optimizer.py` | `linear_sum_assignment()` | Measured bitstrings violating permutation constraints | Deterministic Hungarian projection maps soft probabilities to feasible tours. | `qgar_pipeline.py` |
| **B6** | `backend/app/services/optimization/qgar_pipeline.py` | `evaluate_all_candidates()` | QAOA sampled bitstrings and cost Hamiltonian | Boltzmann energy expectation weights $w_c \propto e^{-\Delta E_c / T}$. | `qgar_pipeline.py` |
| **B7** | `backend/app/services/optimization/qgar_pipeline.py` | `_reconstruct_route_dp_insertion()` | Core quantum tour anchor, remaining cluster stops | Dynamically assembled full vehicle routes minimizing insertion detour cost. | `qgar_pipeline.py` |
| **B8** | `backend/app/services/optimization/qgar_pipeline.py` | `lines_intersect()` | 2D route coordinate segments | Detects topological edge crossings and applies 2-opt uncrossing inversions. | `qgar_pipeline.py` |
| **B9** | `backend/app/services/optimization/qgar_pipeline.py` | Route Certification Guardrail | Reconstructed QGAR route vs. Deterministic Spatial Baseline | Certified routes satisfying Proposition 1 ($C_{\text{final}} \le C_{\text{spatial}} + 10^{-4}$). | `run_phase_i_qgar_benchmark.py` |
| **B10** | `backend/scripts/run_phase_i_qgar_benchmark.py` | CSV Writer | Per-trial metrics across QGAR, Phase H, Spatial, OR-Tools, Clarke-Wright | Appends verified rows to `phase_i_qgar_benchmark_raw.csv`. | Analysis & Reports |

---

## 4. Forensic Synthesis

1. **Why do two paths exist?** Path A represents the stable cloud web application built for the UROP prototype demonstration. Path B represents the cutting-edge scientific research environment created for rigorous peer-reviewed journal publication.
2. **Future Engineering Requirement:** To make the research innovations accessible via the web UI, `backend/app/api/routes/optimization.py` should be updated to wire `algorithm="qgar"` into `QuantumGuidedAdaptiveRouter`.
