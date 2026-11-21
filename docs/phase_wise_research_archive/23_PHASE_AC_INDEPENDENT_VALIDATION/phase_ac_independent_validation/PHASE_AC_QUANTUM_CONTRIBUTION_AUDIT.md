# PHASE AC DELIVERABLE 9: QUANTUM COMPUTING CONTRIBUTION AUDIT

## Project Information
- **Project:** ROUTE/IQ — Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing
- **Institution:** SRM University-AP | **Supervisor:** Dr. Vishnu Prasad Verma
- **Audit Branch:** `research/phase-ac-independent-validation`

---

## 1. Categorization of Quantum Execution Claims

To eliminate ambiguities between simulated and physical quantum computing, this audit enforces strict terminology:

1. **Physical QPU Execution:**
   - **Status:** **NOT PERFORMED / UNVERIFIED**
   - **Audit Evidence:** No IBM Quantum job IDs, calibration metrics, or physical backend execution timestamps exist in the repository.
2. **Hardware Circuit Preparation & Transpilation:**
   - **Status:** **VERIFIED**
   - **Audit Evidence:** Valid Qiskit circuits transpiled to IBM Eagle/Heron Heavy-Hex coupling graphs with basis gates $\{CZ, \sqrt{X}, X, RZ\}$ are present in `prototypes/` and `candidate_generators.py`.
3. **Classical CPU Simulation of QAOA:**
   - **Status:** **VERIFIED**
   - **Audit Evidence:** Executed using Qiskit 2.4.1 `Statevector` simulation and diagonal operator state evolution on classical x86 CPU.

---

## 2. Quantitative Evaluation of QAOA Route Contribution

Across all benchmarks (Phase AB Complete Benchmark and Phase AC Held-Out Audit), QAOA was evaluated under identical candidate budgets ($B = 512$ and $B = 256$ evaluations):

| Evaluation Metric | Phase AB 30-Instance Benchmark | Phase AC 30 Held-Out Instances | Pooled Total |
| :--- | :---: | :---: | :---: |
| **Total Subproblem Instances** | 30 | 30 | 60 |
| **QAOA Evaluated Distance (km)** | 606.36 km | 602.16 km | 604.26 km |
| **Tabu Search Evaluated Distance (km)** | 595.45 km | 595.12 km | 595.29 km |
| **Random Feasible Evaluated Distance (km)** | 602.90 km | 594.63 km | 598.77 km |
| **QAOA Head-to-Head Wins vs Tabu** | 6 / 30 (20.0%) | 7 / 30 (23.3%) | 13 / 60 (21.7%) |
| **QAOA Strictly Superior to All Classical** | N/A | 5 / 30 (16.7%) | N/A |
| **Proposition 1 Rejection Rate for QAOA** | **70.0%** (21 / 30 rejected) | **50.0%** (15 / 30 rejected) | **60.0%** (36 / 60 rejected) |
| **Mean Execution Latency** | 644.85 ms | 401.79 ms | 523.32 ms |
| **Classical Tabu Latency** | 33.85 ms | 17.56 ms | 25.71 ms |
| **Classical Speed Advantage** | **19.05x faster** | **22.88x faster** | **20.35x faster** |

---

## 3. Independent Scientific Findings on Quantum Contribution

1. **No Measurable Complete-Route Advantage:**
   In neither benchmark did QAOA achieve a statistically significant route distance advantage over classical algorithms ($p = 0.1020$ vs Tabu Search in Phase AB).
2. **Proposition 1 Masking Effect:**
   60.0% of all quantum candidate partitions produced by QAOA degraded route quality and were discarded by Proposition 1. The perceived stability of the hybrid pipeline is entirely attributable to the classical Proposition 1 fallback guardrail.
3. **Simulation Overhead Dominance:**
   On classical CPU architectures, simulated QAOA is $20\times$ slower than classical Tabu Search.
4. **Valid Scientific Role for QAOA:**
   QAOA provides a structured, non-local candidate generator capable of occasionally finding distinct bipartitions (winning 16.7% to 21.7% of instances), making it suitable as an exploratory arm within an adaptive controller rather than a standalone primary solver.
