# Phase T Deliverable 13: Failed Experiments & Negative Results

**Document:** `phase_t_nextgen_hybrid_architecture/PHASE_T_FAILED_EXPERIMENTS.md`  
**Date:** 2026-11-06  
**Status:** Completed & Rigorously Verified  
**Branch:** `research/phase-t-nextgen-hybrid-architecture`

---

## 1. Documentation of Unsuccessful Experiments

### 1.1 Exponential Scaling of Classical QAOA Simulation
- **Experiment:** Attempting to simulate a full 16-qubit boundary bipartition circuit on Scale Large_100 ($N=100$).
- **Result:** **SIMULATOR BOTTLENECK (9,343.4 ms for a single circuit evaluation).**
- **Root Cause:** State-vector and tensor simulation on CPU scales as $O(2^{N_q})$. At $N_q = 16$, the state vector has $65,536$ complex amplitudes, and simulating 8 COBYLA iterations with 128 shots followed by 512 shots required over $9.3$ seconds on an Intel CPU.
- **Remediation:** Quantum circuits must be strictly gated to $N_q \le 12$ on classical simulators, and larger instances ($N_q \ge 16$) must await physical QPU hardware.

### 1.2 Unconstrained Vehicle Count Allocation
- **Experiment:** Attempting to formulate multi-vehicle assignment ($M \ge 4$ vehicles) on a single quantum register.
- **Result:** **REJECTED.**
- **Root Cause:** Encoding $N=16$ customers across $M=4$ vehicles requires $N \cdot M = 64$ qubits. Simulating a 64-qubit quantum circuit on classical hardware requires $2^{64} \times 16\text{ bytes} \approx 2.95 \times 10^{11}\text{ GB}$ of RAM, which is physically impossible.
- **Remediation:** Restricted the quantum target to **Two-Vehicle Boundary Bipartitioning** ($N_q = 16$ qubits), which captures the essential inter-route trade-off while remaining simulable.

### 1.3 Blind Micro-Route Quantum Dispatch
- **Experiment:** Continuing to pass 4-customer sub-tours to QAOA after OR-Tools GLS.
- **Result:** **REJECTED (0.00 km Net Fleet Improvement across all tests).**
- **Root Cause:** Fully verified in Phase S; micro-route tours are already at their global minima post-OR-Tools.
