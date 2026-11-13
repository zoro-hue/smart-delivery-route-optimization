# Deliverable 12: Phase V Winning Architecture Specification

## 1. Validated Hybrid Architecture: Dual-Pillar Cooperative Engine

Based on the forensic audit and causal ablation of Phase V, the final, scientifically defensible architecture for ROUTE/IQ integrates **Apache Spark 4.2.0 (Pillar 1)** and **QAOA / Qiskit 2.4.1 (Pillar 2)**, grounded upon **Robust Classical Optimization**:

```mermaid
flowchart TD
    subgraph Pillar1["PILLAR 1: Big Data Computing (Apache Spark 4.2.0)"]
        D1["Fleet Deliveries & Network Topologies"] --> SP1["Distributed Ingestion & Cleansing"]
        SP1 --> SP2["Spatial Clustering & Boundary Buffer Filtering"]
        SP2 --> SP3["Boundary Subproblem Extraction (N <= 16 qubits)"]
    end

    subgraph ClassicalSeed["Classical Fleet Initialization"]
        D1 --> CL1["OR-Tools CVRP / Clarke-Wright Savings"]
        CL1 --> CL2["Incumbent Route Baseline (R_incumbent)"]
    end

    subgraph Pillar2["PILLAR 2: Quantum Computing (QAOA / Qiskit 2.4.1)"]
        SP3 --> QC1["Ising Hamiltonian Mapping (h_i, J_ij)"]
        QC1 --> QC2["p=1 QAOA Variational Circuit (Qiskit Aer)"]
        QC2 --> QC3["Raw Bitstring Measurement Sampling (1024 shots)"]
    end

    subgraph ClassicalGuardrail["Classical Feasibility, Refinement & Certification"]
        QC3 --> CR1["Deterministic Capacity Repair (100% Feasibility)"]
        CR1 --> CR2["Algorithmic VND (Relocate, Swap, 2-opt)"]
        CR2 --> CR3["Proposition 1 Acceptance Guardrail: Cost(R_cand) <= Cost(R_incumbent)"]
        CL2 -.-> CR3
        CR3 --> F1["Final Dispatch Schedule"]
    end
```

---

## 2. Division of Responsibility in the Dual Pillars

1. **Major Pillar 1 — Apache Spark 4.2.0 (Big Data)**:
   - Ingests large delivery batches, computes spatial centroids, and filters boundary customer subsets ($N \le 16$) that sit between adjacent vehicle routes.
   - Enables parallel subproblem dispatch across multiple vehicle pairs.

2. **Major Pillar 2 — QAOA / Qiskit 2.4.1 (Quantum Computing)**:
   - Operates strictly on bounded $N \le 16$ boundary customer clusters.
   - Evaluates the trade-off between customer clustering affinity and vehicle load balance via variational quantum circuits.

3. **Supporting Classical Foundation**:
   - **Initialization**: OR-Tools / Clarke-Wright provides strong incumbent solutions.
   - **Feasibility**: Deterministic repair resolves the 55.08% capacity violation rate in raw quantum samples.
   - **Local Search**: Algorithmic VND delivers rigorous intra- and inter-route optimization.
   - **Safety**: Proposition 1 Guardrail guarantees $\text{Cost}(R_{\text{final}}) \le \text{Cost}(R_{\text{incumbent}})$ unconditionally.
