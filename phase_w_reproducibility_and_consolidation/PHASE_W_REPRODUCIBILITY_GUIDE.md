# Deliverable 11: Phase W Scientific Reproducibility Guide

## 1. Environment & Dependencies

- **OS**: Microsoft Windows 11 / Windows Server (x86_64)
- **Python Runtime**: Python 3.14.2
- **Required Libraries**:
  - `qiskit` == 2.4.1
  - `qiskit-aer` == 0.17.2
  - `pyspark` == 4.2.0
  - `ortools` == 9.15.6755
  - `scipy` == 1.15.0
  - `numpy` == 2.2.3
  - `pandas` == 3.0.0
  - `pytest` == 9.1.1

---

## 2. Step-by-Step Reproduction Commands

### Step 1: Verify Git Branch & Clean Tree
```powershell
git status
# Active branch must be: research/phase-w-reproducibility-and-consolidation
```

### Step 2: Run Full Production Regression Test Suite
```powershell
C:\Python314\python.exe -m pytest backend/tests/ -q
# Expected: 38 passed, 0 failed in ~180s
```

### Step 3: Run Algorithmic VND Unit Tests
```powershell
C:\Python314\python.exe -m pytest phase_v_independent_quantum_validation/tests/test_algorithmic_vnd.py -v
# Expected: 1 passed in ~0.15s
```

### Step 4: Re-Run Independent Phase V Causal Ablation Benchmark
```powershell
C:\Python314\python.exe phase_w_reproducibility_and_consolidation/benchmarks/benchmark_reproduce_phase_v.py
# Generates phase_w_reproducibility_and_consolidation/results/phase_w_reproduction_raw.csv (150 records)
```

### Step 5: Run Out-of-Sample Contribution Boundary & Gating Experiment
```powershell
C:\Python314\python.exe phase_w_reproducibility_and_consolidation/benchmarks/benchmark_qaoa_contribution_boundaries.py
# Generates phase_w_reproducibility_and_consolidation/results/phase_w_boundary_features_raw.csv (40 records)
```

### Step 6: Run QAOA Depth ($p=1$ vs $p=2$) and Rigor Benchmark
```powershell
C:\Python314\python.exe phase_w_reproducibility_and_consolidation/benchmarks/benchmark_qaoa_depth_and_rigor.py
```

### Step 7: Run Apache Spark vs Pandas Preprocessing Audit
```powershell
C:\Python314\python.exe phase_w_reproducibility_and_consolidation/benchmarks/benchmark_spark_vs_pandas.py
```
