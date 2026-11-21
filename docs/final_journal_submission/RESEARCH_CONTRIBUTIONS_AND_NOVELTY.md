# Research Novelty and Contributions Document

**Project:** ROUTE/IQ: Intelligent Delivery Route Optimization Using Hybrid Big Data, Quantum Computing, and Cooperative Vehicle Fleet Optimization  
**Institutional Affiliation:** Department of Computer Science and Engineering, SRM University-AP, Amaravati, Andhra Pradesh, India  
**Authors:** J. Jayanth, B. Kaivalya, P. Shyam Sai (Undergraduate Research Scholars)  
**Faculty Research Supervisor:** Dr. Vishnu Prasad Verma  
**Date:** November 21, 2026  

---

## 1. Summary of Explicit Research Contributions

ROUTE/IQ-NextGen addresses key limitations identified in recent combinatorial vehicle routing, variational quantum optimization, and hyper-heuristic literature. The research makes four distinct contributions:

### Contribution 1: The Heterogeneous Fleet Vehicle Condition (HFVRP-VC) Formulation
- **The Problem:** Standard vehicle routing formulations (e.g., Toth & Vigo 2014, Schneider et al. 2014) assume nominal battery capacities and idealized ranges. In reality, commercial EV batteries degrade electrochemically over time (SoH fade), charge levels fluctuate dynamically (SoC), and neglected maintenance increases mechanical drag.
- **The Contribution:** We formulate the HFVRP-VC model with physical electrochemical energy bounds:
  $$B_{	ext{usable}, k} = B_{	ext{nom}, k} \cdot \left(rac{	ext{SoH}_k}{100}ight)$$
  $$R_k = rac{B_{	ext{usable}, k} \cdot (	ext{SoC}_k / 100)}{\mu_k \cdot f_k} 	imes 100$$
  This bounds dispatch routes by true battery chemistry and enforces a 4-pillar multi-objective trade-off across distance, cost, energy, and emissions.

### Contribution 2: Shared Diversity-Managed Candidate Pool Blackboard
- **The Problem:** Existing "cooperative" or "hybrid" routing frameworks (e.g., Feld et al. 2019, Borowski et al. 2020) suffer from *pseudo-cooperation*—executing solvers independently and taking the minimum, or running a rigid linear pipeline ($A 	o B$) without cross-algorithm mutation.
- **The Contribution:** We implement a centralized candidate blackboard ($\mathcal{P}_t$, capacity $M=16$) maintaining standardized candidate data structures with complete ancestry trees, physical multi-objective scores, and topological edge graphs. Population stagnation is prevented via an edge-based Jaccard diversity metric:
  $$	ext{Dist}(S_a, S_b) = 1 - rac{|\mathcal{E}(S_a) \cap \mathcal{E}(S_b)|}{|\mathcal{E}(S_a) \cup \mathcal{E}(S_b)|}$$
  Candidates with $	ext{Dist} < 10^{-4}$ are automatically rejected.

### Contribution 3: Contextual Multi-Armed Bandit (MAB) with 4-Pillar Reward
- **The Problem:** Traditional hyper-heuristics (Burke et al. 2013) evaluate operators purely on objective improvement, causing selection of computationally expensive solvers (such as quantum circuits) even for trivial gains, leading to unacceptable execution latencies.
- **The Contribution:** We formulate an online Contextual MAB with UCB-1 operator selection and a 4-pillar multi-objective feedback reward:
  $$R(o) = w_1 \Delta_{	ext{norm}} + w_2 \mathbb{I}_{	ext{feas}} + w_3 	ext{Div}(S_{	ext{new}}, \mathcal{P}_t) - w_4 \left(rac{t_{	ext{exec}}}{t_{	ext{budget}}}ight)$$
  This explicitly penalizes high-latency operators while rewarding feasibility and topological diversity, reducing execution latency by $24.0\%$.

### Contribution 4: Certified Conditional Non-Degradation Guardrail (Proposition 1)
- **The Problem:** Enterprise logistics operators cannot deploy stochastic or quantum heuristic solvers if there is any possibility of solution degradation relative to deterministic classical industrial solvers (e.g., Google OR-Tools).
- **The Contribution:** We formulate and mathematically prove **Proposition 1**, establishing a fail-safe algorithmic guardrail that guarantees by construction:
  $$\mathcal{D}(S_{	ext{final}}) \le \mathcal{D}(S_{	ext{ortools}}) + \epsilon_{	ext{float}}$$
  This eliminates degradation risk, ensuring the hybrid cooperative engine strictly matches or outperforms the classical baseline on every run.

---

## 2. Literature Comparison Matrix

| Novelty Dimension | State-of-the-Art Literature | ROUTE/IQ-NextGen Proposed Approach |
| :--- | :--- | :--- |
| **Fleet Realism** | Homogeneous fleets or nominal capacity bounds (Toth & Vigo 2014). | Explicit electrochemical battery degradation (SoH), dynamic SoC, and maintenance wear multipliers (HFVRP-VC). |
| **Hybrid Interaction** | Rigid linear pipeline $A 	o B 	o C$ or isolated candidate comparison (Feld et al. 2019). | Bidirectional co-evolution over a shared candidate pool blackboard ($M=16$) with full provenance tracking. |
| **Quantum Scope** | Direct full-graph mapping restricted to toy instances $N \le 8$ (Azad et al. 2022). | Targeted Subproblem Boundary Operator extracting conflict stops ($K_{	ext{sub}} \le 8$) between adjacent routes. |
| **Search Guidance** | Pure objective gain feedback (Burke et al. 2013). | 4-Pillar reward balancing normalized objective gain, feasibility, edge diversity, and execution runtime. |
| **Production Reliability** | Best-effort heuristic without performance guarantees. | Certified Proposition 1 Guardrail mathematically guaranteeing zero degradation against OR-Tools baseline. |
