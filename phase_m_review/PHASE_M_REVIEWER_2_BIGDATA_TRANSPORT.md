# ROUTE/IQ — PHASE M: SIMULATED PEER REVIEW REPORT 2

**Reviewer Identity:** Reviewer 2 — Big Data Systems and Intelligent Transportation Systems Specialist  
**Target Venue:** *IEEE Transactions on Quantum Engineering* (Joint Transportation Systems Perspective)  
**Manuscript Title:** ROUTE/IQ: A Big Data–Quantum Hybrid Framework for Directed Urban Vehicle Routing with Quality-Aware QAOA and End-to-End Route Certification  
**Authors:** J. Jayanth, B. Kaivalya, P. Shyam Sai, and Vishnu Prasad Verma (SRM University-AP)  

---

## 1. Overall Recommendation

**Recommendation:** **MAJOR REVISION**

---

## 2. Reviewer Summary

This paper presents an architectural integration of Apache Spark 4.2.0 and gate-model QAOA for urban vehicle delivery routing. The transportation testbed uses the 54,128-node largest strongly connected component of Manhattan's road network, incorporating a Bureau of Public Roads (BPR) volume-delay travel impedance model calibrated with NYC DOT hourly traffic volumes and NOAA weather data. Spark executes polar angle sorting and cumulative demand window partitioning to generate vehicle clusters, from which microcluster cores ($m \le 4$ stops) are extracted for QAOA optimization.

While the integration of real-world GIS networks and BPR congestion delay functions is commendable and far exceeds the simplistic Euclidean planes typical of quantum computing papers, the manuscript suffers from two substantial technical overstatements:
1. **Misleading "Streaming Ingestion" Terminology:** The paper repeatedly claims Spark performs "streaming ingestion" and processes "high-volume order streams," but the actual implementation is batch in-memory DataFrame processing.
2. **Geometric Simplification of Planar Crossings on Directed Urban Grids:** The planar crossing regularizer evaluates straight-line Euclidean 2D segment intersections between customer coordinates, ignoring physical street geometry. On directed Manhattan grids with one-way avenues, straight-line non-crossing paths can produce severe physical detours, as acknowledged in the authors' own discussion.

These issues are rectifiable through precise terminology and transparent framing, but represent a major revision requirement.

---

## 3. Major Strengths

1. **Realistic Non-Euclidean Directed Urban Network:**
   The evaluation on the Largest Strongly Connected Component (SCC) of Manhattan (54,128 nodes, 142,123 directed edges) with turn restrictions and one-way streets is a major advance over prior quantum routing literature, which uniformly assumes symmetric Euclidean distances.
2. **Empirical BPR Congestion and Weather Impedance Modeling:**
   Incorporating the FHWA BPR volume-delay formula ($t(e) = t_0 [1 + 0.15 (V/C)^4] \cdot W_{\text{friction}}$) directly into shortest-path edge weights provides physical realism that accounts for dynamic traffic bottlenecks.
3. **Linear Big Data Scalability up to 50,000 Orders:**
   The Spark scaling experiments (Table 5) demonstrate true $O(N \log N)$ execution scaling from 1,000 to 50,000 orders (6,678 clusters) with $100\%$ customer preservation and zero capacity violations.

---

## 4. Major Weaknesses and Technical Concerns

1. **Mischaracterization of Spark Processing as "Streaming":**
   In the Abstract, Section 1.2, Section 4.1, and Figure 1, the authors state that Apache Spark *"actively ingests high-volume order streams"* and processes *"streaming order data."* 
   However, reviewing the methodology in Section 6 and Algorithm 1, the pipeline ingests a static batch DataFrame of $N$ orders, performs parallel sorting and window partitioning, and returns clusters. There is no Kafka ingestion, no Spark Structured Streaming sliding window, no event-time watermarking, and no continuous stream execution. Calling batch DataFrame processing "streaming" will be rejected by distributed systems reviewers.
2. **Local Multiprocessing vs. Distributed Cluster Execution:**
   All Spark experiments were executed in `local[*]` mode on a single workstation JVM. While this proves that PySpark Catalyst expressions function correctly, it does not evaluate network serialization overhead, distributed shuffle spill to disk, or worker-node failover across a multi-node cluster (such as AWS EMR or Databricks). This operational distinction must be stated clearly upfront.
3. **Straight-Line 2D Crossings vs. Directed Street Graph Paths:**
   The planar crossing regularizer calculates intersections between straight Euclidean segments in $\mathbb{R}^2$ connecting customer coordinates. On Manhattan's grid, delivery vans travel along orthogonal avenues and streets. 
   - Two straight lines can cross visually on a map without their physical street trajectories intersecting.
   - More critically, avoiding a 2D Euclidean crossing on a one-way avenue grid can force a vehicle to circumnavigate multiple city blocks, creating a physical detour (as seen in Trial 0 where avoiding a crossing caused a $+0.7\%$ penalty).
   The authors must explicitly state that the crossing regularizer is a 2D geometric heuristic proxy, not a topological analysis of the directed road network.
4. **Volume Data vs. Speed Probes:**
   The authors correctly clarify in code that NYC DOT data provides automated volume counts (vehicles/hour) rather than GPS probe speeds. This distinction should be stated explicitly in Section 3.1 of the main manuscript.

---

## 5. Required Revisions for the Authors

1. **Terminology Correction (Batch vs. Streaming):**
   Replace all mentions of "streaming ingestion" and "streaming order streams" with **"high-throughput batch order ingestion"** or **"distributed batch spatial partitioning."**
2. **Clarification of Local Workstation Execution:**
   In Section 6 and Section 10, explicitly emphasize that Spark was run in single-node `local[*]` mode, and discuss the expected impact of network shuffle latencies in multi-node cloud deployments.
3. **Accurate Description of the Crossing Regularizer:**
   Clarify in Section 5.4 that planar crossings are computed over straight-line segments in Euclidean coordinate space, serving as an empirical inductive bias ($96.4\%$ accuracy) rather than a street-network graph invariant.
4. **Reconciliation of Table 3 Distances:**
   In Table 3, the reported mean difference between QGAR and OR-Tools is $+45.241\text{ km}$, but the true 20-instance global mean difference in the project's raw data is $+25.684\text{ km}$. This numerical error must be corrected.

---

*End of Reviewer 2 Report.*

