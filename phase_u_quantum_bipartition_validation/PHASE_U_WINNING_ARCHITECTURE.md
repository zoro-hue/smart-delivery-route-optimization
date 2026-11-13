# Deliverable 14: Phase U Winning Architecture Specification

## 1. Architectural Blueprint: Dual-Pillar Hybrid Cooperative Engine

Based on the empirical findings of Phases P through U, the winning architecture for ROUTE/IQ integrates **Apache Spark 4.2.0 (Pillar 1)** and **QAOA / Qiskit (Pillar 2)**, reinforced by **Classical Optimization Engines (OR-Tools, VND, Deterministic Capacity Repair)**:

```mermaid
flowchart TD
    subgraph Pillar1["PILLAR 1: Big Data Computing (Apache Spark 4.2.0)"]
        D1["Fleet Deliveries & Road Network"] --> SP1["Distributed Ingestion & Cleaning"]
        SP1 --> SP2["Spatial Clustering & Buffer Filtering"]
        SP2 --> SP3["Boundary Candidate Subproblem Extraction (N <= 16)"]
    end

    subgraph ClassicalSeed["Classical Fleet Initialization"]
        D1 --> CL1["OR-Tools CVRP / Clarke-Wright Savings"]
        CL1 --> CL2["Incumbent Route Baseline (R_incumbent)"]
    end

    subgraph Pillar2["PILLAR 2: Quantum Computing (QAOA / Qiskit)"]
        SP3 --> QC1["Ising Hamiltonian Mapping (h_i, J_ij)"]
        QC1 --> QC2["p-Layer QAOA Variational Circuit (Qiskit Aer)"]
        QC2 --> QC3["Raw Bitstring Measurement Sampling"]
    end

    subgraph ClassicalCooperation["Classical Cooperation & Route Certification"]
        QC3 --> CR1["Deterministic Capacity Repair"]
        CR1 --> CR2["Intra-Route 2-opt / VND Sequencing"]
        CR2 --> CR3["Proposition 1 Acceptance Guardrail: Cost(R_cand) <= Cost(R_incumbent)"]
        CL2 -.-> CR3
        CR3 --> F1["Certified Fleet Delivery Schedule"]
    end
```

---

## 2. Division of Computational Responsibility

1. **Apache Spark (Pillar 1)**:
   - Manages large scale customer batches, spatial coordinate transformations, and candidate extraction.
   - Decouples large-scale VRP problems into bounded $N \le 16$ customer subproblems.

2. **QAOA / Qiskit (Pillar 2)**:
   - Explores the combinatorial trade-off between customer clustering affinity and vehicle capacity balance via parameterized quantum circuits.

3. **Classical Optimization (Supporting Engines)**:
   - Generates initial fleet routes (OR-Tools, Clarke-Wright).
   - Enforces 100% capacity feasibility through deterministic repair.
   - Evaluates intra-route TSP tours via 2-opt / VND.
   - Enforces the Proposition 1 Guardrail to eliminate regression risk.
