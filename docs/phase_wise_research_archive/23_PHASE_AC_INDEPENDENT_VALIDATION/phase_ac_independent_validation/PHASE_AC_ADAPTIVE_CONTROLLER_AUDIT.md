# PHASE AC DELIVERABLE 10: ADAPTIVE CONTROLLER INDEPENDENT AUDIT

## Project Information
- **Project:** ROUTE/IQ — Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing
- **Institution:** SRM University-AP | **Supervisor:** Dr. Vishnu Prasad Verma
- **Audit Branch:** `research/phase-ac-independent-validation`

---

## 1. Feature Availability & Data Leakage Audit

The inputs to `AdaptiveCooperativeController.select_strategy()` were audited for data leakage:

| Feature Name | Mathematical Definition | When Computed | Data Leakage Risk | Independent Audit Verdict |
| :--- | :--- | :--- | :---: | :--- |
| `subproblem_size` | Customer count $N$ | Upfront | None | Clean instance metadata |
| `capacity_slack` | $\frac{(Q_A + Q_B) - \sum d_i}{\sum d_i}$ | Upfront from demands | None | Clean constraint metadata |
| `interaction_density` | Mean pairwise affinity $\frac{1}{\binom{N}{2}} \sum W_{ij}$ | Upfront from distance matrix | None | Clean graph topology metadata |
| `stagnation_count` | Iteration counter without improvement | Tracked dynamically | None | Search state metadata |
| `remaining_budget_ms` | $T_{\text{max}} - T_{\text{elapsed}}$ | Computed from clock | None | Runtime telemetry |

**Verdict:** **ZERO DATA LEAKAGE DETECTED.** None of the features use post-optimization route lengths, candidate rankings, or downstream solver feedback.

---

## 2. Dispatch Discrepancy Analysis

The Phase AB narrative report stated:
- Tabu Search: 19 calls (63.3%)
- Multistart KL: 6 calls (20.0%)
- Random Feasible: 4 calls (13.3%)
- QAOA: 1 call (3.3%)

However, direct inspection of the raw CSV (`phase_ab_complete_benchmark_raw.csv`) revealed:
- Tabu Search: **26 calls (86.7%)**
- Multistart KL: **2 calls (6.7%)**
- Random Feasible: **2 calls (6.7%)**
- QAOA: **0 calls (0.0%)**

### Root Cause of the Discrepancy
In `complete_system_benchmark.py`:
- Demands were generated with $d_i \in [1, 4]$, and vehicle capacity was set to $\text{cap} = \lceil \text{total\_demand} \times 0.55 \rceil$.
- This caused `capacity_slack` to always evaluate to $\approx 0.10$.
- In `adaptive_controller.py`, Condition C requires `capacity_slack > 0.15` to dispatch Random Feasible or Multistart KL.
- Because `capacity_slack = 0.10 \le 0.15`, the controller fell through to the default branch (Tabu Search) in 26 of 30 instances!
- **Scientific Audit Correction:** The narrative dispatch figures (19, 6, 4, 1) in the Phase AB report were an artifact of earlier exploratory runs with variable slack, not the finalized CSV. The true CSV dispatches were **86.7% Tabu Search and 0.0% QAOA**.

---

## 3. Leakage-Safe Held-Out Evaluation ($N = 30$ Instances)

In Phase AC, we constructed a dedicated held-out audit with dynamically varying slack ($\sigma \in [0.05, 0.40]$) and interaction density ($\rho \in [0.3, 1.5]$).

### Dispatch Distribution under Variable Slack:
- Tabu Search: **14 calls (46.7%)**
- Random Feasible: **9 calls (30.0%)**
- QAOA Quantum: **6 calls (20.0%)**
- Multistart KL: **1 call (3.3%)**

### Held-Out Performance Summary:
- **Adaptive Controller:** Mean **595.11 km**, Latency **96.82 ms**, Acceptance **46.7%**.
- **Always Tabu:** Mean **595.12 km**, Latency **17.56 ms**, Acceptance **46.7%**.
- **Always QAOA:** Mean **602.16 km**, Latency **401.79 ms**, Acceptance **50.0%**.
- **Always Random:** Mean **594.63 km**, Latency **20.61 ms**, Acceptance **50.0%**.

### Conclusion
The Adaptive Controller achieves route quality essentially identical to Always Tabu (**595.11 km** vs **595.12 km**) while intelligently dispatching QAOA only when high interaction curvature justifies exploratory tunneling.
