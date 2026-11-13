# ROUTE/IQ — PHASE P: APACHE SPARK SCALING & BIG DATA ABLATION REPORT
**Empirical Comparison of Apache Spark 4.2.0 Distributed Preprocessing vs. Single-Machine Pandas Baseline**

- **Execution Timestamp:** `2026-11-06T17:44:40+05:30`
- **Spark Version:** Apache Spark 4.2.0 (PySpark on Java OpenJDK 64-bit)
- **Deployment Mode:** `master="local[*]"` (Single-Machine Multi-Threaded Local Mode)
- **Dataset Scales:** $N \in \{10, 25, 50, 100, 250, 500\}$ Customer Orders
- **Raw Measurements File:** `phase_p_autonomous_research/results/phase_p_spark_scaling_raw.csv`

---

## 1. Measured Empirical Scaling Data

| Scale ($N$) | Single-Machine Pandas Time (ms) | Apache Spark 4.2.0 Time (ms) | Spark Speedup Ratio ($T_{\text{pandas}} / T_{\text{spark}}$) | Vehicle Clusters Formed | Mathematical Partition Consistency |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **10** | 5.52 | 9,050.35 | $0.0006\times$ | 2 | **100% Identical** |
| **25** | 4.00 | 1,102.98 | $0.0036\times$ | 3 | **100% Identical** |
| **50** | 5.42 | 576.96 | $0.0094\times$ | 7 | **100% Identical** |
| **100** | 8.71 | 574.54 | $0.0152\times$ | 12 | **100% Identical** |
| **250** | 15.36 | 583.14 | $0.0263\times$ | 29 | **100% Identical** |
| **500** | 30.02 | 584.95 | $0.0513\times$ | 58 | **100% Identical** |

---

## 2. Scientific Analysis & Boundary Characterization

### Finding 1: The JVM & Spark Execution Engine Overhead
- On small batches ($N \le 100$), PySpark exhibits a fixed startup and session synchronization overhead of approximately $570\text{ to }580\text{ ms}$ (and up to $9,000\text{ ms}$ for cold-start initial JVM spawn).
- In contrast, Single-Machine Pandas runs in native C/NumPy memory without IPC overhead, executing in under $10\text{ ms}$.
- **Scientific Honesty Commitment:** In single-machine environments (`local[*]`), Apache Spark **does not** provide a computational latency speedup for small delivery campaigns ($N < 500$). Claiming that Spark accelerates small routing problems on a laptop or single VM is empirically false.

### Finding 2: Mathematical Invariant Preservation
- Despite the execution engine differences, the partitioning logic is 100% mathematically consistent across all scales:
  $$\text{Clusters}_{\text{spark}}(N) \equiv \text{Clusters}_{\text{pandas}}(N), \quad \forall N \in \{10, \dots, 500\}$$
- Both implementations compute identical polar angles $\theta_i = \text{atan2}(y_i - y_0, x_i - x_0)$ and cumulative demand bins $\lfloor \sum d_j / Q \rfloor$.

### Finding 3: Role in True Big Data Production Architectures
- Apache Spark's true value in the ROUTE/IQ architecture is **horizontal memory decoupling**:
  1. Ingestion of hundreds of thousands of historical NYC DOT traffic volume records and NOAA meteorological observations.
  2. Map-side aggregation of road network impedances across millions of edges.
  3. Seamless distributed scaling across a cluster where dataset size exceeds single-node RAM ($> 16\text{ GB}$).
- For cloud container deployments with memory constraints (such as Render 512 MB free tier), the single-machine polar sweep provides a mathematically identical lightweight fallback that eliminates JVM heap exhaustion.

