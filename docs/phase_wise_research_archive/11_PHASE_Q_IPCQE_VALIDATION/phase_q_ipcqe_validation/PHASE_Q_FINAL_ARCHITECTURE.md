# ROUTE/IQ — PHASE Q: FINAL ARCHITECTURE SPECIFICATION
**Validated Champion Architecture: Incumbent-Preserving Cooperative Quantum Engine (IP-CQE v2)**

- **Date:** 2026-11-06
- **Architecture Champion:** **IP-CQE v2 (Variational Incumbent-Preserving Cooperative Quantum Engine)**
- **Major Pillar 1:** Apache Spark 4.2.0 Big Data Preprocessing & BPR Traffic Impedance
- **Major Pillar 2:** Variational QAOA on Qiskit Aer (16 Logical Qubits, XY Hopping Mixers)
- **Supporting Optimization:** Google OR-Tools CVRP + Planar Crossing Detection + Classical 2-opt Polish + Proposition 1 Guardrail

---

## 1. Complete Architecture Dataflow & Component Interaction

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                               PILLAR 1: BIG DATA COMPUTING                              │
│ - Apache Spark 4.2.0 Ingestion: Ingests NYC delivery orders & road network graph         │
│ - BPR Travel Impedance Engine: t(e) = t_0 [1 + 0.15(V/C)^4] * W_friction                │
│ - Distributed Polar Sweep: theta = atan2(dy, dx), Window.orderBy(theta).sum(demand)     │
│ - Outputs balanced vehicle clusters with std dev sigma < 1.2 customers                  │
└────────────────────────────────────────────┬────────────────────────────────────────────┘
                                             │
                                             ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                         SUPPORTING: CLASSICAL OPERATIONS RESEARCH                       │
│ - Google OR-Tools CVRP Solver with Guided Local Search                                  │
│ - Generates Initial Certified Incumbent Route R_0 with Baseline Cost C_0                │
│ - Bottleneck Screener: Detects edge crossing intersections & asymmetric detour traps     │
└────────────────────────────────────────────┬────────────────────────────────────────────┘
                                             │
                                             ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                               PILLAR 2: QUANTUM COMPUTING                               │
│ - Subproblem Extraction: Isolates K=4 customer microclusters (N_q = 16 qubits)          │
│ - Classical Permutation Basis State Preparation: |psi_0> = |x_seed>                     │
│ - Continuous XY Hopping Mixers: (XX + YY) preserves row particle number (100% row yield)│
│ - Variational Parameter Adaptation: COBYLA tunes (gamma, beta) to minimize energy       │
│ - Kuhn-Munkres Hungarian Projection: Decodes raw bitstring with minimal delta (<0.76 b) │
└────────────────────────────────────────────┬────────────────────────────────────────────┘
                                             │
                                             ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                     ADAPTIVE RECONSTRUCTION & INCUMBENT GUARDRAIL                       │
│ - Local 2-opt Polish: Cleans subproblem boundary endpoint connections                   │
│ - Proposition 1 Monotonic Incumbent Guardrail:                                          │
│       R_final = R_hybrid if (Cost(R_hybrid) < Cost(R_0) and Feasible) else R_0          │
│ - Feasibility Guarantee: 100% customer preservation, 0 drops, 0 duplicates              │
│ - Telemetry: Unbundled Spark time, QAOA circuit time, and classical optimizer timers    │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Key Mathematical Invariants & Verification Checklist

1. **Monotonic Feasible Cost Property (Proposition 1):**
   $$\text{Cost}(R_{\text{final}}) \le \text{Cost}(R_{\text{OR-Tools}})$$
   Guaranteed by the algorithmic acceptance filter. The system never accepts an inferior or infeasible route.
2. **Qubit Budget Compliance:**
   Strict $16$-qubit ceiling ($K=4 \implies 4 \times 4 = 16$ qubits). Circuit memory footprint is restricted to $\approx 1\text{ MB}$, completely eliminating container OOM risks.
3. **Exact Row Particle Conservation:**
   $$[H_M^{(XY)}, \sum_{p=0}^{K-1} x_{ip}] = 0$$
   Guarantees that no customer is duplicated or omitted within the microcluster.
4. **Transparent Simulation Attribution:**
   All quantum circuits execute classically on `qiskit_aer.AerSimulator`. Physical QPU advantage is not claimed.

