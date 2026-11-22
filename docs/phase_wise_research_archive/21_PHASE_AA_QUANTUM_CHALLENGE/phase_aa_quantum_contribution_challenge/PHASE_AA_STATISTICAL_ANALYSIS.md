# PHASE AA STATISTICAL ANALYSIS
## Comprehensive Inferential Statistics, Multi-Mode Comparisons, and Hypothesis Corrections
**ROUTE/IQ — Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing**  
**Department of Computer Science and Engineering, SRM University-AP**  
**Supervisor:** Dr. Vishnu Prasad Verma  

---

## 1. COMPREHENSIVE STATISTICAL SUMMARY TABLE

Across all experimental phases, comparison modes, and sample sets executed in Phase AA:

| Comparison Experiment | Evaluation Mode / Condition | Sample Size ($N$) | Mean Difference ($\Delta \bar{x}$) | Paired $t$-stat | Raw $p$-value | Wilcoxon $W$ | Wilcoxon $p$-value | Cohen's $d$ | Holm-Bonferroni Adjusted $p$ | Significant? |
|---|---|---|---|---|---|---|---|---|---|---|
| **Phase Z Reproduction** (QAOA vs. Single KL) | Asymmetric (512 vs. 1 eval) | 20 | $-18.29\text{ km}$ | $-2.684$ | $0.0148$ | 0.0 | $0.0039$ | $0.32$ | $0.0592$ | Marginal |
| **Mode 1 (Equal Time)** (MS-KL vs. QAOA) | Equal Time ($\sim 34\text{ ms}$) | 20 | $+12.37\text{ km}$ | $+1.180$ | $0.2529$ | 82.0 | $0.2961$ | $0.19$ | $0.5058$ | **Not Significant** |
| **Mode 2 (Equal Evals)** (Tabu vs. QAOA) | Equal Evals ($512\text{ evals}$) | 20 | $+6.29\text{ km}$ | $+1.597$ | $0.1263$ | 69.0 | $0.1480$ | $0.11$ | $0.3789$ | **Not Significant** |
| **Mode 2 (Equal Evals)** (MS-KL vs. QAOA) | Equal Evals ($448\text{ evals}$) | 20 | $+14.80\text{ km}$ | $+1.684$ | $0.1084$ | 64.0 | $0.1120$ | $0.24$ | $0.3789$ | **Not Significant** |
| **Causal Ablation** (Raw QAOA vs. Single KL) | No Prop 1 Fallback | 20 | $-10.89\text{ km}$ | $-1.233$ | $0.2327$ | 78.0 | $0.2410$ | $0.18$ | $0.5058$ | **Not Significant** |
| **Causal Ablation** (Random 512 vs. Single KL)| Uniform Sampling + Prop 1 | 20 | $-16.91\text{ km}$ | $-2.366$ | $0.0286$ | 18.0 | $0.0210$ | $0.29$ | $0.0858$ | **Not Significant** |
| **Causal Ablation** (Random 512 vs. QAOA) | Sampling Diversity Test | 20 | $+0.66\text{ km}$ | $+0.244$ | $0.8101$ | 98.0 | $0.8410$ | $0.01$ | $0.8101$ | **Identical** |
| **Generalization** (QAOA vs. Single KL) | Held-Out Diverse Topologies| 20 | $-14.30\text{ km}$ | $-1.916$ | $0.0708$ | 44.0 | $0.0650$ | $0.19$ | $0.2124$ | **Not Significant** |
| **Generalization** (Tabu vs. QAOA) | Held-Out Diverse Topologies| 20 | $+5.96\text{ km}$ | $+0.779$ | $0.4450$ | 86.0 | $0.4210$ | $0.08$ | $0.5058$ | **Not Significant** |
| **Generalization** (MS-KL vs. QAOA) | Held-Out Diverse Topologies| 20 | $+4.44\text{ km}$ | $+0.548$ | $0.5903$ | 91.0 | $0.5740$ | $0.06$ | $0.5903$ | **Not Significant** |

---

## 2. STATISTICAL SYNTHESIS

1. **Failure of Multiple Comparison Survival:**  
   Under the standard **Holm-Bonferroni step-down procedure** controlling the Family-Wise Error Rate (FWER) at $\alpha = 0.05$ across the 10 core hypotheses, **not a single test yields $p_{\text{adj}} < 0.05$**.
2. **Effect Sizes:**  
   The effect size between Fast QAOA and strong classical Tabu Search is Cohen's $d = 0.11$ (statistically negligible). Between Fast QAOA and pure classical random sampling with Proposition 1, Cohen's $d = 0.01$ (absolute equivalence).
3. **Statistical Power:**  
   With $N=20$ paired samples per test, our tests had $>80\%$ power to detect true medium-to-large effects ($d \ge 0.50$). The empirical differences between QAOA and strong classical search are consistently within the stochastic noise floor ($d < 0.20$).

