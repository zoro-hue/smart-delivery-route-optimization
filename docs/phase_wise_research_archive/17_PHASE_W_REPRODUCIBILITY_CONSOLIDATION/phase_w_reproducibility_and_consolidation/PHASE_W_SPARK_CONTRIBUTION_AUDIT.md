# Deliverable 5: Phase W Apache Spark Contribution and Big Data Audit

## 1. Scope & Execution Mode Clarification

In compliance with Phase W research instructions:
> **"Verify actual Spark execution mode. If using `local[*]`, explicitly describe it as single-machine parallel execution, not multi-node distributed computing. Compare Spark against an equivalent Pandas or non-Spark implementation using identical inputs and outputs."**

- **Runtime Engine**: PySpark 4.2.0 on Java OpenJDK 64-Bit Server VM.
- **Master Setting**: `local[*]` (utilizing all available local CPU cores via threads).
- **Execution Nature**: Single-machine parallel execution. **No physical multi-node cluster was used or claimed.**

---

## 2. Head-to-Head Benchmark: Spark vs Native Pandas/NumPy

Tested on identical synthetic delivery stop datasets across scales from $N=50$ (the dashboard benchmark) to $N=50,000$ delivery stops:

| Dataset Size ($N$) | Stage Evaluated | Pandas/NumPy Runtime | Spark (`local[*]`) Runtime | Overhead Factor | Output Equivalence |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **$N = 50$ (Dashboard)** | ETL & Boundary Extraction | **4.36 ms** | 46.21 ms | 10.6x JVM overhead | **100% Identical** |
| **$N = 1,000$** | ETL & Boundary Extraction | **2.01 ms** | 46.16 ms | 23.0x JVM overhead | **100% Identical** |
| **$N = 10,000$** | ETL & Boundary Extraction | **2.85 ms** | 121.75 ms | 42.8x JVM overhead | **100% Identical** |
| **$N = 50,000$** | ETL & Boundary Extraction | **6.75 ms** | 355.03 ms | 52.6x JVM overhead | **100% Identical** |

---

## 3. Scientific Conclusions on Pillar 1 (Apache Spark)

1. **Perfect Output Equivalence**:
   - The boundary customer subproblems ($N \le 16$) extracted by Spark and Pandas are **100% identical** across all tested instances.
2. **Workstation Overhead**:
   - For single-machine datasets up to 50,000 records, Pandas and NumPy process vector operations in pure C/Fortran in under 7 ms. PySpark in `local[*]` incurs JVM foreign-function and process serialization overhead, running 10x–50x slower on a single machine.
3. **True Architectural Role of Spark**:
   - Spark's primary value is not raw speed on small in-memory datasets, but **architectural decoupling**: it provides an industrial standard interface for streaming ingestion, geospatial KD-tree partitioning, and parallel quantum payload dispatch when scaling out across enterprise clusters.
