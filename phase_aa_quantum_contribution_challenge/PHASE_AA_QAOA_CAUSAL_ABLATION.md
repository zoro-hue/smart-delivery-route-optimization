# PHASE AA QAOA CAUSAL ABLATION
## Deconstruction of Quantum Causal Contribution vs. Random Sampling and Proposition 1 Ratchet
**ROUTE/IQ — Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing**  
**Department of Computer Science and Engineering, SRM University-AP**  
**Supervisor:** Dr. Vishnu Prasad Verma  

---

## 1. THE CENTRAL SCIENTIFIC QUESTION

Phase Z showed that Fast QAOA + VND ($573.31\text{ km}$) improved upon Single-Pass Kernighan-Lin + VND ($593.31\text{ km}$) with $p = 0.0100$.

The fundamental question of Phase AA is:  
**What actually caused this $20\text{ km}$ improvement?**
- Was it quantum mechanical state evolution and tunneling?
- Was it the fact that QAOA sampled 512 candidate partitions?
- Was it the Algorithmic VND local search engine?
- Was it the Proposition 1 Guardrail acting as an asymmetric ratchet?

To isolate the true causal drivers, we conducted a rigorous 5-way ablation experiment across the 20 benchmark instances.

---

## 2. EMPIRICAL CAUSAL ABLATION MATRIX ($N=20$ INSTANCES)

| Ablation Variant | Description | Mean Fleet Distance (km) | Std Dev (km) | Mean Runtime (ms) | Prop 1 Fallback Triggered | Win Rate vs. Single KL | $p$-value vs. Single KL |
|---|---|---|---|---|---|---|---|
| **1. Single-Pass KL + VND** | Deterministic baseline | 593.31 | 59.95 | **4.87 ms** | 0.0% | Baseline | Baseline (1.0) |
| **2. Random 512 + Prop 1 + VND** | Pure uniform random sampling | **576.40** | **55.20** | **19.43 ms** | **65.0%** | **35.0%** | **$p = 0.0286$** |
| **3. Raw QAOA (No Prop 1) + VND** | QAOA without safety filter | **582.42** | **61.74** | 34.47 ms | **0.0%** | **45.0%** | **$p = 0.2327$** |
| **4. QAOA With Prop 1 + VND** | Full hybrid pipeline (Phase Z) | **575.74** | **56.32** | 34.47 ms | **55.0%** | **45.0%** | **$p = 0.0164$** |
| **5. Exact Global QUBO + Prop 1 + VND**| True global minimum cut | 581.96 | 60.83 | 883.01 ms | 60.0% | 40.0% | **$p = 0.0401$** |

---

## 3. FOUR CRITICAL CAUSAL DISCOVERIES

### Discovery 1: Raw QAOA is NOT Statistically Significant ($p = 0.2327$)
When Fast QAOA is evaluated on its own merits **WITHOUT the Proposition 1 classical guardrail** (Variant 3):
- Mean fleet distance degrades from $575.74\text{ km}$ to **$582.42\text{ km}$**.
- The paired $t$-test against Single-Pass Kernighan-Lin yields:
  $$t = -1.233, \quad p = 0.2327 \quad (> 0.05)$$
- **Conclusion:** Standalone simulated QAOA does NOT achieve a statistically significant improvement over Kernighan-Lin. The apparent statistical significance reported in Phase Z was entirely dependent on Proposition 1 substituting classical solutions when QAOA failed.

### Discovery 2: The 55% Classical Rejection Rate
In **11 out of 20 benchmark instances (55.0%)**, Fast QAOA proposed a customer partition that produced a worse complete delivery route than the classical baseline!  
The only reason Fast QAOA achieved $575.74\text{ km}$ is that Proposition 1 rejected those 11 failures and fell back to the classical incumbent.

### Discovery 3: Pure Random Sampling Matches QAOA ($576.40\text{ km}$ vs. $575.74\text{ km}$)
Look at Variant 2:
- We replaced the entire QAOA quantum circuit with **pure uniform random sampling** of 512 balanced bitstrings, evaluated their QUBO costs, repaired capacity, applied Proposition 1, and ran VND.
- Random 512 Sampling achieved **$576.40\text{ km}$** ($p = 0.0286$ vs. Single KL).
- The difference between Pure Classical Random Sampling ($576.40\text{ km}$) and QAOA ($575.74\text{ km}$) is only **$0.66\text{ km}$**:
  $$t = 0.244, \quad p = 0.8101$$
- **Conclusion:** QAOA is statistically indistinguishable from classical random sampling protected by Proposition 1.

### Discovery 4: The Proposition 1 Asymmetric Ratchet Effect
Why does Random Sampling or QAOA beat Single-Pass KL?
$$\text{Cost}(R_{\text{final}}) = \min\left( \text{Cost}(R_{\text{classical}}), \text{Cost}(R_{\text{sample}}) \right)$$
Because $\text{Cost}(R_{\text{final}}) \le \text{Cost}(R_{\text{classical}})$ unconditionally, sampling $K$ diverse partitions acts as a stochastic lottery ticket. Even if $90\%$ of samples are garbage, if just $1$ sample stumbles into a favorable customer swap, Proposition 1 ratchets the score downwards.

### Summary
The reported "quantum advantage" in Phase Z was an illusion produced by:
1. Multi-candidate stochastic sampling ($K=512$ vs. $K=1$).
2. The Proposition 1 asymmetric ratchet absorbing 55% of quantum failures.
3. Algorithmic VND polishing the resulting TSP tours.
The quantum circuit itself contributed virtually zero unique optimization advantage beyond random diversity generation.

