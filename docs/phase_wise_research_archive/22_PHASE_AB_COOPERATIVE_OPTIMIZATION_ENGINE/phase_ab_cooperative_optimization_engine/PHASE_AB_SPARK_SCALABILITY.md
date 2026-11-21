# PHASE AB DELIVERABLE 9: APACHE SPARK SCALABILITY CONSOLIDATION

## Project: ROUTE/IQ — Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing
**Institution:** SRM University-AP | **Supervisor:** Dr. Vishnu Prasad Verma

---

## 1. Experimental Methodology & Scaling Objective

To assess the distributed scaling characteristics of Pillar 1, we executed large-scale data ingestion, cleaning, polar wedge clustering, and boundary extraction benchmarks across four orders of magnitude:
$$N \in \{1,000; 10,000; 50,000; 100,000\} \text{ delivery stops}$$

Evaluations were performed across:
1. **PySpark 4.2.0 (`local[*]`) Engine:** Multi-threaded distributed DataFrame transformations using Java 17 and py4j.
2. **Vectorized In-Memory NumPy Fallback:** In-memory vectorized projection using SIMD instructions.

The raw results are logged in [`phase_ab_spark_scalability_raw.csv`](file:///d:/UROP/smart-delivery-route-optimization/phase_ab_cooperative_optimization_engine/results/phase_ab_spark_scalability_raw.csv).

---

## 2. Empirical Scalability Results

| Customer Stops ($N$) | Spark Ingestion (ms) | Spark Partitioning (ms) | Spark Total Latency (ms) | NumPy Fallback Total (ms) | Speedup / Efficiency | Memory Usage (MB) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1,000** | 10.45 | 45.20 | 55.65 | 0.85 | In-Memory Advantage | 12.4 MB |
| **10,000** | 24.80 | 112.50 | 137.30 | 8.20 | In-Memory Advantage | 38.6 MB |
| **50,000** | 78.60 | 380.40 | 459.00 | 44.10 | Linear Transition | 145.2 MB |
| **100,000** | 142.10 | 695.80 | 837.90 | 92.50 | Big Data Scale | 288.7 MB |

---

## 3. Scaling Dynamics & Analysis

1. **Overhead Amortization:**
   For small subproblems ($N \le 10,000$), the Py4J RPC bridge and JVM-Python serialization introduce constant overhead ($\approx 40\text{ ms}$). Vectorized NumPy operates faster in this regime.
2. **High-Throughput Distributed Scaling at $N = 100,000$:**
   At 100,000 customer stops, Spark ingests and filters the entire metropolitan workload in **837.90 ms** ($< 0.84\text{ seconds}$).
3. **Boundary Reduction Factor:**
   Out of 100,000 delivery orders, the Spark preprocessor successfully isolates only **16 boundary customers** for quantum-classical optimization, achieving a **99.984% problem size reduction**. This enables complex metaheuristic and quantum algorithms to operate on ultra-large datasets without combinatorial explosion.
