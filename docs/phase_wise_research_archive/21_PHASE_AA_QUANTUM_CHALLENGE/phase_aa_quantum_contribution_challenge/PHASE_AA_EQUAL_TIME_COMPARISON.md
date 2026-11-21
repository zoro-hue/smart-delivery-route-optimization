# PHASE AA EQUAL TIME COMPARISON
## Mode 1: Benchmarking Algorithms Under Strictly Equal Wall-Clock Budgets (~34 ms)
**ROUTE/IQ — Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing**  
**Department of Computer Science and Engineering, SRM University-AP**  
**Supervisor:** Dr. Vishnu Prasad Verma  

---

## 1. EXPERIMENTAL DESIGN: MODE 1 (EQUAL TIME)

In algorithmic benchmarking, an unfair comparison arises when one algorithm is granted an order-of-magnitude larger execution budget than its competitors. In Phase Z, Fast QAOA was allocated **$\sim 33.2\text{ ms}$** of CPU time (variational circuit execution + statevector sampling + repair + VND), whereas the classical baseline (Single-Pass Kernighan-Lin) was terminated after only **$4.19\text{ ms}$**!

In **Mode 1**, we enforce strict computational parity:
- **Target Wall-Clock Budget:** $T \approx 33 - 35\text{ ms}$ per instance.
- **Fast QAOA:** Variational statevector evolution + 512 shots + classical repair + VND (Runtime: **$33.19\text{ ms}$**).
- **Multistart Kernighan-Lin (MS-KL Equal Time):** Continuously initiates randomized balanced restarts and 2-exchange local search passes until the $34\text{ ms}$ time budget is reached (Runtime: **$34.21\text{ ms}$**).
- **Simulated Annealing (SA Equal Time):** Metropolis cooling across multiple cooling schedules within the time window.

---

## 2. EMPIRICAL RESULTS UNDER STRICT EQUAL TIME ($N=20$ INSTANCES)

| Algorithm | Mean Wall-Clock Latency (ms) | Total Search Evaluations | Mean Complete Route (km) | Std Dev (km) | Delta vs. QAOA (km) | Paired $t$-test $p$-value | Wilcoxon $p$-value |
|---|---|---|---|---|---|---|---|
| **Fast QAOA (512 shots) + VND** | **33.19 ms** | 512 | **576.32** | 55.88 | Baseline (0.00) | Baseline | Baseline |
| **Multistart KL (Equal Time)** | **34.21 ms** | **2,133** | **588.69** | 74.39 | $+12.37$ | **$p = 0.2529$** | **$p = 0.2961$** |
| **Simulated Annealing (Equal Time)** | 7.75 ms* | 141 | 603.70 | 58.22 | $+27.38$ | $p = 0.0040$ | $p = 0.0062$ |

*\*Note:* Simulated Annealing reached its minimum temperature threshold early.

---

## 3. STATISTICAL ANALYSIS OF EQUAL-TIME COMPARISON

1. **Non-Significance of the Quantum Margin:**  
   The difference between Fast QAOA ($576.32\text{ km}$) and Multistart Kernighan-Lin ($588.69\text{ km}$) yields:
   $$t = 1.180, \quad p = 0.2529 \quad (\gg 0.05)$$
   Because $p > 0.05$, **there is no statistically significant difference** between QAOA and classical Multistart KL under equal wall-clock time budgets.
2. **Evaluation Throughput Advantage of Classical Search:**  
   In the identical $34\text{ ms}$ window:
   - Fast QAOA performed **512 candidate evaluations** (bounded by quantum statevector matrix-vector products).
   - Multistart KL performed **2,133 candidate evaluations** (a **$4.17\times$ higher exploration throughput**), made possible by fast bitwise operations on classical CPUs.
3. **Conclusion:**  
   When classical heuristics are allowed to consume the same wall-clock time that simulated QAOA requires, the claim of quantum advantage collapses.

