# PHASE AG: JOURNAL READINESS ASSESSMENT & PUBLICATION ROADMAP
## ROUTE/IQ — Smart Delivery Route Optimization Using Hybrid Big Data + Quantum Computing

**Context:** Faculty-Supervised Capstone to Peer-Reviewed Journal Strategy  
**Evaluation Standard:** Peer Review Criteria of IEEE Access, Computers & Operations Research, Applied Soft Computing, and Journal of Heuristics  
**Date:** November 2026  
**Repository:** `D:\UROP\smart-delivery-route-optimization`

---

## 1. Executive Feasibility Assessment

**Can ROUTE/IQ be developed into a peer-reviewed journal paper?**

**YES — with appropriate positioning as an applied systems-engineering and comparative optimization paper.**

ROUTE/IQ is **not** suitable for theoretical mathematics or theoretical quantum physics journals (e.g., *Physical Review A*, *Mathematical Programming*), because it invents neither a novel mathematical theorem nor a new quantum complexity class.

However, ROUTE/IQ possesses strong potential for **Applied Computer Science, Operations Research, and Systems Engineering journals** (e.g., *IEEE Access*, *Applied Soft Computing*, *Computers & Industrial Engineering*, or *Expert Systems with Applications*), provided it is framed around its true strengths: **hybrid system integration, defensive guardrail engineering for NISQ solvers, and transparent multi-paradigm empirical benchmarking**.

---

## 2. Recommended Journal Targets and Positioning

### 2.1 Primary Target Venues
1. **IEEE Access (Applied Computer Science / Intelligent Transportation track):**
   - *Scope:* Broad, welcomes well-engineered systems, open-source architectures, and empirical comparative studies.
   - *Turnaround:* Fast (4–8 weeks).
   - *Impact Factor:* ~3.4.
2. **Applied Soft Computing (Elsevier):**
   - *Scope:* Hybrid metaheuristics, hyper-heuristics, and practical engineering applications.
   - *Focus:* Evaluates the cooperative coupling of Tabu Search, VND, and quantum-inspired methods.
   - *Impact Factor:* ~7.2 (Requires expanded CVRPLIB benchmarks).
3. **Computers & Industrial Engineering (Elsevier):**
   - *Scope:* Logistics operations, vehicle routing systems, Big Data applications.
   - *Focus:* Emphasizes the Apache Spark integration, strict fleet constraints, and real road network data.
   - *Impact Factor:* ~6.7.

### 2.2 Recommended Paper Title
> **"A Closed-Loop Cooperative Hybrid Framework for Capacitated Vehicle Routing: Integrating Big Data Spatial Cuts, Quantum Heuristics, and Classical Optimization with Monotonic Guarantees"**

---

## 3. Strongest Research Assets Already Present

The current ROUTE/IQ repository provides substantial, publication-grade assets:

1. **Complete, Working Implementation:** Unlike purely theoretical papers, ROUTE/IQ is an active, fully integrated full-stack software system (FastAPI backend + React GIS frontend).
2. **Strict Verification Suite:**
   - 70/70 passing backend regression tests covering fleet constraints, coverage repair, adversarial inputs, and resource metrics.
   - 10/10 automated browser test checks confirming end-to-end operational integrity.
3. **Multi-Paradigm Benchmarking on Identical Graphs:**
   - Simultaneous, zero-data-leakage comparison across 8 algorithms on the NYC road network graph.
4. **Honest Negative Findings on NISQ Quantum Heuristics:**
   - Demonstrating that standalone QAOA fails to beat classical baselines without classical local search (VND) provides a valuable, refreshing reality check against hype in the literature.
5. **Architectural Non-Degradation Contract:**
   - Formalizing how enterprise systems can safely test experimental quantum solvers without risking operational failures.

---

## 4. Missing Experiments Required Before Journal Submission

While ROUTE/IQ is fully ready for a top-grade undergraduate capstone (UROP) defense, an impactful peer-reviewed journal paper typically requires the following additional empirical extensions:

| Missing Experiment | Why It Is Needed by Journal Reviewers | Suggested Implementation Plan |
|---|---|---|
| **Standard CVRPLIB Benchmark Instances** | Reviewers expect validation on standard reference datasets (e.g., Augerat Set A/B/P, Christofides, or Uchoa instances) in addition to the NYC road graph. | Run the 8-algorithm benchmark suite on 10–15 standard CVRPLIB benchmark files ($N = 16, 32, 50, 100$). |
| **Statistical Variance Across Multiple Seeds** | Metaheuristics and quantum simulations are stochastic. Journal standards require reporting mean $\pm$ standard deviation across 10–30 runs per instance. | Execute 20 runs per algorithm with random seeds; generate boxplots and report $p$-values (e.g., Wilcoxon signed-rank test). |
| **Ablation Study Matrix** | Reviewers will want to isolate the exact contribution of each component: (1) OR-Tools alone, (2) OR-Tools + VND, (3) OR-Tools + Spark + Tabu, (4) OR-Tools + Spark + QAOA + VND. | Document incremental ablation tables quantifying percentage improvement and runtime contribution for each component. |
| **Scaling Analysis ($N=18$ to $N=200$)** | Reviewers will assess where PySpark distributed processing shifts from incurring overhead to delivering actual speedups over single-threaded pandas. | Benchmark Spark preprocessor runtime across synthetic datasets of 100, 1,000, 10,000, and 100,000 orders. |
| **Simulated Quantum Noise Models** | Qiskit Statevector simulation is ideal/noiseless. Reviewers in quantum computing tracks may ask about the impact of gate fidelity and decoherence. | Run QAOA candidate generator under Qiskit `AerSimulator` with an IBM `FakeManila` or `FakeGuadalupe` noise model to show how VND handles noisy quantum outputs. |

---

## 5. Literature Review Extensions Required

Before paper submission, the literature review should be deepened in two specific areas:

1. **Modern Classical Hyper-Heuristics:**
   - Add recent papers (2020–2025) on adaptive operator selection and contextual bandits in vehicle routing (e.g., Q-learning / Thompson sampling in large neighborhood search).
2. **Current NISQ Quantum Routing Benchmarks:**
   - Incorporate the latest 2024–2025 hybrid quantum papers to contextualize ROUTE/IQ’s closed-loop architecture against the latest D-Wave and IBM Quantum prototypes.

---

## 6. Open Limitations to Explicitly Acknowledge in the Paper

Scientific credibility hinges on transparently documenting system boundaries in the "Discussion and Limitations" section:

1. **Simulation vs Hardware Execution:** State clearly that quantum circuits were executed via Qiskit CPU statevector simulation, not on physical superconducting or trapped-ion QPUs.
2. **Overhead on Small Instances:** Acknowledge that Apache Spark introduces JVM initialization and DataFrame serialization overhead on small instances ($N \le 50$), and is intended for large-scale enterprise data ingestion.
3. **Classical Dominance in Solution Quality:** Openly report that the core solution quality is driven by OR-Tools initialization and VND 2-opt refinement, with QAOA acting as a stochastic subproblem explorer.
4. **Subproblem Size Bound:** Note that due to exponential statevector simulation cost ($2^N$), quantum subproblems are strictly bounded to $N \le 16$ boundary stops.

---

## 7. Absolute Claims to Avoid

To prevent immediate desk rejection or hostile reviewer pushback, **never** make the following claims in a paper draft:

- ❌ *Never claim "Quantum Advantage" or "Quantum Supremacy".*
- ❌ *Never claim "Proposition 1 is a new mathematical theorem."*
- ❌ *Never claim "We invented a fundamentally new routing algorithm."*
- ❌ *Never imply that PySpark was executed across a multi-node cloud cluster.*
- ❌ *Never conceal the negative performance of standalone QAOA.*

---

## 8. Summary Publication Roadmap

```
+---------------------------------------------------------------------------------------------+
|                                    JOURNAL ROADMAP                                          |
+---------------------------------------------------------------------------------------------+
|  Stage 1: Capstone Defense (Immediate)                                                      |
|  - Present ROUTE/IQ as a fully functional, verified, full-stack hybrid logistics platform. |
|  - Defend systems-engineering novelty, 0% degradation guardrail, and fair 8-algo benchmark.|
|                                                                                             |
|  Stage 2: Experimental Expansion (Post-Defense, 4–6 weeks)                                   |
|  - Run batch benchmark on 15 standard CVRPLIB instances.                                    |
|  - Execute 20 multi-seed trials for statistical variance and Wilcoxon tests.                |
|  - Add component-by-component ablation table and Spark scaling curve.                       |
|                                                                                             |
|  Stage 3: Manuscript Writing & Submission (8–10 weeks)                                      |
|  - Draft paper using IEEE Access / Elsevier LaTeX template.                                |
|  - Frame as a closed-loop cooperative architecture with fail-safe NISQ integration.         |
|  - Submit to IEEE Access or Applied Soft Computing.                                         |
+---------------------------------------------------------------------------------------------+
```
