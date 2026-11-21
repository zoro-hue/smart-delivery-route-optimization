# ROUTE/IQ — PHASE R: EXPERIMENTAL PROTOCOL & METHODOLOGICAL INTEGRITY
**Frozen Evaluation Protocol, Split Definitions, Fair Computational Budgets, and Verification Safeguards**

- **Project:** ROUTE/IQ (Phase R — Quantum Contribution Challenge)
- **Branch:** `research/phase-r-quantum-contribution-challenge`
- **Protocol Status:** **FROZEN** (Established prior to experimental execution)
- **Date:** 2026-11-06

---

## 1. Problem Instance Partitioning & Split Definitions

To prevent parameter leakage and overfitting to specific delivery distributions, all routing instances are partitioned into three strictly decoupled sets:

1. **Development Set ($\mathcal{D}_{\text{dev}}$):**
   - Scale: $N = 10, 25$ ($M = 2, 4$ vehicles).
   - Seeds: $S \in \{42, 101\}$.
   - Purpose: Unit testing, subproblem screening threshold tuning ($\tau_{\text{circuity}} = 1.30$), and circuit transpilation profiling.
2. **Validation Set ($\mathcal{D}_{\text{val}}$):**
   - Scale: $N = 25, 50$ ($M = 4, 5$ vehicles).
   - Seeds: $S \in \{202, 303\}$.
   - Purpose: Selection of variational parameter optimization limits ($max\_iter = 10$) and neighborhood selection strategy comparison.
3. **Held-Out Test Set ($\mathcal{D}_{\text{test}}$):**
   - Scale: $N = 25, 50, 100$ ($M = 4, 5, 8$ vehicles).
   - Seeds: $S \in \{777, 888, 999\}$.
   - Purpose: Final unbiased evaluation of complete-route distance, statistical hypothesis testing, and candidate acceptance rates.
   - **Non-Negotiable Rule:** Zero algorithmic or parameter adjustments are permitted based on held-out test evaluations.

---

## 2. Standardized Problem Instance Specification

Every benchmark instance generates a fully specified Capacitated Vehicle Routing Problem (CVRP) on realistic urban coordinates (NYC Manhattan/Queens delivery grid):
- **Depot:** Fixed at $(40.7580, -73.9855)$ with $d_0 = 0$.
- **Customer Coordinates:** Spanning radial distances $r \in [1.2, 9.5]\text{ km}$ from the depot.
- **Demands:** Discrete integer demands $d_i \in \{2, 3, 4, 5\}$ units.
- **Vehicle Capacities:** Uniform fleet capacity $Q \in \{25.0, 30.0, 40.0, 50.0\}$ units.
- **Asymmetric Road Impedance:**
  $$c_{ij} = d_{\text{Haversine}}(i, j) \times 1.25 \times \left(1.0 + 0.15 \cdot \left(\frac{\sin(3.1 i + 1.7 j) + 1}{2}\right)\right)$$
  capturing one-way street circuity, directional traffic congestion, and bridge toll delays.

---

## 3. Strict Fair-Budget Rules

1. **Equal Stopping Criteria for Classical Baselines:**
   - Standard industrial baseline: Google OR-Tools Guided Local Search with a generous time ceiling ($10.0\text{ seconds}$).
   - Classical multistart: 5 independent runs with randomized savings shape parameters $\lambda \in [0.5, 2.0]$.
2. **Symmetric Refinement Policy:**
   - A hybrid quantum candidate is never compared against an unrefined classical candidate.
   - If 2-opt post-polish is permitted for QAOA candidates, an identical 2-opt pass must be executed on all classical baselines.
3. **Unbundled Telemetry Mandate:**
   Every execution must independently record:
   - $T_{\text{preproc}}$: PySpark data ingestion and polar window partitioning latency.
   - $T_{\text{class}}$: Classical solver initialization latency.
   - $T_{\text{qaoa\_circuit}}$: Quantum circuit execution time on Qiskit Aer.
   - $T_{\text{qaoa\_opt}}$: Outer-loop classical parameter optimization time.
   - $T_{\text{recon}}$: Complete route re-insertion and feasibility verification time.
4. **Complete Route Standard:**
   - Subproblem energy improvements ($\Delta E < 0$) are considered intermediate diagnostics only.
   - An experiment is considered successful **if and only if the complete global vehicle route distance decreases**:
     $$\text{Cost}(R_{\text{final}}) < \text{Cost}(R_{\text{incumbent}})$$
     while maintaining 100% capacity feasibility and zero customer drops or duplicates.

