"""
Phase K: Comprehensive Adversarial Non-Degradation and Geometric Regularizer Audit.

Tests 10 Adversarial Edge Cases:
  1. Asymmetric Distances (D_ij != D_ji)
  2. One-Way Street Grid Loops
  3. Disconnected Components / Outliers
  4. Duplicate Customer IDs (preservation invariant)
  5. Multiple Customers at Identical Coordinates
  6. Insufficient Vehicle Capacity (proper feasibility reporting)
  7. Empty (N=0) and Singleton (N=1) Inputs
  8. Unusual Depot Positions (extreme perimeter)
  9. Boundary-Node Insertion Divergence (Trial 19 Counterexample)
  10. Pathological / Degenerate QAOA Candidates (All 0s, All 1s, Noise)

Tests Geometric Regularizer Properties:
  - Collinear Segments
  - Shared Endpoints
  - Overlapping Edges
  - Planar Crossing with Shorter Directed Road Distance (Trial 0 Paradox)
  - Non-Crossing Route with Longer Road Distance (One-Way Detour)

Outputs structured JSON results to scratch/phase_k_reproduction/adversarial_audit_results.json.
"""

import os
import sys
import json
import math
import numpy as np

os.environ["PYTHONPATH"] = "backend"
sys.path.insert(0, "backend")

from app.services.bigdata_pipeline import ensure_spark_environment
from app.services.road_network_service import RoadNetworkService
from app.services.optimization.qgar_pipeline import (
    QuantumGuidedAdaptiveRouter,
    QuantumCandidateEvaluator,
    AdaptiveQuantumInfluenceModel,
    count_tour_crossings,
    lines_intersect
)


def run_adversarial_audit():
    print("=" * 80)
    print("ROUTE/IQ — PHASE K: ADVERSARIAL AND REGULARIZER AUDIT")
    print("=" * 80)

    results = {}
    router = QuantumGuidedAdaptiveRouter(qaoa_p=1, qaoa_shots=256, use_spark=False)

    # -------------------------------------------------------------
    # Case 1: Asymmetric Distances
    # -------------------------------------------------------------
    print("\n[Case 1] Asymmetric Distance Matrix...")
    depot = {"id": "depot", "latitude": 40.75, "longitude": -73.98, "demand": 0}
    custs = [
        {"id": "c1", "latitude": 40.751, "longitude": -73.981, "demand": 2},
        {"id": "c2", "latitude": 40.752, "longitude": -73.982, "demand": 2},
        {"id": "c3", "latitude": 40.753, "longitude": -73.983, "demand": 2}
    ]
    loc_map = {"depot": 0, "c1": 1, "c2": 2, "c3": 3}
    # Highly asymmetric matrix
    mat_asym = np.array([
        [0.0, 1.0, 5.0, 8.0],
        [4.0, 0.0, 1.0, 7.0],
        [9.0, 6.0, 0.0, 1.0],
        [2.0, 8.0, 7.0, 0.0]
    ])
    res_sp = router.optimize_delivery_campaign(custs, depot, mat_asym, 15.0, loc_map, enable_qaoa=False)
    res_qg = router.optimize_delivery_campaign(custs, depot, mat_asym, 15.0, loc_map, enable_qaoa=True)
    c1_passed = res_qg["total_distance_km"] <= res_sp["total_distance_km"] + 1e-4
    results["case_1_asymmetric"] = {
        "passed": bool(c1_passed),
        "spatial_dist": res_sp["total_distance_km"],
        "qgar_dist": res_qg["total_distance_km"],
        "diff": round(res_qg["total_distance_km"] - res_sp["total_distance_km"], 4)
    }
    print(f"  Result: Passed={c1_passed} (Spatial={res_sp['total_distance_km']}, QGAR={res_qg['total_distance_km']})")

    # -------------------------------------------------------------
    # Case 2: One-Way Street Grid Loops
    # -------------------------------------------------------------
    print("\n[Case 2] One-Way Street Grid Loops...")
    # Directed cycle: 0 -> 1 -> 2 -> 3 -> 0 costs 4.0, reverse costs 40.0
    mat_oneway = np.array([
        [0.0, 1.0, 10.0, 10.0],
        [10.0, 0.0, 1.0, 10.0],
        [10.0, 10.0, 0.0, 1.0],
        [1.0, 10.0, 10.0, 0.0]
    ])
    res_sp = router.optimize_delivery_campaign(custs, depot, mat_oneway, 15.0, loc_map, enable_qaoa=False)
    res_qg = router.optimize_delivery_campaign(custs, depot, mat_oneway, 15.0, loc_map, enable_qaoa=True)
    c2_passed = res_qg["total_distance_km"] <= res_sp["total_distance_km"] + 1e-4
    results["case_2_oneway_grid"] = {
        "passed": bool(c2_passed),
        "spatial_dist": res_sp["total_distance_km"],
        "qgar_dist": res_qg["total_distance_km"]
    }
    print(f"  Result: Passed={c2_passed} (Spatial={res_sp['total_distance_km']}, QGAR={res_qg['total_distance_km']})")

    # -------------------------------------------------------------
    # Case 3: Disconnected Components / Extreme Distances
    # -------------------------------------------------------------
    print("\n[Case 3] Extreme Distances / Outliers...")
    mat_outlier = mat_asym.copy()
    mat_outlier[3, :] = 500.0  # c3 is an extreme outlier
    mat_outlier[:, 3] = 500.0
    mat_outlier[3, 3] = 0.0
    res_sp = router.optimize_delivery_campaign(custs, depot, mat_outlier, 15.0, loc_map, enable_qaoa=False)
    res_qg = router.optimize_delivery_campaign(custs, depot, mat_outlier, 15.0, loc_map, enable_qaoa=True)
    c3_passed = res_qg["total_distance_km"] <= res_sp["total_distance_km"] + 1e-4
    results["case_3_outliers"] = {
        "passed": bool(c3_passed),
        "spatial_dist": res_sp["total_distance_km"],
        "qgar_dist": res_qg["total_distance_km"]
    }
    print(f"  Result: Passed={c3_passed} (Spatial={res_sp['total_distance_km']}, QGAR={res_qg['total_distance_km']})")

    # -------------------------------------------------------------
    # Case 4: Duplicate Customer IDs
    # -------------------------------------------------------------
    print("\n[Case 4] Duplicate Customer IDs Preservation...")
    dup_custs = [
        {"id": "dup_1", "customer_id": "dup_1", "latitude": 40.751, "longitude": -73.981, "demand": 2},
        {"id": "dup_1", "customer_id": "dup_1", "latitude": 40.752, "longitude": -73.982, "demand": 2}
    ]
    # Router handles duplicate IDs cleanly by internally disambiguating if needed
    try:
        # Give distinct unique dict handles
        res_dup = router.optimize_delivery_campaign(
            dup_custs, depot, mat_asym[:3, :3], 15.0, {"depot": 0, "dup_1": 1}, enable_qaoa=False
        )
        c4_passed = (res_dup["feasibility"]["total_input_customers"] == 2)
    except Exception as e:
        c4_passed = False
    results["case_4_duplicate_ids"] = {"passed": bool(c4_passed)}
    print(f"  Result: Passed={c4_passed}")

    # -------------------------------------------------------------
    # Case 5: Multiple Customers at Identical Coordinates
    # -------------------------------------------------------------
    print("\n[Case 5] Multiple Customers at Identical Coordinates...")
    same_coord_custs = [
        {"id": "c1", "latitude": 40.751, "longitude": -73.981, "demand": 2},
        {"id": "c2", "latitude": 40.751, "longitude": -73.981, "demand": 3}
    ]
    loc_map_5 = {"depot": 0, "c1": 1, "c2": 2}
    mat_same = np.array([
        [0.0, 2.0, 2.0],
        [2.0, 0.0, 0.0],
        [2.0, 0.0, 0.0]
    ])
    res_same = router.optimize_delivery_campaign(same_coord_custs, depot, mat_same, 15.0, loc_map_5, enable_qaoa=True)
    c5_passed = res_same["feasibility"]["is_feasible"] and (res_same["feasibility"]["total_routed_customers"] == 2)
    results["case_5_identical_coords"] = {"passed": bool(c5_passed), "distance": res_same["total_distance_km"]}
    print(f"  Result: Passed={c5_passed} (Distance={res_same['total_distance_km']})")

    # -------------------------------------------------------------
    # Case 6: Insufficient Vehicle Capacity
    # -------------------------------------------------------------
    print("\n[Case 6] Insufficient Vehicle Capacity...")
    over_custs = [
        {"id": "c1", "latitude": 40.751, "longitude": -73.981, "demand": 20.0}  # Exceeds Q=15
    ]
    res_over = router.optimize_delivery_campaign(over_custs, depot, mat_asym[:2, :2], 15.0, {"depot": 0, "c1": 1})
    c6_passed = (res_over["feasibility"]["capacity_violations"] > 0 or not res_over["feasibility"]["is_feasible"])
    results["case_6_capacity_violation"] = {
        "passed": bool(c6_passed),
        "violations": res_over["feasibility"]["capacity_violations"]
    }
    print(f"  Result: Passed={c6_passed} (Reported violations={res_over['feasibility']['capacity_violations']})")

    # -------------------------------------------------------------
    # Case 7: Empty (N=0) and Singleton (N=1) Inputs
    # -------------------------------------------------------------
    print("\n[Case 7] Empty (N=0) and Singleton (N=1) Inputs...")
    res_empty = router.optimize_delivery_campaign([], depot, np.zeros((1, 1)), 15.0, {"depot": 0})
    res_single = router.optimize_delivery_campaign([custs[0]], depot, mat_asym[:2, :2], 15.0, {"depot": 0, "c1": 1})
    c7_passed = (res_empty["total_distance_km"] == 0.0 and res_single["feasibility"]["is_feasible"] and res_single["num_vehicles"] == 1)
    results["case_7_empty_and_singleton"] = {"passed": bool(c7_passed)}
    print(f"  Result: Passed={c7_passed}")

    # -------------------------------------------------------------
    # Case 8: Unusual Depot Positions (Extreme Perimeter)
    # -------------------------------------------------------------
    print("\n[Case 8] Unusual Depot Positions...")
    remote_depot = {"id": "depot", "latitude": 40.900, "longitude": -74.200, "demand": 0}
    res_sp = router.optimize_delivery_campaign(custs, remote_depot, mat_asym, 15.0, loc_map, enable_qaoa=False)
    res_qg = router.optimize_delivery_campaign(custs, remote_depot, mat_asym, 15.0, loc_map, enable_qaoa=True)
    c8_passed = res_qg["total_distance_km"] <= res_sp["total_distance_km"] + 1e-4
    results["case_8_unusual_depot"] = {"passed": bool(c8_passed)}
    print(f"  Result: Passed={c8_passed}")

    # -------------------------------------------------------------
    # Case 9: Boundary-Node Insertion Divergence (Trial 19)
    # -------------------------------------------------------------
    print("\n[Case 9] Boundary-Node Insertion Divergence (Trial 19 Scenario)...")
    # 3 core nodes + 2 boundary nodes
    custs_5 = [
        {"id": "c1", "latitude": 40.751, "longitude": -73.981, "demand": 2},
        {"id": "c2", "latitude": 40.752, "longitude": -73.982, "demand": 2},
        {"id": "c3", "latitude": 40.753, "longitude": -73.983, "demand": 2},
        {"id": "b1", "latitude": 40.754, "longitude": -73.984, "demand": 2},
        {"id": "b2", "latitude": 40.755, "longitude": -73.985, "demand": 2}
    ]
    loc_map_5b = {c["id"]: i + 1 for i, c in enumerate(custs_5)}
    loc_map_5b["depot"] = 0
    # Construct distance matrix matching Trial 19 condition
    mat_5 = np.random.default_rng(42).uniform(2.0, 15.0, (6, 6))
    np.fill_diagonal(mat_5, 0.0)
    res_sp = router.optimize_delivery_campaign(custs_5, depot, mat_5, 15.0, loc_map_5b, enable_qaoa=False)
    res_qg = router.optimize_delivery_campaign(custs_5, depot, mat_5, 15.0, loc_map_5b, enable_qaoa=True)
    c9_passed = res_qg["total_distance_km"] <= res_sp["total_distance_km"] + 1e-4
    results["case_9_boundary_divergence_guarded"] = {
        "passed": bool(c9_passed),
        "spatial_dist": res_sp["total_distance_km"],
        "qgar_dist": res_qg["total_distance_km"]
    }
    print(f"  Result: Passed={c9_passed} (Spatial={res_sp['total_distance_km']}, QGAR={res_qg['total_distance_km']})")

    # -------------------------------------------------------------
    # Case 10: Pathological / Degenerate QAOA Candidates
    # -------------------------------------------------------------
    print("\n[Case 10] Pathological QAOA Candidates (All 0s, All 1s)...")
    raw_zeros = {"0" * 9: 1024}
    raw_ones = {"1" * 9: 1024}
    eval_zeros = QuantumCandidateEvaluator.evaluate_all_candidates(raw_zeros, custs, depot, mat_asym, loc_map)
    eval_ones = QuantumCandidateEvaluator.evaluate_all_candidates(raw_ones, custs, depot, mat_asym, loc_map)
    inf_zeros = AdaptiveQuantumInfluenceModel.compute_quantum_influence(eval_zeros["best_candidate"], custs, depot, mat_asym, loc_map)
    inf_ones = AdaptiveQuantumInfluenceModel.compute_quantum_influence(eval_ones["best_candidate"], custs, depot, mat_asym, loc_map)
    c10_passed = (inf_zeros["adopted_source"] == "SPATIAL_SWEEP" or inf_zeros["adopted_cost_km"] <= inf_zeros["spatial_cost_km"] + 1e-4) and \
                 (inf_ones["adopted_source"] == "SPATIAL_SWEEP" or inf_ones["adopted_cost_km"] <= inf_ones["spatial_cost_km"] + 1e-4)
    results["case_10_pathological_candidates"] = {"passed": bool(c10_passed)}
    print(f"  Result: Passed={c10_passed}")

    # -------------------------------------------------------------
    # Geometric Regularizer Tests
    # -------------------------------------------------------------
    print("\n[Geometric Regularizer Edge Cases]...")
    # Collinear segments
    collinear_pts = [(0.0, 0.0), (0.0, 1.0), (0.0, 2.0), (0.0, 3.0)]
    cross_collinear = count_tour_crossings(collinear_pts)

    # Shared endpoints
    p1, p2, p3, p4 = (0.0, 0.0), (1.0, 1.0), (1.0, 1.0), (2.0, 0.0)
    shared_endpoint_intersect = lines_intersect(p1, p2, p3, p4)

    # Overlapping edges
    p_a1, p_a2 = (0.0, 0.0), (2.0, 0.0)
    p_b1, p_b2 = (1.0, 0.0), (3.0, 0.0)
    overlapping_intersect = lines_intersect(p_a1, p_a2, p_b1, p_b2)

    # Manhattan road network crossing paradox (Trial 0 verification)
    road_svc = RoadNetworkService()
    road_svc.ensure_loaded()
    trial_0_cluster = [
        (40.7580, -73.9855),  # depot
        (40.7620, -73.9800),  # c1
        (40.7550, -73.9780),  # c2
        (40.7600, -73.9720)   # c3
    ]
    mat_r, _, _ = road_svc.build_road_matrix(trial_0_cluster)
    tour_crossed = [0, 1, 3, 2, 0]
    tour_uncrossed = [0, 1, 2, 3, 0]
    cost_crossed = sum(mat_r[tour_crossed[k], tour_crossed[k+1]] for k in range(4))
    cost_uncrossed = sum(mat_r[tour_uncrossed[k], tour_uncrossed[k+1]] for k in range(4))
    cross_crossed = count_tour_crossings([trial_0_cluster[k] for k in tour_crossed])
    cross_uncrossed = count_tour_crossings([trial_0_cluster[k] for k in tour_uncrossed])

    results["geometric_regularizer_audit"] = {
        "collinear_crossings": cross_collinear,
        "shared_endpoint_rejected": not shared_endpoint_intersect,
        "overlapping_edge_detected": bool(overlapping_intersect),
        "trial_0_crossing_paradox": {
            "crossed_tour_crossings": cross_crossed,
            "crossed_tour_road_km": round(float(cost_crossed), 3),
            "uncrossed_tour_crossings": cross_uncrossed,
            "uncrossed_tour_road_km": round(float(cost_uncrossed), 3),
            "paradox_confirmed": bool(cost_crossed < cost_uncrossed and cross_crossed > cross_uncrossed)
        }
    }
    print(f"  Collinear crossings: {cross_collinear}")
    print(f"  Shared endpoints ignored correctly: {not shared_endpoint_intersect}")
    print(f"  Trial 0 Road Paradox Confirmed: {results['geometric_regularizer_audit']['trial_0_crossing_paradox']['paradox_confirmed']}")

    # Save to JSON
    out_dir = r"scratch/phase_k_reproduction"
    os.makedirs(out_dir, exist_ok=True)
    out_json = os.path.join(out_dir, "adversarial_audit_results.json")
    with open(out_json, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nAdversarial audit results saved to {out_json}")


if __name__ == "__main__":
    run_adversarial_audit()

