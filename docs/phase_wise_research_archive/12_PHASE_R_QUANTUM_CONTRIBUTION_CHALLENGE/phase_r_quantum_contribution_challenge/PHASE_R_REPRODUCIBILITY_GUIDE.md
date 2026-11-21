# Phase R Deliverable 12: Reproducibility & Verification Guide

**Document:** `phase_r_quantum_contribution_challenge/PHASE_R_REPRODUCIBILITY_GUIDE.md`  
**Date:** 2026-11-06  
**Status:** Completed & Rigorously Verified  
**Branch:** `research/phase-r-quantum-contribution-challenge`

---

## 1. Environment & Hardware Specifications

All Phase R benchmarks are fully deterministic and reproducible using the following environment configuration:

- **Operating System:** Windows 11 Enterprise (x86_64)
- **Python Environment:** Python 3.14 (Path: `C:\Python314\python.exe`)
- **Key Scientific Packages:**
  - `qiskit == 2.4.1`
  - `qiskit-aer == 0.17.2`
  - `pyspark == 4.2.0`
  - `ortools == 9.15.6755`
  - `numpy >= 2.0.0`
  - `pandas >= 3.0.0`
  - `scipy >= 1.15.0`
- **Git Branch:** `research/phase-r-quantum-contribution-challenge`
- **Protected Branch (Untouched):** `main`

---

## 2. Step-by-Step Reproduction Instructions

Execute all commands from the repository root: `D:\UROP\smart-delivery-route-optimization`.

### Step 1: Reproduce Strong Classical Baselines
```bash
C:\Python314\python.exe phase_r_quantum_contribution_challenge/benchmarks/benchmark_strong_classical_incumbents.py
```
- **Output:** `phase_r_quantum_contribution_challenge/results/phase_r_classical_incumbents_raw.csv`
- **Verified Runtime:** $\approx 35\text{ seconds}$

### Step 2: Reproduce In-Neighborhood Quantum vs Classical Competition
```bash
C:\Python314\python.exe phase_r_quantum_contribution_challenge/benchmarks/benchmark_neighborhood_quantum_vs_classical.py
```
- **Output:** `phase_r_quantum_contribution_challenge/results/phase_r_neighborhood_competition_raw.csv`
- **Verified Runtime:** $\approx 12\text{ seconds}$

### Step 3: Reproduce 6 Cooperative Architectures Benchmark
```bash
C:\Python314\python.exe phase_r_quantum_contribution_challenge/benchmarks/benchmark_cooperative_architectures.py
```
- **Output:** `phase_r_quantum_contribution_challenge/results/phase_r_cooperative_architectures_raw.csv`
- **Verified Runtime:** $\approx 120\text{ seconds}$

### Step 4: Reproduce Apache Spark Scaling Benchmark
```bash
C:\Python314\python.exe phase_r_quantum_contribution_challenge/benchmarks/benchmark_spark_scaling.py
```
- **Output:** `phase_r_quantum_contribution_challenge/results/phase_r_spark_scaling_raw.csv`
- **Verified Runtime:** $\approx 25\text{ seconds}$

### Step 5: Verify Full Backend Regression Test Suite
```bash
C:\Python314\python.exe -m pytest backend/tests/ -q
```
- **Expected Outcome:** 38 passed, 0 failed.

---

## 3. Raw Data Manifest

| File Path | Description | Records |
| :--- | :--- | :---: |
| `phase_r_quantum_contribution_challenge/results/phase_r_classical_incumbents_raw.csv` | Industrial classical solvers across 10 instances | 10 |
| `phase_r_quantum_contribution_challenge/results/phase_r_neighborhood_competition_raw.csv` | 8-method competition on 12 asymmetric subproblems | 12 |
| `phase_r_quantum_contribution_challenge/results/phase_r_cooperative_architectures_raw.csv` | 6 cooperative architectures on complete routes | 10 |
| `phase_r_quantum_contribution_challenge/results/phase_r_spark_scaling_raw.csv` | Spark vs Pandas scaling across $N \in [10, 1000]$ | 7 |

