# UROP Research Report: Smart Delivery Route Optimization Using Hybrid Big Data + Quantum Computing

**Authors:** J. Jayanth, B. Kaivalya, P. Shyam Sai (Undergraduate Student Researchers)  
**Supervisor:** Prof. Vishnu Prasad Varma (Faculty Supervisor)  
**Department:** Department of Computer Science and Engineering, SRM University-AP  
**Project:** Undergraduate Research Opportunity Program (UROP) — ROUTE/IQ  
**Document Status:** Working Academic Technical Report & Experimental Audit  
**Date:** October 2026  

---

## 1. Executive Summary

This study investigates the performance, scalability, and solution quality of hybrid classical-quantum algorithms applied to urban logistics and the Capacitated Vehicle Routing Problem (CVRP). Using real-world datasets from New York City (customer delivery orders, for-hire vehicle fleets, municipal depot locations, OpenStreetMap road topology, DOT traffic volume counts, and meteorological observations), we implement an Apache Spark 4.2.0 batch processing ETL pipeline and benchmark classical routing algorithms (OR-Tools, Clarke-Wright, 2-Opt, Dijkstra, A*) against a Quantum-Inspired Genetic Algorithm (QIGA) and the Quantum Approximate Optimization Algorithm (QAOA) simulated via Qiskit 2.4.1.

> **Academic Disclosure:** All QAOA experiments were executed via Qiskit classical statevector simulation on x86-64 CPU hardware rather than physical quantum hardware (QPUs). QIGA operates as a quantum-inspired heuristic on classical CPU. No claims of quantum supremacy or physical quantum speedup are asserted.

---

## 2. Dataset Synthesis & Ingestion Analysis

| Dataset Module | Source File | Records / Schema | Processing Engine | Curated Output & Characteristics |
|---|---|---|---|---|
| **1. Customer Orders** | `customers.csv` / `food_order.csv` | 1,898 orders | Apache Spark 4.2.0 | `customers.parquet` (1,898 rows, 128 KB). Delivery demand, service windows. |
| **2. Vehicle Fleet** | `vehicles.csv` / `For_Hire_Vehicles...` | 10,000 vehicles | Apache Spark 4.2.0 | `vehicles.parquet` (10,000 rows, 152 KB). Capacities, emissions, cost factors. |
| **3. Depots / Hubs** | `locations.csv` / `idnyc-locations.csv` | 18 locations | Apache Spark 4.2.0 | `locations.parquet` (18 rows, 3.3 KB). Municipal hubs across NYC 5 boroughs. |
| **4. Traffic Counts** | `traffic_nyc.csv` (DOT Historical) | 42,756 records | Apache Spark 4.2.0 | `traffic.parquet` (897 aggregated roadway features, 21.7 KB). Congestion & speed. |
| **5. Weather Data** | `weather_nyc.csv` (NOAA/NWS) | 59,760 hours | Apache Spark 4.2.0 | `weather.parquet` (4 condition groupings, 3.1 KB). Rain, wind, adverse penalties. |
| **6. Road Network** | `newyork.graphml` (archive 5) | 56,128 nodes, 138,132 edges | NetworkX + KD-Tree | Compiled pickle (68.4 MB). Real street geometries across all 5 NYC boroughs. |
| *6b. Manhattan Subgraph* | `manhatten.graphml` | 4,426 nodes, 9,626 edges | NetworkX | Local Manhattan baseline subgraph for micro-benchmarks. |

---

## 3. Mathematical Problem Formulation

### 3.1 Objective Function
The routing engine optimizes a multi-factor generalized logistics cost function:

$$\min \text{Cost} = w_d \cdot C_{\text{dist}} + w_t \cdot C_{\text{time}} + w_c \cdot C_{\text{cong}} + w_f \cdot C_{\text{fuel}} + w_l \cdot C_{\text{late}}$$

Where:
- $C_{\text{dist}} = \sum_k \sum_{(i,j) \in R_k} D_{i,j}$ (Total route distance)
- $C_{\text{time}} = \sum_k \sum_{(i,j) \in R_k} \frac{D_{i,j}}{V_{\text{speed}}} \cdot \gamma_{\text{traffic}} \cdot \gamma_{\text{weather}}$ (Delay-adjusted travel time)
- $w_d, w_t, w_c, w_f, w_l$ are user-configurable trade-off weights.

### 3.2 Constraints
1. **Visit Constraint:** Each delivery customer $i \in \{1, \dots, n\}$ is visited exactly once.
2. **Depot Boundary:** Every route starts at depot $0$ and terminates at depot $0$.
3. **Vehicle Capacity:** For each vehicle $k$, $\sum_{i \in R_k} d_i \le Q_k$.
4. **Non-negativity:** Edge travel costs $D_{i,j} \ge 0$.

---

## 4. Quantum QUBO & QAOA Formulation

### 4.1 Binary Decision Variables
For a single-vehicle TSP subproblem with $n$ vertices:
$$x_{i,p} \in \{0, 1\} \quad \text{where } x_{i,p} = 1 \text{ iff node } i \text{ is visited at step } p.$$

### 4.2 Hamiltonian Operator Mapping
Converting binary variables $x_i = \frac{I - Z_i}{2}$ yields the Ising Hamiltonian:
$$H_C = \sum_{i,j} J_{i,j} Z_i Z_j + \sum_i h_i Z_i + C_0$$

### 4.3 QAOA Quantum Circuit
With depth $p$, the quantum state is parameterized by angles $(\vec{\gamma}, \vec{\beta})$:
$$|\psi(\vec{\gamma}, \vec{\beta})\rangle = \prod_{l=1}^p e^{-i \beta_l H_M} e^{-i \gamma_l H_C} |+\rangle^{\otimes N}$$
Where $H_M = \sum_i X_i$ is the transverse-field mixer Hamiltonian.

---

## 5. Experimental Results & Comparative Analysis

Empirical evaluation conducted on a 4-node problem (1 depot, 3 customers) under identical road-network distance matrices and traffic scenarios:

| Metric | Google OR-Tools (Exact/Local) | Clarke-Wright / 2-Opt (Heuristic) | QIGA (Quantum-Inspired) | QAOA Simulator (Qiskit 2.4.1) |
|---|---|---|---|---|
| **Total Physical Distance** | 7.40 km | 7.50 km | 7.42 km | 7.40 km |
| **Feasibility Guarantee** | 100% Feasible | 100% Feasible | 100% Feasible | 100% Feasible (Decoded) |
| **Execution Time** | 0.042s | 0.003s | 0.078s | 0.873s – 1.142s |
| **Quantum Variables** | 0 | 0 | Q-bit Rotation Amplitudes | 9–16 Binary Qubits |
| **Circuit Depth** | N/A | N/A | N/A | 37 (Layers: $p=1$ to $p=2$) |
| **Optimization Method** | Guided Local Search | Savings Merge / 2-Opt | Dynamic $\Delta\theta$ Rotation | COBYLA / StatevectorSampler |
| **Hardware Execution** | Classical x86 CPU | Classical x86 CPU | Classical x86 CPU | Classical x86 CPU (Simulated) |
| **Capacity Violations** | 0 | 0 | 0 | 0 |

> **Comparative Takeaway:** While QAOA reliably converges to ground state energy ($E = -55.70$) on small problem instances, classical OR-Tools and heuristic solvers solve identical instances orders of magnitude faster without statevector exponential memory overhead. QIGA achieves high solution quality with minimal computational footprint, bridging quantum probabilistic concepts and scalable classical deployment.

---

## 6. Research Limitations & Future Directions

1. **Qubit Scaling Limit:** Standard statevector simulation is exponentially bounded by $2^N$ amplitudes, limiting local execution to $N \le 20$ qubits ($\sim 4$ to 8 nodes).
2. **Quantum Advantage Horizon:** True quantum advantage requires Fault-Tolerant Quantum Computing (FTQC) or large-scale noisy intermediate-scale quantum (NISQ) devices with error mitigation.
3. **Decomposition Strategy:** For large-scale multi-depot VRPs, a cluster-first route-second approach should partition customer zones classically, solving local route tours on quantum processors.
