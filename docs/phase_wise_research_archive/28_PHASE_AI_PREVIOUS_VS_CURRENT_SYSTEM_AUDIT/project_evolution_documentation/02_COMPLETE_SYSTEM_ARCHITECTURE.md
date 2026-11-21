# 02 — COMPLETE SYSTEM ARCHITECTURE

**Project:** ROUTE/IQ — Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing  
**Institution:** SRM University-AP, Department of Computer Science and Engineering  
**Authors:** J. Jayanth, B. Kaivalya, P. Shyam Sai  
**Faculty Supervisor:** Dr. Vishnu Prasad Verma (`vishnu.v@srmap.edu.in`)  
**Git Baseline Commit (`main`):** `a8eb849`  
**Current Research Branch:** `research/journal-readiness` (Commit: `960dfdb`)  
**Target Journal:** *IEEE Transactions on Quantum Engineering*  

---

## 1. System-Wide Architecture Overview

ROUTE/IQ is a multi-tier, hybrid computing platform engineered to solve the Capacitated Vehicle Routing Problem (CVRP) in dense urban environments. The system uniquely harmonizes **Big Data Computing (Apache Spark)** and **Quantum Computing (QAOA via Qiskit Aer)** into a unified, modular architecture.

Rather than treating quantum and classical algorithms as competing black boxes, ROUTE/IQ introduces a hierarchical division of labor:
1. **Big Data Infrastructure** ingests massive delivery demand, models empirical traffic impedance across road networks, and decomposes the global problem into capacity-compliant clusters.
2. **Quantum Optimization** solves combinatorial sequencing and assignment challenges within resource-bounded micro-clusters ($m \le 4$, up to 16 qubits) where quantum state exploration is meaningful.
3. **Adaptive Classical Bridge** synthesizes quantum candidate tours into complete fleet routes, eliminates geometric crossings, and certifies that the resulting solution never degrades below deterministic spatial baselines.

---

## 2. System Architecture Diagram

```mermaid
flowchart TD
    subgraph UI ["Layer 1: Client & Presentation Layer (React 19 + TypeScript)"]
        UI_Map["Leaflet / OSM Route Map"]
        UI_Plan["Plan Workspace & Demand Config"]
        UI_Analytics["Comparison & Analytics Dashboard"]
    end

    subgraph API ["Layer 2: API Gateway & Coordination (FastAPI + Uvicorn)"]
        API_Route["/api/optimization/run"]
        API_Datasets["/api/datasets/*"]
        API_BigData["/api/bigdata/*"]
        API_Health["/api/health"]
    end

    subgraph Pillar1 ["Layer 3: Big Data Computing Pillar (Apache Spark 4.2.0)"]
        Spark_Ingest["Order & Demand Ingestion (Spark DataFrames)"]
        Spark_BPR["BPR Volume-Delay Impedance Modeling"]
        Spark_Sweep["Capacity-Constrained Polar Sweep Partitioning O(N log N)"]
        Spark_Payload["Quantum Subproblem Payload Generator (m <= 4)"]
    end

    subgraph Pillar2 ["Layer 4: Quantum Computing Pillar (QAOA on Qiskit Aer)"]
        QAOA_Ising["Asymmetric TSP Ising Hamiltonian Mapping"]
        QAOA_XY["Particle-Conserving XY Mixers (XXPlusYYGate)"]
        QAOA_Slack["Exact Binary Slack Capacity Encoding"]
        QAOA_Sim["Qiskit Aer Simulator (1024 Shots, COBYLA)"]
        QAOA_Hungarian["Hungarian Permutation Feasibility Projection"]
    end

    subgraph Bridge ["Layer 5: Operational Bridge & Reconstruction (QGAR)"]
        QGAR_Eval["Quality-Aware Candidate Selection (Boltzmann Energy Scoring)"]
        QGAR_Cross["Planar Crossing Regularizer (2-opt Crossing Elimination)"]
        QGAR_Insert["Dynamic Fleet Route Insertion & Tour Assembly"]
        QGAR_Guard["End-to-End Route Certification Guardrail (Monotonic Non-Degradation)"]
    end

    subgraph Classical ["Layer 6: Supporting Classical Layer & Evaluation Baselines"]
        Base_ORTools["Google OR-Tools Guided Local Search (Benchmark Upper Bound)"]
        Base_CW["Clarke-Wright Savings + 2-opt Local Search"]
        Base_Spatial["Deterministic Spatial Baseline (Angular Sweep + Dijkstra)"]
        Base_Dijkstra["NetworkX Dijkstra Shortest Path Engine"]
    end

    subgraph Persistence ["Layer 7: Data & Persistence Layer"]
        DB_Meta["SQLite / PostgreSQL Database (Experiments & Metadata)"]
        Data_OSM["NYC 54,000-Node Road Network Graph (OSM XML)"]
        Data_DOT["NYC DOT Hourly Traffic Volume Counts"]
        Data_Parquet["Curated Parquet Dataset Storage (PyArrow)"]
    end

    %% Data Flow Connections
    UI -->|HTTP / JSON Requests| API
    API -->|Routing Task| Pillar1
    Pillar1 -->|Micro-Cluster Payloads| Pillar2
    Pillar2 -->|Candidate Bitstrings & State Telemetry| Bridge
    Pillar1 -->|Cluster Partitions & Spatial Reference| Bridge
    Bridge -->|Compare & Certify| Classical
    Bridge -->|Certified Final Routes| API
    API -->|Experiment Records| Persistence
    API -->|GeoJSON Polylines & Metrics| UI
    Pillar1 -.->|Read Volumes & Graph| Persistence
    Classical -.->|Read Network Distances| Persistence
```

---

## 3. Layer-by-Layer Detailed Breakdown

### Layer 1: Client & Presentation Layer
- **Core Technologies:** React 19, TypeScript, Vite, Tailwind CSS, Lucide React, Leaflet, OpenStreetMap.
- **Key Components:**
  - `PlanWorkspace.tsx`: Interactive delivery planning canvas where users configure customer stops, origin depot, fleet capacity, traffic scenarios, and algorithm selections.
  - `ResultsView.tsx`: Displays computed route statistics, per-vehicle metrics (travel distance, time, load utilization), and interactive turn-by-turn road polylines.
  - `ComparisonView.tsx`: Side-by-side benchmarking interface comparing QGAR against OR-Tools GLS, Clarke-Wright, and Classical Spatial Baselines.
  - `DeliveryMapView.tsx`: Geospatial map rendering road-snapped paths, customer stop markers, and depot hubs.
  - `DatasetManagement.tsx`: Management portal for uploading, scanning, validating, and preprocessing CSV delivery datasets.

### Layer 2: API Gateway & Coordination Layer
- **Core Technologies:** FastAPI, Uvicorn, Pydantic V2, Starlette CORS Middleware.
- **Key Modules:**
  - `backend/app/main.py`: Application lifespan management, database initialization, CORS configuration, and heartbeat endpoints (`/health`).
  - `backend/app/api/routes/optimization.py`: Primary routing endpoint (`/api/optimization/run`), parameter validation, problem estimation, and experiment persistence.
  - `backend/app/api/routes/datasets.py`: Dataset ingestion, column mapping, schema validation, and Parquet caching.
  - `backend/app/api/routes/bigdata.py`: Administrative telemetry and ETL execution triggers.

### Layer 3: Big Data Computing Pillar (Apache Spark 4.2.0)
- **Core Technologies:** Apache Spark 4.2.0, PySpark SQL, Catalyst Optimizer, Spark Windowing.
- **Key Modules:**
  - `backend/app/services/spark_routing_preprocessor.py`:
    - `CalibratedTrafficImpedanceModel`: Implements the BPR volume-delay function to calculate dynamic link travel times:
      $$\tau_e = \tau_{e,0} \left[1 + 0.15 \left(\frac{V_e}{C_e}\right)^4\right]$$
    - `SparkRoutingPreprocessor`: Ingests delivery stops into Spark DataFrames, transforms geographic coordinates into polar angles relative to the depot ($\theta = \text{atan2}(y-y_0, x-x_0)$), computes running cumulative customer demands via Spark Window functions, and partitions stops into vehicle capacity-compliant clusters ($O(N \log N)$ runtime).
    - `extract_quantum_subproblem_payload`: Extracts tightly clustered micro-subproblems ($m \le 4$ stops) and packages them into standardized JSON payloads containing distance matrices and customer demands.

### Layer 4: Quantum Computing Pillar (QAOA on Qiskit Aer)
- **Core Technologies:** Qiskit 2.4.1, Qiskit Aer 0.17.2, SciPy (`optimize.minimize` via COBYLA).
- **Key Modules:**
  - `backend/app/services/optimization/qaoa_subproblem_optimizer.py`:
    - `MicroSequencingQUBOFormulator`: Formulates the subproblem tour as an Asymmetric Traveling Salesperson Problem (ATSP), mapping $m^2$ binary assignment variables to Pauli-$Z$ operators to construct the cost Hamiltonian $H_C$.
    - `build_qaoa_circuit`: Constructs parameterized quantum circuits alternating between the cost unitary $e^{-i \gamma H_C}$ and the particle-conserving $XY$ mixer unitary $e^{-i \beta H_M}$ implemented via `XXPlusYYGate`.
    - `MacroAssignmentQUBOFormulator`: Formulates vehicle cluster assignment with exact binary slack variables $\sum 2^b s_{k,b}$ to strictly enforce capacity constraints.
    - `QAOASubproblemOptimizer`: Executes classical variational optimization (COBYLA, 25 iterations) over variational angles $(\gamma, \beta)$, samples 1,024 shots on `AerSimulator`, and applies Hungarian algorithm bipartite matching to project invalid measurement bitstrings into valid permutation tours.

### Layer 5: Operational Bridge & Route Reconstruction (QGAR)
- **Core Technologies:** Python 3.14 / NumPy / Dynamic Programming.
- **Key Modules:**
  - `backend/app/services/optimization/qgar_pipeline.py`:
    - `QuantumCandidateEvaluator`: Analyzes the full empirical measurement spectrum from QAOA, scoring candidate tours by energy expectation values rather than raw shot frequency alone.
    - `AdaptiveQuantumInfluenceModel`: Regulates the weight of quantum sequencing proposals based on circuit approximation ratios and empirical variance.
    - `lines_intersect` & `count_tour_crossings`: Planar crossing regularizer that detects 2D topological edge intersections and applies geometric 2-opt untangling.
    - `_reconstruct_route_dp_insertion`: Assembles micro-cluster quantum candidate tours into complete fleet routes using cost-minimal insertion.
    - `End-to-End Route Certification Guardrail`: Enforces the mathematical non-degradation condition:
      $$C(R_{\text{QGAR}}) \le C(R_{\text{spatial}}) + 10^{-4}\text{ km}$$
      If the reconstructed quantum route exceeds the deterministic spatial baseline, the guardrail rejects the quantum candidate and certifies the spatial baseline.

### Layer 6: Classical Algorithms & Supporting Infrastructure
- **Core Technologies:** Google OR-Tools, NetworkX, SciPy.
- **Key Modules:**
  - `backend/app/services/optimization/classical_solver.py`: Provides industry-standard classical benchmarks (Google OR-Tools Guided Local Search, Clarke-Wright Savings, 2-opt Local Search).
  - `backend/app/services/road_network_service.py`: In-memory NetworkX directed multigraph of 54,000 NYC road nodes, KD-Tree nearest-neighbor coordinate snapping, and Dijkstra shortest path routing.
  - `backend/app/services/geo_validation.py`: Verifies GPS coordinates against NYC 5-borough polygon bounds and prevents invalid stops in water bodies (Hudson River, East River, Atlantic Ocean).

### Layer 7: Data & Persistence Layer
- **Core Technologies:** SQLite (local development), PostgreSQL (cloud production via Render), PyArrow Parquet.
- **Key Datasets:**
  - `manhattan_osm.xml` / `nyc_boroughs.xml`: Authentic OpenStreetMap street networks covering Manhattan, Brooklyn, Queens, Bronx, and Staten Island.
  - NYC DOT Traffic Volume Counts: Empirical hourly vehicular volumes across key arterial corridors.
  - SQLite database storing experiment execution history, per-stop metrics, and comparative logs.

---

## 4. Layer Interaction and Interface Contracts

```mermaid
sequenceDiagram
    autonumber
    actor User as User / Client UI
    participant API as FastAPI Gateway
    participant Spark as Spark Preprocessor (Pillar 1)
    participant QAOA as QAOA Optimizer (Pillar 2)
    participant QGAR as QGAR Bridge & Guardrail
    participant Road as Road Network Service

    User->>API: POST /api/optimization/run (Stops, Depot, Capacity, Algo)
    API->>Road: validate_nyc_coordinate() & snap_coordinate()
    Road-->>API: Snapped Road Node IDs & Validated Coordinates
    API->>Spark: partition_customers_spark(locations, demands, capacity)
    Note over Spark: Spark Windowing & BPR Volume-Delay<br/>Polar Sweep Partitioning O(N log N)
    Spark-->>API: Capacity-Compliant Route Clusters
    API->>Spark: extract_quantum_subproblem_payload(cluster, m <= 4)
    Spark-->>API: Micro-Cluster Subproblem Payloads (Matrix, Demands)
    API->>QAOA: solve_microcluster_tour(distance_matrix, p=2, shots=1024)
    Note over QAOA: Qiskit Aer Simulation<br/>Ising ATSP + XY Mixers + Hungarian Projection
    QAOA-->>API: Quantum Candidate Tours & Energy Spectrum
    API->>QGAR: optimize_delivery_campaign(clusters, qaoa_results)
    Note over QGAR: Quality-Aware Candidate Selection<br/>Planar Crossing Regularizer<br/>Route Certification Guardrail
    QGAR->>Road: build_road_matrix() & Dijkstra Path Traversal
    Road-->>QGAR: Accurate Turn-by-Turn Road Distances
    QGAR-->>API: Certified Optimal Fleet Routes & Performance Telemetry
    API->>User: JSON Response (GeoJSON Polylines, Metrics, Comparison)
```

---

## 5. Deployment and Physical Infrastructure Architecture

ROUTE/IQ is architected for dual-environment deployment:

1. **Cloud Production Deployment:**
   - **Frontend:** Hosted on **Vercel** as a static Single Page Application (SPA), connected to custom domains with global edge CDN caching and automatic SSL termination.
   - **Backend:** Hosted on **Render** as a containerized Python Web Service (`render.yaml`, Docker / Python 3.11 environment).
   - **Memory Management on Cloud:** Production runtime employs strict memory optimizations (`MALLOC_ARENA_MAX=2`, `glibc malloc_trim`, zero-RAM XML schema inspection, compact NumPy KD-Tree arrays) to operate within Render Free Tier resource ceilings (512 MB RAM).
   - **Persistence:** Managed PostgreSQL instance on Render for multi-user experiment history.

2. **Local Research & Benchmarking Environment:**
   - **Host Machine:** Windows 11 Enterprise / Ubuntu LTS, Python 3.14.2 / 3.11, OpenJDK 17.0.20.1+1, Apache Spark 4.2.0, Hadoop 3.3.6 `winutils`.
   - **Local Execution:** High-throughput batch processing utilizing all workstation CPU cores via Spark `local[*]` and Qiskit Aer multi-threaded simulation.
   - **Database:** Fast local SQLite database (`app.db`).
