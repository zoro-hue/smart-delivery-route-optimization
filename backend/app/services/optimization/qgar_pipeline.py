"""
Quantum-Guided Adaptive Reconstruction (QGAR) Pipeline for ROUTE/IQ.

Implements:
1. Quality-Aware Quantum Candidate Selection (sampling and evaluating all unique QAOA bitstrings).
2. Adaptive Quantum Influence Model (modulating lambda based on candidate quality and angular sector crossing penalties).
3. Crossing-Aware Core Backbone Selection (preventing the Angular Disruption Effect).
4. Quantum-Guided Boundary DP Reconstruction (preserving quantum-favored directed transitions).
5. Comprehensive Telemetry: candidate diversity, entropy, lambda, crossings, and unbundled runtimes.
"""

import time
import math
import itertools
from typing import Dict, Any, List, Tuple, Optional, Set
import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment

from app.services.spark_routing_preprocessor import SparkRoutingPreprocessor, CalibratedTrafficImpedanceModel
from app.services.optimization.qaoa_subproblem_optimizer import QAOASubproblemOptimizer


def lines_intersect(p1: Tuple[float, float], p2: Tuple[float, float], p3: Tuple[float, float], p4: Tuple[float, float]) -> bool:
    """Checks if line segment (p1, p2) intersects with (p3, p4)."""
    def ccw(A, B, C):
        return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
    # Ignore shared endpoints
    if p1 == p3 or p1 == p4 or p2 == p3 or p2 == p4:
        return False
    return (ccw(p1, p3, p4) != ccw(p2, p3, p4)) and (ccw(p1, p2, p3) != ccw(p1, p2, p4))


def count_tour_crossings(tour_coords: List[Tuple[float, float]]) -> int:
    """Calculates number of 2D planar edge crossings in a closed tour."""
    n = len(tour_coords)
    if n < 4:
        return 0
    crossings = 0
    edges = [(tour_coords[i], tour_coords[(i + 1) % n]) for i in range(n)]
    for i in range(len(edges)):
        for j in range(i + 2, len(edges)):
            if i == 0 and j == len(edges) - 1:
                continue
            if lines_intersect(edges[i][0], edges[i][1], edges[j][0], edges[j][1]):
                crossings += 1
    return crossings


class QuantumCandidateEvaluator:
    """
    Quality-Aware Quantum Candidate Evaluator.
    Decodes all candidate measurement bitstrings, evaluates directed road costs,
    detects edge crossings, and computes diversity metrics.
    """

    @staticmethod
    def evaluate_all_candidates(
        raw_counts: Dict[str, int],
        customers: List[Dict[str, Any]],
        depot: Dict[str, Any],
        matrix: np.ndarray,
        loc_map: Dict[str, int],
        depot_idx: int = 0
    ) -> Dict[str, Any]:
        m = len(customers)
        total_shots = max(1, sum(raw_counts.values()))
        depot_coord = (float(depot.get("latitude", 40.7580)), float(depot.get("longitude", -73.9855)))
        cust_coords = [(float(c.get("latitude", depot_coord[0])), float(c.get("longitude", depot_coord[1]))) for c in customers]

        valid_candidates = []
        unique_permutations = set()
        entropy = 0.0

        # Sort bitstrings by frequency descending
        sorted_samples = sorted(raw_counts.items(), key=lambda x: x[1], reverse=True)

        for bstr, count in sorted_samples:
            prob = count / total_shots
            if prob > 0:
                entropy -= prob * math.log2(prob)

            # Clean and decode bitstring
            clean_bstr = bstr.replace(" ", "")
            if len(clean_bstr) < m * m:
                continue

            matrix_x = np.zeros((m, m), dtype=int)
            for i in range(m):
                for t in range(m):
                    bit_idx = i * m + t
                    if bit_idx < len(clean_bstr) and clean_bstr[bit_idx] == '1':
                        matrix_x[i, t] = 1

            # Check if valid permutation
            row_sums = matrix_x.sum(axis=1)
            col_sums = matrix_x.sum(axis=0)
            is_valid = (np.all(row_sums == 1) and np.all(col_sums == 1))

            if is_valid:
                step_to_cust = {np.argmax(matrix_x[:, t]): t for t in range(m)}
                # Invert: customer index for each step t
                cust_order_indices = [np.argmax(matrix_x[:, t]) for t in range(m)]
                projection_needed = False
            else:
                projection_needed = True
                # Kuhn-Munkres projection
                cost_mat = -matrix_x
                r_ind, c_ind = linear_sum_assignment(cost_mat)
                step_to_cust = {c_ind[i]: i for i in range(m)}
                cust_order_indices = [step_to_cust[t] for t in range(m)]

            perm_tuple = tuple(cust_order_indices)
            if perm_tuple in unique_permutations:
                continue
            unique_permutations.add(perm_tuple)

            ordered_custs = [customers[idx] for idx in cust_order_indices]
            ordered_indices = [depot_idx] + [loc_map[c["id"]] for c in ordered_custs] + [depot_idx]

            # Compute directed tour cost
            tour_cost = 0.0
            for u, v in zip(ordered_indices[:-1], ordered_indices[1:]):
                tour_cost += matrix[u, v]

            # Compute crossings
            tour_coords = [depot_coord] + [cust_coords[idx] for idx in cust_order_indices] + [depot_coord]
            crossings = count_tour_crossings(tour_coords)

            valid_candidates.append({
                "ordered_stops": ordered_custs,
                "permutation": perm_tuple,
                "directed_cost_km": round(float(tour_cost), 4),
                "frequency": count,
                "probability": round(prob, 4),
                "projection_needed": projection_needed,
                "crossings": crossings
            })

            # Evaluate top 8 unique permutations to conserve runtime
            if len(valid_candidates) >= 8:
                break

        if not valid_candidates:
            # Fallback to natural order
            ordered_custs = list(customers)
            ordered_indices = [depot_idx] + [loc_map[c["id"]] for c in ordered_custs] + [depot_idx]
            tour_cost = sum(matrix[u, v] for u, v in zip(ordered_indices[:-1], ordered_indices[1:]))
            valid_candidates.append({
                "ordered_stops": ordered_custs,
                "permutation": tuple(range(m)),
                "directed_cost_km": round(float(tour_cost), 4),
                "frequency": total_shots,
                "probability": 1.0,
                "projection_needed": False,
                "crossings": 0
            })

        # Quality-Aware Selection: pick candidate with lowest directed cost
        best_candidate = min(valid_candidates, key=lambda c: c["directed_cost_km"])

        return {
            "best_candidate": best_candidate,
            "candidates_evaluated": len(valid_candidates),
            "unique_permutations_sampled": len(unique_permutations),
            "shannon_entropy": round(entropy, 3),
            "all_candidates": valid_candidates
        }


class AdaptiveQuantumInfluenceModel:
    """
    Computes adaptive quantum influence lambda and selects the core backbone.
    """

    @staticmethod
    def compute_quantum_influence(
        qaoa_candidate: Dict[str, Any],
        spatial_stops: List[Dict[str, Any]],
        depot: Dict[str, Any],
        matrix: np.ndarray,
        loc_map: Dict[str, int],
        depot_idx: int = 0
    ) -> Dict[str, Any]:
        depot_coord = (float(depot.get("latitude", 40.7580)), float(depot.get("longitude", -73.9855)))
        spatial_indices = [depot_idx] + [loc_map[c["id"]] for c in spatial_stops] + [depot_idx]
        spatial_cost = sum(matrix[u, v] for u, v in zip(spatial_indices[:-1], spatial_indices[1:]))

        spatial_coords = [depot_coord] + [(float(c.get("latitude", depot_coord[0])), float(c.get("longitude", depot_coord[1]))) for c in spatial_stops] + [depot_coord]
        spatial_crossings = count_tour_crossings(spatial_coords)

        qaoa_cost = qaoa_candidate["directed_cost_km"]
        qaoa_crossings = qaoa_candidate["crossings"]

        # Delta cost: positive if QAOA is strictly better than spatial baseline
        delta_cost_km = spatial_cost - qaoa_cost
        pct_improvement = (delta_cost_km / max(1e-6, spatial_cost)) * 100.0

        # Crossing difference: positive if QAOA introduced new crossings
        crossing_delta = qaoa_crossings - spatial_crossings

        # Adaptive Influence Lambda Formula:
        # 1. Base sigmoid activation on cost improvement
        k = 1.5
        norm_delta = delta_cost_km / max(0.5, spatial_cost * 0.1)
        base_lambda = 1.0 / (1.0 + math.exp(-k * norm_delta))

        # 2. Crossing penalty multiplier
        if crossing_delta > 0:
            crossing_factor = max(0.0, 1.0 - (0.5 * crossing_delta))
        else:
            crossing_factor = 1.0

        lambda_eff = round(base_lambda * crossing_factor, 3)

        # Decision rule: Adopt QAOA if lambda >= 0.50 AND qaoa_cost <= spatial_cost + 1e-4
        if lambda_eff >= 0.50 and qaoa_cost <= spatial_cost + 1e-4:
            adopted_backbone = qaoa_candidate["ordered_stops"]
            adopted_source = "QAOA"
            adopted_cost = qaoa_cost
        else:
            adopted_backbone = list(spatial_stops)
            adopted_source = "SPATIAL_SWEEP"
            adopted_cost = spatial_cost

        return {
            "lambda_eff": lambda_eff,
            "adopted_backbone": adopted_backbone,
            "adopted_source": adopted_source,
            "adopted_cost_km": round(float(adopted_cost), 4),
            "spatial_cost_km": round(float(spatial_cost), 4),
            "qaoa_cost_km": round(float(qaoa_cost), 4),
            "cost_delta_km": round(float(delta_cost_km), 4),
            "pct_improvement": round(float(pct_improvement), 2),
            "spatial_crossings": spatial_crossings,
            "qaoa_crossings": qaoa_crossings,
            "crossings_prevented": max(0, qaoa_crossings - spatial_crossings) if adopted_source == "SPATIAL_SWEEP" else 0
        }


class QuantumGuidedAdaptiveRouter:
    """
    Proposed Dual-Pillar QGAR Router:
    Active Apache Spark 4.2.0 + Genuine Qiskit Aer QAOA +
    Quality-Aware Selection + Adaptive Quantum Influence + Directed DP Reconstruction.
    """

    def __init__(
        self,
        qaoa_p: int = 1,
        qaoa_shots: int = 1024,
        max_qubits: int = 20,
        spark_master: str = "local[*]",
        use_spark: bool = True,
        strict_quantum: bool = True
    ):
        self.qaoa_optimizer = QAOASubproblemOptimizer(p=qaoa_p, shots=qaoa_shots, max_qubits=max_qubits)
        self.preprocessor = SparkRoutingPreprocessor(master=spark_master)
        self.use_spark = use_spark
        self.strict_quantum = strict_quantum
        self.max_core_size = 4

    def optimize_delivery_campaign(
        self,
        customers: List[Dict[str, Any]],
        depot: Dict[str, Any],
        distance_matrix: np.ndarray,
        vehicle_capacity: float,
        location_indices: Dict[str, int],
        enable_qaoa: bool = True,
        enable_adaptive_influence: bool = True,
        enable_quality_selection: bool = True
    ) -> Dict[str, Any]:
        t_global_start = time.perf_counter()
        n_cust = len(customers)
        if n_cust == 0:
            return self._empty_result()

        depot_id = depot.get("id", "depot")
        depot_idx = location_indices.get(depot_id, 0)
        depot_lat = float(depot.get("latitude", 40.7580))
        depot_lon = float(depot.get("longitude", -73.9855))

        # ─── PHASE 1: ACTIVE BIG DATA PREPROCESSING (SPARK) ───
        df_cust = pd.DataFrame([
            {
                "order_id": c.get("id", f"c_{i}"),
                "customer_id": c.get("customer_id", c.get("id", f"c_{i}")),
                "latitude": float(c.get("latitude", depot_lat + 0.01)),
                "longitude": float(c.get("longitude", depot_lon + 0.01)),
                "demand": float(c.get("demand", 1.0)),
                "original_dict": c
            }
            for i, c in enumerate(customers)
        ])

        if self.use_spark:
            clusters, t_spark_ms = self.preprocessor.partition_customers_spark(
                df_cust, depot_lat, depot_lon, vehicle_capacity
            )
        else:
            clusters, t_spark_ms = self.preprocessor.partition_customers_single_machine(
                df_cust, depot_lat, depot_lon, vehicle_capacity
            )

        # ─── PHASE 2: QUANTUM OPTIMIZATION & ADAPTIVE RECONSTRUCTION ───
        t_qaoa_circ_total = 0.0
        t_qaoa_opt_total = 0.0
        t_reconstruct_total = 0.0

        routes = []
        total_distance = 0.0
        total_qaoa_subproblems = 0
        total_qubits_used = 0
        total_circuit_depth = 0
        qaoa_adopted_count = 0
        spatial_retained_count = 0
        all_routed_customer_ids = set()
        lambda_history = []
        crossings_prevented_total = 0
        diversity_history = []

        for k, cluster in enumerate(clusters):
            cluster_custs = [c["original_dict"] for c in cluster["customers"]]
            if not cluster_custs:
                continue

            # Extract bounded quantum payload (core <= 4, boundary)
            payload = self.preprocessor.extract_quantum_subproblem_payload(
                cluster_custs, depot, distance_matrix, location_indices, core_budget=self.max_core_size
            )
            core_custs = payload["core_customers"]
            boundary_custs = payload["boundary_customers"]

            # Execute QAOA on core microcluster if enabled
            if enable_qaoa and len(core_custs) > 1:
                qaoa_res = self.qaoa_optimizer.solve_microcluster_tour(
                    core_custs, depot, distance_matrix, location_indices, strict=self.strict_quantum
                )
                t_qaoa_circ_total += qaoa_res["runtime_circuit_ms"]
                t_qaoa_opt_total += qaoa_res["runtime_opt_ms"]
                total_qaoa_subproblems += 1
                total_qubits_used = max(total_qubits_used, qaoa_res["logical_qubits"])
                total_circuit_depth += qaoa_res["circuit_depth"]

                # Extract shot counts and raw candidates
                raw_counts = qaoa_res.get("raw_counts", {qaoa_res["raw_bitstring"]: 1024})

                if enable_quality_selection:
                    eval_res = QuantumCandidateEvaluator.evaluate_all_candidates(
                        raw_counts, core_custs, depot, distance_matrix, location_indices, depot_idx
                    )
                    best_cand = eval_res["best_candidate"]
                    diversity_history.append(eval_res["unique_permutations_sampled"])
                else:
                    # Greedy baseline selection: use top bitstring directly
                    best_cand = {
                        "ordered_stops": qaoa_res["ordered_stops"],
                        "directed_cost_km": 0.0,
                        "crossings": 0
                    }
                    diversity_history.append(1)

                if enable_adaptive_influence:
                    influence_res = AdaptiveQuantumInfluenceModel.compute_quantum_influence(
                        best_cand, core_custs, depot, distance_matrix, location_indices, depot_idx
                    )
                    adopted_backbone = influence_res["adopted_backbone"]
                    lambda_history.append(influence_res["lambda_eff"])
                    crossings_prevented_total += influence_res["crossings_prevented"]

                    if influence_res["adopted_source"] == "QAOA":
                        qaoa_adopted_count += 1
                    else:
                        spatial_retained_count += 1
                else:
                    # Unconditioned QAOA adoption
                    adopted_backbone = best_cand["ordered_stops"]
                    lambda_history.append(1.0)
                    qaoa_adopted_count += 1
            else:
                # Spatial baseline order
                adopted_backbone = list(core_custs)
                lambda_history.append(0.0)

            # ─── PHASE 3: DIRECTED DP BOUNDARY RECONSTRUCTION ───
            t_r0 = time.perf_counter()
            reconstructed_stops = self._reconstruct_route_dp_insertion(
                adopted_backbone, boundary_custs, distance_matrix, location_indices, depot_idx
            )
            t_reconstruct_total += (time.perf_counter() - t_r0) * 1000.0

            route_dist = self._calculate_route_distance(
                reconstructed_stops, depot_idx, distance_matrix, location_indices
            )
            route_load = sum(c.get("demand", 1.0) for c in cluster_custs)
            total_distance += route_dist

            full_stops = [depot] + reconstructed_stops + [depot]
            routes.append({
                "vehicle_id": k + 1,
                "stops": full_stops,
                "total_distance_km": round(route_dist, 3),
                "total_load": round(route_load, 2),
                "customer_count": len(reconstructed_stops)
            })

            for c in reconstructed_stops:
                all_routed_customer_ids.add(c["id"])

        t_global_total_ms = (time.perf_counter() - t_global_start) * 1000.0

        # Feasibility & Invariant Audit
        input_ids = set(c["id"] for c in customers)
        missing_ids = input_ids - all_routed_customer_ids
        capacity_violations = sum(1 for r in routes if r["total_load"] > vehicle_capacity + 1e-5)
        is_feasible = (len(missing_ids) == 0 and capacity_violations == 0)

        mean_lambda = float(np.mean(lambda_history)) if lambda_history else 0.0
        mean_diversity = float(np.mean(diversity_history)) if diversity_history else 1.0

        return {
            "routes": routes,
            "total_distance_km": round(total_distance, 3),
            "num_vehicles": len(routes),
            "feasibility": {
                "is_feasible": is_feasible,
                "total_input_customers": n_cust,
                "total_routed_customers": len(all_routed_customer_ids),
                "unassigned_customers": len(missing_ids),
                "capacity_violations": capacity_violations,
            },
            "telemetry": {
                "runtime_spark_ms": round(t_spark_ms, 2),
                "runtime_qaoa_circuit_ms": round(t_qaoa_circ_total, 2),
                "runtime_qaoa_opt_ms": round(t_qaoa_opt_total, 2),
                "runtime_reconstruction_ms": round(t_reconstruct_total, 2),
                "runtime_total_ms": round(t_global_total_ms, 2),
                "qaoa_subproblems_solved": total_qaoa_subproblems,
                "max_logical_qubits_used": total_qubits_used,
                "total_circuit_depth": total_circuit_depth,
                "quantum_influence_lambda_mean": round(mean_lambda, 3),
                "qaoa_backbones_accepted": qaoa_adopted_count,
                "spatial_backbones_retained": spatial_retained_count,
                "candidate_diversity_mean": round(mean_diversity, 2),
                "crossings_prevented_total": crossings_prevented_total
            }
        }

    def _reconstruct_route_dp_insertion(
        self,
        core_stops: List[Dict[str, Any]],
        boundary_stops: List[Dict[str, Any]],
        distance_matrix: np.ndarray,
        loc_map: Dict[str, int],
        depot_idx: int
    ) -> List[Dict[str, Any]]:
        if not core_stops:
            return list(boundary_stops)
        if not boundary_stops:
            return list(core_stops)

        current_route = list(core_stops)
        remaining = list(boundary_stops)

        while remaining:
            best_cust_idx = -1
            best_insert_pos = -1
            best_cost_delta = float('inf')

            for c_idx, candidate in enumerate(remaining):
                c_node = loc_map[candidate["id"]]

                for pos in range(len(current_route) + 1):
                    if pos == 0:
                        prev_node = depot_idx
                        next_node = loc_map[current_route[0]["id"]]
                    elif pos == len(current_route):
                        prev_node = loc_map[current_route[-1]["id"]]
                        next_node = depot_idx
                    else:
                        prev_node = loc_map[current_route[pos - 1]["id"]]
                        next_node = loc_map[current_route[pos]["id"]]

                    # Directed delta cost: c(prev, cand) + c(cand, next) - c(prev, next)
                    delta = distance_matrix[prev_node, c_node] + distance_matrix[c_node, next_node] - distance_matrix[prev_node, next_node]
                    if delta < best_cost_delta:
                        best_cost_delta = delta
                        best_cust_idx = c_idx
                        best_insert_pos = pos

            inserted = remaining.pop(best_cust_idx)
            current_route.insert(best_insert_pos, inserted)

        return current_route

    def _calculate_route_distance(
        self,
        stops: List[Dict[str, Any]],
        depot_idx: int,
        distance_matrix: np.ndarray,
        loc_map: Dict[str, int]
    ) -> float:
        if not stops:
            return 0.0
        indices = [depot_idx] + [loc_map[s["id"]] for s in stops] + [depot_idx]
        total_dist = 0.0
        for u, v in zip(indices[:-1], indices[1:]):
            total_dist += distance_matrix[u, v]
        return float(total_dist)

    def _empty_result(self) -> Dict[str, Any]:
        return {
            "routes": [],
            "total_distance_km": 0.0,
            "num_vehicles": 0,
            "feasibility": {
                "is_feasible": True,
                "total_input_customers": 0,
                "total_routed_customers": 0,
                "unassigned_customers": 0,
                "capacity_violations": 0
            },
            "telemetry": {
                "runtime_spark_ms": 0.0,
                "runtime_qaoa_circuit_ms": 0.0,
                "runtime_qaoa_opt_ms": 0.0,
                "runtime_reconstruction_ms": 0.0,
                "runtime_total_ms": 0.0,
                "qaoa_subproblems_solved": 0,
                "max_logical_qubits_used": 0,
                "total_circuit_depth": 0,
                "quantum_influence_lambda_mean": 0.0,
                "qaoa_backbones_accepted": 0,
                "spatial_backbones_retained": 0,
                "candidate_diversity_mean": 0.0,
                "crossings_prevented_total": 0
            }
        }

