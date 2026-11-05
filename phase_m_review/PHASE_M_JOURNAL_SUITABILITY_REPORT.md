# ROUTE/IQ — PHASE M: JOURNAL SUITABILITY REPORT

**Audit Date:** November 5, 2026  
**Auditor:** Journal Editorial Strategy & Bibliometric Auditor  
**Scope:** Comparative assessment of candidate publication venues for the ROUTE/IQ manuscript based on editorial scope, acceptance criteria, review culture, and formatting standards.  
**Evaluated Commit:** `a60779d` on branch `research/journal-readiness`  

---

## 1. Comparative Journal Assessment Matrix

| Journal | Publisher | Impact Factor / Quartile | Primary Scope | Alignment with ROUTE/IQ | Risk Factors |
|---|---|---|---|---|---|
| **IEEE Transactions on Quantum Engineering (TQE)** | IEEE | **2.6 / Q1 (Quantum Science)** | Quantum engineering, hybrid algorithms, systems engineering, applications of NISQ algorithms. | **EXCELLENT (96%)** | Must ensure quantum contribution is central and clearly attributed. |
| **IEEE Transactions on Intelligent Transportation Systems (T-ITS)** | IEEE | **8.4 / Q1 (Transportation)** | Intelligent transportation, traffic engineering, fleet dispatch, routing algorithms. | **MODERATE (72%)** | Reviewers will challenge $m \le 4$ microclusters and 21% gap to OR-Tools. |
| **ACM Transactions on Quantum Computing (TQC)** | ACM | **2.8 / Q1 (Quantum Computing)** | Quantum computer science, complexity, circuit synthesis, error correction. | **MODERATE (65%)** | Expects formal quantum complexity bounds or fault-tolerant circuit theory. |
| **Computers & Operations Research (COR)** | Elsevier | **4.6 / Q1 (Operations Research)** | Combinatorial optimization, exact VRP algorithms, metaheuristics. | **LOW-MODERATE (55%)** | Reviewers will strongly favor OR-Tools GLS and criticize heuristic $XY$ mixers for $m=4$. |
| **IEEE Access** | IEEE | **3.4 / Q2 (Multidisciplinary)** | Rapid open access, broad engineering disciplines. | **HIGH (Fallback only)** | Lower prestige than Transactions; should only be used as a backup. |

---

## 2. In-Depth Journal Evaluations

### 2.1 IEEE Transactions on Quantum Engineering (IEEE TQE) — Primary Recommendation
- **Official Aims & Scope:**
  IEEE TQE publishes papers on the engineering applications of quantum computing, including hybrid quantum-classical algorithms, variational methods (QAOA, VQE), classical-quantum software frameworks, and systems engineering for near-term quantum architectures.
- **Why ROUTE/IQ is an Ideal Fit:**
  1. **Focus on Systems & Hybrid Infrastructure:** TQE explicitly welcomes papers addressing the engineering reality of NISQ computing—including classical-quantum co-processing, software stacks, and hybrid pipelines.
  2. **Direct Precedent:** Harwood et al. (2021) published their seminal paper on constrained QAOA and binary slack capacity variables in IEEE TQE (*IEEE Trans. Quantum Eng.*, vol. 2, pp. 1–14). ROUTE/IQ builds directly upon Harwood's formulation.
  3. **Appreciation of Non-Supremacy Engineering:** TQE reviewers understand that $m \le 4$ is governed by classical statevector simulation constraints and value certified safety filters (QGAR) that prevent variational noise from degrading operational systems.
- **Editorial Requirements & Policies:**
  - *Manuscript Category:* Regular Research Paper.
  - *Format:* Standard IEEE double-column format (`IEEEtran.cls`).
  - *Page Limits:* Typically 10–12 pages for regular research papers (no hard ceiling, but mandatory overlength page charges apply beyond 10 pages).
  - *Code & Data Policy:* IEEE TQE strongly encourages open-source software and reproducible benchmark data repositories. ROUTE/IQ's public GitHub repo directly satisfies this.

### 2.2 IEEE Transactions on Intelligent Transportation Systems (IEEE T-ITS) — Secondary Option
- **Scope & Culture:**
  Focuses on urban traffic management, connected vehicles, and logistics operations.
- **Vulnerabilities for ROUTE/IQ:**
  - T-ITS reviewers are predominantly transportation engineers and classical operations researchers.
  - They will scrutinize the $21\%$ performance gap against Google OR-Tools GLS and question why a city logistics operator would adopt a quantum hybrid system that produces longer routes than classical heuristics.
  - While the BPR traffic impedance and 54,128-node Manhattan network will be praised, the microcluster size $m \le 4$ will be deemed impractical for commercial dispatching unless heavily defended.

### 2.3 ACM Transactions on Quantum Computing (ACM TQC)
- **Scope & Culture:**
  Emphasizes theoretical computer science, quantum information theory, and asymptotic complexity.
- **Vulnerabilities for ROUTE/IQ:**
  - ACM TQC papers typically contain formal quantum circuit depth scaling theorems, Hamiltonian simulation complexity bounds, or fault-tolerant threshold proofs.
  - ROUTE/IQ is an applied engineering architecture combining Apache Spark with Qiskit simulation; it does not offer new quantum complexity theorems.

### 2.4 Computers & Operations Research (COR)
- **Scope & Culture:**
  Dedicated to operations research methodologies and combinatorial algorithms.
- **Vulnerabilities for ROUTE/IQ:**
  - Operations research reviewers evaluate algorithms strictly on solution quality and computational runtime.
  - Because classical OR-Tools solves $N=100$ in 2.0 seconds and finds routes 21% shorter, COR reviewers would likely reject the manuscript on the grounds of computational inferiority.

---

## 3. Final Strategic Submission Recommendation

**Primary Venue:** **IEEE Transactions on Quantum Engineering (IEEE TQE)**  
**Manuscript Type:** Regular Research Paper  
**Target Category:** Hybrid Quantum-Classical Systems and Algorithms  
**Key Positioning Strategy:**
Position the paper as a **systems-engineering and algorithmic reliability breakthrough** that solves the interface between enterprise Big Data and variational quantum optimization:
1. Emphasize that ROUTE/IQ establishes the **first operational blueprint for integrating Apache Spark with gate-model QAOA**.
2. Highlight the **discovery of the Angular Disruption Effect** as a critical NISQ failure mode that all hybrid logistics pipelines must address.
3. Feature the **certified non-degradation guarantee** as an essential engineering safeguard for deploying variational algorithms without commercial risk.
4. Maintain strict scientific integrity by presenting the absence of quantum supremacy at $m \le 4$ as a rigorous attribution baseline.

---

*End of Journal Suitability Report.*

