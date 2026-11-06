# PHASE AE: SCIENTIFIC LIMITATIONS, HARDWARE CONSTRAINTS & HONEST BENCHMARK AUDIT
## ROUTE/IQ — Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing
**Repository:** `D:\UROP\smart-delivery-route-optimization`  
**Branch:** `research/phase-ae-backend-integration`  
**Protected Main Baseline:** `a8eb849988201d7929566f331c1ae3afac09b632`  
**Date:** November 2026  
**Institution:** Department of Computer Science and Engineering, SRM University-AP  
**Supervisor:** Dr. Vishnu Prasad Verma  
**Investigators:** J. Jayanth, B. Kaivalya, P. Shyam Sai

---

## 1. Scientific Integrity Policy

In accordance with strict scientific guidelines and supervisor review standards:
- **No Quantum Advantage:** No quantum advantage has been observed or claimed. QAOA executed on classical simulators operates as a variational quantum heuristic.
- **Fair Classical Comparison:** Classical metaheuristics (Tabu Search, Kernighan-Lin, VND) achieve equivalent solution quality to simulated QAOA while executing significantly faster.
- **Spark Distributed Scaling vs Single-Node:** Single-machine `local[*]` execution demonstrates distributed pipeline mechanics but does not represent multi-node network cluster benchmarks.

---

## 2. Hardware & Simulator Constraints

### 2.1 Statevector Simulation Limits (Hilbert Space Scaling)
The state space of an $N$-qubit system scales as $2^N$ complex amplitudes:
- For $N = 8$: $2^8 = 256$ complex amplitudes ($\approx 4\text{ KB}$ memory).
- For $N = 16$: $2^{16} = 65,536$ complex amplitudes ($\approx 1\text{ MB}$ memory).
- For $N = 20$: $2^{20} = 1,048,576$ complex amplitudes ($\approx 16\text{ MB}$ memory).
- For $N = 30$: $2^{30} \approx 10^9$ complex amplitudes ($\approx 16\text{ GB}$ memory).
- For $N \ge 35$: Infeasible on classical workstations.

**Operational Safeguard:** In ROUTE/IQ, QAOA is restricted to boundary subproblems with $N \le 8$ nodes to ensure responsive simulation without memory exhaustion.

### 2.2 Quantum-Inspired vs Genuine Quantum
- **QIGA / IQGA:** Uses classically simulated Q-bit probability vectors $(\alpha, \beta)$ updated via rotation matrices. It is an evolutionary metaheuristic run entirely on classical CPU.
- **Qiskit Statevector:** Classical linear algebra simulating ideal unitary gate evolution without quantum hardware noise, gate infidelities, or decoherence.

---

## 3. Operational & Algorithmic Limitations

1. **Proposition 1 Incumbent Dependency:**
   Proposition 1 guarantees that the solution never deteriorates relative to the incumbent. However, if the initial incumbent is low quality, Proposition 1 preserves that baseline; it cannot prove global optimality.
2. **Polar Angle Wedge Sorting:**
   The polar sweep clustering heuristic is geometrically effective for radial customer distributions centered around a central depot. For elongated or multi-depot geographies, K-means or Voronoi tessellation may be required.
3. **Execution Latency Tradeoff:**
   While classical heuristics (Tabu Search, 2-Opt) complete within 2–15 ms, simulated QAOA circuits require 50–250 ms per subproblem on classical CPU.

