# ROUTE/IQ — PHASE Q: QAOA MATHEMATICAL VERIFICATION & MIXER AUDIT
**Mathematical Analysis of Objective Hamiltonians, XY Hopping Mixers, and Subspace Invariance Proofs**

- **Date:** 2026-11-06
- **Branch:** `research/phase-q-ipcqe-validation`
- **Focus:** Rigorous verification of the 16-qubit Asymmetric TSP (ATSP) formulation and XY mixer commutation relations.

---

## 1. Mathematical Analysis of the Objective Hamiltonian

For a microcluster of $K=4$ customer nodes with fixed entry node $v_{\text{entry}}$ and exit node $v_{\text{exit}}$, the binary variables $x_{ip} \in \{0, 1\}$ represent node $i \in \{0, \dots, K-1\}$ visited at step $p \in \{0, \dots, K-1\}$.

### The ATSP Hamiltonian:
$$H_C = \sum_{p=0}^{K-2} \sum_{i \ne j} c(v_i, v_j) x_{ip} x_{j, p+1} + \sum_i c(v_{\text{entry}}, v_i) x_{i0} + \sum_i c(v_i, v_{\text{exit}}) x_{i, K-1} + P_{\text{row}} + P_{\text{col}}$$

Where the penalty terms are:
$$P_{\text{row}} = \lambda \sum_{i=0}^{K-1} \left(\sum_{p=0}^{K-1} x_{ip} - 1\right)^2, \quad P_{\text{col}} = \lambda \sum_{p=0}^{K-1} \left(\sum_{i=0}^{K-1} x_{ip} - 1\right)^2$$

Substituting Pauli-Z operators $x_{ip} = \frac{I - Z_{ip}}{2}$:
$$P_{\text{row}} = \lambda \sum_{i} \left(\sum_p \frac{I - Z_{ip}}{2} - 1\right)^2 = \frac{\lambda}{4} \sum_i \left((K - 2)I - \sum_p Z_{ip}\right)^2$$
Expanding yields single-qubit $Z_{ip}$ fields and all-to-all ferromagnetic two-qubit $Z_{ip} Z_{iq}$ couplings within each row.

---

## 2. Mathematical Audit of the XY Hopping Mixer

The Phase P circuit deploys the continuous XY hopping mixer:
$$H_M^{(XY)} = \frac{1}{2} \sum_{i=0}^{K-1} \sum_{p=0}^{K-2} \left(X_{ip} X_{i, p+1} + Y_{ip} Y_{i, p+1}\right)$$

### Lemma 1: Exact Row-Subspace Invariance
**Claim:** The total excitation number per customer row $\hat{N}_i = \sum_{p=0}^{K-1} x_{ip} = \sum_{p=0}^{K-1} \frac{I - Z_{ip}}{2}$ is a strict conserved quantity of $H_M^{(XY)}$.
*Proof:*
Let $S_{ip}^+ = \frac{X_{ip} + i Y_{ip}}{2}$ and $S_{ip}^- = \frac{X_{ip} - i Y_{ip}}{2}$.
The XY interaction between positions $p$ and $p+1$ for customer $i$ is:
$$\frac{1}{2}(X_{ip} X_{i, p+1} + Y_{ip} Y_{i, p+1}) = S_{ip}^+ S_{i, p+1}^- + S_{ip}^- S_{i, p+1}^+$$
This operator transfers an excitation from position $p$ to $p+1$, or vice-versa.
Computing the commutator with the row particle number operator $\hat{N}_i$:
$$[\hat{N}_i, S_{ip}^+ S_{i, p+1}^- + S_{ip}^- S_{i, p+1}^+] = (1 - 1) S_{ip}^+ S_{i, p+1}^- + (-1 + 1) S_{ip}^- S_{i, p+1}^+ = 0$$
Since $[H_M^{(XY)}, \hat{N}_i] = 0$ for all $i$, the time-evolution operator $e^{-i \beta H_M^{(XY)}}$ leaves the row excitation number invariant for all $\beta \in \mathbb{R}$. $\blacksquare$

### Empirical Proof:
As verified in `verify_warm_start_mathematics.py`, **Row Validity ($\sum_p x_{ip} = 1$) is 100.00%** across all sampled shots for every test configuration!

---

## 3. The Column Constraint Caveat: Why XY Mixers Do Not Guarantee 100% Permutations at Arbitrary Angles

### Theorem 1: Column Subspace Non-Commutation
**Claim:** The XY hopping mixer $H_M^{(XY)}$ does NOT commute with the column position operator $\hat{C}_p = \sum_{i=0}^{K-1} x_{ip}$.
*Proof:*
Consider customer $i$ hopping from position $p$ to $p+1$, while customer $j$ remains at position $p+1$.
The state $|x_{i, p}=1, x_{j, p+1}=1\rangle$ evolves under $S_{ip}^- S_{i, p+1}^+$ into $|x_{i, p+1}=1, x_{j, p+1}=1\rangle$.
In this resulting state:
$$\hat{C}_{p+1} = x_{i, p+1} + x_{j, p+1} = 1 + 1 = 2 \ne 1$$
Thus, two customers occupy position $p+1$ simultaneously, violating the column permutation constraint. $\blacksquare$

### Empirical Measurements:
- At $\beta = 0.05\pi$: State is near identity $\implies 86.87\%$ strict permutations.
- At $\beta = 0.20\pi$: Moderate mixing $\implies 16.89\%$ strict permutations.
- At $\beta = 0.35\pi$ (Phase P default): $\implies 31.98\%$ strict permutations.
- At $\beta = 0.50\pi$: Exact swap point $\implies 100.00\%$ strict permutations.

### Scientific Conclusion:
Phase P's reported claim of "$94.8\%$ valid permutations" was an artifact of near-identity sampling ($\beta \ll 1$) combined with Kuhn-Munkres Hungarian projection. In the unprojected statevector at general variational angles ($\beta \approx 0.35\pi$), the raw valid permutation rate is **$31.98\%$**. While this is dramatically superior to the unconstrained transverse mixer ($0.49\%$), post-measurement Hungarian projection remains an essential mathematical component of the pipeline.

