# Deliverable 6: Phase V QAOA Execution Telemetry & Performance Tracking

## 1. QAOA Execution Telemetry Parameters

All quantum circuits were executed using Qiskit Aer simulation under the following standardized parameters:
- **Logical Qubits**: $N = 12$ boundary customer nodes.
- **Circuit Depth**: $p = 1$ alternating layers (cost layer $e^{-i\gamma H_C}$, mixer layer $e^{-i\beta H_M}$).
- **Mixer**: Standard transverse-field mixer $H_M = \sum_{i=1}^N X_i$.
- **Parameter Optimization**: COBYLA optimizer with initial parameters $(\gamma_0, \beta_0) = (0.35, 0.65)$, max iterations $= 40$.
- **Measurement Shots**: 1,024 shots per circuit evaluation.

---

## 2. Telemetry Summary Across Benchmark Instances

| Telemetry Metric | Measured Value | Scientific Interpretation |
| :--- | :---: | :--- |
| **Total QAOA Executions** | 15 runs | Evaluated across 15 independent boundary instances |
| **Mean Circuit Compilation & Sim Time** | 120.88 ms | Dominated by statevector/shot simulation overhead |
| **Mean Classical Optimization Time** | 12.71 ms | Multistart local search and VND refinement |
| **Total Hybrid Execution Time** | 133.59 ms | Total wall-clock time per subproblem |
| **Raw Capacity Feasibility Rate** | 44.92% | Only ~45% of sampled states satisfy capacity constraints |
| **Post-Repair Capacity Feasibility Rate** | 100.0% | Deterministic classical repair restores 100% feasibility |
| **Useful Candidate Rate (Complete Route)** | **26.67%** (4/15) | Only 4 calls yielded a route improvement after VND |
| **Incumbent Improvement Rate (QUBO Cost)**| **40.00%** (6/15) | 6 calls found a repaired partition beating classical seed |
| **Proposition 1 Acceptance Rate** | **100.0%** (15/15) | Guardrail rejected 11 non-improving calls with 0 degradation |
| **Mean Distance Improvement (Useful Calls)** | **39.30 km** | Sizable reduction in the 4 successful instances |
| **Mean Distance Improvement (Overall)** | **15.72 km** | Diluted across all 15 instances |
| **Average Overhead of Unsuccessful Calls** | +120.88 ms | Pure computational tax when classical fallback occurred |

---

## 3. Telemetry Findings

1. **Selective Utility**:
   - QAOA does not provide a universal advantage across all instances. In 73.33% of executions, the quantum candidate is inferior to the classical incumbent.
2. **Value of the Proposition 1 Guardrail**:
   - Because the guardrail automatically rejects non-improving candidates ($73.33\%$ rejection rate), the final dispatch plan never suffers degradation.
3. **Overhead Penalty**:
   - In the $73.33\%$ of cases where QAOA failed to improve the incumbent, the system incurred a $\approx 121\text{ ms}$ simulation delay with zero routing gain.
