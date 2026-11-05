# ROUTE/IQ — PHASE M: TECHNICAL CLAIM AUDIT

**Audit Date:** November 5, 2026  
**Auditor:** Independent Technical & Academic Quality Auditor  
**Scope:** Verification of technical claims in `ROUTE_IQ_FULL_JOURNAL_MANUSCRIPT.md` and `ROUTE_IQ_FULL_JOURNAL_MANUSCRIPT.tex` against the actual Python/Spark/Qiskit implementation and raw benchmark logs.  
**Evaluated Commit:** `a60779d` on branch `research/journal-readiness`  

---

## 1. Executive Verdict & Summary

The technical audit examined the ROUTE/IQ codebase line by line to evaluate whether every technical claim made in the manuscript is supported by reproducible source code and execution logs. 

**Overall Technical Audit Verdict:** **SOUND CORE ARCHITECTURE WITH CRITICAL PRESENTATION CORRECTIONS REQUIRED.**
The core hybrid pipeline functions correctly and faithfully: Apache Spark actively prepares subproblems, Qiskit Aer genuinely executes parameterized QAOA circuits with $XY$ mixers, and the route certification guardrail strictly prevents performance degradation. However, several claims in the manuscript overstate operational capabilities or conflate terminology in ways that peer reviewers will challenge:
1. **Streaming vs. Batch:** The paper repeatedly claims Spark performs "streaming ingestion" and processes "streaming order streams." The implementation is strictly **in-memory batch DataFrame processing**.
2. **Cluster vs. Local Execution:** Spark runs in `local[*]` mode on a single workstation JVM. While disclosed in Section 6, the abstract and introduction use phrasing ("enterprise Big Data infrastructure," "distributed Big Data computing") that implies multi-node cluster deployment.
3. **Geometric Crossing Regularizer:** Crossings are calculated using **2D Euclidean straight-line customer coordinates (latitude, longitude)**, NOT directed OpenStreetMap road network geometries.
4. **Nature of the Non-Degradation Guarantee:** The non-degradation guarantee is an **architectural guarantee by construction (via an explicit acceptance-rejection fallback filter)**, not an intrinsic convergence property of QAOA.

---

## 2. Pillar 1: Apache Spark Implementation Audit

### 2.1 Streaming Ingestion vs. In-Memory Batch Processing
- **Manuscript Claim:**
  > "In Pillar 1, Spark actively ingests high-volume order streams..." (Abstract, p. 1)  
  > "Apache Spark ingests streaming order data..." (Section 1.2, p. 2)  
  > "Pillar 1: Big Data Computing (Apache Spark 4.2.0 Engine): Streaming Orders (N up to 50,000)..." (Figure 1, p. 3)
- **Source Code Evidence:**
  Inspecting `backend/app/services/spark_routing_preprocessor.py` (lines 81–144) and `backend/app/services/optimization/qgar_pipeline.py` (lines 285–305):
  ```python
  df_cust = pd.DataFrame([...])
  clusters, t_spark_ms = self.preprocessor.partition_customers_spark(
      df_cust, depot_lat, depot_lon, vehicle_capacity
  )
  ```
  Inside `partition_customers_spark`:
  ```python
  sdf = spark.createDataFrame(df_customers)
  # SQL transformations: atan2, Window.orderBy, sum, toPandas()
  pdf_res = sdf_partitioned.toPandas()
  ```
- **Audit Finding:**
  The implementation does **NOT** use Spark Structured Streaming (`spark.readStream`, Kafka, socket feeds, or sliding event-time windows). It creates a static in-memory DataFrame from a Pandas DataFrame, executes Catalyst batch transformations, and immediately materializes the result via `.toPandas()`.
- **Reviewer Impact:**
  Reviewer 2 (Big Data & Transportation) will issue a major revision or rejection flag for claiming "streaming ingestion" when the system executes batch micro-partitioning.
- **Mandatory Correction:**
  Replace all occurrences of "streaming order streams" and "streaming ingestion" with **"high-throughput batch order ingestion"** or **"distributed in-memory batch spatial preprocessing."**

### 2.2 Active Pipeline Participation vs. Post-Hoc Analysis
- **Audit Verification:**
  Does Spark actively prepare data consumed by the QAOA pipeline at runtime, or is it merely an offline ETL script?
- **Source Code Evidence:**
  In `qgar_pipeline.py`, line 298:
  ```python
  clusters, t_spark_ms = self.preprocessor.partition_customers_spark(...)
  ```
  The clusters returned by Spark (`clusters`) are directly iterated over in line 323 (`for k, cluster in enumerate(clusters):`), and for each cluster, `extract_quantum_subproblem_payload` generates the exact customer IDs, core stops, and distance submatrices fed into `solve_microcluster_tour()`.
- **Audit Finding:**
  **CLAIM VERIFIED.** Spark actively participates in the end-to-end execution path. Without Spark's polar angle partitioning and capacity-window assignment, the quantum optimizer receives no input subproblems.

### 2.3 Single-Machine Multiprocessing (`local[*]`) vs. Distributed Cluster
- **Manuscript Claim:**
  > "Apache Spark 4.2.0 configured with local[*] running on OpenJDK 17.0.20.1+1 and Apache Hadoop 3.3.6 winutils." (Section 6, p. 5)
- **Audit Finding:**
  While Section 6 explicitly states `local[*]`, the Abstract and Introduction use terms like "distributed Big Data computing" and "distributed road-network processing." On Windows with `local[*]`, Spark executes using multithreaded JVM workers on a single CPU socket. There is no network serialization across physical compute nodes, and network shuffle I/O is zero.
- **Reviewer Impact:**
  Reviewer 2 will demand that the limitations section prominently state that shuffle latency and network serialization across a physical multi-node cluster (e.g. AWS EMR or Databricks) were not measured.
- **Mandatory Correction:**
  Add a clear clarification in Section 6 and Section 10 stating: *"All Spark experiments were executed in local multithreaded mode (`local[*]`) on a single 8-core host. Distributed network partitioning over multi-node clusters is identified as future work."*

---

## 3. Pillar 2: Quantum Computing & QAOA Implementation Audit

### 3.1 Genuine Circuit Execution on Qiskit Aer
- **Audit Verification:**
  Does QAOA execute genuine quantum circuits through Qiskit Aer, or does it fall back to classical heuristics?
- **Source Code Evidence:**
  Inspecting `backend/app/services/optimization/qaoa_subproblem_optimizer.py` (lines 142–245):
  ```python
  circuit = QuantumCircuit(num_qubits)
  # Initial superposition in one-hot subspace
  # Problem Hamiltonian cost layer:
  #   RZZ gates for quadratic cost terms
  # Mixer Hamiltonian layer:
  #   XXPlusYYGate(2 * beta) for particle conservation
  # Measurement: circuit.measure_all()
  # Backend execution:
  sim = AerSimulator()
  result = sim.run(compiled_circuit, shots=self.shots).result()
  counts = result.get_counts()
  ```
- **Audit Finding:**
  **CLAIM VERIFIED.** The implementation constructs bona fide parameterized quantum circuits with state initialization, $R_{ZZ}$ problem Hamiltonian unitary evolution, $XY$ particle-conserving mixer evolution via `XXPlusYYGate`, and shot-based projective measurement on `AerSimulator`. No classical mock or hardcoded bypass was found.

### 3.2 Logical Qubits, Circuit Depth, and Mixer Architecture
- **Manuscript Claims:**
  - Logical Qubits: $m^2 \le 16$ qubits for $m \le 4$ stops.
  - Circuit Depth: $p = 1$ variational layer.
  - Mixer: Particle-conserving $XY$ mixer ($XX + YY$).
  - Shots: 2,048 measurement shots.
- **Audit Finding:**
  **CLAIM VERIFIED.**
  - For $m=3$, circuit uses $3^2 = 9$ qubits.
  - For $m=4$, circuit uses $4^2 = 16$ qubits.
  - Circuit depth is $p=1$ (1 cost layer + 1 mixer layer).
  - Mixer term uses Qiskit's `XXPlusYYGate`, which strictly preserves Hamming weight.
  - COBYLA optimizer executes for at most 30 classical iterations.

### 3.3 QAOA Influence on Final Routing Decisions
- **Audit Verification:**
  Does the QAOA solution genuinely change the route, or does Kuhn-Munkres projection silently restore the classical order?
- **Source Code Evidence:**
  In `qgar_pipeline.py`, line 78–142, the candidate evaluator takes the measurement bitstring counts from Qiskit Aer. It decodes all unique bitstrings. If a bitstring is already a valid permutation matrix, it is accepted directly without Kuhn-Munkres projection. If not, Kuhn-Munkres projects it onto the closest permutation.
  The candidate permutations are evaluated for directed road cost. Across the 20 benchmark instances, QAOA proposed a non-trivial route alteration that was adopted in 32.3% of microclusters (45 out of 139 clusters).
- **Audit Finding:**
  **CLAIM VERIFIED.** QAOA actively drives route decisions in approximately one-third of clusters.

### 3.4 Rigor of Non-Supremacy and Attribution Disclosures
- **Audit Verification:**
  Does the manuscript honestly disclose the absence of quantum computational advantage?
- **Manuscript Text:**
  > "Crucially, attribution ablations confirm that at current NISQ qubit budgets ($m \le 4$, 16 logical qubits), QAOA co-produces candidate permutations whose quality is matched by classical enumeration, and mature global classical heuristics (OR-Tools Guided Local Search) remain 21% shorter. ROUTE/IQ does not claim quantum supremacy..." (Abstract, p. 1)
- **Audit Finding:**
  **EXCELLENT SCIENTIFIC INTEGRITY.** The authors explicitly refrain from claiming quantum advantage, disclose that classical enumeration over $4! = 24$ states is trivial, and acknowledge the 21% gap to OR-Tools. Reviewer 1 (Quantum) will find this disclosure exemplary.

---

## 4. QGAR & Geometric Regularization Audit

### 4.1 Planar Crossing Regularizer vs. Real Road Network Geometry
- **Manuscript Text:**
  > "The number of straight-line 2D planar crossings is computed via line segment intersection: Cross(P) = sum ... Segment(v_i, v_{i+1}) cap Segment(v_j, v_{j+1})" (Section 5.4, p. 4)
- **Source Code Evidence:**
  In `qgar_pipeline.py`, line 24–47:
  ```python
  def lines_intersect(p1, p2, p3, p4): ...
  def count_tour_crossings(tour_coords): ...
  ```
  Here `tour_coords` are the `(latitude, longitude)` geographic coordinates of the customers and depot.
- **Audit Finding:**
  The crossing check tests whether straight Euclidean segments between customer GPS points intersect in $\mathbb{R}^2$. It does **NOT** trace the physical centerline paths through Manhattan's 142,123 directed road segments.
- **Reviewer Impact:**
  Reviewer 2 will immediately point out:
  1. Real road routes follow grid street centerlines, not Euclidean straight lines.
  2. Two street paths can cross at an intersection without causing an inefficient Euclidean cross, or can share a one-way avenue without visually crossing.
  3. Trial 0 in the project's own audit showed that preventing a 2D Euclidean crossing caused a $+0.7\%$ detour because the vehicle had to circumnavigate a one-way street block.
- **Verdict & Mandatory Clarification:**
  The manuscript correctly labels this as an "empirical inductive bias ($96.4\%$ accuracy)" in Section 8, but Section 5.4 must explicitly state: *"Planar crossings are evaluated on the 2D Euclidean projection of customer geographic coordinates, serving as a geometric proxy rather than full road-network topology analysis."*

### 4.2 Customer Preservation & Fleet Capacity Compliance
- **Audit Verification:**
  Does the QGAR pipeline preserve 100% of customers without duplicate visits or capacity violations?
- **Source Code Evidence:**
  In `qgar_pipeline.py`, lines 437–442:
  ```python
  input_ids = set(c["id"] for c in customers)
  missing_ids = input_ids - all_routed_customer_ids
  capacity_violations = sum(1 for r in routes if r["total_load"] > vehicle_capacity + 1e-5)
  is_feasible = (len(missing_ids) == 0 and capacity_violations == 0)
  ```
  In all 20 paired instances across all 5 seeds ($N=10$ to $100$), `missing_ids` is strictly 0 and `capacity_violations` is strictly 0.
- **Audit Finding:**
  **CLAIM VERIFIED.** Feasibility is maintained across all test instances.

---

## 5. Non-Degradation Guarantee Audit

### 5.1 Verification of Theorem 1 ($C(R_{\text{QGAR}}) \le C(R_{\text{spatial}}) + \epsilon$)
- **Manuscript Formulation:**
  Theorem 1 states:
  $$C(R_{\text{QGAR}}) \le C(R_{\text{spatial}}) + \epsilon \quad (\epsilon = 10^{-4}\text{ km})$$
- **Source Code Evidence:**
  In `qgar_pipeline.py`, lines 396–415:
  ```python
  if enable_adaptive_influence and influence_res.get("adopted_source") == "QAOA" and boundary_custs:
      reconstructed_spatial = self._reconstruct_route_dp_insertion(...)
      dist_spatial = self._calculate_route_distance(...)
      if dist_qaoa <= dist_spatial + 1e-4:
          reconstructed_stops = reconstructed_qaoa
          route_dist = dist_qaoa
      else:
          reconstructed_stops = reconstructed_spatial
          route_dist = dist_spatial
  ```
- **Audit Finding:**
  - If `dist_qaoa <= dist_spatial + 1e-4`, the QAOA route is accepted.
  - If `dist_qaoa > dist_spatial + 1e-4`, the algorithm explicitly replaces `reconstructed_stops` with `reconstructed_spatial` and `route_dist` with `dist_spatial`.
  - If `boundary_custs` is empty, line 216 enforces `qaoa_cost <= spatial_cost + 1e-4` at the core level.
- **Reviewer Impact & Critique (Reviewer 3):**
  Reviewer 3 (Operations Research) will note:
  > *"Theorem 1 is not a mathematical property of QAOA or variational quantum states. It is an algorithmic fallback guardrail—an acceptance-rejection wrapper where the algorithm explicitly checks if candidate $\le$ baseline, and reverts to baseline if false. Calling $\min(f(x), f(x_0)) \le f(x_0)$ a 'Theorem' overstates the mathematical contribution."*
- **Verdict & Mandatory Revision:**
  The paper must frame Theorem 1 as an **"Architectural Non-Degradation Guarantee by Construction"** or **"Algorithmic Safety Guardrail Theorem,"** explicitly acknowledging that the guarantee arises from the post-reconstruction certification filter.

---

## 6. Prioritized Technical Claims Summary Table

| Claim | Location | Audit Status | Required Action |
|---|---|---|---|
| Spark performs streaming order ingestion | Abstract, Sec 1, Fig 1 | **INACCURATE** (Batch in-memory DataFrame) | Rephrase to "high-throughput batch ingestion" |
| Spark runs in distributed cluster mode | Implied in Sec 1 | **PARTIALLY TRUE** (`local[*]` on 1 host) | Clarify single-node local parallel execution |
| QAOA circuits genuinely simulated | Sec 4, Sec 6 | **VERIFIED** (Qiskit Aer, $XY$ mixer) | Retain as is |
| Absence of quantum supremacy stated | Abstract, Sec 1.3, Sec 9 | **VERIFIED** (Transparent and honest) | Retain as is |
| Crossings calculated on road network | Sec 5.4 | **MISLEADING** (2D Euclidean coordinates) | Explicitly clarify 2D Euclidean proxy |
| Feasibility & 100% preservation | Sec 8 | **VERIFIED** (0 unassigned, 0 violations) | Retain as is |
| Non-degradation guarantee holds | Sec 5.5, Theorem 1 | **VERIFIED BY CONSTRUCTION** | Clarify that it is an algorithmic guardrail |

---

*End of Technical Claim Audit.*
