# ROUTE/IQ: Chronological Project History & Engineering Timeline
**Time Horizon:** September 1, 2026 to November 21, 2026  
**Methodology:** Git Commit Forensic Reconstruction & Development Log Analysis  
**Institutional Milestone:** SRM University-AP UROP Research Cycle  
**Status:** Complete Forensic Record `[VERIFIED]`

---

## 1. Timeline Overview: Key Eras of ROUTE/IQ

```
+-----------------------------------------------------------------------------+
| ERA 1: GENESIS & EXPLORATION (Sept 1 - Sept 20, 2026)                       |
| Problem Formulation, NYC Graph Extraction, Classical Heuristic Prototyping  |
+-----------------------------------------------------------------------------+
                                      |
                                      v
+-----------------------------------------------------------------------------+
| ERA 2: QUANTUM & SPARK FOUNDATIONS (Sept 21 - Oct 15, 2026)                 |
| PySpark Polar Sweep, Qiskit QAOA Hamiltonian Formulation, Angular Disruption|
+-----------------------------------------------------------------------------+
                                      |
                                      v
+-----------------------------------------------------------------------------+
| ERA 3: AUTONOMOUS RESEARCH PHASES P-W (Oct 16 - Nov 5, 2026)               |
| MAB Adaptive Controller, QGAR Boundary Search, Proposition 1 Proof          |
+-----------------------------------------------------------------------------+
                                      |
                                      v
+-----------------------------------------------------------------------------+
| ERA 4: BACKEND CLOUD & MEMORY CRUCIBLE (Nov 6 - Nov 15, 2026)               |
| Phase AE: Render 512MB RAM Cap, NPZ/CSR Road Caching, Full REST Integration  |
+-----------------------------------------------------------------------------+
                                      |
                                      v
+-----------------------------------------------------------------------------+
| ERA 5: SUPREMACY & PRODUCTION HARDENING (Nov 16 - Nov 21, 2026)              |
| Next-Gen ALNS Ruin-and-Recreate, Regret-3, Bug Autopsies, 30-Instance Win   |
+-----------------------------------------------------------------------------+
```

---

## 2. Chronological Deep Dive by Phase

### Phase 1: Genesis & Foundations (Sept 1 – Sept 20, 2026)
- **Problem Identification:** Meeting with supervisor Prof. Vishnu Prasad Verma to establish UROP project scope. The problem: last-mile delivery route optimization combining big data spatial systems and emerging quantum optimization paradigms.
- **Dataset Extraction:** Assembled open-source operational datasets for New York City:
  - 1,898 delivery points from NYC OpenData commercial delivery zones.
  - 10,000 TLC vehicle records for realistic fleet capacity distributions.
  - NYC DOT automated traffic sensor data (42,756 records) and NOAA weather observations.
  - Road network extracted via OSMnx from OpenStreetMap (54,128 nodes, 134,814 edges).
- **Initial Architecture:** Built initial React 18 + Leaflet frontend and FastAPI backend skeleton. Implemented basic classical algorithms: Dijkstra, A*, and Clarke-Wright savings.

### Phase 2: Quantum & Spark Integration (Sept 21 – Oct 15, 2026)
- **Spark Workload Organizer:** Implemented `SparkWorkloadOrganizer` utilizing PySpark 4.2.0 to compute polar angle coordinates relative to municipal depots ($	heta = 	ext{atan2}(\Delta y, \Delta x)$) and partition customers into vehicle sectors.
- **Discovery of the "Angular Disruption Effect":** Identified that rigid polar angular clustering often cuts across natural street corridors or separates delivery points on opposite sides of a one-way street, increasing total travel distance. Introduced boundary customer identification to mitigate this.
- **Initial QAOA Formulation:** Built gate-based QAOA using Qiskit 2.4.1. Formulated CVRP boundary partitioning as an unconstrained Quadratic Unconstrained Binary Optimization (QUBO) problem using penalty multipliers $A, B$.
- **Discovery of Penalty Imbalance:** Observed that standard transverse mixer QAOA frequently produced infeasible solutions (vehicle capacity exceeded) because penalty terms distorted the ground state energy landscape.

### Phase 3: Autonomous Research Cycles (Phases P – W) (Oct 16 – Nov 5, 2026)
- **Phase P:** Drafted comprehensive mathematical framework, risks and research integrity protocol. Introduced XY-mixer Alternating Operator Ansatz to restrict quantum state evolution to valid subspace permutations.
- **Phase Q & R (IPCQE Validation):** Tested Iterative Polar-Cooperative Quantum Engine. Discovered that pure simulated QAOA on classical CPU scales poorly ($O(2^n)$) beyond 16 qubits, motivating its restriction to local 2-vehicle boundary subproblems.
- **Phase S & T (Adaptive Controller):** Designed `AdaptiveCooperativeController` using Multi-Armed Bandit (UCB1) theory to balance exploration and exploitation across solver operators.
- **Phase U & V (Proposition 1 Formalization):** Mathematically formulated and implemented the Proposition 1 Non-Degradation Guardrail:
  $$	ext{Cost}(S_{	ext{final}}) = \min(	ext{Cost}(S_{	ext{incumbent}}), 	ext{Cost}(S_{	ext{candidate}}))$$
  Guaranteed zero solution degradation even when quantum simulation diverged.
- **Phase W (Reproducibility & Seed Control):** Established 30-instance deterministic benchmark suite with locked pseudo-random seeds.

### Phase 4: Production Deployment & Cloud Memory Optimization (Phases X – AE) (Nov 6 – Nov 15, 2026)
- **Render Cloud Barrier:** Deployment to Render free tier failed with Out-Of-Memory (OOM, error code 137). Loading the 54,128-node NetworkX GraphML file consumed 1,240 MB RAM against the 512 MB physical limit.
- **Phase AE Sparse Breakthrough:** Converted the road graph into a precomputed SciPy Compressed Sparse Row (CSR) matrix (`road_matrix_csr.npz`) and coordinate lookup table. Reduced cold-start memory footprint from 1,240 MB to 280 MB, achieving instant startup on Render.
- **Vercel Frontend Deployment:** Successfully deployed Vite React frontend to Vercel, integrating live polling and WebSocket-compatible REST communication.

### Phase 5: Supremacy Engineering & Final Archival (Nov 16 – Nov 21, 2026)
- **Next-Generation Cooperative Engine:** Engineered a major algorithmic leap by integrating Adaptive Large Neighborhood Search (ALNS) ruin-and-recreate operators:
  - Shaw relatedness removal (spatial proximity + demand affinity).
  - Worst-cost removal (targeting high-impedance road segments).
  - Random perturbation removal.
  - Regret-3 insertion (evaluating opportunity cost across 3 best vehicle insertion positions).
- **The 30-Instance Supremacy Milestone:** Evaluated Next-Gen engine on 30 benchmark instances: **12 wins, 18 ties, 0 losses** against Google OR-Tools (+0.61% average distance reduction, 100% feasibility).
- **Critical Production Bug Autopsies:** Resolved the 10/11 queued solver freeze, dataset sync timeout (350s), and route identity visual sharing.
- **Master Archive Assembly:** Completed exhaustive 31-document forensic archive and knowledge transfer package.\n