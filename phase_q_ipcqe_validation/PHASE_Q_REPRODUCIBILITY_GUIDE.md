# ROUTE/IQ — PHASE Q: REPRODUCIBILITY & REPLICATION GUIDE
**Complete Guide to Reproducing Phase Q Audits, Warm-Start Tests, and Benchmark Results**

- **Date:** 2026-11-06
- **Branch:** `research/phase-q-ipcqe-validation`
- **Baseline Git Commit:** `e7149f4`

---

## 1. Quick Verification Commands

### Step 1: Run the Warm-Start Mathematical Audit
Verifies the XY hopping mixer row/column validity and Hungarian projection deltas:
```powershell
python phase_q_ipcqe_validation/benchmarks/verify_warm_start_mathematics.py
```
Expected output: Row validity 100.00%, Column validity 31.98% at $\beta=0.35\pi$ and 100% at $\beta=0.50\pi$.

### Step 2: Run the Controlled Subproblem Benchmark
Verifies that Variational QAOA achieves a 100% improvement rate over suboptimal heuristic seeds:
```powershell
python phase_q_ipcqe_validation/benchmarks/test_qaoa_improvement_potential.py
```
Expected output: Overall Improvement Rate 100.0%, Mean Cost Reduction $\approx 37.03\text{ km}$ ($30.03\%$).

### Step 3: Run the Apache Spark Contribution Audit
Verifies PySpark 4.2.0 partitioning, cluster balance, and single-machine comparison across $N=25\text{–}500$:
```powershell
python phase_q_ipcqe_validation/benchmarks/audit_spark_contribution.py
```
Expected output: Cluster balance std dev $< 1.3$, clusters 100% identical to Pandas baseline.

### Step 4: Run the Master Comparative Benchmark Suite
Compares OR-Tools, Clarke-Wright, 2-opt, IP-CQE v1, and IP-CQE v2 across $N=10, 25, 50$:
```powershell
python phase_q_ipcqe_validation/benchmarks/run_phase_q_benchmarks.py
```
Expected output: Raw CSV saved to `phase_q_ipcqe_validation/results/phase_q_benchmark_raw.csv`. 100% feasibility confirmed.

---

## 2. Integrity & Isolation Verification
To confirm that zero live backend API or frontend files were modified:
```powershell
git status
git branch --show-current
```
Branch must be `research/phase-q-ipcqe-validation`. All changes must be strictly untracked within `phase_q_ipcqe_validation/`.

