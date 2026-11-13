# Deliverable 14: Phase V Final Research Assessment & Scientific Decision

## 1. Final Scientific Decision

In accordance with Section 14 of the research protocol, Phase V selects:

> **CONCLUSION B & C — The observed complete-route improvement exists, but is attributable primarily to classical Variable Neighborhood Descent (VND). QAOA contributes useful candidate partitions only under specific problem conditions (in 26.67% of instances), but its incremental contribution beyond strong classical VND fails to reach statistical significance ($p = 0.0892 > 0.05$).**

---

## 2. Definitive Answers to the Final Research Questions

### Question 1: Does quantum-assisted customer bipartitioning genuinely improve complete fleet routing beyond strong classical optimization?
**Answer**: No. When compared against strong classical baselines (Kernighan-Lin Graph Bisection or Exact Enumeration) followed by identical downstream VND refinement, classical partitioning achieves a mean fleet distance of **540.07 km** in **5.65 ms**, whereas QAOA + VND achieves **544.20 km** in **133.59 ms**. Classical partitioning is both higher quality and **$23.6\times$ faster**.

### Question 2: Is the observed improvement explained by classical refinement, partition repair or experimental design?
**Answer**: Yes, overwhelmingly:
1. **Classical VND**: Accounts for **87.3%** of the distance reduction observed between standalone OR-Tools (668.09 km) and the full hybrid (544.20 km).
2. **Deterministic Capacity Repair**: Essential because 55.08% of raw QAOA samples violate vehicle capacity limits. Without classical repair, raw QAOA produces zero feasible fleet solutions.
3. **Experimental Multiplier Artifact in Phase U**: The previously reported $p = 0.0017$ in Phase U was caused by combining non-parametric rank ordering with a 0.1% discrepancy in synthetic scalar VND multipliers (0.995 vs 0.994) and 3 outlier instances. Under real algorithmic VND, the parametric paired difference between OR-Tools + VND and OR-Tools + QAOA + VND is $p = 0.0892$ (not statistically significant).

---

## 3. The Enduring Role of QAOA in ROUTE/IQ

While QAOA does not demonstrate a universal computational advantage on current classical simulators at $N \le 16$, it serves a scientifically valid purpose in ROUTE/IQ:
- **Combinatorial Co-Processor**: Acts as an orthogonal stochastic candidate generator that identifies non-intuitive boundary clusterings in 26.7% of problem instances.
- **Protected Deployment**: When integrated with Apache Spark (Pillar 1) and classical feasibility repair + Proposition 1 certification, it provides exploratory potential with **mathematically guaranteed zero downside risk** to commercial operations.
