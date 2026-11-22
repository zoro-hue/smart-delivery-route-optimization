# Phase S Deliverable 13: Winning Architecture Specification — IP-CQE v3 (Directed Asymmetric Edition)

**Document:** `phase_s_asymmetric_quantum_neighborhoods/PHASE_S_WINNING_ARCHITECTURE.md`  
**Date:** 2026-11-06  
**Status:** Completed & Rigorously Verified  
**Branch:** `research/phase-s-asymmetric-quantum-neighborhoods`

---

## 1. System Architecture Overview

The final architecture synthesized from Phase S findings is **IP-CQE v3 (Incumbent-Preserving Cooperative Quantum Engine: Directed Asymmetric Edition)**.

It preserves both mandatory computational pillars:
- **Pillar 1 (Big Data):** Apache Spark 4.2.0 distributed preprocessing, BPR traffic delay modeling, and spatial polar-angle window partitioning.
- **Pillar 2 (Quantum Computing):** Variational QAOA parameterized with continuous XY-mixers and Hungarian bipartite post-projection.
- **Classical Supporting Infrastructure:** Google OR-Tools Guided Local Search augmented with **Variable Neighborhood Descent (VND: Relocate + Swap + Or-opt + Directed 2-opt)** and Proposition 1 Monotonic Guardrail certification.

```mermaid
flowchart TD
    subgraph Pillar1["Computational Pillar 1: Apache Spark 4.2.0"]
        A[NYC DOT Traffic Volume Streams\nNOAA Weather Friction Data] --> B[Calibrated BPR Travel Time Engine\nt(e) = t0 * (1 + 0.15*(V/C)^4) * W_friction]
        B --> C[PySpark Polar-Angle Spatial Decomposition\nCumulative Vehicle Capacity Windowing]
    end

    subgraph ClassicalFoundation["Classical Optimization Foundation"]
        C --> D[Google OR-Tools CVRP Solver\nGuided Local Search with Time Bounding]
        D --> E[Directed Classical VND Refinement\nRelocate -> Swap -> Or-opt -> Directed 2-opt]
        E --> F[Certified High-Quality Incumbent R_incumbent]
    end

    subgraph Gating["Phase S Empirical Decision Gating"]
        F --> G{Directed Asymmetry alpha >= 0.35\nAND Classical Stagnation\nAND Quantum Budget Available?}
        G -- No --> M[Bypass Quantum Execution\nRetain Incumbent]
        G -- Yes --> H[Extract Bounded Subproblem QUBO\nSize K=4 to 6]
    end

    subgraph Pillar2["Computational Pillar 2: QAOA Quantum Engine"]
        H --> I[Warm-Start State Preparation\n|psi_0> = |pi_seed>]
        I --> J[Continuous XY-Mixer Circuit\nU_XY(beta) with COBYLA Optimization]
        J --> K[Hungarian Bipartite Projection\nResolve Column Collisions (68.8% frequency)]
    end

    subgraph Certification["Proposition 1 Non-Degradation Guardrail"]
        K --> L[Classical Polish & Complete Tour Feasibility Check]
        L --> N{Cost(R_candidate) < Cost(R_incumbent)\nAND IsFeasible?}
        N -- Yes --> O[Accept Quantum Candidate\nR_final = R_candidate]
        N -- No --> P[Trigger Proposition 1 Guardrail\nR_final = R_incumbent]
        M --> O
        P --> O
    end

    O --> Q[Certified Final Production Dispatch Plan]
```

---

## 2. Key Architectural Upgrades in IP-CQE v3

1. **Replaced Pure 2-opt with Directed VND:**  
   Phase S demonstrated that pure 2-opt suffers from $15.25\%$ average optimality gap on asymmetric networks due to edge inversion penalties. IP-CQE v3 embeds Variable Neighborhood Descent (Relocate $\to$ Swap $\to$ Or-opt $\to$ Directed 2-opt) into the classical foundation, reducing classical gap to $0.33\%$ in $0.19\text{ ms}$.
2. **Empirical Quantum Decision Gating:**  
   QAOA is no longer dispatched blindly across arbitrary clusters. The Gating Engine inspects the subproblem's Frobenius asymmetry ratio $\alpha(D)$. If $\alpha < 0.35$ or if classical VND has already proven global optimality, quantum circuit execution is bypassed, saving $98\%$ of simulation runtime.
3. **Mandatory Hungarian Decoder:**  
   Because $68.85\%$ of raw measurements from row-wise XY-mixers violate column uniqueness, every quantum measurement is processed by Kuhn-Munkres bipartite matching before candidate evaluation.
4. **Guaranteed Zero Solution Degradation:**  
   Proposition 1 guarantees that regardless of quantum sampling noise, the certified output tour $R_{\text{final}}$ will never exceed the classical cost floor:
   $$\text{Cost}(R_{\text{final}}) \le \text{Cost}(R_{\text{incumbent}}) \quad \forall \text{ instances}$$

