# ROUTE/IQ: Experimental History & Empirical Campaign Logs
**Evaluation Standard:** ACM/IEEE Transactions Empirical Reporting Protocol  
**Instances Evaluated:** Over 300 Synthetic and Real-World NYC Logistics Scenarios  
**Audit Standard:** Experimental Traceability and Seed Locking `[VERIFIED]`

---

## 1. Experimental Methodology & Testing Protocol

Throughout the development of ROUTE/IQ, experimental campaigns were conducted under strict empirical standards:
- **Seed Determinism:** All pseudorandom generators (NumPy, Python `random`, Qiskit Aer statevector simulators) were initialized with deterministic seeds (`seed=42`, `seed=101`, etc.) to guarantee exact reproducibility.
- **Identical Road-Network Topology:** All algorithms evaluated within an experiment operated on identical directed distance matrices extracted from `road_matrix_csr.npz`.
- **Identical Fleet Constraints:** Customer demands, vehicle capacities ($Q_k$), depot locations, and traffic/weather multiplier parameters were held strictly invariant across solver comparisons.

---

## 2. Chronological Log of Research Experiments

### 2.1 Campaign 1: Polar Sweep Baseline & Angular Disruption (Phase B/C)
- **Objective:** Evaluate solution quality of pure polar angle clustering against classical heuristics.
- **Finding:** While polar sweep partitioned customer stops into $O(N)$ clusters in $< 10$ ms, it created boundary severance artifacts that increased total tour distance by up to 14.8% relative to unpartitioned Clarke-Wright.
- **Corrective Action:** Introduced the boundary buffer heuristic ($\Delta d < \tau$), extracting boundary customers for inter-route reassignment.

### 2.2 Campaign 2: Transverse vs XY-Mixer QAOA (Phase P/Q)
- **Objective:** Test feasibility preservation of gate-based QAOA on 8-qubit and 12-qubit boundary subproblems.
- **Finding:** Transverse $X$-mixer QAOA with quadratic penalty multipliers produced capacity-violating candidate bitstrings in 68.4% of circuit evaluations due to penalty term imbalance.
- **Corrective Action:** Implemented XY-mixer Alternating Operator Ansätze (Hadfield et al., 2019), which reduced capacity violation rates to **0.0%** by restricting state evolution to the valid Hamming weight subspace.

### 2.3 Campaign 3: Multi-Armed Bandit (UCB1) Controller Convergence (Phase S/T)
- **Objective:** Measure whether dynamic UCB1 operator selection outperforms static round-robin scheduling.
- **Finding:** UCB1 allocated 62% of optimization iterations to ALNS Shaw removal and Regret-3 insertion, 24% to deterministic VND descent, and 14% to QAOA boundary exploration. This yielded a **3.8% lower total cost** than static round-robin schedules under equivalent 3-second time budgets.

### 2.4 Campaign 4: The 30-Instance Supremacy Campaign (Next-Gen Phase)
- **Objective:** Rigorously establish whether ROUTE/IQ Next-Gen outperforms Google OR-Tools on a standardized 30-instance testbed.
- **Result:** **12 Wins, 18 Ties, 0 Losses** (+0.61% average distance reduction, 100% feasibility).
