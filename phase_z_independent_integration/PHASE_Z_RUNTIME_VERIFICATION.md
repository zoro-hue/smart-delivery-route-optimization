# PHASE Z RUNTIME VERIFICATION
## Deconstruction of Execution Latency, Profiling Breakdown, and Acceleration Audit
**ROUTE/IQ — Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing**  
**Department of Computer Science and Engineering, SRM University-AP**  
**Supervisor:** Dr. Vishnu Prasad Verma  

---

## 1. RESEARCH MANDATE

Phase Y reported that **Adaptive Fast QAOA (Formulation F)** achieved a **$3.05\times$ speedup** over baseline QAOA (reducing average wall-clock latency from **121.58 ms to 39.84 ms**) with zero degradation in solution quality.

Phase Z was mandated to deconstruct this claim, profile each computational stage independently, and determine whether the reported acceleration was algorithmic, implementation-driven, or a measurement artifact.

---

## 2. STAGE-BY-STAGE LATENCY DECOMPOSITION

To establish an unassailable profile, Phase Z instrumented and measured each step of the optimization pipeline across 15 benchmark instances:

```mermaid
flowchart LR
    S1["1. Build (1.5 ms)"] --> S2["2. Statevector (17.0 ms)"]
    S2 --> S3["3. Sampling (23.8 ms)"]
    S3 --> S4["4. Repair (0.1 ms)"]
    S4 --> S5["5. VND Eval (2.0 ms)"]

    style S1 fill:#e3f2fd,stroke:#1565c0
    style S2 fill:#e8f5e9,stroke:#2e7d32
    style S3 fill:#fff3e0,stroke:#e65100
    style S4 fill:#fce4ec,stroke:#c2185b
    style S5 fill:#f3e5f5,stroke:#7b1fa2
```

### Empirical Profiling Breakdown (Mean ms per Instance)

| Optimization Stage | Phase Y Reported (Formulation A) | Phase Y Reported (Formulation F) | Genuine Qiskit (Transverse) | Genuine Qiskit (XY-Mixer) | Classical Kernighan-Lin |
|---|---|---|---|---|---|
| **1. Circuit Construction** | Included in overhead | Included in overhead | 1.53 ms | 1.98 ms | 0.00 ms |
| **2. Unitary Evolution / Sim** | ~36.58 ms (loop) | ~24.84 ms (loop) | 17.00 ms | 19.31 ms | 1.63 ms (search) |
| **3. Hardcoded Overhead** | **85.00 ms** (synthetic) | **15.00 ms** (synthetic) | **0.00 ms** | **0.00 ms** | 0.00 ms |
| **4. Sampling & Decoding** | Included in loop | Included in loop | 23.82 ms | 23.09 ms | 0.00 ms |
| **5. Classical Repair** | 0.09 ms | 0.08 ms | 0.09 ms | 0.10 ms | 0.00 ms |
| **6. VND Fleet Tour Eval** | 1.59 ms | 1.78 ms | 2.06 ms | 1.80 ms | 2.03 ms |
| **Total Pipeline Latency** | **145.64 ms** | **46.17 ms** | **44.41 ms** | **46.18 ms** | **3.65 ms** |

---

## 3. AUDIT OF THE 3.05x ACCELERATION MECHANISM

Inspection of the source code in `phase_y_breakthrough_engineering/prototypes/advanced_quantum_formulations.py` (lines 105–137) revealed the exact origin of the reported 3.05x speedup:

1. **Shot Reduction:**  
   In Formulation F, the number of simulated sampling iterations was halved:
   ```python
   actual_shots = 512 if fast_mode else shots  # 512 vs 1024
   ```
2. **Hardcoded Compilation Overhead:**  
   The runtime calculation contained an explicit synthetic additive constant:
   ```python
   compilation_overhead = 15.0 if fast_mode else (45.0 if use_xy_mixer else 85.0)
   t_ms = (time.perf_counter() - t0) * 1000.0 + compilation_overhead
   ```

### Audit Finding
- The delta between Formulation A and Formulation F was largely driven by subtracting **70.0 ms of synthetic compilation overhead** ($85.0 - 15.0 = 70.0\text{ ms}$) and halving the sampling loop iterations.
- When genuine Qiskit 2.4.1 statevector simulation is executed without synthetic additives, **both transverse and XY circuits execute in ~44 to 46 ms total latency**.
- Analytical statevector contraction in Qiskit is genuinely fast ($\sim 17\text{ ms}$ for $N=12$), but the acceleration is an inherent property of exact linear algebra on classical CPUs at small $N$, not a novel algorithmic quantum breakthrough.

---

## 4. THE CLASSICAL SPEED COMPARISON

The most significant latency finding is the comparison against classical solvers:

- **Classical Kernighan-Lin:** Executes complete bipartitioning search in **1.63 ms**, with total pipeline time (including VND fleet evaluation) of **3.65 ms**.
- **Speedup of Classical over QAOA:**
  $$\text{Speedup}(\text{Classical vs. Genuine QAOA}) = \frac{44.41\text{ ms}}{3.65\text{ ms}} = 12.17\times$$
  $$\text{Speedup}(\text{Classical vs. Baseline QAOA}) = \frac{145.64\text{ ms}}{3.65\text{ ms}} = 39.90\times$$

### Conclusion
Even the fastest simulated QAOA variant requires over $12\times$ the computational budget of classical Kernighan-Lin. In an operational logistics environment where fleet dispatchers must re-route thousands of vehicles dynamically, unassisted QAOA simulation creates an unacceptable computational penalty unless guarded by an adaptive classifier that prunes unpromising invocations.

