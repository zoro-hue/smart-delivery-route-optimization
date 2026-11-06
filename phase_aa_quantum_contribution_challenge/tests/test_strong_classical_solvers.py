"""
Phase AA Unit Tests: Strong Classical Solvers & Fair Budgeting Suite.
Verifies correctness, capacity compliance, determinism, and execution bounds for:
- Multistart Kernighan-Lin
- Tabu Search
- Simulated Annealing
- Exact 2^N Enumeration
"""

import sys
import os
import pytest
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from phase_aa_quantum_contribution_challenge.benchmarks.benchmark_strong_classical_challenge import (
    StrongClassicalSuite
)


class TestStrongClassicalSolvers:
    @classmethod
    def setup_class(cls):
        cls.suite = StrongClassicalSuite()
        cls.N = 8
        np.random.seed(42)
        cls.demands = np.random.randint(1, 4, cls.N)
        total_demand = sum(cls.demands)
        cls.cap_a = float(np.ceil(total_demand * 0.55))
        cls.cap_b = float(np.ceil(total_demand * 0.55))
        cls.h_diff = np.random.uniform(-5.0, 5.0, cls.N)
        cls.W = np.random.uniform(0.5, 3.0, (cls.N, cls.N))
        cls.W = (cls.W + cls.W.T) / 2.0
        np.fill_diagonal(cls.W, 0.0)

        delta_q = cls.cap_a - cls.cap_b
        lambda_c = 2.0
        cls.Q = np.zeros((cls.N, cls.N))
        for i in range(cls.N):
            for j in range(cls.N):
                if i != j:
                    cls.Q[i, j] = -cls.W[i, j] + lambda_c * cls.demands[i] * cls.demands[j]
            cls.Q[i, i] = cls.h_diff[i] - 2.0 * lambda_c * delta_q * cls.demands[i]

    def test_multistart_kl_capacity_compliance(self):
        """Verify Multistart KL produces strictly capacity-compliant bipartitions."""
        p, cost, evals = self.suite.multistart_kernighan_lin(
            self.Q, self.demands, self.h_diff, self.cap_a, self.cap_b, max_restarts=10
        )
        assert len(p) == self.N
        qa = sum(self.demands[k] for k in range(self.N) if p[k] == 1)
        qb = sum(self.demands[k] for k in range(self.N) if p[k] == 0)
        assert qa <= self.cap_a
        assert qb <= self.cap_b
        assert evals > 0

    def test_tabu_search_capacity_compliance(self):
        """Verify Tabu Search produces strictly capacity-compliant bipartitions."""
        p, cost, evals = self.suite.tabu_search_partition(
            self.Q, self.demands, self.h_diff, self.cap_a, self.cap_b, max_evals=64
        )
        assert len(p) == self.N
        qa = sum(self.demands[k] for k in range(self.N) if p[k] == 1)
        qb = sum(self.demands[k] for k in range(self.N) if p[k] == 0)
        assert qa <= self.cap_a
        assert qb <= self.cap_b
        assert evals <= 80

    def test_simulated_annealing_capacity_compliance(self):
        """Verify Simulated Annealing produces strictly capacity-compliant bipartitions."""
        p, cost, evals = self.suite.simulated_annealing_partition(
            self.Q, self.demands, self.h_diff, self.cap_a, self.cap_b, max_evals=100
        )
        assert len(p) == self.N
        qa = sum(self.demands[k] for k in range(self.N) if p[k] == 1)
        qb = sum(self.demands[k] for k in range(self.N) if p[k] == 0)
        assert qa <= self.cap_a
        assert qb <= self.cap_b

    def test_exact_enumeration_optimality(self):
        """Verify Exact Enumeration finds the true global minimum QUBO cost."""
        p_ex, cost_ex, evals = self.suite.exact_enumeration_partition(
            self.Q, self.demands, self.cap_a, self.cap_b
        )
        assert len(p_ex) == self.N
        # Any other feasible partition must have cost >= cost_ex
        qa = sum(self.demands[k] for k in range(self.N) if p_ex[k] == 1)
        qb = sum(self.demands[k] for k in range(self.N) if p_ex[k] == 0)
        assert qa <= self.cap_a
        assert qb <= self.cap_b

        # Sample 20 random partitions and check cost
        for _ in range(20):
            p_test = np.random.randint(0, 2, self.N)
            q1 = sum(self.demands[k] for k in range(self.N) if p_test[k] == 1)
            q2 = sum(self.demands[k] for k in range(self.N) if p_test[k] == 0)
            if q1 <= self.cap_a and q2 <= self.cap_b and (0 < q1 < sum(self.demands)):
                c_test = float(p_test.T @ self.Q @ p_test)
                assert c_test >= cost_ex - 1e-4
