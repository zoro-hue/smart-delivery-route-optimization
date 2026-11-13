# ROUTE/IQ — PHASE M: SIMULATED PEER REVIEW REPORT 1

**Reviewer Identity:** Reviewer 1 — Quantum Computing and Variational Algorithms Specialist  
**Target Venue:** *IEEE Transactions on Quantum Engineering*  
**Manuscript Title:** ROUTE/IQ: A Big Data–Quantum Hybrid Framework for Directed Urban Vehicle Routing with Quality-Aware QAOA and End-to-End Route Certification  
**Authors:** J. Jayanth, B. Kaivalya, P. Shyam Sai, and Vishnu Prasad Verma (SRM University-AP)  

---

## 1. Overall Recommendation

**Recommendation:** **MINOR REVISION**

---

## 2. Reviewer Summary

The manuscript presents ROUTE/IQ, a hybrid classical-quantum framework coupling Apache Spark distributed preprocessing with QAOA on Qiskit Aer to solve the Capacitated Vehicle Routing Problem (CVRP) on directed urban road graphs. The quantum contribution centers on microcluster core sequencing ($m \le 4$ stops, requiring up to 16 logical qubits) formulated as an Asymmetric Traveling Salesperson Problem (ATSP). The authors utilize particle-conserving $XY$ mixers (`XXPlusYYGate`) to restrict state evolution to the one-hot permutation subspace, combined with exact binary slack variable encoding for capacity penalties. 

To combat variational noise at depth $p=1$, the authors identify the "Angular Disruption Effect" and introduce Quantum-Guided Adaptive Reconstruction (QGAR), which incorporates quality-aware candidate decoding from measurement bitstrings, planar crossing regularization, and an end-to-end non-degradation certification guardrail.

Overall, this is a well-engineered and uncharacteristically honest quantum applications paper. Unlike many submissions in the quantum logistics space that make sweeping claims of quantum advantage on toy graphs, the authors explicitly state that classical enumeration easily solves $m \le 4$ subproblems and that mature classical heuristics (OR-Tools) achieve 21% shorter routes. The paper focuses appropriately on the architectural, noise-mitigation, and safety infrastructure necessary for variational algorithms. With minor technical clarifications regarding circuit compilation and mixer gate counts, the paper will make a strong contribution to *IEEE Transactions on Quantum Engineering*.

---

## 3. Major Strengths

1. **Particle-Conserving $XY$ Mixer Implementation:**
   The adoption of $XY$ mixers ($\frac{1}{2}(XX + YY)$) to preserve the one-hot Hamming weight subspace is a significant improvement over standard transverse-field mixers ($X$). By maintaining feasibility natively in the quantum state space, the authors avoid destructive quadratic penalty terms that distort the energy spectrum.
2. **Exemplary Scientific Integrity Regarding Quantum Supremacy:**
   The authors deserve high commendation for explicitly refraining from exaggerated claims of quantum advantage. The controlled ablation across six regimes (Table 4) proves that at $m \le 4$ nodes ($16$ qubits), random bitstrings and classical local search achieve comparable performance. Identifying QAOA's current role as an effective stochastic candidate proposer rather than an oracle of quantum advantage is refreshing and scientifically defensible.
3. **Identification of the Angular Disruption Effect:**
   The paper correctly identifies a critical failure mode of near-term variational algorithms: shallow QAOA states under-converge, and inserting noisy candidate bitstrings into spatial clusterings shatters the monotonic angular sweep, causing routing degradation ($-4.55\%$ in Phase H). Documenting this effect and solving it via crossing regularization is a valuable practical contribution for NISQ literature.
4. **Exact Binary Slack Formulation:**
   The macro capacity formulation builds soundly on Harwood et al. (2021), using exact binary slack expansion rather than continuous approximations.

---

## 4. Major Weaknesses and Technical Questions

1. **Circuit Decomposition and Two-Qubit Gate Overhead:**
   The manuscript describes the $XY$ mixer as being implemented via `XXPlusYYGate(2 \beta)`. However, the authors do not provide the compiled gate counts or decomposition for hardware execution. On native superconducting architectures (e.g., IBM Quantum eagle/heron processors), `XXPlusYYGate` must be decomposed into elementary CNOT (or ECR) and single-qubit gates. 
   *Question:* For a 16-qubit circuit with all-to-all or nearest-neighbor mixer connectivity, what is the exact CNOT count and circuit depth after transpilation to a standard basis set (`cx`, `rz`, `sx`)?
2. **COBYLA Parameter Optimization Landscapes:**
   The authors execute QAOA at depth $p=1$ with 30 classical COBYLA iterations. At $p=1$, there are only two variational parameters $(\gamma, \beta)$. Did the authors observe barren plateaus or local minima traps during COBYLA convergence? A 2D contour plot of the expectation value $\langle H_C \rangle$ over $(\gamma, \beta) \in [0, 2\pi] \times [0, \pi]$ would provide valuable insight into the parameter landscape.
3. **Statevector vs. Shot-Based Sampling Noise:**
   Table 4 evaluates Regime B with 2,048 measurement shots. What fraction of the decoded bitstrings represented valid permutation matrices prior to Kuhn-Munkres projection? Providing the raw feasibility ratio before projection would strengthen the empirical analysis of $XY$ mixer confinement.

---

## 5. Required Revisions for the Authors

1. **Transpiled Circuit Complexity:**
   Add a brief discussion or table detailing the transpiled gate count (specifically 2-qubit CNOT counts) and two-qubit gate depth for $m=3$ (9 qubits) and $m=4$ (16 qubits) under a linear or heavy-hex coupling map.
2. **Pre-Projection Permutation Feasibility:**
   Report the percentage of raw measurement bitstrings that satisfied the permutation constraints natively versus those requiring Kuhn-Munkres projection.
3. **Effect Size Typo in Table 3:**
   In Table 3, the rank-biserial effect size for QGAR vs. Phase H is listed as $+0.942$. Recomputing from the reported Wilcoxon statistics ($W^+ = 194.0, W^- = 16.0$) yields $r_B = \frac{194 - 16}{210} = +0.848$. This typographical discrepancy must be corrected.

---

*End of Reviewer 1 Report.*

