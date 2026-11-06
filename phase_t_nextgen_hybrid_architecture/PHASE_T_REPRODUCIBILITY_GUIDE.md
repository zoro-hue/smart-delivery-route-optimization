# Phase T Deliverable 15: Reproducibility & Verification Guide

**Document:** `phase_t_nextgen_hybrid_architecture/PHASE_T_REPRODUCIBILITY_GUIDE.md`  
**Date:** 2026-11-06  
**Status:** Completed & Rigorously Verified  
**Branch:** `research/phase-t-nextgen-hybrid-architecture`

---

## 1. Environment & Dependencies

All Phase T benchmarks are deterministic and reproducible using:
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
- **Active Research Branch:** `research/phase-t-nextgen-hybrid-architecture`
- **Protected Branch:** `main` (commit `a8eb849`, Untouched)

---

## 2. Step-by-Step Reproduction Instructions

From the workspace root (`d:\UROP\smart-delivery-route-optimization`):

### Step 1: Execute NextGen Engine Unit Test Suite
```bash
C:\Python314\python.exe -m pytest phase_t_nextgen_hybrid_architecture/tests/test_nextgen_engine.py -v
```
- **Expected Outcome:** 3 passed in $\approx 7\text{ seconds}$.

### Step 2: Reproduce Comprehensive Scalable Benchmark ($N=10$ to $1,000$)
```bash
C:\Python314\python.exe phase_t_nextgen_hybrid_architecture/benchmarks/benchmark_phase_t_comprehensive.py
```
- **Output:** `phase_t_nextgen_hybrid_architecture/results/phase_t_comprehensive_benchmark_raw.csv`
- **Expected Runtime:** $\approx 60\text{ seconds}$.

### Step 3: Verify Full Backend Production Test Suite (Zero Regression)
```bash
C:\Python314\python.exe -m pytest backend/tests/ -q
```
- **Expected Outcome:** 38 passed in $\approx 115\text{ seconds}$.

---

## 3. Raw Data Manifest

| File Path | Description | Records |
| :--- | :--- | :---: |
| `phase_t_nextgen_hybrid_architecture/results/phase_t_comprehensive_benchmark_raw.csv` | Comprehensive benchmark across 7 problem scales ($N=10$ to $1,000$) | 7 |
