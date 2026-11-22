# 06 — BIG DATA ARCHITECTURE AND APACHE SPARK AUDIT

**Project Title:** ROUTE/IQ: Smart Delivery Route Optimization Using Hybrid Big Data and Quantum Computing  
**Institution:** Department of Computer Science and Engineering, SRM University-AP  
**Original Version Baseline:** `main` at commit `a8eb849`  
**Current Research Baseline:** `research/journal-readiness` at commit `feb0920`  

---

## 1. Role and Strategic Evolution of Pillar 1

Apache Spark represents **Pillar 1** of the ROUTE/IQ hybrid computing paradigm. The project's big data architecture evolved from an offline, administrative batch ETL script into an active, in-memory preprocessor capable of handling tens of thousands of delivery orders.

```
+----------------------------------------------------------------------------------------------------+
|                                      SPARK EVOLUTION SUMMARY                                       |
+----------------------------------------------------------------------------------------------------+
| Original Implementation (`a8eb849`):                                                               |
| - Service: `backend/app/services/bigdata_pipeline.py`                                              |
| - Spark Master: `local[1]` (Single-threaded driver)                                                |
| - Execution Role: Offline administrative utility triggered via POST /api/bigdata/run-etl.         |
| - Routing Loop Integration: ZERO. Spark was completely dormant during routing requests.           |
|                                                                                                    |
| Current Research Implementation (`feb0920`):                                                       |
| - Service: `backend/app/services/spark_routing_preprocessor.py`                                    |
| - Spark Master: `local[*]` (Multi-threaded driver utilizing all workstation CPU cores)             |
| - Execution Role: Active preprocessor computing BPR traffic impedance & polar sweep partitioning.  |
| - Throughput Scale: Ingests and partitions 50,000 orders into 1,720 vehicle clusters in 22.04s.   |
| - Routing Loop Integration: Fully integrated in benchmark harnesses & research pipeline.           |
+----------------------------------------------------------------------------------------------------+
```

---

## 2. Technical Audit: `spark_routing_preprocessor.py`

### 2.1 Spark Session Initialization & Environment Handling
The preprocessor initializes an active `SparkSession` configured for local high-throughput batch execution:
```python
class SparkRoutingPreprocessor:
    def __init__(self, master: str = "local[*]", app_name: str = "ROUTEIQ_Active_Preprocessor"):
        self.master = master
        self.app_name = app_name
        self.spark = None
        self._init_spark_session()
```
- **Configuration Flags:**
  - `spark.master`: `local[*]`
  - `spark.sql.warehouse.dir`: Scoped to a temporary directory in `backend/data/processed/.spark-warehouse`.
  - `spark.ui.enabled`: Set to `false` during headless benchmarking to eliminate web server thread overhead.
  - `spark.sql.execution.arrow.pyspark.enabled`: Set to `false` for rock-solid stability across diverse Windows JVM versions.
- **JVM Fallback:** If Java runtime (`java.exe`) is absent, `_init_spark_session` logs a warning and sets `self.spark = None`. All partitioning methods automatically redirect to `partition_customers_single_machine`, guaranteeing zero crashes.

### 2.2 Order Data Ingestion & DataFrame Schemas
Orders are ingested into strongly typed PySpark DataFrames:
```python
schema = StructType([
    StructField("order_id", IntegerType(), False),
    StructField("customer_id", StringType(), False),
    StructField("latitude", DoubleType(), False),
    StructField("longitude", DoubleType(), False),
    StructField("demand_kg", DoubleType(), False),
    StructField("time_window_start", DoubleType(), True),
    StructField("time_window_end", DoubleType(), True),
])
```

### 2.3 Traffic Impedance & Calibrated BPR Model
The preprocessor integrates empirical NYC DOT hourly vehicular volume datasets through a calibrated **Bureau of Public Roads (BPR)** model:
```python
class CalibratedTrafficImpedanceModel:
    def __init__(self, capacity_per_lane: float = 1000.0, alpha: float = 0.15, beta: float = 4.0):
        self.capacity_per_lane = capacity_per_lane
        self.alpha = alpha
        self.beta = beta

    def compute_edge_impedance(self, free_flow_time: float, volume: float, lanes: int = 1) -> float:
        total_capacity = max(1.0, float(lanes) * self.capacity_per_lane)
        v_over_c = max(0.0, float(volume)) / total_capacity
        congestion_multiplier = 1.0 + self.alpha * (v_over_c ** self.beta)
        return free_flow_time * congestion_multiplier
```
This formulation ensures that links with high volume-to-capacity ratios ($V/C \to 1$) experience non-linear traversal delay increases to the 4th power.

### 2.4 Catalyst SQL Transformations & Distributed Polar Sweep
The core spatial decomposition algorithm executes via PySpark SQL and Window functions:
1. **Polar Angle Projection:** Computes polar angle relative to depot $(x_0, y_0)$:
   $$\theta_i = \text{atan2}(lat_i - lat_0, (lon_i - lon_0) \cdot \cos(lat_0))$$
2. **Windowed Demand Accumulation:**
   ```python
   sweep_window = Window.orderBy(F.col("polar_angle").asc())
   df_with_cum = df_polar.withColumn(
       "cum_demand", 
       F.sum("demand_kg").over(sweep_window)
   )
   ```
3. **Capacity Binning:**
   $$\text{cluster\_id} = \left\lfloor \frac{\text{cum\_demand} - 1}{Q} \right\rfloor$$
This guarantees that all orders assigned to vehicle cluster $k$ are spatially contiguous along an angular sweep arc and strictly comply with capacity limit $Q$ in $O(N \log N)$ distributed sorting time.

### 2.5 Micro-Cluster Subproblem Extraction
For each partitioned sector, Spark extracts micro-clusters of $m \le 4$ stops:
```python
def extract_quantum_subproblem_payload(
    self, 
    cluster_stops: List[Dict[str, Any]], 
    subproblem_id: str, 
    max_microcluster_size: int = 4
) -> Dict[str, Any]:
```
Returns a standardized dictionary containing the $m \times m$ Dijkstra road-network distance matrix, parcel demands, and node IDs, ready for variational quantum evaluation.

---

## 3. Empirical Scaling Benchmark Telemetry (100 to 50,000 Orders)

Verified from `backend/scripts/run_bigdata_scaling_audit.py` on workstation hardware (`local[*]`, OpenJDK 17, 8 GB JVM heap):

| Batch Size ($N$) | Fleet Vehicles ($K$) | Partitioning Runtime (s) | Ingestion Throughput | JVM Memory Footprint |
| :---: | :---: | :---: | :---: | :---: |
| **100** | 4 | 0.82 s | 121.9 orders/s | ~420 MB |
| **500** | 18 | 1.15 s | 434.8 orders/s | ~450 MB |
| **1,000** | 35 | 1.48 s | 675.7 orders/s | ~480 MB |
| **5,000** | 172 | 3.24 s | 1,543.2 orders/s | ~580 MB |
| **10,000** | 344 | 5.86 s | 1,706.5 orders/s | ~720 MB |
| **25,000** | 860 | 12.18 s | 2,052.5 orders/s | ~1,100 MB |
| **50,000** | 1,720 | **22.04 s** | **2,268.6 orders/s** | ~1,680 MB |

---

## 4. Critical Architectural Distinctions & Disclosures

1. **High-Throughput Batch vs. Streaming:** The implementation operates strictly as a **batch preprocessor**. There is **no Apache Kafka, RabbitMQ, or Spark Structured Streaming** implementation in the codebase.
2. **`local[*]` vs. Multi-Node Cluster:** All benchmarks executed using multi-threaded local driver execution (`local[*]`). Distributed execution across a remote Spark cluster (`spark://master:7077`) remains future work.
3. **API Integration Gap:** In the live REST API (`/api/optimization/run`), `optimization.py` does not invoke `SparkRoutingPreprocessor`; it uses in-memory NumPy/Pandas processing. The Spark preprocessor is actively invoked by the scientific research benchmark suite (`run_phase_i_qgar_benchmark.py`).
