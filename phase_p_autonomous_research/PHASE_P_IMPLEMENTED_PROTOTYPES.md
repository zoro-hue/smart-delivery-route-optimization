# ROUTE/IQ — PHASE P: IMPLEMENTED EXPERIMENTAL PROTOTYPES
**Architectural Verification and Source Code Documentation of Five Isolated Prototypes**

---

## 1. Prototype Directory & Interface Summary

All experimental prototypes are isolated in `phase_p_autonomous_research/prototypes/` with zero production API code modifications:

1. `common_evaluator.py`: Standardized problem generator (`ProblemInstance`) with NYC Midtown coordinates, asymmetric Manhattan road impedance, and rigorous CVRP feasibility auditing (`audit_solution_feasibility`).
2. `proto_1_classical_seeded_qaoa.py`: Architecture 1 — Classical-Seeded Warm-Start QAOA with XY Hopping Mixers.
3. `proto_2_spark_hierarchical_qaoa.py`: Architecture 2 — Spark-Driven Hierarchical Quantum Decomposition with DP Boundary Insertion.
4. `proto_3_adaptive_neighborhood_qaoa.py`: Architecture 3 — Adaptive Quantum Neighborhood Search with Planar Crossing Detection.
5. `proto_4_cooperative_qaoa_qiga.py`: Architecture 5 — Cooperative QAOA + Classically-Seeded QIGA.
6. `proto_5_iterative_feedback_controller.py`: Architecture 15 — Incumbent-Preserving Cooperative Quantum Engine (IP-CQE).
7. `test_prototypes_smoke.py`: Automated regression test runner executing all five prototypes against a benchmark instance.

---

## 2. Smoke Test Execution Verification

- **Command:** `C:\Python314\python.exe phase_p_autonomous_research/prototypes/test_prototypes_smoke.py`
- **Result:** `5 passed in 19.543s (OK)`
- **Feasibility Rate:** 100% across all 5 prototypes.
- **Circuit Transpilation:** Integrated `qiskit.transpile()` to decompose `XXPlusYYGate` into native Qiskit Aer basis gates (`rx`, `rz`, `cx`).

---

## 3. Prototype Characteristics Matrix

| Prototype | Architecture | Big Data Component | Quantum Engine | Classical Engine | Key Mechanism |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Proto 1** | Arch 1: CS-QAOA | Road matrix generation | Qiskit Aer Warm-Start QAOA ($N_q=16$, $p=1$) | OR-Tools Initial Seed + Hungarian Projection | Permutation basis state $|x_{\text{seed}}\rangle$ with XY mixers |
| **Proto 2** | Arch 2: Spark-HQD | PySpark 4.2.0 Polar Window Partitioning | Qiskit Aer Subproblem Sequencing | DP Minimum Incremental Cost Boundary Insertion | Scalable decomposition for $N \ge 50$ |
| **Proto 3** | Arch 3: AQNS | Calibrated BPR Detour Factor | Qiskit Aer Uncrossing QAOA | 2D Planar Segment Intersection Detector | Crossings trigger localized 4-node QAOA |
| **Proto 4** | Arch 5: Coop-QQ | Global customer coordinate sharding | Periodic Qiskit Aer QAOA Injection | Q-bit amplitude bias $(\alpha, \beta)$ from Clarke-Wright | Bi-directional QIGA evolution + QAOA sub-tour polish |
| **Proto 5** | Arch 15: IP-CQE | Spark Spatial Partitioning | Warm-Start QAOA on Bottlenecks | OR-Tools Baseline + 2-opt Polish + Guardrail | Proposition 1 Monotonic Non-Degradation |

