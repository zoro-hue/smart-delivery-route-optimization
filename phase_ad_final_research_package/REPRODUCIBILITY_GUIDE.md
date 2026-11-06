# ROUTE/IQ: INDEPENDENT REPRODUCIBILITY GUIDE & EXECUTION MANIFEST

**Project:** Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing  
**Institution:** SRM University-AP, Amaravati, Andhra Pradesh  
**Supervisor:** Dr. Vishnu Prasad Verma  
**Team:** J. Jayanth, B. Kaivalya, P. Shyam Sai  
**Scope:** Complete Step-by-Step Instructions to Reproduce All Artifacts, Benchmarks, and Tests  

---

## 1. System Requirements & Runtime Environment

To replicate the results reported in ROUTE/IQ, the host machine must satisfy the following specifications:

| Component | Verified Specification | Notes |
| :--- | :--- | :--- |
| **Operating System** | Windows 11 Enterprise / Ubuntu 22.04 LTS (x86_64) | Tested on Windows 11 (AMD64) |
| **Python** | `3.14.2` | Core execution environment (`C:\Python314\python.exe`) |
| **Java Runtime** | OpenJDK 17.0.x / Temurin 17 | Required for Apache Spark JVM runtime (`JAVA_HOME`) |
| **Physical Memory** | $\ge 16\text{ GB RAM}$ | Required for 100,000-stop Spark scaling & statevector cache |
| **Disk Space** | $\ge 10\text{ GB Free Space}$ | For PySpark temp files, logs, and benchmark CSVs |

### Verified Python Dependency Versions
```
pyspark == 4.2.0
qiskit == 2.4.1
ortools == 9.15.6755
numpy == 2.4.3
scipy == 1.17.1
pandas == 3.0.5
pytest == 9.1.1
fastapi >= 0.115.0
pydantic >= 2.10.0
```

---

## 2. Repository Layout & Module Classification

It is vital to distinguish the production application code from the standalone autonomous research packages:

```
smart-delivery-route-optimization/
├── backend/                                   [PRODUCTION APPLICATION]
│   ├── app/main.py                            -> FastAPI application root (untouched baseline)
│   ├── app/api/routes/optimization.py         -> Live API endpoints (/api/optimize)
│   └── tests/                                 -> 38 Regression tests
├── frontend/                                  [PRODUCTION UI]
│   └── src/                                   -> React / Vite optimization dashboard
├── phase_ab_cooperative_optimization_engine/  [RESEARCH PACKAGE 1]
│   ├── engine/                                -> Spark, QAOA, Tabu, Controller, Guardrail
│   ├── benchmarks/                            -> 30-instance complete system benchmark
│   └── results/                               -> phase_ab_complete_benchmark_raw.csv
├── phase_ac_independent_validation/          [RESEARCH PACKAGE 2 - AUDIT SUITE]
│   ├── benchmarks/                            -> Held-out controller audit & Spark audit
│   ├── tests/                                 -> 11 Adversarial guardrail tests
│   └── results/                               -> Reproduced raw CSV outputs
└── phase_ad_final_research_package/           [RESEARCH PACKAGE 3 - FINAL DELIVERABLES]
    ├── ROUTE_IQ_FINAL_RESEARCH_PAPER.md       -> Academic research paper
    ├── SUPERVISOR_BRIEFING.md                 -> Executive briefing for supervisor
    ├── ROUTE_IQ_FINAL_PRESENTATION.md         -> 15-Slide defense presentation
    ├── VIVA_QUESTIONS_AND_ANSWERS.md          -> 38 Viva defense Q&A guide
    ├── REPRODUCIBILITY_GUIDE.md               -> This document
    ├── FINAL_CLAIMS_AUDIT.md                  -> Final claims classification matrix
    └── ARCHITECTURE_DIAGRAMS.md               -> Canonical Mermaid diagrams
```

---

## 3. Step-by-Step Reproduction Workflow

Open PowerShell (Windows) or Bash (Linux) in the repository root directory (`D:\UROP\smart-delivery-route-optimization`).

### Step 1: Verify Git Safety & Protected Baseline
```powershell
# 1. Verify working branch
git branch --show-current
# Expected output: research/phase-ad-final-research-package

# 2. Verify protected main baseline commit hash
git rev-parse main
# Expected output: a8eb849988201d7929566f331c1ae3afac09b632

# 3. Verify working tree is clean
git status
# Expected output: nothing to commit, working tree clean
```

---

### Step 2: Execute Complete Repository Test Suite (57 Tests)
Run all three test suites to verify system health and absence of regressions:

```powershell
# A. Run backend regression test suite (38 tests)
C:\Python314\python.exe -m pytest backend/tests/ -q
# Expected output: 38 passed in ~170s

# B. Run Phase AB cooperative engine unit tests (5 tests)
C:\Python314\python.exe -m pytest phase_ab_cooperative_optimization_engine/tests/ -v
# Expected output: 5 passed in ~14s

# C. Run Phase AC adversarial guardrail and reproducibility tests (14 tests)
C:\Python314\python.exe -m pytest phase_ac_independent_validation/tests/ -v
# Expected output: 14 passed in ~28s
```
**Total Expected Test Outcome:** **57 passed, 0 failed, 0 skipped.**

---

### Step 3: Reproduce the 30-Instance Complete System Benchmark
This reproduces the 240 evaluations across Configurations A through H:

```powershell
C:\Python314\python.exe phase_ab_cooperative_optimization_engine/benchmarks/benchmark_complete_system.py
```
- **Output Artifact:** `phase_ab_cooperative_optimization_engine/results/phase_ab_complete_benchmark_raw.csv`
- **Expected Runtimes:**
  - Config A (Sequential Incumbent): $0.04\text{ ms}$
  - Config B (OR-Tools + VND): $8.27\text{ ms}$
  - Config D (Tabu Search + VND): $33.85\text{ ms}$
  - Config F (Fast QAOA + VND): $644.85\text{ ms}$
  - Config G (Adaptive Controller + VND): $34.87\text{ ms}$
- **Numerical Verification:** Re-running this script produces bit-for-bit identical floats ($0.000000\text{ km}$ deviation).

---

### Step 4: Reproduce Apache Spark Scalability Benchmark
This benchmarks Spark against in-memory NumPy across $N \in [1k, 10k, 50k, 100k]$ delivery stops:

```powershell
C:\Python314\python.exe phase_ac_independent_validation/benchmarks/reproduce_spark_scalability.py
```
- **Output Artifact:** `phase_ac_independent_validation/results/phase_ac_spark_scalability_reproduced.csv`
- **Expected Runtimes (Spark local[*]):**
  - $N = 1,000$: $\approx 6.5\text{ seconds}$ (JVM session initialization)
  - $N = 10,000$: $\approx 1.1\text{ seconds}$
  - $N = 50,000$: $\approx 2.1\text{ seconds}$
  - $N = 100,000$: $\approx 3.3\text{ seconds}$
- **Semantic Equivalence Check:** `boundary_match_pandas` evaluates to `True` for every scale.

---

### Step 5: Reproduce Leakage-Safe Controller Held-Out Audit
This executes the 30-instance held-out evaluation with dynamically variable capacity slack and density:

```powershell
C:\Python314\python.exe phase_ac_independent_validation/benchmarks/audit_adaptive_controller.py
```
- **Output Artifact:** `phase_ac_independent_validation/results/phase_ac_controller_audit_raw.csv`
- **Expected Dispatch Distribution:**
  - Tabu Search: 14 instances (46.7%)
  - Random Feasible: 9 instances (30.0%)
  - Fast QAOA: 6 instances (20.0%)
  - Multistart KL: 1 instance (3.3%)
- **Expected Distances:** Adaptive Controller achieves $\approx 595.11\text{ km}$, matching Always Tabu ($595.12\text{ km}$) while QAOA averages $602.16\text{ km}$.

---

## 4. Deterministic Random Seed Manifest

Exact reproduction depends on deterministic pseudo-random number generator (PRNG) seeds:

| Benchmark / Test Suite | Seed Formula | Description |
| :--- | :--- | :--- |
| **Complete System Benchmark (Phase AB)** | `seed = 400 + instance_id` ($i \in [0, 29]$) | Generates reproducible coordinates, demands, and initial routes |
| **Spark Scalability Consolidation** | `seed = 42` | Generates reproducible New York coordinates across $1k$ to $100k$ |
| **Controller Held-Out Audit (Phase AC)** | `seed = 1000 + instance_id` ($i \in [0, 29]$) | Generates independent held-out instances with variable slack |
| **Adversarial Guardrail Stress Suite** | Hardcoded matrices | Hardcoded edge cases in `test_guardrail_adversarial.py` |

---

## 5. Known Environment Limitations

1. **Pandas 3.0+ Deprecation Warnings:** When running PySpark 4.2.0 with Pandas 3.0.5, PySpark emits `FutureWarning: PySpark does not yet fully support pandas >= 3.0.0`. These warnings are benign and do not affect numerical calculations.
2. **Pydantic V2 Config Deprecation:** In `backend/app/core/config.py`, Pydantic emits a deprecation warning regarding class-based `config`. This does not impact test execution.
3. **Hardware Requirement for QAOA:** Classical CPU statevector simulation requires exponential memory $O(2^N)$. Do not increase `max_boundary_size` beyond 20 qubits on standard 16 GB workstations.
