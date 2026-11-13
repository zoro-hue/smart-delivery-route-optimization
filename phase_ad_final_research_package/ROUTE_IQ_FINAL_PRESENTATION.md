# ROUTE/IQ: FINAL UROP RESEARCH PRESENTATION

**Slide Deck:** 15-Slide Master Presentation  
**Project:** Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing  
**Institution:** SRM University-AP, Amaravati, Andhra Pradesh  
**Supervisor:** Dr. Vishnu Prasad Verma  
**Team:** J. Jayanth, B. Kaivalya, P. Shyam Sai  

---

## Slide 1: Title & Research Team

### Slide Content:
- **Project Title:** ROUTE/IQ: A Cooperative Hybrid Architecture for Scalable Vehicle Routing via Apache Spark and Quantum Approximate Optimization
- **Program:** Undergraduate Research Opportunity Program (UROP)
- **Institution:** Department of Computer Science and Engineering, SRM University-AP
- **Student Researchers:** J. Jayanth, B. Kaivalya, P. Shyam Sai
- **Faculty Supervisor:** Dr. Vishnu Prasad Verma

> **Speaker Notes:**  
> "Good morning, respected committee members and supervisor. Today, we present ROUTE/IQ, our final UROP research project investigating how distributed Big Data processing and Quantum Approximate Optimization can cooperatively address metropolitan-scale vehicle routing."

---

## Slide 2: Problem Statement

### Slide Content:
- **Core Challenge:** Capacitated Vehicle Routing Problem (CVRP) is NP-hard.
- **Enterprise Scale:** Metropolitan package distribution ($N \ge 100,000$ deliveries, hundreds of vehicles).
- **Exact Solvers Infeasible:** Integer programming branch-and-cut suffers combinatorial explosion beyond $N \approx 500$.
- **Boundary Defect:** Spatial decomposition heuristics isolate geographical sectors, but trap customers along cluster boundaries in suboptimal vehicle routes.

> **Speaker Notes:**  
> "CVRP is the core mathematical problem behind urban package logistics. Exact classical algorithms cannot scale to metropolitan sizes. While heuristic clustering divides cities into sectors, boundary customers between adjacent vehicle zones are frequently assigned suboptimally, inflating fleet mileage."

---

## 3. Slide 3: Research Motivation

### Slide Content:
- **The Quantum Promise:** Quantum Approximate Optimization Algorithm (QAOA) offers non-local Hilbert space search via quantum tunneling.
- **The NISQ Bottleneck:** Current QPUs cannot solve monolithic CVRP ($O(K \cdot N^2)$ variables require millions of qubits).
- **The Research Question:** Can we build a hybrid division of labor where Big Data handles macroscopic decomposition, Quantum/Classical solvers optimize high-leverage boundary cuts, and a mathematical guardrail guarantees fleet feasibility?

> **Speaker Notes:**  
> "We recognized that monolithic quantum routing is impossible on NISQ hardware. Our motivation was to discover a realistic division of labor: let Apache Spark process the massive big data volume, let simulated QAOA and classical metaheuristics optimize small, ambiguous boundary interfaces, and enforce a mathematical guardrail so the system never degrades."

---

## Slide 4: Key Objectives & Contributions

### Slide Content:
1. **Dual-Pillar Framework:** Unified Apache Spark 4.2.0 with Qiskit 2.4.1 QAOA.
2. **Workload Reduction:** Reduced 100,000 deliveries to 16 boundary customers in 3.37 seconds (99.984% reduction).
3. **Proposition 1 Guardrail:** Mathematical proof and verified filter guaranteeing 100% feasibility and 0% degradation.
4. **Adaptive Controller:** Multi-Armed Bandit with feature-conditioned gating achieving 597.44 km in 34.87 ms.
5. **Scientific Rigor:** 100% deterministically reproducible benchmark across 240 evaluations; honest reporting of negative quantum results.

> **Speaker Notes:**  
> "Our contributions are fivefold: a dual-pillar architecture, a 99.984% Big Data reduction factor, a mathematically proven non-degradation guardrail, an intelligent adaptive controller, and an uncompromising commitment to reproducible, honest science."

---

## Slide 5: System Architecture

### Slide Content:
- **Four Cooperative Tiers:**
  1. *Big Data Tier (Apache Spark):* Ingestion, cleaning, polar wedge clustering.
  2. *Adaptive Controller (MAB):* Feature extraction and solver dispatch.
  3. *Candidate Generators:* Tabu Search, Multistart KL, Uniform Random, Fast QAOA.
  4. *Safety Guardrail:* Algorithmic VND refinement and Proposition 1 acceptance.
- *(Suggested Diagram: See `ARCHITECTURE_DIAGRAMS.md` — Diagram 1)*

> **Speaker Notes:**  
> "This diagram illustrates the ROUTE/IQ workflow. Data flows from Spark's distributed preprocessor, through the Adaptive Controller, into candidate generators, and finally into the Proposition 1 Guardrail. Crucially, the research engine is cleanly decoupled from the production API, preserving system stability."

---

## Slide 6: Big Data & Apache Spark Methodology (Pillar 1)

### Slide Content:
- **High-Throughput Ingestion:** Schema validation, deduplication, demand clamping.
- **Polar Wedge Decomposition:** Centroid angle calculation: $\theta_i = \text{atan2}(y_i - y_{\text{depot}}, x_i - x_{\text{depot}})$.
- **Boundary Filter:** Isolates stops where centroid distance difference $|D_{i,A} - D_{i,B}| < \delta$.
- **Subproblem Output:** Ambiguous 16-customer boundary bipartition ($N \le 16$).
- *(Suggested Diagram: See `ARCHITECTURE_DIAGRAMS.md` — Diagram 2)*

> **Speaker Notes:**  
> "In Pillar 1, Spark ingests raw coordinates, calculates polar angles, and clusters orders into vehicle wedges. It then identifies stops on the border between adjacent vehicles. Out of 100,000 deliveries, only 16 customers need combinatorial re-evaluation, preventing combinatorial explosion."

---

## Slide 7: Quantum Computing & QAOA Methodology (Pillar 2)

### Slide Content:
- **QUBO Mapping:** Formulates bipartition as an Ising Hamiltonian with capacity penalty:
  $$\hat{H}_C = \sum_{i < j} J_{ij} \hat{Z}_i \hat{Z}_j + \sum_i h_i \hat{Z}_i + \lambda (\sum d_i \hat{Z}_i - \Delta Q)^2$$
- **Mixers Tested:**
  - *Transverse Mixer:* Unconstrained Hilbert space exploration.
  - *Subspace XY-Mixer:* Conserves Hamming weight, boosting capacity feasibility to 89.5%.
- **Execution Mode:** Classical CPU statevector simulation (Qiskit 2.4.1); transpilation to IBM Heavy-Hex coupling graphs.
- *(Suggested Diagram: See `ARCHITECTURE_DIAGRAMS.md` — Diagram 3)*

> **Speaker Notes:**  
> "Pillar 2 maps the boundary subproblem to an Ising Hamiltonian. We implemented both transverse and subspace XY-mixers. We simulated the parameterized quantum circuits on classical CPUs, and transpiled them for IBM Heavy-Hex quantum hardware."

---

## Slide 8: Classical Optimization Components

### Slide Content:
- **OR-Tools Constraint Programming:** Initial incumbent route generation.
- **Metaheuristic Generators:**
  - *Tabu Search:* 7-tenure recency memory matrix prevents reverse swaps.
  - *Multistart KL:* 32 random-start greedy exchange trajectories.
  - *Uniform Random:* 512 feasible bitstring samples.
- **Algorithmic VND:** 4 deterministic neighborhoods (Intra 2-Opt, Inter Relocate, Inter Swap, Inter Cross-Exchange).
- **Impact:** Initial VND cuts greedy routes from 1,307.16 km to 621.45 km (-52.46%) in 8.27 ms.

> **Speaker Notes:**  
> "Classical algorithms provide both the initial routes and local search polish. Algorithmic VND systematically searches four topological neighborhoods. As our results show, initial VND cuts greedy route distances by over 52% in just 8 milliseconds."

---

## Slide 9: Cooperative Workflow & Proposition 1 Guardrail

### Slide Content:
- **Proposition 1 Statement:**
  $$C(R_{\text{final}}) = \min(C(\mathcal{V}(R_{\text{inc}})), C(\mathcal{V}(R_{\text{cand}})))$$
  Subject to strict customer coverage and vehicle capacity invariance.
- **Fail-Safe Mechanism:**
  - If candidate violates capacity $\to$ Rejected.
  - If candidate omits/duplicates stops $\to$ Rejected.
  - If candidate degrades distance $\to$ Rejected.
- **Result:** Monotonic improvement guaranteed across all subproblems.

> **Speaker Notes:**  
> "Proposition 1 is our central mathematical guardrail. Any candidate produced by quantum simulation or metaheuristics must pass coverage, capacity, and cost tests. If a candidate degrades the route or violates payload limits, the incumbent is retained unconditionally. Feasibility is 100% guaranteed."

---

## Slide 10: Experimental Setup & Benchmark Suite

### Slide Content:
- **Test Matrix:** 30 diverse problem instances, 8 configurations (240 evaluations).
- **Strict Budget Equality:** All generators operate with $B = 512$ evaluations.
- **Standard Downstream Processing:** Identical tour reconstruction, VND, and guardrail filtering.
- **Configurations Evaluated:**
  - *Config A:* Trivial Sequential Incumbent | *Config B:* OR-Tools + VND
  - *Config C:* KL Single + VND | *Config D:* Tabu Search + VND
  - *Config E:* Random 512 + VND | *Config F:* Fast QAOA + VND
  - *Config G:* Adaptive Controller + VND | *Config H:* Spark Unified Engine

> **Speaker Notes:**  
> "To prevent experimental bias, we enforced strict evaluation budget equality: every candidate generator evaluates exactly 512 candidates. All solutions pass through the exact same reconstruction, VND, and guardrail. We tested 8 configurations across 30 instances."

---

## Slide 11: Complete System Benchmark Results

### Slide Content:

| Configuration | Fleet Distance (km) | Latency (ms) | Accepted % | Statistical $p$-value vs B |
| :--- | :---: | :---: | :---: | :---: |
| **Config A (Sequential)** | 1,307.16 | 0.04 | Baseline | N/A |
| **Config B (OR-Tools + VND)** | 621.45 | 8.27 | Baseline | Baseline |
| **Config C (KL Single)** | 603.72 | 19.90 | 46.7% | $p = 0.0010$ |
| **Config D (Tabu Search)** | **595.45** | **33.85** | **60.0%** | $p = 0.0001$ |
| **Config E (Random 512)** | 602.90 | 53.00 | 46.7% | $p = 0.0032$ |
| **Config F (Fast QAOA)** | 606.36 | 644.85 | 30.0% | $p = 0.0080$ |
| **Config G (Adaptive Controller)**| **597.44** | **34.87** | **63.3%** | $p = 0.00003$ |
| **Config H (Spark Unified)** | 599.68 | 504.00* | 60.0% | $p = 0.00007$ |

> **Speaker Notes:**  
> "Here are the headline results. Tabu Search achieved the best absolute distance (595.45 km). The Adaptive Controller achieved 597.44 km with the highest acceptance rate (63.3%) in only 34.87 ms. Fast QAOA achieved 606.36 km, trailing Tabu Search by nearly 11 km while running 19 times slower."

---

## Slide 12: Quantum Findings & Scientific Integrity

### Slide Content:
- **No Empirical Quantum Advantage:**
  - Fast QAOA vs Tabu Search: $\Delta = +10.91\text{ km}$ ($p = 0.1020$, statistically insignificant).
  - Head-to-Head: Tabu won 14 instances, tied 10, QAOA won only 6.
- **High Quantum Rejection Rate:**
  - 21 of 30 QAOA candidates (70.0%) were rejected by Proposition 1 due to route degradation.
- **Simulation Overhead:**
  - Simulated QAOA is $19.05\times$ slower than Tabu Search on classical CPUs.
- **Scientific Takeaway:** The hybrid pipeline's strength originates from VND and Proposition 1, not quantum coherence.

> **Speaker Notes:**  
> "A core strength of our UROP research is scientific honesty. We proved that simulated QAOA offers no quantum advantage over strong classical search on these subproblems. 70% of QAOA candidates were rejected by the guardrail. Claiming quantum superiority would be scientifically false."

---

## Slide 13: Big Data Spark Scalability Findings

### Slide Content:
- **Scalability Range:** Tested from $N = 1,000$ to $100,000$ delivery stops.
- **Massive Problem Reduction:**
  - 100,000 deliveries $\to$ 16 boundary customers in 3.37 seconds (99.984% reduction).
- **Semantic Equivalence:** Spark and in-memory NumPy extracted 100% identical boundary customer sets.
- **Hardware Qualification:**
  - Evaluated on single-machine multi-threaded `local[*]`, not a multi-node physical cluster.
  - In-memory NumPy is faster on a single machine; Spark's true value is scaling beyond single-node RAM limits.

> **Speaker Notes:**  
> "Our Spark scalability benchmark proved that Big Data spatial decomposition works: 100,000 orders are reduced to 16 boundary customers in under 4 seconds. We qualify this honestly: tests ran on single-machine local mode, where NumPy has lower overhead, while Spark provides out-of-core scalability."

---

## Slide 14: Limitations & Future Research

### Slide Content:
- **Current Limitations:**
  - Classical statevector simulation limited to $N \le 16$ qubits.
  - Physical quantum processors (QPUs) were not executed.
  - Synthetic spatial coordinates used rather than real road network graphs.
  - Research engine decoupled from production FastAPI application.
- **Future Research Directions:**
  - Deploy transpiled Heavy-Hex circuits on physical IBM 127-qubit QPUs.
  - Deploy Spark across physical multi-node clusters.
  - Integrate live OpenStreetMap distance matrices into Algorithmic VND.

> **Speaker Notes:**  
> "We explicitly acknowledge our limitations: simulation was limited to 16 qubits, physical QPUs were not run, and tests were conducted on synthetic coordinates. Future work will submit these circuits to physical IBM QPUs and integrate real road network APIs."

---

## Slide 15: Conclusion & Q&A

### Slide Content:
- **Summary of Achievements:**
  - Built and verified the ROUTE/IQ cooperative optimization engine.
  - Proved that Big Data + Classical Search drives practical routing performance.
  - Formulated and verified Proposition 1 non-degradation guardrail (100% feasible).
  - Maintained 100% reproducible science across 57 passing test cases.
- **Thank You!**
- **Questions & Discussion Welcome.**

> **Speaker Notes:**  
> "In conclusion, ROUTE/IQ proves that practical quantum-classical hybrid architectures must be built on robust Big Data decomposition and rigorous classical guardrails. Thank you for your time and guidance. We now welcome questions from the committee."
