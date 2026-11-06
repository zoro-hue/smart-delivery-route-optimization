# ROUTE/IQ: CANONICAL SYSTEM ARCHITECTURE DIAGRAMS

**Project:** Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing  
**Institution:** SRM University-AP | **Supervisor:** Dr. Vishnu Prasad Verma  
**Phase:** AD — Final Research Package  

---

## 1. Complete ROUTE/IQ Hybrid System Architecture

The high-level system architecture illustrates the separation of concerns across the Big Data processing pillar, classical optimization components, quantum candidate generation, adaptive controller, and the non-degradation guardrail.

```mermaid
graph TD
    subgraph PILLAR 1: Distributed Big Data Processing [Apache Spark 4.2.0 Engine]
        RawData[Metropolitan Delivery Orders & Telematics GPS] --> Ingest[High-Throughput Ingestion & Schema Cleaning]
        Ingest --> PolarClustering[Geospatial Polar Wedge Decomposition]
        PolarClustering --> BoundaryFilter[Centroid-Proximity Boundary Filter]
    end

    subgraph WORKLOAD REDUCTION: 99.984% Subproblem Extraction
        BoundaryFilter --> BoundarySubproblem["Ambiguous Boundary Subproblem (N <= 16 Customers)"]
    end

    subgraph ADAPTIVE METAHEURISTIC CONTROLLER: Multi-Armed Bandit
        BoundarySubproblem --> FeatureExtractor[Feature Extractor: Density, Slack, Stagnation, Budget]
        FeatureExtractor --> ControllerEngine{Feature-Conditioned Gating Engine}
    end

    subgraph PILLAR 2 & CLASSICAL GENERATORS: Standardized Candidate Sampling
        ControllerEngine -- "Curvature > 1.85 & Budget >= 35ms" --> QAOA[QAOA Quantum Sampler: Qiskit 2.4.1 Statevector]
        ControllerEngine -- "Stagnation Escape / High Slack" --> Tabu[Tabu Search Metaheuristic: 7-Tenure Memory]
        ControllerEngine -- "Moderate Density / Standard" --> MSKL[Multistart Kernighan-Lin: 32 Restarts]
        ControllerEngine -- "Diversity Harvest" --> RandomSampler[Uniform Random Feasible Sampler]
        ControllerEngine -- "Budget < 15ms" --> FastKL[Single-Pass KL Fast Fallback]
    end

    subgraph ROUTE RECONSTRUCTION & LOCAL SEARCH FOUNDATION
        QAOA --> TourBuilder[Greedy Insertion & Tour Sequencer]
        Tabu --> TourBuilder
        MSKL --> TourBuilder
        RandomSampler --> TourBuilder
        FastKL --> TourBuilder
        TourBuilder --> VND[Algorithmic VND: 2-Opt, Relocate, Swap, Cross-Exchange]
    end

    subgraph CENTRALIZED PROPOSITION 1 ACCEPTANCE GUARDRAIL
        VND --> GuardrailFilter{Proposition 1 Safety Filter}
        IncumbentRoute[Initial Feasible Route Baseline] --> GuardrailFilter
        GuardrailFilter -- "Strictly Feasible & Cost Decreased" --> AdoptNew[Adopt Candidate Route]
        GuardrailFilter -- "Degraded, Infeasible, or Invalid" --> RetainIncumbent[Retain Incumbent Unconditionally]
        AdoptNew --> FeedbackUpdate[Online Multi-Armed Bandit Reward Update]
        RetainIncumbent --> FeedbackUpdate
    end

    subgraph FINAL OUTPUT
        FeedbackUpdate --> FleetSchedule[Global Capacity-Feasible Fleet Route Schedule]
    end
```

---

## 2. Spark Big Data Preprocessing & Workload Reduction Pipeline

Illustrates how 100,000 raw customer deliveries are filtered down to an isolated 16-qubit combinatorial optimization subproblem.

```mermaid
flowchart LR
    A["Raw Customer Orders (N = 100,000)"] --> B["PySpark Schema Validation & Deduplication"]
    B --> C["Centroid Polar Projection: atan2(lat - depot_lat, lon - depot_lon)"]
    C --> D["Angular Sector Sorting & Vehicle Capacity Binning"]
    D --> E["Cluster Centroid Euclidean Projections (dist_A, dist_B)"]
    E --> F["Boundary Extraction Filter: |dist_A - dist_B| < 0.035 deg"]
    F --> G["Isolated Boundary Subproblem (N = 16 Customers, 99.984% Reduction)"]
```

---

## 3. QAOA Candidate Generation Pipeline

Illustrates the simulated quantum optimization process from Hamiltonian construction to statevector sampling.

```mermaid
flowchart TD
    SubData["Boundary Customers (Demands d_i, Distances D_ij)"] --> IsingMap["Map to Ising QUBO Hamiltonian: H_C = Sum J_ij Z_i Z_j + Sum h_i Z_i + Lambda (Sum d_i Z_i - Delta Q)^2"]
    IsingMap --> MixerSelect{"Mixer Strategy Selection"}
    MixerSelect -- "Subspace Feasibility" --> XYMixer["Subspace XY-Mixer: H_M = Sum (X_i X_j + Y_i Y_j)"]
    MixerSelect -- "Standard Unconstrained" --> TransverseMixer["Transverse Field Mixer: H_M = Sum X_i"]
    XYMixer --> ParameterizedCirc["Parameterized Ansatz: U(gamma, beta) = Prod e^(-i beta H_M) e^(-i gamma H_C)"]
    TransverseMixer --> ParameterizedCirc
    ParameterizedCirc --> SimulationEngine["Classical CPU Statevector Evolution (Qiskit 2.4.1)"]
    SimulationEngine --> BitstringSampling["Sample Bitstrings (B = 512 Evaluations)"]
    BitstringSampling --> CapacityRepair["Greedy Feasibility Repair Heuristic"]
    CapacityRepair --> QuantumCandidate["Feasible Boundary Bipartition (S_A, S_B)"]
```

---

## 4. Classical Optimization & Algorithmic VND Pipeline

Illustrates the 4-neighborhood deterministic Variable Neighborhood Descent.

```mermaid
flowchart TD
    PartitionInput["Bipartition Sets (S_A, S_B)"] --> TourExtraction["Nearest-Neighbor Tour Initialization"]
    TourExtraction --> N1["Neighborhood 1: Intra-Route 2-Opt (Edge Inversion)"]
    N1 -- "Improvement Found" --> N1
    N1 -- "Local Optimum" --> N2["Neighborhood 2: Inter-Route Customer Relocate"]
    N2 -- "Improvement Found" --> N1
    N2 -- "Local Optimum" --> N3["Neighborhood 3: Inter-Route Customer Swap"]
    N3 -- "Improvement Found" --> N1
    N3 -- "Local Optimum" --> N4["Neighborhood 4: Inter-Route Cross-Exchange (Segment Swap)"]
    N4 -- "Improvement Found" --> N1
    N4 -- "Local Optimum" --> OptimizedVND["Locally Optimal Fleet Route (Tour_A, Tour_B)"]
```

---

## 5. Adaptive Controller & Proposition 1 Guardrail Pipeline

Illustrates the feature gating rules and mathematical safety filter.

```mermaid
flowchart TD
    SubproblemState["Boundary State Features (Density, Slack, Stagnation, Budget)"] --> BudgetCheck{"Remaining Budget < 15ms?"}
    BudgetCheck -- "Yes" --> FastFallback["Single-Pass KL Fallback"]
    BudgetCheck -- "No" --> StagnationCheck{"Stagnation Count >= 2?"}
    StagnationCheck -- "Yes" --> TabuEscape["Tabu Search (7-Tenure Recency Escape)"]
    StagnationCheck -- "No" --> CurvatureCheck{"Curvature Score > 1.85 & Budget >= 35ms?"}
    CurvatureCheck -- "Yes" --> QAOADispatch["Fast QAOA Quantum Sampling"]
    CurvatureCheck -- "No" --> SlackCheck{"Capacity Slack > 0.15?"}
    SlackCheck -- "Yes" --> RandomOrTabu{"60% Tabu Search / 40% Random Feasible"}
    SlackCheck -- "No" --> DefaultTabu["Default Tabu Search"]
    
    FastFallback --> CandidateRoute["Candidate Route R_cand"]
    TabuEscape --> CandidateRoute
    QAOADispatch --> CandidateRoute
    RandomOrTabu --> CandidateRoute
    DefaultTabu --> CandidateRoute

    CandidateRoute --> GuardCoverage{"Coverage Valid? set(stops) == S & len == N"}
    GuardCoverage -- "No" --> RejectCoverage["Reject: Retain Incumbent (INVALID_CUSTOMER_COVERAGE)"]
    GuardCoverage -- "Yes" --> GuardCap{"Capacity Valid? q_A <= Q_A & q_B <= Q_B & q > 0"}
    GuardCap -- "No" --> RejectCap["Reject: Retain Incumbent (CAPACITY_CONSTRAINT_VIOLATION)"]
    GuardCap -- "Yes" --> GuardCost{"Cost(VND(R_cand)) < Cost(VND(R_inc)) - 1e-4"}
    GuardCost -- "No" --> RejectCost["Reject: Retain Incumbent (SUBOPTIMAL_OBJECTIVE_REJECTED)"]
    GuardCost -- "Yes" --> AcceptCandidate["Adopt Candidate Route R_final = VND(R_cand)"]
```

---

## 6. Complete End-to-End Experimental & Audit Workflow

Illustrates the end-to-end benchmarking and verification procedure across all phases.

```mermaid
flowchart LR
    A["Instance Generator (Seeded Coordinates & Demands)"] --> B["Spatial Polar Decomposition (Spark local[*])"]
    B --> C["Initial Route Baseline (OR-Tools / Sequential)"]
    C --> D["Initial VND Untangling (Config B Baseline)"]
    D --> E["Candidate Generators: Random, KL, Tabu, QAOA"]
    E --> F["Route Reconstruction & VND Polish"]
    F --> G["Proposition 1 Safety Acceptance Filter"]
    G --> H["Raw Telemetry & Metric Logging (CSV / JSON)"]
    H --> I["Independent Statistical Reanalysis (Paired t, Wilcoxon, Cohen's d)"]
```

---

## 7. Deployment Call Graph & Research Module Isolation

This diagram illustrates that `phase_ab_cooperative_optimization_engine/` and `phase_ac_independent_validation/` are self-contained research packages that are deliberately decoupled from the production FastAPI backend and React frontend.

```mermaid
graph TD
    subgraph PRODUCTION APPLICATION [Live Deployment : localhost:8000 & 5173]
        Frontend[React Vite Dashboard : frontend/src/] --> RESTAPI[FastAPI Endpoints : backend/app/main.py]
        RESTAPI --> ClassicalAPI[Classical Solver Service : OR-Tools / Clarke-Wright]
        RESTAPI --> QuantumAPI[Quantum Solver Service : Basic Qiskit Transpiler]
        RESTAPI --> QIGAAPI[Quantum-Inspired Genetic Algorithm Service]
        RESTAPI --> SparkService[Big Data Ingestion Pipeline Service]
    end

    subgraph RESEARCH WORKSPACE [Autonomous Research Packages : Unmerged Branches]
        CooperativeEngine[Cooperative Optimization Engine : phase_ab/]
        ValidationAudit[Independent Validation & Audit Suite : phase_ac/]
        ResearchPaper[Final Research Paper & Presentation : phase_ad/]
        CooperativeEngine --> ValidationAudit
        ValidationAudit --> ResearchPaper
    end

    RESTAPI -.->|NO COUPLING / SAFEGUARDED| CooperativeEngine
```
