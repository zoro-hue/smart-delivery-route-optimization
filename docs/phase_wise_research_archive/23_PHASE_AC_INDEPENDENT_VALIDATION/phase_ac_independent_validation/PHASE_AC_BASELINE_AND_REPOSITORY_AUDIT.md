# PHASE AC DELIVERABLE 2: BASELINE & REPOSITORY AUDIT

## Project Information
- **Project:** ROUTE/IQ — Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing
- **Repository:** `D:\UROP\smart-delivery-route-optimization`
- **Supervisor:** Dr. Vishnu Prasad Verma, SRM University-AP
- **Active Branch:** `research/phase-ac-independent-validation`
- **Audit Target Branch:** `research/phase-ab-cooperative-optimization-engine`
- **Expected Phase AB Commit:** `5ae91a9ea49f2bf4a785ad1c69b9a4938a46b6cd`
- **Verified Phase AB Commit:** `5ae91a9ea49f2bf4a785ad1c69b9a4938a46b6cd` (Exact Match)
- **Protected Main Baseline:** `a8eb849988201d7929566f331c1ae3afac09b632` (Verified Untouched)

---

## 1. Repository Safety Verification

Before undertaking any computational or statistical analysis, the repository environment was audited against strict safety protocols:

1. **Main Branch Isolation:**
   - Git command `git rev-parse main` confirmed commit hash: `a8eb849988201d7929566f331c1ae3afac09b632`.
   - Main branch has not been merged, modified, rebased, or reset.
2. **Phase AB Commit Verification:**
   - Git command `git rev-parse HEAD` on the base branch confirmed: `5ae91a9ea49f2bf4a785ad1c69b9a4938a46b6cd`.
   - The tree was clean prior to branching.
3. **Dedicated Audit Branch:**
   - Created and switched to `research/phase-ac-independent-validation`.
4. **Historical File Integrity:**
   - Zero files in `phase_ab_cooperative_optimization_engine/`, `backend/`, or `frontend/` have been altered or deleted. All Phase AB artifacts and CSV outputs remain pristine.

---

## 2. Environment & Dependency Inventory

The runtime environment was inventoried directly via Python 3.14 introspective inspection:

| Component | Verified Version | Environment / Path | Role in Architecture |
| :--- | :--- | :--- | :--- |
| **Python** | `3.14.2 (AMD64)` | `C:\Python314\python.exe` | Base Runtime Environment |
| **PySpark** | `4.2.0` | Ingested via Python 3.14 site-packages | Pillar 1: Big Data Distributed Processing |
| **Qiskit** | `2.4.1` | Python 3.14 site-packages | Pillar 2: Quantum Circuit & QAOA Construction |
| **Google OR-Tools** | `9.15.6755` | Python 3.14 site-packages | Classical Optimization / Incumbent Solver |
| **NumPy** | `2.4.3` | Python 3.14 site-packages | Numerical linear algebra & matrix operations |
| **SciPy** | `1.17.1` | Python 3.14 site-packages | Statistical hypothesis testing (paired t, Wilcoxon) |
| **Pandas** | `3.0.5` | Python 3.14 site-packages | Tabular data logging and CSV processing |
| **FastAPI** | `0.115.0+` | `backend/app/` | Production REST API (untouched baseline) |
| **Java Runtime** | `OpenJDK 17.0.x` | `JAVA_HOME` | JVM substrate for Apache Spark execution |

---

## 3. Structural Inventory of Phase AB Codebase

The audit inspected all 27 committed files within `phase_ab_cooperative_optimization_engine/`:

- **Engine Core:**
  - `spark_preprocessor.py`: Implements `SparkWorkloadOrganizer` with PySpark DataFrame and in-memory NumPy fallback.
  - `candidate_generators.py`: Implements `UniformRandomGenerator`, `KernighanLinGenerator`, `TabuSearchGenerator`, `QAOACandidateGenerator`.
  - `classical_engine.py`: Implements `ClassicalOptimizationEngine` with `generate_ortools_incumbent`, `refine_with_vnd`, and tour extraction.
  - `adaptive_controller.py`: Implements `AdaptiveCooperativeController` Multi-Armed Bandit with feature-conditioned gating.
  - `proposition1_guardrail.py`: Centralized `Proposition1Guardrail` non-degradation and capacity filter.
  - `cooperative_engine.py`: Master orchestrator coordinating Spark, Controller, Generators, VND, and Guardrail.
- **Benchmarks & Data:**
  - `benchmarks/benchmark_complete_system.py`: 30-instance complete system benchmark (240 evaluations).
  - `benchmarks/benchmark_spark_scalability_consolidation.py`: Spark scaling benchmark across $N \in [1k, 10k, 50k, 100k]$.
  - `results/phase_ab_complete_benchmark_raw.csv`: 240 raw benchmark evaluation rows.
  - `results/phase_ab_spark_scalability_raw.csv`: 8 scaling measurement records.
- **Cluster Deployment:**
  - `cluster/docker-compose.yml`: Master + 2 Worker Spark cluster configuration.
  - `cluster/Dockerfile`: Container image build for Spark 4.2.0.
  - `cluster/spark-defaults.conf`: Spark JVM execution settings.
- **Test Suite:**
  - `tests/test_cooperative_engine.py`: 5 unit and integration tests.
- **Documentation:**
  - Deliverables 1 through 13 covering architecture, benchmarks, statistics, and master report.

---

## 4. Initial Audit Findings & Observations

1. **Pristine State:** The repository is fully intact and compiles cleanly under Python 3.14.2.
2. **Traceability:** Raw benchmark CSVs match the commit tree and contain full per-instance observations.
3. **Label Discrepancy Flag:** `generate_ortools_incumbent` in `classical_engine.py` was discovered to execute a sequential index split rather than calling Google OR-Tools constraint solver, explaining the reported 0.04 ms latency. This is formally analyzed in Deliverables 3 and 4.
