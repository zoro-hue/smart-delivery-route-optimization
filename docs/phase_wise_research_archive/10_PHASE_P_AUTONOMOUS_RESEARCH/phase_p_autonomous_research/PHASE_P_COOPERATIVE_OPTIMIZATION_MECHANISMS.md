# ROUTE/IQ — PHASE P: COOPERATIVE OPTIMIZATION MECHANISMS
**Detailed Specification of Classical-to-Quantum Warm-Starts, Projection, and Feedback Loops**

---

## 1. Classical-to-QAOA Warm-Start Mechanism

Standard QAOA initializes all qubits in an uninformative uniform superposition $|+\rangle^{\otimes N_q} = \frac{1}{\sqrt{2^{N_q}}} \sum_{z \in \{0, 1\}^{N_q}} |z\rangle$. For constrained combinatorial problems like TSP, over $99.96\%$ of this state space consists of invalid bitstrings (non-permutations).

### The ROUTE/IQ Warm-Start Method:
1. **Incumbent Solution Extraction:** Classical OR-Tools or 2-opt solves the initial routing problem, producing an incumbent ordering for the microcluster $(v_{\pi(0)}, v_{\pi(1)}, \dots, v_{\pi(K-1)})$.
2. **Binary Tensor Encoding:** This permutation is mapped to a binary indicator matrix $X^{(0)} \in \{0, 1\}^{K \times K}$:
   $$X_{i, p}^{(0)} = \begin{cases} 1 & \text{if customer } i \text{ is at position } p \\ 0 & \text{otherwise} \end{cases}$$
3. **Register Initialization:** The 16-qubit quantum register is initialized to the product state corresponding to the classical seed:
   $$|\psi_0\rangle = \bigotimes_{i=1}^K \bigotimes_{p=0}^{K-1} \left(X_{ip}^{(0)} |1\rangle + (1 - X_{ip}^{(0)}) |0\rangle\right)$$
4. **Subspace-Preserving Evolution:** By applying the continuous XY hopping mixer $H_M^{(XY)}$, quantum transitions occur strictly as particle-conserving swaps between adjacent position qubits within the same customer row:
   $$e^{-i \beta (X_{ip} X_{i, p+1} + Y_{ip} Y_{i, p+1})}$$
   This concentrates the quantum search amplitude strictly within valid and near-valid permutation states, eliminating the exponential search overhead of unconstrained transverse mixers.

---

## 2. Classical-to-QIGA Probability Initialization

In standard QIGA, Q-bit chromosomes are initialized in maximum entropy states:
$$\alpha_{ki} = \beta_{ki} = \frac{1}{\sqrt{2}} \implies P(|1\rangle) = 0.5$$
This forces QIGA to spend early generations evaluating random, low-quality tours.

### The ROUTE/IQ Classical Amplitude Bias Method:
Given a set of classical candidate routes $\mathcal{R}_{\text{seeds}} = \{R_{\text{OR-Tools}}, R_{\text{Clarke-Wright}}, R_{\text{2-opt}}\}$:
1. We compute the normalized relative precedence score $S(i) \in [0, 1]$ of customer $i$ across all seed routes:
   $$S(i) = 1.0 - \frac{\text{avg\_position}(i)}{N}$$
2. We initialize the Q-bit angles $\theta_i$ with an amplitude bias:
   $$\theta_i = \arcsin\left(\sqrt{0.10 + 0.80 \cdot S(i)}\right)$$
   $$\alpha_i = \cos(\theta_i), \quad \beta_i = \sin(\theta_i)$$
3. **Entropy Guardrail:** The initial probability $P_i(|1\rangle) = \sin^2(\theta_i)$ is bounded in $[0.10, 0.90]$ to prevent premature deterministic collapse, ensuring adequate quantum exploratory entropy while immediately favoring promising classical orderings.

---

## 3. Post-Measurement Hungarian Matching (Kuhn-Munkres Projection)

When sampling from QAOA on Qiskit Aer, shot noise or minor phase imperfections may occasionally produce bitstrings $z \in \{0, 1\}^{16}$ that do not form a strict doubly stochastic permutation matrix.

### Algorithmic Projection Steps:
1. Reshape the 16-bit measurement vector $z$ into a $4 \times 4$ matrix $M \in \{0, 1\}^{4 \times 4}$.
2. Define a cost matrix for assignment:
   $$\mathcal{C}_{ip} = 1.0 - M_{ip}$$
3. Execute the Kuhn-Munkres Hungarian algorithm (`scipy.optimize.linear_sum_assignment`):
   $$\min_{\pi \in S_4} \sum_{i=1}^4 \mathcal{C}_{i, \pi(i)}$$
4. This yields the unique valid permutation $\pi^*$ with minimal Hamming distance from the raw quantum measurement.
5. Record the projection delta $\Delta_{\text{proj}} = \text{Hamming}(z, z_{\pi^*})$ for scientific observability.

---

## 4. Multi-Round Feedback Loop and Dynamic Penalty Tuning

If QAOA samples invalid states or fails to improve the classical objective during round $k$:
1. **Penalty Multiplier Update:** Increase the penalty multiplier:
   $$\lambda^{(k+1)} = \lambda^{(k)} \cdot \left(1 + \eta \cdot \frac{\text{invalid\_shots}}{\text{total\_shots}}\right)$$
2. **Neighborhood Dilation:** If the 4-node cluster is tightly constrained, expand the neighborhood by dilating boundary nodes or swapping adjacent customer pairs.
3. **Re-optimization:** Run round $k+1$ using the updated parameters.

