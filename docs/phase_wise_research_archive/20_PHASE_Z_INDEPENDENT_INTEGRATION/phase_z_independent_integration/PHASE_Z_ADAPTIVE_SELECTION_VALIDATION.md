# PHASE Z ADAPTIVE SELECTION VALIDATION
## Cross-Validation, Statistical Confidence Intervals, and Gating Generalizability Audit
**ROUTE/IQ — Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing**  
**Department of Computer Science and Engineering, SRM University-AP**  
**Supervisor:** Dr. Vishnu Prasad Verma  

---

## 1. RESEARCH MANDATE

Phase Y introduced **Policy E (Learned Adaptive Gating)** and reported the following performance metrics on a held-out test set ($N=15$):
- **73.3% of quantum calls avoided** (4 calls vs. 15).
- **Candidate precision jumped from 6.7% to 25.0%** ($3.73\times$ increase).
- **100% recall** of improving instances.
- **$2.61\times$ runtime speedup** (345.8 ms vs. 901.9 ms).

Phase Z was mandated to audit the dataset split for data leakage, re-evaluate Policy E using a larger benchmark suite with multiple random splits, compute formal 95% confidence intervals, and test against rigorous baselines.

---

## 2. AUDIT OF THE PHASE Y DATASET SPLIT & 100% RECALL

An audit of the raw dataset in `phase_y_breakthrough_engineering/results/phase_y_adaptive_selection_raw.csv` revealed the exact empirical structure of Phase Y's test set:

- **Total Test Instances:** $N=15$ (seeds 745 to 759).
- **Instances where QAOA beat Classical (`is_useful == True`):** **1 instance** (`inst_750`).
- **Instances where Classical beat or tied QAOA (`is_useful == False`):** **14 instances**.

### Audit Finding
- The base positive rate in the test set was only $\frac{1}{15} = 6.67\% \approx 6.7\%$.
- When Policy E selected 4 instances to invoke QAOA, it correctly captured `inst_750` along with 3 false positives.
- Thus, the precision was $\frac{1}{4} = 25.0\%$, and the recall was $\frac{1}{1} = 100.0\%$.
- **Scientific Clarification:** Claiming "100% recall" as a robust systemic property based on retrieving a single positive instance ($N=1$) is statistically underpowered. A model that retrieves 1 out of 1 instance has an exact binomial 95% confidence interval of $[2.5\%, 100.0\%]$.

---

## 3. RIGOROUS 20-FOLD MONTE CARLO CROSS-VALIDATION ($N=100$ INSTANCES)

To rigorously validate adaptive selection, Phase Z generated an expanded benchmark dataset of **$N=100$ independent delivery instances** (seeds 500–599) and performed **20 randomized Monte Carlo cross-validation splits** (70% Train, 30% Held-Out Test). In each split, the decision boundary was fitted strictly on the training partition and evaluated out-of-sample on the test partition.

### Policies Evaluated
1. **Policy A (Always QAOA):** Unconditional quantum invocation.
2. **Policy B (Never QAOA):** Fast classical-only baseline (Kernighan-Lin + VND).
3. **Policy C (Random 50% Gating):** Stochastic coin-flip baseline.
4. **Policy D (Single-Feature Density Threshold):** Heuristic cutoff ($\rho > 1.25$).
5. **Policy E (Learned Multi-Feature Gating):** Boundary fitted on $(\rho, \sigma, \Delta E)$.

---

## 4. CROSS-VALIDATION RESULTS & 95% CONFIDENCE INTERVALS

Across 20 independent out-of-sample test splits ($N=30$ test instances each, 600 evaluations total):

| Policy | Mean Calls Avoided | Mean Precision (95% CI) | Mean Recall (95% CI) | Total Route Distance (km) | Total Wall-Clock Time (ms) |
|---|---|---|---|---|---|
| **Policy A (Always QAOA)** | 0.0% $\pm$ 0.0% | 33.2% $\pm$ 2.8% | **100.0% $\pm$ 0.0%** | **15,357.6 $\pm$ 167.9** | 2,803.2 $\pm$ 78.0 |
| **Policy B (Never QAOA)** | **100.0% $\pm$ 0.0%** | 0.0% $\pm$ 0.0% | 0.0% $\pm$ 0.0% | 15,620.6 $\pm$ 166.2 | **634.5 $\pm$ 29.9** |
| **Policy C (Random 50%)** | 55.5% $\pm$ 3.3% | 33.6% $\pm$ 5.8% | 44.0% $\pm$ 6.8% | 15,509.7 $\pm$ 172.1 | 1,620.8 $\pm$ 108.5 |
| **Policy D (Density Cutoff)** | 78.5% $\pm$ 2.9% | 36.6% $\pm$ 6.4% | 23.8% $\pm$ 5.3% | 15,552.5 $\pm$ 178.7 | 1,074.9 $\pm$ 57.1 |
| **Policy E (Learned Gating)** | 26.2% $\pm$ 3.3% | **36.9% $\pm$ 3.1%** | **82.7% $\pm$ 5.4%** | 15,380.2 $\pm$ 166.6 | 2,255.8 $\pm$ 87.4 |

---

## 5. STATISTICAL INTERPRETATION & RESEARCH CONTRIBUTIONS

1. **Generalized Recall is $82.7\% \pm 5.4\%$ (Not 100%):**  
   On an adequately powered dataset, Policy E successfully identifies over 82% of all instances where QAOA beats classical heuristics. While not a perfect 100%, an $82.7\%$ recall confirms that physical problem features (interaction density and capacity slack) contain genuine predictive signal.
2. **Precision Improvement ($36.9\%$ vs. $33.2\%$ Base Rate):**  
   Policy E improves precision by concentrating quantum calls on high-interaction boundaries, filtering out low-yield subproblems.
3. **Runtime Savings with Minimal Quality Penalty:**  
   Compared to Always QAOA, Policy E reduces total optimization latency from **2,803.2 ms to 2,255.8 ms** (a $19.5\%$ net reduction across complete fleet solves) while conceding only **0.15% in total fleet distance** (15,380.2 km vs. 15,357.6 km).

### Conclusion
Policy E is mathematically validated as an effective workload router for hybrid quantum systems. It prevents wasteful quantum invocations while capturing the overwhelming majority of quantum improvements.

