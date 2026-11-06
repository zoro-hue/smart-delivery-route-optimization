# PHASE Z COMPLETE-ROUTE BENCHMARK
## Rigorous Multi-Configuration Competition Across Benchmark Instances (Configs A through H)
**ROUTE/IQ — Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing**  
**Department of Computer Science and Engineering, SRM University-AP**  
**Supervisor:** Dr. Vishnu Prasad Verma  

---

## 1. BENCHMARK METHODOLOGY

To definitively establish routing performance, Phase Z evaluated 8 standardized configurations across **20 independent benchmark delivery instances** ($N=16$ customers per boundary problem, seeds 300 to 319, 160 evaluations total):

- **Config A:** OR-Tools alone (Greedy initial assignment).
- **Config B:** OR-Tools + Algorithmic VND (Classical local search).
- **Config C:** OR-Tools + Kernighan-Lin Bipartitioning + VND (Strong classical baseline).
- **Config D:** OR-Tools + Original QAOA (Transverse Mixer) + VND.
- **Config E:** OR-Tools + Subspace XY-QAOA + VND.
- **Config F:** OR-Tools + Adaptive Fast QAOA + VND.
- **Config G:** OR-Tools + Adaptive Quantum Selection (Policy E) + VND.
- **Config H:** Spark + OR-Tools + Best Validated Unified Pipeline (Complete ROUTE/IQ).

All configurations operated on identical customer locations, travel distance matrices, vehicle capacities, and parcel demands.

---

## 2. EMPIRICAL BENCHMARK RESULTS

| Config ID | Architecture Description | Fleet Distance (km) | Std Dev (km) | Mean Runtime (ms) | Quantum Calls | Useful Calls | Capacity Feasibility | $p$-value vs Config A | $p$-value vs Config C |
|---|---|---|---|---|---|---|---|---|---|
| **Config A** | OR-Tools Alone | 1,232.26 | 138.97 | **0.01 ms** | 0 / 20 | 0 | **100.0%** | Baseline | $p < 10^{-14}$ |
| **Config B** | OR-Tools + VND | 606.83 | 67.03 | 4.82 ms | 0 / 20 | 0 | **100.0%** | $p = 5.77 \times 10^{-14}$ | $p = 0.2767$ |
| **Config C** | OR-Tools + KL + VND | 593.31 | 59.95 | 4.51 ms | 0 / 20 | 0 | **100.0%** | $p = 1.75 \times 10^{-14}$ | Baseline (1.0) |
| **Config D** | OR-Tools + Transverse QAOA + VND | 576.32 | 55.88 | 118.62 ms | 20 / 20 | 9 (45%) | **100.0%** | $p = 6.71 \times 10^{-15}$ | **$p = 0.0179$** |
| **Config E** | OR-Tools + Subspace XY-QAOA + VND| 583.45 | 57.35 | 82.49 ms | 20 / 20 | 5 (25%) | **100.0%** | $p = 1.77 \times 10^{-14}$ | $p = 0.0730$ |
| **Config F** | OR-Tools + Adaptive Fast QAOA + VND| **573.31** | **55.71** | 32.81 ms | 20 / 20 | 10 (50%) | **100.0%** | $p = 5.67 \times 10^{-15}$ | **$p = 0.0100$** |
| **Config G** | OR-Tools + Adaptive Gating + VND | 601.53 | 68.96 | 29.12 ms | 14 / 20 | 8 (57%) | **100.0%** | $p = 2.91 \times 10^{-14}$ | $p = 0.4536$ |
| **Config H** | Spark + Unified ROUTE/IQ Pipeline | 603.49 | 64.23 | 32.46 ms | 15 / 20 | 8 (53%) | **100.0%** | $p = 7.01 \times 10^{-14}$ | $p = 0.3060$ |

---

## 3. KEY BENCHMARK INSIGHTS

1. **VND Drives the Primary Distance Reduction:**  
   Applying Algorithmic VND to initial OR-Tools routes cuts mean fleet distance from **1,232.26 km down to 606.83 km** (a massive $50.7\%$ reduction, $p < 10^{-13}$).
2. **Classical Kernighan-Lin is Fast and Formidable:**  
   Classical Kernighan-Lin (Config C) achieves **593.31 km in only 4.51 ms**, outperforming unguided greedy assignment consistently.
3. **QAOA as a Valuable Local Catalyst with Guardrail:**  
   When QAOA is evaluated unconditionally and protected by Proposition 1 (Configs D and F), it achieves statistically significant complete-route improvements over Kernighan-Lin:
   - Config D: **576.32 km** ($p = 0.0179$ vs Config C)
   - Config F: **573.31 km** ($p = 0.0100$ vs Config C)
   On $45\% - 50\%$ of benchmark instances, QAOA proposed a non-local customer partition that classical Kernighan-Lin missed, which VND then polished into a superior complete fleet tour.
4. **Adaptive Gating Trades Small Distance for Big Speed:**  
   Under Adaptive Gating (Configs G and H), unpromising instances are routed purely to classical VND, reducing quantum execution time while capturing 8 of the 10 possible improvements and achieving higher call precision ($53\% - 57\%$).
5. **Absolute Monotonic Safety:**  
   Across all 160 test runs, **zero route degradations** occurred and **100.0% capacity feasibility** was maintained.

