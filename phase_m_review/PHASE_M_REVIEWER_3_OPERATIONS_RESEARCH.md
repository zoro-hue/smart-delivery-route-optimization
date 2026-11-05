# ROUTE/IQ — PHASE M: SIMULATED PEER REVIEW REPORT 3

**Reviewer Identity:** Reviewer 3 — Operations Research and Mathematical Optimization Specialist  
**Target Venue:** *IEEE Transactions on Quantum Engineering* (Mathematical Optimization Perspective)  
**Manuscript Title:** ROUTE/IQ: A Big Data–Quantum Hybrid Framework for Directed Urban Vehicle Routing with Quality-Aware QAOA and End-to-End Route Certification  
**Authors:** J. Jayanth, B. Kaivalya, P. Shyam Sai, and Vishnu Prasad Verma (SRM University-AP)  

---

## 1. Overall Recommendation

**Recommendation:** **MINOR REVISION** (Pending framing of Theorem 1 and statistical table reconciliation)

---

## 2. Reviewer Summary

The authors address the Capacitated Vehicle Routing Problem (CVRP) in directed metropolitan road networks by proposing ROUTE/IQ, a two-pillar hybrid architecture. Pillar 1 uses Apache Spark for polar sweep spatial decomposition and capacity-window partitioning, while Pillar 2 optimizes microcluster cores ($m \le 4$) using QAOA with particle-conserving $XY$ mixers. The authors introduce Quantum-Guided Adaptive Reconstruction (QGAR), featuring quality-aware candidate selection, planar crossing regularization, and an End-to-End Route Certification Guardrail.

From an operations research perspective, this manuscript is methodologically rigorous, thoroughly benchmarked, and refreshingly candid about the performance of classical vs. quantum approaches. The authors test 20 paired instances across 5 seeds from $N=10$ to $N=100$, conduct proper non-parametric Wilcoxon signed-rank tests, compute bootstrap confidence intervals, and apply Benjamini-Hochberg FDR adjustments. 

However, two mathematical and presentation issues require revision:
1. **The Framing of Theorem 1:** Theorem 1 is presented as a profound mathematical guarantee, but in reality, it is an **acceptance-rejection safety guardrail by algorithmic construction**. The algorithm computes both the candidate route and the baseline route, checks if $C(R_{\text{QGAR}}) \le C(R_{\text{spatial}}) + \epsilon$, and falls back to the baseline if not. While practically effective, calling the tautology $\min(a, b) \le b$ a mathematical non-degradation theorem of QAOA is mathematically pretentious and misleading.
2. **Missing Seminal Literature:** The paper omits Andrew Lucas's 2014 foundational paper on Ising mappings of NP problems and Gillett & Miller's 1974 sweep algorithm for vehicle dispatch.

---

## 3. Major Strengths

1. **Rigorous Experimental Design and Statistical Testing:**
   Unlike many heuristics papers that report only point averages, the authors evaluate 20 paired instances across multiple scales, perform paired Wilcoxon signed-rank tests ($W = 105.0, p = 0.000491$), compute 95% bootstrap confidence intervals, and report rank-biserial effect sizes.
2. **Transparent Benchmarking Against Industrial Solvers:**
   The authors do not hide the fact that Google OR-Tools Guided Local Search and Clarke-Wright + 2-opt achieve $\approx 21\%$ shorter routes than ROUTE/IQ. In operations research, classical metaheuristics with global edge-exchange operators (2-opt*, relocate, swap) across all $N$ nodes routinely outperform cluster-first, route-second heuristics. Documenting this gap with complete honesty establishes strong academic credibility.
3. **Discovery of Non-Monotonic Dynamic Programming Insertion:**
   The identification in Trial 19 that inserting boundary customers via dynamic programming into a cheaper core sub-tour can produce a longer overall tour is a sharp mathematical insight that justifies the need for the campaign-level certification guardrail.
4. **Feasibility by Construction:**
   The combination of Spark cumulative capacity windowing and DP boundary insertion guarantees $100\%$ customer preservation and zero vehicle capacity violations across all instances.

---

## 4. Major Weaknesses and Mathematical Concerns

1. **Pretentious Presentation of Theorem 1:**
   In Section 5.5, Theorem 1 states:
   $$C(R_{\text{QGAR}}) \le C(R_{\text{spatial}}) + \epsilon$$
   The "proof" simply notes that the code evaluates both $r_{k, \text{QAOA}}$ and $r_{k, \text{spatial}}$ and chooses the cheaper one:
   $$r_k = \begin{cases} r_{k, \text{QAOA}}, & \text{if } C(r_{k, \text{QAOA}}) \le C(r_{k, \text{spatial}}) + \epsilon / K \\ r_{k, \text{spatial}}, & \text{otherwise} \end{cases}$$
   This is an **acceptance-rejection filter / safety guardrail**, not an intrinsic convergence proof of QAOA or variational quantum states. An operations researcher reading this will immediately perceive it as an attempt to dress up a conditional `if-else` fallback statement as deep mathematics.
   *Required Revision:* Retitle Theorem 1 as **"Proposition 1 (Campaign-Level Non-Degradation by Algorithmic Construction)"** or **"Algorithmic Safety Guardrail Theorem,"** and explicitly state that the guarantee is enforced by post-reconstruction certification.
2. **Numerical Inconsistencies in Table 3:**
   - The rank-biserial effect size $r_B$ for QGAR vs. Phase H is reported as $+0.942$, but exact calculation from $W^+ = 194.0, W^- = 16.0$ yields $r_B = \frac{194 - 16}{210} = \mathbf{+0.848}$.
   - The reported mean difference for QGAR vs. OR-Tools in Table 3 is $+45.241\text{ km}$, whereas the true mean difference across the 20 paired instances in the project's raw data is **$+25.684\text{ km}$**.
   - The reported mean difference for QGAR vs. Clarke-Wright is $+45.022\text{ km}$, whereas the true raw value is **$+26.157\text{ km}$**.
3. **Missing Literature Attribution:**
   - The polar coordinate sweep implemented in Spark is mathematically identical to the Gillett-Miller sweep algorithm (Gillett & Miller, *Operations Research*, 1974). Citing only Clarke-Wright (which is a savings heuristic, not a sweep) misattributes the origin of the polar sweep.
   - Andrew Lucas's 2014 paper (*Frontiers in Physics*) must be cited in Section 5.1 for the Ising formulation of TSP.

---

## 5. Required Revisions for the Authors

1. **Reframe Theorem 1:**
   Change "Theorem 1" to "Proposition 1 (Non-Degradation via Route Certification Guardrail)" and clarify in the prose that this bound is an algorithmic property of the dual-evaluation decision rule.
2. **Correct Table 3 Values:**
   Update Table 3 with the exact recomputed numbers:
   - QGAR vs. Phase H effect size: $r_B = +0.848$.
   - QGAR vs. OR-Tools mean difference: $+25.684\text{ km}$ ($95\%\text{ CI: } [+18.34, +33.67]\text{ km}$).
   - QGAR vs. Clarke-Wright mean difference: $+26.157\text{ km}$ ($95\%\text{ CI: } [+18.05, +34.84]\text{ km}$).
   - QGAR vs. RB-QCD mean difference: $+17.260\text{ km}$ ($95\%\text{ CI: } [+11.23, +24.03]\text{ km}$).
3. **Add Missing References:**
   Add Gillett & Miller (1974), Lucas (2014), and Voudouris & Tsang (1999) to the bibliography and cite them appropriately in Sections 2, 4, 5, and 7.

---

*End of Reviewer 3 Report.*
