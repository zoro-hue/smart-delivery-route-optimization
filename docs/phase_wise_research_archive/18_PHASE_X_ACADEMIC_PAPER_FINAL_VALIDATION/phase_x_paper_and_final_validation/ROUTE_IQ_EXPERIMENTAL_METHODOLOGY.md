# ROUTE/IQ: Experimental Methodology & Benchmarking Protocol

## 1. Datasets & Provenance

To evaluate real-world freight routing characteristics, experiments utilize:
1. **Canonical Manhattan 50-Stop Delivery Benchmark**:
   - Customer coordinates distributed within the Manhattan delivery zone ($[40.70^\circ, 40.85^\circ]\text{ N}$, $[-74.02^\circ, -73.93^\circ]\text{ W}$).
   - Fleet: 4 vehicles, each with capacity $C = 100\text{ kg}$.
   - Road network: Asymmetric travel-cost matrix reflecting directed street geography and one-way avenues.
2. **Phase V/W Controlled Ablation Instances ($N=15$, Seeds 100–114)**:
   - 12 boundary customers per subproblem; total demand $\sum q_i \in [24, 38]\text{ kg}$.
   - Vehicle capacities: $C_A = C_B = \lceil 0.55 \times \sum q_i \rceil$.
3. **Phase W Out-of-Sample Evaluation Dataset ($N=40$ Instances)**:
   - Training Set: 20 independent instances (Seeds 500–519).
   - Held-Out Test Set: 20 independent instances (Seeds 600–619).
   - Capacity slack randomly varied between $0.52 \sum q_i$ and $0.68 \sum q_i$.

---

## 2. Computational Environment

- **Operating System**: Microsoft Windows 11 / Windows Server (x86_64)
- **Python Version**: Python 3.14.2
- **Major Libraries**:
  - `qiskit` == 2.4.1 (Variational circuit assembly, Pauli operator mathematics)
  - `qiskit-aer` == 0.17.2 (Classical CPU simulation of quantum circuits)
  - `pyspark` == 4.2.0 (Apache Spark engine executed in `local[*]` single-machine parallel mode)
  - `ortools` == 9.15.6755 (Google OR-Tools routing engine)
  - `scipy` == 1.15.0 (Optimization and statistical testing)
  - `numpy` == 2.2.3 (Vectorized matrix calculations)
  - `pandas` == 3.0.0 (Data manipulation)

> [!NOTE]
> **Execution Environment Transparency**:
> All quantum circuit executions were conducted via **classical CPU statevector and shot-based simulation on Qiskit Aer**. No physical quantum hardware (QPU) was utilized. Apache Spark was executed in **`local[*]` single-machine mode**; no physical multi-node cluster was claimed or utilized.

---

## 3. Algorithmic Configurations Benchmarked

The experimental framework evaluates 10 rigorous pipelines across identical benchmark instances:

- **Config A (OR-Tools Alone)**: Industrial constraint programming and Guided Local Search.
- **Config B (OR-Tools + Algorithmic VND)**: OR-Tools seeded into real Variable Neighborhood Descent (2-opt, relocate, and swap).
- **Config C (OR-Tools + QAOA)**: OR-Tools baseline paired with raw/repaired QAOA boundary partitioning without downstream VND.
- **Config D (OR-Tools + QAOA + VND)**: Complete hybrid pipeline with QAOA boundary partitioning and downstream algorithmic VND.
- **Config E (OR-Tools + Kernighan-Lin + VND)**: Classical graph bisection competitor replacing QAOA.
- **Config F (OR-Tools + Random Feasible Part + VND)**: Random uniform binary partitioning repaired for capacity, serving as stochastic control.
- **Config G (OR-Tools + QIGA + VND)**: Quantum-Inspired Genetic Algorithm replacing QAOA.
- **Config H (OR-Tools + Exact Part + VND)**: Exhaustive enumeration ($2^N$ ground truth) replacing QAOA.
- **Config I (Spark + OR-Tools + VND)**: Big Data preprocessing pipeline paired with classical routing.
- **Config J (Spark + OR-Tools + QAOA + VND)**: Complete dual-pillar Big Data + Quantum architecture.

---

## 4. Statistical Testing Protocol

- **Independent Unit of Analysis**: The paired benchmark instance ($N = 15$ or $N = 20$). Repeated quantum measurement shots on the same instance are treated as stochastic samples of a single observation, never as independent instances.
- **Tests Evaluated**: Two-tailed paired Student's $t$-test (parametric) and Wilcoxon signed-rank test (non-parametric).
- **Significance Level**: $\alpha = 0.05$.
- **Multiple Comparisons**: Holm-Bonferroni step-down critical value adjustments.
