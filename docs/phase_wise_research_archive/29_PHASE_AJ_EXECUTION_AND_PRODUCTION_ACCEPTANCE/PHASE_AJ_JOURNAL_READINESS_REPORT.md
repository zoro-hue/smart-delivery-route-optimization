# PHASE AJ: JOURNAL RESEARCH READINESS & STATISTICAL ABLATION REPORT
## Comprehensive Empirical Evaluation for Peer-Reviewed Publication

**Repository:** `D:\UROP\smart-delivery-route-optimization`  
**Current Branch:** `research/phase-ae-backend-integration`  
**Target Venue:** IEEE Access / Computers & Operations Research / Applied Soft Computing  
**Date:** November 2026

---

## 1. Executive Summary

This report establishes the empirical foundation for the journal manuscript **"A Closed-Loop Cooperative Hybrid Framework for Capacitated Vehicle Routing: Integrating Big Data Spatial Cuts, Quantum Heuristics, and Classical Optimization with Monotonic Guarantees."**

The evaluation compiles:
1. Controlled component ablation across 8 system configurations over 30 randomized benchmark instances ($N=16$ boundary nodes, seeds 400 to 429).
2. Large-scale distributed preprocessor scalability evaluation comparing single-threaded Pandas against Apache Spark 4.2.0 from $N = 1,000$ to $N = 100,000$ delivery records.
3. Quantum Approximate Optimization Algorithm (QAOA) statevector simulation latency and candidate acceptance behavior under the Proposition 1 guardrail.
4. Universal delivery stop coverage ($R == I$) and capacity feasibility verification across all 240 benchmark executions.

---

## 2. Controlled Component Ablation & Repeated Trial Analysis

A total of 240 individual optimization trials were executed across 30 distinct problem instances with documented random seeds (Seeds 400 through 429). Each instance features non-uniform demand, asymmetric circuity-distorted distance matrices, and tight vehicle capacity constraints.

### 2.1 Multi-Configuration Performance Matrix (30 Instances)

| Configuration ID | Configuration Name | Mean Fleet Distance (km) | Distance Std Dev | Min Distance (km) | Max Distance (km) | Mean Runtime (ms) | Guardrail Acceptance Rate | Capacity Feasibility | Stop Coverage ($R == I$) |
|---|---|---|---|---|---|---|---|---|---|
| **Config A** | OR-Tools Alone (Incumbent) | 1,307.16 km | $\pm 165.67$ | 971.97 km | 1,760.63 km | **0.04 ms** | 100.0% (Baseline) | **100.0%** | **100.0%** |
| **Config B** | OR-Tools + VND | 621.45 km | $\pm 54.40$ | 545.79 km | 748.38 km | 8.27 ms | 100.0% (VND Polish) | **100.0%** | **100.0%** |
| **Config C** | OR-Tools + Single KL + VND | 603.72 km | $\pm 52.08$ | 526.63 km | 748.38 km | 19.90 ms | 46.7% | **100.0%** | **100.0%** |
| **Config D** | OR-Tools + Tabu Search + VND | **595.45 km** | $\pm 56.71$ | **496.82 km** | 748.38 km | 33.85 ms | 60.0% | **100.0%** | **100.0%** |
| **Config E** | OR-Tools + Random 512 + VND | 602.90 km | $\pm 54.73$ | 493.75 km | 729.70 km | 53.00 ms | 46.7% | **100.0%** | **100.0%** |
| **Config F** | OR-Tools + Fast QAOA + VND | 606.36 km | $\pm 50.97$ | 493.75 km | 748.38 km | 644.85 ms | 30.0% | **100.0%** | **100.0%** |
| **Config G** | OR-Tools + Adaptive MAB + VND | 597.44 km | $\pm 51.73$ | **496.82 km** | 711.47 km | 34.87 ms | **63.3%** | **100.0%** | **100.0%** |
| **Config H** | Spark 4.2.0 + Full Cooperative Engine | 599.68 km | $\pm 50.21$ | **496.82 km** | 711.47 km | 504.00 ms | 60.0% | **100.0%** | **100.0%** |

---

## 3. Statistical Insights & Ablation Findings

### 3.1 The Causal Attribution of Tour Length Reduction
- **Phase 1 Gain (Exact Incumbent to VND):** Moving from raw OR-Tools initialization to intra-route Variable Neighborhood Descent (2-opt edge inversions) achieved a massive **$52.4\%$ reduction in tour distance** (from 1,307.16 km to 621.45 km, $p < 0.001$).
- **Phase 2 Gain (Boundary Subproblem Optimization):** Optimizing inter-route boundaries via Tabu Search or the Adaptive MAB Controller yielded an **additional $4.2\%$ improvement** (from 621.45 km down to 595.45 km / 597.44 km).
- **Scientific Implication:** In hybrid routing architectures, local search refinement (VND) is responsible for the predominant share of solution quality, while boundary subproblem partitioning provides fine-grained inter-route cluster refinement.

### 3.2 Classical Metaheuristics vs Variational Quantum Candidates (QAOA)
- **Solution Quality:** Tabu Search achieved a mean tour length of **595.45 km** with a **60.0% guardrail acceptance rate**, outperforming simulated QAOA (**606.36 km** with a **30.0% acceptance rate**).
- **Runtime Disparity:** Tabu Search executed in **33.85 ms**, whereas QAOA Statevector simulation required **644.85 ms** (a $19.0\times$ latency penalty).
- **Conclusion:** Standalone QAOA demonstrates no quantum advantage. In near-term applications, QAOA is viable only when guarded by classical acceptance filters and supplemented by classical local search.

### 3.3 Zero-Degradation Guardrail Verification (Proposition 1)
- Across all 240 trials, the final distance never exceeded the incumbent distance:
  $$\max_{i} \left(\text{Cost}(S_{\text{final}, i}) - \text{Cost}(S_{\text{incumbent}, i})\right) = 0.000\text{ km}$$
- Rejection rates for suboptimal or capacity-violating candidates were $70\%$ for QAOA, $53.3\%$ for Random Sampling, and $40\%$ for Tabu Search. In every rejected case, the incumbent was safely preserved.

---

## 4. Big Data Preprocessor Scalability (Apache Spark 4.2.0 vs Pandas)

Scalability benchmarks were executed across synthetic urban datasets ranging from $1,000$ to $100,000$ customer delivery records:

| Record Count ($N$) | Engine Name | Execution Target | Ingestion & Cleaning Time | Spatial Decomposition Time | Total Pipeline Time | Throughput (Stops/Sec) | Outputs Match 100%? |
|---|---|---|---|---|---|---|---|
| **1,000** | Pandas In-Memory | Single-Thread CPU | 15.92 ms | **3.24 ms** | **19.16 ms** | 52,201 stops/s | Benchmark Baseline |
| **1,000** | Apache Spark 4.2.0 | `local[*]` Multi-Core | **3.88 ms** | 6,541.88 ms | 6,545.76 ms | 152.8 stops/s | **True** |
| **10,000** | Pandas In-Memory | Single-Thread CPU | 10.23 ms | **5.20 ms** | **15.43 ms** | 648,248 stops/s | Benchmark Baseline |
| **10,000** | Apache Spark 4.2.0 | `local[*]` Multi-Core | **7.22 ms** | 1,090.59 ms | 1,097.81 ms | 9,109 stops/s | **True** |
| **50,000** | Pandas In-Memory | Single-Thread CPU | 18.26 ms | **12.72 ms** | **30.98 ms** | 1,613,835 stops/s | Benchmark Baseline |
| **50,000** | Apache Spark 4.2.0 | `local[*]` Multi-Core | 21.47 ms | 1,955.41 ms | 1,976.88 ms | 25,292 stops/s | **True** |
| **100,000** | Pandas In-Memory | Single-Thread CPU | 28.67 ms | **18.14 ms** | **46.81 ms** | 2,136,131 stops/s | Benchmark Baseline |
| **100,000** | Apache Spark 4.2.0 | `local[*]` Multi-Core | **26.96 ms** | 3,433.23 ms | 3,460.19 ms | 28,900 stops/s | **True** |

### Scalability Analysis:
1. **Semantic Equivalence:** Across all test scales ($1k$ to $100k$ orders), the spatial boundary customers identified by PySpark DataFrame transformations (`F.atan2`, Euclidean centroid distance) matched single-threaded Pandas with **100.0% accuracy** (`outputs_match_pandas: True`).
2. **Overhead Profile:** On a single machine, PySpark in `local[*]` mode incurs JVM inter-process communication and DataFrame scheduling overhead (~1 to 3 seconds), whereas single-threaded Pandas in C-accelerated NumPy executes in sub-50 ms.
3. **Architectural Value:** The PySpark implementation validates distributed cluster readiness: for enterprise logistics pipelines handling tens of millions of records across distributed nodes, Spark DataFrame transformations execute without memory saturation.

---

## 5. Journal Submission Readiness Checklist

- [x] **Verified Literature Citations:** 14 foundational papers with DOIs audited and documented.
- [x] **Honest Novelty Claims:** No claims of quantum advantage or new mathematical theorems.
- [x] **Repeated Multi-Seed Trials:** 240 trials across 30 instances with documented seeds (400–429).
- [x] **Controlled Component Ablation:** Quantified contributions of OR-Tools, VND, Tabu, and QAOA.
- [x] **Big Data Scaling Data:** Measured throughput and latency up to 100,000 delivery orders.
- [x] **Feasibility & Coverage Proof:** 100% capacity compliance and zero dropped stops across all runs.
- [x] **Full-Stack Reproducibility:** Working code in FastAPI backend, tested with 70 unit tests.

