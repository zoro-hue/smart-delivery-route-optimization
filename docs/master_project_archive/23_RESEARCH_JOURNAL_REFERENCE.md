# ROUTE/IQ: Research Journal Reference & Student Progress Logs
**Institutional Context:** Department of Computer Science and Engineering, SRM University-AP  
**Supervisor:** Prof. Vishnu Prasad Verma (`vishnu.v@srmap.edu.in`)  
**Student Researchers:** J. Jayanth, B. Kaivalya, P. Shyam Sai  
**Academic Record:** UROP Semester Research Logbook & Weekly Milestone Tracking `[VERIFIED]`

---

## 1. Project Logbook & Weekly Milestone Summary

This document serves as the formal student lab notebook and progress record for UROP weekly reviews, departmental presentations, and supervisor sign-offs.

### Week 1–2 (Sept 1 – Sept 14, 2026): Topic Approval & Literature Survey
- **Supervisor Guidance:** Prof. Vishnu Prasad Verma approved the research topic: "Smart Delivery Route Optimization Using Hybrid Big Data and Quantum Computing". Focus placed on practical last-mile logistics constraints.
- **Milestones:** Conducted literature review across IEEE Xplore, ACM Digital Library, and arXiv. Identified key papers: Clarke & Wright (1964), Gillett & Miller (1974), Farhi et al. (2014), and Feld et al. (2019).
- **Deliverables:** Formulated Research Questions RQ1–RQ4 and drafted initial Project Charter.

### Week 3–4 (Sept 15 – Sept 28, 2026): Dataset Ingestion & Network Extraction
- **Milestones:** Downloaded and cleaned NYC OpenData freight delivery points (1,898 orders), TLC vehicle fleet data (10,000 vehicles), NYC DOT traffic sensor feeds (42,756 records), and NOAA weather history. Extracted the 5-borough road network using OSMnx (54,128 nodes, 134,814 edges).
- **Key Discovery:** Identified that Euclidean distance underestimates real urban road travel by 28–42% due to one-way street loops and bridge crossings.

### Week 5–6 (Sept 29 – Oct 12, 2026): Big Data Spark & Polar Sweep Implementation
- **Milestones:** Implemented `SparkWorkloadOrganizer` using PySpark 4.2.0. Converted customer coordinates into relative polar coordinates ($\theta = \text{atan2}(\Delta y, \Delta x)$) relative to municipal depots.
- **Obstacle Encountered:** Discovered the "Angular Disruption Effect"—rigid sector rays cut through natural delivery corridors, stranding neighboring customers across artificial vehicle boundaries. Formulated the boundary customer buffer heuristic ($\Delta d < \tau$) to mitigate this.

### Week 7–8 (Oct 13 – Oct 26, 2026): Quantum Variational Circuit Design (Qiskit Aer)
- **Milestones:** Mapped customer boundary bipartition subproblems onto Ising spin glasses. Implemented gate-based QAOA using Qiskit 2.4.1.
- **Critical Failure:** Transverse $X$-mixer QAOA with quadratic penalties caused frequent vehicle capacity violations (68% violation rate).
- **Corrective Breakthrough:** Adopted the XY-mixer Alternating Operator Ansatz (Hadfield et al., 2019; Wang et al., 2020), restricting quantum exploration strictly to the valid Hamming weight subspace. Capacity violation rate dropped to 0%.

### Week 9–10 (Oct 27 – Nov 9, 2026): Proposition 1 Guardrail & MAB Controller
- **Milestones:** Formulated and mathematically proved the Proposition 1 Monotonic Feasibility Guardrail:
  $$\text{Cost}(S_{\text{next}}) = \min(\text{Cost}(S_{\text{incumbent}}), \text{Cost}(S_{\text{candidate}}))$$
  Integrated Multi-Armed Bandit (UCB1) adaptive hyper-heuristic controller to dynamically balance ALNS, VND, and quantum candidate generators.

### Week 11–12 (Nov 10 – Nov 21, 2026): Next-Gen Engine, Cloud Hardening & Archival
- **Milestones:** Implemented Next-Generation ALNS (Shaw removal, Worst removal, Regret-3 insertion). Solved the Render 512 MB memory crash using SciPy CSR sparse matrix caching (`road_matrix_csr.npz`). Executed 30-instance supremacy benchmark (12 wins, 18 ties, 0 losses vs OR-Tools). Completed master documentation package.
