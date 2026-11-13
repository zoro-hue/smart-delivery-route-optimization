# PHASE Z SPARK CLUSTER VALIDATION
## Distributed Infrastructure Audit, Scalability Profiling, and Real vs. Simulated Performance
**ROUTE/IQ — Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing**  
**Department of Computer Science and Engineering, SRM University-AP**  
**Supervisor:** Dr. Vishnu Prasad Verma  

---

## 1. RESEARCH MANDATE

Phase Y claimed that Apache Spark multi-worker scaling achieved a **$2.96\times$ speedup** and reached processing throughputs of **over 540,000 records/second** at $N=100{,}000$ stops. It also provided a Docker standalone cluster configuration (`docker-compose.yml`, `Dockerfile`, `spark-defaults.conf`).

Phase Z was tasked with independently verifying whether these metrics originated from physical multi-node execution, auditing the cluster manifests, and benchmarking genuine PySpark 4.2.0 performance on identical stop volumes.

---

## 2. AUDIT OF CLUSTER DEPLOYMENT & HOST CAPABILITY

1. **Docker Availability Check:**  
   Execution of `docker --version` on the host machine failed with:
   ```
   docker : The term 'docker' is not recognized as the name of a cmdlet, function, script file...
   ```
   The host machine does not have the Docker daemon installed. Consequently, spinning up the multi-container standalone cluster was physically impossible on this environment.
2. **Phase Y Benchmark Audit:**  
   Examination of `phase_y_breakthrough_engineering/benchmarks/benchmark_spark_scalability.py` (lines 73–98) revealed that Phase Y did not run PySpark:
   ```python
   # Simulated worker scaling using NumPy chunking and empirical formula
   jvm_base = 35.0 if N <= 10000 else (90.0 if N <= 50000 else 180.0)
   worker_scaling = 1.0 / (w ** 0.6)
   t_etl_s = ((time.perf_counter() - t0) * 1000.0) * worker_scaling + jvm_base
   ```
   The reported 2.96x speedup and 540,000 records/sec throughput were derived entirely from a mathematical simulation of worker scaling, not actual distributed Spark task execution.

---

## 3. GENUINE PYSPARK 4.2.0 SCALABILITY BENCHMARK

To replace the simulation with empirical ground truth, Phase Z executed real Apache Spark 4.2.0 benchmarks running on OpenJDK 17 (`backend/tools/jdk-17.0.20.1+1-jre`) with local worker configurations (`local[1]`, `local[2]`, `local[4]`) against a vectorized Pandas baseline on datasets ranging from $N=1{,}000$ to $N=100{,}000$ delivery stops:

### Measured Empirical Latency & Throughput

| Dataset Size ($N$) | Engine Mode | DataFrame Creation (ms) | Spark SQL Transform (ms) | Action Collect (ms) | Total Latency (ms) | Throughput (stops/sec) |
|---|---|---|---|---|---|---|
| **1,000** | **Pandas In-Memory** | 0.00 | 2.87 | 0.00 | **2.87** | **348,675** |
| 1,000 | PySpark `local[1]` | 1,363.06 | 1,191.37 | 886.05 | 3,440.48 | 291 |
| 1,000 | PySpark `local[2]` | 31.24 | 272.26 | 146.08 | 449.58 | 2,224 |
| 1,000 | PySpark `local[4]` | 25.39 | 165.26 | 78.22 | 268.87 | 3,719 |
| **10,000** | **Pandas In-Memory** | 0.00 | 2.66 | 0.00 | **2.66** | **3,759,398** |
| 10,000 | PySpark `local[1]` | 41.87 | 182.07 | 190.03 | 413.97 | 24,156 |
| 10,000 | PySpark `local[2]` | 41.68 | 243.03 | 154.92 | 439.63 | 22,746 |
| 10,000 | PySpark `local[4]` | 37.83 | 255.98 | 171.72 | 465.53 | 21,481 |
| **50,000** | **Pandas In-Memory** | 0.00 | 5.31 | 0.00 | **5.31** | **9,416,551** |
| 50,000 | PySpark `local[1]` | 93.57 | 216.48 | 471.74 | 781.79 | 63,955 |
| 50,000 | PySpark `local[2]` | 107.58 | 168.22 | 460.52 | 736.32 | 67,906 |
| 50,000 | PySpark `local[4]` | 96.19 | 177.03 | 391.73 | 664.95 | 75,194 |
| **100,000** | **Pandas In-Memory** | 0.00 | 10.76 | 0.00 | **10.76** | **9,297,742** |
| 100,000 | PySpark `local[1]` | 176.25 | 207.15 | 887.50 | 1,270.90 | 78,685 |
| 100,000 | PySpark `local[2]` | 161.74 | 228.10 | 807.89 | 1,197.73 | 83,491 |
| 100,000 | PySpark `local[4]` | 170.60 | 188.75 | 784.93 | **1,144.28** | **87,392** |

---

## 4. SCIENTIFIC ANALYSIS OF BIG DATA PERFORMANCE

1. **The In-Memory Crossover Reality:**  
   On single-node workstations where dataset volume fits comfortably within physical RAM ($N \le 100{,}000$ delivery stops $\approx 8\text{ MB}$ data footprint), vectorized NumPy/Pandas processing outperforms Spark by two orders of magnitude (10.76 ms vs. 1,144.28 ms) due to the complete absence of JVM serialization, socket communication, and task coordination overhead.
2. **True PySpark Throughput:**  
   At $N=100{,}000$ stops, genuine PySpark 4.2.0 achieves **87,392 stops/second** on 4 local cores, not 540,000 stops/sec as simulated. Multi-threading yields modest improvements in transformation latency (improving from 207.15 ms on 1 core to 188.75 ms on 4 cores), but the action `.collect()` and SerDe bridge to Python dominate overall runtime.
3. **The True Architectural Role of Apache Spark:**  
   Apache Spark is not intended to outperform NumPy on 8 MB datasets. Its genuine architectural value in ROUTE/IQ (Pillar 1) lies in:
   - Ingesting multi-gigabyte historical NYC DOT traffic logs (40,516 road segments) and NOAA precipitation feeds.
   - Performing distributed spatial joins across massive geographic areas that exceed host RAM.
   - Partitioning fleet workloads into localized, capacity-bounded micro-clusters before dispatching bounded subproblems to quantum and classical solvers.

