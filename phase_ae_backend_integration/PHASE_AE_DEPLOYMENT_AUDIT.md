# PHASE AE: DEPLOYMENT & PRODUCTION READINESS AUDIT
## ROUTE/IQ — Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing
**Repository:** `D:\UROP\smart-delivery-route-optimization`  
**Branch:** `research/phase-ae-backend-integration`  
**Protected Main Baseline:** `a8eb849988201d7929566f331c1ae3afac09b632`  
**Date:** November 2026  
**Institution:** Department of Computer Science and Engineering, SRM University-AP  
**Supervisor:** Dr. Vishnu Prasad Verma  
**Investigators:** J. Jayanth, B. Kaivalya, P. Shyam Sai

---

## 1. Executive Summary

This deployment audit evaluates the operational readiness of ROUTE/IQ across computational environments, dependencies, database persistence, and API availability.

---

## 2. Environment Verification

| Component | Target Version | Installed Runtime | Health Status | Verification Mechanism |
|---|---|---|---|---|
| **Python** | 3.10+ | Python 3.14.2 AMD64 | **READY** | Native execution via `C:\Python314\python.exe`. |
| **FastAPI** | 0.110+ | 0.115.0 | **READY** | Uvicorn ASGI server with async SQLite database. |
| **Apache Spark** | 4.2.0 | 4.2.0 (`pyspark`) | **READY** | JRE verified, `local[*]` session builder operational. |
| **Qiskit** | 2.4.1 | 2.4.1 (`qiskit`) | **READY** | Statevector simulation operational. |
| **OR-Tools** | 9.10+ | 9.15.6755 | **READY** | Constraint Solver / Guided Local Search operational. |
| **Frontend UI** | Node 18+ / React 18 | Vite 5.4.2 / React 18.3.1 | **READY** | Production bundle compiled cleanly (`tsc -b && vite build`). |

---

## 3. Production Deployment Guidelines

### 3.1 Starting the Production Backend
```powershell
# Set Python path to include backend root
$env:PYTHONPATH = "backend;."
C:\Python314\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3.2 Starting the Production Frontend
```powershell
cd frontend
npm run dev
# Dashboard accessible at http://localhost:5173
```

### 3.3 Database Health & Initialization
- SQLite database is auto-migrated at startup in `backend/app/db/database.py`.
- Lifespan initializes:
  1. Road network graph for NYC 5-borough road distances (`RoadNetworkService`).
  2. Geographic boundary validation tables (`GeoValidationService`).
  3. Pre-loaded NYC delivery addresses.

---

## 4. Resilience & Graceful Fallback Matrix

| Subsystem Failure | Detection Mechanism | Automated Fallback Behavior |
|---|---|---|
| **Apache Spark Cluster Offline** | `SparkSession.builder.getOrCreate()` throws exception or JRE missing | Gracefully reverts to single-machine vectorized Pandas/NumPy polar coordinate clustering (`Single_Machine_Pandas`). No user disruption. |
| **QPU / Qiskit Statevector Simulator Timeout** | Subproblem execution exceeds latency budget | Adaptive Strategy Controller overrides to `Tabu_Search` or `Multistart_KL`. Response returned within interactive limits. |
| **OR-Tools No Solution** | Solver status is `NOT_SOLVED` | Automatic fallback to Clarke-Wright savings heuristic to produce valid initial incumbent. |
| **Candidate Rejection** | $f(\mathbf{x}_{\text{cand}}) > f(\mathbf{x}_{\text{inc}})$ or capacity exceeded | Proposition 1 Guardrail discards candidate and strictly preserves incumbent. |

