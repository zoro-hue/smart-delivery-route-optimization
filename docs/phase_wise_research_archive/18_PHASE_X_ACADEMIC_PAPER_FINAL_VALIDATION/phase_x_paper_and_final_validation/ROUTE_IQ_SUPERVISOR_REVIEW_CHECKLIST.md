# ROUTE/IQ: Research Supervisor Review Checklist

**Project**: ROUTE/IQ — Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing  
**Supervisor**: Dr. Vishnu Prasad Verma, Department of Computer Science and Engineering, SRM University-AP  
**Date**: November 2026  
**Active Research Branch**: `research/phase-x-paper-and-final-validation`  
**Protected Branch**: `main` (`a8eb849`, untouched)

---

## 1. Compliance & Integrity Checklist

| Review Area | Verification Standard | Status | Audit Reference |
| :--- | :--- | :---: | :--- |
| **Repository Safety** | `main` branch remains protected and untouched; zero production code modified. | **VERIFIED** | HEAD commit on `research/phase-x-paper-and-final-validation`; `main` at `a8eb849`. |
| **Frontend & API Protection** | `frontend/` UI and `backend/app/main.py` preserved intact. | **VERIFIED** | Live dashboard scorecard numbers remain 100% functional. |
| **Pillar 1 Preservation** | Apache Spark 4.2.0 remains a foundational pillar for ingestion and spatial partitioning. | **VERIFIED** | Documented in Section 4 & Deliverable 5. |
| **Pillar 2 Preservation** | QAOA / Qiskit 2.4.1 remains the quantum optimization pillar for boundary Ising models. | **VERIFIED** | Documented in Section 4 & Deliverable 4. |
| **No False Quantum Claims** | No claims of physical QPU execution, quantum speedup, or quantum supremacy. | **VERIFIED** | Clearly labeled as Qiskit Aer classical CPU simulation. |
| **Statistical Integrity** | Paired instance-level comparisons ($N=15$ and $N=20$); no shot-level mislabeling. | **VERIFIED** | Recomputed in Deliverables 6 & 7 ($p = 0.089152$). |
| **Causal Decomposition** | Classical VND isolated from QAOA contribution (VND drives 87.3% of improvement). | **VERIFIED** | Traceable in Table 1 & Table 2. |
| **Citation Verification** | 100% genuine peer-reviewed scholarly references in BibTeX (`references.bib`). | **VERIFIED** | Verified in `ROUTE_IQ_REFERENCE_VERIFICATION.md`. |
| **Code Traceability** | Every table and figure mapped to raw CSV data files and Git commits. | **VERIFIED** | Documented in `ROUTE_IQ_PAPER_TO_CODE_TRACEABILITY.md`. |
| **Regression Safety** | Full test suite passing with zero regressions. | **VERIFIED** | `pytest backend/tests/ -q` $\to$ **38 passed, 0 failed in 99.08s**. |

---

## 2. Supervisor Recommendation for Publication Venues

Based on the verified experimental evidence, the paper presents a scientifically defensible, realistic study suitable for:
1. **IEEE Transactions on Quantum Engineering (TQE)**
2. **ACM Transactions on Evolutionary Learning and Optimization (TELO)**
3. **Computers & Operations Research (Elsevier)**
4. **IEEE International Conference on Quantum Computing and Engineering (QCE)**
