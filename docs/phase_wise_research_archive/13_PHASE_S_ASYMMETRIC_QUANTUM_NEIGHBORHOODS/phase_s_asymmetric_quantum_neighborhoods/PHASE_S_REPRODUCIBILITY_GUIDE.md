# Phase S Deliverable 14: Reproducibility & Verification Guide

**Document:** `phase_s_asymmetric_quantum_neighborhoods/PHASE_S_REPRODUCIBILITY_GUIDE.md`  
**Date:** 2026-11-06  
**Status:** Completed & Rigorously Verified  
**Branch:** `research/phase-s-asymmetric-quantum-neighborhoods`

---

## 1. System Requirements

All benchmarks are deterministic and reproducible using:
- **Operating System:** Windows 11 Enterprise (x86_64)
- **Python Binary:** `C:\Python314\python.exe`
- **Installed Packages:**
  - `qiskit == 2.4.1`
  - `qiskit-aer == 0.17.2`
  - `pyspark == 4.2.0`
  - `ortools == 9.15.6755`
  - `scipy >= 1.15.0`
  - `numpy >= 2.0.0`
  - `pandas >= 3.0.0`
- **Active Research Branch:** `research/phase-s-asymmetric-quantum-neighborhoods`
- **Protected Branch:** `main` (Untouched)

---

## 2. Reproduction Commands

From the workspace root (`d:\UROP\smart-delivery-route-optimization`):

### Step 1: Execute Phase S Solvers Unit Test Suite
```bash
C:\Python314\python.exe -m pytest phase_s_asymmetric_quantum_neighborhoods/tests/test_asymmetric_classical_solvers.py -v
```
- **Expected Outcome:** 1 passed in $< 0.5\text{ seconds}$.

### Step 2: Reproduce 20-Instance Asymmetric Quantum vs Classical Benchmark
```bash
C:\Python314\python.exe phase_s_asymmetric_quantum_neighborhoods/benchmarks/benchmark_asymmetric_neighborhoods_exhaustive.py
```
- **Output:** `phase_s_asymmetric_quantum_neighborhoods/results/phase_s_asymmetric_neighborhoods_raw.csv`
- **Expected Runtime:** $\approx 35\text{ seconds}$

### Step 3: Verify Full Production Test Suite (Zero Regression)
```bash
C:\Python314\python.exe -m pytest backend/tests/ -q
```
- **Expected Outcome:** 38 passed in $\approx 115\text{ seconds}$.

---

## 3. Raw Data Manifest

| File Path | Description | Records |
| :--- | :--- | :---: |
| `phase_s_asymmetric_quantum_neighborhoods/results/phase_s_asymmetric_neighborhoods_raw.csv` | 20 asymmetric instances evaluated across 11 algorithms | 20 |
| `phase_s_asymmetric_quantum_neighborhoods/results/phase_s_complete_routes_raw.csv` | Complete-route fleet benchmarks ($N=10$ to $100$) | 4 |

