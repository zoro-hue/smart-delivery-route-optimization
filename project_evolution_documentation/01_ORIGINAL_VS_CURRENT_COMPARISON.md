# 01 — ORIGINAL VS CURRENT PROJECT ARCHITECTURE & IMPLEMENTATION COMPARISON

**Project:** ROUTE/IQ — Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing  
**Institution:** SRM University-AP, Department of Computer Science and Engineering  
**Authors:** J. Jayanth, B. Kaivalya, P. Shyam Sai  
**Faculty Supervisor:** Dr. Vishnu Prasad Verma (`vishnu.v@srmap.edu.in`)  
**Git Baseline Commit (`main`):** `a8eb849`  
**Current Research Branch:** `research/journal-readiness` (Commit: `960dfdb`)  
**Target Journal:** *IEEE Transactions on Quantum Engineering*  

---

## 1. Executive Summary

This document presents an exhaustive, source-code-verified audit comparing the original implementation of **ROUTE/IQ** (as preserved at commit `a8eb849` on branch `main`) with the current research-ready system (at commit `960dfdb` on branch `research/journal-readiness`).

The project evolved from an educational web prototype with separate, disconnected components into a mathematically rigorous, dual-pillar hybrid optimization architecture. The table below highlights the foundational transition:

| Dimension | Original Implementation (`a8eb849`) | Current Implementation (`960dfdb`) |
| :--- | :--- | :--- |
| **Primary Paradigm** | Educational web application with classical solvers and a toy monolithic QUBO model. | Mathematically formalized **Dual-Pillar Architecture** (Apache Spark 4.2.0 + QAOA on Qiskit Aer). |
| **Big Data Role** | Offline administrative ETL script (`bigdata_pipeline.py`, `local[1]`) writing Parquet files; **not** used during routing. | **Active runtime preprocessor** (`SparkRoutingPreprocessor`, `local[*]`) computing BPR volume-delay impedance, polar sweep partitioning up to 50k orders, and generating quantum payloads. |
| **Quantum Role** | Monolithic $O(n^2 \cdot K)$ QUBO in `quantum_solver.py` with soft penalty terms, failing for $n > 8$ customers. | Resource-bounded micro-cluster optimization ($m \le 4$, up to 16 qubits) with asymmetric TSP Ising mapping, particle-conserving $XY$ mixers, and binary slack capacity. |
| **Integration Layer** | Independent solvers called directly via if-else blocks; no hybrid quantum-classical coupling. | **Quantum-Guided Adaptive Reconstruction (QGAR)** with quality-aware sampling, planar crossing regularization, and route certification guardrails. |
| **Guarantees** | No mathematical guarantees; quantum bitstring failures silently triggered classical fallbacks. | **End-to-End Route Certification Guardrail** guaranteeing monotonic non-degradation ($C(R_{\text{QGAR}}) \le C(R_{\text{spatial}}) + 10^{-4}\text{ km}$) by construction. |
| **Empirical Rigor** | Ad-hoc single-instance runs in UI without statistical significance or ablation testing. | 20 paired benchmark trials, bootstrap 95% CIs, Wilcoxon signed-rank tests ($p < 0.001$), Benjamini-Hochberg FDR adjustments, and subproblem ablations. |

---

## 2. Detailed Dimension-by-Dimension Comparison

### 2.1 Project Objectives
- **Original (`a8eb849`):** Provide an interactive dashboard demonstrating route optimization on NYC streets using multiple independent solvers (Google OR-Tools, Clarke-Wright, 2-opt, QIGA, and a small QAOA demo).
- **Current (`960dfdb`):** Establish a scientifically validated, reproducible research architecture demonstrating how Big Data processing (Apache Spark) and Quantum Optimization (QAOA) collaboratively solve large-scale vehicle routing problems within realistic NISQ hardware constraints.

### 2.2 Computational Architecture
- **Original (`a8eb849`):**
  - Monolithic backend where `optimization.py` orchestrated routing by directly passing distance matrices to isolated solver classes (`classical_solver.py`, `quantum_solver.py`, `qiga_solver.py`).
  - Big data was confined to an auxiliary route (`/api/bigdata/run`) that ran PySpark offline as an administrative batch ETL job to convert raw CSVs into Parquet files.
  - When a user clicked "Run Optimization", Apache Spark was completely dormant.
- **Current (`960dfdb`):**
  - **Pillar 1 (Big Data):** `SparkRoutingPreprocessor` executes actively at runtime during the routing pipeline. It accepts raw delivery orders, maps them onto a 54,000-node road network, applies Bureau of Public Roads (BPR) impedance formulas based on NYC DOT traffic volumes, partitions customers using capacity-constrained polar sweep partitioning in $O(N \log N)$ distributed runtime, and packages micro-clusters for quantum evaluation.
  - **Pillar 2 (Quantum):** `QAOASubproblemOptimizer` accepts Spark payloads, maps each micro-cluster ($m \le 4$) to an Ising asymmetric TSP Hamiltonian, applies $XY$ particle-conserving mixers (`XXPlusYYGate`), optimizes variational parameters using COBYLA, executes 1,024 shots on Qiskit Aer, decodes measurement bitstrings, and enforces feasibility via Hungarian projection.
  - **Bridge (QGAR):** `QuantumGuidedAdaptiveRouter` evaluates candidate energy distributions, applies planar crossing regularizers, adaptively reconstructs the full fleet route, and validates against the spatial baseline via the Route Certification Guardrail.

### 2.3 Frontend & User Interface
- **Original (`a8eb849`):**
  - React 19, Vite, TypeScript, Tailwind CSS, Leaflet maps.
  - Pages included `OverviewDashboard.tsx`, `PlanWorkspace.tsx`, `ResultsView.tsx`, `ComparisonView.tsx`, `DatasetManagement.tsx`, `TrafficView.tsx`, `DeliveryMapView.tsx`.
  - UI allowed configuring vehicle capacity, algorithm selection, traffic/weather scenario, and viewing route polylines.
- **Current (`960dfdb`):**
  - Preserved the full React 19 + TypeScript frontend.
  - Fixed map visualization issues (glowing 'D' depot marker, aligned stop numbers 1–18 with Plan workspace).
  - Maintained complete backward compatibility with all frontend API contracts.

### 2.4 Data Processing Pipeline
- **Original (`a8eb849`):**
  - File: `backend/app/services/data_processor.py`.
  - Used Pandas and NumPy for in-memory coordinate calculations and Haversine distances.
  - Traffic and weather adjustments were applied as scalar multipliers (e.g., `traffic_factor = 1.3` for moderate traffic, `weather_factor = 1.2` for rain).
  - Parquet datasets were loaded via PyArrow without active Spark execution.
- **Current (`960dfdb`):**
  - File: `backend/app/services/spark_routing_preprocessor.py`.
  - Genuine Apache Spark 4.2.0 DataFrame transformations with Catalyst optimizer and Window functions.
  - Ingests delivery orders, joins with NYC DOT traffic volume datasets (hourly volume counts across 54k road segments), and computes calibrated link travel times using the BPR formula.
  - Dynamically computes polar angles relative to the depot, calculates running cumulative demand via Spark Window functions, and partitions orders into capacity-compliant clusters.

### 2.5 Road Network Handling
- **Original (`a8eb849`):**
  - File: `backend/app/services/road_network_service.py`.
  - Loaded NYC 5-Borough road network from an OSM XML file (`manhattan_osm.xml` / `nyc_boroughs.xml`) into a NetworkX graph (~54k nodes).
  - Computed shortest paths using NetworkX Dijkstra. Snapped customer GPS coordinates to nearest road nodes using KD-Tree.
  - Scaled edge weights by scalar scenario multipliers.
- **Current (`960dfdb`):**
  - Preserved the KD-Tree coordinate snapping and NetworkX Dijkstra routing engine for true road-network distance matrices.
  - Replaced crude scalar scenario multipliers with edge-level BPR volume-delay impedance calculations ($\tau = \tau_0 [1 + \alpha (V/C)^\beta]$), linking physical road capacity and empirical DOT volume data to traversal time.

### 2.6 Classical Optimization Algorithms
- **Original (`a8eb849`):**
  - File: `backend/app/services/optimization/classical_solver.py`.
  - Google OR-Tools Guided Local Search (GLS).
  - Clarke-Wright Savings heuristic.
  - 2-opt local search heuristic.
  - Used as primary production solvers.
- **Current (`960dfdb`):**
  - Classical solvers retained in full and repurposed as rigorous, standardized **comparative baselines** and **supporting components**.
  - OR-Tools GLS provides the classical state-of-the-art upper bound.
  - Clarke-Wright + 2-opt provides the standard classical heuristic baseline.
  - Classical Hungarian algorithm acts as a deterministic feasibility projection mechanism when quantum measurement bitstrings violate permutation constraints.

### 2.7 Quantum Optimization & QAOA Implementation
- **Original (`a8eb849`):**
  - File: `backend/app/services/optimization/quantum_solver.py`.
  - Formulated full VRP as a monolithic QUBO with $x_{i,k} \in \{0,1\}$ (assignment) and $y_{i,j,k} \in \{0,1\}$ (sequencing).
  - Problem size grew as $O(n^2 \cdot K)$ binary variables. A 10-customer, 3-vehicle problem required over 100 qubits—far exceeding NISQ simulation limits.
  - Used quadratic penalty terms for one-hot constraints ($P \sum (\sum x - 1)^2$). Penalty values dominated the cost matrix, causing QAOA to sample invalid bitstrings almost 100% of the time.
  - Included a mock manual fallback (`_run_manual_qaoa`) that randomly generated tours when Qiskit was unavailable or circuits failed.
- **Current (`960dfdb`):**
  - File: `backend/app/services/optimization/qaoa_subproblem_optimizer.py`.
  - Decomposes the routing problem into resource-bounded subproblems:
    - **Macro-Assignment QUBO:** Formulated with binary slack variables $\sum 2^b s_{k,b}$ to strictly enforce vehicle capacity without heuristic penalty tuning.
    - **Micro-Sequencing Ising Hamiltonian:** Formulates micro-clusters of $m \le 4$ stops (up to 16 logical qubits) as an Asymmetric TSP.
  - Replaced standard transverse-field $X$ mixer with **particle-conserving $XY$ mixers** (`XXPlusYYGate`), restricting quantum evolution to the valid permutation subspace $\sum_{p} x_{i,p} = 1$.
  - Executed on Qiskit Aer (`AerSimulator`) with 1,024 shots and COBYLA parameter optimization (25 iterations).
  - Hungarian assignment algorithm used as a deterministic projection to guarantee permutation feasibility.
  - Removed all mock random fallbacks; telemetry captures raw bitstring frequency distributions and energy profiles.

### 2.8 Benchmarking and Validation Methodology
- **Original (`a8eb849`):**
  - Ad-hoc single runs triggered manually via frontend "Compare" tab.
  - No statistical replication, no confidence intervals, no hypothesis testing.
  - Results varied depending on arbitrary random seeds.
- **Current (`960dfdb`):**
  - Rigorous scientific benchmarking suite (`backend/scripts/`):
    - `run_phase_i_qgar_benchmark.py`: 20 paired trials across problem sizes $N=25, 50, 100$.
    - `run_qaoa_subproblem_ablation.py`: Exact quantum circuit depth, gate count, and approximation ratio telemetry for $m=3$ (9 qubits) and $m=4$ (16 qubits).
    - `run_bigdata_scaling_audit.py`: Spark batch scaling from $N=100$ to $N=50,000$ delivery orders.
    - `run_phase_k_quantum_attribution.py`: Quantum attribution verification proving QAOA's objective contribution over a no-QAOA ablation.
    - `run_phase_k_adversarial_audit.py`: Worst-case scenario verification testing edge cases.
  - Full statistical rigor: paired Wilcoxon signed-rank tests, bootstrap 95% confidence intervals, rank-biserial effect sizes ($r_B$), and Benjamini-Hochberg False Discovery Rate (FDR) adjustments.

---

## 3. Comprehensive Modification Matrix

The following table itemizes every major component change between `a8eb849` and `960dfdb`:

| Component / Subsystem | Original State (`a8eb849`) | Modified State (`960dfdb`) | Rationale for Modification | Implementing Files | Functional / Measurable Benefit | Remaining Limitations |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Spark Preprocessor** | Offline batch ETL in `bigdata_pipeline.py` (`local[1]`), never called during routing. | Active runtime preprocessor `SparkRoutingPreprocessor` (`local[*]`). | Spark must be an active computational pillar during routing, not just an offline script. | `backend/app/services/spark_routing_preprocessor.py` | Scales up to 50,000 orders in 22.04s; outputs capacity-compliant clusters in $O(N \log N)$. | Executes on single workstation via `local[*]`; multi-node cluster (`spark://`) not yet deployed. |
| **Traffic Impedance Model** | Fixed scalar multipliers (e.g. 1.3x) applied globally to all road edges. | Edge-specific BPR volume-delay impedance: $\tau = \tau_0 [1 + 0.15 (V/C)^4]$. | Incorporates empirical NYC DOT traffic counts and road capacity into edge traversal costs. | `spark_routing_preprocessor.py` | Accurate physical travel time estimates across 54,000 road segments. | Uses hourly volume data rather than real-time GPS probe speed telemetry. |
| **QAOA Subproblem Formulation** | Monolithic QUBO with $O(n^2 \cdot K)$ variables; fails for $n > 8$. | Bounded micro-cluster formulation with $m \le 4$ stops (up to 16 qubits). | Conforms problem dimensions to current NISQ simulation capabilities. | `backend/app/services/optimization/qaoa_subproblem_optimizer.py` | Circuit depth bounded to 15 ($m=3$) and 24 ($m=4$); runs reliably in Qiskit Aer. | Micro-clusters bounded to $m \le 4$; classical solvers can easily enumerate small $m$. |
| **Quantum Mixer Circuit** | Transverse-field $X$ mixer ($\sum X_i$), allowing search space to drift into invalid states. | Particle-conserving $XY$ mixer using `XXPlusYYGate`. | Constrains quantum evolution to the valid one-hot permutation subspace. | `qaoa_subproblem_optimizer.py` | Eliminates Hamming-weight violations; focuses circuit on permutation ordering. | Circuit compilation overhead; gate count increases with subproblem size. |
| **Capacity Constraint Encoding** | Soft penalty terms added to cost function, causing constraint violations. | Exact binary slack capacity encoding: $\sum 2^b s_{k,b}$. | Soft penalties either dominate the cost function or allow capacity overfilling. | `qaoa_subproblem_optimizer.py` | Guaranteed binary representation of vehicle capacity constraints. | Requires additional slack qubits for macro-assignment. |
| **Quantum-Classical Bridge** | No bridge; independent classical or quantum solvers called in isolation. | Quantum-Guided Adaptive Reconstruction (QGAR). | Quantum subproblem solutions must inform the overall multi-vehicle fleet routing. | `backend/app/services/optimization/qgar_pipeline.py` | Leverages QAOA candidate tours to guide route assembly; $-4.10\%$ distance vs Phase H. | Heuristic reconstruction; does not guarantee global optimality across vehicles. |
| **Candidate Selection** | Highest-count bitstring selected regardless of feasibility or energy. | Quality-Aware Candidate Selection based on empirical energy spectrum. | Most frequent bitstring is not always the lowest energy state in noisy/shallow circuits. | `qgar_pipeline.py` | Filters candidate tours by true cost Hamiltonian energy rather than raw frequency alone. | Dependent on sample size (1,024 shots). |
| **Geometric Regularizer** | None. | Planar Crossing Regularizer based on 2-opt edge crossing detection. | Removes self-intersecting loops from reconstructed tours. | `qgar_pipeline.py` | Eliminates topological crossings in 2D Euclidean space. | In asymmetric BPR graph networks, crossing removal can occasionally cause detours (e.g. Trial 0). |
| **Route Certification Guardrail** | None; worst-case quantum routes accepted or crashed silently. | End-to-End Route Certification Guardrail ($C(R_{\text{QGAR}}) \le C(R_{\text{spatial}}) + 10^{-4}$). | Guarantees that quantum-guided solutions never degrade below deterministic classical baselines. | `qgar_pipeline.py`, `hybrid_quantum_pipeline.py` | **Monotonic Non-Degradation Guarantee** proven by construction; 14 wins, 0 losses, 6 ties vs baseline. | If QAOA fails to find a better tour, the system simply certifies the spatial baseline. |
| **Benchmarking Suite** | None; ad-hoc single-instance runs in web browser. | Automated benchmark scripts with paired statistical analysis and FDR correction. | Journal-quality research requires reproducible, statistically verified evidence. | `backend/scripts/run_phase_i_qgar_benchmark.py`, etc. | Statistically significant results ($p = 0.000491$, $r_B = +1.000$ vs spatial baseline). | Benchmarks run in simulated environment rather than real-world delivery fleet. |

---

## 4. Architectural Summary

The evolution from `a8eb849` to `960dfdb` represents a complete transformation from an **exploratory prototype** to a **scientifically grounded hybrid quantum-classical system**:

1. **Big Data:** Shifted from an offline Parquet converter to an active, in-memory Spark preprocessor handling volume-delay impedance and spatial partitioning for tens of thousands of orders.
2. **Quantum Computing:** Abandoned intractable monolithic QUBO formulations in favor of resource-bounded micro-cluster optimization using particle-conserving $XY$ mixers and exact binary slack variables.
3. **Hybrid Integration:** Replaced isolated solver execution with QGAR, coupling quantum subproblem solutions into global fleet routing with quality-aware sampling, geometric regularization, and a certified non-degradation guardrail.
4. **Research Integrity:** Replaced unsubstantiated quantum supremacy claims with honest, reproducible NISQ-scale evaluations, transparently benchmarking against classical state-of-the-art tools (OR-Tools GLS).
