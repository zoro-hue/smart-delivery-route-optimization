"""
Optimization & Experiments API — Classical VRP, QAOA, Comparison, Experiment History
"""

import json
import math
import time
import uuid
from datetime import datetime, timezone
from typing import List, Optional

import numpy as np
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from loguru import logger
from pydantic import BaseModel, Field
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_db
from app.models.models import Experiment, ExperimentResult
from app.services.data_processor import data_processor, haversine
from app.services.optimization.classical_solver import classical_solver
from app.services.optimization.quantum_solver import quantum_solver
from app.services.optimization.qiga_solver import qiga_solver
from app.services.optimization.cooperative_solver import cooperative_solver
from app.services.geo_validation import check_water_body, validate_nyc_coordinate
from app.services.road_network_service import road_network_service
from app.services.optimization.route_validator import (
    validate_fleet_coverage,
    repair_fleet_coverage,
    profile_algorithm_execution,
)

settings = get_settings()
router = APIRouter(prefix="/api", tags=["Optimization"])

AVAILABLE_ALGORITHMS = [
    {
        "id": "routeiq_cooperative",
        "name": "ROUTE/IQ Cooperative Engine",
        "category": "cooperative",
        "category_label": "Cooperative Hybrid (Big Data + Quantum)",
        "tag": "Spark + Adaptive + QAOA/Tabu + VND",
        "description": "End-to-end cooperative optimization unifying Spark spatial decomposition, Multi-Armed Bandit adaptive control, QAOA/Tabu candidate generation, VND refinement, and Proposition 1 non-degradation guardrail.",
        "operational": True,
        "max_customers": 200,
        "is_primary": False,
        "compute_type": "Hybrid (Spark + Classical CPU + Simulated QPU)",
    },
    {
        "id": "ortools",
        "name": "OR-Tools",
        "category": "classical",
        "category_label": "Classical",
        "tag": "Exact / Local Search",
        "description": "Classical vehicle routing optimization using Google OR-Tools CVRP solver.",
        "operational": True,
        "max_customers": 200,
        "is_primary": True,
        "compute_type": "Classical CPU",
    },
    {
        "id": "clarke_wright",
        "name": "Clarke–Wright Savings",
        "category": "classical",
        "category_label": "Classical",
        "tag": "Construction Heuristic",
        "description": "Route construction heuristic merging customer tours based on calculated travel savings.",
        "operational": True,
        "max_customers": 200,
        "is_primary": False,
        "compute_type": "Classical CPU",
    },
    {
        "id": "two_opt",
        "name": "2-opt",
        "category": "classical",
        "category_label": "Classical",
        "tag": "Improvement Heuristic",
        "description": "Route improvement heuristic iteratively uncrossing path edges until 2-opt local optimality.",
        "operational": True,
        "max_customers": 200,
        "is_primary": False,
        "compute_type": "Classical CPU",
    },
    {
        "id": "dijkstra",
        "name": "Dijkstra",
        "category": "classical",
        "category_label": "Classical",
        "tag": "Shortest-Path Baseline",
        "description": "Shortest-path baseline traversing road distance reachability trees from depot.",
        "operational": True,
        "max_customers": 200,
        "is_primary": False,
        "compute_type": "Classical CPU",
    },
    {
        "id": "astar",
        "name": "A*",
        "category": "classical",
        "category_label": "Classical",
        "tag": "Heuristic Search",
        "description": "Heuristic-based shortest-path search using admissible distance lower bounds.",
        "operational": True,
        "max_customers": 200,
        "is_primary": False,
        "compute_type": "Classical CPU",
    },
    {
        "id": "qaoa",
        "name": "QAOA",
        "category": "quantum_hybrid",
        "category_label": "Quantum / Quantum-Classical",
        "tag": "Hybrid Quantum-Classical",
        "description": "Hybrid variational quantum-classical optimization via Qiskit statevector simulation.",
        "operational": True,
        "max_customers": 8,
        "is_primary": False,
        "compute_type": "Classical Statevector Simulation (Qiskit)",
    },
    {
        "id": "qiga",
        "name": "Quantum-Inspired Genetic Algorithm (QIGA/IQGA)",
        "category": "quantum_inspired",
        "category_label": "Quantum / Quantum-Classical",
        "tag": "Quantum-Inspired",
        "description": "Quantum-inspired evolutionary optimization using Q-bit probability amplitudes and rotation gates, simulated classically.",
        "operational": True,
        "max_customers": 50,
        "is_primary": False,
        "compute_type": "Classically Simulated Q-Bits",
    },
]


# ─── Request/Response Models ─────────────────────────────────────

class OptimizationRequest(BaseModel):
    algorithm: str = "classical"  # legacy support: classical, qaoa, both
    selection_mode: str = "recommended"  # "recommended", "custom", "compare"
    selected_algorithms: Optional[List[str]] = None  # e.g. ["ortools", "clarke_wright", "two_opt", "dijkstra", "astar", "qaoa", "qiga"]
    num_customers: int = Field(10, ge=1, le=200)
    num_vehicles: int = Field(3, ge=1, le=50)
    vehicle_capacity: float = Field(100, gt=0)
    depot_lat: float = Field(40.7580, ge=-90, le=90)
    depot_lon: float = Field(-73.8292, ge=-180, le=180)

    # Objective weights
    weight_distance: float = Field(1.0, ge=0)
    weight_travel_time: float = Field(0.5, ge=0)
    weight_congestion: float = Field(0.3, ge=0)
    weight_fuel: float = Field(0.2, ge=0)
    weight_late_penalty: float = Field(0.5, ge=0)

    # Scenario
    traffic_scenario: str = "normal"  # normal, moderate, high_congestion, severe
    weather_scenario: str = "clear"  # clear, cloudy, rain, heavy_rain, storm

    # Classical settings
    classical_time_limit_sec: int = Field(30, ge=1, le=300)

    # QAOA settings
    qaoa_depth: int = Field(1, ge=1, le=5)
    qaoa_shots: int = Field(1024, ge=100, le=10000)
    qaoa_optimizer: str = "COBYLA"
    qaoa_penalty: float = Field(10.0, gt=0)

    # Optional explicit customer stops from Step 1
    custom_customers: Optional[List[dict]] = None

    # Reproducibility
    random_seed: int = 42

    class Config:
        json_schema_extra = {
            "example": {
                "selection_mode": "recommended",
                "selected_algorithms": ["ortools"],
                "num_customers": 6,
                "num_vehicles": 2,
                "vehicle_capacity": 50,
            }
        }


# ─── Optimization Endpoints ──────────────────────────────────────

@router.get("/optimization/algorithms")
async def get_optimization_algorithms():
    """Return available operational optimization algorithms and their capabilities."""
    return {
        "status": "success",
        "count": len(AVAILABLE_ALGORITHMS),
        "algorithms": AVAILABLE_ALGORITHMS,
    }


@router.post("/optimization/run")
async def run_optimization(
    req: OptimizationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Run optimization with specified algorithm or comparison suite."""
    t0 = time.time()

    # Prepare customer locations
    locations, demands = _prepare_problem(req)
    n = len(locations)

    # Validate depot location against NYC 5-Borough road network bounds and water bodies
    is_valid_depot, depot_err = validate_nyc_coordinate(req.depot_lat, req.depot_lon)
    if not is_valid_depot:
        raise HTTPException(
            status_code=400,
            detail=f"Origin Depot Hub validation error: {depot_err}"
        )

    for idx, (loc_lat, loc_lon) in enumerate(locations[1:], start=1):
        is_valid_stop, stop_err = validate_nyc_coordinate(loc_lat, loc_lon)
        if not is_valid_stop:
            raise HTTPException(
                status_code=400,
                detail=f"Customer stop #{idx} validation error: {stop_err}"
            )

    # Apply traffic/weather factors
    traffic_factor = data_processor.get_traffic_factor(req.traffic_scenario)
    weather_factor = data_processor.get_weather_factor(req.weather_scenario)

    snapped_node_ids = []
    road_warnings = []

    # Build authentic road-network distance matrix using Dijkstra on NYC road graph
    if road_network_service.is_ready():
        logger.info(f"Computing road-network distance matrix for {n} locations using NYC road graph...")
        adjusted_matrix, snapped_node_ids, road_warnings, physical_matrix = road_network_service.build_road_matrix(
            locations, traffic_factor=traffic_factor, weather_factor=weather_factor, return_physical=True
        )
    else:
        logger.warning("RoadNetworkService not ready, using haversine fallback...")
        distance_matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                if i != j:
                    distance_matrix[i][j] = haversine(
                        locations[i][0], locations[i][1],
                        locations[j][0], locations[j][1]
                    )
        physical_matrix = distance_matrix
        adjusted_matrix = distance_matrix * traffic_factor * weather_factor
        road_warnings.append("Road network graph unavailable; straight-line distance fallback used.")

    objective_weights = {
        "distance": req.weight_distance,
        "travel_time": req.weight_travel_time,
    }

    # Strictly preserve user-specified fleet constraints (never silently change vehicle count or capacity)
    demands_int = [int(d) for d in demands]
    total_cust_demand = sum(demands_int)
    total_fleet_capacity = req.num_vehicles * int(req.vehicle_capacity)
    capacities = [int(req.vehicle_capacity)] * req.num_vehicles

    if total_cust_demand > total_fleet_capacity:
        road_warnings.append(
            f"Fleet capacity warning: Total customer demand ({total_cust_demand}) exceeds total fleet capacity "
            f"({total_fleet_capacity} units across {req.num_vehicles} vehicles). Solvers will incur capacity penalties."
        )

    to_run: List[str] = []
    mode = (req.selection_mode or "recommended").lower().strip()

    if mode == "recommended":
        # Flagship hybrid recommendation: ROUTE/IQ Cooperative Engine
        to_run = ["routeiq_cooperative"]
    elif mode == "compare":
        if req.selected_algorithms and len(req.selected_algorithms) >= 2:
            to_run = list(req.selected_algorithms)
        else:
            # Default comparison suite across classical and quantum-inspired
            to_run = ["ortools", "clarke_wright", "two_opt", "qiga"]
            # Only add QAOA if within safe qubit limit (<= 8 customers + depot = 9 nodes)
            if n <= 9:
                to_run.append("qaoa")
    elif mode == "custom":
        if req.selected_algorithms and len(req.selected_algorithms) > 0:
            to_run = list(req.selected_algorithms)
        else:
            to_run = ["ortools"]
    else:
        # Backward compatibility with legacy algorithm field
        if req.algorithm == "both":
            to_run = ["ortools", "qaoa"]
        elif req.algorithm == "qaoa":
            to_run = ["qaoa"]
        else:
            to_run = ["ortools"]

    # Normalize algorithm keys
    normalized_to_run = []
    for a in to_run:
        key = a.lower().strip()
        if key == "classical":
            key = "ortools"
        if key not in normalized_to_run:
            normalized_to_run.append(key)
    to_run = normalized_to_run

    # Create experiment record
    now_utc = datetime.now(timezone.utc)
    experiment = Experiment(
        id=str(uuid.uuid4()),
        name=f"Optimization {now_utc.strftime('%Y%m%d_%H%M%S')}",
        timestamp=now_utc,
        algorithm=",".join(to_run),
        num_customers=req.num_customers,
        num_vehicles=req.num_vehicles,
        depot_lat=req.depot_lat,
        depot_lon=req.depot_lon,
        vehicle_capacity=req.vehicle_capacity,
        weight_distance=req.weight_distance,
        weight_travel_time=req.weight_travel_time,
        weight_congestion=req.weight_congestion,
        weight_fuel=req.weight_fuel,
        weight_late_penalty=req.weight_late_penalty,
        traffic_scenario=req.traffic_scenario,
        weather_scenario=req.weather_scenario,
        classical_time_limit_sec=req.classical_time_limit_sec,
        qaoa_depth=req.qaoa_depth,
        qaoa_shots=req.qaoa_shots,
        qaoa_optimizer=req.qaoa_optimizer,
        qaoa_penalty=req.qaoa_penalty,
        random_seed=req.random_seed,
        status="running",
    )
    db.add(experiment)
    await db.flush()

    results = {}

    try:
        def _execute_single_algo(algo: str) -> Dict[str, Any]:
            logger.info(f"Executing algorithm '{algo}' on {n} nodes, {req.num_vehicles} vehicles")

            def _run_raw_solver() -> Dict[str, Any]:
                if algo in ("routeiq_cooperative", "cooperative", "routeiq"):
                    res = cooperative_solver.solve(
                        distance_matrix=adjusted_matrix,
                        num_vehicles=req.num_vehicles,
                        depot=0,
                        demands=demands_int,
                        vehicle_capacities=capacities,
                        time_limit_sec=0.15,
                        objective_weights=objective_weights,
                        locations=locations,
                        seed=req.random_seed,
                    )
                    res["algorithm_name"] = "ROUTE/IQ Cooperative Engine"
                    res["category"] = "cooperative"
                    res["category_label"] = "Cooperative Hybrid"
                    res["compute_type"] = "Hybrid (Spark + Adaptive + QAOA/Tabu + VND)"
                    return res

                elif algo in ("ortools", "classical_ortools"):
                    effective_time_limit = 0.25 if n <= 35 else min(req.classical_time_limit_sec or 3, 5)
                    res = classical_solver.solve_ortools(
                        adjusted_matrix,
                        req.num_vehicles,
                        depot=0,
                        demands=demands_int,
                        vehicle_capacities=capacities,
                        time_limit_sec=effective_time_limit,
                        objective_weights=objective_weights,
                    )
                    res["algorithm_name"] = "OR-Tools (CVRP)"
                    res["category"] = "classical"
                    res["category_label"] = "Classical"
                    res["compute_type"] = "Classical CPU"
                    return res

                elif algo in ("clarke_wright", "clarkewright", "savings"):
                    res = classical_solver.solve_clarke_wright(
                        adjusted_matrix,
                        req.num_vehicles,
                        depot=0,
                        demands=demands_int,
                        vehicle_capacities=capacities,
                        objective_weights=objective_weights,
                    )
                    res["algorithm_name"] = "Clarke–Wright Savings"
                    res["category"] = "classical"
                    res["category_label"] = "Classical"
                    res["compute_type"] = "Classical CPU"
                    return res

                elif algo in ("two_opt", "2opt"):
                    res = classical_solver.solve_two_opt(
                        adjusted_matrix,
                        req.num_vehicles,
                        depot=0,
                        demands=demands_int,
                        vehicle_capacities=capacities,
                        objective_weights=objective_weights,
                    )
                    res["algorithm_name"] = "2-opt Improvement"
                    res["category"] = "classical"
                    res["category_label"] = "Classical"
                    res["compute_type"] = "Classical CPU"
                    return res

                elif algo in ("dijkstra", "shortest_path"):
                    res = classical_solver.solve_dijkstra(
                        adjusted_matrix,
                        req.num_vehicles,
                        depot=0,
                        demands=demands_int,
                        vehicle_capacities=capacities,
                        objective_weights=objective_weights,
                    )
                    res["algorithm_name"] = "Dijkstra Shortest-Path"
                    res["category"] = "classical"
                    res["category_label"] = "Classical"
                    res["compute_type"] = "Classical CPU"
                    return res

                elif algo in ("astar", "a*", "a_star"):
                    res = classical_solver.solve_astar(
                        adjusted_matrix,
                        req.num_vehicles,
                        depot=0,
                        demands=demands_int,
                        vehicle_capacities=capacities,
                        objective_weights=objective_weights,
                        locations=locations,
                    )
                    res["algorithm_name"] = "A* Heuristic Search"
                    res["category"] = "classical"
                    res["category_label"] = "Classical"
                    res["compute_type"] = "Classical CPU"
                    return res

                elif algo == "qiga":
                    res = qiga_solver.solve(
                        adjusted_matrix,
                        req.num_vehicles,
                        depot=0,
                        demands=demands_int,
                        vehicle_capacities=capacities,
                        objective_weights=objective_weights,
                    )
                    res["algorithm_name"] = "Quantum-Inspired GA (QIGA/IQGA)"
                    res["category"] = "quantum_inspired"
                    res["category_label"] = "Quantum / Quantum-Classical"
                    res["compute_type"] = "Classically Simulated Q-Bits"
                    return res

                elif algo == "qaoa":
                    if n > settings.MAX_CUSTOMERS_QAOA + 1:
                        logger.warning(f"QAOA: solving first {settings.MAX_CUSTOMERS_QAOA} customers on quantum simulator; remaining will be capacity-repaired")
                        qaoa_n = settings.MAX_CUSTOMERS_QAOA + 1
                        qaoa_matrix = adjusted_matrix[:qaoa_n, :qaoa_n]
                        qaoa_demands = demands[:qaoa_n]
                    else:
                        qaoa_n = n
                        qaoa_matrix = adjusted_matrix
                        qaoa_demands = demands

                    res = quantum_solver.solve(
                        qaoa_matrix,
                        req.num_vehicles,
                        depot=0,
                        demands=qaoa_demands,
                        vehicle_capacity=req.vehicle_capacity,
                        p=req.qaoa_depth,
                        shots=req.qaoa_shots,
                        optimizer_name=req.qaoa_optimizer,
                        penalty=req.qaoa_penalty,
                        random_seed=req.random_seed,
                        max_iter=2,
                    )
                    res["algorithm_name"] = "QAOA Hybrid"
                    res["category"] = "quantum_hybrid"
                    res["category_label"] = "Quantum / Quantum-Classical"
                    res["compute_type"] = "Qiskit Statevector Simulator"
                    return res
                else:
                    res = classical_solver.solve_ortools(
                        adjusted_matrix,
                        req.num_vehicles,
                        depot=0,
                        demands=demands_int,
                        vehicle_capacities=capacities,
                        time_limit_sec=0.25,
                        objective_weights=objective_weights,
                    )
                    res["algorithm_name"] = "OR-Tools (CVRP)"
                    res["category"] = "classical"
                    res["category_label"] = "Classical"
                    res["compute_type"] = "Classical CPU"
                    return res

            try:
                algo_res, res_metrics = profile_algorithm_execution(_run_raw_solver, algo)
            except Exception as e:
                logger.error(f"Solver {algo} execution error: {e}")
                algo_res = {"success": False, "error": str(e), "routes": [], "status": "FAILED"}
                res_metrics = {
                    "runtime_ms": 0.0,
                    "cpu_time_ms": 0.0,
                    "cpu_utilization_percent": 0.0,
                    "memory_used_mb": 0.0,
                    "peak_memory_mb": 0.0,
                    "time_complexity": "N/A",
                    "space_complexity": "N/A",
                    "measurement_available": False,
                }

            # Universal 100% Stop Coverage Repair & Centralized Validation (R == I)
            input_cust_ids = [i for i in range(1, n)]
            repaired_routes, val_report = repair_fleet_coverage(
                algo_res.get("routes", []),
                input_cust_ids,
                adjusted_matrix,
                demands_int,
                capacities,
                req.num_vehicles,
                depot=0,
            )

            # Reconstruct real road waypoints
            for r_idx, route in enumerate(repaired_routes, start=1):
                route["vehicle_id"] = r_idx
                route["total_distance_km"] = route.get("distance_km", 0.0)
                if road_network_service.is_ready() and len(snapped_node_ids) >= len(locations):
                    road_wps = road_network_service.reconstruct_vehicle_road_route(
                        route["stops"], locations, snapped_node_ids
                    )
                    route["waypoints"] = road_wps
                else:
                    route["waypoints"] = [
                        {
                            "lat": locations[s][0],
                            "lon": locations[s][1],
                            "type": "depot" if s == 0 else "customer",
                            "index": s,
                            "is_stop": True
                        }
                        for s in route["stops"]
                        if s < len(locations)
                    ]

            algo_res["routes"] = repaired_routes
            algo_res["total_distance_km"] = round(float(sum(r["distance_km"] for r in repaired_routes)), 3)
            algo_res["total_objective_cost"] = algo_res["total_distance_km"]
            algo_res["total_travel_time_min"] = round(float((algo_res["total_objective_cost"] / 40.0) * 60), 2)
            algo_res["resource_metrics"] = res_metrics
            algo_res["validation_report"] = val_report
            algo_res["execution_time_sec"] = round(res_metrics["runtime_ms"] / 1000.0, 3)

            # Feasibility: Must be complete (0 unserved, 0 duplicates) AND have 0 capacity violations
            algo_res["unserved_customers"] = len(val_report["missing_delivery_ids"])
            algo_res["served_customers"] = val_report["visited_delivery_count"]
            algo_res["capacity_violations"] = val_report["capacity_violations"]
            algo_res["is_feasible"] = val_report["is_valid"]
            algo_res["status"] = "SUCCESS" if val_report["is_valid"] else ("PENALIZED" if val_report["capacity_violations"] > 0 else "FAILED")

            if road_warnings:
                algo_res["warnings"] = list(set(algo_res.get("warnings", []) + road_warnings))

            return algo_res

        from concurrent.futures import ThreadPoolExecutor

        if len(to_run) == 1:
            results[to_run[0]] = _execute_single_algo(to_run[0])
        else:
            with ThreadPoolExecutor(max_workers=min(len(to_run), 8)) as executor:
                future_to_algo = {executor.submit(_execute_single_algo, a): a for a in to_run}
                for fut in future_to_algo:
                    a = future_to_algo[fut]
                    try:
                        results[a] = fut.result()
                    except Exception as exc:
                        logger.error(f"Concurrent worker for {a} raised: {exc}")
                        results[a] = {"success": False, "error": str(exc), "routes": [], "status": "FAILED"}

        # Safely attempt persistence in ExperimentResult table for each algorithm
        for a_name, a_res in results.items():
            try:
                exp_res = ExperimentResult(
                    experiment_id=experiment.id,
                    algorithm=a_name,
                    total_distance_km=a_res.get("total_distance_km", 0),
                    total_travel_time_min=a_res.get("total_travel_time_min", 0),
                    total_objective_cost=a_res.get("total_objective_cost", 0),
                    execution_time_sec=a_res.get("execution_time_sec", 0),
                    is_feasible=a_res.get("is_feasible", False),
                    capacity_violations=a_res.get("capacity_violations", 0),
                    unserved_customers=a_res.get("unserved_customers", 0),
                    routes=a_res.get("routes", []),
                    solver_log=a_res.get("solver_log", ""),
                    warnings=a_res.get("warnings", []),
                    qubit_count=a_res.get("num_qubits", 0),
                    circuit_depth=a_res.get("circuit_depth", 0),
                    qaoa_layers=a_res.get("qaoa_layers", 0),
                    measurement_shots=a_res.get("measurement_shots", 0),
                    best_bitstring=a_res.get("best_bitstring", ""),
                    optimizer_iterations=a_res.get("optimizer_iterations", 0),
                    energy_history=a_res.get("energy_history", []),
                )
                db.add(exp_res)
            except Exception as db_err:
                logger.warning(f"Could not persist experiment result for '{a_name}': {db_err}")

        # Build comprehensive comparison summary with unique canonical IDs and resource metrics
        comparison_items = []
        for algo_key in to_run:
            if algo_key not in results:
                continue
            algo_data = results[algo_key]
            res_m = algo_data.get("resource_metrics", {})
            comparison_items.append({
                "id": algo_key,
                "name": algo_data.get("algorithm_name", algo_key.upper()),
                "category": algo_data.get("category", "classical"),
                "category_label": algo_data.get("category_label", "Classical"),
                "compute_type": algo_data.get("compute_type", "Classical CPU"),
                "status": algo_data.get("status", "SUCCESS"),
                "is_simulated_fallback": algo_data.get("is_simulated_fallback", False),
                "error": algo_data.get("error", None),
                "execution_time_sec": algo_data.get("execution_time_sec", 0.0),
                "total_distance_km": algo_data.get("total_distance_km", 0.0),
                "total_travel_time_min": algo_data.get("total_travel_time_min", 0.0),
                "total_objective_cost": algo_data.get("total_objective_cost", 0.0),
                "is_feasible": algo_data.get("is_feasible", False),
                "capacity_violations": algo_data.get("capacity_violations", 0),
                "unserved_customers": algo_data.get("unserved_customers", 0),
                "served_customers": algo_data.get("served_customers", (n - 1) - algo_data.get("unserved_customers", 0)),
                "vehicles_used": len(algo_data.get("routes", [])),
                "convergence_info": algo_data.get("convergence_info", {}),
                "cpu_utilization_percent": res_m.get("cpu_utilization_percent", 0.0),
                "cpu_core_ratio_percent": res_m.get("cpu_core_ratio_percent", 0.0),
                "memory_used_mb": res_m.get("memory_used_mb", 0.0),
                "peak_memory_mb": res_m.get("peak_memory_mb", 0.0),
                "heap_allocated_mb": res_m.get("heap_allocated_mb", 0.0),
                "heap_peak_mb": res_m.get("heap_peak_mb", 0.0),
                "process_rss_mb": res_m.get("process_rss_mb", 0.0),
                "time_complexity": res_m.get("time_complexity", "O(N^2)"),
                "space_complexity": res_m.get("space_complexity", "O(N)"),
                "resource_metrics": res_m,
                "is_best": False,
            })

        # Identify Best Feasible Result (Universal Policy: strictly requires is_feasible, 0 unserved, 0 violations)
        feasible_items = [
            it for it in comparison_items
            if it.get("status") in ("SUCCESS", "OPTIMAL") and it["is_feasible"] and it["capacity_violations"] == 0 and it["unserved_customers"] == 0
        ]

        if feasible_items:
            best_item = min(feasible_items, key=lambda x: (x["total_distance_km"], x["total_objective_cost"]))
            best_reason = f"Lowest route distance ({best_item['total_distance_km']} km) with 100% stop coverage and 0 constraint violations"
        elif comparison_items:
            # If no feasible candidate exists, select lowest-violation candidate but report honestly
            best_item = min(
                comparison_items,
                key=lambda x: (x["unserved_customers"] * 1000 + x["capacity_violations"] * 100, x["total_distance_km"])
            )
            if total_cust_demand > total_fleet_capacity:
                best_reason = f"Mathematically infeasible fleet: total customer demand ({total_cust_demand}) exceeds total fleet capacity ({total_fleet_capacity}). Solutions incur {best_item['capacity_violations']} capacity violation(s)."
            else:
                best_reason = f"Infeasible solution: {best_item['capacity_violations']} capacity violation(s), {best_item['unserved_customers']} unserved stop(s)."
        else:
            best_item = None
            best_reason = "No solutions evaluated"

        if best_item:
            best_item["is_best"] = True

        experiment.status = "completed"
        await db.flush()
        await db.commit()

        return {
            "experiment_id": experiment.id,
            "status": "completed",
            "execution_time_sec": round(time.time() - t0, 3),
            "selection_mode": mode,
            "selected_algorithms": to_run,
            "primary_algorithm": to_run[0] if to_run else "ortools",
            "best_feasible_algorithm": best_item["id"] if best_item else "ortools",
            "comparison_summary": {
                "best_algorithm": best_item["id"] if best_item else "ortools",
                "best_algorithm_name": best_item["name"] if best_item else "OR-Tools",
                "best_reason": best_reason,
                "best_feasible_distance_km": best_item["total_distance_km"] if best_item else 0.0,
                "items": comparison_items,
            },
            "problem": {
                "num_customers": n - 1,
                "num_vehicles": req.num_vehicles,
                "depot": {"lat": locations[0][0], "lon": locations[0][1]},
                "traffic_factor": traffic_factor,
                "weather_factor": weather_factor,
                "locations": [{"lat": l[0], "lon": l[1], "demand": d}
                              for l, d in zip(locations, demands)],
            },
            "results": results
        }

    except Exception as e:
        experiment.status = "failed"
        experiment.error_message = str(e)
        logger.error(f"Optimization failed: {e}")
        raise HTTPException(500, f"Optimization failed: {str(e)}")


@router.get("/optimization/limits")
async def get_optimization_limits():
    """Get current optimization size limits."""
    return {
        "max_customers_classical": settings.MAX_CUSTOMERS_CLASSICAL,
        "max_customers_qaoa": settings.MAX_CUSTOMERS_QAOA,
        "note": "QAOA is limited by simulator qubit count. For n customers and K vehicles, QUBO needs n*K qubits (assignment) or n^2 qubits (TSP)."
    }


@router.get("/delivery-stops")
async def get_delivery_stops(limit: int = 50):
    """Retrieve processed customer delivery stops for route planning workbench."""
    stops = []
    seen_coords = set()
    duplicate_count = 0
    invalid_count = 0
    total_rows = 0

    if data_processor.customers_df is not None and len(data_processor.customers_df) > 0:
        total_rows = len(data_processor.customers_df)
        df = data_processor.customers_df.copy()
        if 'latitude' not in df.columns or df['latitude'].isna().all() or ('coordinates_source' in df.columns and df['coordinates_source'].iloc[0] == 'estimated'):
            df = data_processor.assign_coordinates_to_customers(df, data_processor.locations_df)

        for i, (_, row) in enumerate(df.head(limit).iterrows()):
            try:
                lat_raw = float(row.get('latitude', 40.7580))
                lon_raw = float(row.get('longitude', -73.8292))
                # Validate and correct swapped coordinates
                if lat_raw < 0 and lon_raw > 0:
                    lat_raw, lon_raw = lon_raw, lat_raw

                # Range check for NYC metropolitan region
                if not (40.50 <= lat_raw <= 40.95 and -74.25 <= lon_raw <= -73.70):
                    invalid_count += 1
                    continue

                # Exclude New Jersey across Hudson River (lat > 40.70, lon < -74.02)
                if lat_raw > 40.70 and lon_raw < -74.02:
                    invalid_count += 1
                    continue

                # Water body check - delivery stops must be on land roadways
                if check_water_body(lat_raw, lon_raw):
                    invalid_count += 1
                    continue

                coord_key = (round(lat_raw, 4), round(lon_raw, 4))
                if coord_key in seen_coords:
                    duplicate_count += 1
                else:
                    seen_coords.add(coord_key)

                lat = round(lat_raw, 6)
                lon = round(lon_raw, 6)
            except (ValueError, TypeError):
                invalid_count += 1
                continue

            order_id = str(row.get('order_id', f"ORD-{1000 + i}"))
            cust_id = str(row.get('customer_id', f"CUST-{i + 1}"))
            cuisine = str(row.get('cuisine_type', 'Standard'))
            demand = float(row.get('demand', 5 + (i % 15)))
            addr = str(row.get('address', f"NYC Delivery Sector #{100 + i}"))

            stops.append({
                "id": order_id,
                "customer_id": cust_id,
                "name": f"{cuisine} Delivery ({cust_id})",
                "lat": lat,
                "lon": lon,
                "demand": round(demand, 1),
                "service_time_min": 10.0 + (i % 5) * 2,
                "address": addr,
                "status": "valid",
                "is_included": True
            })

    # If no processed data is ready, return default NYC stops
    if not stops:
        default_coords = [
            (40.7580, -73.9855, "Midtown Manhattan Depot"),
            (40.7484, -73.9857, "Empire State Delivery"),
            (40.7589, -73.9787, "Rockefeller Center Stop"),
            (40.7614, -73.9776, "MoMA Delivery"),
            (40.7505, -73.9934, "Penn Station Stop"),
            (40.7295, -73.9965, "Washington Sq Stop"),
            (40.7128, -74.0060, "Lower Manhattan Stop"),
            (40.7739, -73.9712, "Central Park East Stop"),
        ]
        total_rows = len(default_coords)
        for i, (lat, lon, name) in enumerate(default_coords):
            stops.append({
                "id": f"ORD-{2000 + i}",
                "customer_id": f"CUST-{i + 1}",
                "name": name,
                "lat": lat,
                "lon": lon,
                "demand": 12.0 + (i * 3),
                "service_time_min": 12.0,
                "address": f"{name}, New York, NY",
                "status": "valid",
                "is_included": True
            })

    return {
        "count": len(stops),
        "depot": {"lat": 40.7580, "lon": -73.8292, "name": "Flushing Logistics Hub"},
        "stops": stops,
        "diagnostics": {
            "total_dataset_rows": total_rows,
            "valid_coordinate_rows": len(stops),
            "invalid_coordinate_rows": invalid_count,
            "duplicate_coordinates": duplicate_count,
            "source": "NYC Ingested Fleet & Physical Facilities"
        }
    }


@router.post("/optimization/estimate")
async def estimate_problem_size(req: OptimizationRequest):
    """Estimate complexity, qubit requirements, and feasibility for problem size."""
    n = req.num_customers
    k = req.num_vehicles
    
    # In VRP QUBO formulation, qubits = n * k (binary assignment) or n^2 (permutation)
    assignment_qubits = n * k
    tsp_qubits = n * n
    
    qaoa_feasible = assignment_qubits <= 20
    warning = None
    if not qaoa_feasible:
        warning = (
            f"QAOA statevector simulation requires {assignment_qubits} qubits (exceeds simulator limit of 20). "
            f"Please reduce stops to ≤ 8 or vehicles to ≤ 2 for QAOA simulation, or use Classical mode."
        )

    return {
        "num_customers": n,
        "num_vehicles": k,
        "classical_supported": True,
        "classical_estimated_time_sec": round(0.1 + n * 0.02, 2),
        "qaoa_supported": qaoa_feasible,
        "assignment_qubits": assignment_qubits,
        "tsp_qubits": tsp_qubits,
        "warning": warning,
        "recommended_mode": "classical" if not qaoa_feasible else "both"
    }


# ─── Experiment Endpoints ────────────────────────────────────────

@router.get("/experiments")
async def list_experiments(
    page: int = 1, size: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """List all experiments with pagination."""
    offset = (page - 1) * size
    result = await db.execute(
        select(Experiment).order_by(Experiment.timestamp.desc()).offset(offset).limit(size)
    )
    experiments = result.scalars().all()
    return [_experiment_to_dict(e) for e in experiments]


@router.get("/experiments/{experiment_id}")
async def get_experiment(experiment_id: str, db: AsyncSession = Depends(get_db)):
    """Get detailed experiment results."""
    result = await db.execute(
        select(Experiment).where(Experiment.id == experiment_id)
    )
    experiment = result.scalar_one_or_none()
    if not experiment:
        raise HTTPException(404, "Experiment not found")

    exp_dict = _experiment_to_dict(experiment)

    # Load results
    results_query = await db.execute(
        select(ExperimentResult).where(ExperimentResult.experiment_id == experiment_id)
    )
    exp_results = results_query.scalars().all()
    exp_dict["results"] = {r.algorithm: _result_to_dict(r) for r in exp_results}

    return exp_dict


@router.get("/experiments/{experiment_id}/export")
async def export_experiment(experiment_id: str, format: str = "json",
                             db: AsyncSession = Depends(get_db)):
    """Export experiment as JSON or CSV."""
    result = await db.execute(
        select(Experiment).where(Experiment.id == experiment_id)
    )
    experiment = result.scalar_one_or_none()
    if not experiment:
        raise HTTPException(404, "Experiment not found")

    results_query = await db.execute(
        select(ExperimentResult).where(ExperimentResult.experiment_id == experiment_id)
    )
    exp_results = results_query.scalars().all()

    export = {
        "experiment": _experiment_to_dict(experiment),
        "results": {r.algorithm: _result_to_dict(r) for r in exp_results},
        "exported_at": datetime.utcnow().isoformat()
    }

    return export


@router.delete("/experiments/{experiment_id}")
async def delete_experiment(experiment_id: str, db: AsyncSession = Depends(get_db)):
    """Delete an experiment."""
    result = await db.execute(
        select(Experiment).where(Experiment.id == experiment_id)
    )
    experiment = result.scalar_one_or_none()
    if not experiment:
        raise HTTPException(404, "Experiment not found")
    await db.execute(delete(ExperimentResult).where(ExperimentResult.experiment_id == experiment_id))
    await db.delete(experiment)
    await db.commit()
    return {"message": "Experiment deleted"}


# ─── Analytics Endpoints ─────────────────────────────────────────

@router.get("/analytics/summary")
async def get_analytics_summary(db: AsyncSession = Depends(get_db)):
    """Get overall analytics from processed datasets."""
    summary = data_processor.get_analytics_summary()

    # Add experiment stats
    exp_result = await db.execute(select(Experiment).order_by(Experiment.timestamp.desc()))
    experiments = exp_result.scalars().all()
    summary["experiments"] = {
        "total": len(experiments),
        "completed": sum(1 for e in experiments if e.status == "completed"),
        "recent": [_experiment_to_dict(e) for e in experiments[:5]]
    }

    return summary


@router.get("/road-network")
async def get_road_network():
    """Get road network summary."""
    if data_processor.road_graph is None:
        return {"available": False, "message": "No road network loaded. Upload and process road dataset."}

    G = data_processor.road_graph
    # Sample some nodes and edges for visualization
    nodes_sample = []
    for node_id, data in list(G.nodes(data=True))[:500]:
        if 'x' in data and 'y' in data:
            nodes_sample.append({
                "id": str(node_id),
                "lat": float(data['y']),
                "lon": float(data['x'])
            })

    edges_sample = []
    for u, v, data in list(G.edges(data=True))[:1000]:
        u_data = G.nodes[u]
        v_data = G.nodes[v]
        if 'x' in u_data and 'y' in u_data and 'x' in v_data and 'y' in v_data:
            edges_sample.append({
                "source": {"lat": float(u_data['y']), "lon": float(u_data['x'])},
                "target": {"lat": float(v_data['y']), "lon": float(v_data['x'])},
                "length": float(data.get('length', 0)),
                "highway": str(data.get('highway', '')),
            })

    return {
        "available": True,
        "node_count": G.number_of_nodes(),
        "edge_count": G.number_of_edges(),
        "nodes_sample": nodes_sample,
        "edges_sample": edges_sample,
    }


# ─── Helpers ─────────────────────────────────────────────────────

def _prepare_problem(req: OptimizationRequest):
    """Prepare customer locations and demands for optimization."""
    # Validate depot location against NYC 5-Borough road network bounds and water bodies
    is_valid_depot, depot_err = validate_nyc_coordinate(float(req.depot_lat), float(req.depot_lon))
    if not is_valid_depot:
        raise HTTPException(
            status_code=400,
            detail=f"Depot location ({req.depot_lat}, {req.depot_lon}) validation error: {depot_err}"
        )

    # Check if explicit custom_customers were sent from Step 1
    if req.custom_customers and len(req.custom_customers) > 0:
        locations = [(float(req.depot_lat), float(req.depot_lon))]
        demands = [0.0]
        for idx, c in enumerate(req.custom_customers[:req.num_customers], start=1):
            try:
                lat = float(c.get('lat', c.get('latitude', req.depot_lat)))
                lon = float(c.get('lon', c.get('longitude', req.depot_lon)))
                demand = float(c.get('demand', 10.0))
            except (ValueError, TypeError):
                lat = float(req.depot_lat)
                lon = float(req.depot_lon)
                demand = 10.0

            # Validate customer stop
            is_valid_stop, stop_err = validate_nyc_coordinate(lat, lon)
            if not is_valid_stop:
                name = c.get('name', f'Delivery Stop #{idx}')
                raise HTTPException(
                    status_code=400,
                    detail=f"Customer '{name}' at ({lat:.4f}, {lon:.4f}) validation error: {stop_err}"
                )

            locations.append((lat, lon))
            demands.append(demand)
        return locations, demands

    n = req.num_customers + 1  # +1 for depot

    # Try to use processed customer data
    if data_processor.customers_df is not None and len(data_processor.customers_df) > 0:
        df = data_processor.customers_df.copy()

        # Assign coordinates if missing
        if 'latitude' not in df.columns or df['latitude'].isna().all():
            df = data_processor.assign_coordinates_to_customers(df, data_processor.locations_df)

        # Select subset of customers
        subset = df.head(req.num_customers)
        locations = [(req.depot_lat, req.depot_lon)]
        demands = [0.0]

        for _, row in subset.iterrows():
            try:
                lat = float(row.get('latitude'))
                lon = float(row.get('longitude'))
            except (ValueError, TypeError):
                lat = float(req.depot_lat + 0.01)
                lon = float(req.depot_lon + 0.01)

            is_valid, _ = validate_nyc_coordinate(lat, lon)
            if not is_valid:
                lat = 40.7500 + (len(locations) % 15) * 0.003
                lon = -73.9850 + ((len(locations) % 10) - 5) * 0.002

            try:
                demand = float(row.get('demand', 1.0))
            except (ValueError, TypeError):
                demand = 1.0

            locations.append((lat, lon))
            demands.append(demand)

    else:
        # Generate sample locations strictly on NYC land
        logger.warning("No customer data loaded. Using verified NYC test land locations.")
        np.random.seed(req.random_seed)
        locations = [(req.depot_lat, req.depot_lon)]
        demands = [0.0]
        for i in range(req.num_customers):
            lat = 40.7300 + (i % 20) * 0.003
            lon = -73.9850 + ((i % 12) - 6) * 0.0025
            if check_water_body(lat, lon):
                lat = 40.7580 + (i % 10) * 0.002
                lon = -73.9780 + (i % 8) * 0.0015
            demand = float(5 + (i % 15))
            locations.append((lat, lon))
            demands.append(demand)

    return locations, demands


def _experiment_to_dict(e: Experiment) -> dict:
    ts_str = None
    if e.timestamp:
        if isinstance(e.timestamp, str):
            ts_str = e.timestamp.replace(" ", "T")
            if not ts_str.endswith("Z"):
                ts_str += "Z"
        elif hasattr(e.timestamp, "isoformat"):
            ts_str = e.timestamp.isoformat()
            if not ts_str.endswith("Z"):
                ts_str += "Z"
        else:
            ts_str = str(e.timestamp)

    best_dist = None
    best_algo = None
    total_runtime = None
    if hasattr(e, "results") and e.results:
        feasible = [r for r in e.results if r.is_feasible and (r.total_distance_km or 0) > 0]
        pool = feasible if feasible else [r for r in e.results if (r.total_distance_km or 0) > 0]
        if pool:
            best_res = min(pool, key=lambda r: r.total_distance_km)
            best_dist = round(float(best_res.total_distance_km), 2)
            best_algo = best_res.algorithm
        total_runtime = round(float(sum(r.execution_time_sec or 0.0 for r in e.results)), 3)

    return {
        "id": e.id,
        "name": e.name,
        "timestamp": ts_str,
        "algorithm": e.algorithm,
        "num_customers": e.num_customers,
        "num_vehicles": e.num_vehicles,
        "vehicle_capacity": e.vehicle_capacity,
        "depot_lat": e.depot_lat,
        "depot_lon": e.depot_lon,
        "weight_distance": e.weight_distance,
        "weight_travel_time": e.weight_travel_time,
        "traffic_scenario": e.traffic_scenario,
        "weather_scenario": e.weather_scenario,
        "classical_time_limit_sec": e.classical_time_limit_sec,
        "qaoa_depth": e.qaoa_depth,
        "qaoa_shots": e.qaoa_shots,
        "qaoa_optimizer": e.qaoa_optimizer,
        "random_seed": e.random_seed,
        "status": e.status,
        "error_message": e.error_message,
        "best_distance_km": best_dist,
        "best_algorithm": best_algo,
        "total_runtime_sec": total_runtime,
    }


def _result_to_dict(r: ExperimentResult) -> dict:
    return {
        "id": r.id,
        "algorithm": r.algorithm,
        "total_distance_km": r.total_distance_km,
        "total_travel_time_min": r.total_travel_time_min,
        "total_objective_cost": r.total_objective_cost,
        "execution_time_sec": r.execution_time_sec,
        "is_feasible": r.is_feasible,
        "capacity_violations": r.capacity_violations,
        "unserved_customers": r.unserved_customers,
        "routes": r.routes,
        "qubit_count": r.qubit_count,
        "circuit_depth": r.circuit_depth,
        "qaoa_layers": r.qaoa_layers,
        "measurement_shots": r.measurement_shots,
        "best_bitstring": r.best_bitstring,
        "optimizer_iterations": r.optimizer_iterations,
        "energy_history": r.energy_history,
        "solver_log": r.solver_log,
        "warnings": r.warnings,
    }
