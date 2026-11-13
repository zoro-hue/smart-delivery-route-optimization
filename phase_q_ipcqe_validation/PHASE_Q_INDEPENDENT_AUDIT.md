# ROUTE/IQ — PHASE Q: INDEPENDENT AUDIT OF PHASE P AND IP-CQE
**Rigorous Forensic Audit, Claim Classification, and Root-Cause Analysis of Phase P Outcomes**

- **Audit Date:** 2026-11-06
- **Branch:** `research/phase-q-ipcqe-validation`
- **Baseline Git Commit:** `e7149f4` (preserving Phase P)
- **Protected Branch:** `main` (`a8eb849` — Untouched)
- **Scope:** Independent forensic review of all Phase P prototypes, benchmark scripts, raw CSV data, and mathematical claims.

---

## 1. Classification of Phase P Research Claims

Every central claim from Phase P has been audited against source code, raw CSV logs, and mathematical mechanics:

| Phase P Claim | Audit Classification | Evidence & Forensic Analysis |
| :--- | :---: | :--- |
| **Claim 1: PySpark Partitioning is Consistent with Pandas** | **Independently Reproduced** | Verified in `run_spark_scaling_benchmark.py`: identical clusters formed across $N \in [10, 500]$. |
| **Claim 2: Spark Startup Overhead Dominates Local Execution** | **Independently Reproduced** | Verified in `phase_p_spark_scaling_raw.csv`: Spark latency plateaus at $\approx 580\text{ ms}$, while Pandas runs in $< 30\text{ ms}$. |
| **Claim 3: Feasibility Rate is 100% across all Prototypes** | **Independently Reproduced** | Verified in `test_prototypes_smoke.py`: 5/5 prototypes passed with 0 drops, 0 duplicates, 0 capacity violations. |
| **Claim 4: Warm-Start XY Mixers Increase Valid Permutation Rate** | **Partially Supported (Caveated)** | The XY hopping mixer preserves Hamming weight per customer row ($\sum_p x_{ip} = 1$), but **does not commute with column constraints** ($\sum_i x_{ip} = 1$). High feasibility is partially an artifact of initializing in $|x_{\text{seed}}\rangle$ with low rotation angles $\beta$, plus Hungarian post-projection. |
| **Claim 5: Prototype 1 and Prototype 5 Execute Full QAOA** | **Reproduced with Discrepancies** | The implementation in `proto_1_classical_seeded_qaoa.py` assigns **static analytical parameters** ($\gamma_0, \beta_0$) without a classical outer-loop variational optimizer (COBYLA/Nelder-Mead). It executes a single quantum sampling step, not a closed-loop variational optimization. |
| **Claim 6: IP-CQE Outperforms Clarke-Wright** | **Independently Reproduced** | Verified in `phase_p_benchmark_raw.csv`: IP-CQE achieves $76.56\text{ km}$ vs Clarke-Wright $81.53\text{ km}$ at $N=25$ ($6.49\%$ improvement). |
| **Claim 7: IP-CQE Outperforms OR-Tools via QAOA** | **Contradicted by Evidence** | In `phase_p_benchmark_raw.csv`, the improvement over OR-Tools is **exactly 0.00% across every single benchmark run**. In 100% of runs, `guardrail_triggered` was `True`. QAOA never produced a candidate superior to the OR-Tools incumbent; the system retained OR-Tools via the guardrail. |

---

## 2. In-Depth Root-Cause Analysis: Why QAOA Failed to Beat OR-Tools in Phase P

### Issue 1: The Subproblem Microcluster Optimality Paradox
- In Phase P, subproblems of size $K=4$ were extracted from the OR-Tools incumbent route.
- **The Mathematical Reality:** Google OR-Tools (Guided Local Search with 2-opt and Large Neighborhood Search) evaluates all 2-opt and 3-opt moves. For a 4-node sub-tour, the search space contains only $4! = 24$ permutations.
- On planar and low-circuity networks, OR-Tools had **already found the globally optimal sequence** for those 4 nodes!
- Since the classical seed was already the global minimum for that subproblem, **no mathematical algorithm (quantum, classical, or divine) could discover a shorter tour** on those 4 nodes without changing the boundary nodes or reassigning customers.

### Issue 2: Fixed Static Parameters ($\gamma, \beta$) vs. Variational Optimization
- True QAOA relies on the variational principle:
  $$\min_{\boldsymbol{\gamma}, \boldsymbol{\beta}} \langle \psi(\boldsymbol{\gamma}, \boldsymbol{\beta}) | H_C | \psi(\boldsymbol{\gamma}, \boldsymbol{\beta}) \rangle$$
- In `proto_1_classical_seeded_qaoa.py`, parameters were fixed at $\gamma_0 = 0.15\pi / \max(c_{ij})$ and $\beta_0 = 0.35\pi$. Without variational parameter tuning via COBYLA or Nelder-Mead, destructive interference cannot be adapted to the specific instance cost landscape.

### Issue 3: Microcluster Isolation vs. Complete Route Dynamics
- Improving a 4-node subproblem in isolation does not guarantee complete-route improvement unless:
  1. The subproblem is extracted around a **genuine classical heuristic trap** (e.g. crossing edges from Clarke-Wright or greedy dispatch that 2-opt cannot uncross).
  2. Multi-route exchanges (2-opt* or customer swaps between adjacent vehicles) are permitted.

---

## 3. Mandatory Research Directives for Phase Q

To advance from defensive non-degradation to **demonstrable quantum-assisted improvement**, Phase Q must:
1. **Implement True Variational QAOA (V-QAOA):** Integrate an outer-loop classical optimizer (COBYLA/SPSA) to actively tune $(\boldsymbol{\gamma}, \boldsymbol{\beta})$ to minimize energy $\langle H_C \rangle$.
2. **Target Genuine Classical Heuristic Traps:** Identify subproblems where classical construction heuristics (Clarke-Wright, Nearest Neighbor, Greedy) are demonstrably sub-optimal ($E_{\text{class}} > E_{\text{exact}}$).
3. **Benchmark Against Exact Permutation Enumeration:** On all $K \le 5$ subproblems, compute ground-truth exact permutation costs to measure the exact Approximation Ratio of QAOA:
   $$\alpha_{\text{QAOA}} = \frac{E_{\text{QAOA}} - E_{\text{min}}}{E_{\text{max}} - E_{\text{min}}}$$
4. **Develop IP-CQE v2:** A refined architecture featuring variational parameter adaptation, multi-candidate sampling diversity, and route-level re-insertion that actively beats standard classical heuristics without relying solely on the fallback guardrail.

