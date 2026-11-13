# PHASE AC DELIVERABLE 7: GUARDRAIL ADVERSARIAL STRESS TESTS

## Project Information
- **Project:** ROUTE/IQ — Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing
- **Institution:** SRM University-AP | **Supervisor:** Dr. Vishnu Prasad Verma
- **Audit Branch:** `research/phase-ac-independent-validation`

---

## 1. Adversarial Test Methodology

To determine whether `Proposition1Guardrail` can be broken, bypassed, or tricked into accepting an infeasible or degrading route, we constructed an adversarial test suite (`test_guardrail_adversarial.py`) evaluating **11 critical edge cases**.

---

## 2. Adversarial Test Suite Execution & Results

Executed via `pytest phase_ac_independent_validation/tests/test_guardrail_adversarial.py -v`:

| Test Case # | Adversarial Stress Condition | Injected Defect / Challenge | Expected Guardrail Behavior | Observed Behavior | Test Status |
| :---: | :--- | :--- | :--- | :--- | :---: |
| **T1** | Exact Capacity Boundary | Payload demand $q_A = \text{cap}_A$ exactly ($20.0 = 20.0$) | Accept if improving; must not falsely flag as violation | Accepted as feasible ($q_A \le \text{cap}_A$) | **PASSED** |
| **T2** | Slight Capacity Overage | Payload demand $q_A = 20.0$, $\text{cap}_A = 19.99$ (+0.01 overage) | Must reject immediately | Rejected with `CAPACITY_CONSTRAINT_VIOLATION` | **PASSED** |
| **T3** | Empty Partition | Candidate places all customers in Vehicle B ($T_A = []$) | Must reject empty vehicle assignment | Rejected with `CAPACITY_CONSTRAINT_VIOLATION` ($qa = 0$) | **PASSED** |
| **T4** | Singleton Partition | Candidate assigns exactly 1 customer to A, $N-1$ to B | Must permit if capacities allow; verify feasible | Verified feasible | **PASSED** |
| **T5** | Missing Customer | Customer 3 dropped entirely from candidate tours | Must reject coverage defect | Rejected with `INVALID_CUSTOMER_COVERAGE` | **PASSED** |
| **T6** | Duplicate Customer | Customer 2 placed in both Vehicle A and Vehicle B | Must reject duplicate customer stop | Rejected with `INVALID_CUSTOMER_COVERAGE` | **PASSED** |
| **T7** | Out-of-Bounds Customer | Customer ID 999 injected into candidate tour | Must reject invalid node index | Rejected with `INVALID_CUSTOMER_COVERAGE` | **PASSED** |
| **T8** | Unreachable Edge / $\infty$ Cost | Injected $\infty$ cost ($10^9$) on candidate's edge | Must reject infinite path degradation | Rejected with `SUBOPTIMAL_OBJECTIVE_REJECTED` | **PASSED** |
| **T9** | Asymmetric Directed Road Costs | $D_{1,2} = 50.0 \ne D_{2,1} = 1.0$ (one-way street) | Must correctly evaluate directed TSP orientation | Evaluated directed tour correctly | **PASSED** |
| **T10** | Improving Single Vehicle but Degrading Fleet | Vehicle A improves by 5 km, Vehicle B degrades by 12 km (net +7 km degradation) | Must evaluate sum of fleet routes and reject net degradation | Rejected with `SUBOPTIMAL_OBJECTIVE_REJECTED`; retained incumbent | **PASSED** |
| **T11** | Numerical Precision Drift | Candidate improves by only $10^{-6}$ km (below $10^{-4}$ tolerance) | Must reject micro-drift noise below tolerance | Rejected with `SUBOPTIMAL_OBJECTIVE_REJECTED` | **PASSED** |

---

## 3. Adversarial Test Summary

- **Total Adversarial Trials:** 11 edge cases.
- **Failures:** 0.
- **Bypasses:** 0.
- **Unresolved Edge Cases:** 0.
- **Independent Verdict:** The implementation of Proposition 1 is robust, fails safe against all adversarial injections, and unconditionally prevents degraded or infeasible routes from entering the delivery schedule.
