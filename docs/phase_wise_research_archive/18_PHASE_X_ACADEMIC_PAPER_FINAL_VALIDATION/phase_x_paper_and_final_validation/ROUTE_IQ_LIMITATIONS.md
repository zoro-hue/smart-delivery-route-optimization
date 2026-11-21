# ROUTE/IQ: Research Limitations & Scientific Boundaries

## 1. Explicit Disclosure of Limitations

In adherence to strict academic honesty and peer-review integrity, this research acknowledges the following computational and methodological limitations:

---

## 2. Itemized Limitations

### 1. Classical Simulation vs Physical Quantum Hardware (QPU)
All quantum circuits were executed via **classical CPU simulation on Qiskit Aer (v0.17.2)**. No physical quantum processor (QPU), superconducting circuit, or ion-trap hardware was utilized. Consequently:
- No quantum speedup or quantum supremacy is claimed or implied.
- Simulation runtimes reflect classical statevector/matrix multiplication overheads, not physical quantum gate execution times.

### 2. Lack of Statistical Significance for Incremental Quantum Benefit
The incremental distance reduction achieved by adding QAOA to OR-Tools + VND ($\Delta = -15.72\text{ km}$, $-2.81\%$) yielded a paired $t$-test of **$p = 0.089152$**. Because $p > 0.05$, the incremental contribution of simulated QAOA is **not statistically significant** under standard parametric thresholds.

### 3. Outperformance by Classical Partitioning Heuristics
Classical graph bisection (Kernighan-Lin) achieved superior complete fleet distances (**540.07 km** vs **544.20 km**) while executing **$19.7\times$ faster** ($6.50\text{ ms}$ vs $128.28\text{ ms}$). For subproblem sizes $N \le 16$, classical algorithms (including exact $2^N$ enumeration) are computationally tractable and systematically outperform simulated QAOA.

### 4. Single-Machine Spark Execution (`local[*]`)
Apache Spark 4.2.0 was benchmarked in `local[*]` single-machine multi-threaded mode on a single workstation. The experiments do not establish physical distributed scaling across a multi-node cluster (e.g., AWS EMR or Dataproc). For single-node datasets under $N = 50,000$, PySpark incurs 10x–50x JVM serialization overhead compared to native in-memory C/NumPy arrays.

### 5. Reliance on Classical Post-Processing for Feasibility
Unconstrained transverse-field QAOA ($H_M = \sum X_i$) resulted in **55.08% of raw sampled states violating vehicle capacity constraints ($Q > C$)**. The architecture relies entirely on a deterministic classical repair operator to restore operational feasibility.

### 6. Nature of the Non-Degradation Guarantee
The guarantee that complete route distance never degrades below the classical baseline ($\text{Cost}(R_{\text{final}}) \le \text{Cost}(R_{\text{incumbent}})$) is **strictly an algorithmic feature of the Proposition 1 classical guardrail**. It is not evidence of quantum optimization capability.

### 7. Dataset Provenance and Scale
Controlled ablation was conducted on synthetic 12-customer boundary subproblems and a 50-stop Manhattan delivery fleet. While spatial coordinates and directed asymmetric cost matrices reflect realistic urban logistics, performance on irregular rural topologies or fleets with hundreds of heterogeneous vehicles remains unverified.
