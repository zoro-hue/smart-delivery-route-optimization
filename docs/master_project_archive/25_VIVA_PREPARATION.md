# ROUTE/IQ: Viva Examination & Supervisor Defense Master Dossier
**Examination Focus:** Comprehensive Oral Defense & Cross-Examination Preparation  
**Target Audience:** UROP Defense Panel, External Examiners, Departmental Review Committee  
**Institution:** SRM University-AP, Department of CSE  
**Audit Standard:** Formal Defense Preparation & Model Answers `[VERIFIED]`

---

## 1. Top 15 High-Frequency Examiner Questions & Model Answers

### Q1: "Are you running these quantum algorithms on an actual quantum computer, or just a simulator?"
- **Model Answer:**  
  "All quantum routines in ROUTE/IQ are executed via **classical CPU statevector simulation** using Qiskit Aer 2.4.1. We explicitly disclaim physical quantum supremacy on hardware QPUs. In our hybrid architecture, QAOA functions as a candidate generator exploring boundary bipartition configurations within localized 8-to-16 qubit subproblems ($O(2^n)$ complex amplitudes). We maintain complete transparency regarding this distinction throughout our paper and system documentation."

### Q2: "If QAOA is running on a classical simulator, what advantage does it offer over a purely classical heuristic?"
- **Model Answer:**  
  "Our 5-way ablation study demonstrates that simulated QAOA with XY-mixers provides a distinct, non-local exploration mechanism that escapes local minima on boundary clusters, yielding a statistically significant improvement ($p = 0.0410$, Cohen's $d = 0.22$) over the ablated classical-only engine (`no_qaoa`). While classical local search is greedy and deterministic, quantum statevector sampling explores superpositions of candidate allocations. Furthermore, under our Proposition 1 guardrail, even if the quantum circuit fails to find an improvement, the classical incumbent is strictly preserved with zero risk of degradation."

### Q3: "What is Proposition 1, and why do you consider it an important contribution?"
- **Model Answer:**  
  "Proposition 1 is the **Monotonic Feasibility Guardrail**, formally defined as:
  $$\text{Cost}(S_{\text{next}}) = \min(\text{Cost}(S_{\text{incumbent}}), \text{Cost}(S_{\text{candidate}}))$$
  subject to strict feasibility verification. In the published hybrid quantum literature (e.g., Feld et al., 2019; Azad et al., 2022), hybrid solvers frequently return degraded or infeasible routes due to quantum circuit noise and barren plateaus. Proposition 1 provides an inductive mathematical guarantee that our cooperative engine will never return a solution inferior to the classical industrial incumbent (Google OR-Tools), establishing an essential safety guarantee for real-world logistics."

### Q4: "What is the 'Angular Disruption Effect' that you identified in your Spark pipeline?"
- **Model Answer:**  
  "When Apache Spark decomposes urban delivery points using geometric polar coordinate sweep ($\theta = \text{atan2}(\Delta y, \Delta x)$), the radial partition lines frequently bisect natural delivery corridors or separate customer stops on opposite sides of a one-way street. We observed empirically that rigid sector boundaries increased total fleet travel distance by up to 14.8%. We solved this by developing a dynamic boundary buffer heuristic ($\Delta d < \tau$) that extracts boundary customers and passes them to our Cooperative Engine's QAOA and ALNS pools for inter-route reassignment."

### Q5: "How does your system handle realistic road traffic compared to standard CVRP benchmarks?"
- **Model Answer:**  
  "Standard academic benchmarks (such as CVRPLIB) rely on static Euclidean distances on a 2D plane. ROUTE/IQ embeds a real 54,128-node directed road network of New York City extracted via OSMnx. We calculate travel impedance using the federal Bureau of Public Roads (BPR) volume-delay formula:
  $$t_e = t_e^0 \left[ 1 + 0.15 \left( \frac{V_e}{C_e} \right)^4 \right] \cdot W_{\text{weather}}$$
  calibrated against 42,756 NYC DOT traffic sensor records and NOAA meteorological data. This captures turn restrictions, bridge bottlenecks, and rush-hour congestion."

### Q6: "Why did you use XY-mixers instead of standard transverse $X$-mixers in your QAOA circuits?"
- **Model Answer:**  
  "Standard transverse mixers ($H_M = \sum \sigma_i^x$) allow state transitions that change the total number of 1s in the register (Hamming weight). In vehicle routing, this causes quantum state evolution to leak into infeasible subspaces where vehicle capacities are drastically violated (exhibiting a 68% violation rate in our tests). The XY-mixer:
  $$H_{\text{XY}} = \frac{1}{2} \sum \left( \sigma_i^x \sigma_j^x + \sigma_i^y \sigma_j^y \right)$$
  acts as a particle-conserving hop operator. It strictly preserves the total Hamming weight, restricting quantum exploration exclusively to valid bipartition configurations that satisfy vehicle capacity parity."

### Q7: "How did you overcome the 512 MB memory limit on Render cloud hosting?"
- **Model Answer:**  
  "Initially, loading the 54,128-node NetworkX graph object consumed 1,240 MB of RAM, causing immediate Out-of-Memory crashes (SIGKILL 137). We resolved this by precomputing the directed road network into a SciPy Compressed Sparse Row (CSR) matrix (`road_matrix_csr.npz`) and building a spatial `cKDTree` for coordinate snapping. This reduced memory consumption on startup from 1,240 MB to **280 MB RAM**, allowing our backend to boot instantaneously and operate reliably within Render's 512 MB physical ceiling."

### Q8: "How does the Multi-Armed Bandit (UCB1) controller select optimization operators?"
- **Model Answer:**  
  "The UCB1 controller balances exploitation of high-performing operators with exploration of less-frequently used operators by calculating:
  $$\text{Score}_i = \bar{R}_i + c \sqrt{\frac{\ln T}{N_i}}$$
  Where $\bar{R}_i$ is the empirical reward ratio (distance improvement divided by execution latency in milliseconds), $T$ is total search iterations, and $N_i$ is the invocation count of operator $i$. In our experiments, UCB1 dynamically shifted search effort toward ALNS Shaw removal and Regret-3 insertion during early iterations, transitioning to fine-grained VND descent as convergence approached."

### Q9: "What was the root cause of the bug where 10/11 algorithms completed and the 11th got stuck queued?"
- **Model Answer:**  
  "The defect was caused by Python's single-threaded event loop starvation. Heavy CPU-bound execution of QAOA and VND without cooperative async yields locked the Uvicorn worker thread. When the client probed `/api/health`, the request timed out, causing the frontend to display `Disconnected · Retry`. Additionally, an unhandled timeout in one of the solvers failed to decrement the pending solver counter, leaving the job permanently at 10/11. We resolved this by wrapping background solvers in isolated error-handling blocks with explicit state transitions and cooperative `await asyncio.sleep(0.01)` event-loop yields."

### Q10: "Can you prove that your algorithm outperforms OR-Tools statistically, and not just by chance?"
- **Model Answer:**  
  "Yes. On our standardized 30-instance NYC benchmark suite, ROUTE/IQ achieved 12 wins, 18 ties, and 0 losses against Google OR-Tools. Because the difference in routing distances violates normality assumptions, we conducted a two-tailed Wilcoxon signed-rank test. The test yielded a test statistic $W = 0.0$ and a $p$-value of **$p = 0.00049$**, which is well below the standard significance threshold $\alpha = 0.01$. The Cohen's $d$ effect size is $0.42$, confirming a statistically significant and practically meaningful improvement."
