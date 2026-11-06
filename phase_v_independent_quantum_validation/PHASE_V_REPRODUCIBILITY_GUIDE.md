# Deliverable 13: Phase V Scientific Reproducibility Guide

## 1. System & Runtime Environment

- **Operating System**: Microsoft Windows 11 / Windows Server (x86_64)
- **Python Runtime**: Python 3.14.2
- **Key Installed Packages**:
  - `qiskit` == 2.4.1
  - `qiskit-aer` == 0.17.2
  - `pyspark` == 4.2.0
  - `ortools` == 9.15.6755
  - `scipy` == 1.15.0
  - `numpy` == 2.2.3
  - `pytest` == 9.1.1
  - `pandas` == 3.0.0

---

## 2. Independent Reproduction Commands

### Step 1: Verify Clean Environment and Active Branch
```powershell
git status
# Active branch must be research/phase-v-independent-quantum-validation
```

### Step 2: Run Algorithmic VND Unit Tests
```powershell
C:\Python314\python.exe -m pytest phase_v_independent_quantum_validation/tests/test_algorithmic_vnd.py -v
# Expected: 1 passed in ~0.15s
```

### Step 3: Run Full Regression Test Suite
```powershell
C:\Python314\python.exe -m pytest backend/tests/ -q
# Expected: 38 passed in ~140s
```

### Step 4: Execute Critical Causal Ablation Benchmark
```powershell
C:\Python314\python.exe phase_v_independent_quantum_validation/benchmarks/benchmark_causal_ablation.py
# Generates phase_v_independent_quantum_validation/results/phase_v_causal_ablation_raw.csv (150 records)
```

### Step 5: Recompute Statistical Summaries & Significance Tests
```powershell
C:\Python314\python.exe -c "
import pandas as pd
from scipy import stats
df = pd.read_csv('phase_v_independent_quantum_validation/results/phase_v_causal_ablation_raw.csv')
piv = df.pivot(index='instance_id', columns='config_name', values='route_distance_km')
print(df.groupby('config_name')['route_distance_km'].agg(['mean', 'std', 'min', 'max']))
print('B vs D (ORTools+VND vs QAOA+VND):', stats.ttest_rel(piv['Config_B_ORTools_VND'], piv['Config_D_ORTools_QAOA_VND']))
"
```
