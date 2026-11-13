# Deliverable 5: Phase U QAOA Implementation Audit & Feasibility Analysis

## 1. Scope & Objective

This audit examines the implementation of the **16-qubit QAOA boundary customer bipartitioning engine** introduced in Phase T and evaluated in Phase U. The goal is to determine the exact mathematical mechanics, circuit depth, mixer behavior, parameter optimization efficiency, and physical feasibility of solutions produced by QAOA.

---

## 2. Hamiltonian Construction & Parameterization

The problem Hamiltonian $H_C$ encodes boundary customer assignment to two delivery vehicles $A$ and $B$:
$$H_C = \sum_{i=1}^N h_i Z_i + \sum_{i < j}^N J_{ij} Z_i Z_j + C_0$$

Where:
- $h_i$ represents the relative affinity bias of customer $i$ towards Vehicle $A$ versus Vehicle $B$, plus linear expansion terms from the quadratic capacity penalty.
- $J_{ij}$ represents the mutual spatial interaction and quadratic capacity cross-coupling between customers $i$ and $j$:
  $$J_{ij} = -\frac{1}{2} w_{ij} + \frac{\lambda_C}{2} q_i q_j$$
- $Z_i$ is the Pauli-$Z$ operator acting on qubit $i \in \{0, \dots, N-1\}$.

### Quantum Circuit Structure
- **Initial State**: Uniform superposition $|+\rangle^{\otimes N} = \frac{1}{\sqrt{2^N}} \sum_{x \in \{0, 1\}^N} |x\rangle$.
- **Cost Layer**: $U(C, \gamma) = e^{-i \gamma H_C} = \prod_i R_z(2 \gamma h_i) \prod_{i < j} R_{zz}(2 \gamma J_{ij})$.
- **Mixer Layer**: $U(M, \beta) = e^{-i \beta H_M} = \prod_i R_x(2 \beta)$, where $H_M = \sum_i X_i$.
- **Alternating Depth**: Evaluated at depths $p \in \{1, 2, 3\}$.
- **Classical Optimizer**: COBYLA (constrained optimization by linear approximation) with maximum iterations $M_{\text{iter}} \in [30, 80]$.

---

## 3. The 55.08% Capacity Violation Discovery

Phase T claimed a "100% feasible-state density" for boundary bipartitioning, contrasting it with micro-TSP permutation encodings which had a $99.96\%$ penalty violation rate. 

Phase U conducted an independent empirical audit of raw measurement bitstrings sampled from an 8-qubit QAOA circuit ($p=1$, 2048 shots, $\lambda_C = 2.0$):

```
+-------------------------------------------------------------------+
| Metric                                    | Value                 |
+-------------------------------------------------------------------+
| Total Shots Sampled                       | 2048                  |
| Graph Assignment Validity (Binary Domain) | 100.0% (2048/2048)    |
| Capacity-Feasible States (Q_A, Q_B <= C)  | 44.92% (920/2048)     |
| Capacity-Violating States (Q > C)         | 55.08% (1128/2048)    |
| Empty Route Partitions (All 0s or All 1s) | 1.86% (38/2048)       |
+-------------------------------------------------------------------+
```

### Critical Takeaway:
Binary validity (every bit is 0 or 1) does **not** equal physical feasibility (both vehicles must have total demand $\le$ vehicle capacity $C$). Without deterministic capacity repair or hard-constraint XY mixers, over half of raw QAOA samples violate vehicle capacity limits.

---

## 4. Necessity of the Hybrid Co-Design

This finding mathematically demonstrates why QAOA cannot operate in isolation for CVRP boundary partitioning:
1. **Classical Role**: Must execute deterministic capacity repair on raw bitstrings sampled from QAOA to restore feasibility.
2. **Proposition 1 Guardrail**: Must verify that the reconstructed routes strictly improve or match the incumbent classical baseline ($\Delta \text{Cost} \le 0$).
3. **Apache Spark Role**: Organizes spatial customer clusters, filters boundary candidates, and parallelizes multiple subproblem evaluations.
