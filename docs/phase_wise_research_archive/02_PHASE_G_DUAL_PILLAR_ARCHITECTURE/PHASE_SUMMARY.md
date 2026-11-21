# Phase G: Dual-Pillar Quantum & Big Data Architecture

## 1. Executive Metadata
* **Phase Identifier:** `Phase G`
* **Archive Directory:** `02_PHASE_G_DUAL_PILLAR_ARCHITECTURE/`
* **Time Horizon:** Nov 4 – Nov 5, 2026
* **Git References:** Commit `77fc748`
* **Next Phase Connection:** Phase H: Independent Big Data scaling audit to verify Spark throughput under large-scale workloads.

---

## 2. Research Objective & Motivation
Formalize the two primary research pillars: Apache Spark big data preprocessing and Qiskit QAOA quantum subproblem optimization.

---

## 3. Key Technical Changes & Implementation
Implemented `hybrid_quantum_pipeline.py`, `qaoa_subproblem_optimizer.py`, and `spark_routing_preprocessor.py`. Added unit tests and ablation harnesses.

---

## 4. Algorithmic Formulations & Innovations
* **Algorithms Evaluated / Built:** QAOA Gate-Based Solver (p=1, p=2), Spark Polar Sweep, Classical Clarke-Wright baseline.
* **Apache Spark Big Data Contributions:** PySpark spatial polar angle partitioning relative to municipal depots (theta = atan2(dy, dx)).
* **Quantum Computing & QAOA Contributions:** Qiskit Aer statevector simulation of Ising Hamiltonian for customer cluster sequencing.
* **Cooperative Optimization Engine Developments:** Dual-pillar handoff: Spark preprocessor clusters delivery nodes; subproblems passed to QAOA optimizer.

---

## 5. Experimental Configurations & Empirical Results
Executed `run_dual_pillar_benchmark.py` and `run_qaoa_subproblem_ablation.py` across 4 to 12-node instances.

### Key Quantitative Findings:
QAOA p=1 converges rapidly on small subproblems (<=8 qubits); higher qubit counts suffer exponential statevector simulation time.

---

## 6. Negative Findings, Failed Approaches & Limitations
CPU statevector simulation limits subproblems to <=12 nodes; quantum circuit simulation overhead dominates classical solve time.

---

## 7. Archived Documents in this Phase
- [`hybrid_quantum_pipeline.py`](hybrid_quantum_pipeline.py)
- [`qaoa_subproblem_optimizer.py`](qaoa_subproblem_optimizer.py)
- [`run_dual_pillar_benchmark.py`](run_dual_pillar_benchmark.py)
- [`run_qaoa_subproblem_ablation.py`](run_qaoa_subproblem_ablation.py)
- [`spark_routing_preprocessor.py`](spark_routing_preprocessor.py)
