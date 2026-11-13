# ROUTE/IQ: COMPREHENSIVE VIVA VOCE DEFENSE & EXAMINER GUIDE

**Project:** Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing  
**Institution:** SRM University-AP, Amaravati, Andhra Pradesh  
**Supervisor:** Dr. Vishnu Prasad Verma  
**Team:** J. Jayanth, B. Kaivalya, P. Shyam Sai  
**Scope:** 38 Rigorous Technical and Critical Questions for Oral Defense  

---

## Category 1: Vehicle Routing Foundations & Complexity (Questions 1–6)

### Q1: Why is the Capacitated Vehicle Routing Problem (CVRP) computationally difficult?
**Answer:** CVRP is strongly NP-hard. It generalizes the Traveling Salesperson Problem (TSP) by adding vehicle capacity constraints and multiple vehicle tours. The solution space scales factorially $O(N!)$ with customer count $N$, and partitioning $N$ customers among $K$ capacitated vehicles involves Stirling numbers of the second kind, causing exact branch-and-cut algorithms to face combinatorial explosion beyond several hundred stops.

### Q2: How does CVRP differ mathematically from the standard Traveling Salesperson Problem (TSP)?
**Answer:** A standard TSP seeks a single Hamiltonian cycle visiting all $N$ vertices at minimum cost. CVRP seeks $K$ distinct cycles originating and terminating at a single depot such that every customer vertex is visited exactly once by exactly one vehicle, and the sum of demands $\sum_{i \in T_k} d_i \le Q_{\text{veh}}$ along every tour $k$ does not exceed vehicle capacity $Q_{\text{veh}}$.

### Q3: What is the difference between asymmetric and symmetric vehicle routing?
**Answer:** In symmetric routing, distance $D_{ij} = D_{ji}$ is identical in both travel directions. In asymmetric routing (common in urban environments with one-way streets, divided highways, and turn restrictions), $D_{ij} \ne D_{ji}$. Asymmetric matrices invalidate standard 2-opt segment reversals unless paths are re-evaluated in the directed forward orientation.

### Q4: Why can't exact solvers like integer linear programming (ILP) solve metropolitan-scale CVRP?
**Answer:** Exact ILP formulations (e.g., two-index or three-index vehicle flow formulations) require exponential numbers of subtour elimination constraints ($2^N - 2$). At metropolitan scale ($N = 100,000$ deliveries), the linear programming relaxation matrix exceeds terabytes of memory, making exact resolution impossible within enterprise planning deadlines.

### Q5: What is the Clarke-Wright Savings heuristic, and what are its limitations?
**Answer:** Clarke-Wright begins with $N$ individual back-and-forth routes $(0 \to i \to 0)$. It iteratively merges tours based on computed distance savings $s_{ij} = D_{i,0} + D_{0,j} - D_{ij}$ whenever capacity permits. Its limitation is that it is a greedy, one-pass constructive heuristic that makes irreversible early merge decisions, resulting in suboptimal crossing routes.

### Q6: What is a spatial decomposition heuristic in fleet logistics?
**Answer:** Spatial decomposition divides a large geographical delivery region into smaller, manageable subproblems. Standard methods include polar angle sweeping, $k$-means centroid clustering, and Voronoi tessellation. Each cluster is then solved as an independent single-vehicle TSP.

---

## Category 2: Big Data Processing & Apache Spark (Questions 7–12)

### Q7: Why is Apache Spark needed in ROUTE/IQ if classical solvers optimize the routes?
**Answer:** Classical optimization solvers cannot ingest, clean, and compute pairwise distances for $N = 100,000$ raw telematics GPS points without running out of memory. Apache Spark provides distributed, in-memory Resilient Distributed Datasets (RDDs) and DataFrames that parallelize spatial polar projections and cluster filtering across worker cores, reducing 100,000 deliveries to 16 boundary customers in 3.37 seconds (a 99.984% reduction).

### Q8: *Critical Examiner Question:* If NumPy is faster than PySpark on a single machine, why use Spark at all?
**Answer:** On a single machine, in-memory NumPy is indeed faster ($54.01\text{ ms}$ vs $3,375.05\text{ ms}$ at 100,000 stops) because PySpark incurs JVM-to-Python IPC serialization overhead via py4j. However, NumPy is bounded by single-machine physical RAM. Apache Spark is architecturally necessary for horizontal out-of-core scaling when order volumes exceed hundreds of thousands of records, allowing the workload to be partitioned across distributed worker nodes.

### Q9: What exact Spark DataFrame transformations were used in Pillar 1?
**Answer:** We used PySpark SQL functions including `withColumn`, `atan2` (for polar angles from the depot), `sqrt` and arithmetic expressions (for Euclidean centroid distances $D_{i,A}$ and $D_{i,B}$), `abs` (for difference computation $|D_{i,A} - D_{i,B}|$), `filter` (for threshold filtering), and `limit(16)` coupled with `collect()` to extract the boundary subproblem.

### Q10: Was Spark executed on a physical multi-node cluster?
**Answer:** No. As established during our independent Phase AC audit, the experiments were executed using PySpark 4.2.0 in `local[*]` multi-threaded mode on a single multicore host. While a containerized Docker Compose cluster configuration was designed and committed, physical multi-node execution was not performed, and we explicitly qualify our results as single-machine parallel processing.

### Q11: How were the 16 boundary customers selected from the 100,000 stops?
**Answer:** Spark computes the spatial centroid of each adjacent vehicle wedge. For every customer stop, it evaluates distance difference $|D_{i,A} - D_{i,B}|$. Customers with the smallest difference lie along the ambiguous border between vehicles. The top 16 stops with differences below the spatial threshold ($\delta = 0.035^\circ \approx 3.8\text{ km}$) are extracted for combinatorial bipartitioning.

### Q12: Did the Spark boundary reduction discard any delivery constraints?
**Answer:** No. Customer demands, vehicle capacities, and depot locations are fully preserved. Customers deep inside vehicle territories remain assigned to their respective vehicles. Only the ambiguous boundary interface is extracted, meaning optimizing the subproblem strictly optimizes the complete fleet.

---

## Category 3: Quantum Computing & QAOA (Questions 13–18)

### Q13: What is QAOA, and how does it solve combinatorial problems?
**Answer:** The Quantum Approximate Optimization Algorithm (QAOA) is a hybrid variational algorithm for gate-model quantum computers. It maps a combinatorial optimization problem to an Ising Hamiltonian $\hat{H}_C$. It prepares a parameterized state $|\psi(\vec{\gamma}, \vec{\beta})\rangle = \prod_{l=1}^p e^{-i \beta_l \hat{H}_M} e^{-i \gamma_l \hat{H}_C} |\psi_0\rangle$ by alternating problem phase separations with mixer Hamiltonians, and optimizes the variational parameters $(\vec{\gamma}, \vec{\beta})$ to maximize the expectation value $\langle \psi | -\hat{H}_C | \psi \rangle$.

### Q14: How is customer bipartitioning mapped to a Quadratic Unconstrained Binary Optimization (QUBO) problem?
**Answer:** Each customer $i$ is assigned a spin variable $s_i \in \{-1, +1\}$ ($+1$ for Vehicle A, $-1$ for Vehicle B). Spatial affinity between customer pairs $(i, j)$ is encoded as quadratic coupling $J_{ij} = \frac{5.0}{D_{ij} + 0.5}$. Depot affinity is encoded as linear field $h_i$. Capacity balance is enforced via penalty $\lambda_{\text{cap}} (\sum_i d_i s_i - \Delta Q)^2$. Expanding this yields an Ising QUBO matrix $Q_{ij} s_i s_j$.

### Q15: What is the difference between a Transverse Mixer and a Subspace XY-Mixer?
**Answer:** A Transverse Mixer ($\hat{H}_M = \sum_i \hat{X}_i$) applies single-qubit bit-flips, exploring the entire unconstrained $2^N$ Hilbert state space. An XY-Mixer ($\hat{H}_M = \sum_{(i,j)} (\hat{X}_i \hat{X}_j + \hat{Y}_i \hat{Y}_j)$) performs pairwise particle swaps $(|01\rangle \leftrightarrow |10\rangle)$, conserving the total number of 1s (Hamming weight). In our experiments, the XY-Mixer raised initial capacity compliance from 41.2% to 89.5%.

### Q16: Was any physical quantum processor (QPU) executed in this project?
**Answer:** No. All QAOA experiments were executed via classical CPU statevector simulation using Qiskit 2.4.1. Hardware circuits were transpiled to IBM Heavy-Hex coupling graphs with basis gates $\{CZ, \sqrt{X}, X, RZ\}$, but no physical QPU jobs were submitted. We report this openly and honestly.

### Q17: *Critical Examiner Question:* If classical algorithms outperform QAOA, what is the quantum contribution?
**Answer:** The quantum contribution is the formulation, circuit construction, and empirical boundary mapping of QAOA as an exploratory candidate generator within an adaptive portfolio. While QAOA does not achieve an overall advantage on 16-qubit subproblems ($p = 0.1020$), it won 16.7% to 21.7% of individual instances where spatial interaction curvature was high. Our research establishes a realistic scientific baseline that disproves false claims of quantum supremacy while defining where quantum candidate generation can integrate into modern pipelines.

### Q18: Why is QAOA statevector simulation limited to $N \le 16$ qubits?
**Answer:** A statevector of $N$ qubits requires storing $2^N$ complex amplitudes ($\mathbb{C}^{2^N}$). At $N = 16$, the vector requires $2^{16} = 65,536$ elements ($1\text{ MB}$). At $N = 30$, it requires 16 gigabytes. At $N = 50$, it exceeds available global supercomputer memory. Hence, classical simulation on standard workstations is fundamentally bounded around 16–20 qubits.

---

## Category 4: Classical Optimization & Local Search (Questions 19–24)

### Q19: What is Variable Neighborhood Descent (VND), and how does it work in ROUTE/IQ?
**Answer:** VND is a deterministic local search framework that systematically shifts between multiple neighborhood operators. In ROUTE/IQ, VND sequences four neighborhoods: (1) Intra-route 2-Opt, (2) Inter-route Relocate, (3) Inter-route Swap, and (4) Inter-route Cross-Exchange. Whenever an improving move is accepted, the algorithm restarts at Neighborhood 1. It terminates only when a local optimum is reached across all 4 neighborhoods.

### Q20: What was the impact of Algorithmic VND on initial greedy routing?
**Answer:** Applying Algorithmic VND to initial greedy routes cut fleet travel distance from **1,307.16 km to 621.45 km (-52.46% / 685.71 km cut)** in just $8.27\text{ ms}$. This proved that VND is the single most powerful optimization component in the entire pipeline.

### Q21: How does Tabu Search prevent getting trapped in local minima?
**Answer:** Tabu Search maintains a recency memory matrix (tabu list) that forbids reversing recent customer moves for $T$ iterations ($T = 7$). This forces the search to explore uphill and lateral moves across objective plateaus. It also incorporates an aspiration criterion that overrides tabu status if a forbidden move produces a new global best solution.

### Q22: What is Multistart Kernighan-Lin (MS-KL)?
**Answer:** Kernighan-Lin is an $O(N^2)$ greedy graph bipartitioning heuristic that computes cumulative swap gains. Single-pass KL is deterministic and easily trapped in shallow local minima. Multistart KL executes 32 independent KL trajectories initiated from randomized feasible initial assignments, harvesting diverse partition cuts.

### Q23: Why did Tabu Search achieve the best standalone performance (595.45 km)?
**Answer:** Tabu Search evaluates structured 1-swap and 2-swap neighborhoods guided by its recency memory. Unlike QAOA (which optimizes an unsequenced Ising proxy) and Uniform Random (which samples aimlessly), Tabu Search systematically explores adjacent feasible partitions without cycling, generating high-quality candidates that VND can polish effectively.

### Q24: What is nearest-neighbor tour reconstruction, and why is it needed?
**Answer:** Partitioning algorithms (QAOA, Tabu, KL) only divide customers into two sets $S_A$ and $S_B$; they do not determine the travel sequence. Nearest-neighbor tour reconstruction begins at the depot ($0$), greedily visits the closest unvisited customer in the set, and returns to the depot. This converts a set bipartition into valid cyclic vehicle routes $(0 \to \pi(1) \to \dots \to 0)$.

---

## Category 5: Proposition 1 & Acceptance Guardrail (Questions 25–29)

### Q25: What is Proposition 1, and what does it mathematically guarantee?
**Answer:** Proposition 1 is a centralized acceptance guardrail stating that a candidate route $R_{\text{cand}}$ produced by any solver is adopted if and only if it satisfies customer coverage, vehicle capacity, and achieves a strictly lower post-VND distance than the incumbent: $C(\mathcal{V}(R_{\text{cand}})) < C(\mathcal{V}(R_{\text{inc}})) - \epsilon$. Otherwise, the incumbent is retained unconditionally. It mathematically guarantees 100% capacity feasibility and 0.00% complete-route degradation.

### Q26: Does Proposition 1 guarantee optimal fleet routes?
**Answer:** No. Proposition 1 is a **monotonicity and feasibility guarantee**, not an optimality proof. It guarantees that the route will never degrade ($C(R_{\text{final}}) \le C(R_{\text{inc}})$) and will never violate capacity, but it does not claim to find the global minimum of the NP-hard CVRP.

### Q27: How was Proposition 1 validated against adversarial edge cases?
**Answer:** In Phase AC, we constructed 11 adversarial tests covering: exact capacity boundaries, slight overages, empty vehicle partitions, singleton partitions, missing customer IDs, duplicate customer IDs, out-of-bounds indices, asymmetric directed costs, infinite road edges, net fleet degradation, and floating-point precision drift. Proposition 1 passed all 11 tests with 0 bypasses and 0 failures.

### Q28: Why were 70% of QAOA candidate bipartitions rejected by Proposition 1?
**Answer:** QAOA optimizes a discrete 1D Ising Hamiltonian where spatial affinity is represented by pairwise scalar penalties. It has no intrinsic knowledge of continuous 2D Euclidean geometry, tour sequencing, or directional edge crossings. Consequently, many low-energy Ising cuts result in twisted, crossed tours that have higher post-VND distance than the incumbent, triggering immediate rejection by Proposition 1.

### Q29: Can a candidate improve one vehicle while degrading the fleet overall?
**Answer:** Yes, this is a common failure mode in multi-vehicle routing. However, Proposition 1 explicitly evaluates the combined two-vehicle fleet cost $C = \text{Cost}(T_A) + \text{Cost}(T_B)$. If Vehicle A improves by 5 km but Vehicle B degrades by 12 km (net $+7\text{ km}$ degradation), Proposition 1 rejects the candidate and retains the incumbent.

---

## Category 6: Adaptive Controller & Experimental Audit (Questions 30–34)

### Q30: How does the Adaptive Cooperative Controller work?
**Answer:** It functions as a Multi-Armed Bandit with feature-conditioned gating. It evaluates five upfront features: subproblem size $N$, capacity slack $\sigma$, interaction density $\rho$, stagnation counter $S_{\text{count}}$, and remaining budget $T_{\text{rem}}$. Based on these features, it routes the subproblem to Tabu Search, Multistart KL, Uniform Random, or QAOA.

### Q31: Was there any data leakage in the Adaptive Controller?
**Answer:** No. Our Phase AC audit confirmed zero data leakage. All five features are extracted strictly from instance metadata (coordinates, demands, capacities, and elapsed time) before optimization begins. None of the features contain post-optimization distances or candidate tour lengths.

### Q32: *Critical Examiner Question:* In Phase AB, the controller dispatch was reported as 19 Tabu / 1 QAOA, but Phase AC found 26 Tabu / 0 QAOA in the CSV. Why?
**Answer:** In Phase AB's 30-instance benchmark, demands and capacities were generated such that capacity slack was constant ($\sigma \approx 0.10 \le 0.15$). In the controller's decision tree, slack below 0.15 channels execution to the default branch (Tabu Search). In Phase AB's report, narrative text reflected preliminary exploratory runs with variable slack. Phase AC audited the actual committed CSV and corrected the record to 26 Tabu, 2 MSKL, 2 Random, and 0 QAOA. When tested on variable-slack held-out instances in Phase AC, the controller dispatched Tabu (46.7%), Random (30.0%), QAOA (20.0%), and MSKL (3.3%).

### Q33: What was the "OR-Tools Baseline Artifact" uncovered in Phase AC?
**Answer:** In Phase AB, `generate_ortools_incumbent()` in `classical_engine.py` was labeled as OR-Tools, but its code was actually a sequential list slice (`ta = 1..half`, `tb = half+1..N`). This caused an inflated baseline distance of 1,307.16 km and an artificially low latency of 0.04 ms. Phase AC corrected this: Config A is labeled "Trivial Sequential Incumbent", and Config B (OR-Tools + VND: 621.45 km) is established as the true classical baseline.

### Q34: What statistical tests were used to evaluate configuration differences?
**Answer:** We computed paired two-tailed Student's t-tests, non-parametric Wilcoxon signed-rank tests, and paired Cohen's $d$ effect sizes ($d_{\text{paired}} = \bar{D} / s_D$) across all 30 paired problem instances. Configs C through H achieved statistically significant improvements over Config B ($p < 0.01$). Differences between QAOA and classical metaheuristics were statistically insignificant ($p > 0.05$).

---

## Category 7: Software Integration & Threats to Validity (Questions 35–38)

### Q35: Is the Phase AB/AC Cooperative Engine deployed in the live website?
**Answer:** No. The live FastAPI backend (`backend/app/main.py`) exposes baseline classical VRP, basic Qiskit transpilation, and QIGA. The Cooperative Engine is a self-contained research package located in `phase_ab_cooperative_optimization_engine/`. This deliberate decoupling preserved the protected `main` branch (`a8eb849`) and ensured zero breaking regressions in the production API.

### Q36: *Critical Examiner Question:* What is genuinely novel in this research?
**Answer:** The genuine novelty is three-fold:
1. **The Dual-Pillar Division of Labor:** Demonstrating that Apache Spark can reduce a 100,000-delivery metropolitan problem by 99.984% into an isolated boundary subproblem suitable for small quantum circuits or metaheuristics.
2. **Proposition 1 Centralized Guardrail:** The mathematical proof and verified implementation of an incumbent-preserving filter that neutralizes quantum infeasibility and guarantees 0% fleet degradation.
3. **Rigorous Equal-Budget Causal Mapping:** Providing an honest, reproducible benchmark that establishes where quantum algorithms currently stand relative to strong classical search under equal evaluation budgets.

### Q37: What are the primary threats to validity in this study?
**Answer:**
1. *Construct Validity:* Testing on classical CPU simulation rather than physical noisy QPUs.
2. *Internal Validity:* Single-machine Spark `local[*]` execution rather than a physical multi-node cluster.
3. *External Validity:* Using uniform 2D Euclidean coordinates rather than real-world road networks with live traffic congestion and turn penalties.

### Q38: If you had another 6 months of funding, what would be the immediate next step?
**Answer:** First, obtain IBM Quantum Cloud credits to execute the transpiled Heavy-Hex circuits on physical 127-qubit IBM Eagle QPUs to measure noise degradation. Second, deploy the Spark preprocessor on an AWS EMR multi-node cluster. Third, integrate OpenStreetMap road distance matrices into Algorithmic VND.
