# PHASE AE: BACKEND ARCHITECTURE & COOPERATIVE PIPELINE SPECIFICATION
## ROUTE/IQ — Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing
**Repository:** `D:\UROP\smart-delivery-route-optimization`  
**Branch:** `research/phase-ae-backend-integration`  
**Protected Main Baseline:** `a8eb849988201d7929566f331c1ae3afac09b632`  
**Date:** November 2026  
**Institution:** Department of Computer Science and Engineering, SRM University-AP  
**Supervisor:** Dr. Vishnu Prasad Verma  
**Investigators:** J. Jayanth, B. Kaivalya, P. Shyam Sai

---

## 1. System Architecture Overview

The ROUTE/IQ Cooperative Optimization Architecture integrates distributed Big Data spatial pre-processing with hybrid quantum-classical search and rigorous classical metaheuristics. It operates under a strict monotonic non-degradation contract formalized by Proposition 1.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        FRONTEND OPERATOR DASHBOARD                      │
│     (Preserved 100%: Zinc Dark / Neon Volt Theme, Cards, Leaflet Map)  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP REST API (JSON)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        FASTAPI REST BACKEND GATEWAY                    │
│      Endpoint: POST /api/optimization/run (Dispatch Controller)        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
           ┌────────────────────────┴────────────────────────┐
           ▼                                                 ▼
┌───────────────────────┐                         ┌───────────────────────┐
│ INDEPENDENT BASELINES │                         │   ROUTE/IQ COOPERATIVE│
│ • OR-Tools (CVRP)     │                         │   OPTIMIZATION ENGINE │
│ • Clarke-Wright       │                         └───────────┬───────────┘
│ • 2-Opt Improvement   │                                     │
│ • Dijkstra Tree       │                                     ▼
│ • A* Heuristic        │                 ┌───────────────────────────────────────┐
│ • QIGA Evolutionary   │                 │ PILLAR 1: APACHE SPARK 4.2.0           │
│ • QAOA Statevector    │                 │ • Spatial Polar Coordinate Clustering │
└───────────────────────┘                 │ • Boundary Customer Identification   │
                                          └───────────────────┬───────────────────┘
                                                              │
                                                              ▼
                                          ┌───────────────────────────────────────┐
                                          │ ADAPTIVE STRATEGY CONTROLLER (MAB)   │
                                          │ • Feature Vector Evaluation           │
                                          │ • Dynamic Generator Selection         │
                                          └───────┬───────────────────────┬───────┘
                                                  │                       │
                                    ┌─────────────┴─────┐   ┌─────────────┴─────┐
                                    ▼                   ▼   ▼                   ▼
                               ┌───────────┐       ┌───────────┐           ┌───────────┐
                               │ PILLAR 2: │       │ TABU      │           │ MULTISTART│
                               │ FAST QAOA │       │ SEARCH    │           │ K-LIN     │
                               │ XY-Mixer  │       │ Tenured   │           │ Heuristic │
                               └─────┬─────┘       └─────┬─────┘           └─────┬─────┘
                                     │                   │                       │
                                     └─────────────┬─────┴───────────────────────┘
                                                   │ Candidate Partitions
                                                   ▼
                                          ┌───────────────────────────────────────┐
                                          │ CLASSICAL REFINEMENT: ALGORITHMIC VND │
                                          │ • Relocate Operator                   │
                                          │ • Swap Operator                       │
                                          │ • Intra-Route 2-Opt Inversion         │
                                          └───────────────────┬───────────────────┘
                                                              │
                                                              ▼
                                          ┌───────────────────────────────────────┐
                                          │ PROPOSITION 1 ACCEPTANCE GUARDRAIL   │
                                          │ f(x_cand) <= f(x_inc) AND Feasible?   │
                                          │  ├─ YES: Accept Improved Solution     │
                                          │  └─ NO:  Reject & Preserve Incumbent  │
                                          └───────────────────┬───────────────────┘
                                                              │
                                                              ▼
                                          ┌───────────────────────────────────────┐
                                          │ Validated Routes & Real Telemetry     │
                                          └───────────────────────────────────────┘
```

---

## 2. Pillar 1: Apache Spark 4.2.0 Distributed Spatial Workload Organizer

The Big Data tier decomposes high-dimensional geographic demand distributions across NYC into tractable vehicle routing subproblems:

1. **Distributed Data Ingestion & Sanitization:**
   - Validates schema against missing values, invalid GPS coordinates, and water body collisions.
   - Cleans and deduplicates customer orders using PySpark DataFrames on local cluster execution (`local[*]`).
2. **Polar Angle Geometric Sweep:**
   - For customer stop $i$ with coordinates $(\text{lat}_i, \text{lon}_i)$ relative to depot $(\text{lat}_0, \text{lon}_0)$:
     $$\theta_i = \text{atan2}(\text{lat}_i - \text{lat}_0, \text{lon}_i - \text{lon}_0)$$
   - Sorts customers along the circular sweep $\theta_i \in [-\pi, \pi]$ and partitions them into angular wedges bounded by vehicle capacity:
     $$\sum_{i \in \mathcal{W}_k} q_i \le Q_k$$
3. **Centroid-Difference Boundary Extraction:**
   - For adjacent clusters $\mathcal{C}_a$ and $\mathcal{C}_b$ with centroids $\mathbf{c}_a, \mathbf{c}_b$:
     $$\Delta d_i = |\|\mathbf{x}_i - \mathbf{c}_a\|_2 - \|\mathbf{x}_i - \mathbf{c}_b\|_2|$$
   - Boundary nodes with $\Delta d_i \le \tau_{\text{boundary}}$ are extracted into a localized boundary subproblem $\mathcal{B}_{ab}$.

---

## 3. Pillar 2: Variational Quantum Candidate Generation & Classical Metaheuristics

The boundary customer partition problem is mapped to an unconstrained binary quadratic problem (QUBO) / Ising Hamiltonian:
$$\mathcal{H}_C = \sum_{i < j} J_{ij} Z_i Z_j + \sum_i h_i Z_i$$

### 3.1 Fast QAOA (Variational Quantum Optimization)
- **Circuit Depth:** $p \in \{1, 2\}$.
- **Parameterized State:** $|\psi(\boldsymbol{\gamma}, \boldsymbol{\beta})\rangle = \prod_{k=1}^p e^{-i \beta_k \mathcal{H}_M} e^{-i \gamma_k \mathcal{H}_C} |+\rangle^{\otimes N}$.
- **Mixer Hamiltonian $\mathcal{H}_M$:**
  - Standard Transverse Mixer: $\mathcal{H}_M^{(X)} = \sum_{i=1}^N X_i$.
  - Subspace XY Mixer: $\mathcal{H}_M^{(XY)} = \sum_{(i,j) \in \mathcal{E}} (X_i X_j + Y_i Y_j)$ preserving Hamming weight (cluster balance).
- **Simulation Backend:** Qiskit `Statevector` backend simulation.

### 3.2 Classical Metaheuristic Generators
- **Tabu Search (`Tabu_Search`):**
  - Maintains dynamic tabu tenure $T = 7$ iterations.
  - Explores 1-flip neighborhood with aspiration criterion (overrides tabu state if candidate strictly improves global best).
- **Multistart Kernighan-Lin (`Multistart_KL`):**
  - Iterative 2-exchange partition refinement evaluated over 10 randomized initial configurations.

---

## 4. Adaptive Strategy Controller (Multi-Armed Bandit)

The Adaptive Controller selects the generator dynamically using an Upper Confidence Bound (UCB-1) / Feature Gated policy:

$$\text{Score}(a) = \bar{\mu}_a + c \sqrt{\frac{\ln t}{N_a(t)}} + \boldsymbol{\theta}^T \mathbf{x}_{\text{sub}}$$

where:
- $\bar{\mu}_a$: Empirical reward rate of generator $a$ (frequency of accepted non-zero distance improvements under Proposition 1).
- $N_a(t)$: Number of times generator $a$ has been selected.
- $\mathbf{x}_{\text{sub}} = [N_{\text{boundary}}, \text{Slack}_{\text{capacity}}, \rho_{\text{interaction}}, t_{\text{remaining}}]^T$: Contextual feature vector.
- **Safety Policy:** If remaining latency budget $t_{\text{remaining}} < 25\text{ ms}$, the controller overrides to classical fast heuristic (`Tabu_Search` or `Multistart_KL`) to maintain sub-second interactive response on the dashboard.

---

## 5. Classical Route Refinement: Algorithmic VND

Once a candidate partition $(\mathcal{A}, \mathcal{B})$ is generated, it is transformed into vehicle tours and refined via Variable Neighborhood Descent:

1. **Neighborhood 1: Relocate Operator (1-0 Exchange):**
   - Moves customer $i \in \mathcal{A}$ into route $\mathcal{B}$ at insertion index $k$ if $C_b + q_i \le Q_b$ and $\Delta f < 0$.
2. **Neighborhood 2: Swap Operator (1-1 Exchange):**
   - Exchanges customer $i \in \mathcal{A}$ with customer $j \in \mathcal{B}$ if capacities permit and $\Delta f < 0$.
3. **Neighborhood 3: Intra-Route 2-Opt Inversion:**
   - Reverses sub-sequence $(i..j)$ within each route if $d(i-1, j) + d(i, j+1) < d(i-1, i) + d(j, j+1)$.

---

## 6. Proposition 1 Acceptance Guardrail

The Proposition 1 non-degradation guardrail is the central mathematical safety mechanism of ROUTE/IQ. 

$$\mathbf{x}_{\text{next}} = \begin{cases} \mathbf{x}_{\text{cand}}, & \text{if } f(\mathbf{x}_{\text{cand}}) \le f(\mathbf{x}_{\text{inc}}) \;\wedge\; \forall k, C_k(\mathbf{x}_{\text{cand}}) \le Q_k \\ \mathbf{x}_{\text{inc}}, & \text{otherwise} \end{cases}$$

### Theoretical Guarantees:
1. **Monotonic Non-Degradation:** The final route distance $f(\mathbf{x}_{\text{final}})$ is strictly bounded by the incumbent distance:
   $$f(\mathbf{x}_{\text{final}}) \le f(\mathbf{x}_{\text{inc}})$$
2. **100% Invariant Feasibility:** If the initial incumbent is capacity-feasible, the output solution is guaranteed to remain strictly capacity-feasible.
3. **Safe Quantum Exploration:** Experimental QAOA candidate generation can be deployed freely without risk of deteriorating operational logistics performance.

