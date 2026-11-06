# Deliverable 11: Phase V Failed Experiments and Scientific Corrections

## 1. Scientific Integrity Policy

Scientific progress requires the transparent publication of failed hypotheses, rejected models, and corrected prior claims. Phase V thoroughly investigated several proposed quantum enhancements and found them invalid or ineffective:

---

## 2. Documented Negative Findings

### Negative Finding 1: The Myth of General Quantum Superiority in Configuration G
- **Prior Claim (Phase U)**: Configuration G achieved $p = 0.0017$ over OR-Tools, proving general quantum advantage.
- **Audited Truth**: In 80.0% of evaluated instances, QAOA produced zero improvement and was rejected by the Proposition 1 Guardrail. The overall distance reduction was driven overwhelmingly (87.3%) by classical VND local search, while the reported $p = 0.0017$ was an artifact of an aggressive non-parametric test and a synthetic 0.1% multiplier difference. The true paired $t$-test against classical VND is $p = 0.0892$ (not statistically significant).

### Negative Finding 2: Inefficacy of XY Mixers for Weighted Demands
- **Hypothesis**: Replacing standard transverse mixers ($H_M = \sum X_i$) with continuous XY mixers ($H_{XY} = \frac{1}{2} \sum (X_i X_j + Y_i Y_j)$) will guarantee capacity feasibility by preserving the subspace of equal customer counts.
- **Experimental Result**: FAILED. In real CVRP problems, customer demands are heterogeneous ($q_i \in \{1, 2, 3, 4, \dots\}$). Preserving the binary Hamming weight (e.g., exactly 6 customers in Vehicle A and 6 in Vehicle B) **does not preserve total capacity balance** ($\sum q_i x_i$). In testing, 42.1% of bitstrings produced by XY mixers still violated vehicle weight limits.

### Negative Finding 3: Deep QAOA Circuits ($p=3$) to Suppress Violations
- **Hypothesis**: Increasing circuit depth from $p=1$ to $p=3$ will allow the variational state to locate the capacity-feasible ground state without classical repair.
- **Experimental Result**: FAILED. Tripling the circuit depth increased simulation wall-clock time from 120 ms to 420 ms and exacerbated barren plateaus during classical optimization, yet raw capacity feasibility only increased from 44.9% to 51.8%. Classical repair remained completely necessary.

### Negative Finding 4: Replacing Classical Partitioning with QIGA
- **Hypothesis**: Using QIGA with quantum rotation gates as a drop-in replacement for classical Kernighan-Lin graph bisection.
- **Experimental Result**: FAILED. QIGA took 125 ms and produced mean fleet distances of 558.80 km, failing to beat classical Kernighan-Lin (540.07 km in 5.65 ms).
