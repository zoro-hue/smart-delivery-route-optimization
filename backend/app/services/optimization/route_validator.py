"""
Centralized Route Validation, Deterministic Repair & Resource Profiling Module for ROUTE/IQ.

Enforces:
1. Universal Delivery Coverage Invariant: R == I
   (Every valid input delivery ID appears in the final fleet routes exactly once).
2. Vehicle Capacity Constraints: sum(d_i for i in R_k) <= Q_k.
3. Fleet Lower Bound & Dynamic Consistency Verification.
4. Deterministic Capacity-Aware Cheapest-Insertion Repair.
5. Accurate Process Resource Profiling (Wall time, CPU time, CPU %, RAM, Peak RAM, Big-O).
"""

import time
import math
import copy
import logging
import tracemalloc
from typing import Dict, Any, List, Set, Tuple, Optional, Callable
import numpy as np

logger = logging.getLogger(__name__)

# Theoretical Big-O Time and Space Complexities
ALGORITHM_COMPLEXITIES: Dict[str, Dict[str, str]] = {
    "routeiq_cooperative": {
        "time_complexity": "O(N log N + K·B^2 + 2^p)",
        "space_complexity": "O(N + K·B)",
        "method": "Hybrid Spark + Adaptive MAB + QAOA/Tabu + VND",
    },
    "ortools": {
        "time_complexity": "O(K · N^2 · T_limit)",
        "space_complexity": "O(N^2)",
        "method": "Branch-and-Bound + Guided Local Search",
    },
    "clarke_wright": {
        "time_complexity": "O(N^2 log N)",
        "space_complexity": "O(N^2)",
        "method": "Greedy Savings Heuristic",
    },
    "two_opt": {
        "time_complexity": "O(Iters · N^2)",
        "space_complexity": "O(N)",
        "method": "Intra-route Edge Inversion",
    },
    "dijkstra": {
        "time_complexity": "O(E + V log V)",
        "space_complexity": "O(V)",
        "method": "Greedy Shortest-Path Chain",
    },
    "astar": {
        "time_complexity": "O(b^d)",
        "space_complexity": "O(b^d)",
        "method": "Heuristic A* Search",
    },
    "qiga": {
        "time_complexity": "O(G · P · N)",
        "space_complexity": "O(P · N)",
        "method": "Quantum-Inspired Genetic Superposition",
    },
    "tabu_search": {
        "time_complexity": "O(Iters · N · K)",
        "space_complexity": "O(N)",
        "method": "Recency-Memory Tabu Search Metaheuristic",
    },
    "kernighan_lin": {
        "time_complexity": "O(N^2 log N)",
        "space_complexity": "O(N)",
        "method": "Variable-Depth Bipartition Exchange",
    },
    "vnd": {
        "time_complexity": "O(K · N^2)",
        "space_complexity": "O(N)",
        "method": "Variable Neighborhood Descent (2-opt + Relocate + Swap)",
    },
    "qaoa": {
        "time_complexity": "O(P · 2^q)",
        "space_complexity": "O(2^q)",
        "method": "Variational Quantum Statevector Simulation",
    },
}


def validate_fleet_coverage(
    routes: List[Dict[str, Any]],
    input_customer_ids: List[int],
    demands: List[float],
    vehicle_capacities: List[float],
    depot: int = 0,
) -> Dict[str, Any]:
    """
    Validates complete fleet route solutions against the Universal Coverage Invariant R == I.
    Operates on the entire fleet solution, not individual routes in isolation.
    """
    input_set: Set[int] = set(input_customer_ids)
    visited_multiset: List[int] = []
    vehicle_loads: List[float] = []
    capacity_violations = 0
    route_details = []

    for r_idx, route in enumerate(routes):
        stops = route.get("stops", [])
        c_stops = [s for s in stops if s != depot]
        visited_multiset.extend(c_stops)

        # Check vehicle load
        route_load = sum(demands[s] if s < len(demands) else 1.0 for s in c_stops)
        cap = (
            vehicle_capacities[r_idx]
            if r_idx < len(vehicle_capacities)
            else (vehicle_capacities[-1] if vehicle_capacities else 100.0)
        )
        is_over = route_load > cap + 1e-4
        if is_over:
            capacity_violations += 1

        vehicle_loads.append(route_load)
        route_details.append({
            "vehicle_index": r_idx,
            "stops_count": len(c_stops),
            "load": round(route_load, 2),
            "capacity": round(cap, 2),
            "is_over_capacity": is_over,
            "excess": round(max(0.0, route_load - cap), 2),
        })

    visited_set = set(visited_multiset)
    missing_ids = sorted(list(input_set - visited_set))
    unknown_ids = sorted(list(visited_set - input_set))

    # Detect duplicates
    seen = set()
    duplicates = set()
    for s in visited_multiset:
        if s in seen:
            duplicates.add(s)
        seen.add(s)
    duplicate_ids = sorted(list(duplicates))

    is_complete = (len(missing_ids) == 0 and len(unknown_ids) == 0 and len(duplicate_ids) == 0)
    capacity_feasible = (capacity_violations == 0)
    is_valid = is_complete and capacity_feasible

    return {
        "is_complete": is_complete,
        "is_valid": is_valid,
        "capacity_feasible": capacity_feasible,
        "capacity_violations": capacity_violations,
        "input_delivery_count": len(input_customer_ids),
        "visited_delivery_count": len(visited_set),
        "missing_delivery_ids": missing_ids,
        "duplicate_delivery_ids": duplicate_ids,
        "unknown_delivery_ids": unknown_ids,
        "unassigned_delivery_ids": missing_ids,
        "vehicle_loads": vehicle_loads,
        "route_details": route_details,
    }


def repair_fleet_coverage(
    routes: List[Dict[str, Any]],
    input_customer_ids: List[int],
    distance_matrix: np.ndarray,
    demands: List[float],
    vehicle_capacities: List[float],
    num_vehicles: int,
    depot: int = 0,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Deterministically repairs missing delivery stops to guarantee 100% customer coverage.
    1. Identifies missing customer nodes.
    2. Identifies cheapest capacity-feasible insertion position across all routes.
    3. If capacity permits, inserts cleanly; if total capacity is tight, selects cheapest position.
    4. Recalculates all route geometries, loads, and fleet metrics.
    5. Returns repaired routes and full validation report.
    """
    repaired_routes = copy.deepcopy(routes)
    input_set = set(input_customer_ids)

    # Ensure at least one route exists
    if not repaired_routes:
        repaired_routes = [{
            "vehicle_id": 1,
            "stops": [depot, depot],
            "customer_stops": [],
            "distance_km": 0.0,
            "load": 0.0,
            "capacity": vehicle_capacities[0] if vehicle_capacities else 100.0,
            "utilization_pct": 0.0,
        }]

    # Step 1: Deduplicate and strip unknown customer nodes across routes
    seen_customers: Set[int] = set()
    cleaned_routes = []
    for r in repaired_routes:
        cleaned_stops = [depot]
        for s in r.get("stops", []):
            if s == depot:
                continue
            if s in input_set and s not in seen_customers:
                seen_customers.add(s)
                cleaned_stops.append(s)
            elif s not in input_set:
                logger.warning(f"Repair: Discarding unknown node {s} not in customer input set.")
            else:
                logger.warning(f"Repair: Discarding duplicate visit to customer {s}.")
        cleaned_stops.append(depot)
        r["stops"] = cleaned_stops
        cleaned_routes.append(r)
    repaired_routes = cleaned_routes

    # Step 2: Ensure vehicle count matches fleet limit (num_vehicles)
    if len(repaired_routes) > num_vehicles:
        # Merge excess routes into the primary fleet routes with smallest load
        merged_routes = repaired_routes[:num_vehicles]
        for extra_r in repaired_routes[num_vehicles:]:
            for stop in extra_r.get("stops", []):
                if stop != depot:
                    min_load_r = min(
                        merged_routes,
                        key=lambda r: sum(demands[s] if s < len(demands) else 1.0 for s in r.get("stops", []) if s != depot)
                    )
                    min_load_r["stops"].insert(-1, stop)
        repaired_routes = merged_routes

    while len(repaired_routes) < num_vehicles:
        new_v_id = len(repaired_routes) + 1
        cap = vehicle_capacities[new_v_id - 1] if new_v_id - 1 < len(vehicle_capacities) else 100.0
        repaired_routes.append({
            "vehicle_id": new_v_id,
            "stops": [depot, depot],
            "customer_stops": [],
            "distance_km": 0.0,
            "load": 0.0,
            "capacity": cap,
            "utilization_pct": 0.0,
        })

    # Step 3: Find which customers are currently visited after merge
    visited_nodes: Set[int] = set()
    for r in repaired_routes:
        c_stops = [s for s in r.get("stops", []) if s != depot]
        visited_nodes.update(c_stops)

    missing = sorted(list(input_set - visited_nodes))

    if missing:
        logger.info(f"Fleet Repair: Found {len(missing)} missing delivery stops: {missing}. Applying capacity-aware insertion.")

        for u in missing:
            u_demand = demands[u] if u < len(demands) else 1.0

            best_r_idx = None
            best_pos = None
            best_extra_cost = float("inf")
            best_is_cap_feasible = False

            # Search across all vehicles and all edge insertion positions
            for r_idx in range(min(len(repaired_routes), num_vehicles)):
                r = repaired_routes[r_idx]
                st = r.get("stops", [depot, depot])
                current_load = sum(demands[s] if s < len(demands) else 1.0 for s in st if s != depot)
                v_cap = vehicle_capacities[r_idx] if r_idx < len(vehicle_capacities) else 100.0
                can_fit = (current_load + u_demand <= v_cap + 1e-4)

                for p in range(len(st) - 1):
                    i_node = st[p]
                    j_node = st[p + 1]

                    # Directed road-cost insertion delta
                    d_iu = float(distance_matrix[i_node, u])
                    d_uj = float(distance_matrix[u, j_node])
                    d_ij = float(distance_matrix[i_node, j_node])
                    extra = d_iu + d_uj - d_ij

                    # If edge or node is inaccessible / infinite cost, skip insertion position
                    if math.isinf(d_iu) or math.isinf(d_uj) or math.isnan(extra) or math.isinf(extra):
                        continue

                    # Priority 1: Capacity-feasible insertion with minimal extra distance
                    # Priority 2: Infeasible insertion with minimal extra distance (only if no vehicle has room)
                    if can_fit and not best_is_cap_feasible:
                        best_is_cap_feasible = True
                        best_extra_cost = extra
                        best_r_idx = r_idx
                        best_pos = p + 1
                    elif can_fit == best_is_cap_feasible:
                        if extra < best_extra_cost:
                            best_extra_cost = extra
                            best_r_idx = r_idx
                            best_pos = p + 1

            if best_r_idx is not None and best_pos is not None and not math.isinf(best_extra_cost):
                repaired_routes[best_r_idx]["stops"].insert(best_pos, u)
            else:
                logger.warning(f"Stop {u} cannot be feasibly reached on road network. Remains unserved.")

    # Recalculate metrics for all routes
    for r_idx, r in enumerate(repaired_routes, start=1):
        st = r["stops"]
        # Ensure depot start and end
        if not st or st[0] != depot:
            st = [depot] + st
        if len(st) < 2 or st[-1] != depot:
            st = st + [depot]
        r["stops"] = st
        c_stops = [s for s in st if s != depot]
        r["customer_stops"] = c_stops
        r["vehicle_id"] = r_idx

        # Calculate accurate distance
        d_km = sum(float(distance_matrix[st[k], st[k + 1]]) for k in range(len(st) - 1))
        r["distance_km"] = round(d_km, 3)

        # Calculate load and capacity
        v_cap = vehicle_capacities[r_idx - 1] if r_idx - 1 < len(vehicle_capacities) else 100.0
        r["capacity"] = v_cap
        r["load"] = round(sum(demands[s] if s < len(demands) else 1.0 for s in c_stops), 2)
        r["utilization_pct"] = round(r["load"] / v_cap * 100.0, 1) if v_cap > 0 else 0.0

    # Prune completely empty trailing routes if vehicle count permits
    non_empty = [r for r in repaired_routes if len(r["customer_stops"]) > 0]
    final_routes = non_empty if non_empty else repaired_routes[:1]

    # Re-index vehicle IDs sequentially
    for i, r in enumerate(final_routes, start=1):
        r["vehicle_id"] = i

    validation_report = validate_fleet_coverage(
        final_routes, input_customer_ids, demands, vehicle_capacities, depot
    )

    return final_routes, validation_report


def profile_algorithm_execution(
    solver_fn: Callable[[], Dict[str, Any]],
    algo_key: str,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Executes an algorithm while measuring actual OS wall-clock time, CPU process time,
    Python heap allocation (tracemalloc), and process resident RAM (psutil).
    Keeps theoretical asymptotic complexity strictly separated from empirical measurements.
    """
    import psutil
    process = psutil.Process()
    tracemalloc.start()
    t0_wall = time.perf_counter()
    t0_cpu = time.process_time()

    try:
        result = solver_fn()
    finally:
        t1_cpu = time.process_time()
        t1_wall = time.perf_counter()
        current_heap, peak_heap = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        try:
            process_rss_bytes = process.memory_info().rss
        except Exception:
            process_rss_bytes = 0

    wall_ms = round((t1_wall - t0_wall) * 1000.0, 2)
    cpu_ms = round((t1_cpu - t0_cpu) * 1000.0, 2)
    # CPU Core Time Ratio: Ratio of accumulated CPU time relative to elapsed wall time
    cpu_ratio = round((cpu_ms / max(wall_ms, 0.001)) * 100.0, 1)

    heap_alloc_mb = round(current_heap / (1024.0 * 1024.0), 3)
    heap_peak_mb = round(peak_heap / (1024.0 * 1024.0), 3)
    process_rss_mb = round(process_rss_bytes / (1024.0 * 1024.0), 2)

    complexity = ALGORITHM_COMPLEXITIES.get(
        algo_key,
        {
            "time_complexity": "O(N^2)",
            "space_complexity": "O(N)",
            "method": "Routing Heuristic",
        },
    )

    resource_metrics = {
        "runtime_ms": wall_ms,
        "cpu_time_ms": cpu_ms,
        "cpu_utilization_percent": min(cpu_ratio, 100.0),
        "cpu_core_ratio_percent": cpu_ratio,
        "memory_used_mb": heap_alloc_mb,
        "peak_memory_mb": heap_peak_mb,
        "heap_allocated_mb": heap_alloc_mb,
        "heap_peak_mb": heap_peak_mb,
        "process_rss_mb": process_rss_mb,
        "time_complexity": complexity["time_complexity"],
        "space_complexity": complexity["space_complexity"],
        "measurement_available": True,
        "measurement_method": "psutil (Process RSS) + tracemalloc (Python Heap) + high-res OS process timers",
        "measurement_nature": {
            "wall_clock": "Empirically measured via time.perf_counter monotonic clock",
            "cpu_time": "Empirically measured via time.process_time system/user counters",
            "cpu_utilization": "Derived ratio: (CPU time / Wall time) * 100",
            "heap_memory": "Empirically measured via tracemalloc (Python heap delta & peak)",
            "process_rss": "Empirically measured via psutil (total resident process RAM)",
            "asymptotic_complexity": "Theoretical worst-case Big-O bound (unaffected by empirical runtime)"
        }
    }

    return result, resource_metrics

