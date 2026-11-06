# ROUTE/IQ — PHASE P: CONTROLLED EXPERIMENTAL BENCHMARKING PROTOCOL
**Standardized Test Protocol, Hardware Baseline, and Evaluation Metrics**

---

## 1. Experimental Objectives

This protocol provides the definitive framework to test the central research hypothesis:
> *Does classical-seeded quantum-assisted (QAOA) and quantum-inspired (QIGA) optimization yield statistically significant improvements over strong classical baselines under strictly fair, identical computational budgets?*

To prevent experimental bias, the protocol enforces:
1. **Identical Road Geometries:** All solvers evaluate the exact same NYC road graph distance matrix \(\mathbf{D}\) and BPR travel-time matrix \(\mathbf{T}\).
2. **Identical Hardware Environment:** All runs execute on the identical dedicated CPU compute node.
3. **Controlled Wall-Clock Budgets:** Classical baselines are given ample execution time (up to 30 seconds) rather than artificially truncated limits.
4. **Reproducibility:** Standardized random seeds \(\{42, 101, 2024, 777, 999\}\) across 5 independent trials per configuration.

---

## 2. Benchmark Problem Instances

Testing spans three problem scales representing urban delivery distribution regimes:

| Scale | Customers (\(N\)) | Fleet Size (\(M\)) | Capacity (\(Q\)) | Geographic Scope | Density Regime |
| :---: | :---: | :---: | :---: | :--- | :--- |
| **Small** | \(N = 25\) | \(M = 3\) | \(50\text{ units}\) | Lower Manhattan & Midtown | Dense Urban Core |
| **Medium** | \(N = 50\) | \(M = 5\) | \(60\text{ units}\) | Manhattan + Western Queens | Multi-Borough River Crossing |
| **Large** | \(N = 100\) | \(M = 8\) | \(75\text{ units}\) | 5-Borough NYC Wide | Large-Scale Regional Logistics |

### Road Graph Specification
- **Nodes:** 54,128 intersections indexed in spatial KD-Tree.
- **Edges:** 142,123 directed road segments with one-way restrictions and speed limits.
- **Source:** Authenticated OpenStreetMap NYC road network pickle file (`road_graph_newyork.pickle`).

---

## 3. The 8 Controlled Configurations (A through H)

To decouple the contribution of every architectural component, 8 configurations are evaluated on every problem instance:

```
[Pure Classical Baselines]
  Config A: Google OR-Tools CVRP Alone (Exact Guided Local Search)
  Config B: Clarke–Wright Savings + 2-opt Local Search

[Pure Quantum / Quantum-Inspired Baselines]
  Config C: Unseeded QIGA Alone (Uniform random initial amplitudes)
  Config D: Unseeded QAOA Alone (Random uniform superposition |+>^Nq)

[Cooperative Hybrid Configurations]
  Config E: Classical Initialization + QAOA on Qiskit Aer (Cooperative Micro-Bottlenecks)
  Config F: Classical Initialization + Seeded QIGA
  Config G: Classical Initialization + QAOA + QIGA (Full Hybrid Synthesis)
  Config H: Apache Spark 4.2.0 + Full Cooperative Hybrid System
```

### Configuration Parameters

| Config | Solvers Involved | Classical Seeding | Subproblem Engine | Partitioning Engine |
| :---: | :--- | :---: | :--- | :--- |
| **A** | Google OR-Tools | N/A | Global C++ Solver | N/A |
| **B** | Clarke–Wright, 2-opt | N/A | Global Heuristic | N/A |
| **C** | QIGA | None (Uniform) | Q-Bit Evolutionary | Single-Machine |
| **D** | QAOA (Qiskit Aer) | None (\(|+\rangle\)) | Micro-clusters (\(K=4\)) | Single-Machine |
| **E** | OR-Tools + QAOA | Permutation State | QAOA with XY Mixers | Single-Machine |
| **F** | OR-Tools + QIGA | Amplitude Seeding | Seeded QIGA | Single-Machine |
| **G** | OR-Tools + QAOA + QIGA | Dual Seeding | QAOA (\(K \le 4\)) + QIGA (\(K > 4\)) | Single-Machine |
| **H** | Spark + OR-Tools + QAOA + QIGA | Dual Seeding | Full Cooperative Engine | **Apache Spark 4.2.0** |

---

## 4. Standardized Metrics Recorded

For every experimental run, the test harness records 12 primary metrics:

### 4.1 Solution Quality Metrics
1. **Total Physical Road Distance (\(D_{\text{total}}\), km):** Sum of physical road segment lengths.
2. **Total Generalized Impedance Cost (\(C_{\text{total}}\)):** BPR travel-time cost.
3. **Improvement over Best Classical Baseline (\(\Delta \%\)):**
   \[
   \Delta \% = \frac{D_{\text{classical\_best}} - D_{\text{evaluated}}}{D_{\text{classical\_best}}} \times 100\%
   \]
4. **Planar Edge Crossing Count (\(\mathcal{X}\)):** Number of geometric line intersections.

### 4.2 Feasibility & Constraint Metrics
5. **Feasibility Status (\(\text{IsFeasible}\)):** Boolean flag (true iff capacity and uniqueness strictly satisfied).
6. **Capacity Violations (\(V_{\text{cap}}\)):** Number of vehicle routes exceeding \(Q\).
7. **Unserved Customers (\(U_{\text{cust}}\)):** Count of skipped or dropped customer stops.

### 4.3 Computational Efficiency & Resource Metrics
8. **Total Wall-Clock Runtime (\(T_{\text{total}}\), s):** End-to-end execution latency.
9. **Component Latency Breakdown:**
   - \(T_{\text{spark}}\): Big data partitioning and impedance matrix time.
   - \(T_{\text{init}}\): Classical solver initialization time.
   - \(T_{\text{qaoa}}\): Qiskit Aer statevector simulation time.
   - \(T_{\text{qiga}}\): Q-bit evolutionary simulation time.
   - \(T_{\text{recon}}\): Dynamic programming tour reconstruction and 2-opt polish.
10. **Logical Qubits Allocated (\(N_q\)):** Peak quantum register width.
11. **Variational Circuit Depth (\(p\)):** Number of QAOA alternating layers.
12. **Quantum Candidate Acceptance Rate (\(R_{\text{accept}}\)):** Percentage of QAOA backbones accepted by the Incumbent Guardrail.

---

## 5. Controlled Hardware & Software Environment

To ensure strict reproducibility:
- **Processor:** Intel Core i7 / AMD Ryzen (x86_64), 8 physical cores.
- **RAM:** 16 GB DDR4.
- **Operating System:** Windows 11 / Ubuntu 22.04 LTS.
- **Python Runtime:** Python 3.11 / 3.14.
- **Java Runtime:** OpenJDK 17.0.20+ (64-Bit).
- **Core Libraries:**
  - `pyspark`: 4.2.0
  - `qiskit`: 2.4.1
  - `qiskit-aer`: 0.16.4
  - `ortools`: 9.12.x
  - `networkx`: 3.4.x
  - `scipy`: 1.15.x

---

## 6. Execution Safeguards

1. **No Hardware Claim:** The protocol explicitly records the Qiskit Aer simulator backend (`AerSimulator`).
2. **Timeout Protection:** Any individual solver exceeding 60.0 seconds is terminated and marked as timed-out.
3. **Data Integrity:** All raw JSON execution logs are saved to an immutable benchmark log directory (`experiments/phase_p_raw_logs/`) with cryptographic SHA-256 hashes.

