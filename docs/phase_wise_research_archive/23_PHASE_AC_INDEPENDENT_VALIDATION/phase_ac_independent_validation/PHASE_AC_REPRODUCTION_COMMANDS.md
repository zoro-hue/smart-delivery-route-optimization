# PHASE AC DELIVERABLE 13: REPRODUCTION COMMANDS & MANIFEST

## Project Information
- **Project:** ROUTE/IQ — Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing
- **Institution:** SRM University-AP | **Supervisor:** Dr. Vishnu Prasad Verma
- **Audit Branch:** `research/phase-ac-independent-validation`

---

## 1. Environment Requirements

- **Operating System:** Windows 11 (AMD64)
- **Python:** 3.14.2 (`C:\Python314\python.exe`)
- **Java:** OpenJDK 17 (`JAVA_HOME`)
- **Core Packages:** `pyspark==4.2.0`, `qiskit==2.4.1`, `ortools==9.15.6755`, `numpy==2.4.3`, `scipy==1.17.1`, `pandas==3.0.5`, `pytest==9.1.1`

---

## 2. Complete Independent Reproduction Workflow

### Step 1: Verify Git Tree & Safeguards
```powershell
git status
git rev-parse HEAD
# Expected: Commit on research/phase-ac-independent-validation
git rev-parse main
# Expected: a8eb849988201d7929566f331c1ae3afac09b632
```

### Step 2: Execute Existing Backend Regression Tests (38 tests)
```powershell
C:\Python314\python.exe -m pytest backend/tests/ -q
# Expected: 38 passed in ~170s
```

### Step 3: Execute Phase AB Unit Tests (5 tests)
```powershell
C:\Python314\python.exe -m pytest phase_ab_cooperative_optimization_engine/tests/ -v
# Expected: 5 passed in ~14s
```

### Step 4: Execute Phase AC Adversarial & Reproducibility Tests (14 tests)
```powershell
C:\Python314\python.exe -m pytest phase_ac_independent_validation/tests/ -v
# Expected: 14 passed in ~28s
```

### Step 5: Reproduce Complete System Benchmark (30 instances, 240 evaluations)
```powershell
C:\Python314\python.exe phase_ab_cooperative_optimization_engine/benchmarks/benchmark_complete_system.py
# Generates: phase_ab_cooperative_optimization_engine/results/phase_ab_complete_benchmark_raw.csv
```

### Step 6: Reproduce Spark Scalability Benchmark
```powershell
C:\Python314\python.exe phase_ac_independent_validation/benchmarks/reproduce_spark_scalability.py
# Generates: phase_ac_independent_validation/results/phase_ac_spark_scalability_reproduced.csv
```

### Step 7: Reproduce Leakage-Safe Controller Held-Out Audit (30 instances)
```powershell
C:\Python314\python.exe phase_ac_independent_validation/benchmarks/audit_adaptive_controller.py
# Generates: phase_ac_independent_validation/results/phase_ac_controller_audit_raw.csv
```

---

## 3. Seed Manifest for Exact Deterministic Reproduction

- **Phase AB Complete Benchmark:** `seed = 400 + instance_id` ($i \in [0, 29]$).
- **Phase AB Spark Scalability:** `seed = 42`.
- **Phase AC Controller Held-Out Audit:** `seed = 1000 + instance_id` ($i \in [0, 29]$).
- **Phase AC Guardrail Adversarial Tests:** Deterministic coordinates and matrices hardcoded in `test_guardrail_adversarial.py`.
