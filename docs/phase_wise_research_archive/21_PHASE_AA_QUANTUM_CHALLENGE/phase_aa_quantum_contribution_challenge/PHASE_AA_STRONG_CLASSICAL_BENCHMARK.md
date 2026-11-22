# PHASE AA STRONG CLASSICAL BENCHMARK
## Challenging Simulated QAOA Against Modern Classical Metaheuristics
**ROUTE/IQ — Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing**  
**Department of Computer Science and Engineering, SRM University-AP**  
**Supervisor:** Dr. Vishnu Prasad Verma  

---

## 1. RESEARCH MANDATE

Phase Z compared Fast QAOA against **Single-Pass Kernighan-Lin**, an algorithm that runs in $4.2\text{ ms}$ and evaluates a single partition. In operational logistics and combinatorial optimization, single-pass heuristics do not represent the state of the art in classical search.

Phase AA subjected QAOA to a direct experimental challenge against four established, stronger classical metaheuristics:
1. **Multistart Kernighan-Lin (MS-KL):** Iterated restarts from randomized balanced partitions with local 2-exchange passes.
2. **Tabu Search (TS):** Neighborhood exploration with recency memory (tenure 5) and aspiration criteria to escape local minima.
3. **Simulated Annealing (SA):** Metropolis stochastic acceptance with geometric temperature cooling ($T_0=15.0, \alpha=0.96$).
4. **Exact Global Enumeration ($2^N$):** Exhaustive evaluation of all $65{,}536$ bipartitions to find the provable global minimum of the QUBO Hamiltonian.

---

## 2. EMPIRICAL BENCHMARK COMPARISON ($N=20$ BENCHMARK INSTANCES)

All algorithms were evaluated on identical $N=16$ boundary subproblems with identical distance matrices, vehicle capacities, and parcel demands:

| Algorithm | Algorithm Class | Fleet Distance (km) | Std Dev (km) | Runtime (ms) | Mean Evaluations | Win vs. Single-Pass KL | Win vs. Fast QAOA | $p$-value vs. Fast QAOA |
|---|---|---|---|---|---|---|---|---|
| **Single-Pass KL + VND** | Deterministic Greedy Heuristic | 593.31 | 59.95 | **4.19 ms** | 1 | 0.0% | 0.0% | **$p = 0.0179$** |
| **Multistart KL (Equal Evals)** | Multi-Start Local Search | 591.12 | 65.94 | **9.99 ms** | 448 | 40.0% | 20.0% | $p = 0.1084$ |
| **Tabu Search (Equal Evals)** | Memory-Guided Local Search | **582.61** | **58.77** | **12.90 ms** | 513 | 35.0% | 15.0% | **$p = 0.1263$** |
| **Multistart KL (Equal Time)** | Multi-Start Local Search | 588.69 | 74.39 | 34.21 ms | 2,133 | 40.0% | 20.0% | **$p = 0.2529$** |
| **Exact $2^N$ Global Optimum**| Exhaustive Branch & Bound | 582.53 | 60.09 | 880.76 ms | 65,536 | 40.0% | 0.0% | $p = 0.2188$ |
| **Fast QAOA (512 shots) + VND**| Variational Quantum Algorithm | 576.32 | 55.88 | 33.19 ms | 512 | 45.0% | Baseline | Baseline (1.0) |

---

## 3. KEY SCIENTIFIC FINDINGS

### Finding 1: The Apparent Quantum Advantage Disappears Under Strong Classical Search
When compared against **Single-Pass KL** ($4.19\text{ ms}$), Fast QAOA appeared to achieve statistical significance ($p = 0.0179$).  
However, when compared against:
- **Tabu Search (512 evaluations):** $p = 0.1263$ (NOT statistically significant).
- **Multistart KL (Equal Time):** $p = 0.2529$ (NOT statistically significant).
- **Exact Global Enumeration:** $p = 0.2188$ (NOT statistically significant).

In all three fair classical challenges, **the null hypothesis cannot be rejected**. The apparent advantage reported in Phase Z was an artifact of comparing against an under-budgeted classical baseline.

### Finding 2: Classical Tabu Search Outperforms QAOA in Computational Efficiency
- **Tabu Search:** Achieves a mean fleet distance of **$582.61\text{ km}$** in **$12.90\text{ ms}$**.
- **Fast QAOA:** Achieves **$576.32\text{ km}$** in **$33.19\text{ ms}$**.
- **Efficiency Metric:** Tabu Search delivers equivalent solution quality in **$2.57\times$ less wall-clock time** with zero quantum simulation overhead and zero specialized hardware dependencies.

