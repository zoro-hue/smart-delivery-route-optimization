# ROUTE/IQ: FIGURE AND TABLE SPECIFICATION PLAN

**Manuscript Title:** ROUTE/IQ: A Big Data–Quantum Hybrid Framework for Directed Urban Vehicle Routing with Quality-Aware QAOA and End-to-End Route Certification  
**Authors:** J. Jayanth, B. Kaivalya, P. Shyam Sai, and Vishnu Prasad Verma  
**Affiliation:** Department of Computer Science and Engineering, SRM University-AP, Amaravati, Andhra Pradesh, India  
**Document Purpose:** Detailed specification of all 11 mandatory figures and 10 structured tables required for journal submission.

---

## Part 1: Mandatory Figures (11 Figures)

1. **Figure 1: Overall ROUTE/IQ Dual-Pillar Architecture**  
   *Visual:* Conceptual flowchart showing Pillar 1 (Apache Spark 4.2.0), Pillar 2 (QAOA on Qiskit Aer), and the QGAR bridge with the End-to-End Certification Guardrail.
2. **Figure 2: Spark-to-QAOA Runtime Dataflow**  
   *Visual:* Sequence diagram tracing data movement between the JVM (PySpark) and C-Python (Qiskit/Aer).
3. **Figure 3: QAOA Circuit Architecture & Particle-Conserving Mixers**  
   *Visual:* Circuit schematic showing state preparation, Ising problem unitary $U(C, \gamma)$, and $XY$ mixer rotations (`XXPlusYYGate`).
4. **Figure 4: Quantum Candidate Evaluation Workflow**  
   *Visual:* Flow diagram showing measurement bitstring extraction, Kuhn-Munkres Hungarian projection, and min-cost directed candidate selection.
5. **Figure 5: Adaptive Reconstruction Workflow**  
   *Visual:* Flow diagram showing computation of $\lambda_{\text{base}}$, planar crossing penalty multiplier, and backbone adoption.
6. **Figure 6: End-to-End Route Certification Flowchart**  
   *Visual:* Decision flowchart verifying $C(R_{\text{QGAR}}) \le C(R_{\text{spatial}}) + 10^{-4}\text{ km}$ to eliminate DP insertion divergence.
7. **Figure 7: Spark Scaling Graph (1,000 to 50,000 Orders)**  
   *Visual:* Dual-axis plot of wall-clock runtime (ms) and throughput (orders/s) scaling near-linearly ($O(N \log N)$).
8. **Figure 8: Route-Distance Comparison Graph Across Scales**  
   *Visual:* Grouped bar chart comparing Full QGAR, Spatial Baseline, Phase H, OR-Tools GLS, Clarke-Wright, and RB-QCD across scales $N=10, 25, 50, 100$.
9. **Figure 9: QAOA Subproblem Approximation-Quality Graph**  
   *Visual:* Approximation ratios ($\alpha = 0.9079$ at $m=3$, $\alpha = 0.8435$ at $m=4$) vs. random sampling baseline.
10. **Figure 10: Quantum Attribution Controlled Ablation Graph (Regimes A–F)**  
    *Visual:* Bar chart comparing campaign route distances across Spatial Only (A), Genuine QAOA (B), Uniform Random (C), Shuffled QAOA (D), Transitions Disabled (E), and Classical Candidates (F).
11. **Figure 11: Unbundled Runtime Breakdown Graph**  
    *Visual:* Stacked bar chart showing Spark preprocessing time, QAOA circuit simulation time, classical COBYLA optimization time, and DP reconstruction time.

---

## Part 2: Mandatory Tables (10 Tables)

1. **Table 1: Dataset Characteristics:** Manhattan OSM Largest SCC (54,128 nodes, 142,123 edges), NYC DOT hourly traffic volumes, NOAA weather.
2. **Table 2: Mathematical Notation & Parameter Dictionary:** Complete dictionary of symbols ($G, V, E, W, \mathcal{C}, Q, D, \lambda_{\text{eff}}, \epsilon, \alpha, \beta$).
3. **Table 3: Algorithm Configurations & Solver Hyperparameters:** Parameter settings for Spark, QAOA ($p=1$, 2,048 shots, COBYLA maxiter=30), OR-Tools GLS, and Clarke-Wright.
4. **Table 4: Experimental Environment & Hardware Specifications:** Workstation hardware, Windows 11, OpenJDK 17, Hadoop 3.3.6 winutils, Spark 4.2.0, Qiskit 2.4.1.
5. **Table 5: Multi-Algorithm Benchmark Performance Comparison:** Performance table across scales $N=10$ to $150$ with means, standard deviations, and feasibility rates.
6. **Table 6: QAOA Microcluster Subproblem Results:** Logical qubits ($9$ and $16$), circuit depth, energy expectation values, and approximation ratios.
7. **Table 7: Quantum Attribution Ablation Telemetry:** Regimes A through F comparison on identical instances with accepted transitions and routes changed.
8. **Table 8: Statistical Significance & Inferential Hypothesis Testing:** Paired Wilcoxon signed-rank tests ($W, p, r_B$), bootstrap 95% CIs, and Benjamini-Hochberg FDR adjustments.
9. **Table 9: Systematic Prior Art Comparison Matrix:** Detailed feature comparison against Feld et al. (2019), Harwood et al. (2021), and Azad et al. (2022).
10. **Table 10: Limitations, Assumptions, and Research Status:** Epistemic classification distinguishing theorems, empirical findings, and open hypotheses.
