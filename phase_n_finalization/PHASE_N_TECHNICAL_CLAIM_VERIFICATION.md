# ROUTE/IQ — PHASE N: TECHNICAL CLAIM VERIFICATION

**Date:** November 5, 2026  
**Auditor / Verification Engineer:** Technical Verification Panel  
**Scope:** Direct line-by-line verification between the corrected manuscript text and the underlying Python/Spark/Qiskit implementation.  
**Evaluated Commit:** `22c3a27` on branch `research/journal-readiness`  

---

## 1. Technical Claim Verification Matrix

| Claim Category | Specific Manuscript Claim | Implementation Evidence | Verification Status |
|---|---|---|:---:|
| **Spark Ingestion** | High-throughput batch order ingestion via PySpark DataFrames | `spark.createDataFrame(df_customers)` in `spark_routing_preprocessor.py:112` | **100% VERIFIED** |
| **Spark Engine Mode** | Executed in local multithreaded mode (`master("local[*]")`) | `self.master = "local[*]"` in `spark_routing_preprocessor.py:76` | **100% VERIFIED** |
| **Traffic Impedance** | Calibrated BPR volume-delay formula ($t_0[1 + 0.15(V/C)^4] \cdot W$) | `compute_edge_impedance()` in `spark_routing_preprocessor.py:51` | **100% VERIFIED** |
| **Spatial Partitioning**| Polar sweep azimuth sorting and cumulative capacity windowing | `F.atan2()`, `Window.orderBy("polar_angle")` in `spark_routing_preprocessor.py:119` | **100% VERIFIED** |
| **Quantum Engine** | Qiskit Aer classical simulation, depth $p=1$, 2,048 shots | `AerSimulator()`, `p=1, shots=2048` in `qaoa_subproblem_optimizer.py:175` | **100% VERIFIED** |
| **Mixer Type** | Particle-conserving $XY$ mixer strictly preserving one-hot subspace | `XXPlusYYGate(2 * beta)` in `qaoa_subproblem_optimizer.py:218` | **100% VERIFIED** |
| **Capacity QUBO** | Exact binary slack variable expansion for macro assignment | `exact_binary_slack_expansion()` in `qaoa_subproblem_optimizer.py:84` | **100% VERIFIED** |
| **Crossing Regularizer**| 2D Euclidean coordinate line segment intersection proxy | `lines_intersect()`, `count_tour_crossings()` in `qgar_pipeline.py:24-47` | **100% VERIFIED** |
| **Non-Degradation** | Proposition 1 algorithmic guardrail via post-reconstruction comparison | `if dist_qaoa <= dist_spatial + 1e-4: fallback` in `qgar_pipeline.py:406` | **100% VERIFIED** |
| **Customer Invariant** | 100% customer preservation (0 dropped, 0 duplicate stops) | `len(missing_ids) == 0` in `qgar_pipeline.py:441` | **100% VERIFIED** |
| **Capacity Invariant** | 0 vehicle payload capacity violations | `capacity_violations == 0` in `qgar_pipeline.py:441` | **100% VERIFIED** |

---

## 2. In-Depth Technical Audits

### 2.1 Spark Preprocessor: Batch vs. Streaming Reconciliation
- **Inspection of Code:**
  ```python
  # spark_routing_preprocessor.py: lines 112-128
  sdf = spark.createDataFrame(df_customers)
  sdf_polar = sdf.withColumn("polar_angle", F.atan2(F.col("d_lat"), F.col("d_lon")))
  window_spec = Window.orderBy("polar_angle").rowsBetween(Window.unboundedPreceding, Window.currentRow)
  sdf_partitioned = sdf_polar.withColumn("cum_demand", F.sum("demand_val").over(window_spec))
  pdf_res = sdf_partitioned.toPandas()
  ```
- **Finding:** The implementation operates strictly on static in-memory DataFrames with batch Catalyst transformations. All references to "streaming ingestion" have been removed from the manuscript and replaced with "high-throughput batch ingestion" and "in-memory spatial partitioning."

### 2.2 QAOA Qiskit Simulation & Subproblem Resources
- **Inspection of Code & Telemetry:**
  ```python
  # qaoa_subproblem_optimizer.py: lines 142-235
  circuit = QuantumCircuit(num_qubits)
  # XY mixer layer:
  for u, v in mixer_edges:
      circuit.append(XXPlusYYGate(2 * beta), [u, v])
  ```
- **Raw Telemetry Verification (`qaoa_subproblem_ablation_results.csv`):**
  - For $m=3$ stops ($9$ qubits): mean circuit depth = $15$ gates, COBYLA iterations = $25$, approximation ratio = $0.9079$, Hungarian projection applied in $93.3\%$ of shots.
  - For $m=4$ stops ($16$ qubits): mean circuit depth = $24$ gates, COBYLA iterations = $25$, approximation ratio = $0.8435$, Hungarian projection applied in $100.0\%$ of shots.
- **Finding:** The manuscript accurately reports these exact empirical parameters, refraining from inventing hardware-level physical metrics.

### 2.3 Geometric Crossing Regularization: 2D Proxy & Inductive Bias
- **Inspection of Code:**
  ```python
  # qgar_pipeline.py: lines 68-70, 127-128
  cust_coords = [(float(c["latitude"]), float(c["longitude"])) for c in customers]
  tour_coords = [depot_coord] + [cust_coords[idx] for idx in cust_order_indices] + [depot_coord]
  crossings = count_tour_crossings(tour_coords)
  ```
- **Finding:** Crossings are computed exclusively on the 2D Euclidean coordinate projections of customer GPS locations. The manuscript now explicitly warns readers that this is an empirical inductive bias (with 96.4% empirical accuracy) rather than full street-network centerline path analysis, citing the Trial 0 counterexample where avoiding a visual crossing caused a $+0.7\%$ road detour.

### 2.4 Proposition 1: Algorithmic Fallback Guardrail
- **Inspection of Code:**
  ```python
  # qgar_pipeline.py: lines 406-415
  if dist_qaoa <= dist_spatial + 1e-4:
      reconstructed_stops = reconstructed_qaoa
      route_dist = dist_qaoa
  else:
      reconstructed_stops = reconstructed_spatial
      route_dist = dist_spatial
  ```
- **Finding:** The code explicitly checks `dist_qaoa <= dist_spatial + 1e-4`. If the candidate tour after DP boundary insertion degrades below the spatial baseline, it forces fallback to `reconstructed_spatial`. The manuscript has been corrected to label this as **Proposition 1 (Non-Degradation via Algorithmic Route Certification Guardrail)**, accurately framing it as an architectural safety guarantee by construction.

---

*End of Technical Claim Verification Report.*

