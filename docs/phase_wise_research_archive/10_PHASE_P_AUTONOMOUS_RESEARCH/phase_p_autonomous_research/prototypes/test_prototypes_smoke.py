"""
Smoke test suite for Phase P experimental prototypes.
Verifies that all 5 prototypes execute end-to-end on a test instance (N=10) with 100% feasibility.
"""

import sys
import os
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from phase_p_autonomous_research.prototypes.common_evaluator import generate_benchmark_instance
from phase_p_autonomous_research.prototypes.proto_1_classical_seeded_qaoa import ClassicalSeededQAOASolver
from phase_p_autonomous_research.prototypes.proto_2_spark_hierarchical_qaoa import SparkHierarchicalQAOASolver
from phase_p_autonomous_research.prototypes.proto_3_adaptive_neighborhood_qaoa import AdaptiveNeighborhoodQAOASolver
from phase_p_autonomous_research.prototypes.proto_4_cooperative_qaoa_qiga import CooperativeQAOAQIGASolver
from phase_p_autonomous_research.prototypes.proto_5_iterative_feedback_controller import IncumbentPreservingCooperativeEngine


class TestPhasePPrototypes(unittest.TestCase):

    def setUp(self):
        self.instance = generate_benchmark_instance(num_customers=10, num_vehicles=2, vehicle_capacity=25.0, seed=42)

    def test_proto_1_classical_seeded_qaoa(self):
        solver = ClassicalSeededQAOASolver(p=1, shots=256)
        res = solver.solve_instance(self.instance)
        print(f"\nProto 1 Result: {res}")
        self.assertTrue(res["is_feasible"])
        self.assertGreater(res["total_distance_km"], 0.0)

    def test_proto_2_spark_hierarchical_qaoa(self):
        # Test single machine path for fast unit test
        solver = SparkHierarchicalQAOASolver(p=1, shots=256)
        res = solver.solve_instance(self.instance, use_spark=False)
        print(f"\nProto 2 Result: {res}")
        self.assertTrue(res["is_feasible"])
        self.assertGreater(res["total_distance_km"], 0.0)

    def test_proto_3_adaptive_neighborhood_qaoa(self):
        solver = AdaptiveNeighborhoodQAOASolver(p=1, shots=256)
        res = solver.solve_instance(self.instance)
        print(f"\nProto 3 Result: {res}")
        self.assertTrue(res["is_feasible"])
        self.assertGreater(res["total_distance_km"], 0.0)

    def test_proto_4_cooperative_qaoa_qiga(self):
        solver = CooperativeQAOAQIGASolver(pop_size=10, generations=5, qaoa_interval=5, shots=128)
        res = solver.solve_instance(self.instance)
        print(f"\nProto 4 Result: {res}")
        self.assertTrue(res["is_feasible"])
        self.assertGreater(res["total_distance_km"], 0.0)

    def test_proto_5_iterative_feedback_controller(self):
        solver = IncumbentPreservingCooperativeEngine(qaoa_p=1, qaoa_shots=256)
        res = solver.solve_instance(self.instance, use_spark=False)
        print(f"\nProto 5 Result: {res}")
        self.assertTrue(res["is_feasible"])
        self.assertGreater(res["total_distance_km"], 0.0)
        self.assertLessEqual(res["total_distance_km"], res["ortools_initial_distance_km"])


if __name__ == "__main__":
    unittest.main()

