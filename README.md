# ROUTE/IQ
### Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing

> **Research Program:** Undergraduate Research Opportunity Program (UROP)  
> **Institution:** Department of Computer Science and Engineering, SRM University-AP, Amaravati, Andhra Pradesh, India  
> **Faculty Supervisor:** Dr. Vishnu Prasad Verma  
> **Student Researchers:** J. Jayanth, B. Kaivalya, P. Shyam Sai  
> **Primary Literature Survey Reference:** `LITERATURE_SURVEY (4).pdf` (*A Literature Survey of Hybrid Big Data and Quantum Computing for Smart Delivery Route Optimization*)

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.14-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Apache Spark](https://img.shields.io/badge/Apache%20Spark-4.2.0-E25A1C?style=for-the-badge&logo=apachespark&logoColor=white)](https://spark.apache.org/)
[![Java](https://img.shields.io/badge/OpenJDK-17.0.20.1-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white)](https://adoptium.net/)
[![Qiskit](https://img.shields.io/badge/Qiskit-2.4.1-6929C4?style=for-the-badge&logo=qiskit&logoColor=white)](https://qiskit.org/)
[![React](https://img.shields.io/badge/React-18.3-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-5.4-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev/)
[![Leaflet](https://img.shields.io/badge/Leaflet-1.9.4-199900?style=for-the-badge&logo=leaflet&logoColor=white)](https://leafletjs.com/)

---

## 📌 Project Overview

### The Problem We Are Addressing
Urban last-mile delivery operations in densely populated metropolitan areas (such as New York City) encounter compounding computational, operational, and physical bottlenecks:
* **Data Scale and Ingestion Friction:** Modern logistics dispatch systems must process thousands of delivery orders alongside heterogeneous fleet specifications, municipal depot facilities, and municipal traffic observations containing missing records, inconsistent naming, and unstructured fields.
* **Dynamic Traffic Congestion & Weather Volatility:** Rush-hour arterial congestion and severe weather events (heavy rain, snowfall) drastically impair vehicular travel times. Traditional dispatch models relying on static speed assumptions produce unrealistic delivery ETAs and inefficient vehicle schedules.
* **Failure of Euclidean Distance Approximations:** Straight-line or Manhattan grid distance formulas fail to represent actual street travel, ignoring one-way road networks, median dividers, turn restrictions, bridge crossings, and geographic water boundaries.
* **Combinatorial Complexity of the CVRP:** The Capacitated Vehicle Routing Problem (CVRP) is NP-hard ($O(n!)$ search space). As delivery stops increase, exact classical algorithms experience combinatorial explosion, while emerging quantum optimization methods face strict physical qubit and memory constraints.

### What Solution We Developed
**ROUTE/IQ** is an experimental research prototype engineered to investigate how Big Data engineering and quantum / quantum-inspired optimization can be coupled under authentic urban road network topology:
1. **Big Data Processing (Apache Spark 4.2.0):** An offline batch ETL engine cleans, deduplicates, and aggregates over **114,000 New York City records** (TLC taxi fleet, DOT traffic volumes, NOAA weather logs, IDNYC municipal depots, customer orders) into curated, compressed Parquet tables.
2. **Road-Network-Aware Cost Modeling:** Routes operate over an indexed OpenStreetMap graph of **54,128 nodes and 142,123 street edges** (Manhattan and the Bronx). GPS stops are snapped to real street intersections via a spatial KD-Tree, ensuring dual-layer 5-borough geographic validation.
3. **Classical Optimization Baselines:** Implements production-grade classical solvers for rigorous benchmarking: **Google OR-Tools** (Guided Local Search), **Clarke–Wright Savings**, and **2-opt** local search.
4. **Gate-Model Quantum Optimization (QAOA):** Formulates routing instances as Quadratic Unconstrained Binary Optimization (QUBO) and Ising Hamiltonians, solved via a parameterized 2-layer Quantum Approximate Optimization Algorithm ansatz evaluated with **Qiskit 2.4.1**'s `StatevectorSampler`.
5. **Quantum-Inspired Genetic Algorithm (QIGA):** Implements qubit probability-amplitude representation $[\cos\theta, \sin\theta]^T$ and dynamic quantum rotation gates on classical CPUs, providing an evolutionary bridge for medium-scale routing instances without quantum hardware constraints.
6. **Interactive Scenario Simulation:** A React 18 + TypeScript Leaflet frontend offering real-time weather and traffic scenario sliders, multi-solver comparison scorecards, and SQLite experiment run persistence.

> **Operational Distinction:** Big Data batch ETL prepares and enriches the cost matrix inputs offline; solvers execute on request to determine optimal stop sequences across that enriched matrix. Algorithms do not all execute simultaneously unless the user activates the multi-solver "Compare" suite.

### Practical Logistics Relevance
Systems built on this architecture offer potential operational benefits for urban logistics:
* **Scenario-Calibrated Dispatch:** Fleet dispatchers can pre-evaluate delivery costs under severe rain or rush-hour conditions before deploying vehicles.
* **Fair Algorithmic Benchmarking:** Logistics researchers can directly evaluate the solution quality, computational latency, and memory footprint of emerging quantum formulations against battle-tested classical solvers on identical problem instances.
* **Turn-by-Turn Road Feasibility:** Drivers receive routes following actual one-way street networks and legal turn geometries rather than impossible straight-line jumps across buildings or waterways.

> **Research Prototype Disclosure:** ROUTE/IQ is an academic research prototype developed under UROP. It is not currently deployed in production commercial logistics operations, and potential cost, fuel, or emissions reductions represent analytical simulation projections rather than measured commercial savings.

### Research Objective
The objective of this project is to evaluate the viability, algorithmic trade-offs, and scaling boundaries of combining Big Data cost enrichment with quantum (QAOA) and quantum-inspired (QIGA) solvers under real-world municipal road constraints.

---

## 🔬 Research Gaps and Project Contributions

The research framework of ROUTE/IQ is grounded in our literature survey, `LITERATURE_SURVEY (4).pdf` (*A Literature Survey of Hybrid Big Data and Quantum Computing for Smart Delivery Route Optimization*, SRM University-AP), which systematically reviews 20 foundational papers spanning Big Data, Logistics, Route Optimization, Quantum Computing, and Dynamic Transportation.

### Literature Observations vs. ROUTE/IQ Implementation

| Research Observation from Our Survey | Challenge or Gap Identified (Section 20 of Survey) | How ROUTE/IQ Addresses It | Evidence and Current Limitation |
| :--- | :--- | :--- | :--- |
| **Scalability in Combinatorial Routing** (Azad et al. [7], Wang et al. [10]) | VRP search space grows exponentially ($O(n!)$); gate-based quantum routing has been evaluated only on minimal problem sizes ($N \le 4$) due to qubit availability. | Implements a multi-paradigm suite: Google OR-Tools for large instances, QIGA for intermediate instances (up to 20 stops), and QAOA for 3-4 stop NISQ formulation testing. | Solves 4-node instances in 0.62s via QAOA simulation; oversized instances ($>20$ qubits) are blocked by an automated guard to prevent memory exhaustion. |
| **Dynamic Transportation & Environmental Data** (Zheng [2], Niyazi [16], Yuan [20]) | Static distance matrices fail during dynamic traffic congestion, rain, and snow; route costs must incorporate environmental conditions. | PySpark cleans 42,756 DOT traffic counts and 59,760 NOAA weather records to compute hourly speed profiles and weather friction multipliers ($\gamma = 1.0\times$ to $1.92\times$). | Currently implemented as offline batch Parquet ETL and user-driven scenario sliders, rather than automated real-time Kafka streaming. |
| **Big Data + Quantum Computing Integration** (Chen [1], Zhu [3], El Azzaoui [11]) | Literature treats Big Data analytics and quantum computing as isolated silos; no end-to-end framework bridges raw municipal data with quantum routing circuits. | Implements cost-matrix enrichment: Big Data Parquet metrics dynamically inflate edge traversal costs on a 54,128-node road graph before matrix input to QAOA/QIGA. | Demonstrates functional coupling on classical infrastructure; does not stream live data directly into physical quantum co-processors. |
| **Quantum Hardware & NISQ Constraints** (Sarkar et al. [9], Azad et al. [7]) | Physical quantum processors suffer from limited qubit counts, gate noise, and brief coherence times, restricting direct deployment. | Discloses and utilizes classical CPU statevector simulation (Qiskit 2.4.1 `StatevectorSampler`), accompanied by a classical Quantum-Inspired Genetic Algorithm (QIGA). | QAOA simulation is strictly limited by CPU RAM ($O(2^N)$); does not execute on physical IBM Quantum or D-Wave QPUs. |
| **Dynamic Scenario Re-Optimization** (Issaoui [4], Hussain [6], Jagarlamudi [18]) | Delivery operations require rapid cost re-calculation and route re-planning when urban conditions change. | Interactive frontend enables dispatchers to adjust traffic congestion and weather factors, re-triggering solvers in sub-second time. | Re-optimization is currently user-initiated via scenario controls; does not autonomously ingest telematics from moving vehicles. |

### Our Contributions
1. **End-to-End Hybrid Architecture:** Coupled an Apache Spark 4.2.0 batch data pipeline with a multi-paradigm optimization hub, bridging raw municipal open datasets with quantum circuit formulation.
2. **Transparent Quantum Simulation Benchmarking:** Rigorously formulated CVRP into QUBO and Ising Hamiltonians evaluated via Qiskit 2.4.1, openly reporting classical CPU simulation limits ($N \le 20$ qubits) without exaggerated claims of quantum advantage.
3. **Quantum-Inspired Bridge (QIGA):** Deployed an evolutionary solver using probability-amplitude vectors and rotation gates on classical CPU, solving medium-scale delivery instances where gate simulation is intractable.
4. **Authentic Road-Network Grounding:** Grounded all routing upon a real 54,128-node OpenStreetMap street graph with KD-Tree snapping and dual-layer 5-borough boundary validation, preventing invalid water or out-of-boundary paths.

---

## 📑 Table of Contents

- [📌 Project Overview](#-project-overview)
- [🔬 Research Gaps and Project Contributions](#-research-gaps-and-project-contributions)
- [1. Visual Showcase](#1-visual-showcase)
- [2. System Architecture](#2-system-architecture)
- [3. Big Data Pipeline (Apache Spark 4.2.0)](#3-big-data-pipeline-apache-spark-420)
- [4. Quantum Computing & QIGA Mechanics](#4-quantum-computing--qiga-mechanics)
- [5. Routing Solvers & Algorithmic Comparison](#5-routing-solvers--algorithmic-comparison)
- [6. Geographic Validation & Road-Network Snapping](#6-geographic-validation--road-network-snapping)
- [7. End-to-End Execution Trace](#7-end-to-end-execution-trace)
- [8. Installation & Quickstart Guide](#8-installation--quickstart-guide)
- [9. API Reference](#9-api-reference)
- [10. Project Directory Structure](#10-project-directory-structure)
- [11. Academic Background & Citations](#11-academic-background--citations)
- [12. License & Acknowledgments](#12-license--acknowledgments)

---

## 1. Visual Showcase

| Route Planning Workspace & Active Map | Live Multi-Solver Comparison & Scorecard |
| :---: | :---: |
| ![Planning Workspace](docs/assets/screenshots/02_route_planning_workspace.png) | ![Completed Comparison](docs/assets/screenshots/03_completed_route_comparison.png) |
| *Interactive Leaflet map showing stop snapping, traffic/weather controls, and algorithm selector.* | *Side-by-side scorecard comparing distance, compute time, and carbon emissions across all 6 solvers.* |

| Executive Analytics Overview | Big Data Curated Datasets & ETL Status |
| :---: | :---: |
| ![Dashboard Overview](docs/assets/screenshots/01_dashboard.png) | ![Big Data Pipeline](docs/assets/screenshots/04_big_data_pipeline.png) |
| *Operational fleet telemetry, delivery volume distributions, and road network topology metrics.* | *Apache Spark batch ETL status, Parquet file artifacts, schemas, and missing value audits.* |

| Persistent Experiments & Benchmarking History |
| :---: |
| ![Experiments History](docs/assets/screenshots/05_experiments_benchmark.png) |
| *Automated trial persistence recording runtime, solver type, vehicles, and distance metrics to SQLite.* |

---

## 2. System Architecture

ROUTE/IQ decouples offline/startup data preparation from real-time routing optimization:

```mermaid
flowchart TD
    subgraph Data_Layer ["Phase 1: Big Data Batch ETL (Apache Spark 4.2.0 + Java 17)"]
        Raw_CSV["Raw NYC Datasets (114k+ records)<br/>• Customers (1,898)<br/>• Fleet (10,000)<br/>• Depots (18)<br/>• DOT Traffic (42,756)<br/>• Weather (59,760)"]
        Spark_Engine["PySpark Session (local[1])<br/>• Schema Normalization & Dedup<br/>• Traffic Roadway Congestion Aggregation<br/>• Weather Friction Indexing"]
        Curated_Parquet["Curated Parquet Outputs (/data/processed/spark_output/)<br/>• customers_curated.parquet (81.8 KB)<br/>• vehicles_curated.parquet (588.5 KB)<br/>• locations_curated.parquet (14.2 KB)<br/>• traffic_speeds_curated.parquet (24.5 KB)<br/>• weather_curated.parquet (2.8 KB)"]
        Raw_CSV --> Spark_Engine --> Curated_Parquet
    end

    subgraph Service_Layer ["Phase 2: FastAPI Backend Engine (Port 8000)"]
        API_Gateway["API Endpoint Gateway: POST /api/optimization/run"]
        Geo_Check{"Geographic Validator<br/>validate_nyc_coordinate()"}
        Road_Engine["RoadNetworkService (NetworkX + KD-Tree)<br/>• 54,128 Nodes / 142,123 Edges (newyork.graphml)<br/>• Spatial KD-Tree Stop Snapping<br/>• Traffic/Weather Cost Inflation (1.92x)"]
        
        Curated_Parquet -.->|Loaded on Startup| Road_Engine
        API_Gateway --> Geo_Check
        Geo_Check -->|Invalid: Nassau/NJ/Water| Err_Resp["HTTP 400 Out-of-Bounds Error"]
        Geo_Check -->|Valid NYC Stop| Road_Engine
    end

    subgraph Solver_Hub ["Phase 3: Multi-Paradigm Optimization Hub"]
        Road_Engine --> Solver_Dispatch{"Algorithm Selector"}
        Solver_Dispatch -->|Exact / Heuristic| Classical_Solvers["ClassicalVRPSolver<br/>• Google OR-Tools (Guided Local Search)<br/>• Clarke-Wright Savings Heuristic<br/>• 2-opt Iterative Edge Exchange"]
        Solver_Dispatch -->|Baseline| Graph_Solvers["Shortest-Path Trees<br/>• Dijkstra Graph Traversal<br/>• A* Heuristic Search"]
        Solver_Dispatch -->|Quantum-Inspired| QIGA_Solver["QIGASolver (Classical CPU)<br/>• Q-bit Representation [cos θ, sin θ]^T<br/>• Dynamic Rotation Gate Updates U(Δθ)"]
        Solver_Dispatch -->|Gate-Based QC| QAOA_Solver["QuantumVRPSolver (Qiskit 2.4.1)<br/>• Binary Position Mapping (x_{i,p})<br/>• QUBO & Ising Cost/Mixer Hamiltonians<br/>• StatevectorSampler + COBYLA (10 iter)"]
    end

    subgraph Presentation_Layer ["Phase 4: Client Presentation & Mapping (Port 5173)"]
        Geom_Recon["RoadNetworkService.reconstruct_route_geometry()<br/>Extracts authentic WKT street curvature along directed edges"]
        Frontend_UI["React + TypeScript UI<br/>• Interactive Leaflet Map with 90° Intersection Turns<br/>• Multi-Solver Comparison Scorecards<br/>• SQLite Experiment Persistence (sdro.db)"]
        
        Classical_Solvers --> Geom_Recon
        Graph_Solvers --> Geom_Recon
        QIGA_Solver --> Geom_Recon
        QAOA_Solver --> Geom_Recon
        Geom_Recon --> Frontend_UI
    end
```

---

## 3. Big Data Pipeline (Apache Spark 4.2.0)

Urban delivery optimization cannot rely on clean, toy distance matrices. Real cities present messy, multi-source, high-volume sensor streams. ROUTE/IQ implements a dedicated PySpark batch processing pipeline to ingest and curate raw municipal data into analytics-ready columnar Parquet tables.

```mermaid
flowchart LR
    A["Raw Data Ingestion<br/>• customers.csv (1,898)<br/>• vehicles.csv (10,000)<br/>• locations.csv (18)<br/>• traffic_nyc.csv (42,756)<br/>• weather_nyc.csv (59,760)"] --> B["PySpark ETL Service<br/>(bigdata_pipeline.py)"]
    B --> C["Transformation & Cleaning<br/>• Deduplicate on order_id<br/>• Median demand imputation<br/>• TLC active license filters<br/>• Roadway name standardization<br/>• Hourly volume aggregations"]
    C --> D["Curated Columnar Parquet<br/>• Compression: Snappy<br/>• Total footprint: ~712 KB<br/>• ~60% size reduction"]
    D --> E["DataProcessor Memory Cache<br/>• Sub-millisecond route ingestion<br/>• Dynamic cost modulation"]
```

### Verified Dataset Inventory

| Dataset Category | Source File & Characteristics | Spark Transformation Applied | Curated Parquet Artifact | Size |
| :--- | :--- | :--- | :--- | :---: |
| **Customer Orders** | `data/raw/customers.csv` (1,898 food orders) | Deduplicates IDs, parses cuisine types, imputes missing demand with median, computes delivery durations. | `customers_curated.parquet` | 81.8 KB |
| **Vehicle Fleet** | `data/raw/vehicles.csv` (10,000 TLC vehicles) | Filters active licensed vehicles, parses VIN/year, assigns capacity classes and cost/km rates. | `vehicles_curated.parquet` | 588.5 KB |
| **Depot Facilities** | `data/raw/locations.csv` (18 municipal IDNYC hubs) | Validates borough coordinates, filters valid dispatch yards, standardizes operating hours. | `locations_curated.parquet` | 14.2 KB |
| **Traffic Counts** | `data/raw/traffic_nyc.csv` (42,756 DOT hourly records) | Cleans street names (e.g. ordinals, expressway acronyms), groups by roadway, aggregates mean and peak volume. | `traffic_speeds_curated.parquet` (897 roadways) | 24.5 KB |
| **Weather Logs** | `data/raw/weather_nyc.csv` (59,760 hourly observations) | Aggregates 2016–2022 observations into 4 distinct condition groups; computes mean precipitation. | `weather_curated.parquet` (4 condition groups) | 2.8 KB |
| **Road Network** | `data/raw/newyork.graphml` (54,128 nodes, 142,123 edges) | Extracts largest strongly connected component (53,769 nodes); indexes coordinates into SciPy cKDTree. | `road_graph_newyork.pickle` | 68.4 MB |

### Dynamic Cost Modulation Formula
Rather than treating distance as a static Euclidean quantity, edge travel costs are dynamically inflated based on current environmental scenarios:

$$\text{Generalized Cost} = D_{\text{physical}} \times \gamma_{\text{traffic}} \times \gamma_{\text{weather}}$$

* **Baseline Conditions (Normal + Clear):** $\gamma_{\text{traffic}} = 1.0$, $\gamma_{\text{weather}} = 1.0 \implies \text{Multiplier} = 1.00\times$
* **Adverse Conditions (High Congestion + Rain):** $\gamma_{\text{traffic}} = 1.6$, $\gamma_{\text{weather}} = 1.2 \implies \text{Multiplier} = 1.92\times$
* **Empirical Verification:** A road edge measuring **15.72 m** under base conditions correctly scales to **30.19 m** ($15.72 \times 1.92$) when adverse parameters are selected.

---

## 4. Quantum Computing & QIGA Mechanics

### 1. Gate-Model QAOA (Qiskit 2.4.1)

QAOA is a variational hybrid quantum-classical algorithm designed for combinatorial optimization problems represented as an Ising spin glass.

```mermaid
flowchart TD
    A["Delivery Stops & Depot (N nodes)"] --> B["QUBO Formulation (binary x_{i,p})<br/>Minimize: Σ d_{ij} x_{i,p} x_{j,p+1}<br/>Penalties: A(Σ_p x_{i,p} - 1)^2 + B(Σ_i x_{i,p} - 1)^2"]
    B --> C["Ising Hamiltonian Mapping<br/>Substitution: x_k = (I - Z_k) / 2<br/>Yields Pauli-Z operator tensor products"]
    C --> D["Parameterized Quantum Circuit (Depth p=1)<br/>Initial state: |+⟩^{⊗N} = H^{⊗N} |0⟩^{⊗N}<br/>Applies e^{-i γ H_C} followed by e^{-i β H_M}"]
    D --> E["Qiskit 2.4.1 StatevectorSampler<br/>Computes energy expectation value ⟨ψ(γ,β)| H_C |ψ(γ,β)⟩"]
    E --> F["SciPy COBYLA Classical Optimizer<br/>Iteratively updates variational parameters (γ, β) [10 iterations]"]
    F -->|Converged| G["Final Measurement & Decoding<br/>Samples lowest-energy bitstring (e.g. 001010100)<br/>Decodes to permutation: Depot → Stop 1 → Stop 2 → Stop 3 → Depot"]
```

#### Empirical Execution Profile (4-Node Problem: 1 Depot, 3 Customers):
* **Binary Qubits Required:** 9 qubits (fixed origin depot at position 0).
* **Quantum Circuit Depth:** 37 gates.
* **Classical Optimizer:** COBYLA (10 iterations).
* **Sampled Energy (Ground State):** **-56.10**.
* **Simulated Fallback Flag:** `is_simulated_fallback: False` (genuine circuit simulation).
* **Execution Time:** **0.6228 seconds** on classical CPU.
* **Oversized Instance Guard:** Statevector simulation memory scales as $O(2^N)$. If an input requires $>20$ qubits (e.g. 6 stops = 36 qubits), ROUTE/IQ throws an immediate HTTP 400 error:  
  `"QAOA qubit requirement (36 qubits) exceeds local simulation threshold (20 qubits). Reduce stop count or select QIGA."`

---

### 2. Quantum-Inspired Genetic Algorithm (QIGA)

To overcome the exponential memory bottleneck of quantum statevector simulation on classical machines, ROUTE/IQ includes an independent **Quantum-Inspired Genetic Algorithm** (`qiga_solver.py`):

```mermaid
flowchart TD
    A["Initialize Q-bit Population<br/>Pop Size = 20, Max Gen = 50<br/>Set Phase Angles θ_j = π/4 (Equal Superposition)"] --> B["Sample Permutations<br/>Random r ~ U[0, 1) against |β_j|^2 = sin^2(θ_j)<br/>Construct Candidate Stop Permutations"]
    B --> C["Evaluate Objective & Route Feasibility<br/>Compute Total Road-Network Tour Cost D(P)<br/>Identify Best Chromosome P_best"]
    C --> D{"Stopping Criteria Met?<br/>Max Generations OR Convergence"}
    D -->|No| E["Apply Quantum Rotation Gate U(Δθ)<br/>Update Phase Angles θ_j Towards P_best<br/>Δθ = s(α, β) × f(fitness)"]
    E --> B
    D -->|Yes| F["Return Optimal Route Sequence & Metrics"]
```

1. **Q-Bit Probability Chromosomes:** Each gene is defined by probability amplitudes:
   $$q_j = \begin{bmatrix} \alpha_j \\ \beta_j \end{bmatrix} = \begin{bmatrix} \cos(\theta_j) \\ \sin(\theta_j) \end{bmatrix}, \quad |\alpha_j|^2 + |\beta_j|^2 = 1$$
2. **Measurement / Collapse:** Random numbers $r \sim U[0, 1)$ sample states against $|\beta_j|^2 = \sin^2(\theta_j)$, collapsing the superposition into a permutation of customer visits.
3. **Quantum Rotation Gate:** Rather than classical crossover or mutation, chromosome phase angles are rotated toward the best-known solution using rotation matrix $U(\Delta\theta)$:
   $$\begin{bmatrix} \alpha_j' \\ \beta_j' \end{bmatrix} = \begin{bmatrix} \cos(\Delta\theta_j) & -\sin(\Delta\theta_j) \\ \sin(\Delta\theta_j) & \cos(\Delta\theta_j) \end{bmatrix} \begin{bmatrix} \alpha_j \\ \beta_j \end{bmatrix}$$
4. **Performance:** Solves a 4-node problem in **0.0168 seconds** and a 10-node problem in **0.078 seconds** with 100% route feasibility.

---

## 5. Routing Solvers & Algorithmic Comparison

All 6 algorithms evaluate the identical road-network distance/cost matrix generated from OpenStreetMap graph topology:

| Algorithm Name | Category | Mathematical / Algorithmic Approach | 4-Node Distance | Compute Time | Strengths | Limitations |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| **Google OR-Tools** | Classical Exact/Local | Constraint programming + Guided Local Search | **8.0 km** | 0.042 s | Proven global optimality; handles capacity and delivery time windows. | Higher latency on micro-instances due to solver initialization overhead. |
| **Clarke–Wright** | Classical Heuristic | Savings calculation merging circular customer tours | **8.0 km** | 0.0001 s | Extremely fast ($O(N^2 \log N)$); excellent initial tour generation. | Greedy approach can get trapped in local optima on complex topologies. |
| **2-opt** | Classical Heuristic | Local search iteratively swapping non-adjacent edge pairs | **8.0 km** | 0.0001 s | Eliminates self-intersecting loops and doglegs quickly. | Requires a feasible initial tour; sensitive to initial vertex sequence. |
| **Dijkstra** | Classical Baseline | Single-source shortest path reachability tree | **8.0 km** | 0.0002 s | Guarantees shortest physical path between individual node pairs. | Not a combinatorial tour optimizer; serves as distance baseline. |
| **A\*** | Classical Baseline | Goal-directed heuristic search using Euclidean lower bounds | **8.0 km** | 0.0002 s | Faster point-to-point traversal than Dijkstra on large graphs. | Route order depends on greedy waypoint chaining. |
| **QIGA** | Quantum-Inspired | Evolutionary Q-bits with dynamic rotation gates $U(\Delta\theta)$ | **8.0 km** | 0.0168 s | High population diversity; rapid convergence without local minima traps. | Heuristic nature; runs on classical CPU rather than quantum hardware. |
| **QAOA (p=1)** | Gate-Model Quantum | Variational QUBO Hamiltonian minimization via Qiskit | **8.0 km** | 0.6228 s | Demonstrates gate-based formulation for future fault-tolerant QPUs. | Exponential memory ($O(2^N)$) limits local simulation to $\le 20$ qubits. |

---

## 6. Geographic Validation & Road-Network Snapping

To ensure realistic vehicle routing, ROUTE/IQ rejects arbitrary straight-line paths and restricts delivery operations to the authentic street network:

1. **5-Borough Dispatch Boundary:**  
   The underlying road network (`newyork.graphml`) covers **Manhattan, Brooklyn, Queens, The Bronx, and Staten Island** with longitudinal limits `[-74.2553, -73.7005]`.
   * Clicks in Nassau County (e.g. `[40.7322, -73.6340]`, ~6 km east of Queens) are intercepted by `validate_nyc_coordinate()` and return an informative message:
     ```
     Coordinate (40.7322, -73.6340) is in Nassau County / Long Island, outside the active NYC 5-Borough road network (Manhattan, Brooklyn, Queens, Bronx, Staten Island).
     ```
   * Clicks in open water (Hudson River, East River, Jamaica Bay) or across the state line in New Jersey are similarly rejected.
2. **Sub-100m Node Snapping:**  
   Valid street addresses are projected onto nearest road graph intersections using a SciPy KD-Tree:
   * Manhattan (Central Park West): **42.9 m**
   * Brooklyn (Crown Heights): **7.1 m**
   * Queens (Fresh Meadows): **21.8 m**
   * The Bronx (Pelham Parkway): **81.1 m**
   * Staten Island (Todt Hill): **286.6 m**
3. **Turn-by-Turn Geometry Reconstruction:**  
   After the optimization solver determines the stop sequence, `road_network_service.reconstruct_route_geometry()` extracts the full WKT polyline coordinates of every directed street edge traversed. Routes turn at **clean 90-degree street intersections** rather than cutting through city blocks.

---

## 7. End-to-End Execution Trace

```
[User Action in Browser]
  │ Click 'Run Optimization' or 'Compare (6 Solvers)'
  ▼
[frontend/src/pages/PlanWorkspace.tsx]
  │ handleRunOptimization() builds OptimizationRequest payload
  ▼
[HTTP POST /api/optimization/run]
  │ Handled by backend/app/api/routes/optimization.py:run_optimization()
  ▼
[backend/app/services/geo_validation.py]
  │ validate_nyc_coordinate() checks depot and customer coordinates
  │ ├── If out-of-bounds: throws HTTP 400 Bad Request
  │ └── If valid: proceeds
  ▼
[backend/app/services/data_processor.py]
  │ Fetches traffic and weather penalty multipliers from curated Parquet tables
  ▼
[backend/app/services/road_network_service.py]
  │ build_road_matrix() snaps locations to KD-Tree nodes
  │ Computes Dijkstra shortest path on 54,128-node graph; applies cost multiplier (1.92x)
  ▼
[Algorithm Execution Hub]
  │ ├── 'ortools': classical_solver.solve(algorithm='ortools')
  │ ├── 'clarke_wright': classical_solver.solve(algorithm='clarke_wright')
  │ ├── 'two_opt': classical_solver.solve(algorithm='two_opt')
  │ ├── 'qiga': qiga_solver.solve()
  │ └── 'qaoa': quantum_solver.solve() -> Qiskit StatevectorSampler
  ▼
[backend/app/services/road_network_service.py]
  │ reconstruct_route_geometry() chains directed edge WKT coordinates
  ▼
[HTTP 200 Response Payload]
  │ Returns GeoJSON polylines, stop sequences, distances, times, and emissions
  ▼
[frontend/src/components/Map/DeliveryMap.tsx]
  │ Renders street-accurate route layers, markers, and comparison scorecard
```

---

## 8. Installation & Quickstart Guide

### Prerequisites
* **Operating System:** Windows 10/11, macOS, or Ubuntu Linux
* **Python:** 3.11.x or 3.14.x
* **Node.js:** v18+ or v20+ (with `npm`)
* **Java Virtual Machine:** OpenJDK 17 (pre-bundled in `backend/tools/jdk-17.0.20.1+1-jre`)

### 1. Clone the Repository
```bash
git clone https://github.com/zoro-hue/smart-delivery-route-optimization.git
cd smart-delivery-route-optimization
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
# source venv/bin/activate

pip install -r requirements.txt
```

### 3. Run the Big Data Spark ETL (Optional — Pre-Generated Artifacts Included)
```bash
python -c "from app.services.bigdata_pipeline import BigDataPipelineService; BigDataPipelineService().run_pipeline()"
```

### 4. Start Backend Server
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```
*API Swagger Documentation active at: `http://127.0.0.1:8000/docs`*

### 5. Frontend Setup
```bash
cd ../frontend
npm install
npm run dev
```
*Application UI active at: `http://localhost:5173`*

---

## 9. API Reference

### Optimization Endpoints
* **`POST /api/optimization/run`** — Dispatches route optimization using specified algorithm or comparison suite.
  ```json
  {
    "algorithm": "classical",
    "selection_mode": "compare",
    "selected_algorithms": ["ortools", "clarke_wright", "two_opt", "qiga", "qaoa"],
    "num_customers": 4,
    "num_vehicles": 1,
    "vehicle_capacity": 50,
    "depot_lat": 40.7580,
    "depot_lon": -73.8292,
    "traffic_scenario": "normal",
    "weather_scenario": "clear"
  }
  ```
* **`GET /api/optimization/algorithms`** — Returns available algorithms, operational status, compute paradigm, and stop limits.
* **`GET /api/experiments/history`** — Returns persistent database records of previous optimization runs.

### Big Data Endpoints
* **`GET /api/bigdata/status`** — Returns Apache Spark version, Java version, and curated Parquet artifacts metadata.
* **`POST /api/bigdata/run-etl`** — Triggers on-demand PySpark batch processing pipeline across raw CSVs.

---

## 10. Project Directory Structure

```
smart-delivery-route-optimization/
├── backend/
│   ├── app/
│   │   ├── api/routes/          # FastAPI REST endpoints (optimization, bigdata, datasets)
│   │   ├── core/                # Centralized settings and path configurations
│   │   ├── db/                  # SQLite / SQLAlchemy async session manager
│   │   ├── models/              # Experiment and delivery data database schemas
│   │   └── services/            # Core business and computational services
│   │       ├── bigdata_pipeline.py    # Apache Spark 4.2.0 batch ETL service
│   │       ├── data_processor.py      # Parquet loader and cost factor calculator
│   │       ├── geo_validation.py      # Water body & 5-borough boundary validator
│   │       ├── road_network_service.py # KD-Tree snapping & street geometry reconstruction
│   │       └── optimization/
│   │           ├── classical_solver.py # OR-Tools, Clarke-Wright, 2-opt, Dijkstra, A*
│   │           ├── quantum_solver.py   # Qiskit 2.4.1 QUBO/Ising statevector solver
│   │           └── qiga_solver.py      # Quantum-Inspired Genetic Algorithm
│   ├── data/
│   │   ├── raw/                 # Raw NYC CSV datasets (orders, fleet, traffic, weather)
│   │   └── processed/
│   │       ├── road_graph_newyork.pickle  # 54,128-node indexed road graph
│   │       └── spark_output/              # 5 Curated Parquet datasets
│   ├── tests/                   # Automated pytest integration and regression test suite
│   └── tools/                   # Pre-bundled OpenJDK 17 JRE and Hadoop Winutils
├── frontend/
│   ├── src/
│   │   ├── components/Map/      # Interactive Leaflet map and route polyline layers
│   │   ├── pages/               # PlanWorkspace, DatasetsView, ExperimentsView
│   │   ├── services/            # Axios API client integrations
│   │   └── utils/geoValidation.ts # Client-side 5-borough coordinate validation
├── docs/
│   ├── assets/screenshots/      # Genuine UI screenshots embedded in README
│   └── research_report.md       # Technical audit report with exact empirical benchmarks
├── PROJECT_VS_SURVEY_APPROACH_DIFFERENCES.md # Detailed audit against LITERATURE_SURVEY (4).pdf
└── README.md                    # Project documentation
```

---

## 11. Academic Background & Citations

This project implements the theoretical framework, research gaps, and taxonomy established in our UROP literature survey:

> **A Literature Survey of Hybrid Big Data and Quantum Computing for Smart Delivery Route Optimization**  
> *J. Jayanth, B. Kaivalya, P. Shyam Sai, and Prof. Vishnu Prasad Varma*  
> Department of Computer Science and Engineering, SRM University-AP, Amaravati, Andhra Pradesh, India.  
> Document references: `LITERATURE_SURVEY (4).pdf` and `paper_preview.pdf`.

### Foundational References from Our Survey
1. **Chen (2020):** Y.-H. Chen, *"Intelligent algorithms for cold chain logistics distribution optimization based on Big Data cloud computing analysis,"* *Journal of Cloud Computing*, Vol. 9, No. 37, 2020. [DOI: 10.1186/s13677-020-00174-x](https://doi.org/10.1186/s13677-020-00174-x).
2. **Zheng (2019):** S. Zheng, *"Solving vehicle routing problem: A Big Data analytic approach,"* *IEEE Access*, Vol. 7, pp. 169565–169570, 2019. [DOI: 10.1109/ACCESS.2019.2955250](https://doi.org/10.1109/ACCESS.2019.2955250).
3. **Zhu et al. (2019):** L. Zhu, F. R. Yu, Y. Wang, B. Ning, and T. Tang, *"Big Data analytics in intelligent transportation systems: A survey,"* *IEEE Transactions on Intelligent Transportation Systems*, Vol. 20, No. 1, pp. 383–398, 2019. [DOI: 10.1109/TITS.2018.2815678](https://doi.org/10.1109/TITS.2018.2815678).
4. **Azad et al. (2023):** M. Azad, B. K. Behera, E. A. Ahmed, P. K. Panigrahi, and A. Farouk, *"Solving Vehicle Routing Problem Using Quantum Approximate Optimization Algorithm,"* *IEEE Transactions on Intelligent Transportation Systems*, Vol. 24, No. 7, pp. 7564–7573, 2023. [DOI: 10.1109/TITS.2022.3172241](https://doi.org/10.1109/TITS.2022.3172241).
5. **Yarkoni et al. (2020):** E. Yarkoni et al., *"Quantum Shuttle: Traffic navigation with quantum computing,"* 2020.
6. **Sarkar et al. (2026):** P. Sarkar, M. Hassan, A. H. Rambe, and M. Jusoh, *"Integrating quantum computing into intelligent transportation systems: A comprehensive review of emerging trends, open challenges, and future research directions,"* *Archives of Computational Methods in Engineering*, 2026. [DOI: 10.1007/s11831-026-10716-2](https://doi.org/10.1007/s11831-026-10716-2).
7. **Wang et al. (2021):** S. Wang, Z. Pei, C. Wang, and J. Wu, *"Shaping the future of the application of quantum computing in intelligent transportation system,"* *Intelligent and Converged Networks*, Vol. 2, No. 4, pp. 259–276, 2021. [DOI: 10.23919/ICN.2021.0019](https://doi.org/10.23919/ICN.2021.0019).
8. **El Azzaoui et al. (2021):** A. El Azzaoui, T. W. Kim, Y. Pan, and J. H. Park, *"A quantum approximate optimization algorithm based on blockchain heuristic approach for scalable and secure smart logistics systems,"* *Human-Centric Computing and Information Sciences*, Vol. 11, No. 46, 2021. [DOI: 10.22967/HCIS.2021.11.046](https://doi.org/10.22967/HCIS.2021.11.046).
9. **Niyazi & Behnamian (2023):** M. Niyazi and J. Behnamian, *"Application of cloud computing and Big Data in three-stage dynamic modeling of disaster relief logistics and wounded transportation,"* *Environmental Science and Pollution Research*, 2023. [DOI: 10.1007/s11356-022-24770-3](https://doi.org/10.1007/s11356-022-24770-3).
10. **Yuan et al. (2025):** Q. Yuan et al., *"Collaborative truck-UAV delivery routing optimization under dynamic weather conditions and customer demands,"* *IEEE Transactions on Consumer Electronics*, 2025. [DOI: 10.1109/TCE.2025.3622367](https://doi.org/10.1109/TCE.2025.3622367).

---

## 12. License & Acknowledgments

* **License:** Not yet specified. Licensing and ownership permissions for this collaborative university research project are pending confirmation.
* **Data Sources:** New York City Open Data, NYC Department of Transportation (DOT), NYC Taxi & Limousine Commission (TLC), OpenStreetMap (OSM) contributors, NOAA National Weather Service.
* **Institution:** Department of Computer Science & Engineering, SRM University-AP.
