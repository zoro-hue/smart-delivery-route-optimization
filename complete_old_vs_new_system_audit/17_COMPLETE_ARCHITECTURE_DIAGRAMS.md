# 17 — COMPLETE SYSTEM ARCHITECTURE DIAGRAMS

**Project Title:** ROUTE/IQ: Smart Delivery Route Optimization Using Hybrid Big Data and Quantum Computing  
**Institution:** Department of Computer Science and Engineering, SRM University-AP  
**Original Version Baseline:** `main` at commit `a8eb849`  
**Current Research Baseline:** `research/journal-readiness` at commit `feb0920`  

---

## 1. Original Prototype Architecture (`a8eb849`)

```mermaid
flowchart TD
    subgraph UI ["Frontend UI (React 19)"]
        UI_Dash["Overview Dashboard"]
        UI_Plan["Plan Workspace"]
        UI_Results["Results View"]
    end

    subgraph API ["FastAPI Web Server"]
        API_Opt["POST /api/optimization/run"]
        API_Data["GET /api/datasets"]
        API_Big["POST /api/bigdata/run-etl"]
    end

    subgraph Solvers ["Disconnected Solver Implementations"]
        Solv_OR["classical_solver.py (Google OR-Tools)"]
        Solv_CW["classical_solver.py (Clarke-Wright)"]
        Solv_QIGA["qiga_solver.py (QIGA Bloch Rotation)"]
        Solv_ToyQAOA["quantum_solver.py (Monolithic QUBO, <= 8 stops)"]
    end

    subgraph Data ["Data Processing"]
        Data_Proc["data_processor.py (Scalar 1.3x Traffic Factors)"]
        Data_Road["road_network_service.py (54k OSM Graph, Dijkstra)"]
        Data_Spark["bigdata_pipeline.py (local[1] Parquet ETL - Offline Only)"]
    end

    UI_Plan --> API_Opt
    API_Opt --> Data_Proc
    API_Opt --> Data_Road
    API_Opt --> Solvers
    API_Big -.->|Admin Trigger Only| Data_Spark
```

---

## 2. Current Complete Dual-Pillar Architecture (`feb0920`)

```mermaid
flowchart TD
    subgraph Layer1 ["Layer 1: Presentation (React 19 + TypeScript + Leaflet)"]
        L1_Workspace["Plan Workspace & Preset Map"]
        L1_Results["Results View & Road Polylines"]
        L1_Dashboard["Overview Dashboard & Analytics"]
    end

    subgraph Layer2 ["Layer 2: API Gateway & Coordination (FastAPI)"]
        L2_Opt["/api/optimization/run"]
        L2_Geo["geo_validation.py (NYC Bounds & Water Checks)"]
        L2_Snap["road_network_service.py (KD-Tree Snapping)"]
    end

    subgraph Layer3 ["Layer 3: Big Data Computing Pillar (Apache Spark 4.2.0)"]
        L3_Ingest["DataFrame Order Ingestion"]
        L3_BPR["BPR Volume-Delay Impedance Modeling"]
        L3_Sweep["Capacity-Constrained Polar Sweep O(N log N)"]
        L3_Payload["Quantum Subproblem Extraction (m <= 4)"]
    end

    subgraph Layer4 ["Layer 4: Quantum Computing Pillar (QAOA on Qiskit Aer)"]
        L4_Ising["Asymmetric TSP Ising Cost Hamiltonian"]
        L4_XY["Particle-Conserving XY Mixers (XXPlusYYGate)"]
        L4_Slack["Exact Binary Slack Capacity Encoding"]
        L4_Sim["Qiskit AerSimulator (1024 Shots, COBYLA)"]
        L4_Hungarian["Hungarian Permutation Feasibility Projection"]
    end

    subgraph Layer5 ["Layer 5: Operational Bridge & Reconstruction (QGAR)"]
        L5_Boltzmann["Quality-Aware Boltzmann Candidate Sampling"]
        L5_Insert["Dynamic DP Tour Insertion"]
        L5_Cross["Planar Crossing Regularizer (2-opt Untangling)"]
        L5_Guard["End-to-End Route Certification Guardrail (Proposition 1)"]
    end

    subgraph Layer6 ["Layer 6: Supporting Infrastructure & Baselines"]
        L6_ORTools["Google OR-Tools GLS (Classical SOTA Upper Bound)"]
        L6_CW["Clarke-Wright Savings + 2-opt Heuristic"]
        L6_Dijkstra["NetworkX 54k-Node Dijkstra Engine"]
        L6_DB["PostgreSQL / SQLite Database Persistence"]
    end

    L1_Workspace --> L2_Opt
    L2_Opt --> L2_Geo
    L2_Geo --> L2_Snap
    L2_Snap --> L3_Ingest
    L3_Ingest --> L3_BPR
    L3_BPR --> L3_Sweep
    L3_Sweep --> L3_Payload
    L3_Payload --> L4_Ising
    L4_Ising --> L4_XY
    L4_XY --> L4_Sim
    L4_Sim --> L4_Hungarian
    L4_Hungarian --> L5_Boltzmann
    L3_Sweep --> L5_Insert
    L5_Boltzmann --> L5_Insert
    L5_Insert --> L5_Cross
    L5_Cross --> L5_Guard
    L6_Dijkstra -.-> L3_Payload
    L6_Dijkstra -.-> L5_Insert
    L5_Guard -->|Certified Final Routes| L2_Opt
    L2_Opt --> L6_DB
    L2_Opt --> L1_Results
```

---

## 3. Frontend Component Architecture

```mermaid
flowchart TD
    Root["index.html"] --> Main["src/main.tsx"]
    Main --> ThemeProv["ThemeProvider (context/ThemeContext.tsx)"]
    ThemeProv --> SettProv["SettingsProvider (context/SettingsContext.tsx)"]
    SettProv --> App["src/App.tsx (Tab State Manager)"]
    
    App --> Navbar["components/layout/Navbar.tsx"]
    App --> ErrorB["components/ErrorBoundary.tsx"]
    
    App --> Overview["pages/OverviewDashboard.tsx"]
    App --> Plan["pages/PlanWorkspace.tsx"]
    App --> Datasets["pages/DatasetManagement.tsx"]
    App --> Results["pages/ResultsView.tsx"]
    App --> History["pages/ExperimentHistory.tsx"]
    App --> Settings["pages/SystemSettings.tsx"]
    
    Overview --> HeroCube["components/hero/LogisticsRouteCube.tsx"]
    Plan --> LeafletMap1["Leaflet Map Engine (CartoDB Tiles, Markers)"]
    Results --> LeafletMap2["Leaflet Map Engine (Turn-by-turn Polylines)"]
    
    App --> ApiService["services/api.ts (Axios HTTP Client)"]
```

---

## 4. Backend Service Architecture

```mermaid
flowchart TD
    FastAPIApp["app/main.py (FastAPI Application)"] --> Routers
    
    subgraph Routers ["API Routers"]
        R_Opt["routes/optimization.py (/api/optimization/*)"]
        R_Data["routes/datasets.py (/api/datasets/*)"]
        R_Big["routes/bigdata.py (/api/bigdata/*)"]
    end
    
    R_Opt --> Svc_Geo["services/geo_validation.py"]
    R_Opt --> Svc_Road["services/road_network_service.py"]
    R_Opt --> Svc_Class["services/optimization/classical_solver.py"]
    R_Opt --> Svc_QIGA["services/optimization/qiga_solver.py"]
    R_Opt --> Svc_LegacyQAOA["services/optimization/quantum_solver.py"]
    
    subgraph ResearchServices ["Research-Readiness Services"]
        Svc_Spark["services/spark_routing_preprocessor.py"]
        Svc_QAOA["services/optimization/qaoa_subproblem_optimizer.py"]
        Svc_QGAR["services/optimization/qgar_pipeline.py"]
        Svc_Hybrid["services/optimization/hybrid_quantum_pipeline.py"]
        Svc_RBQCD["services/optimization/rb_qcd_decomposer.py"]
        Svc_HNOE["services/optimization/hnoe_screening_engine.py"]
    end
    
    R_Data --> Svc_Dataset["services/dataset_service.py"]
    R_Big --> Svc_BigETL["services/bigdata_pipeline.py"]
```

---

## 5. API Request / Response Flow

```mermaid
sequenceDiagram
    autonumber
    actor Dispatcher as Dispatcher (UI)
    participant Client as React Client (api.ts)
    participant API as FastAPI Gateway
    participant DB as SQLite / PostgreSQL
    participant Solver as Solver Engine

    Dispatcher->>Client: Click "Run Optimization"
    Client->>API: POST /api/optimization/run (OptimizationRequest JSON)
    API->>API: Pydantic Validation & Coordinate Boundary Checks
    API->>Solver: Execute Routing Algorithm
    Solver-->>API: Computed Routes, Distances & Metrics
    API->>DB: INSERT Experiment & ExperimentResult (session.commit())
    DB-->>API: Rows Committed
    API-->>Client: HTTP 200 OK (OptimizationResponse JSON)
    Client->>Dispatcher: Render Turn-by-Turn Map & Dashboard
```

---

## 6. Database and Storage Architecture

```mermaid
flowchart LR
    subgraph DB ["Relational Persistence (SQLAlchemy 2.0 Async)"]
        Exp["Table: experiments<br/>(id, timestamp, algorithm, num_customers)"]
        Res["Table: experiment_results<br/>(id, experiment_id, routes_json, metrics_json)"]
        Meta["Table: dataset_metadata<br/>(id, name, filename, row_count, status)"]
        Exp --- Res
    end

    subgraph Files ["Filesystem Columnar & Graph Storage"]
        Raw["backend/data/raw/ (CSV Datasets)"]
        Proc["backend/data/processed/ (Parquet Cache via PyArrow)"]
        OSM["backend/app/services/road_network/ (OSM XML 54k Graph)"]
        Bench["phase_i_qgar_benchmark_raw.csv (Benchmark Telemetry)"]
    end
```

---

## 7. Big Data Spark Architecture (Pillar 1)

```mermaid
flowchart TD
    Orders["Raw Delivery Orders (Lat, Lon, Demand)"] --> DF["Ingest to PySpark DataFrame"]
    DF --> Polar["Compute Polar Angle: theta = atan2(dy, dx)"]
    Polar --> Win["Catalyst Window: OrderBy(theta ASC)"]
    Win --> Sum["Cumulative Demand Sum: sum(demand_kg).over(window)"]
    Sum --> Bin["Capacity Allocation: Floor((cum_demand - 1) / Q)"]
    Bin --> Sectors["Partitioned Capacity-Compliant Route Clusters"]
    Sectors --> Payload["extract_quantum_subproblem_payload() (m <= 4 stops)"]
    
    DOT["NYC DOT Hourly Volumes"] --> BPR["BPR Model: tau = tau_0 [1 + 0.15(V/C)^4]"]
    BPR --> Payload
```

---

## 8. Quantum QAOA Architecture (Pillar 2)

```mermaid
flowchart TD
    Sub["Micro-Cluster Subproblem (m <= 4 stops, Matrix D)"] --> Form["Ising ATSP Formulation: x_{i,p} -> (I - Z_{i,p})/2"]
    Form --> HC["Cost Hamiltonian: H_C on m^2 Logical Qubits"]
    
    Init["Initial Superposition |psi_0>"] --> Circuit["Alternating Parameterized Circuit (p=2)"]
    HC --> Circuit
    HM["XY Mixer Hamiltonian: XXPlusYYGate(2 beta)"] --> Circuit
    Slack["Binary Slack Capacity Encoding: sum 2^b s_{k,b}"] --> Circuit
    
    Circuit --> AerSim["Qiskit AerSimulator (1024 Shots)"]
    AerSim --> COBYLA["COBYLA Classical Parameter Optimization (25 iters)"]
    COBYLA -.->|Update gamma, beta| Circuit
    
    AerSim --> Measure["Collapsed Measurement Bitstrings"]
    Measure --> Check{"Valid Permutation?"}
    Check -->|Yes| RawTour["Direct Feasible Tour"]
    Check -->|No (93.3% - 100%)| Hungarian["Hungarian Algorithm Bipartite Matching"]
    Hungarian --> FeasibleTour["Projected Feasible Candidate Tour"]
```

---

## 9. Road-Network and Traffic Architecture

```mermaid
flowchart LR
    OSM["manhattan_osm.xml (25 MB)"] --> Stream["cElementTree.iterparse (Zero-RAM Streaming)"]
    Stream --> Graph["NetworkX MultiDiGraph (54,000 Nodes)"]
    Graph --> LSCC["Extract Largest Strongly Connected Component"]
    LSCC --> KD["SciPy KD-Tree Index (float32 Arrays)"]
    
    Stop["Customer GPS (lat, lon)"] --> KD
    KD --> Snapped["Snapped OSM Node ID (< 5 km)"]
    Snapped --> Dijkstra["NetworkX Dijkstra Shortest Path Engine"]
    Dijkstra --> Matrix["Asymmetric Travel Time Matrix"]
    Dijkstra --> Predecessor["Predecessor Tree (Turn-by-Turn Road Polylines)"]
```

---

## 10. Optimization Architecture (Comprehensive)

```mermaid
flowchart TD
    Input["Delivery Routing Problem Instance"] --> Mode{"Selection Mode"}
    
    Mode -->|Recommended| ORTools["Google OR-Tools GLS (Primary Classical CVRP)"]
    Mode -->|Compare| Suite["Multi-Algorithm Benchmark Suite"]
    Mode -->|Research| DualPillar["ROUTE/IQ Dual-Pillar Hybrid Engine"]
    
    Suite --> ORTools
    Suite --> CW["Clarke-Wright Savings"]
    Suite --> TwoOpt["2-opt Local Search"]
    Suite --> QIGA["QIGA Bloch Evolutionary Heuristic"]
    Suite --> LegacyQAOA["Legacy Monolithic QAOA (n <= 8)"]
    
    DualPillar --> Spark["Pillar 1: Spark Preprocessor O(N log N)"]
    Spark --> QAOA["Pillar 2: QAOA on Qiskit Aer (m <= 4)"]
    QAOA --> QGAR["Operational Bridge: QGAR Pipeline"]
    QGAR --> Guard["Route Certification Guardrail"]
```

---

## 11. QGAR Reconstruction and Certification Architecture

```mermaid
flowchart TD
    Bits["Sampled QAOA Bitstrings"] --> Eval["Boltzmann Quality-Aware Evaluator: w_c proportional to exp(-Delta E / T)"]
    Eval --> Anchor["Select Anchor Micro-Cluster Core Tour"]
    Anchor --> Insert["Dynamic DP Route Insertion (Cost-Minimal Insertion)"]
    Insert --> Assembled["Full Fleet Vehicle Routes"]
    Assembled --> Cross["Planar Crossing Regularizer (Orientation Determinants)"]
    Cross --> Untangled["Uncrossed Reconstructed Routes (R_QGAR)"]
    
    Untangled --> Guard{"Route Certification Guardrail<br/>Cost(R_QGAR) <= Cost(R_spatial) + 1e-4"}
    Guard -->|PASS (14 Wins, 6 Ties)| FinalQGAR["Certified QGAR Routes"]
    Guard -->|FAIL (0 Losses)| FinalSpatial["Certified Spatial Baseline Routes"]
```

---

## 12. Full End-to-End Runtime Execution Flow

```mermaid
flowchart TD
    A["1. Dispatcher selects stops in PlanWorkspace.tsx"] --> B["2. Axios dispatches POST to /api/optimization/run"]
    B --> C["3. FastAPI validates Pydantic OptimizationRequest"]
    C --> D["4. geo_validation.py checks NYC bounds & water bodies"]
    D --> E["5. road_network_service.py snaps coordinates via KD-Tree"]
    E --> F["6. Dijkstra computes distance matrix & predecessor tree"]
    F --> G["7. Target solver executes (OR-Tools / QGAR)"]
    G --> H["8. Turn-by-turn road polylines reconstructed"]
    H --> I["9. Run persisted to SQLite/PostgreSQL database"]
    I --> J["10. HTTP 200 JSON returned to client"]
    J --> K["11. ResultsView.tsx renders Leaflet map & vehicle cards"]
```

---

## 13. Cloud Deployment Architecture

```mermaid
flowchart LR
    subgraph Vercel ["Vercel Edge Platform"]
        V_Static["Static SPA Assets (dist/)"]
        V_Rewrite["vercel.json (SPA Rewrite Rules)"]
    end

    subgraph Render ["Render Cloud Platform"]
        R_App["FastAPI / Uvicorn Web Service"]
        R_Opt["Memory Optimizations: MALLOC_ARENA_MAX=2, malloc_trim"]
        R_PG["Managed PostgreSQL Database"]
    end

    User["Web Browser"] -->|HTTPS| V_Static
    User -->|REST API| R_App
    R_App --> R_PG
```

---

## 14. Testing & Verification Architecture

```mermaid
flowchart TD
    Pytest["pytest backend/tests/ -q (38 Tests Passing in 71.62s)"]
    
    Pytest --> T1["test_spark_routing_preprocessor.py (4 tests: DataFrames, BPR, Fallback)"]
    Pytest --> T2["test_qaoa_subproblem_optimizer.py (6 tests: Ising, XY, Slack, Hungarian)"]
    Pytest --> T3["test_qgar_pipeline.py (6 tests: Proposition 1 Guardrail, Crossings)"]
    Pytest --> T4["test_hybrid_quantum_pipeline.py (4 tests: Spark-QAOA Integration)"]
    Pytest --> T5["test_rb_qcd_and_hnoe.py (6 tests: Regressions, H-NOE Disabled)"]
    Pytest --> T6["test_optimization_and_pipeline.py (12 tests: Classical SOTA, Boundary)"]
```
