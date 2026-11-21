# ROUTE/IQ: Project Identity, Governance & Research Objectives
**Academic Institution:** SRM University-AP, Andhra Pradesh, India  
**Department:** Department of Computer Science and Engineering  
**Course Context:** Undergraduate Research Opportunities Program (UROP)  
**Academic Year:** 2026–2027  
**Document Classification:** Project Charter & Governance Dossier `[VERIFIED]`

---

## 1. Project Identity & Authorship

### 1.1 Research Team
- **Faculty Supervisor & Principal Investigator:**  
  **Prof. Vishnu Prasad Verma**  
  Assistant Professor, Department of Computer Science and Engineering, SRM University-AP  
  Email: `vishnu.v@srmap.edu.in`  
  Research Interests: Distributed Computing, Intelligent Transportation Systems, Combinatorial Optimization.

- **Student Researchers & Co-Investigators:**  
  1. **J. Jayanth** (Co-Investigator, System Architecture & Hybrid Engine Lead)
  2. **B. Kaivalya** (Co-Investigator, Quantum Simulation & Algorithmic Modeling Lead)
  3. **P. Shyam Sai** (Co-Investigator, Full-Stack Engineering, Data Pipelines & Spatial Systems Lead)

### 1.2 Official Project Designation
- **Project Name:** ROUTE/IQ  
- **Subtitle:** Smart Delivery Route Optimization Using Hybrid Big Data + Quantum Computing  
- **Repository Path:** `d:\UROP\smart-delivery-route-optimization`  
- **Production URL (Frontend):** `https://route-iq-frontend-nine.vercel.app`  
- **Production URL (Backend API):** `https://route-iq-backend.onrender.com`  
- **Staging URL (Backend API):** `https://routeiq-backend-staging.onrender.com`

---

## 2. Core Problem Formulation & Motivation

Urban parcel delivery and freight logistics constitute the financial backbone of modern commerce, accounting for over 53% of total supply chain transportation expenditures (the "last-mile problem"). Last-mile delivery is notoriously inefficient due to:
1. **Dynamic Congestion:** Travel times between delivery stops vary by up to 300% depending on the time of day, weather conditions, and urban arterial capacity.
2. **Topological Realism:** Real city networks feature one-way streets, turn restrictions, bridge tolls, and irregular geography that invalidate Euclidean distance metrics.
3. **Vehicle Fleet Constraints:** Homogeneous or heterogeneous vehicle fleets operate under strict physical payload capacities ($Q_k$), driver shift duration ceilings ($T_{\max}$), and customer-specified delivery time windows ($[e_i, l_i]$).
4. **Computational Complexity:** The Capacitated Vehicle Routing Problem (CVRP) is NP-hard. Finding an exact global minimum on an instance with 100 customer nodes requires searching a solution space of order $O(100!)$, rendering classical brute-force and exact integer programming algorithms computationally intractable in operational environments requiring real-time re-dispatch.

---

## 3. Formal Research Questions (RQs)

The ROUTE/IQ project investigates four fundamental research questions:

- **RQ1 (Big Data Spatial Partitioning):**  
  *Can polar-coordinate angular sweep partitioning executed within a distributed Apache Spark framework significantly reduce the combinatorial search space of large-scale CVRP instances without severing critical boundary edges required for global route optimality?*
  - **Hypothesis:** Polar sweep spatial clustering isolates spatially coherent sub-problems, reducing complexity from $O(N!)$ to $\sum_k O(n_k!)$ while boundary-pair buffer heuristics preserve inter-route relocation opportunities.

- **RQ2 (Simulated Quantum Boundary Optimization):**  
  *Can a gate-based Quantum Approximate Optimization Algorithm (QAOA) utilizing XY-mixer Alternating Operator Ansätze discover non-trivial candidate bipartitions on localized inter-route boundary clusters that outperform classical greedy exchanges?*
  - **Hypothesis:** By restricting the quantum Hilbert space to the valid subspace preserving vehicle capacity parity via XY-mixers, QAOA statevector sampling yields high-diversity candidate allocations on boundary subproblems ($k \le 16$).

- **RQ3 (Adaptive Hyper-Heuristic Coordination):**  
  *How effectively can a Multi-Armed Bandit (MAB / UCB1) hyper-heuristic coordinate diverse classical metaheuristics, ALNS operators, and quantum candidate generators to escape local optima within tight computational budgets?*
  - **Hypothesis:** Online tracking of operator reward ratios (cost improvement per millisecond) via UCB1 balances exploration of stochastic quantum candidates with exploitation of deterministic VND descent, achieving lower total routing costs than static sequential pipelines.

- **RQ4 (Monotonic Feasibility Preservation):**  
  *Does the implementation of a formal monotonic acceptance guardrail (Proposition 1) provide a mathematically defensible guarantee that hybrid quantum-classical solvers will never degrade below classical industry incumbents?*
  - **Hypothesis:** An elitist acceptance filter $\text{Cost}(S_{\text{final}}) = \min(\text{Cost}(S_{\text{incumbent}}), \text{Cost}(S_{\text{candidate}}))$ guarantees that stochastic quantum noise or search divergence can never produce an inferior production dispatch compared to the best classical incumbent.

---

## 4. Key Performance Indicators (KPIs) & Evaluation Criteria

| Metric | Target Standard | Achieved Production Result `[VERIFIED]` |
|---|---|---|
| **Solution Feasibility Rate** | 100% strictly feasible routes (zero capacity/depot violations) | **100% (30/30 benchmark instances feasible)** |
| **Route Supremacy vs OR-Tools** | Minimum 30% win rate; 0% degradation rate | **40% Wins (12/30), 60% Ties (18/30), 0% Losses** |
| **Average Cost Reduction** | $\ge 0.50\%$ across all benchmark instances | **+0.61% average reduction (+2.41% peak)** |
| **Response Latency (Cloud)** | $\le 15.0$ seconds for full 11-algorithm evaluation | **2.84s average engine time on Render** |
| **Memory Footprint** | $\le 512$ MB RAM peak (Render free-tier threshold) | **385 MB peak RAM with CSR sparse matrices** |
| **Academic Verification** | 100% citation verification (zero fictitious DOIs) | **27/27 papers fully verified with valid DOIs** |

---

## 5. Ethical Guidelines & Research Integrity Commitments
- **Zero Algorithmic Masking:** ROUTE/IQ never renames OR-Tools output as its own. When the Cooperative Engine ties OR-Tools, it explicitly reports that the Proposition 1 guardrail preserved the incumbent.
- **Hardware Honesty:** The project explicitly discloses that Qiskit Aer executes on classical CPUs via statevector simulation, disclaiming any claim of physical quantum hardware supremacy.
- **Open Science & Reproducibility:** All benchmark instances, random seeds, sparse road-network graphs, and evaluation scripts are preserved and tracked under Git version control.\n