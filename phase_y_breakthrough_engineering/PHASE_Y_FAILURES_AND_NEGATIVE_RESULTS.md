# Deliverable 10: Phase Y Failures, Bottlenecks & Negative Findings

## 1. Transparency Standard

In compliance with strict scientific integrity, all experimental failures, computational bottlenecks, and infrastructure blockers encountered in Phase Y are documented below:

---

## 2. Documented Failures and Limitations

### 1. Failure to Beat Classical Kernighan-Lin
- **Attempt**: Developed six advanced quantum formulations (Formulations A–F), including continuous XY mixers, warm starts, and asymmetric directed QUBOs.
- **Result**: FAILED. Classical Kernighan-Lin achieved **542.28 km**, outperforming all six quantum formulations (best quantum: XY Mixer at **545.10 km**). Kernighan-Lin ran in **1.06 ms**, which is $37.6\times$ faster than Adaptive Fast QAOA (39.84 ms).
- **Cause**: Graph bisection on planar routing neighborhoods exhibits clean convex separability that pairwise vertex swaps resolve in $\mathcal{O}(N^2)$ iterations, leaving virtually no room for quantum tunneling advantages.

### 2. Incompleteness of XY-Mixer Feasibility
- **Attempt**: Formulation B (continuous XY mixer) was deployed to eliminate capacity violations by restricting evolution to the $\sum x_i = k$ subspace.
- **Result**: PARTIALLY FAILED. While raw feasibility improved from 31.5% to 79.9%, it did not reach 100%. In 20.1% of samples, capacity violations still occurred because customer demands are non-uniform ($q_i \in \{1, 2, 3, 4\}$). Preserving binary Hamming weight does not preserve weighted demand sums.

### 3. Blocked Real QPU Hardware Execution
- **Attempt**: Attempted to connect to real IBM Quantum hardware backends through Qiskit Runtime.
- **Result**: BLOCKED. `qiskit-ibm-runtime` is not installed, and no API credentials or authorized tokens are available in the host environment. No physical hardware execution could be conducted.

### 4. Blocked Multi-Node Docker Cluster Execution
- **Attempt**: Designed containerized Docker-based Apache Spark multi-worker standalone cluster.
- **Result**: BLOCKED. Docker Engine is not installed on the Windows host operating system. The cluster configuration was fully authored and verified in `phase_y_breakthrough_engineering/cluster/`, but physical distributed execution remains unverified.

