# ROUTE/IQ — PHASE P: COMPREHENSIVE REPRODUCIBILITY GUIDE
**Step-by-Step Instructions to Independently Replicate All Experimental Benchmarks, Prototypes, and Results**

- **Project:** ROUTE/IQ
- **Branch:** `research/phase-p-autonomous-architectures`
- **Baseline Commit:** `6bc091de1056153f7fe3d6524a7f7b82bd30b96d`
- **Hardware Prerequisites:** Any standard x86_64 CPU (minimum 8 GB RAM, 4 CPU cores). No GPU or quantum processor required.

---

## 1. Environment Setup

Verify Python 3.14 (or Python 3.10+) with required scientific packages:
```bash
# Verify Python version
python --version

# Verify core dependencies
python -c "import qiskit, qiskit_aer, pyspark, ortools, numpy, scipy; print('All Core Libraries Present!')"
```

Required versions:
- `qiskit >= 2.0.0` (installed: 2.4.1)
- `qiskit-aer >= 0.16.0` (installed: 0.17.2)
- `pyspark >= 3.5.0` (installed: 4.2.0)
- `ortools >= 9.8` (installed: 9.15.6755)
- `numpy >= 2.0` (installed: 2.4.3)
- `scipy >= 1.15` (installed: 1.17.1)

---

## 2. Running Prototype Smoke Tests

To verify that all five experimental prototypes run end-to-end with zero errors:
```powershell
python phase_p_autonomous_research/prototypes/test_prototypes_smoke.py
```
Expected output:
```text
Ran 5 tests in ~19.5s
OK
```

---

## 3. Running the Spark Scaling Benchmark

To reproduce the Spark 4.2.0 scaling and single-machine comparison:
```powershell
python phase_p_autonomous_research/benchmarks/run_spark_scaling_benchmark.py
```
Output:
- Terminal prints execution times for $N \in [10, 25, 50, 100, 250, 500]$.
- Raw CSV saved to `phase_p_autonomous_research/results/phase_p_spark_scaling_raw.csv`.

---

## 4. Running the Multi-Scale Comparative Benchmark

To reproduce the multi-scale comparison across Classical Baselines (OR-Tools, Clarke-Wright) and Hybrid Prototypes (Proto 1 through Proto 5):
```powershell
python phase_p_autonomous_research/benchmarks/run_phase_p_benchmarks.py
```
Output:
- Terminal prints paired distances, wall times, and QAOA calls.
- Raw CSV saved to `phase_p_autonomous_research/results/phase_p_benchmark_raw.csv`.

---

## 5. Verifying Repository & Frontend Integrity

To verify that zero production code or frontend UI files were modified:
```powershell
# Verify git status
git status

# Verify branch
git branch --show-current
```
- Branch must be `research/phase-p-autonomous-architectures`.
- Untracked files must be confined strictly to `phase_p_autonomous_research/` and Phase P markdown artifacts.
- Zero changes in `frontend/` or `backend/app/`.

