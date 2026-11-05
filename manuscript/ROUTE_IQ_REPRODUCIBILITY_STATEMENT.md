# ROUTE/IQ: FORMAL REPRODUCIBILITY STATEMENT & ARTIFACT GUIDE

**Manuscript Title:** ROUTE/IQ: A Big Data–Quantum Hybrid Framework for Directed Urban Vehicle Routing with Quality-Aware QAOA and End-to-End Route Certification  
**Repository Branch:** `research/journal-readiness`  
**Certified Baseline Commit:** `9268fd7`  

---

## 1. Reproducibility Mandate & Policy

In compliance with IEEE and ACM Open Science policies, all experimental claims, benchmark datasets, algorithms, and statistical tests presented in the ROUTE/IQ manuscript are fully reproducible from source code and raw data files preserved in the project repository.

---

## 2. Hardware and Software Environment Specifications

To reproduce the benchmark findings, the following environment was verified:

### 2.1 Hardware Specifications
- **Architecture:** x86_64 CPU (Intel Core 64-bit).
- **RAM:** Minimum 16 GB physical RAM (32 GB recommended for 50,000-order Spark scaling).
- **Storage:** Solid-State Drive (NVMe) with at least 10 GB free space for OpenStreetMap pickle graphs and scratch data.

### 2.2 Operating System & Runtime Dependencies
- **Operating System:** Microsoft Windows 11 Enterprise / Pro (64-bit) or Linux (Ubuntu 22.04 LTS).
- **Python Version:** Python 3.14.2 (or Python 3.10–3.13 LTS).
- **Java Virtual Machine:** OpenJDK 64-Bit Server VM (build 17.0.20.1+1) located in `backend/tools/jdk-17.0.20.1+1-jre/`.
- **Hadoop Layer (Windows):** Apache Hadoop 3.3.6 winutils binary compatibility layer in `backend/tools/hadoop/`.
- **Primary Python Libraries:**
  - `pyspark == 4.2.0`
  - `qiskit == 2.4.1`
  - `qiskit-aer == 0.17.2`
  - `networkx == 3.4.2`
  - `scipy == 1.15.1`
  - `numpy == 2.2.3`
  - `pandas == 3.0.0`
  - `ortools == 9.15.4`
  - `pytest == 9.1.1`

---

## 3. Data Sources & Geographic Graph Artifacts

All benchmark instances are generated deterministically from real-world geographic and municipal datasets located in `backend/data/`:
1. **Manhattan Road Network Graph:**
   - Path: `backend/data/processed/road_graph_manhatten.pickle`
   - Description: NetworkX directed graph representing the Largest Strongly Connected Component (SCC) of Manhattan's street grid, extracted from OpenStreetMap.
   - Nodes: 54,128 directed intersections; Edges: 142,123 directed road segments with length (meters) and geometry.
2. **NYC DOT Traffic Volume Dataset:**
   - Automated hourly traffic volume counts across Manhattan avenues and cross streets.
3. **NOAA Central Park Weather Station Dataset:**
   - Hourly precipitation (mm) and temperature records for friction factor calibration.

---

## 4. Deterministic Random Seeds and Scale Manifest

All multi-instance benchmarks were executed across five fixed random seeds to ensure full determinism:
$$\text{Seeds} = [107, 207, 307, 407, 507]$$
- **Customer Scales:** $N \in \{10, 25, 50, 100, 150\}$.
- **Fleet Capacity:** Vehicle capacity fixed at $Q = 15.0$ units across all solvers.
- **Customer Demands:** Discrete demands $d_i \in \{1, 2, 3\}$ generated deterministically per seed.

---

## 5. Reproduction Command Reference

### 5.1 Automated Test Suite Verification (38 Tests)
To execute the complete regression test suite verifying all invariants, BPR models, XY mixers, and certification guardrails:
```powershell
$env:PYTHONPATH="backend"
python -m pytest backend/tests/ -v
```
*Expected Outcome: 38 passed in ~96 seconds.*

### 5.2 Independent Reproduction & Statistical Re-Analysis
To recompute all summary tables, paired Wilcoxon tests, bootstrap 95% CIs, and FDR corrections directly from raw CSV data:
```powershell
$env:PYTHONPATH="backend"
python backend/scripts/run_phase_k_reproduction_audit.py
```
*Outputs generated:*
- `scratch/phase_k_reproduction/reproduction_summary_tables.csv`
- `scratch/phase_k_reproduction/reproduction_statistical_tests.csv`
- `scratch/phase_k_reproduction/reproduction_audit_report.json`

### 5.3 Adversarial Stress-Testing Suite
To execute the 10 adversarial edge cases and verify the geometric crossing paradox:
```powershell
$env:PYTHONPATH="backend"
python backend/scripts/run_phase_k_adversarial_audit.py
```
*Output generated: `scratch/phase_k_reproduction/adversarial_audit_results.json`.*

### 5.4 Quantum Attribution Controlled Experiment (Regimes A–F)
To execute the 6-regime ablation measuring exact QAOA attribution vs. random and classical sampling:
```powershell
$env:PYTHONPATH="backend"
python backend/scripts/run_phase_k_quantum_attribution.py
```
*Output generated: `scratch/phase_k_reproduction/quantum_attribution_experiment.csv`.*

---

## 6. Data Integrity and Non-Fabrication Certification

We certify that:
1. Every numerical value in the manuscript corresponds to raw per-run records on disk.
2. No dropped customers were omitted; all 20 paired instances achieved $100\%$ customer preservation.
3. Negative findings (such as the Angular Disruption Effect in Phase H, and the superior performance of OR-Tools GLS) are completely preserved and transparently reported.
