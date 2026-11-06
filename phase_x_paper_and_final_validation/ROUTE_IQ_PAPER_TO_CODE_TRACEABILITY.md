# ROUTE/IQ: Paper-to-Code Traceability Table

## 1. Traceability Protocol

To ensure 100% scientific reproducibility, every numerical table, figure, and quantitative claim in the research paper is mapped directly to its underlying execution script, input dataset, raw CSV record, and Git commit.

---

## 2. Traceability Matrix

| Paper Item / Metric | Numerical Values Reported | Generating Script | Input Parameters / Seeds | Raw Output Data File | Git Commit |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **Table 1: Phase V Independent Reproduction** | Config A: 668.09 km<br>Config B: 559.92 km<br>Config D: 544.20 km<br>Config E: 540.07 km<br>$\Delta(B, D) = -15.72$ km ($p=0.089$) | `phase_w_reproducibility_and_consolidation/benchmarks/benchmark_reproduce_phase_v.py` | Seeds: 100–114<br>$N = 12$<br>Shots: 1024 | `phase_w_reproducibility_and_consolidation/results/phase_w_reproduction_raw.csv` | `1fafc53` |
| **Table 2: Causal Ablation Breakdown** | OR-Tools: 668.09 km<br>VND Alone: 559.92 km<br>VND Contribution: 87.3% | `phase_v_independent_quantum_validation/benchmarks/benchmark_causal_ablation.py` | Seeds: 100–114<br>$N = 12$<br>Real algorithmic VND | `phase_v_independent_quantum_validation/results/phase_v_causal_ablation_raw.csv` | `68ffbbd` |
| **Table 3: Out-of-Sample Boundary Gating** | Always QAOA: 526.35 km<br>Never QAOA: 526.92 km<br>$\Delta = 0.57$ km ($0.11\%$) | `phase_w_reproducibility_and_consolidation/benchmarks/benchmark_qaoa_contribution_boundaries.py` | Train: Seeds 500–519<br>Test: Seeds 600–619<br>$N = 12$ | `phase_w_reproducibility_and_consolidation/results/phase_w_boundary_features_raw.csv` | `1fafc53` |
| **Table 4: QAOA Depth Rigor ($p=1$ vs $p=2$)** | $p=1$: 45.8% viol (148.1 ms)<br>$p=2$: 44.4% viol (303.9 ms)<br>Cost: -29.00 (Identical) | `phase_w_reproducibility_and_consolidation/benchmarks/benchmark_qaoa_depth_and_rigor.py` | Qubits: 12<br>COBYLA: 40/80 evals<br>Shots: 1024 | Standard stdout / execution log | `1fafc53` |
| **Table 5: Spark vs Pandas Preprocessing** | $N=50$: 4.36 ms vs 46.21 ms<br>$N=50k$: 6.75 ms vs 355.03 ms<br>Equivalence: 100% Identical | `phase_w_reproducibility_and_consolidation/benchmarks/benchmark_spark_vs_pandas.py` | Scales: $N \in \{50, 1000, 10000, 50000\}$ | Standard stdout / execution log | `1fafc53` |
| **Table 6: Complete Fleet Routing (Dashboard)** | Clarke-Wright: 217.3 km<br>2-opt: 217.6 km<br>OR-Tools: 218.2 km<br>QAOA Hybrid: 219.7 km | `backend/tests/test_hybrid_quantum_pipeline.py` | 50 Manhattan Stops<br>Capacity $C = 100$ | UI Dashboard Scorecard / Test Logs | `a8eb849` |
| **Proposition 1 Monotonicity Guardrail** | Degradation rate: 0.0%<br>Rejection rate: 73.3%–90.0% | `phase_w_reproducibility_and_consolidation/benchmarks/benchmark_reproduce_phase_v.py` | Verified across all 150 evaluations | `phase_w_reproducibility_and_consolidation/results/phase_w_reproduction_raw.csv` | `1fafc53` |
