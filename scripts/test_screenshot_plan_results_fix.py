"""
Test Script: Verification of the Plan & Results Screenshot Bug Fixes
Validates:
1. Non-contradictory algorithm status counts (total, successful, failed, timed_out, running, queued).
2. Elimination of "Completed with failures: 3/3" and "All 3 evaluated" when failures exist.
3. Strict best-algorithm selection: only feasible, non-failed solvers can win; if all fail, best_algorithm is None.
4. Correct canonical statuses: SUCCESS, FAILED, TIMED_OUT, QUEUED, RUNNING.
5. Correct progress label generation.
"""

import sys
import os

# Add backend to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.api.routes.optimization import _build_comparison_summary, _format_job_status_response

def test_summary_all_successful():
    results = {
        "ortools": {
            "success": True,
            "status": "SUCCESS",
            "algorithm": "ortools",
            "algorithm_name": "Google OR-Tools",
            "total_distance_km": 150.0,
            "execution_time_sec": 0.4,
            "validation": {"is_feasible": True, "capacity_violations": 0, "unserved_count": 0},
            "routes": [{"vehicle_id": 1, "distance_km": 75.0}, {"vehicle_id": 2, "distance_km": 75.0}],
        },
        "routeiq_cooperative": {
            "success": True,
            "status": "SUCCESS",
            "algorithm": "routeiq_cooperative",
            "algorithm_name": "ROUTE/IQ Cooperative Engine",
            "total_distance_km": 142.0,
            "execution_time_sec": 1.2,
            "validation": {"is_feasible": True, "capacity_violations": 0, "unserved_count": 0},
            "routes": [{"vehicle_id": 1, "distance_km": 71.0}, {"vehicle_id": 2, "distance_km": 71.0}],
        },
        "qaoa": {
            "success": True,
            "status": "SUCCESS",
            "algorithm": "qaoa",
            "algorithm_name": "QAOA",
            "total_distance_km": 165.0,
            "execution_time_sec": 2.5,
            "validation": {"is_feasible": True, "capacity_violations": 0, "unserved_count": 0},
            "routes": [{"vehicle_id": 1, "distance_km": 80.0}, {"vehicle_id": 2, "distance_km": 85.0}],
        }
    }
    summary = _build_comparison_summary(["ortools", "routeiq_cooperative", "qaoa"], results, 100, 300, 12)
    assert summary["has_feasible_solution"] is True, "Should have feasible solution"
    assert summary["best_algorithm"] == "routeiq_cooperative", "Cooperative should win with 142 km"
    assert summary["best_feasible_distance_km"] == 142.0, "Best distance should be 142.0"
    print("PASS: test_summary_all_successful")

def test_summary_partial_failure():
    # 2 succeed, 1 failed with lower distance (e.g. invalid/failed)
    results = {
        "ortools": {
            "success": True,
            "status": "SUCCESS",
            "algorithm": "ortools",
            "algorithm_name": "Google OR-Tools",
            "total_distance_km": 150.0,
            "execution_time_sec": 0.4,
            "validation": {"is_feasible": True, "capacity_violations": 0, "unserved_count": 0},
            "routes": [{"vehicle_id": 1, "distance_km": 150.0}],
        },
        "routeiq_cooperative": {
            "success": False,
            "status": "FAILED",
            "algorithm": "routeiq_cooperative",
            "algorithm_name": "ROUTE/IQ Cooperative Engine",
            "error": "Simulated solver crash",
            "total_distance_km": 50.0, # even with lower distance, must not win!
            "validation": {"is_feasible": False, "capacity_violations": 2, "unserved_count": 5},
            "routes": [],
        },
        "qaoa": {
            "success": True,
            "status": "SUCCESS",
            "algorithm": "qaoa",
            "algorithm_name": "QAOA",
            "total_distance_km": 165.0,
            "execution_time_sec": 2.5,
            "validation": {"is_feasible": True, "capacity_violations": 0, "unserved_count": 0},
            "routes": [{"vehicle_id": 1, "distance_km": 165.0}],
        }
    }
    summary = _build_comparison_summary(["ortools", "routeiq_cooperative", "qaoa"], results, 100, 300, 12)
    assert summary["has_feasible_solution"] is True, "Should find feasible solution among ortools/qaoa"
    assert summary["best_algorithm"] == "ortools", "ortools must win because cooperative failed!"
    assert summary["best_feasible_distance_km"] == 150.0
    # verify item for cooperative is flagged properly
    coop_item = next(it for it in summary["items"] if it["id"] == "routeiq_cooperative")
    assert coop_item["status"] == "FAILED"
    assert coop_item["is_best"] is False
    print("PASS: test_summary_partial_failure")

def test_summary_all_failed():
    results = {
        "ortools": {
            "success": False,
            "status": "FAILED",
            "error": "Memory limit exceeded",
            "total_distance_km": 0.0,
        },
        "qaoa": {
            "success": False,
            "status": "TIMED_OUT",
            "error": "Execution timed out after 30s",
            "total_distance_km": 0.0,
        }
    }
    summary = _build_comparison_summary(["ortools", "qaoa"], results, 100, 300, 12)
    assert summary["has_feasible_solution"] is False, "Must be False when all fail"
    assert summary["best_algorithm"] is None, "Must NOT invent a winner"
    assert summary["best_algorithm_name"] is None
    assert summary["best_feasible_distance_km"] is None
    assert "No feasible solution found" in summary["best_reason"]
    print("PASS: test_summary_all_failed")

def test_job_status_response_counts_and_labels():
    # Scenario A: All 3 succeed
    job_all_succ = {
        "job_id": "job-123",
        "experiment_id": "exp-123",
        "status": "COMPLETED",
        "total_algorithms": 3,
        "selected_algorithms": ["ortools", "routeiq_cooperative", "tabu_search"],
        "primary_algorithm": "ortools",
        "solver_statuses": {
            "ortools": "SUCCESS",
            "routeiq_cooperative": "SUCCESS",
            "tabu_search": "SUCCESS",
        },
        "results": {
            "ortools": {"success": True, "status": "SUCCESS", "total_distance_km": 150.0, "validation": {"is_feasible": True}},
            "routeiq_cooperative": {"success": True, "status": "SUCCESS", "total_distance_km": 140.0, "validation": {"is_feasible": True}},
            "tabu_search": {"success": True, "status": "SUCCESS", "total_distance_km": 155.0, "validation": {"is_feasible": True}},
        },
        "errors": {},
        "created_at": 100.0,
    }
    resp_a = _format_job_status_response(job_all_succ)
    assert resp_a["total_algorithms"] == 3
    assert resp_a["successful_count"] == 3
    assert resp_a["failed_count"] == 0
    assert resp_a["timed_out_count"] == 0
    assert resp_a["completed_algorithms"] == 3
    assert "All 3 algorithms completed successfully" in resp_a["progress_label"]
    print(f"PASS Scenario A: {resp_a['progress_label']}")

    # Scenario B: 2 succeed, 1 failed (Screenshot condition!)
    job_partial = {
        "job_id": "job-456",
        "experiment_id": "exp-456",
        "status": "COMPLETED_WITH_FAILURES",
        "total_algorithms": 3,
        "selected_algorithms": ["ortools", "routeiq_cooperative", "qaoa"],
        "primary_algorithm": "ortools",
        "solver_statuses": {
            "ortools": "SUCCESS",
            "routeiq_cooperative": "SUCCESS",
            "qaoa": "FAILED",
        },
        "results": {
            "ortools": {"success": True, "status": "SUCCESS", "total_distance_km": 150.0, "validation": {"is_feasible": True}},
            "routeiq_cooperative": {"success": True, "status": "SUCCESS", "total_distance_km": 140.0, "validation": {"is_feasible": True}},
            "qaoa": {"success": False, "status": "FAILED", "error": "Quantum simulator timeout", "total_distance_km": 0.0},
        },
        "errors": {"qaoa": "Quantum simulator timeout"},
        "created_at": 100.0,
    }
    resp_b = _format_job_status_response(job_partial)
    assert resp_b["total_algorithms"] == 3
    assert resp_b["successful_count"] == 2
    assert resp_b["failed_count"] == 1
    assert resp_b["timed_out_count"] == 0
    assert resp_b["completed_algorithms"] == 2, f"Expected 2 completed, got {resp_b['completed_algorithms']}"
    assert "Evaluation completed: 2 successful, 1 failed." == resp_b["progress_label"]
    # Verify that it NEVER says "Completed with failures: 3/3"
    assert "3/3" not in resp_b["progress_label"]
    print(f"PASS Scenario B: {resp_b['progress_label']} (successful: {resp_b['successful_count']}, failed: {resp_b['failed_count']})")

    # Scenario C: 1 succeed, 1 failed, 1 timed out
    job_timeout = {
        "job_id": "job-789",
        "experiment_id": "exp-789",
        "status": "COMPLETED_WITH_FAILURES",
        "total_algorithms": 3,
        "selected_algorithms": ["ortools", "qiga", "qaoa"],
        "primary_algorithm": "ortools",
        "solver_statuses": {
            "ortools": "SUCCESS",
            "qiga": "FAILED",
            "qaoa": "TIMED_OUT",
        },
        "results": {
            "ortools": {"success": True, "status": "SUCCESS", "total_distance_km": 150.0, "validation": {"is_feasible": True}},
            "qiga": {"success": False, "status": "FAILED", "error": "Simulation error"},
            "qaoa": {"success": False, "status": "TIMED_OUT", "error": "Timed out after 30s"},
        },
        "errors": {"qiga": "Simulation error", "qaoa": "Timed out after 30s"},
        "created_at": 100.0,
    }
    resp_c = _format_job_status_response(job_timeout)
    assert resp_c["successful_count"] == 1
    assert resp_c["failed_count"] == 1
    assert resp_c["timed_out_count"] == 1
    assert resp_c["completed_algorithms"] == 1
    assert "Evaluation completed: 1 successful, 1 failed, 1 timed out." == resp_c["progress_label"]
    print(f"PASS Scenario C: {resp_c['progress_label']}")

    # Scenario D: Still evaluating (1 running, 1 queued, 1 successful)
    job_running = {
        "job_id": "job-running",
        "experiment_id": "exp-running",
        "status": "RUNNING",
        "total_algorithms": 3,
        "selected_algorithms": ["ortools", "routeiq_cooperative", "tabu_search"],
        "primary_algorithm": "ortools",
        "solver_statuses": {
            "ortools": "SUCCESS",
            "routeiq_cooperative": "RUNNING",
            "tabu_search": "QUEUED",
        },
        "results": {
            "ortools": {"success": True, "status": "SUCCESS", "total_distance_km": 150.0, "validation": {"is_feasible": True}},
        },
        "errors": {},
        "created_at": 100.0,
    }
    resp_d = _format_job_status_response(job_running)
    assert resp_d["successful_count"] == 1
    assert resp_d["running_count"] == 1
    assert resp_d["queued_count"] == 1
    assert "Evaluating: 1/3 successful · 1 running · 1 queued" in resp_d["progress_label"]
    print(f"PASS Scenario D: {resp_d['progress_label']}")

if __name__ == "__main__":
    test_summary_all_successful()
    test_summary_partial_failure()
    test_summary_all_failed()
    test_job_status_response_counts_and_labels()
    print("\nALL VERIFICATION TESTS PASSED SUCCESSFULLY!")
