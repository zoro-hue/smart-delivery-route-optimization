# PHASE AA EQUAL EVALUATION COMPARISON
## Mode 2: Benchmarking Algorithms Under Strictly Equal Candidate Evaluations (512 Evals)
**ROUTE/IQ — Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing**  
**Department of Computer Science and Engineering, SRM University-AP**  
**Supervisor:** Dr. Vishnu Prasad Verma  

---

## 1. EXPERIMENTAL DESIGN: MODE 2 (EQUAL EVALUATIONS)

In combinatorial search, fair comparison requires holding the **search sample budget** constant. If an algorithm tests 500 solutions while another tests only 1, the former will naturally discover better solutions through pure probability sampling.

In **Mode 2**, we fix the total number of candidate bipartitions evaluated to **$E \approx 512$ candidates**:
- **Fast QAOA (512 shots):** Samples 512 projective measurement outcomes from the quantum statevector distribution, computing QUBO costs for all 512 bitstrings (Evaluations: **512**).
- **Tabu Search (Equal Evals):** Explores 1-flip neighborhood transitions with recency memory up to 512 objective evaluations (Evaluations: **513**).
- **Multistart KL (Equal Evals):** Executes 15 independent randomized restarts of Kernighan-Lin, terminating upon reaching the evaluation ceiling (Evaluations: **448**).

---

## 2. EMPIRICAL RESULTS UNDER STRICT EQUAL EVALUATIONS ($N=20$ INSTANCES)

| Algorithm | Search Mechanism | Candidate Evaluations | Complete Route (km) | Std Dev (km) | Mean Runtime (ms) | Speedup vs. QAOA | $p$-value vs. QAOA |
|---|---|---|---|---|---|---|---|
| **Fast QAOA + VND** | Statevector Sampling | **512** | **576.32** | 55.88 | 33.19 ms | Baseline (1.0x) | Baseline |
| **Tabu Search + VND** | Memory Local Search | **513** | **582.61** | 58.77 | **12.90 ms** | **2.57x Faster** | **$p = 0.1263$** |
| **Multistart KL + VND** | Multi-Restart Search | **448** | **591.12** | 65.94 | **9.99 ms** | **3.32x Faster** | **$p = 0.1084$** |

---

## 3. INFERENTIAL STATISTICAL EVALUATION

1. **Tabu Search Matches QAOA Solution Quality:**  
   The difference between Tabu Search ($582.61\text{ km}$) and Fast QAOA ($576.32\text{ km}$) yields:
   $$t = 1.597, \quad p = 0.1263 \quad (> 0.05)$$
   There is no statistically significant difference in complete fleet distance between classical Tabu Search and simulated QAOA under equal evaluation counts.
2. **Tabu Search Executes $2.57\times$ Faster:**  
   To evaluate 512 states, classical Tabu Search required only **$12.90\text{ ms}$**, compared to **$33.19\text{ ms}$** for Fast QAOA. Tabu Search explores candidate configurations $257\%$ faster because it avoids quantum statevector unitary compilation, parameter binding, and complex probability sampling.
3. **Multistart KL Executes $3.32\times$ Faster:**  
   Similarly, Multistart KL evaluated 448 configurations in **$9.99\text{ ms}$**, achieving $591.12\text{ km}$ ($p = 0.1084$ vs. QAOA).
4. **Conclusion:**  
   Under an equal evaluation budget, classical metaheuristics achieve statistical parity with simulated QAOA while requiring significantly less wall-clock execution time.

