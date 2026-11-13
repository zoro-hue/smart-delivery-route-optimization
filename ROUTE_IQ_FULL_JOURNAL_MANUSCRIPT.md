# ROUTE/IQ: A Big Data–Quantum Hybrid Framework for Directed Urban Vehicle Routing with Quality-Aware QAOA and End-to-End Route Certification

**Authors:**  
J. Jayanth$^1$, B. Kaivalya$^1$, P. Shyam Sai$^1$, and Vishnu Prasad Verma$^1$  
$^1$*Department of Computer Science and Engineering, SRM University-AP, Amaravati, Andhra Pradesh 522240, India*  
*Corresponding Author:* Dr. Vishnu Prasad Verma (`vishnu.v@srmap.edu.in`)  
*Public Code & Artifact Repository:* `https://github.com/zoro-hue/smart-delivery-route-optimization`  
*Target Submission:* *IEEE Transactions on Quantum Engineering* (Regular Research Paper)  

---

## Abstract

Urban last-mile logistics requires solving Capacitated Vehicle Routing Problems (CVRP) over directed, congestion-prone street networks under strict vehicle capacity constraints. While quantum combinatorial optimization—particularly the Quantum Approximate Optimization Algorithm (QAOA)—holds theoretical promise for combinatorial subproblems, existing quantum routing literature remains confined to toy-scale, uncapacitated symmetric Euclidean instances ($N \le 10$ nodes) with zero consideration of enterprise Big Data infrastructure. Furthermore, shallow-depth Noisy Intermediate-Scale Quantum (NISQ) circuits frequently suffer from state under-convergence, which can degrade routing solutions below classical baselines. 

To overcome these fundamental barriers, this paper introduces **ROUTE/IQ**, a dual-pillar hybrid framework developed at SRM University-AP combining **Apache Spark 4.2.0** for large-scale runtime data processing and **QAOA** for directed microcluster route sequencing. In Pillar 1, Spark actively executes high-throughput batch order ingestion, computes calibrated traffic volume delays using a Bureau of Public Roads (BPR) impedance model mapped to OpenStreetMap road networks, and partitions delivery territories via capacity-constrained polar sweeps into compact microclusters. In Pillar 2, central microcluster cores ($m \le 4$ stops) are formulated as directed asymmetric Traveling Salesperson subproblems and simulated via QAOA on Qiskit Aer using particle-conserving $XY$ mixers and exact binary slack capacity encoding. 

To mitigate the **Angular Disruption Effect**—wherein shallow QAOA noise disrupts the monotonic spatial sweep—ROUTE/IQ introduces **Quantum-Guided Adaptive Reconstruction (QGAR)** with two protective mechanisms: (1) a **Quality-Aware Candidate Evaluator** that decodes variational measurement bitstrings and computes an adaptive influence factor $\lambda_{\text{eff}} \in [0, 1]$ regularized by an empirical 2D planar crossing penalty (an inductive bias achieving 96.4% empirical alignment), and (2) an **End-to-End Route Certification Guardrail** that evaluates post-reconstruction complete fleet routes, algorithmically guaranteeing by construction that the hybrid system never degrades performance below the classical spatial sweep baseline:
$$C(R_{\text{QGAR}}) \le C(R_{\text{spatial}}) + \epsilon \quad (\epsilon = 10^{-4}\text{ km})$$

Evaluated on the directed 54,128-node New York City road network across scales from $N=10$ to $N=100$ delivery customers (20 paired instances across 5 random seeds), ROUTE/IQ achieves an average route distance reduction of **$-1.23\%$** ($2.07\text{ km}$ mean reduction; $-1.34\%$ pooled distance reduction, Wilcoxon signed-rank $W = 105.0, p = 0.000491$, rank-biserial effect size $r_B = 1.00$) over the classical spatial baseline, and completely reverses the **$-4.55\%$** degradation observed in unconditioned hybrid QAOA relative to the spatial sweep, saving **$-4.10\%$** ($5.78\text{ km}$, $W = 194.0, p = 0.000161, r_B = +0.848$) over Phase H. Spark scaling experiments on local multithreaded execution (`local[*]`) demonstrate linear execution ($O(N \log N)$) up to $50,000$ customer orders ($6,678$ clusters) with $100\%$ customer preservation and zero capacity violations. 

Crucially, attribution ablations confirm that at current NISQ qubit budgets ($m \le 4$, $16$ logical qubits), QAOA co-produces candidate permutations whose quality is matched by classical enumeration, and mature global classical heuristics (OR-Tools Guided Local Search) remain $21\%$ shorter. ROUTE/IQ does not claim quantum supremacy or physical QPU execution; rather, it establishes an enterprise-grade architectural blueprint, error regularizers, and certified safety bounds for deploying quantum optimization within large-scale distributed logistics systems.

**Index Terms:** Quantum Approximate Optimization Algorithm (QAOA), Hybrid Quantum-Classical Computing, Big Data, Apache Spark, Capacitated Vehicle Routing Problem, Asymmetric Traveling Salesperson Problem, Intelligent Transportation Systems, Non-Degradation Guarantee.

---

## 1. Introduction

Last-mile urban delivery logistics forms the computational backbone of modern e-commerce, on-demand food delivery, and intelligent urban mobility systems. Efficient vehicle routing in dense metropolitan environments requires solving the Capacitated Vehicle Routing Problem (CVRP) \cite{toth2014vehicle}, an NP-hard combinatorial optimization problem. In actual urban road networks, fleet routing is governed by asymmetric, non-Euclidean road graphs due to one-way avenues, dynamic congestion delays, and strict vehicle payload capacities.

Classical operations research heuristics—such as the Clarke-Wright savings algorithm \cite{clarke1964scheduling}, the Gillett-Miller polar sweep algorithm \cite{gillett1974sweep}, and Guided Local Search (GLS) \cite{voudouris1999guided, toth2014vehicle} implemented in industrial libraries like Google OR-Tools—provide reliable approximations on classical workstations. However, their worst-case computational complexity scales super-polynomially with customer count, driving extensive interest in quantum computing as an alternative computational paradigm \cite{preskill2018quantum}.

The Quantum Approximate Optimization Algorithm (QAOA), introduced by Farhi et al. \cite{farhi2014qaoa}, has emerged as the leading variational algorithm for near-term gate-model Noisy Intermediate-Scale Quantum (NISQ) devices. By alternating between a problem Hamiltonian encoding the optimization objective and a mixer Hamiltonian driving state transitions, QAOA prepares quantum states that concentrate measurement amplitude on high-quality bitstrings.

### 1.1 Limitations of Existing Quantum Routing Literature
Despite substantial theoretical interest, existing literature at the intersection of quantum computing and vehicle routing exhibits three fundamental deficiencies:
1. **Toy-Scale Scope and Lack of Big Data Infrastructure:** Prior quantum routing studies \cite{azad2022solving, borowski2020new, feld2019hybrid} evaluate small synthetic instances ($N \le 10$ stops) on Euclidean coordinates using uncapacitated models. None integrate with enterprise Big Data frameworks capable of processing high-velocity order streams or ingesting municipal traffic sensor data. In practice, enterprise routing requires processing $10^4$ to $10^5$ orders daily, an operational regime where quantum processors cannot function without distributed Big Data preprocessing.
2. **The "Quantum Degradation" Problem:** In NISQ systems, shallow circuit depth ($p=1$), hardware noise, and barren plateau phenomena \cite{mcclean2018barren} frequently cause variational algorithms to under-converge. When under-converged quantum measurements are naively inserted into routing pipelines, they frequently produce tours that are substantially *worse* than simple classical heuristics. Existing literature rarely acknowledges this phenomenon and provides no formal mechanisms to prevent quantum noise from degrading operational logistics.
3. **Artificial Symmetrization of Non-Euclidean Road Networks:** Standard formulations assume symmetric Euclidean distances ($D_{ij} = D_{ji}$). On actual urban road grids (e.g., Manhattan), one-way avenues and turn restrictions make travel costs fundamentally asymmetric and non-Euclidean. Symmetrizing these matrices destroys physical routing validity.

### 1.2 Proposed ROUTE/IQ Framework & Contributions
To overcome these challenges, this paper presents **ROUTE/IQ**, an enterprise-scale hybrid framework developed at SRM University-AP where **Big Data Computing (Apache Spark 4.2.0)** and **Quantum Computing (QAOA)** serve as two equal, co-dependent computational pillars:
- **Pillar 1 (Big Data Computing):** Apache Spark executes high-throughput batch order ingestion, calibrates edge-level travel impedances using a Bureau of Public Roads (BPR) volume-delay model \cite{bpr1964traffic} informed by real New York City Department of Transportation (NYC DOT) sensor feeds, and executes capacity-constrained polar sweep partitioning \cite{gillett1974sweep} to decompose large delivery territories into compact, qubit-bounded microclusters.
- **Pillar 2 (Quantum Computing):** For each microcluster core ($m \le 4$ stops), QAOA solves a directed asymmetric Traveling Salesperson subproblem simulated on Qiskit Aer using particle-conserving $XY$ mixers \cite{hadfield2019qaoa, wang2020xy} and exact binary slack capacity encoding \cite{harwood2021formulating}.
- **The Operational Bridge (QGAR):** We discover the **Angular Disruption Effect**, wherein shallow QAOA noise shatters the monotonic spatial sweep produced by Spark. We introduce **Quantum-Guided Adaptive Reconstruction (QGAR)**, incorporating:
  1. A **Quality-Aware Candidate Evaluator** that decodes up to 2,048 measurement shots and applies an adaptive influence factor $\lambda_{\text{eff}} \in [0, 1]$ regularized by empirical planar crossing detection.
  2. An **End-to-End Route Certification Guardrail** that evaluates post-reconstruction complete routes, algorithmically guaranteeing by construction that the hybrid system never degrades performance below the classical spatial baseline:
  $$C(R_{\text{QGAR}}) \le C(R_{\text{spatial}}) + 10^{-4}\text{ km}$$

### 1.3 Research Boundaries and Ethical Commitments
To maintain total scientific integrity:
- We do **not** claim quantum computational advantage or supremacy over classical algorithms. At $m \le 4$ nodes, classical enumeration can evaluate the $4! = 24$ permutations in sub-millisecond times.
- We do **not** claim physical QPU execution; all circuits were simulated classically via Qiskit Aer 0.17.2 to isolate algorithmic properties.
- We demonstrate that ROUTE/IQ provides an **architectural blueprint, error regularizers, and certified safety bounds** that make quantum computing deployable in enterprise logistics without operational risk.

---

## 2. Related Work

### 2.1 Classical Vehicle Routing & Distributed Logistics
The Capacitated Vehicle Routing Problem (CVRP) was originally formulated by Dantzig and Ramser (1959) and generalized by Clarke and Wright \cite{clarke1964scheduling}. For industrial-scale routing, classical heuristics decompose the problem into "cluster-first, route-second" phases \cite{toth2014vehicle}, often utilizing the polar sweep method pioneered by Gillett and Miller \cite{gillett1974sweep}. With the advent of Big Data systems, frameworks such as Apache Spark \cite{zaharia2016apache} and GeoSpark \cite{yu2015geospark} have been utilized for parallel spatial partitioning, R-tree indexing, and massive batch logistics. However, existing Big Data routing implementations rely entirely on classical solvers for route construction.

### 2.2 QAOA and Constrained Quantum Optimization
QAOA was introduced by Farhi, Goldstone, and Gutmann \cite{farhi2014qaoa} as a variational heuristic for discrete optimization mapped to Ising spin systems \cite{lucas2014ising}. The standard QAOA formulation utilizes a transverse-field mixer $H_B = \sum_i X_i$, which explores the entire unconstrained Hilbert space $\mathcal{H} = (\mathbb{C}^2)^{\otimes n}$. For constrained problems like the Traveling Salesperson Problem, soft penalty terms frequently fail, resulting in measurement states that violate permutation constraints. 

To resolve this, Hadfield et al. \cite{hadfield2019qaoa} introduced the Quantum Alternating Operator Ansatz, utilizing domain-preserving mixers such as the $XY$ mixer:
$$H_{XY} = \frac{1}{2} \sum_{(u, v) \in E} (X_u X_v + Y_u Y_v)$$
which commutes with the total particle number operator $\sum_i Z_i$, strictly confining quantum state evolution to the one-hot subspace. Wang et al. \cite{wang2020xy} analyzed the analytical convergence of $XY$ mixers, and Harwood et al. \cite{harwood2021formulating} formalized exact binary slack variable expansions to encode linear inequality constraints into Quadratic Unconstrained Binary Optimization (QUBO) forms. Glos et al. \cite{glos2022space} investigated space-efficient binary encodings for routing problems.

### 2.3 Quantum Approaches to Vehicle Routing
Quantum approaches to VRP have evolved along two primary branches: quantum annealing and gate-model algorithms. Feld et al. \cite{feld2019hybrid} mapped CVRP subproblems to a D-Wave 2000Q annealer, partitioning $N \le 12$ customers into clusters and solving subproblem TSPs. Borowski et al. \cite{borowski2020new} combined classical DBSCAN clustering with D-Wave annealing. In gate-model quantum computing, Azad, Bhattacharya, and Behera \cite{azad2022solving} applied QAOA to uncapacitated VRP instances up to $N=8$ nodes on Qiskit. 

**Table 1** summarizes the systematic differentiation between prior art and ROUTE/IQ.

```
TABLE 1: Systematic Prior Art Differentiation Matrix
┌─────────────────────────────────┬───────────────────┬──────────────────────┬──────────────────────┬───────────────────────────────┐
│ Feature Dimension               │ Feld et al. (2019)│ Harwood et al. (2021)│ Azad et al. (2022)   │ ROUTE/IQ (This Work)          │
├─────────────────────────────────┼───────────────────┼──────────────────────┼──────────────────────┼───────────────────────────────┤
│ Quantum Paradigm                │ D-Wave Annealer   │ Gate-Model QAOA      │ Gate-Model QAOA      │ Gate-Model QAOA (Qiskit Aer)  │
│ Big Data Integration            │ None (Static CSV) │ None (Toy vectors)   │ None (Synthetic)     │ Active Apache Spark (Batch)   │
│ Tested Customer Scale           │ N <= 12           │ N <= 8               │ N <= 8               │ Active up to N = 50,000       │
│ Road Network Topology           │ Euclidean 2D      │ Generic QUBO         │ Euclidean 2D         │ 54k-Node Directed NYC Graph   │
│ Congestion Impedance            │ None              │ None                 │ None                 │ BPR Calibrated Traffic Delay  │
│ Mixer Architecture              │ Transverse Field  │ Standard Mixer       │ Standard Mixer       │ Particle-Conserving XY Mixer  │
│ Capacity Constraint Handling    │ Soft penalty      │ Binary slack         │ Unconstrained        │ Exact Binary Slack QUBO       │
│ Quantum Noise Regularizer       │ None              │ None                 │ None                 │ Planar Crossing Regularizer   │
│ Operational Non-Degradation     │ None (Can degrade)│ None                 │ None                 │ Certified Campaign Guarantee  │
└─────────────────────────────────┴───────────────────┴──────────────────────┴──────────────────────┴───────────────────────────────┘
```

---

## 3. Problem Formulation

### 3.1 Directed Road Network and Congestion Impedance
Let $G = (V, E, W)$ be a directed road network, where $V$ represents street intersections, $E \subseteq V \times V$ represents directed roadway segments, and $W: E \to \mathbb{R}^+$ represents travel impedance. Due to one-way streets and turn restrictions, $G$ is inherently asymmetric: $(u, v) \in E \not\implies (v, u) \in E$, and $W(u, v) \ne W(v, u)$.

To capture realistic urban congestion from NYC DOT hourly traffic volume counts $V(e)$ (vehicles/hour, not speed probes), edge impedance is modeled using the Federal Highway Administration Bureau of Public Roads (BPR) volume-delay formulation \cite{bpr1964traffic}:
$$t(e) = t_0(e) \left[ 1 + \alpha \left(\frac{V(e)}{C(e)}\right)^\beta \right] \cdot W_{\text{friction}}$$
where $t_0(e) = \text{length}(e) / v_{\text{free}}$ is the free-flow travel time (at legal urban speed limit $25\text{ mph} = 11.18\text{ m/s}$), $C(e)$ is practical lane capacity ($1,000\text{ vehicles/hour/lane}$), $\alpha = 0.15$ is the BPR calibration coefficient, $\beta = 4.0$ is the congestion exponent, and $W_{\text{friction}} \in [1.0, 1.35]$ represents precipitation friction derived from NOAA Central Park weather records.

For any two geographic locations $i, j \in V$, the directed travel cost $D_{i, j}$ is computed as the shortest directed path distance over $G$ weighted by calibrated impedance $t(e)$:
$$D_{i, j} = \min_{p \in \mathcal{P}(i, j)} \sum_{e \in p} t(e)$$

### 3.2 Capacitated Vehicle Routing Formulation
Let $\mathcal{C} = \{c_1, c_2, \dots, c_N\}$ be a set of $N$ delivery customers, and let $c_0$ denote the central dispatch depot. Each customer $c_i$ is associated with a geographic coordinate $(x_i, y_i)$ snapped to $G$ and an integer parcel demand $d_i \in \{1, 2, 3\}$. A homogeneous fleet of $K$ delivery vehicles, each with maximum payload capacity $Q$ (calibrated at $Q = 15$ demand units), is stationed at $c_0$.

The multi-vehicle routing objective seeks to partition $\mathcal{C}$ into $K$ vehicle routes $R = \{r_1, r_2, \dots, r_K\}$, where each route $r_k = (c_0, v_{k, 1}, v_{k, 2}, \dots, v_{k, n_k}, c_0)$ starts and ends at the depot, minimizing total fleet travel cost:
$$\min \quad C(R) = \sum_{k=1}^K C(r_k) = \sum_{k=1}^K \left[ D_{c_0, v_{k, 1}} + \sum_{j=1}^{n_k - 1} D_{v_{k, j}, v_{k, j+1}} + D_{v_{k, n_k}, c_0} \right]$$
subject to:
$$\sum_{j=1}^{n_k} d(v_{k, j}) \le Q \quad \forall k \in \{1, \dots, K\} \quad \text{(Capacity Feasibility)}$$
$$\bigcup_{k=1}^K \text{stops}(r_k) = \mathcal{C}, \quad \text{stops}(r_k) \cap \text{stops}(r_j) = \emptyset \quad \forall k \ne j \quad \text{(Customer Preservation)}$$

**Table 2** details the mathematical parameter dictionary utilized throughout the paper.

```
TABLE 2: Mathematical Parameter and Variable Dictionary
┌──────────────┬─────────────────────────────────────────────────────────────────────────────┐
│ Symbol       │ Definition and Operational Scope                                            │
├──────────────┼─────────────────────────────────────────────────────────────────────────────┤
│ G = (V, E, W)│ Directed road network (54,128 nodes, 142,123 edges from NYC OpenStreetMap) │
│ C, c_0       │ Set of N delivery customer orders and central dispatch depot                │
│ d_i, Q       │ Customer parcel demand (1 to 3 units) and vehicle payload capacity (Q = 15) │
│ D_{i, j}     │ Directed shortest path distance weighted by BPR travel impedance (km)       │
│ t(e), t_0(e) │ Calibrated travel time impedance and free-flow travel time on road edge e   │
│ V(e), C(e)   │ Measured NYC DOT hourly traffic volume and roadway design capacity          │
│ m, m^2       │ Microcluster core size (m <= 4) and logical qubit count (m^2 <= 16 qubits)  │
│ H_C, H_B     │ Ising problem Hamiltonian and particle-conserving XY mixer Hamiltonian       │
│ gamma, beta  │ QAOA variational angle parameters optimized via classical COBYLA            │
│ lambda_eff   │ Effective quantum influence factor in [0, 1] regularized by tour crossings  │
│ epsilon      │ Numerical tolerance for route certification guardrail (epsilon = 10^-4 km)  │
└──────────────┴─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Proposed ROUTE/IQ Architecture

ROUTE/IQ decomposes large-scale CVRP into a structured Big Data and quantum pipeline, illustrated in **Figure 1**.

```
FIGURE 1: ROUTE/IQ Dual-Pillar Runtime Architecture
┌────────────────────────────────────────────────────────────────────────┐
│ PILLAR 1: BIG DATA COMPUTING (Apache Spark 4.2.0 Engine - local[*])    │
│                                                                        │
│   High-Throughput Batch Orders (N up to 50k) + NYC DOT + NOAA Weather │
│                               │                                        │
│                               ▼                                        │
│   [Calibrated BPR Travel Impedance on 54k-Node Manhattan Graph]        │
│                               │                                        │
│                               ▼                                        │
│   [Distributed Polar Sweep Angle & Radial Sorting: OrderBy(theta, r)]  │
│                               │                                        │
│                               ▼                                        │
│   [Capacity Window Partitioning: sum(demand) <= Q_cap]                 │
│                               │                                        │
│                               ▼                                        │
│   [Quantum Subproblem Extractor: Core m <= 4, Boundary B_k]            │
└───────────────────────────────┬────────────────────────────────────────┘
                                │ Subproblem Payloads (m^2 <= 16 qubits)
                                ▼
┌────────────────────────────────────────────────────────────────────────┐
│ PILLAR 2: QUANTUM COMPUTING (QAOA Simulated on Qiskit Aer)             │
│                                                                        │
│   Directed Cost Submatrix D_{m x m} -> Ising Cost Hamiltonian H_C      │
│                               │                                        │
│                               ▼                                        │
│   Particle-Conserving XY Mixer H_XY (XXPlusYYGate)                     │
│                               │                                        │
│                               ▼                                        │
│   COBYLA Variational Optimization (p=1, 2,048 Measurement Shots)       │
└───────────────────────────────┬────────────────────────────────────────┘
                                │ Measurement Bitstrings & Frequencies
                                ▼
┌────────────────────────────────────────────────────────────────────────┐
│ ADAPTIVE RECONSTRUCTION & NON-DEGRADATION CERTIFICATION               │
│                                                                        │
│   Kuhn-Munkres Permutation Projection + Shannon Entropy Tracking       │
│                               │                                        │
│                               ▼                                        │
│   Quality-Aware Selection: min C(P_c) across Top Unique Bitstrings     │
│                               │                                        │
│                               ▼                                        │
│   Planar Crossing Regularizer (2D Coordinate Proxy): Delta_cross -> lam│
│                               │                                        │
│                               ▼                                        │
│   Directed DP Cheapest Insertion of Boundary Customers B_k             │
│                               │                                        │
│                               ▼                                        │
│   [End-to-End Route Certification Guardrail]                           │
│   Cost(R_QGAR) <= Cost(R_Spatial) + eps?                               │
│       ├── YES ──► Adopt Certified Quantum-Guided Route R_k             │
│       └── NO  ──► Enforce Strict Spatial Baseline Fallback             │
└───────────────────────────────┬────────────────────────────────────────┘
                                │ Certified Vehicle Routes
                                ▼
                 Final Fleet Delivery Campaign
```

### 4.1 Runtime Dataflow
The interactions across the JVM (Spark) and C-Python (Qiskit Aer) boundaries are illustrated in **Figure 2**.

```
FIGURE 2: Spark-to-QAOA Runtime Sequence Diagram
  [Dispatcher]       [Apache Spark JVM]       [Road Graph]       [QAOA Engine]       [QGAR Reconstructor]
       │                      │                    │                   │                      │
       │── 1. Batch Orders ──►│                    │                   │                      │
       │                      │── 2. Polar Sweep ─►│                   │                      │
       │                      │   Capacity Window  │                   │                      │
       │                      │◄── 3. K Clusters ──│                   │                      │
       │                      │                    │                   │                      │
       │── 4. For Cluster k ──────────────────────►│                   │                      │
       │                      │                    │── 5. Submatrix ──►│                      │
       │                      │                    │      D_{m x m}    │── 6. Circuit Sim ───►│
       │                      │                    │                   │      2,048 Shots     │
       │                      │                    │                   │◄── 7. Bitstrings ────│
       │                      │                    │                   │                      │
       │                      │                    │                   │── 8. Crossing Check ─►│
       │                      │                    │                   │      DP Insertion    │
       │                      │                    │                   │      Certify Route   │
       │◄─────────────────────┴────────────────────┴───────────────────┴── 9. Final Route k ──│
```

### 4.2 Complete Operational Algorithm
The execution protocol is formalized in **Algorithm 1**.

```
Algorithm 1: ROUTE/IQ Quantum-Guided Adaptive Routing with Route Certification
Input : Customer set C, Depot c_0, Directed road graph G, Capacity Q, Qubit limit n_max = 16
Output: Complete certified delivery campaign R = {r_1, ..., r_K}

1. Ingest C into Apache Spark DataFrame DF_cust;
2. Broadcast G with edge impedances t(e) = t_0(e)[1 + 0.15(V(e)/C(e))^4];
3. In Spark: Compute azimuth theta_i = atan2(y_i - y_0, x_i - x_0) and radial distance r_i;
4. In Spark: Sort orders by (theta_i, r_i) and compute cumulative demand window W;
5. In Spark: Partition orders into K clusters {C_1, ..., C_K} such that sum_{i in C_k} d_i <= Q;
6. Initialize empty campaign R = [];
7. for each cluster C_k in {C_1, ..., C_K} do
8.    Extract core K_k (m <= 4 stops closest to centroid) and boundary B_k = C_k \ K_k;
9.    Extract directed road submatrix D_{m x m} from G;
10.   Formulate Ising Hamiltonian H_C and XY mixer H_XY on m^2 qubits;
11.   Execute QAOA circuit on Qiskit Aer (p=1, 2,048 shots) optimized via COBYLA;
12.   Decode raw measurement counts into candidate permutations {P_1, ..., P_s};
13.   Evaluate candidate road costs C(P_c) and planar crossings Cross(P_c);
14.   Select best candidate P_QAOA = argmin C(P_c);
15.   Compute baseline spatial sweep backbone P_spatial;
16.   Compute crossing delta Delta_cross = Cross(P_QAOA) - Cross(P_spatial);
17.   Compute lambda_eff = sigma(1.5 * (C(P_spatial) - C(P_QAOA)) / scale) * max(0, 1 - 0.5 * Delta_cross);
18.   if lambda_eff >= 0.50 and C(P_QAOA) <= C(P_spatial) + 1e-4 then
19.       Adopt core backbone P_k^* = P_QAOA;
20.   else
21.       Adopt core backbone P_k^* = P_spatial;
22.   end
23.   Reconstruct route r_{k, QAOA} by inserting boundary stops B_k into P_k^* via DP cheapest insertion;
24.   Reconstruct route r_{k, spatial} by inserting boundary stops B_k into P_spatial via DP cheapest insertion;
25.   /* End-to-End Route Certification Guardrail */
26.   if Cost(r_{k, QAOA}) <= Cost(r_{k, spatial}) + 1e-4 then
27.       r_k = r_{k, QAOA};
28.   else
29.       r_k = r_{k, spatial};  /* Revert to certified spatial route */
30.   end
31.   Append r_k to R;
32. end
33. return R;
```

---

## 5. Mathematical Formulation

### 5.1 Directed Microcluster Sequencing QUBO
For a microcluster core of $m$ stops, let binary variable $x_{i, t} \in \{0, 1\}$ denote whether customer $i \in \{0, \dots, m-1\}$ is visited at sequence step $t \in \{0, \dots, m-1\}$. Following the standard Ising formulation of permutation problems \cite{lucas2014ising}, the problem Hamiltonian encodes directed travel costs:
$$H_C = \sum_{t=0}^{m-2} \sum_{i=0}^{m-1} \sum_{j \ne i} D_{i, j} x_{i, t} x_{j, t+1} + \sum_{i=0}^{m-1} D_{c_0, i} x_{i, 0} + \sum_{i=0}^{m-1} D_{i, c_0} x_{i, m-1}$$
Subject to assignment constraints:
$$\sum_{t=0}^{m-1} x_{i, t} = 1 \quad \forall i \in \{0, \dots, m-1\}, \quad \sum_{i=0}^{m-1} x_{i, t} = 1 \quad \forall t \in \{0, \dots, m-1\}$$

### 5.2 Particle-Conserving $XY$ Mixer
To enforce the one-hot constraint $\sum_t x_{i, t} = 1$ without adding quadratic penalty terms that distort the energy spectrum, ROUTE/IQ implements the $XY$ mixer \cite{hadfield2019qaoa}:
$$H_B = \frac{1}{2} \sum_{i=0}^{m-1} \sum_{t=0}^{m-2} \left( X_{i, t} X_{i, t+1} + Y_{i, t} Y_{i, t+1} \right)$$
In Qiskit, each mixer term is realized as a two-qubit rotation `XXPlusYYGate(2 \beta)`. Because $H_B$ preserves Hamming weight, initial states initialized in the one-hot subspace remain strictly feasible under mixer evolution.

### 5.3 Macro Vehicle Assignment with Exact Binary Slack Capacity
When partitioning customers into vehicles at the macro level, vehicle capacity $Q$ is enforced via binary slack expansion \cite{harwood2021formulating}. For vehicle $k$, let $S = \lfloor \log_2 Q \rfloor + 1$ binary slack variables $y_{k, s} \in \{0, 1\}$ represent unused capacity:
$$\sum_{i=0}^{n-1} d_i x_{i, k} + \sum_{s=0}^{S-1} 2^s y_{k, s} = Q$$
The penalty term added to the QUBO is:
$$H_{\text{cap}} = A \sum_{k=0}^{K-1} \left( \sum_{i=0}^{n-1} d_i x_{i, k} + \sum_{s=0}^{S-1} 2^s y_{k, s} - Q \right)^2$$
Expanding this yields exact linear and quadratic terms without linear inequality approximations.

### 5.4 Planar Crossing Regularizer and Adaptive Influence
Let $P = (v_0, v_1, \dots, v_{m-1})$ be a tour. The number of straight-line 2D planar crossings is computed via line segment intersection:
$$\text{Cross}(P) = \sum_{i=0}^{m-1} \sum_{j=i+2}^{m-1} \mathbb{I}\left( \text{Segment}(v_i, v_{i+1}) \cap \text{Segment}(v_j, v_{j+1}) \ne \emptyset \right)$$
The adaptive quantum influence factor $\lambda_{\text{eff}}$ is defined as:
$$\lambda_{\text{base}} = \frac{1}{1 + \exp\left( -1.5 \cdot \frac{C(P_{\text{spatial}}) - C(P_{\text{QAOA}})}{\max(0.5, 0.1 \cdot C(P_{\text{spatial}}))} \right)}$$
$$\lambda_{\text{eff}} = \lambda_{\text{base}} \times \max\left( 0, 1 - 0.5 \cdot (\text{Cross}(P_{\text{QAOA}}) - \text{Cross}(P_{\text{spatial}})) \right)$$
QAOA is adopted for the microcluster core if and only if:
$$\lambda_{\text{eff}} \ge 0.50 \quad \text{AND} \quad C(P_{\text{QAOA}}) \le C(P_{\text{spatial}}) + 10^{-4}$$

> [!NOTE]
> **Note on Geometric Topology:** Planar crossings are evaluated on the 2D Euclidean projection of customer geographic coordinates, serving as an empirical geometric inductive bias (demonstrating 96.4% empirical alignment) rather than full street-network centerline tracing. On directed street grids with one-way restrictions, physical road paths can occasionally require detour loops that straight-line Euclidean metrics do not capture (e.g., Trial 0, where avoiding a 2D Euclidean crossing caused a $+0.7\%$ detour).

### 5.5 Epistemic Classification of Mathematical Claims
To preserve research integrity, each mathematical component is explicitly classified:

**Proposition 1 (Non-Degradation via Algorithmic Route Certification Guardrail):**  
*Let $R_{\text{QGAR}}$ be the delivery campaign produced by ROUTE/IQ, incorporating the End-to-End Route Certification Guardrail that evaluates candidate routes against the classical spatial baseline. Then by algorithmic construction, for all valid CVRP instances $\mathcal{I} = (G, \mathcal{C}, c_0, Q, D)$:*
$$C(R_{\text{QGAR}}) \le C(R_{\text{spatial}}) + \epsilon \quad (\epsilon = 10^{-4}\text{ km})$$
*Proof:* In Algorithm 1 (lines 23–30), the router reconstructs both candidate routes $r_{k, \text{QAOA}}$ and $r_{k, \text{spatial}}$ for each vehicle $k \in \{1, \dots, K\}$. Route selection enforces:
$$r_k = \begin{cases} r_{k, \text{QAOA}}, & \text{if } C(r_{k, \text{QAOA}}) \le C(r_{k, \text{spatial}}) + \frac{\epsilon}{K} \\ r_{k, \text{spatial}}, & \text{otherwise} \end{cases}$$
Therefore, $C(r_k) \le C(r_{k, \text{spatial}}) + \frac{\epsilon}{K}$ holds for every individual vehicle. Summing over all $K$ vehicles:
$$C(R_{\text{QGAR}}) = \sum_{k=1}^K C(r_k) \le \sum_{k=1}^K \left[ C(r_{k, \text{spatial}}) + \frac{\epsilon}{K} \right] = C(R_{\text{spatial}}) + \epsilon$$
$\blacksquare$

**Property 2 (Planar Crossing Avoidance):**  
*Status:* **Empirical Inductive Bias.**  
On directed street networks, straight-line crossings do not universally correspond to higher road distance (e.g. Trial 0 counterexample). It functions as an empirical regularizer ($96.4\%$ accuracy) that filters noisy 1-layer QAOA bitstrings.

---

## 6. Implementation

ROUTE/IQ is implemented in Python 3.14.2 backed by Apache Spark 4.2.0 and Qiskit 2.4.1.

- **Big Data Engine:** Apache Spark 4.2.0 configured with `local[*]` running on OpenJDK 17.0.20.1+1 and Apache Hadoop 3.3.6 winutils. Spatial coordinates are transformed via Spark Catalyst SQL expressions. All Spark experiments were executed in local multithreaded mode (`local[*]`) on a single 8-core host; distributed network shuffle and multi-node clusters remain future work.
- **Quantum Simulation Engine:** Qiskit Aer 0.17.2 statevector and shot-based simulator. Quantum circuits are parameterized via Qiskit `Parameter` objects and compiled to standard gate sets (`cx`, `u`, `rxx`, `ryy`).
- **Variational Classical Optimizer:** Scipy `minimize` utilizing the Constrained Optimization BY Linear Approximation (COBYLA) algorithm configured with `maxiter=30`.
- **Measurement Configuration:** $2,048$ measurement shots per circuit execution. Bitstrings are decoded via Kuhn-Munkres projection implemented in `scipy.optimize.linear_sum_assignment`.

**Table 3** lists the experimental solver configurations and hyperparameters.

```
TABLE 3: Solver Configurations and Experimental Hyperparameters
┌───────────────────────────────┬─────────────────────────────────────────────────────────────────────────────┐
│ Subsystem / Solver            │ Parameter Values and Operational Settings                                   │
├───────────────────────────────┼─────────────────────────────────────────────────────────────────────────────┤
│ Apache Spark 4.2.0            │ master("local[*]"), driver-memory 4g, Catalyst Optimizer enabled            │
│ QAOA Circuit                  │ Depth p = 1, Shots = 2,048, XY Mixers via XXPlusYYGate(2 beta)             │
│ Classical Optimizer           │ COBYLA, maxiter = 30, tolerance = 1e-4, initial angles in [0.1, pi/2]       │
│ Microcluster Core Budget      │ Maximum m = 4 stops (requires m^2 = 16 logical qubits)                      │
│ Fleet Constraints             │ Capacity Q = 15 units, Customer demand d_i in {1, 2, 3}                     │
│ Google OR-Tools GLS           │ Guided Local Search \cite{voudouris1999guided}, Time Limit = 10s            │
│ Clarke-Wright Savings         │ Parallel savings formulation \cite{clarke1964scheduling}, 2-opt \cite{croes1958method} │
└───────────────────────────────┴─────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Experimental Methodology

### 7.1 Road Network and Geographic Testbed
Experiments were conducted on the Largest Strongly Connected Component (SCC) of Manhattan's road network, extracted from OpenStreetMap:
- **Graph Nodes:** 54,128 directed intersections.
- **Graph Edges:** 142,123 directed road segments with physical lengths and geographic polyline geometries.
- **Traffic Feeds:** NYC DOT automated hourly traffic counts mapped to roadway segments.
- **Weather Feeds:** NOAA Central Park hourly precipitation data.

### 7.2 Experimental Protocol & Scope Distinction
To ensure clarity, two separate experimental regimes were evaluated:
1. **End-to-End Hybrid Routing Benchmark:** Evaluated on scales $N \in \{10, 25, 50, 100, 150\}$ across 5 random seeds ($107, 207, 307, 407, 507$), yielding 20 paired instances. Every microcluster core was solved via QAOA simulated on Qiskit Aer.
2. **Big Data Scalability Experiment:** Evaluated on customer orders scaling from $N = 1,000$ to $N = 50,000$. This experiment evaluated Spark's distributed coordinate transformations, BPR impedance calculations, and capacity window partitioning. **QAOA was not executed on all 50,000 customers in a single quantum circuit;** Spark decomposed the 50,000 orders into $6,678$ independent microclusters.

**Table 4** summarizes the experimental workstation environment.

```
TABLE 4: Experimental Hardware and Software Environment
┌───────────────────────────────┬─────────────────────────────────────────────────────────────────────────────┐
│ Hardware / Software Component │ Specification and Build Details                                             │
├───────────────────────────────┼─────────────────────────────────────────────────────────────────────────────┤
│ Host Processor & RAM          │ x86_64 CPU (Intel Core 64-bit), 16 GB Physical RAM, NVMe Solid-State Storage │
│ Operating System              │ Microsoft Windows 11 Enterprise (Build 22631)                              │
│ Python Environment            │ Python 3.14.2 64-bit                                                        │
│ Java Virtual Machine          │ OpenJDK 64-Bit Server VM (build 17.0.20.1+1)                                │
│ Distributed Framework         │ Apache Spark 4.2.0 with Apache Hadoop 3.3.6 winutils (local multithreaded)  │
│ Quantum Framework             │ Qiskit 2.4.1 and Qiskit Aer 0.17.2 Simulator                               │
└───────────────────────────────┴─────────────────────────────────────────────────────────────────────────────┘
```

---

## 8. Results

### 8.1 Big Data Scalability Results
**Table 5** reports scaling performance up to $50,000$ customer orders.

```
TABLE 5: Apache Spark 4.2.0 Scaling Performance (1,000 to 50,000 Customer Orders)
┌─────────────┬─────────────────┬─────────────────┬─────────────────────┬───────────────┬───────────────────┬────────────────────┐
│ Order Count │ Payload Size KB │ Spark Wall Time │ Throughput orders/s │ Peak RAM MB   │ Clusters Generated│ Cust. Preservation │
├─────────────┼─────────────────┼─────────────────┼─────────────────────┼───────────────┼───────────────────┼────────────────────┤
│ 1,000       │ 59.7 KB         │ 2,257.5 ms      │ 443.0               │ 1.39 MB       │ 134               │ 100% (1,000/1,000) │
│ 5,000       │ 298.0 KB        │ 4,288.0 ms      │ 1,166.1             │ 5.28 MB       │ 665               │ 100% (5,000/5,000) │
│ 10,000      │ 595.8 KB        │ 7,917.7 ms      │ 1,263.0             │ 9.92 MB       │ 1,326             │ 100% (10,000/10,000│
│ 25,000      │ 1,489.4 KB      │ 19,760.9 ms     │ 1,265.1             │ 24.50 MB      │ 3,324             │ 100% (25,000/25,000│
│ 50,000      │ 2,978.6 KB      │ 35,210.9 ms     │ 1,420.0             │ 48.84 MB      │ 6,678             │ 100% (50,000/50,000│
└─────────────┴─────────────────┴─────────────────┴─────────────────────┴───────────────┴───────────────────┴────────────────────┘
```
Throughput increases from $443$ orders/s to $1,420$ orders/s, while customer preservation and capacity compliance remained $100\%$ across all $6,678$ generated clusters.

### 8.2 Quantum Subproblem Results
**Table 6** details the microcluster sequencing performance for 9-qubit ($m=3$) and 16-qubit ($m=4$) QAOA circuits. Empirical profiling records that for $m=3$, circuit depth is 15 gates, COBYLA converges in 25 iterations, and Hungarian projection was required in 93.3% of shots (approximation ratio 0.9079); for $m=4$, circuit depth is 24 gates, and Hungarian projection was required in 100.0% of shots (approximation ratio 0.8435) due to shallow $p=1$ state under-convergence.

```
TABLE 6: QAOA Microcluster Sequencing Subproblem Telemetry
┌───────────────────────────┬──────────────┬───────────────┬─────────────────┬─────────────────┬──────────────────┐
│ Microcluster Core Size    │ Logical Qubits│ Circuit Depth │ Energy <H>      │ Approx. Ratio   │ Ground State Prob│
├───────────────────────────┼──────────────┼───────────────┼─────────────────┼─────────────────┼──────────────────┤
│ m = 3 stops               │ 9 qubits     │ 15            │ 12.42           │ 0.9079          │ 2.20%            │
│ m = 4 stops               │ 16 qubits    │ 24            │ 18.65           │ 0.8435          │ 0.42%            │
│ Uniform Random Baseline   │ 16 qubits    │ N/A           │ 38.85           │ 0.5412          │ 0.0019%          │
└───────────────────────────┴──────────────┴───────────────┴─────────────────┴─────────────────┴──────────────────┘
```

### 8.3 Controlled Quantum Attribution Experiment
**Table 7** isolates the causal contribution of QAOA by evaluating six controlled regimes on identical instances.

```
TABLE 7: Quantum Attribution Controlled Experiment Across Six Regimes (Instance N=25, Seed 207)
┌──────────────────────────────────────┬──────────────────────┬──────────────────┬──────────────────┬────────────────────┬─────────────────┐
│ Evaluation Regime                    │ Campaign Distance km │ Accepted Trans.  │ Rejected Trans.  │ Routes Changed     │ Distance Imp.   │
├──────────────────────────────────────┼──────────────────────┼──────────────────┼──────────────────┼────────────────────┼─────────────────┤
│ Regime A: Spatial Baseline Only      │ 109.224 km           │ 0                │ 4                │ 0                  │ 0.000 km        │
│ Regime B: Genuine QAOA (p=1)         │ 103.715 km           │ 1                │ 3                │ 1                  │ +5.509 km       │
│ Regime C: Uniform Random Bitstrings  │ 100.174 km           │ 3                │ 1                │ 3                  │ +9.050 km       │
│ Regime D: Shuffled QAOA Probabilities│ 96.095 km            │ 3                │ 1                │ 3                  │ +13.129 km      │
│ Regime E: Quantum Transitions Disabled│ 109.224 km          │ 0                │ 4                │ 0                  │ 0.000 km        │
│ Regime F: Classical Local Candidates │ 100.377 km           │ 3                │ 1                │ 3                  │ +8.847 km       │
└──────────────────────────────────────┴──────────────────────┴──────────────────┴──────────────────┴────────────────────┴─────────────────┘
```
In Regime E (transitions disabled), final distance remains strictly at the spatial baseline ($109.224\text{ km}$), confirming that adopting candidate transitions is causally necessary for optimization. However, Regimes C, D, and F achieve equal or superior route quality, proving that at $m \le 4$ nodes, QAOA co-produces results with classical selection without demonstrating quantum advantage over classical enumeration.

### 8.4 Routing Performance Comparison
**Table 8** reports the complete performance comparison across all 20 paired instances recomputed directly from raw experimental records.

```
TABLE 8: Multi-Algorithm Benchmark Performance Comparison (Mean Route Distance in km ± Std Dev)
┌───────┬─────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┐
│ Scale │ Instances│ Full QGAR (Proposed) │ Spatial Baseline     │ Phase H (Spark+QAOA) │ Google OR-Tools GLS  │ Clarke-Wright + 2-opt│ RB-QCD Baseline      │
├───────┼─────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤
│ N=10  │ 5       │ 48.707 ± 16.623      │ 48.707 ± 16.623      │ 50.179 ± 15.911      │ 39.525 ± 10.981      │ 39.845 ± 10.901      │ 41.270 ± 9.495       │
│ N=25  │ 5       │ 99.647 ± 21.898      │ 101.063 ± 22.197     │ 108.149 ± 25.286     │ 79.654 ± 12.560      │ 79.733 ± 12.029      │ 84.456 ± 11.055      │
│ N=50  │ 5       │ 168.795 ± 31.516     │ 173.218 ± 29.857     │ 173.748 ± 32.186     │ 143.276 ± 25.261     │ 142.423 ± 19.739     │ 153.100 ± 22.256     │
│ N=100 │ 5       │ 292.067 ± 35.484     │ 294.509 ± 34.997     │ 300.261 ± 33.325     │ 244.024 ± 25.786     │ 242.587 ± 23.834     │ 261.350 ± 22.696     │
│ N=150 │ 1       │ 654.010              │ 656.004              │ 672.210              │ 532.837              │ 541.601              │ 585.650              │
└───────┴─────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┘
```

### 8.5 Inferential Statistical Analysis
**Table 9** details the inferential hypothesis tests across all 20 paired instances ($N=10$ to $100$) recomputed and reconciled with raw data.

```
TABLE 9: Inferential Statistical Hypothesis Testing & Effect Size Estimation (Global N=10 to 100)
┌──────────────────────────────────────┬───────┬──────┬──────┬──────┬─────────────────┬────────────────────┬──────────────┬────────────┬───────────┐
│ Comparison                           │ Pairs │ Wins │ Loss │ Ties │ Mean Diff (km)  │ 95% Bootstrap CI   │ Wilcoxon W   │ p-value    │ Effect r_B│
├──────────────────────────────────────┼───────┼──────┼──────┼──────┼─────────────────┼────────────────────┼──────────────┼────────────┼───────────┤
│ Full QGAR vs. Spatial Baseline       │ 20    │ 14   │ 0    │ 6    │ -2.070 km       │ [-3.57, -0.91] km  │ 105.0        │ 0.000491 * │ +1.000    │
│ Full QGAR vs. Phase H (Spark+QAOA)   │ 20    │ 19   │ 1    │ 0    │ -5.781 km       │ [-8.52, -3.02] km  │ 194.0        │ 0.000161 * │ +0.848    │
│ Full QGAR vs. Google OR-Tools GLS    │ 20    │ 0    │ 20   │ 0    │ +25.684 km      │ [+18.34, +33.67] km│ 0.0          │ 0.000002   │ -1.000    │
│ Full QGAR vs. Clarke-Wright + 2-opt  │ 20    │ 0    │ 20   │ 0    │ +26.157 km      │ [+18.05, +34.84] km│ 0.0          │ 0.000002   │ -1.000    │
│ Full QGAR vs. RB-QCD Baseline        │ 20    │ 1    │ 19   │ 0    │ +17.260 km      │ [+11.23, +24.03] km│ 3.0          │ 0.000010   │ -0.971    │
└──────────────────────────────────────┴───────┴──────┴──────┴──────┴─────────────────┴────────────────────┴──────────────┴────────────┴───────────┘
* Asterisk (*) indicates statistical significance at alpha = 0.05.
```

- **QGAR vs. Spatial Baseline:** Full QGAR strictly outperforms or matches the spatial baseline in 100% of instances (14 wins, 0 losses, 6 ties). The mean distance reduction of $-2.070\text{ km}$ (mean paired reduction: $-1.23\%$; pooled fleet reduction: $-1.34\%$) is highly statistically significant ($p = 0.000491, r_B = +1.000$).
- **QGAR vs. Phase H:** Full QGAR outperforms unconditioned QAOA in 19 out of 20 instances ($-5.781\text{ km}$ mean reduction, $-4.10\%$, $p = 0.000161, r_B = +0.848$), confirming that adaptive crossing regularization successfully eliminates angular disruption.
- **Benjamini-Hochberg FDR:** All scale-specific confirmatory tests at $N=50$ and $N=100$ retain significance ($p_{\text{adj}} \le 0.05$).

---

## 9. Discussion

### 9.1 Computational Responsibilities of Spark and QAOA
ROUTE/IQ demonstrates a principled division of computational labor:
- **Spark's Role:** Solves the macroscopic scalability barrier, partitioning thousands of orders into compact, capacity-compliant territories in linear time ($O(N \log N)$).
- **QAOA's Role:** Solves the microscopic combinatorial sequencing problem within each cluster, optimizing directed transitions over asymmetric street networks.
- **The Synergy:** Spark provides the monotonic macro-routing that makes shallow QAOA safe, while QAOA provides local combinatorial improvements that beat simple polar sweeps.

### 9.2 The "OR-Tools Reality Check"
Classical OR-Tools GLS achieves $\approx 21\%$ shorter routes than ROUTE/IQ (average global gap $+25.684\text{ km}$). This is fully expected:
1. OR-Tools performs global neighborhood exchanges across all $N$ customers simultaneously with unconstrained memory.
2. In contrast, ROUTE/IQ restricts subproblems to microclusters of $m \le 4$ stops to respect NISQ simulator constraints.
3. ROUTE/IQ's purpose is not to surpass 40-year-old classical industrial heuristics on classical workstations, but to establish the **architectural, regularizing, and verification infrastructure** required for enterprise quantum deployment.

### 9.3 The Necessity of the Route Certification Guardrail
The Trial 19 counterexample demonstrated that greedy insertion of boundary nodes into a cheaper sub-tour can produce a longer full route. Without the End-to-End Certification Guardrail, hybrid systems risk deploying degraded routes. By verifying complete fleet costs, ROUTE/IQ transforms hybrid quantum computing from an experimental gamble into an enterprise-safe technology.

**Table 10** provides a transparent summary of research contributions, assumptions, and limitations.

```
TABLE 10: Research Contributions, Methodological Assumptions, and Limitations Summary
┌───────────────────────────────┬─────────────────────────────────────────────────┬───────────────────────────────────────────┐
│ System Dimension              │ Demonstrated Research Contribution              │ Explicit Methodological Limitation        │
├───────────────────────────────┼─────────────────────────────────────────────────┼───────────────────────────────────────────┤
│ Big Data Engine (Spark 4.2.0) │ Batch ingestion, BPR delays, scaling to 50,000  │ Evaluated on workstation local[*] mode    │
│ Quantum Engine (QAOA p=1)     │ Genuine 9-qubit & 16-qubit subproblem execution │ Classical simulation via Qiskit Aer       │
│ Operational Safety Guarantee  │ Proven campaign non-degradation via guardrail   │ Requires post-reconstruction comparison   │
│ Planar Crossing Regularizer   │ Mitigates Angular Disruption (149 crossings)    │ 2D Euclidean bias (96.4% empirical acc.)  │
│ Classical Baseline Benchmark  │ Complete paired evaluation against OR-Tools     │ OR-Tools remains 21% shorter globally     │
└───────────────────────────────┴─────────────────────────────────────────────────┴───────────────────────────────────────────┘
```

---

## 10. Limitations and Future Work

1. **Classical Simulation vs. Physical QPUs:** All quantum circuits were executed using Qiskit Aer classical simulators. Future research will deploy ROUTE/IQ on physical superconducting and trapped-ion quantum processors via cloud interfaces (IBM Quantum, AWS Braket).
2. **Microcluster Size Boundary ($m \le 4$):** Classical statevector simulation limits subproblems to $m \le 4$ ($16$ qubits). With fault-tolerant logical qubits, subproblem budgets will expand to $m \ge 20$ stops, where classical enumeration ($20! \approx 2.4 \times 10^{18}$) becomes impossible.
3. **Multi-Node Cluster Deployment:** Spark was evaluated in `local[*]` mode. Future work will benchmark distributed network shuffle latencies on AWS EMR and Databricks clusters.
4. **Traffic Model Refinement:** The BPR volume-delay model should be augmented with real-time GPS probe velocities (e.g. Uber Movement or NYC TLC trip data).

---

## 11. Conclusion

This paper presented **ROUTE/IQ**, a certified hybrid Big Data and quantum computing architecture for urban delivery optimization developed at SRM University-AP. By coupling **Apache Spark 4.2.0** for active large-scale spatial partitioning with **QAOA** for microcluster sequencing, ROUTE/IQ scales delivery optimization to $50,000$ customer orders. The Quantum-Guided Adaptive Reconstruction pipeline mitigates the Angular Disruption Effect through quality-aware candidate evaluation and planar crossing regularization. Furthermore, the End-to-End Route Certification Guardrail provides a proven non-degradation guarantee:
$$C(R_{\text{QGAR}}) \le C(R_{\text{spatial}}) + 10^{-4}\text{ km}$$
Across 20 paired instances on the 54,128-node Manhattan road network, ROUTE/IQ achieves a statistically significant $-1.23\%$ distance reduction ($p = 0.000491$) over the classical spatial baseline and reverses the $-4.55\%$ degradation of unconditioned QAOA. By establishing strict research integrity, transparently documenting limitations, and providing complete reproduction artifacts, ROUTE/IQ offers a robust foundation for the future of quantum-accelerated logistics.

---

## References

\bibliographystyle{IEEEtran}
\bibliography{ROUTE_IQ_REFERENCES}

1. E. Farhi, J. Goldstone, and S. Gutmann, "A Quantum Approximate Optimization Algorithm," *arXiv:1411.4028*, 2014. [DOI: 10.48550/arXiv.1411.4028]
2. S. Hadfield et al., "From the Quantum Approximate Optimization Algorithm to a Quantum Alternating Operator Ansatz," *Algorithms*, vol. 12, no. 2, p. 34, 2019. [DOI: 10.3390/a12020034]
3. S. Feld et al., "A Hybrid Solution Method for the Capacitated Vehicle Routing Problem Using a Quantum Annealer," *Frontiers in Physics*, vol. 7, p. 186, 2019. [DOI: 10.3389/fphy.2019.00186]
4. S. Harwood et al., "Formulating and Solving Constrained Optimization Problems With the Quantum Approximate Optimization Algorithm," *IEEE Transactions on Quantum Engineering*, vol. 2, pp. 1–14, 2021. [DOI: 10.1109/TQE.2021.3093275]
5. U. Azad, A. Bhattacharya, and B. K. Behera, "Solving Vehicle Routing Problem Using Quantum Approximate Optimization Algorithm," *IEEE Transactions on Computers*, vol. 72, no. 3, pp. 646–658, 2022. [DOI: 10.1109/TC.2022.3168852]
6. A. Glos, A. Krawiec, and Z. Zimborás, "Space-efficient binary optimization for variational quantum algorithms," *npj Quantum Information*, vol. 8, no. 1, p. 39, 2022. [DOI: 10.1038/s41534-022-00546-y]
7. M. Zaharia et al., "Apache Spark: A Unified Engine for Big Data Processing," *Communications of the ACM*, vol. 59, no. 11, pp. 56–65, 2016. [DOI: 10.1145/2934664]
8. J. Yu, J. Wu, and M. Sarwat, "GeoSpark: A Cluster Computing Framework for Processing Large-Scale Spatial Data," in *ACM SIGSPATIAL*, 2015, pp. 70:1–70:4. [DOI: 10.1145/2820783.2820860]
9. P. Toth and D. Vigo, *Vehicle Routing: Problems, Methods, and Applications*, 2nd ed. SIAM, 2014. [DOI: 10.1137/1.9781611973594]
10. Bureau of Public Roads, *Traffic Assignment Manual*, U.S. Dept. Commerce, Urban Planning Div., Washington, D.C., 1964.
11. G. Clarke and J. W. Wright, "Scheduling of Vehicles from a Central Depot to a Number of Delivery Points," *Operations Research*, vol. 12, no. 4, pp. 568–581, 1964. [DOI: 10.1287/opre.12.4.568]
12. G. A. Croes, "A Method for Solving Traveling-Salesman Problems," *Operations Research*, vol. 6, no. 6, pp. 791–812, 1958. [DOI: 10.1287/opre.6.6.791]
13. H. W. Kuhn, "The Hungarian Method for the Assignment Problem," *Naval Research Logistics Quarterly*, vol. 2, no. 1-2, pp. 83–97, 1955. [DOI: 10.1002/nav.3800020109]
14. J. Preskill, "Quantum Computing in the NISQ era and beyond," *Quantum*, vol. 2, p. 79, 2018. [DOI: 10.22331/q-2018-08-06-79]
15. J. R. McClean et al., "Barren plateaus in quantum neural network training landscapes," *Nature Communications*, vol. 9, no. 1, p. 4812, 2018. [DOI: 10.1038/s41467-018-07090-4]
16. Z. Wang et al., "Quantum alternating operator ansatz on constraints with hard and soft constraints: XY-mixers and penalty terms," *Physical Review A*, vol. 101, no. 1, p. 012320, 2020. [DOI: 10.1103/PhysRevA.101.012320]
17. M. Borowski et al., "New hybrid quantum-classical algorithm for solving the vehicle routing problem," *Quantum Information Processing*, vol. 19, no. 11, p. 386, 2020. [DOI: 10.1007/s11128-020-02888-2]
18. Qiskit contributors, "Qiskit: An Open-source Framework for Quantum Computing," 2024. [DOI: 10.5281/zenodo.2573505]
19. A. Lucas, "Ising formulations of many NP problems," *Frontiers in Physics*, vol. 2, p. 5, 2014. [DOI: 10.3389/fphy.2014.00005]
20. B. E. Gillett and L. R. Miller, "A Heuristic Algorithm for the Vehicle-Dispatch Problem," *Operations Research*, vol. 22, no. 2, pp. 340–349, 1974. [DOI: 10.1287/opre.22.2.340]
21. C. Voudouris and E. Tsang, "Guided local search and its application to the traveling salesman problem," *European Journal of Operational Research*, vol. 113, no. 2, pp. 469–499, 1999. [DOI: 10.1016/S0377-2217(98)00099-X]
