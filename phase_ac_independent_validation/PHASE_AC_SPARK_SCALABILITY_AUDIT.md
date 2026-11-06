# PHASE AC DELIVERABLE 8: APACHE SPARK SCALABILITY AUDIT

## Project Information
- **Project:** ROUTE/IQ — Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing
- **Institution:** SRM University-AP | **Supervisor:** Dr. Vishnu Prasad Verma
- **Audit Branch:** `research/phase-ac-independent-validation`

---

## 1. Scope & Execution Environment Audit

Phase AB reported scalability benchmarks for Apache Spark 4.2.0 across $N \in [1,000; 10,000; 50,000; 100,000]$ delivery stops.

### Critical Execution Reality Check
- **Execution Target:** The benchmark was executed on single-machine multi-threaded CPU (`master="local[*]"`) using the PySpark JVM bridge on Windows.
- **Physical Multi-Node Cluster:** A Docker Compose cluster configuration is provided in `cluster/docker-compose.yml`, but was **not** deployed as a live distributed physical multi-node cluster during benchmark collection.
- **Data Source:** Synthetic uniform geospatial delivery coordinates generated within the New York metropolitan bounding box ($40.70^\circ\text{N}$ to $40.85^\circ\text{N}$, $-74.02^\circ\text{W}$ to $-73.93^\circ\text{W}$).
- **Audit Finding:** Claims of "distributed scaling" must be accurately qualified as **single-machine multi-core parallel processing**, not distributed multi-node cluster execution.

---

## 2. Independent Reproduction Benchmark Results

Independently executed via `phase_ac_independent_validation/benchmarks/reproduce_spark_scalability.py`:

| Dataset Size ($N$) | Execution Engine | Execution Target | Data Gen (ms) | Ingest & Clean (ms) | Boundary Decomp (ms) | Total Latency (ms) | Throughput (stops/sec) | Boundary Extracted | Boundary Semantic Match | Partitions | Memory (MB) |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1,000** | NumPy Vectorized | Single CPU | 12.56 | 9.74 | 2.83 | **12.57** | 79,548 | 16 | Baseline | 1 | 116.1 |
| **1,000** | Apache Spark 4.2.0 | `local[*]` (Single Node) | 12.56 | 4.14 | 6,559.31* | **6,563.45** | 152 | 16 | **True (100% Match)** | 8 | 145.0 |
| **10,000** | NumPy Vectorized | Single CPU | 4.53 | 7.50 | 4.79 | **12.29** | 813,590 | 16 | Baseline | 1 | 148.4 |
| **10,000** | Apache Spark 4.2.0 | `local[*]` (Single Node) | 4.53 | 4.81 | 1,137.68 | **1,142.49** | 8,753 | 16 | **True (100% Match)** | 8 | 148.4 |
| **50,000** | NumPy Vectorized | Single CPU | 18.32 | 13.66 | 7.32 | **20.98** | 2,382,666 | 16 | Baseline | 1 | 161.7 |
| **50,000** | Apache Spark 4.2.0 | `local[*]` (Single Node) | 18.32 | 19.54 | 2,149.24 | **2,168.78** | 23,054 | 16 | **True (100% Match)** | 8 | 164.7 |
| **100,000** | NumPy Vectorized | Single CPU | 31.29 | 37.30 | 16.71 | **54.01** | 1,851,368 | 16 | Baseline | 1 | 184.5 |
| **100,000** | Apache Spark 4.2.0 | `local[*]` (Single Node) | 31.29 | 32.22 | 3,342.83 | **3,375.05** | 29,629 | 16 | **True (100% Match)** | 8 | 199.7 |

*\*Note: 1,000-stop Spark latency includes initial JVM session instantiation and classloader overhead.*

---

## 3. Analysis of the "100,000 to 16 Customers" Reduction

### What Do the 16 Boundary Customers Represent?
1. The Spark preprocessor computes spatial polar angles from the depot and project Euclidean distance differences $|\|c_i - \bar{c}_A\| - \|c_i - \bar{c}_B\||$ between vehicle cluster centroids.
2. Stops where the distance difference is below threshold ($\delta = 0.035^\circ \approx 3.8\text{ km}$) are identified as ambiguous boundary customers that could feasibly be served by either Vehicle A or Vehicle B.
3. The top 16 boundary stops form the boundary subproblem.
4. **Original Fleet Objective Preservation:** Customers deep inside Vehicle A's sector remain assigned to Vehicle A; customers deep inside Vehicle B remain assigned to B. Only the boundary interface is optimized. Because non-boundary customer assignments are fixed, optimizing the boundary subproblem guarantees monotonic improvement of the entire fleet.
5. **100% Semantic Equivalence:** In every scale evaluated, Spark and in-memory NumPy extracted the exact same set of 16 boundary stops (`boundary_match_pandas = True`).
