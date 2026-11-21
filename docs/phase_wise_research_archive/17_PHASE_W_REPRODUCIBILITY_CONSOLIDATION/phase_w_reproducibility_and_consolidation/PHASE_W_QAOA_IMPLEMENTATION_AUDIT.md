# Deliverable 4: Phase W QAOA Implementation and Mathematical Rigor Audit

## 1. Mathematical Mechanics & Hamiltonian Formulation

The problem Hamiltonian $H_C$ encodes boundary customer bipartitioning between Vehicle $A$ and Vehicle $B$:
$$H_C = \sum_{i=1}^N h_i Z_i + \sum_{i < j}^N J_{ij} Z_i Z_j + C_0$$

Where:
- $h_i = \frac{1}{2} (d(i, A) - d(i, B)) - \lambda_C (C_A - C_B) q_i + \frac{\lambda_C}{2} q_i \sum_{j \ne i} q_j$
- $J_{ij} = -\frac{1}{2} W_{ij} + \frac{\lambda_C}{2} q_i q_j$
- Standard transverse mixer: $H_M = \sum_{i=1}^N X_i$
- Initial state: Uniform superposition $|+\rangle^{\otimes N} = \frac{1}{\sqrt{2^N}} \sum_{x \in \{0, 1\}^N} |x\rangle$

---

## 2. Experimental Verification Across Circuit Depths ($p=1$ vs $p=2$)

Evaluating 1,024 measurement shots on $N=12$ boundary qubits:

| QAOA Configuration | Circuit Depth ($p$) | Parameter Tuning | Raw Capacity Violations (%) | Best Found Cost ($H_C$) | Classical Sim Runtime (ms) | Post-Repair Feasibility (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **$p=1$ Fixed Parameters** | 1 | $(\gamma_0, \beta_0) = (0.35, 0.65)$ | 54.9% | -27.24 | 105.1 ms | 100.0% |
| **$p=1$ COBYLA Optimized** | 1 | Variational loop (40 evals) | 45.8% | **-29.00** | 148.1 ms | 100.0% |
| **$p=2$ COBYLA Optimized** | 2 | Variational loop (80 evals) | 44.4% | **-29.00** | 303.9 ms | 100.0% |

---

## 3. Key Mathematical and Algorithmic Discoveries

1. **Depth Doubling Inefficacy**:
   - Moving from $p=1$ to $p=2$ increased simulation runtime by **$105.2\%$** (148.1 ms $\to$ 303.9 ms), yet raw capacity violations remained stubbornly high at **$44.4\%$**, and the ground state energy was identical ($-29.00$).
2. **The Soft-Penalty Trade-Off**:
   - Because $H_M = \sum X_i$ mixes states across the entire $2^N$ Hilbert space, unconstrained transverse mixers will always sample capacity-violating states whenever vehicle capacity bounds are tight relative to total customer demand.
3. **Mandatory Post-Processing Role**:
   - Deterministic classical capacity repair is not an optional add-on; it is a structural mathematical prerequisite for deploying QAOA in capacity-constrained vehicle routing.
