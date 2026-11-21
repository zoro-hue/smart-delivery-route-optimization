# PHASE AA GENERALIZATION & ROBUSTNESS
## Out-of-Sample Validation Across Diverse Held-Out Problem Topologies ($N=20$)
**ROUTE/IQ — Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing**  
**Department of Computer Science and Engineering, SRM University-AP**  
**Supervisor:** Dr. Vishnu Prasad Verma  

---

## 1. EXPERIMENTAL DESIGN: DIVERSE HELD-OUT TEST SET

To ensure that conclusions are not artifacts of a specific instance generator or parameter regime, Phase AA evaluated all algorithms on a strictly held-out test suite of **$N=20$ diverse benchmark instances** (seeds 800 to 819) featuring:
- **Spatial Topologies:** Both Gaussian-clustered bi-modal distributions and uniform dispersed distributions.
- **Capacity Constraint Regimes:** Tight vehicle slack ($52\%$ capacity ceiling) and generous slack ($65\%$).
- **Asymmetric Travel Matrices:** Directional traffic volume friction factors ($c_{ij} \ne c_{ji}$).

No algorithm parameters, hyperparameters, or thresholds were tuned on these held-out instances.

---

## 2. OUT-OF-SAMPLE BENCHMARK RESULTS

| Algorithm | Search Mode / Budget | Mean Fleet Distance (km) | Std Dev (km) | Mean Runtime (ms) | $p$-value vs. Single KL | $p$-value vs. QAOA (Prop 1) |
|---|---|---|---|---|---|---|
| **Single-Pass KL + VND** | Deterministic (1 eval) | 484.67 | 78.45 | **5.12 ms** | Baseline (1.0) | $p = 0.0708$ |
| **Tabu Search + VND** | Equal Evals (512 evals) | **476.33** | 76.12 | **24.67 ms** | $p = 0.1420$ | **$p = 0.4450$** |
| **Multistart KL + VND** | Equal Time (~57 ms) | **474.81** | 74.88 | 56.96 ms | $p = 0.1180$ | **$p = 0.5903$** |
| **Raw QAOA (No Prop 1)** | Unassisted QAOA (512 shots)| 475.71 | 79.10 | 62.19 ms | **$p = 0.3018$** | $p = 0.2810$ |
| **Fast QAOA (With Prop 1)**| Hybrid with Guardrail | 470.37 | 75.30 | 62.19 ms | **$p = 0.0708$** | Baseline (1.0) |

---

## 3. INFERENTIAL STATISTICAL AUDIT & MULTIPLE TESTING CORRECTION

### 1. Quantum Advantage Disappears Even Against Single-Pass KL ($p = 0.0708$)
On this diverse held-out test set, even with the benefit of the Proposition 1 asymmetric guardrail, Fast QAOA achieved a $p$-value of:
$$p = 0.0708 \quad (> 0.05)$$
Because $p > 0.05$, **the null hypothesis cannot be rejected**. The Phase Z finding of $p = 0.0100$ failed to replicate across out-of-sample problem distributions.

### 2. Standalone Raw QAOA Fails Completely ($p = 0.3018$)
When QAOA is evaluated without classical incumbent substitution:
- Raw QAOA distance: **$475.71\text{ km}$** vs. Single-Pass KL: **$484.67\text{ km}$**.
- Paired $t$-test: $t = -1.060, p = 0.3018$.
- Standalone QAOA shows zero statistically detectable benefit over classical search.

### 3. Strong Classical Equivalence ($p = 0.4450$ and $p = 0.5903$)
- **Tabu Search vs. QAOA:** Delta $= +5.96\text{ km}$ ($1.2\%$), with $p = 0.4450$.
- **Multistart KL vs. QAOA:** Delta $= +4.44\text{ km}$ ($0.9\%$), with $p = 0.5903$.
- Under the **Holm-Bonferroni correction** for multiple hypothesis testing across all benchmark configurations, all adjusted $p$-values exceed $p_{\text{adj}} > 0.40$.

---

## 4. GENERALIZATION VERDICT

The claim of reproducible quantum advantage is **definitively refuted**:
1. When tested on out-of-sample problem distributions, QAOA fails to achieve statistical significance even against weak single-pass heuristics ($p = 0.0708$).
2. Against modern classical metaheuristics (Tabu Search and Multistart KL), QAOA is statistically indistinguishable ($p \ge 0.445$).
3. Classical Tabu Search delivers identical solution quality in **less than half the runtime** ($24.67\text{ ms}$ vs. $62.19\text{ ms}$).

