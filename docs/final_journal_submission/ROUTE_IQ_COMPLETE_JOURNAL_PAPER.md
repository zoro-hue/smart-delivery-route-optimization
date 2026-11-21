# ROUTE/IQ-NextGen: An Adaptive, Vehicle-Condition-Aware Cooperative Optimization Engine for Heterogeneous Urban Logistics

**J. Jayanth, B. Kaivalya, and P. Shyam Sai**  
*Undergraduate Research Scholars, Department of Computer Science and Engineering, SRM University-AP, Amaravati, Andhra Pradesh, India*  

**Faculty Research Supervisor: Dr. Vishnu Prasad Verma**  
*Department of Computer Science and Engineering, SRM University-AP, Amaravati, Andhra Pradesh, India*  

**Target Publication:** IEEE Transactions on Intelligent Transportation Systems  
**Date:** November 21, 2026  
**Open-Source Repository:** [https://github.com/zoro-hue/smart-delivery-route-optimization](https://github.com/zoro-hue/smart-delivery-route-optimization)  

---

## Abstract
Urban last-mile logistics increasingly relies on mixed commercial fleets composed of battery electric vehicles (BEVs), internal combustion engine (ICE) vans, and hybrid powertrains. However, standard vehicle routing formulations assume uniform nominal capacities and idealized operating ranges, failing to account for real-world physical vehicle conditions such as battery State of Health (SoH) capacity degradation, dynamic State of Charge (SoC), and maintenance wear. Furthermore, while hybrid metaheuristics and variational quantum algorithms (e.g., Quantum Approximate Optimization Algorithm, QAOA) have been proposed, existing hybrid routing systems are typically configured as unidirectional linear pipelines or isolated candidate comparisons without genuine algorithmic cooperation, bidirectional candidate exchange, or online learning.

To address these fundamental challenges, this paper presents **ROUTE/IQ-NextGen**, an adaptive, vehicle-condition-aware cooperative optimization framework. The engine organizes multiple optimization paradigms—including Apache Spark spatial partitioning, simulated QAOA variational boundary cuts, Quantum-Inspired Genetic Algorithm (QIGA) rotation gates, Tabu Search, Deep Variable Neighborhood Descent (VND), and Google OR-Tools—around a shared, diversity-managed candidate blackboard. The framework introduces four primary research contributions: (1) an explicit **Heterogeneous Fleet Vehicle Condition (HFVRP-VC)** formulation that bounds routes by usable battery energy ($E = B_{	ext{nom}} \cdot 	ext{SoH} \cdot 	ext{SoC}$) and enforces multi-objective trade-offs across distance, operating cost, energy, and carbon emissions; (2) a **Topological Edge Jaccard Diversity Metric** that prevents candidate pool stagnation; (3) an **Adaptive Contextual Multi-Armed Bandit (MAB)** controller with Upper Confidence Bound (UCB-1) learning and a multi-objective feedback reward penalizing execution runtime while rewarding feasibility and diversity; and (4) a proven **Conditional Non-Degradation Guardrail (Proposition 1)** guaranteeing by construction that final fleet distance never exceeds the classical OR-Tools baseline.

Empirically validated on real-world New York City delivery networks across scales $N \in [12, 30]$ with heterogeneous vehicle fleets, ROUTE/IQ-NextGen achieves a mean distance reduction of **$-1.24\%$** over Google OR-Tools alone (reaching **$-3.16\%$** on $N=30$ nodes), while reducing mean execution latency by **$24.0\%$** ($1219.2	ext{ ms}$ vs $1604.0	ext{ ms}$) compared to legacy cooperative architectures through adaptive operator selection. Ablation experiments confirm that shared candidate exchange contributes a $1.07\%$ distance improvement over isolated waterfall execution, while QIGA and QAOA operators generate high topological diversity ($\mathcal{D} = 0.41	ext{--}0.61$). All quantum circuits are simulated classically via Qiskit Aer, with zero claims of physical quantum supremacy.

**Keywords:** Cooperative optimization, heterogeneous fleet vehicle routing, vehicle condition awareness, battery degradation, contextual multi-armed bandit, QAOA, QIGA, Apache Spark.

---

## 1. Introduction
Urban freight transportation and last-mile delivery operations are currently undergoing two simultaneous structural transformations: rapid fleet electrification and algorithmic digitization. As commercial logistics operators transition toward decarbonized operations, real-world delivery fleets have become deeply heterogeneous, comprising battery electric vehicles (BEVs), conventional diesel cargo vans, and hybrid powertrains.

Crucially, in operational settings, vehicles cannot be treated as nominal identical entities. A battery electric van with a 90% State of Health (SoH) and an 80% State of Charge (SoC) has a fundamentally different usable operating range than a brand-new diesel vehicle. Dispatching an electric delivery vehicle without accounting for electrochemical degradation and current charge levels leads to mid-route battery depletion, driver strandings, and schedule disruptions. Furthermore, mechanical wear on delivery vehicles due to neglected maintenance increases fuel consumption, elevates breakdown risk, and invalidates standard static routing plans.

Simultaneously, the combinatorial optimization community has investigated hybrid metaheuristics and quantum approximate optimization algorithms to tackle the NP-hard Capacitated Vehicle Routing Problem (CVRP). However, our forensic audit of existing hybrid literature reveals three pervasive structural deficiencies:
1. **Pseudo-Cooperation:** Most proposed "cooperative" engines merely run algorithms independently and compare their final outputs, or execute a rigid, unidirectional pipeline ($A 	o B 	o C$). There is no persistent shared candidate population, no cross-algorithm exchange, and no mechanism allowing one solver to iteratively improve a candidate generated by another paradigm.
2. **Isolated Quantum Toy Problems:** Quantum routing literature focuses almost exclusively on tiny symmetric graphs ($N \le 8$ nodes) with zero connection to enterprise Big Data pipelines or practical fleet management constraints.
3. **Vehicle Condition Obliviousness:** Existing routing algorithms optimize pure spatial distance under rigid, uniform vehicle capacity assumptions, ignoring vehicle-specific powertrain costs, energy consumption, and maintenance degradation.

To overcome these barriers, this paper presents **ROUTE/IQ-NextGen**, an adaptive, vehicle-condition-aware cooperative optimization framework. Rather than running solvers in isolation, ROUTE/IQ-NextGen orchestrates seven heterogeneous operators—Apache Spark polar sweeps, Google OR-Tools, simulated QAOA variational boundary cuts, Quantum-Inspired Genetic Algorithm (QIGA) rotation gates, Tabu Search, Deep Variable Neighborhood Descent (VND), and Guided Local Search—around a shared candidate pool blackboard.

---

## 2. Related Work and Literature Review
To establish the theoretical and algorithmic foundations of ROUTE/IQ-NextGen, we systematically reviewed 27 pivotal research papers across four foundational domains:
1. **Classical Vehicle Routing & Heuristics:** Toth and Vigo (2014) established canonical CVRP/VRPTW branch-and-cut formulations; Clarke and Wright (1964) designed the edge-savings greedy heuristic; Croes (1958) formulated 2-opt edge inversion; Kuhn (1955) proved exact Hungarian bipartite assignment; Gillett and Miller (1974) proposed polar sweep clustering; Glover (1986) formulated Tabu Search with recency/frequency memory; Voudouris and Tsang (1999) developed Guided Local Search; Hansen and Mladenovic (2001) unified Variable Neighborhood Search/Descent (VND); and the Bureau of Public Roads (BPR, 1964) established the standard volume-delay congestion function.
2. **Big Data & Spatial Analytics:** Zaharia et al. (2016) created Apache Spark with Resilient Distributed Datasets (RDDs); Yu et al. (2015) extended Spark into GeoSpark with spatial partitioning trees.
3. **Quantum Optimization in NISQ:** Farhi et al. (2014) formulated QAOA; Hadfield et al. (2019) introduced the Quantum Alternating Operator Ansatz; Feld et al. (2019) and Borowski et al. (2020) demonstrated hybrid classical-quantum clustering for CVRP; Harwood et al. (2021) analyzed QAOA constraint penalties; Azad et al. (2022) mapped small VRP instances ($N \le 8$) to QAOA; Glos et al. (2022) developed space-efficient binary encodings; Lucas (2014) cataloged NP Ising formulations; Preskill (2018) defined NISQ boundaries; McClean et al. (2018) identified quantum barren plateaus; and Qiskit Contributors (2024) developed the open-source Aer execution engine.
4. **Cooperative Search & Adaptive Control:** Auer et al. (2002) proved logarithmic regret bounds for UCB-1 Multi-Armed Bandits; Toulouse and Crainic (2004) formalized cooperative blackboard search; Talbi (2009) established hybrid metaheuristic taxonomies; and Burke et al. (2013) surveyed hyper-heuristic search frameworks.

---

## 3. Mathematical Formulation: HFVRP-VC
We formalize the Heterogeneous Fleet Vehicle Routing Problem with Vehicle Condition (HFVRP-VC) on a directed graph $\mathcal{G} = (\mathcal{V}, \mathcal{E})$. Customer stops $\mathcal{V}_c = \{1, \dots, N\}$ possess payload demands $q_i > 0$.

### Physical Vehicle Condition Equations
Each vehicle $k \in \mathcal{K}$ possesses physical condition telemetry $\mathbf{p}_k$. Usable battery capacity and maximum operating range are given by:
$$B_{	ext{usable}, k} = B_{	ext{nom}, k} \cdot \left(rac{	ext{SoH}_k}{100}ight) \quad (	ext{kWh})$$
$$R_k = egin{cases} 
\dfrac{B_{	ext{usable}, k} \cdot (	ext{SoC}_k / 100)}{\mu_k \cdot f_k} 	imes 100 & 	ext{if } \phi_k = 	ext{BEV} \[2ex]
\dfrac{V_{	ext{nom}, k} \cdot (	ext{FuelLevel}_k / 100)}{\mu_k \cdot f_k} 	imes 100 & 	ext{if } \phi_k \in \{	ext{Diesel}, 	ext{Petrol}\}
\end{cases} \quad (	ext{km})$$
where $\mu_k = 1.15$ applies a 15% wear penalty when maintenance is overdue.

### Multi-Objective Formulation
Let $x_{ijk} \in \{0, 1\}$ be arc traversal decision variables. The scalarized multi-objective objective is:
$$\min \quad \mathcal{F}(\mathbf{x}) = lpha_1 rac{\mathcal{D}(\mathbf{x})}{\mathcal{D}_0} + lpha_2 rac{\mathcal{C}(\mathbf{x})}{\mathcal{C}_0} + lpha_3 rac{\mathcal{E}(\mathbf{x})}{\mathcal{E}_0} + lpha_4 rac{\mathcal{M}(\mathbf{x})}{\mathcal{M}_0}$$
balancing total distance $\mathcal{D}(\mathbf{x})$, operational cost $\mathcal{C}(\mathbf{x})$, energy $\mathcal{E}(\mathbf{x})$, and carbon emissions $\mathcal{M}(\mathbf{x})$.

---

## 4. System Architecture and Candidate Blackboard
ROUTE/IQ-NextGen organizes all solver execution around a centralized candidate blackboard ($\mathcal{P}_t$, capacity $M=16$). 

### Topological Jaccard Diversity Metric
To prevent genetic collapse and premature stagnation, the distance between any two candidates $S_a, S_b$ is computed as:
$$	ext{Dist}(S_a, S_b) = 1 - rac{|\mathcal{E}(S_a) \cap \mathcal{E}(S_b)|}{|\mathcal{E}(S_a) \cup \mathcal{E}(S_b)|}$$
$$	ext{Diversity}(S, \mathcal{P}) = rac{1}{|\mathcal{P}|} \sum_{S' \in \mathcal{P}} 	ext{Dist}(S, S')$$
Candidates with $	ext{Dist} < 10^{-4}$ are automatically rejected as redundant. The top $k_{	ext{elite}} = 4$ solutions are strictly preserved across generations.

---

## 5. Contextual MAB Controller and Operators
At each cooperative iteration $t$, the Adaptive Controller observes state $\mathbf{s}_t = (N, K, H, \mathcal{D}_t, \sigma_t)$ and selects operator $o_t \in \mathcal{O}$ using UCB-1:
$$	ext{Score}(o, \mathbf{s}_t) = Q_t(o) + c \sqrt{rac{\ln(t + 1)}{N_t(o) + 1}} + \Psi(o, \mathbf{s}_t)$$

### 4-Pillar Multi-Objective Feedback Reward
$$R(o) = w_1 \Delta_{	ext{norm}} + w_2 \mathbb{I}_{	ext{feas}} + w_3 	ext{Div}(S_{	ext{new}}, \mathcal{P}_t) - w_4 \left(rac{t_{	ext{exec}}}{t_{	ext{budget}}}ight)$$
with weights $w_1 = 0.50, w_2 = 0.25, w_3 = 0.20, w_4 = 0.05$. This explicitly penalizes computationally slow operators while rewarding feasibility and structural diversity.

### Simulated QAOA Subproblem Operator
Extracts up to $K_{	ext{sub}} \le 8$ adjacent route boundary stops and formulates a 2-route partitioning QUBO Hamiltonian $H_C = \sum h_i Z_i + \sum J_{ij} Z_i Z_j$. Variational depth $p=1$ statevectors are simulated on classical CPU via Qiskit Aer, followed by classical 2-opt post-tour reconstruction.

### QIGA Rotation Gate Operator
Represents customer stop assignments as quantum probability vectors $|\psi_iangle = lpha_{i0}|0angle + lpha_{i1}|1angle$ and applies dynamic rotation gates $U(\Delta 	heta)$ directed toward the elite incumbent candidate.

---

## 6. Theoretical Guarantee: Proposition 1
**Proposition 1 (Conditional Non-Degradation Guardrail).** *Let $S_{	ext{ortools}}$ be the initial feasible solution generated by Google OR-Tools. Let $S_{	ext{final}}$ be the output produced by ROUTE/IQ-NextGen. Under identical distance matrix $\mathbf{D}$ and fleet constraints:*
$$\mathcal{D}(S_{	ext{final}}) \le \mathcal{D}(S_{	ext{ortools}}) + \epsilon_{	ext{float}} \quad (\epsilon_{	ext{float}} \le 10^{-4}	ext{ km})$$

*Proof:* By construction, $S_{	ext{baseline}} = 	ext{deepcopy}(S_{	ext{ortools}})$ is cached at $t=0$. In Stage 5, the guardrail identifies the minimum-distance candidate $S^* = rg\min_{S \in \mathcal{P}_T \cup \{S_{	ext{baseline}}\}} \mathcal{D}(S)$. If $\mathcal{D}(S^*) \le \mathcal{D}(S_{	ext{baseline}}) + \epsilon_{	ext{float}}$, the candidate $S^*$ is returned. If $\mathcal{D}(S^*) > \mathcal{D}(S_{	ext{baseline}}) + \epsilon_{	ext{float}}$, the engine executes a deterministic fail-safe fallback: $S_{	ext{final}} \leftarrow S_{	ext{baseline}}$. Thus, $\mathcal{D}(S_{	ext{final}}) \le \mathcal{D}(S_{	ext{ortools}}) + \epsilon_{	ext{float}}$ holds unconditionally across all executions. $lacksquare$

---

## 7. Empirical Results and Discussion
Across 6 benchmark instances evaluated on real-world NYC delivery networks with mixed fleets:
- **Routing Distance:** ROUTE/IQ-NextGen achieved a mean fleet distance of **179.31 km**, yielding a **$-1.24\%$** reduction over Google OR-Tools alone (181.57 km). On the $N=30$ node instance, Next-Gen attained **250.76 km** versus **258.95 km** for OR-Tools, achieving a **$-3.16\%$** reduction.
- **Computational Latency:** Legacy cooperative architectures required $1604.0	ext{ ms}$; ROUTE/IQ-NextGen reduced mean runtime to **1219.2 ms**, representing an execution latency reduction of **$24.0\%$**.
- **Ablation Significance:** Removing the candidate pool blackboard degraded distance by **+1.09%**, proving that shared candidate exchange is the primary mechanism driving cooperative improvement.

---

## 8. Limitations and Honest Scientific Disclosures
1. **Classical Simulation of Quantum Circuits:** All QAOA circuits were simulated classically using Qiskit Aer on CPU. We make zero claims of physical quantum advantage.
2. **Small-Instance Dominance:** For $N \le 15$ delivery stops, Google OR-Tools alone discovers the optimal solution in $< 150	ext{ ms}$, rendering cooperative co-evolution unnecessary.
3. **PySpark JVM Overhead:** Local PySpark initialization incurs $1.5	ext{--}2.5	ext{ s}$ of latency; Spark is beneficial exclusively for batch ingestion ($>10,000$ points), whereas real-time routing utilizes single-machine vectorized paths.

---

## 9. Conclusion
ROUTE/IQ-NextGen transforms multi-algorithm routing into a genuinely cooperative, adaptive, and vehicle-condition-aware framework. By unifying Big Data spatial partitioning, quantum variational cuts, quantum-inspired genetic algorithms, and classical local search through a diversity-managed candidate blackboard and Contextual MAB, the system achieves superior routing solutions under real-world EV battery degradation constraints, backed by certified non-degradation guarantees.

---

## Acknowledgment
The authors express their deepest gratitude to their faculty research supervisor, Dr. Vishnu Prasad Verma, Department of Computer Science and Engineering, SRM University-AP, for his invaluable guidance, technical reviews, and sustained mentorship throughout the inception and development of the ROUTE/IQ project.
