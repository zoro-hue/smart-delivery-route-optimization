# Deliverable 15: Phase U Scientific Reproducibility Guide

## 1. Environment Specifications

- **Operating System**: Microsoft Windows 11 / Windows Server
- **Python Runtime**: Python 3.14.2 (x86_64)
- **Primary Libraries**:
  - `qiskit` == 2.4.1
  - `qiskit-aer` == 0.17.2
  - `pyspark` == 4.2.0
  - `ortools` == 9.15.6755
  - `scipy` == 1.15.0
  - `numpy` == 2.2.3
  - `pytest` == 9.1.1

---

## 2. Step-by-Step Reproduction Commands

### Step 1: Verify Clean Environment and Git Baseline
```powershell
git status
# Branch must be research/phase-u-quantum-bipartition-validation
```

### Step 2: Run Full Production Regression Test Suite
```powershell
C:\Python314\python.exe -m pytest backend/tests/ -q
# Expected: 38 passed in ~133s
```

### Step 3: Run Classical Partitioning Solver Unit Tests
```powershell
C:\Python314\python.exe -m pytest phase_u_quantum_bipartition_validation/tests/test_classical_partition_solvers.py -v
# Expected: 1 passed in ~0.2s
```

### Step 4: Execute Controlled Ablation Benchmark
```powershell
C:\Python314\python.exe phase_u_quantum_bipartition_validation/benchmarks/benchmark_ablation_study.py
# Generates phase_u_quantum_bipartition_validation/results/phase_u_ablation_raw.csv (150 records)
```

### Step 5: Generate Statistical and Feasibility Summaries
```powershell
C:\Python314\python.exe -c "
import pandas as pd
df = pd.read_csv('phase_u_quantum_bipartition_validation/results/phase_u_ablation_raw.csv')
print(df.groupby('config_name').mean())
"
```
