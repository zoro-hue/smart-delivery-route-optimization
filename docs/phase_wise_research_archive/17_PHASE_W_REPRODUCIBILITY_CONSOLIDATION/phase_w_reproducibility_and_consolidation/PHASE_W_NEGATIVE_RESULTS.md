# Deliverable 8: Phase W Consolidated Negative Results and Scientific Boundaries

## 1. Scientific Integrity Policy

Scientific progress in quantum optimization requires the unvarnished documentation of negative results, invalid hypotheses, and computational boundaries. The following findings were empirically confirmed and consolidated in Phase W:

---

## 2. Exhaustive Negative Findings

### Negative Finding 1: Lack of General Quantum Superiority
- **Hypothesis**: QAOA boundary partitioning provides a general, statistically significant route improvement over strong classical methods.
- **Empirical Reality**: REFUTED. In 73.33% of instances in the ablation benchmark and 90.0% of instances in the held-out test set, QAOA produced no improvement. Comparing OR-Tools + VND directly against OR-Tools + QAOA + VND yields $t = 1.8266, p = 0.0892$, failing to achieve statistical significance at $\alpha = 0.05$.

### Negative Finding 2: Inefficacy of Deeper QAOA Circuits ($p=2$) for Constraint Satisfaction
- **Hypothesis**: Increasing circuit depth from $p=1$ to $p=2$ will enable the quantum state to avoid vehicle capacity violations.
- **Empirical Reality**: REFUTED. $p=2$ increased simulation runtime from 148.1 ms to 303.9 ms (+105.2%), yet raw capacity violations remained at 44.4%, and the minimum found cost was identical (-29.00).

### Negative Finding 3: Inability to Predict Quantum Utility Pre-Execution
- **Hypothesis**: Coarse boundary features (capacity slack, spatial density, demand imbalance) can accurately predict when to invoke QAOA.
- **Empirical Reality**: REFUTED. Feature-conditioned gating on held-out test data avoided 85% of quantum calls, but yielded 0% precision and missed all useful quantum candidates ($r \approx 0$). Useful quantum calls arise from intricate non-convex graph cuts that cannot be detected by coarse scalar metrics.

### Negative Finding 4: Single-Machine Spark Overhead
- **Hypothesis**: Apache Spark accelerates preprocessing on workstation-scale delivery datasets.
- **Empirical Reality**: REFUTED. On single-machine workloads ($N \le 50,000$), PySpark in `local[*]` mode incurs 10x–50x JVM serialization overhead compared to vector C/NumPy execution.

### Negative Finding 5: Conflation of Guardrails with Quantum Power
- **Hypothesis**: The fact that hybrid complete routes never degrade below classical baselines proves quantum effectiveness.
- **Empirical Reality**: REFUTED. Monotonic non-degradation is solely an algorithmic feature of the Proposition 1 classical acceptance rule, which actively discards 73%–90% of quantum proposals.
