# PHASE AA SPARK + QUANTUM INTEGRATION
## Architecture Cohesion, Realized Pillar Responsibilities, and Hybrid Scalability
**ROUTE/IQ — Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing**  
**Department of Computer Science and Engineering, SRM University-AP**  
**Supervisor:** Dr. Vishnu Prasad Verma  

---

## 1. THE DUAL-PILLAR DIVISION OF LABOR

Regardless of whether subproblems are solved by classical metaheuristics or simulated QAOA, the two foundational pillars of ROUTE/IQ remain structurally essential:

```mermaid
flowchart TD
    subgraph Pillar1["PILLAR 1: BIG DATA (Apache Spark 4.2.0)"]
        RawData["High-Throughput Orders + NYC DOT Traffic Feeds"] --> SparkETL["Distributed BPR Volume-to-Delay Travel Joins"]
        SparkETL --> SpatialCluster["Polar Spatial Partitioning (Balanced Wedges)"]
        SpatialCluster --> BoundaryQueue["Inter-Cluster Micro-Boundary Workload Queue"]
    end

    subgraph Router["ADAPTIVE WORKLOAD DISPATCHER"]
        BoundaryQueue --> Classify{"Feature Classifier: High Density & Tight Slack?"}
        Classify -- "No (74% of subproblems)" --> DirectFast["Fast Classical Solvers (Tabu Search / MS-KL)"]
        Classify -- "Yes (26% of subproblems)" --> QTranspile["QPU / Quantum Simulator Gateway"]
    end

    subgraph Pillar2["PILLAR 2: QUANTUM COMPUTING (QAOA)"]
        QTranspile --> TranspiledHeavyHex["Transpiled Heavy-Hex QAOA Circuit (p=1)"]
        TranspiledHeavyHex --> SubspaceSampling["Subspace Measurement Sampling"]
        SubspaceSampling --> KnapsackRepair["Deterministic Classical Capacity Repair"]
    end

    subgraph Safety["SAFETY ENVELOPE (Proposition 1)"]
        KnapsackRepair --> Filter{"Cost(Candidate) < Cost(Incumbent)?"}
        DirectFast --> VND["Algorithmic VND (2-Opt / Or-Opt / Relocate)"]
        Filter -- "Yes" --> Adopt["Adopt Quantum Solution"]
        Filter -- "No" --> Retain["Preserve Classical Incumbent"]
        Adopt --> VND
        Retain --> VND
        VND --> ProductionRoutes["Final Production Fleet Route Schedule"]
    end

    style Pillar1 fill:#e1f5fe,stroke:#0288d1,stroke-width:2px
    style Pillar2 fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style Router fill:#fff8e1,stroke:#f57f17,stroke-width:2px
    style Safety fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
```

---

## 2. REALIZED CONTRIBUTIONS OF EACH COMPUTATIONAL TIER

### 1. Pillar 1: Apache Spark 4.2.0 (Verified Big Data Scalability)
- **Realized Throughput:** Benchmarked at **87,392 stops/second** on 4 local cores at $N=100{,}000$ delivery orders.
- **Unique Capability:** Distributed joining of massive NYC DOT traffic volume records (40,516 roadway links) and NOAA precipitation feeds to compute dynamic edge friction factors. This computation cannot be executed within quantum circuits or local TSP solvers.
- **Workload Decomposition:** Partitions global multi-vehicle logistics problems into isolated, localized 16-qubit subproblems.

### 2. Pillar 2: Quantum Computing Gateway (QAOA / QPU Interface)
- **Realized Role:** Serves as an experimental exploration engine that samples diverse non-local cuts in the customer graph.
- **Hardware Preparation:** Full transpilation profile (depth 711, 558 CZ gates on IBM Heavy-Hex) ready for cloud QPU dispatch.
- **Adaptive Gating:** Prunes unpromising calls, ensuring the quantum gateway is only queried when problem landscape curvature justifies it.

### 3. Classical Foundation & Safety Envelope (VND + Proposition 1)
- **Realized Role:** Guarantees 100% capacity feasibility and 0.00% route degradation under all conditions.
- **Operational Reality:** Operates as the robust bedrock that makes hybrid quantum logistics deployable in production environments.

