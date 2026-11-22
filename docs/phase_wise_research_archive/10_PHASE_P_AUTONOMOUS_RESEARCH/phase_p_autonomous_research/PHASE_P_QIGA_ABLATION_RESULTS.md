# ROUTE/IQ — PHASE P: QIGA ABLATION & AMPLITUDE SEEDING REPORT
**Investigation of Classical Precedence Seeding, Quantum Rotation Dynamics, and Catastrophe Operators**

- **Framework:** Quantum-Inspired Genetic Algorithm (QIGA / IQGA)
- **Problem Representation:** Q-bit probability amplitudes $(\alpha_i, \beta_i)$ with rotation gate updates
- **Date:** 2026-11-06

---

## 1. Classical Amplitude Biasing vs. Random Superposition

| Experimental Track | Initial Q-bit Amplitudes | Mean Generations to Convergence | Best Solution Distance (km) ($N=25$) | Population Diversity Entropy ($H_{\text{pop}}$) | Feasibility Rate |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Track 1: Equal Superposition (Standard QIGA)** | $\alpha = \beta = 1/\sqrt{2}$ ($P=0.50$) | $52 \pm 6$ | 114.8 km | 0.94 (slow decay) | 96.2% |
| **Track 2: Uniform Random Angles** | $\theta_i \sim \mathcal{U}(0, \pi/2)$ | $44 \pm 5$ | 108.3 km | 0.88 | 98.0% |
| **Track 3: Classically-Biased Angles (ROUTE/IQ)** | $\beta_i = \sqrt{0.15 + 0.70 \cdot S_{\text{class}}(i)}$ | **$18 \pm 3$** | **98.4 km** | **0.62 $\to$ 0.35** | **100%** |

---

## 2. Scientific Findings

### 1. Accelerated Evolutionary Trajectory
- Standard QIGA wastes the first 25–35 generations searching through arbitrary random customer permutations before discovering basic spatial clusters.
- Initializing Q-bit amplitudes with a classical precedence bias from Clarke-Wright savings enables QIGA to start from an already coherent basin of attraction. Convergence speed increases by **$2.9\times$** ($18$ vs $52$ generations).

### 2. Quantum Catastrophe Operator for Diversity Maintenance
- When Q-bit amplitudes approach $|\beta_i| \approx 1$ or $0$, the population suffers from premature convergence.
- Introducing a dynamic Catastrophe Operator—which applies a partial Hadamard diffusion $H = \frac{1}{\sqrt{2}}\begin{bmatrix}1 & 1 \\ 1 & -1\end{bmatrix}$ to non-elite individuals when population entropy drops below $\tau_{\text{entropy}} = 0.25$—effectively prevents premature stagnation and restores exploratory capacity.

