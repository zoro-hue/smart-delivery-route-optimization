# Deliverable 6: Phase W Complete Fleet Route Benchmark

## 1. Complete Fleet Route Evaluation Protocol

Subproblem cut values and Ising ground-state energies are intermediate surrogates. The ultimate metric of commercial success in ROUTE/IQ is **total completed fleet delivery distance (km)** along the directed road network, under strict capacity and customer visit constraints.

---

## 2. Complete-Route Benchmark Matrix (Evaluated Across 15 Instances)

| Optimization Pipeline | Complete Route Distance (km) | Pipeline Runtime (ms) | Complete Feasibility (%) | Guardrail Action |
| :--- | :---: | :---: | :---: | :---: |
| **OR-Tools Alone (Config A)** | 668.09 km | 11.55 ms | 100.0% | Baseline Seed |
| **OR-Tools + Algorithmic VND (Config B)** | 559.92 km | 12.98 ms | 100.0% | Classical Improvement |
| **OR-Tools + Kernighan-Lin + VND (Config E)** | **540.07 km** | **6.50 ms** | **100.0%** | **Strongest Classical Baseline** |
| **OR-Tools + QAOA + VND (Config D)** | 544.20 km | 128.28 ms | 100.0% | Accepted (in 4/15 instances) |
| **Spark + OR-Tools + VND (Config I)** | 559.92 km | 23.48 ms | 100.0% | Classical + Spark |
| **Spark + OR-Tools + QAOA + VND (Config J)** | 544.20 km | 143.28 ms | 100.0% | Full Hybrid Architecture |

---

## 3. Comparison with Canonical ROUTE/IQ Dashboard Ground Truth

On the production Manhattan 50-stop benchmark:

| Algorithm Displayed on Live Scorecard | Distance (km) | Architectural Role | Complete Feasibility |
| :--- | :---: | :--- | :---: |
| **Clarke-Wright Savings** | **217.3 km** | Global initial baseline heuristic | **100.0%** |
| **2-opt Improvement** | **217.6 km** | Intra-route local tour refinement | **100.0%** |
| **OR-Tools (CVRP Engine)** | **218.2 km** | Constraint-guided initial fleet routing | **100.0%** |
| **QAOA Hybrid (Dual-Pillar Spark + Qiskit)** | **219.7 km** | Cooperative hybrid quantum-classical pipeline | **100.0%** |
| **Dijkstra Shortest-Path** | **254.8 km** | Point-to-point network distance baseline | **100.0%** |
| **A\* Heuristic Search** | **256.0 km** | Directed heuristic graph search | **100.0%** |
| **Quantum-Inspired GA (QIGA/IQGA)** | **319.4 km** | Exploration heuristic baseline | **100.0%** |

---

## 4. Rigorous Guardrail Disclaimer

> [!IMPORTANT]
> **Scientific Integrity Disclosure on Proposition 1**:
> The fact that `Config D` (QAOA + VND) never produces a route worse than `Config B` (OR-Tools + VND) is **strictly an architectural property of the Proposition 1 acceptance rule** ($\text{Cost}(R_{\text{final}}) \le \text{Cost}(R_{\text{incumbent}})$). It is **NOT** evidence of quantum optimization superiority. In 73.33% of instances, QAOA proposed a non-improving or capacity-violating candidate that the classical guardrail actively suppressed.
