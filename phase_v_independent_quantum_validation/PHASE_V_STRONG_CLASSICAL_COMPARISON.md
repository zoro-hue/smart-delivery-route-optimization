# Deliverable 5: Phase V Strong Classical Competitor Comparison

## 1. Benchmarking Protocol & Competitors

To avoid the pitfall of comparing quantum algorithms against strawman baselines, Phase V implemented and evaluated 6 robust industrial classical solvers under equal hardware and wall-clock computational budgets:

1. **Exact Bipartition Enumeration**: Exhaustive search over all $2^{12} = 4,096$ states (Ground Truth).
2. **Balanced Kernighan-Lin (KL) Bisection**: Iterative pairwise customer exchange.
3. **Multistart Local Search (MLS)**: 20 independent randomized restarts with 1-flip and 2-swap steepest descent.
4. **Classical Simulated Annealing (SA)**: Metropolis-Hastings cooling schedule ($T_0=10.0, \alpha=0.95, T_{\text{min}}=0.01$).
5. **OR-Tools Guided Local Search (GLS)**: Industrial metaheuristic CVRP engine.
6. **Algorithmic Variable Neighborhood Descent (VND)**: Relocate, 2-opt, and swap until local minimum.

---

## 2. Head-to-Head Performance Matrix ($N=12$)

| Optimization Algorithm | Nature of Algorithm | Mean QUBO Energy | Final Route Distance (km) | Mean Runtime (ms) | Mathematical Optimality Guarantee |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Exact Enumeration** | Deterministic Ground Truth | **-38.45** | **540.07 km** | 81.83 ms | **Guaranteed (100%)** |
| **Kernighan-Lin (KL)** | Classical Heuristic | -37.82 | **540.07 km** | **5.65 ms** | Heuristic ($98.4\%$ opt) |
| **Multistart Local Search** | Classical Metaheuristic | -38.10 | **540.07 km** | 8.21 ms | Empirical ($99.1\%$ opt) |
| **Simulated Annealing** | Stochastic Classical | -37.40 | 542.15 km | 14.30 ms | Asymptotic |
| **OR-Tools CVRP Baseline** | Constraint Programming | -32.10 | 668.09 km | 8.21 ms | Initial Fleet Seed |
| **OR-Tools + Algorithmic VND** | Classical Local Search | -36.50 | 559.92 km | 12.71 ms | Local Optimum |
| **QAOA (Repaired) + VND** | Hybrid Quantum-Classical | -37.15 | 544.20 km | 133.59 ms | Variational Sampling |

---

## 3. Scientific Assessment of Classical Competitiveness

1. **Runtime Efficiency**:
   - Classical Kernighan-Lin runs in **5.65 ms**, which is **$23.6\times$ faster** than simulated QAOA (**133.59 ms**), while producing a shorter route distance (**540.07 km** vs **544.20 km**).
2. **Solution Quality**:
   - For subproblem sizes $N \le 16$, exact enumeration guarantees global optimality in under 100 ms on a standard CPU.
   - Consequently, simulated QAOA provides no computational or quality advantage over exact or heuristic classical methods at current NISQ problem scales.
