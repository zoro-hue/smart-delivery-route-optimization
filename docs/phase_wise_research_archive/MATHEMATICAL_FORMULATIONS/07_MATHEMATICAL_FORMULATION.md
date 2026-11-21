# 07 — MATHEMATICAL AND THEORETICAL FORMULATION

**Project:** ROUTE/IQ — Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing  
**Institution:** SRM University-AP, Department of Computer Science and Engineering  
**Authors:** J. Jayanth, B. Kaivalya, P. Shyam Sai  
**Faculty Supervisor:** Dr. Vishnu Prasad Verma (`vishnu.v@srmap.edu.in`)  
**Git Baseline Commit (`main`):** `a8eb849`  
**Current Research Branch:** `research/journal-readiness` (Commit: `960dfdb`)  
**Target Journal:** *IEEE Transactions on Quantum Engineering*  

---

## 1. Overview of Theoretical Framework

This document details the complete mathematical and physical formulation of the ROUTE/IQ framework, spanning graph-theoretic transportation modeling, big data spatial partitioning, quantum Hamiltonian mappings, and adaptive route certification. 

Every equation is presented alongside its formal definition, variable domain, and an intuitive plain-language explanation of its practical engineering purpose.

---

## 2. Transportation Graph & Empirical Traffic Impedance

### 2.1 Directed Road Network Graph
The physical urban street network is represented as a directed, weighted multigraph:

$$\mathcal{G} = (\mathcal{V}_{\text{road}}, \mathcal{E}_{\text{road}}, \mathcal{W})$$

Where:
- $\mathcal{V}_{\text{road}}$: Set of $N_V \approx 54,000$ road intersections and terminal nodes extracted from OpenStreetMap.
- $\mathcal{E}_{\text{road}} \subseteq \mathcal{V}_{\text{road}} \times \mathcal{V}_{\text{road}}$: Set of directed road segments representing one-way and two-way streets.
- $\mathcal{W}: \mathcal{E}_{\text{road}} \to \mathbb{R}^+$: Edge weight function assigning dynamic congested traversal times $\tau_e$.

*Plain-Language Explanation:* A realistic street network is not an open 2D plane; delivery vans must follow street directions, one-way avenues, and physical street connections. $\mathcal{G}$ models the actual road layout of New York City.

### 2.2 Calibrated Bureau of Public Roads (BPR) Impedance Model
To reflect real-world congestion without crude scalar approximations, the traversal time $\tau_e$ on road link $e \in \mathcal{E}_{\text{road}}$ is determined by the calibrated BPR volume-delay equation:

$$\tau_e = \tau_{e,0} \left[ 1 + \alpha \left( \frac{V_e}{C_e} \right)^\beta \right]$$

Where:
- $\tau_{e,0} = \frac{L_e}{v_{\text{free}}}$: Free-flow travel time, computed from segment length $L_e$ (meters) and posted speed limit $v_{\text{free}}$ (km/h).
- $V_e$: Empirical vehicular traffic volume count observed on segment $e$ (vehicles per hour), derived from NYC DOT sensor telemetry.
- $C_e$: Practical road carrying capacity, calibrated at $1,000 \times \text{lanes}_e$ vehicles per hour.
- $\alpha = 0.15$: Standard BPR coefficient governing the onset of congestion delay.
- $\beta = 4.0$: Calibrated power exponent modeling the sharp non-linear increase in travel delay as traffic volume approaches capacity ($V/C \to 1$).

*Plain-Language Explanation:* When a street has little traffic ($V_e \ll C_e$), a van drives at the speed limit ($\tau_{e,0}$). When the street becomes congested ($V_e \approx C_e$), travel time spikes sharply to the 4th power, penalizing heavily congested corridors.

---

## 3. Global Capacitated Vehicle Routing Problem (CVRP)

Let $\mathcal{C} = \{1, 2, \dots, N\}$ denote the set of customer delivery locations, and let index $0$ denote the central depot hub. The delivery fleet consists of $K$ homogeneous vehicles, each with maximum payload capacity $Q$. Each customer $i \in \mathcal{C}$ has a non-negative parcel demand $q_i \ge 0$.

Let binary decision variable $x_{i,j,k} \in \{0, 1\}$ equal 1 if vehicle $k$ traverses directly from stop $i$ to stop $j$:

### 3.1 Objective Function (Total Fleet Cost Minimization)
$$\min \sum_{k=1}^K \sum_{i=0}^N \sum_{j=0}^N d_{i,j} \cdot x_{i,j,k}$$

Where $d_{i,j}$ represents the shortest-path travel distance between stops $i$ and $j$ on the road graph $\mathcal{G}$ computed via Dijkstra's algorithm.

### 3.2 Problem Constraints
1. **Customer Visit Degree Constraint:** Every customer is visited exactly once by exactly one vehicle:
   $$\sum_{k=1}^K \sum_{j=0, j \neq i}^N x_{i,j,k} = 1 \quad \forall i \in \mathcal{C}$$

2. **Flow Conservation:** If a vehicle enters stop $j$, it must depart from stop $j$:
   $$\sum_{i=0, i \neq j}^N x_{i,j,k} - \sum_{l=0, l \neq j}^N x_{j,l,k} = 0 \quad \forall j \in \{0\} \cup \mathcal{C}, \quad \forall k \in \{1, \dots, K\}$$

3. **Vehicle Capacity Limit:** Total parcel demand on vehicle $k$ cannot exceed capacity $Q$:
   $$\sum_{i \in \mathcal{C}} q_i \left( \sum_{j=0, j \neq i}^N x_{i,j,k} \right) \le Q \quad \forall k \in \{1, \dots, K\}$$

4. **Depot Depot Departure and Return:** Every vehicle starts and finishes at depot $0$:
   $$\sum_{j=1}^N x_{0,j,k} \le 1 \quad \text{and} \quad \sum_{i=1}^N x_{i,0,k} \le 1 \quad \forall k \in \{1, \dots, K\}$$

---

## 4. Pillar 1: Distributed Polar Sweep Partitioning

To partition $N$ delivery stops across $K$ vehicles in $O(N \log N)$ distributed time, Apache Spark transforms customer coordinates into polar coordinates relative to origin depot $(x_0, y_0)$:

### 4.1 Coordinate Projection and Angular Mapping
$$\Delta x_i = (lon_i - lon_0) \cdot \cos\left( \frac{lat_0 \cdot \pi}{180} \right), \quad \Delta y_i = lat_i - lat_0$$

$$\theta_i = \text{atan2}(\Delta y_i, \Delta x_i) \in [-\pi, \pi]$$

*Plain-Language Explanation:* Maps all customer GPS points onto an angular circular clock face centered on the warehouse depot.

### 4.2 Catalyst Windowed Cumulative Demand & Binning
Customers are sorted in ascending polar angle order: $\theta_{(1)} \le \theta_{(2)} \le \dots \le \theta_{(N)}$. Spark computes the cumulative demand using a Catalyst Window function:

$$\text{cum\_demand}_{(i)} = \sum_{j=1}^i q_{(j)}$$

Vehicle cluster assignment is determined by integer division:

$$\text{cluster\_id}_{(i)} = \left\lfloor \frac{\text{cum\_demand}_{(i)} - 1}{Q} \right\rfloor$$

*Plain-Language Explanation:* Sweeps a radar arm around the depot. As customer parcels are accumulated along the sweep, as soon as the total weight fills a vehicle's capacity $Q$, the vehicle is sealed and the next vehicle begins.

---

## 5. Pillar 2: Micro-Cluster QAOA & Hamiltonian Formulation

Within each partitioned cluster, Spark extracts micro-clusters of $m \le 4$ stops ($m^2 \le 16$ qubits) for variational quantum sequencing.

### 5.1 Asymmetric Traveling Salesperson Problem (ATSP)
Let $x_{i,p} \in \{0, 1\}$ indicate whether stop $i \in \{0, \dots, m-1\}$ is visited at position $p \in \{0, \dots, m-1\}$:

$$H_C^{\text{classical}} = \sum_{i=0}^{m-1} \sum_{j=0}^{m-1} \sum_{p=0}^{m-1} d_{i,j} \cdot x_{i,p} \cdot x_{j,(p+1) \pmod m}$$

### 5.2 Mapping Binary Variables to Quantum Pauli-Z Spins
Using the mapping $x_{i,p} = \frac{I - Z_{i,p}}{2}$, the product of two binary variables becomes:

$$x_{i,p} x_{j,p+1} = \frac{1}{4} \left( I - Z_{i,p} - Z_{j,p+1} + Z_{i,p} Z_{j,p+1} \right)$$

Substituting into the classical cost function yields the 2-local Ising Cost Hamiltonian:

$$\hat{H}_C = \sum_{i,j,p} \frac{d_{i,j}}{4} \left( Z_{i,p} Z_{j,p+1} - Z_{i,p} - Z_{j,p+1} \right) + \text{constant}$$

Where $Z_{i,p}$ is the Pauli-$Z$ operator acting on the logical qubit corresponding to customer $i$ at position $p$.

### 5.3 Particle-Conserving XY Mixer Hamiltonian
To prevent the quantum circuit from exploring non-permutation states ($\sum_p x_{i,p} \neq 1$), ROUTE/IQ uses an $XY$ mixer Hamiltonian:

$$\hat{H}_M = \frac{1}{2} \sum_{i=0}^{m-1} \sum_{p=0}^{m-2} \left( X_{i,p} X_{i,p+1} + Y_{i,p} Y_{i,p+1} \right)$$

In Qiskit Aer, the unitary evolution operator $e^{-i \beta \hat{H}_M}$ is synthesized via native `XXPlusYYGate` operations:

$$\text{XXPlusYYGate}(2\beta) = \exp\left( -i \beta (X \otimes X + Y \otimes Y) \right)$$

*Physical Property:* The commutator $[\hat{H}_M, \sum_p x_{i,p}] = 0$. Consequently, the mixer strictly preserves the total Hamming weight of each position partition, keeping the quantum state inside the valid permutation subspace.

### 5.4 Exact Binary Slack Capacity Formulation
For vehicle assignment problems, inequality constraints $\sum_i q_i x_{i,k} \le Q_k$ are encoded using exact binary slack variables:

$$\sum_{i=1}^n q_i x_{i,k} + \sum_{b=0}^{B-1} 2^b s_{k,b} = Q_k, \quad \text{where } B = \lceil \log_2(Q_k + 1) \rceil$$

This introduces penalty Hamiltonian:

$$\hat{H}_{\text{capacity}} = \lambda \sum_{k=1}^K \left( \sum_{i=1}^n q_i x_{i,k} + \sum_{b=0}^{B-1} 2^b s_{k,b} - Q_k \right)^2$$

Because slack variables represent integer slack exactly, no penalty parameter fine-tuning is required.

---

## 6. QGAR Bridge: Candidate Quality & Geometric Regularization

### 6.1 Boltzmann Quality-Aware Candidate Weighting
Given measurement distribution $\{\mathbf{b}_c\}$ with counts $N_c$ and evaluated energies $E_c = \langle \mathbf{b}_c | \hat{H}_C | \mathbf{b}_c \rangle$:

$$w_c = \frac{e^{-\Delta E_c / T}}{\sum_{j} e^{-\Delta E_j / T}}, \quad \text{where } \Delta E_c = E_c - \min_j E_j$$

Here $T$ represents the empirical variance of the energy spectrum. High-energy, sub-optimal bitstrings receive exponentially lower weights regardless of their measurement frequency.

### 6.2 Planar Crossing Elimination Condition
Two directed segments $S_1 = (p_1, p_2)$ and $S_2 = (p_3, p_4)$ intersect in 2D space if and only if their 2D cross-product orientation determinants alternate signs:

$$\text{orient}(A, B, C) = (B_x - A_x)(C_y - A_y) - (B_y - A_y)(C_x - A_x)$$

$$\text{Intersect}(S_1, S_2) \iff \begin{cases} 
\text{orient}(p_1, p_2, p_3) \cdot \text{orient}(p_1, p_2, p_4) < 0 \\ 
\quad \text{and} \\ 
\text{orient}(p_3, p_4, p_1) \cdot \text{orient}(p_3, p_4, p_2) < 0 
\end{cases}$$

When $\text{Intersect}(S_1, S_2) = \text{True}$, a 2-opt edge inversion is evaluated.

---

## 7. Proposition 1: Monotonic Non-Degradation Guarantee

### Mathematical Statement
Let $R_{\text{QGAR}}$ denote the fleet route generated by the hybrid QGAR pipeline, and let $R_{\text{spatial}}$ denote the deterministic spatial baseline route constructed on identical order partitions. Then:

$$C(R_{\text{final}}) \le C(R_{\text{spatial}}) + 10^{-4}\text{ km}$$

### Proof by Construction (Architectural Guardrail)
1. Let $C(R) = \sum_{k=1}^K \text{Length}(R_k)$ denote the scalar cost function measuring total fleet travel distance on road graph $\mathcal{G}$.
2. In `backend/app/services/optimization/qgar_pipeline.py`, the final fleet solution $R_{\text{final}}$ is defined by the decision rule:
   $$R_{\text{final}} = \begin{cases} 
   R_{\text{QGAR}} & \text{if } C(R_{\text{QGAR}}) \le C(R_{\text{spatial}}) + \epsilon \\ 
   R_{\text{spatial}} & \text{otherwise} 
   \end{cases}$$
   Where numerical comparison tolerance $\epsilon = 10^{-4}\text{ km}$.
3. Case 1: If $C(R_{\text{QGAR}}) \le C(R_{\text{spatial}}) + \epsilon$, then $R_{\text{final}} = R_{\text{QGAR}}$, and the condition holds trivially.
4. Case 2: If $C(R_{\text{QGAR}}) > C(R_{\text{spatial}}) + \epsilon$, then $R_{\text{final}} = R_{\text{spatial}}$, and $C(R_{\text{final}}) = C(R_{\text{spatial}}) \le C(R_{\text{spatial}}) + \epsilon$.
5. Therefore, $C(R_{\text{final}}) \le C(R_{\text{spatial}}) + \epsilon$ holds universally across all problem instances, graph topologies, and circuit noise realizations. $\blacksquare$

*Practical Significance:* This theorem establishes that ROUTE/IQ can safely incorporate experimental quantum variational heuristics into production logistics workflows without risking fleet route degradation.
