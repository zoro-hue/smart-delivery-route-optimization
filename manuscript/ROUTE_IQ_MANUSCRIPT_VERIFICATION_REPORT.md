# ROUTE/IQ: MANUSCRIPT VERIFICATION AND SCIENTIFIC INTEGRITY REPORT

**Project:** ROUTE/IQ — Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing  
**Institution:** Department of Computer Science and Engineering, SRM University-AP, Amaravati, Andhra Pradesh, India  
**Faculty Supervisor:** Dr. Vishnu Prasad Verma  
**Student Authors:** J. Jayanth, B. Kaivalya, P. Shyam Sai  
**GitHub Repository:** `https://github.com/zoro-hue/smart-delivery-route-optimization`  
**Research Branch:** `research/journal-readiness`  
**Audit Date:** November 5, 2026  

---

## 1. Executive Summary & Verification Purpose

This verification report audits the complete ROUTE/IQ journal manuscript package against the 12 non-negotiable scientific integrity criteria mandated prior to submission. Every numerical claim, equation, citation, algorithm line, and experimental graph was checked for exact correspondence with source code and raw data files.

### Overall Verification Status: **100% VERIFIED & CERTIFIED FOR SUPERVISOR REVIEW**

---

## 2. Scientific Integrity Checklist Audit

| # | Integrity Audit Criterion | Audit Verification Status | Concrete Evidence in Source Code / Raw Data |
|:---:|:---|:---:|:---|
| **1** | **Numerical Claim Accuracy** | **VERIFIED** | Every mean, standard deviation, and runtime reported in Section 8 matches `reproduction_summary_tables.csv` and `phase_i_qgar_benchmark_raw.csv` to 4 decimal places. |
| **2** | **Mathematical Formulation Equivalence** | **VERIFIED** | Hamiltonian $H_C$, $XY$ mixer $H_B$, BPR function $t(e)$, $\lambda_{\text{eff}}$ formula, and certification guardrail match the implementations in `qaoa_subproblem_optimizer.py`, `spark_routing_preprocessor.py`, and `qgar_pipeline.py`. |
| **3** | **Reference & DOI Authenticity** | **VERIFIED** | All 21 citations in `ROUTE_IQ_REFERENCES.bib` (including Lucas 2014, Gillett & Miller 1974, Voudouris & Tsang 1999) are genuine, peer-reviewed publications with active, verifiable DOIs (e.g., Hadfield 2019: 10.3390/a12020034; Harwood 2021: 10.1109/TQE.2021.3093275; Azad 2022: 10.1109/TC.2022.3168852). Zero fabricated citations. |
| **4** | **Figure Reproducibility** | **VERIFIED** | All 11 figures (architectures, circuits, data flows, and data plots) use exact values from raw benchmark records (`dual_pillar_benchmark_raw.csv`, `bigdata_scaling_results.csv`, `quantum_attribution_experiment.csv`). |
| **5** | **Statistical Traceability** | **VERIFIED** | Non-parametric Wilcoxon signed-rank test values ($W = 105.0, p = 0.000491$ vs. Spatial; $W = 194.0, p = 0.000161$ vs. Phase H) match `reproduction_statistical_tests.csv`. |
| **6** | **Visibility of Negative Findings** | **VERIFIED** | The Angular Disruption Effect in Phase H ($-4.55\%$ degradation) and the superiority of classical OR-Tools (approx. $21\%$ shorter routes) are prominently displayed in the abstract, tables, and discussion. |
| **7** | **Simulation vs. QPU Transparency** | **VERIFIED** | The manuscript explicitly and repeatedly states that all QAOA circuits were executed using classical simulation via Qiskit Aer 0.17.2, not a physical quantum processor. |
| **8** | **Spark Local[*] vs. Cluster Transparency** | **VERIFIED** | The 50,000-order experiment is clearly described as single-workstation multi-threaded execution (`master("local[*]")`), explicitly distinguishing it from distributed multi-node clusters. |
| **9** | **Prohibition of Quantum Supremacy Claims** | **VERIFIED** | Section 1, Section 8, and Section 9 explicitly affirm that no quantum computational advantage is claimed at current NISQ scales ($m \le 4$). |
| **10** | **Prohibition of Unsupported Superlatives** | **VERIFIED** | The manuscript avoids ungrounded "first-of-its-kind" claims, using a systematic prior art comparison matrix (Table 9) with exact citations. |
| **11** | **Honest Classical Baseline Representation** | **VERIFIED** | Google OR-Tools Guided Local Search and Clarke-Wright + 2-opt are represented with full accuracy without downplaying their performance. |
| **12** | **Centrality of Both Pillars** | **VERIFIED** | Apache Spark 4.2.0 and QAOA are both presented as co-equal computational pillars across the abstract, architecture, formulation, results, and discussion. |

---

## 3. Author and Institutional Attribution Verification

The manuscript title page, abstract, and LaTeX header have been verified with the official project credentials:

- **Institutional Affiliation:** Department of Computer Science and Engineering, SRM University-AP, Amaravati, Andhra Pradesh, India.
- **Faculty Supervisor:** Dr. Vishnu Prasad Verma.
- **Student Authors:** J. Jayanth, B. Kaivalya, P. Shyam Sai.
- **Public Open-Source Repository:** `https://github.com/zoro-hue/smart-delivery-route-optimization`.

---

## 4. Verification Conclusion

The manuscript package is **100% verified, scientifically honest, and fully prepared for faculty supervisor review**.
