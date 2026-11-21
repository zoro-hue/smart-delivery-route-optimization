# ROUTE/IQ — PHASE Q: WARM-START QAOA REPRODUCIBILITY REPORT
**Independent Experimental Reproduction of Quantum Circuit Execution and State Distribution Sampling**

- **Date:** 2026-11-06
- **Test File:** `phase_q_ipcqe_validation/benchmarks/verify_warm_start_mathematics.py`
- **Raw Measurements:** `phase_q_ipcqe_validation/results/phase_q_warm_start_audit_raw.csv`
- **Qiskit Version:** 2.4.1 | Qiskit Aer: 0.17.2 | Total Shots per Test: 2,048

---

## 1. Measured Sampling Distributions Across Mixer Configurations

| Circuit Configuration | Initial State $|\psi_0\rangle$ | Mixer $H_M$ | $\beta / \pi$ | Row Valid Rate (%) | Column Valid Rate (%) | Strict Valid Permutation Rate (%) | Mean Hungarian Delta (bits) |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Standard Unconstrained** | Uniform $|+\rangle^{\otimes 16}$ | Transverse $\sum X_i$ | 0.35 | 1.76% | 1.37% | **0.49%** | 2.314 |
| **Classical Seed + Transverse** | Seed $|x_{\text{seed}}\rangle$ | Transverse $\sum X_i$ | 0.35 | 0.00% | 0.05% | **0.00%** | 2.977 |
| **Warm-Start + XY (Low Beta)** | Seed $|x_{\text{seed}}\rangle$ | XY Hopping | 0.05 | 100.00% | 86.87% | **86.87%** | 0.136 |
| **Warm-Start + XY (Mid Beta)** | Seed $|x_{\text{seed}}\rangle$ | XY Hopping | 0.20 | 100.00% | 16.89% | **16.89%** | 1.036 |
| **Warm-Start + XY (Phase P Default)** | Seed $|x_{\text{seed}}\rangle$ | XY Hopping | 0.35 | 100.00% | 31.98% | **31.98%** | 0.756 |
| **Warm-Start + XY (Half-Pi Swap)** | Seed $|x_{\text{seed}}\rangle$ | XY Hopping | 0.50 | 100.00% | 100.00% | **100.00%** | 0.000 |
| **Perturbed Seed + XY** | Perturbed $|x_{\text{pert}}\rangle$ | XY Hopping | 0.35 | 100.00% | 31.15% | **31.15%** | 0.785 |

---

## 2. Key Scientific Reproducibility Conclusions

1. **Reproduction of Transverse Mixer Collapse:**
   Phase P's finding that standard transverse mixers produce $< 1\%$ valid permutations is **confirmed and independently reproduced** ($0.49\%$). Transverse mixers are completely unsuitable for position-encoded routing problems.
2. **Clarification of XY Mixer Yield:**
   The XY hopping mixer guarantees **100% row validity** by conservation of particle number. However, column collisions reduce the raw strict permutation yield to **$31.98\%$** at the standard mixing angle ($\beta = 0.35\pi$).
3. **The Half-Pi ($\beta = \pi/2$) Discrete Invariance:**
   At $\beta = 0.50\pi$, the XY operator behaves as a deterministic permutation swap between adjacent position modes, achieving **100.00% strict permutations** with zero Hungarian projection distortion.
4. **Hungarian Projection Impact:**
   The average projection delta for Warm-Start XY is only **$0.756\text{ bits}$** (less than 1 bit flip), compared to **$2.314\text{ bits}$** for the transverse mixer. Hungarian matching functions as a minor phase-error filter rather than a heavy-handed reconstruction.

