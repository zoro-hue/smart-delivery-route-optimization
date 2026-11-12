# ROUTE/IQ — SYSTEM & ALGORITHM ARCHITECTURE DIAGRAMS
**Visual Architecture Specifications & Data Flow Blueprints**
**Repository:** `D:\UROP\smart-delivery-route-optimization`  
**Current Branch:** `research/phase-ae-backend-integration`  
**Baseline Main:** `a8eb849988201d7929566f331c1ae3afac09b632`

---

## 1. Previous Architecture (Baseline Main @ `a8eb8499`)

The original implementation featured an isolated, single-dispatch pipeline where algorithms ran in complete silos without cross-algorithmic communication, cooperative refinement, or safety guardrails:

```mermaid
flowchart TD
    subgraph UI["Frontend User Interface (React 19 + Leaflet)"]
        A["Dashboard View"] --> B["Algorithm Dropdown Selector"]
        B --> C["Run Button (Single Algorithm)"]
    end

    subgraph API["Backend API Gateway (FastAPI 0.136.3)"]
        C -->|"POST /api/optimization/run"| D["Single Solver Dispatcher"]
    end

    subgraph StaticData["Static Preprocessing (Isolated Script)"]
        E["Raw NYC Datasets (ZIP/CSV)"] --> F["PySpark Extraction Script (Batch)"]
        F --> G["Static CSV Files on Disk"]
    end

    subgraph Solvers["Independent Solvers (Isolated Execution)"]
        D --> H["Google OR-Tools CVRP (Standard GLS)"]
        D --> I["Classical Heuristics (CW / 2-Opt / Dijkstra / A*)"]
        D --> J["QIGA (Python Classical Simulation)"]
        D --> K["QAOA Standalone (Qiskit Statevector, Max 8 Nodes)"]
    end

    subgraph Output["Output Processing (Unverified)"]
        H --> L["Raw Vehicle Routes"]
        I --> L
        J --> L
        K -->|"Omitted Nodes Dropped Silently"| L
        L --> M["SQLite Experiment Table"]
        L --> N["Leaflet Route Map (Euclidean / Partial Lines)"]
    end

    classDef implemented fill:#22c55e,stroke:#15803d,stroke-width:2px,color:#fff;
    classDef unverified fill:#ef4444,stroke:#b91c1c,stroke-width:2px,color:#fff;
    classDef simulated fill:#3b82f6,stroke:#1d4ed8,stroke-width:2px,color:#fff;

    class A,B,C,D,E,F,G,H,I,M implemented;
    class J,K simulated;
    class L,N unverified;
```

---

## 2. Current Architecture (Phase AE @ `5981351`)

The Phase AE architecture integrates big data spatial decomposition, variational quantum simulation, classical constraint solvers, deterministic coverage repair, and the Proposition 1 guardrail into a unified system:

```mermaid
flowchart TD
    subgraph UI_Layer["Frontend Layer (React 19 + TailwindCSS + Leaflet)"]
        UI_A["Plan Workspace & Planning Controls"]
        UI_B["Mode Switcher: Recommended | Custom | Compare"]
        UI_C["Algorithm Comparison Scorecard (CPU, RAM, Big-O)"]
        UI_D["Interactive OSM Map (Turn-by-turn driving polylines)"]
        UI_E["Dataset Management (0% Missing Audit)"]
    end

    subgraph API_Layer["Backend Gateway (FastAPI 0.136.3)"]
        API_A["/api/optimization/run"]
        API_B["ThreadPoolExecutor (Parallel Benchmarking)"]
        API_C["Strict Fleet Constraint Validator"]
    end

    subgraph Pillar1["Pillar 1: Big Data Engine (Apache Spark 4.2.0 local[*])"]
        SP_A["NYC Historical Big Data Ingestion"]
        SP_B["Centroid Polar-Angle Sorting (theta_i = atan2)"]
        SP_C["Capacity-Balanced Wedge Partitioning"]
        SP_D["Boundary Interface Extraction (Vertices B_k)"]
    end

    subgraph CooperativeEngine["Flagship: ROUTE/IQ Cooperative Optimization Engine"]
        CO_A["1. Initial Incumbent (OR-Tools Guided Local Search)"]
        CO_B["2. Adaptive Controller (MAB UCB-1 Arm Selection)"]
        CO_C["3. Boundary Candidate Generators:"]
        CO_C1["Arm 1: QAOA Circuit (Qiskit 2.4.1 Statevector, q <= 8)"]
        CO_C2["Arm 2: Tabu Search (Short-term memory vertex swaps)"]
        CO_C3["Arm 3: Kernighan-Lin (2-way partition swap)"]
        CO_C4["Arm 4: Random Walk (Combinatorial perturbation)"]
        CO_D["4. Variable Neighborhood Descent (2-Opt, Relocate, Swap)"]
        CO_E["5. Proposition 1 Guardrail: Assert C(coop) <= C(incumbent)"]
    end

    subgraph IndependentSuite["Independent Baseline Suite (Zero-Bias Comparison)"]
        IND_A["OR-Tools CVRP"]
        IND_B["Clarke-Wright Savings"]
        IND_C["2-Opt Improvement"]
        IND_D["Dijkstra Shortest-Path"]
        IND_E["A* Heuristic Search"]
        IND_F["QIGA (Quantum-Inspired GA)"]
        IND_G["QAOA Hybrid (Simulated)"]
    end

    subgraph Validation["Centralized Verification & Repair Engine"]
        VAL_A["Universal Delivery Coverage Invariant (R == I)"]
        VAL_B["Deterministic Capacity-Aware Cheapest-Insertion Repair"]
        VAL_C["Capacity Overload Detection (Strict Non-Overriding)"]
        VAL_D["Inaccessible Node Guardrail (Infinite Distance Halt)"]
    end

    subgraph Profiling["Real-Time Resource Measurement"]
        PRF_A["psutil 7.2.2 (Process RSS RAM)"]
        PRF_B["tracemalloc (Python Heap Delta & Peak)"]
        PRF_C["time.perf_counter (Monotonic Wall Time)"]
        PRF_D["time.process_time (CPU User/Kernel Time)"]
        PRF_E["Theoretical Big-O Asymptotic Separator"]
    end

    subgraph RoadNetwork["Road Network & Waypoint Reconstruction"]
        RN_A["OpenStreetMap NYC GraphML (54,128 Nodes)"]
        RN_B["O(1) Spatial Snapping Cache"]
        RN_C["Dijkstra Driving Polyline Generator"]
    end

    UI_B --> API_A
    API_A --> API_C
    API_C --> API_B
    API_B -->|"Mode: Recommended"| CooperativeEngine
    API_B -->|"Mode: Compare / Custom"| IndependentSuite

    CooperativeEngine --> Pillar1
    Pillar1 --> CO_A
    CO_A --> CO_B
    CO_B --> CO_C
    CO_C --> CO_C1 & CO_C2 & CO_C3 & CO_C4
    CO_C1 & CO_C2 & CO_C3 & CO_C4 --> CO_D
    CO_D --> CO_E

    CooperativeEngine --> Validation
    IndependentSuite --> Validation

    Validation --> VAL_A
    VAL_A --> VAL_B
    VAL_B --> VAL_C & VAL_D

    Validation --> RoadNetwork
    RoadNetwork --> RN_A --> RN_B --> RN_C

    API_B --> Profiling
    Profiling --> PRF_A & PRF_B & PRF_C & PRF_D & PRF_E

    RoadNetwork & Profiling & Validation --> UI_C & UI_D

    classDef ui fill:#8b5cf6,stroke:#6d28d9,stroke-width:2px,color:#fff;
    classDef spark fill:#f97316,stroke:#c2410c,stroke-width:2px,color:#fff;
    classDef quantum fill:#06b6d4,stroke:#0891b2,stroke-width:2px,color:#fff;
    classDef classical fill:#10b981,stroke:#047857,stroke-width:2px,color:#fff;
    classDef guardrail fill:#ec4899,stroke:#be185d,stroke-width:2px,color:#fff;

    class UI_A,UI_B,UI_C,UI_D,UI_E ui;
    class SP_A,SP_B,SP_C,SP_D spark;
    class CO_C1,IND_G quantum;
    class CO_A,CO_C2,CO_C3,CO_C4,CO_D,IND_A,IND_B,IND_C,IND_D,IND_E,IND_F classical;
    class CO_E,VAL_A,VAL_B,VAL_C,VAL_D guardrail;
```

---

## 3. Cooperative Optimization Execution Flow

The detailed internal feedback loop within the ROUTE/IQ Cooperative Engine:

```mermaid
sequenceDiagram
    autonumber
    actor User as Logistics Dispatcher
    participant Frontend as ROUTE/IQ UI
    participant Backend as FastAPI Gateway
    participant Spark as Apache Spark (Pillar 1)
    participant ORTools as OR-Tools (Incumbent)
    participant MAB as MAB Controller (UCB-1)
    participant Generator as Candidate Generator (QAOA/Tabu)
    participant VND as Algorithmic VND
    participant Repair as Route Validator (R == I)
    participant Prop1 as Proposition 1 Guardrail

    User->>Frontend: Clicks "Run Optimization" (Recommended Mode)
    Frontend->>Backend: POST /api/optimization/run (req.num_vehicles, capacity, stops)
    Backend->>Backend: Validate fleet constraints (Never silently alter K or Q)

    rect rgb(240, 248, 255)
        note over Backend,Spark: Step 1: Big Data Spatial Decomposition
        Backend->>Spark: partition_and_extract_boundaries(stops, K)
        Spark-->>Backend: Returns K spatial clusters & boundary interface vertices B
    end

    rect rgb(240, 255, 240)
        note over Backend,ORTools: Step 2: High-Speed Classical Incumbent
        Backend->>ORTools: solve_ortools(stops, K, Q, time_limit=50ms)
        ORTools-->>Backend: Initial Incumbent S_incumbent with Cost C(S_incumbent)
    end

    rect rgb(255, 250, 240)
        note over Backend,Generator: Step 3: Adaptive Boundary Search
        Backend->>MAB: Select generator arm for boundary set B
        MAB-->>Backend: Selected Arm (e.g. QAOA 8-qubit variational circuit)
        Backend->>Generator: Execute selected generator on QUBO(B)
        Generator-->>Backend: Raw boundary permutation candidate pi
    end

    rect rgb(255, 245, 245)
        note over Backend,Prop1: Step 4: Refinement, Repair & Guardrail
        Backend->>VND: refine_route_candidate(S_candidate, neighborhoods=[2-opt, relocate, swap])
        VND-->>Backend: Locally cleaned candidate S_refined
        Backend->>Repair: repair_fleet_coverage(S_refined, input_stops)
        Repair-->>Backend: Repaired fleet routes (Guaranteed R == I)
        Backend->>Prop1: Evaluate: C(S_refined) <= C(S_incumbent) AND Feasible?
        alt Condition Satisfied (Cost Improved)
            Prop1-->>Backend: ACCEPT S_refined as final solution; update MAB reward r > 0
        else Condition Violated (Cost Degraded or Infeasible)
            Prop1-->>Backend: REJECT S_refined; ROLLBACK to S_incumbent; update MAB reward r = 0
        end
    end

    Backend-->>Frontend: Returns final routes, validation report, and resource metrics
    Frontend-->>User: Renders verified routes on Leaflet map and Scorecard metrics
```

---

## 4. Previous vs Current Data Flow

```mermaid
flowchart LR
    subgraph PrevData["Previous Data Flow"]
        P1["Raw Orders"] --> P2["Static CSV File"]
        P2 --> P3["Single Chosen Solver"]
        P3 --> P4["Unchecked Output (Dropped Stops Ignored)"]
    end

    subgraph CurrData["Current Phase AE Data Flow"]
        C1["Raw Orders & Fleet Spec"] --> C2["Schema Ingestion (0% Missing)"]
        C2 --> C3["Spatial Polar Wedge Partitioning"]
        C3 --> C4["Cooperative Incumbent + Boundary Search"]
        C4 --> C5["Universal Invariant R == I Repair"]
        C5 --> C6["Proposition 1 Non-Degradation Guardrail"]
        C6 --> C7["OSM Road Graph Waypoint Reconstruction"]
        C7 --> C8["Multi-Tier Resource Telemetry & Verified UI"]
    end

    classDef oldflow fill:#fee2e2,stroke:#ef4444,stroke-width:1px,color:#000;
    classDef newflow fill:#dcfce7,stroke:#22c55e,stroke-width:1px,color:#000;

    class P1,P2,P3,P4 oldflow;
    class C1,C2,C3,C4,C5,C6,C7,C8 newflow;
```

---

## 5. Previous vs Current Algorithm Execution Flow

| Algorithmic Stage | Previous Baseline (`main`) | Current Phase AE (`research/phase-ae`) |
|---|---|---|
| **Dispatch Mode** | Serial, single algorithm. | Parallel multi-algorithm benchmarking (`ThreadPoolExecutor`) or Flagship Cooperative Engine. |
| **Subproblem Scope** | Global (all nodes) or truncated (first 8 nodes). | Polar-angle cluster interfaces ($|B| \le 8$) decomposed via Spark. |
| **Quantum Role** | Standalone solver claiming global solution. | Exploratory boundary candidate generator within cooperative portfolio. |
| **Classical Role** | Standalone competitor. | High-speed global incumbent generator + deterministic VND cleaner + baseline benchmark. |
| **Search Controller** | None (manual user toggle). | Multi-Armed Bandit (MAB UCB-1) credit assignment across quantum and classical arms. |
| **Output Integrity** | Unchecked; dropped stops silently omitted. | Universal Invariant $R == I$ strictly enforced; missing stops repaired deterministically. |
| **Safety Assurance** | None; degraded routes returned if solver failed. | Proposition 1 Guardrail mathematically guarantees $C(S_{\text{coop}}) \le C(S_{\text{incumbent}})$. |
| **Resource Reporting** | Wall-clock execution time only. | Full OS process telemetry: process RSS, heap allocation/peak, CPU time, and theoretical Big-O. |

