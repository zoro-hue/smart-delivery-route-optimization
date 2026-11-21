"""
Optimization & Experiments API — Classical VRP, QAOA, Comparison, Experiment History
"""
from __future__ import annotations

import asyncio
import gc
import json
import math
import time
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple, Set

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
from app.services.optimization.quantum_solver import quantum_solver, _check_qiskit_available
from app.services.optimization.qiga_solver import qiga_solver
from app.services.optimization.cooperative_solver import cooperative_solver
from app.services.optimization.route_identity import compute_route_identity_diagnostics
from app.services.optimization.energy_service import (
    compute_full_energy_analysis,
    compute_algorithm_energy_profile,
    compute_energy_comparison,
    PROPULSION_MODELS,
)
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
        "category_label": "Cooperative Hybrid (Spark Local + Classical + QAOA CPU Sim)",
        "tag": "Spark + Adaptive + QAOA/Tabu + VND",
        "description": "End-to-end cooperative optimization unifying Spark local spatial decomposition, Multi-Armed Bandit adaptive control, classical heuristics (Tabu/KL/VND), and QAOA with Qiskit Aer/statevector CPU simulation with Proposition 1 non-degradation guardrail.",
        "operational": True,
        "max_customers": 200,
        "is_primary": False,
        "compute_type": "Hybrid (Spark Local + Classical CPU + QAOA Statevector CPU Simulation)",
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
        "id": "tabu_search",
        "name": "Tabu Search",
        "category": "classical",
        "category_label": "Classical",
        "tag": "Metaheuristic Memory",
        "description": "Recency-memory metaheuristic with tabu tenure and aspiration to escape local optima.",
        "operational": True,
        "max_customers": 200,
        "is_primary": False,
        "compute_type": "Classical CPU",
    },
    {
        "id": "kernighan_lin",
        "name": "Kernighan–Lin",
        "category": "classical",
        "category_label": "Classical",
        "tag": "Bipartition Exchange",
        "description": "Variable-depth bipartition sequence exchange with node locking and 2-opt refinement.",
        "operational": True,
        "max_customers": 200,
        "is_primary": False,
        "compute_type": "Classical CPU",
    },
    {
        "id": "vnd",
        "name": "Variable Neighborhood Descent (VND)",
        "category": "classical",
        "category_label": "Classical",
        "tag": "Multi-Neighborhood Descent",
        "description": "Deterministic local search systematically traversing 2-opt, Relocate, and Swap neighborhoods.",
        "operational": True,
        "max_customers": 200,
        "is_primary": False,
        "compute_type": "Classical CPU",
    },
    {
        "id": "qaoa",
        "name": "QAOA",
        "category": "quantum_hybrid",
        "category_label": "Quantum-Classical Simulation",
        "tag": "Hybrid Quantum-Classical",
        "description": "Hybrid variational quantum-classical optimization using QAOA with Qiskit Aer/statevector CPU simulation.",
        "operational": True,
        "max_customers": 8,
        "is_primary": False,
        "compute_type": "QAOA with Qiskit Aer/statevector CPU simulation",
    },
    {
        "id": "qiga",
        "name": "Quantum-Inspired Genetic Algorithm (QIGA/IQGA)",
        "category": "quantum_inspired",
        "category_label": "Quantum-Inspired Classical",
        "tag": "Quantum-Inspired",
        "description": "Quantum-inspired evolutionary optimization using Q-bit probability amplitudes and rotation gates, executed entirely on classical CPU.",
        "operational": True,
        "max_customers": 50,
        "is_primary": False,
        "compute_type": "Classically Simulated Q-Bits (Classical CPU)",
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
    service_time_per_stop_min: float = Field(0.0, ge=0.0, le=120.0)  # Stop delivery dwell time in minutes

    # Classical settings
    classical_time_limit_sec: int = Field(30, ge=1, le=300)

    # QAOA settings
    qaoa_depth: int = Field(1, ge=1, le=5)
    qaoa_shots: int = Field(1024, ge=100, le=10000)
    qaoa_optimizer: str = "COBYLA"
    qaoa_penalty: float = Field(10.0, gt=0)

    # Optional explicit customer stops from Step 1
    custom_customers: Optional[List[dict]] = None

    # Vehicle Profile & Fleet Condition Modeling
    vehicle_profiles: Optional[List[dict]] = None

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


class EnergyAnalysisRequest(BaseModel):
    results: Dict[str, Any]
    propulsion_type: Optional[str] = "diesel"
    baseline_algorithm: Optional[str] = "ortools"
    vehicle_capacity: Optional[float] = 0.0
    traffic_factor: Optional[float] = 1.0
    vehicle_profiles: Optional[List[dict]] = None


# ─── Optimization Endpoints ──────────────────────────────────────

@router.get("/optimization/propulsion-models")
async def get_propulsion_models():
    """Retrieve all supported vehicle propulsion profiles, emission factors, and fuel prices."""
    return {
        "status": "success",
        "models": PROPULSION_MODELS,
        "default": "diesel",
    }


@router.post("/optimization/energy-analysis")
async def calculate_energy_analysis_endpoint(req: EnergyAnalysisRequest):
    """Calculate comprehensive energy, fuel, carbon emissions, and operational cost analysis."""
    try:
        analysis = compute_full_energy_analysis(
            results=req.results,
            default_propulsion=req.propulsion_type or "diesel",
            baseline_algo=req.baseline_algorithm or "ortools",
            vehicle_capacity=req.vehicle_capacity or 0.0,
            traffic_factor=req.traffic_factor or 1.0,
            vehicle_profiles=req.vehicle_profiles,
        )
        return {
            "status": "success",
            "energy_analysis": analysis,
        }
    except Exception as e:
        logger.error(f"Error calculating energy analysis: {e}")
        raise HTTPException(500, f"Energy analysis failed: {str(e)}")

@router.get("/optimization/algorithms")
async def get_optimization_algorithms():
    """Return available operational optimization algorithms and their capabilities."""
    return {
        "status": "success",
        "count": len(AVAILABLE_ALGORITHMS),
        "algorithms": AVAILABLE_ALGORITHMS,
    }


# ─── Optimization Helper Functions & Job Architecture ─────────────

import psutil

def _get_process_memory_mb() -> float:
    try:
        return round(psutil.Process().memory_info().rss / (1024 * 1024), 2)
    except Exception:
        return 0.0

_active_jobs: Dict[str, Dict[str, Any]] = {}
_MAX_ACTIVE_JOBS = 5
_job_semaphore = asyncio.Semaphore(1)


def _evict_old_active_jobs():
    """Keep in-memory active jobs bounded to prevent monotonically growing heap allocations."""
    if len(_active_jobs) > _MAX_ACTIVE_JOBS:
        sorted_keys = sorted(_active_jobs.keys(), key=lambda k: _active_jobs[k].get("created_at", 0))
        to_evict = sorted_keys[: len(_active_jobs) - _MAX_ACTIVE_JOBS]
        for ek in to_evict:
            _active_jobs.pop(ek, None)


def _prepare_optimization_problem(req: OptimizationRequest):
    """Validate coordinates, compute road matrix, and prepare problem parameters."""
    locations, demands = _prepare_problem(req)
    n = len(locations)

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

    traffic_factor = data_processor.get_traffic_factor(req.traffic_scenario)
    weather_factor = data_processor.get_weather_factor(req.weather_scenario)

    snapped_node_ids = []
    road_warnings = []

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

    demands_int = [int(d) for d in demands]
    total_cust_demand = sum(demands_int)

    # Heterogeneous Fleet Processing & Individual Vehicle Condition Evaluation
    usable_vehicle_profiles = []
    vehicle_ranges = []
    fleet_capacities = []

    if req.vehicle_profiles and len(req.vehicle_profiles) > 0:
        for vp in req.vehicle_profiles:
            is_avail = vp.get("is_available", True)
            maint = str(vp.get("maintenance_status", "ok")).lower()
            if is_avail and maint != "critical":
                usable_vehicle_profiles.append(vp)
                fleet_capacities.append(int(vp.get("max_payload_kg", req.vehicle_capacity)))
                usable_range = float(vp.get("usable_range_km", 250.0) or 250.0)
                vehicle_ranges.append(usable_range)
            else:
                road_warnings.append(
                    f"Vehicle '{vp.get('name', vp.get('vehicle_id'))}' excluded from dispatch: "
                    f"is_available={is_avail}, maintenance_status='{maint}'."
                )

        if not usable_vehicle_profiles:
            road_warnings.append("All configured fleet vehicles were unavailable or in critical maintenance. Reverting to default fleet.")
            usable_vehicle_profiles = None
            fleet_capacities = [int(req.vehicle_capacity)] * req.num_vehicles
            vehicle_ranges = None

    if not usable_vehicle_profiles:
        usable_vehicle_profiles = None
        fleet_capacities = [int(req.vehicle_capacity)] * req.num_vehicles
        vehicle_ranges = None
        num_dispatch_vehicles = req.num_vehicles
    else:
        num_dispatch_vehicles = len(usable_vehicle_profiles)

    total_fleet_capacity = sum(fleet_capacities)
    capacities = fleet_capacities

    if total_cust_demand > total_fleet_capacity:
        road_warnings.append(
            f"Fleet capacity warning: Total customer demand ({total_cust_demand}) exceeds total fleet capacity "
            f"({total_fleet_capacity} units across {num_dispatch_vehicles} vehicles). Solvers will incur capacity penalties."
        )

    return (
        locations, demands, n, adjusted_matrix, snapped_node_ids,
        road_warnings, physical_matrix, objective_weights, demands_int,
        total_cust_demand, total_fleet_capacity, capacities,
        traffic_factor, weather_factor, num_dispatch_vehicles,
        vehicle_ranges, usable_vehicle_profiles
    )


def _resolve_algorithms_to_run(req: OptimizationRequest, n: int) -> Tuple[List[str], str]:
    """Resolve normalized list of algorithm keys based on selection mode."""
    to_run: List[str] = []
    mode = (req.selection_mode or "recommended").lower().strip()

    if mode == "recommended":
        to_run = ["routeiq_cooperative"]
    elif mode == "compare":
        if req.selected_algorithms and len(req.selected_algorithms) >= 2:
            to_run = list(req.selected_algorithms)
        else:
            to_run = [a["id"] for a in AVAILABLE_ALGORITHMS]
    elif mode in ("custom", "single", "individual"):
        if req.selected_algorithms and len(req.selected_algorithms) > 0:
            to_run = list(req.selected_algorithms)
        else:
            to_run = ["ortools"]
    else:
        if req.algorithm == "both":
            to_run = ["ortools", "qaoa"]
        elif req.algorithm == "qaoa":
            to_run = ["qaoa"]
        else:
            to_run = ["ortools"]

    normalized_to_run = []
    for a in to_run:
        key = a.lower().strip()
        if key == "classical":
            key = "ortools"
        if key not in normalized_to_run:
            normalized_to_run.append(key)
    return normalized_to_run, mode


def _solve_single_algo(
    algo: str,
    n: int,
    num_vehicles: int,
    vehicle_capacity: float,
    classical_time_limit_sec: int,
    qaoa_depth: int,
    qaoa_shots: int,
    qaoa_optimizer: str,
    qaoa_penalty: float,
    random_seed: int,
    locations: List[Tuple[float, float]],
    demands_int: List[int],
    capacities: List[int],
    adjusted_matrix: np.ndarray,
    objective_weights: Dict[str, float],
    snapped_node_ids: List[int],
    road_warnings: List[str],
    route_geometry_cache: Dict[Tuple[int, ...], List[Dict[str, Any]]],
    physical_matrix: Optional[np.ndarray] = None,
    traffic_factor: float = 1.0,
    weather_factor: float = 1.0,
    service_time_per_stop_min: float = 0.0,
    vehicle_ranges: Optional[List[float]] = None,
    vehicle_profiles: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Execute a single solver with resource profiling, coverage repair, and waypoint reconstruction."""
    logger.info(f"Executing algorithm '{algo}' on {n} nodes, {num_vehicles} vehicles")

    def _run_raw_solver() -> Dict[str, Any]:
        effective_time_limit = 0.25 if n <= 35 else min(classical_time_limit_sec or 3, 5)
        if algo in ("routeiq_cooperative", "cooperative", "routeiq"):
            res = cooperative_solver.solve(
                distance_matrix=adjusted_matrix,
                num_vehicles=num_vehicles,
                depot=0,
                demands=demands_int,
                vehicle_capacities=capacities,
                time_limit_sec=effective_time_limit,
                objective_weights=objective_weights,
                locations=locations,
                seed=random_seed,
                vehicle_ranges=vehicle_ranges,
                vehicle_profiles=vehicle_profiles,
            )
            res["algorithm_name"] = "ROUTE/IQ Cooperative Engine"
            res["category"] = "cooperative"
            res["category_label"] = "Cooperative Hybrid (Spark Local + Classical + QAOA CPU Sim)"
            res["compute_type"] = "Hybrid (Spark Local + Classical CPU + QAOA Statevector CPU Simulation)"
            return res

        elif algo in ("ortools", "classical_ortools"):
            effective_time_limit = 0.25 if n <= 35 else min(classical_time_limit_sec or 3, 5)
            res = classical_solver.solve_ortools(
                adjusted_matrix,
                num_vehicles,
                depot=0,
                demands=demands_int,
                vehicle_capacities=capacities,
                time_limit_sec=effective_time_limit,
                objective_weights=objective_weights,
                vehicle_ranges=vehicle_ranges,
                vehicle_profiles=vehicle_profiles,
            )
            res["algorithm_name"] = "OR-Tools (CVRP)"
            res["category"] = "classical"
            res["category_label"] = "Classical"
            res["compute_type"] = "Classical CPU"
            return res

        elif algo in ("clarke_wright", "clarkewright", "savings"):
            res = classical_solver.solve_clarke_wright(
                adjusted_matrix,
                num_vehicles,
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
                num_vehicles,
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
                num_vehicles,
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
                num_vehicles,
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

        elif algo in ("tabu_search", "tabu", "tabusearch"):
            res = classical_solver.solve_tabu_search(
                adjusted_matrix,
                num_vehicles,
                depot=0,
                demands=demands_int,
                vehicle_capacities=capacities,
                objective_weights=objective_weights,
                max_iterations=25 if n <= 35 else 50,
            )
            res["algorithm_name"] = "Tabu Search Metaheuristic"
            res["category"] = "classical"
            res["category_label"] = "Classical"
            res["compute_type"] = "Classical CPU"
            return res

        elif algo in ("kernighan_lin", "kl", "kernighanlin"):
            res = classical_solver.solve_kernighan_lin(
                adjusted_matrix,
                num_vehicles,
                depot=0,
                demands=demands_int,
                vehicle_capacities=capacities,
                objective_weights=objective_weights,
                max_passes=2 if n <= 35 else 3,
            )
            res["algorithm_name"] = "Kernighan–Lin Bipartition"
            res["category"] = "classical"
            res["category_label"] = "Classical"
            res["compute_type"] = "Classical CPU"
            return res

        elif algo in ("vnd", "variable_neighborhood_descent"):
            res = classical_solver.solve_vnd(
                adjusted_matrix,
                num_vehicles,
                depot=0,
                demands=demands_int,
                vehicle_capacities=capacities,
                objective_weights=objective_weights,
            )
            res["algorithm_name"] = "Variable Neighborhood Descent (VND)"
            res["category"] = "classical"
            res["category_label"] = "Classical"
            res["compute_type"] = "Classical CPU"
            return res

        elif algo == "qiga":
            res = qiga_solver.solve(
                adjusted_matrix,
                num_vehicles,
                depot=0,
                demands=demands_int,
                vehicle_capacities=capacities,
                objective_weights=objective_weights,
            )
            res["algorithm_name"] = "Quantum-Inspired GA (QIGA/IQGA)"
            res["category"] = "quantum_inspired"
            res["category_label"] = "Quantum-Inspired Classical"
            res["compute_type"] = "Classically Simulated Q-Bits (Classical CPU)"
            return res

        elif algo == "qaoa":
            q_avail, _ = _check_qiskit_available()
            if not q_avail:
                logger.warning("QAOA: Qiskit package unavailable in environment; marking as FAILED")
                return {
                    "success": False,
                    "error": "Qiskit is not available for CPU statevector simulation",
                    "routes": [],
                    "status": "FAILED",
                    "algorithm_name": "QAOA Hybrid",
                    "category": "quantum_hybrid",
                    "category_label": "Quantum-Classical Simulation",
                    "compute_type": "QAOA with Qiskit Aer/statevector CPU simulation",
                }

            if n > settings.MAX_CUSTOMERS_QAOA + 1:
                logger.warning(f"QAOA: solving first {settings.MAX_CUSTOMERS_QAOA} customers on quantum simulator; remaining will be capacity-repaired")
                qaoa_n = settings.MAX_CUSTOMERS_QAOA + 1
                qaoa_matrix = adjusted_matrix[:qaoa_n, :qaoa_n]
                qaoa_demands = demands_int[:qaoa_n]
            else:
                qaoa_n = n
                qaoa_matrix = adjusted_matrix
                qaoa_demands = demands_int

            try:
                res = quantum_solver.solve(
                    qaoa_matrix,
                    num_vehicles,
                    depot=0,
                    demands=qaoa_demands,
                    vehicle_capacity=vehicle_capacity,
                    p=qaoa_depth,
                    shots=qaoa_shots,
                    optimizer_name=qaoa_optimizer,
                    penalty=qaoa_penalty,
                    random_seed=random_seed,
                    max_iter=2,
                )
            except Exception as q_err:
                logger.warning(f"QAOA statevector simulation error: {q_err}")
                return {
                    "success": False,
                    "error": f"QAOA CPU simulation error: {str(q_err)}",
                    "routes": [],
                    "status": "FAILED",
                    "algorithm_name": "QAOA Hybrid",
                    "category": "quantum_hybrid",
                    "category_label": "Quantum-Classical Simulation",
                    "compute_type": "QAOA with Qiskit Aer/statevector CPU simulation",
                }

            res["algorithm_name"] = "QAOA Hybrid"
            res["category"] = "quantum_hybrid"
            res["category_label"] = "Quantum-Classical Simulation"
            res["compute_type"] = "QAOA with Qiskit Aer/statevector CPU simulation"
            return res
        else:
            logger.warning(f"Unrecognized algorithm '{algo}'. Rejecting unrecognized solver request.")
            raise ValueError(f"Algorithm '{algo}' is not registered in the ROUTE/IQ canonical registry.")

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

    raw_routes = algo_res.get("routes", [])
    if not algo_res.get("success", True) or not raw_routes:
        logger.warning(f"Solver '{algo}' failed or produced no routes: {algo_res.get('error')}")
        algo_res["routes"] = []
        algo_res["total_distance_km"] = 0.0
        algo_res["total_objective_cost"] = 0.0
        algo_res["total_travel_time_min"] = 0.0
        algo_res["resource_metrics"] = res_metrics
        algo_res["execution_time_sec"] = round(res_metrics.get("runtime_ms", 0.0) / 1000.0, 3)
        algo_res["unserved_customers"] = n - 1
        algo_res["served_customers"] = 0
        algo_res["capacity_violations"] = 0
        algo_res["is_feasible"] = False
        algo_res["status"] = "FAILED"
        if not algo_res.get("error"):
            algo_res["error"] = "Solver failed to find a feasible route"
        return algo_res

    # Universal 100% Stop Coverage Repair & Centralized Validation (R == I)
    input_cust_ids = [i for i in range(1, n)]
    repaired_routes, val_report = repair_fleet_coverage(
        raw_routes,
        input_cust_ids,
        adjusted_matrix,
        demands_int,
        capacities,
        num_vehicles,
        depot=0,
        physical_matrix=physical_matrix,
        base_speed_kmh=40.0,
        traffic_factor=traffic_factor,
        weather_factor=weather_factor,
        service_time_per_stop_min=service_time_per_stop_min,
        vehicle_ranges=vehicle_ranges,
        vehicle_profiles=vehicle_profiles,
    )

    for r_idx, route in enumerate(repaired_routes, start=1):
        route["vehicle_id"] = r_idx
        route["total_distance_km"] = route.get("distance_km", 0.0)
        route_stops = route.get("stops", [])

        # Fast leg-based road geometry reconstruction using shared pairwise cache
        route_wps = []
        if len(route_stops) >= 2 and road_network_service.is_ready() and len(snapped_node_ids) >= len(locations):
            for leg_i in range(len(route_stops) - 1):
                su = route_stops[leg_i]
                sv = route_stops[leg_i + 1]
                leg_key = (su, sv)
                if leg_key not in route_geometry_cache:
                    nu = snapped_node_ids[su]
                    nv = snapped_node_ids[sv]
                    nu = str(nu[0]) if isinstance(nu, (tuple, list)) else str(nu)
                    nv = str(nv[0]) if isinstance(nv, (tuple, list)) else str(nv)
                    pts = road_network_service.get_road_path_geometry(nu, nv)
                    if not pts:
                        pts = [(locations[su][0], locations[su][1]), (locations[sv][0], locations[sv][1])]
                    route_geometry_cache[leg_key] = pts

                pts = route_geometry_cache[leg_key]
                step = max(1, len(pts) // 30) if len(pts) > 30 else 1
                start_p = 0 if not route_wps else 1
                for p_idx in range(start_p, len(pts)):
                    is_edge_point = (p_idx == 0 or p_idx == len(pts) - 1)
                    if not is_edge_point and (p_idx % step != 0):
                        continue
                    p_lat, p_lon = pts[p_idx]
                    route_wps.append({
                        "lat": round(float(p_lat), 5),
                        "lon": round(float(p_lon), 5),
                        "type": "depot" if (p_idx == 0 and su == 0) or (p_idx == len(pts) - 1 and sv == 0) else "customer",
                        "index": su if p_idx == 0 else (sv if p_idx == len(pts) - 1 else 0),
                        "is_stop": (p_idx == 0 and su != 0) or (p_idx == len(pts) - 1 and sv != 0),
                    })
            route["waypoints"] = route_wps
        else:
            route["waypoints"] = [
                {
                    "lat": locations[s][0],
                    "lon": locations[s][1],
                    "type": "depot" if s == 0 else "customer",
                    "index": s,
                    "is_stop": True
                }
                for s in route_stops
                if s < len(locations)
            ]

    total_dist = round(float(sum(r["distance_km"] for r in repaired_routes)), 3)
    total_driving_min = round(float(sum(r.get("driving_time_min", (r["distance_km"] / 40.0) * 60.0) for r in repaired_routes)), 2)
    total_service_min = round(float(sum(r.get("service_time_min", 0.0) for r in repaired_routes)), 2)
    total_duration_min = round(total_driving_min + total_service_min, 2)
    combined_env = max(0.1, float(traffic_factor) * float(weather_factor))
    effective_speed = round(float(40.0 / combined_env), 1)
    implied_speed = round(float(total_dist / (total_driving_min / 60.0)), 1) if total_driving_min > 0 else effective_speed
    operational_speed = round(float(total_dist / (total_duration_min / 60.0)), 1) if total_duration_min > 0 else implied_speed

    algo_res["routes"] = repaired_routes
    algo_res["total_distance_km"] = total_dist
    algo_res["total_objective_cost"] = total_dist
    algo_res["total_travel_time_min"] = total_driving_min
    algo_res["driving_duration_min"] = total_driving_min
    algo_res["service_duration_min"] = total_service_min
    algo_res["total_duration_min"] = total_duration_min
    algo_res["implied_speed_kmh"] = implied_speed
    algo_res["operational_speed_kmh"] = operational_speed
    algo_res["speed_model"] = {
        "base_speed_kmh": 40.0,
        "traffic_factor": round(float(traffic_factor), 2),
        "weather_factor": round(float(weather_factor), 2),
        "effective_speed_kmh": effective_speed,
        "service_time_per_stop_min": round(float(service_time_per_stop_min), 2),
        "model_description": "NYC urban road transit model (25 mph statutory speed limit = 40.0 km/h baseline, adjusted for scenario traffic)",
        "includes_service_time": service_time_per_stop_min > 0,
    }
    algo_res["resource_metrics"] = res_metrics
    algo_res["validation_report"] = val_report
    algo_res["execution_time_sec"] = round(res_metrics["runtime_ms"] / 1000.0, 3)

    algo_res["unserved_customers"] = len(val_report["missing_delivery_ids"])
    algo_res["served_customers"] = val_report["visited_delivery_count"]
    algo_res["capacity_violations"] = val_report["capacity_violations"]
    algo_res["is_feasible"] = val_report["is_valid"]
    algo_res["status"] = "SUCCESS" if val_report["is_valid"] else val_report.get("status", "FAILED")

    if "execution_id" not in algo_res:
        algo_res["execution_id"] = str(uuid.uuid4())

    if road_warnings:
        algo_res["warnings"] = list(set(algo_res.get("warnings", []) + road_warnings))

    return algo_res


def _build_comparison_summary(
    to_run: List[str],
    results: Dict[str, Any],
    total_cust_demand: int,
    total_fleet_capacity: int,
    n: int,
    vehicle_profiles: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Build canonical comparison summary items and determine best feasible solution."""
    comparison_items = []
    for algo_key in to_run:
        if algo_key not in results:
            continue
        algo_data = results[algo_key]
        res_m = algo_data.get("resource_metrics", {})
        val = algo_data.get("validation", {})
        is_feas = algo_data.get("is_feasible", val.get("is_feasible", algo_data.get("success", False)))
        cap_viol = algo_data.get("capacity_violations", val.get("capacity_violations", 0))
        unserved = algo_data.get("unserved_customers", val.get("unserved_count", 0))
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
            "driving_duration_min": algo_data.get("driving_duration_min", algo_data.get("total_travel_time_min", 0.0)),
            "service_duration_min": algo_data.get("service_duration_min", 0.0),
            "total_duration_min": algo_data.get("total_duration_min", algo_data.get("total_travel_time_min", 0.0)),
            "implied_speed_kmh": algo_data.get("implied_speed_kmh", 40.0),
            "operational_speed_kmh": algo_data.get("operational_speed_kmh", 40.0),
            "speed_model": algo_data.get("speed_model", {}),
            "total_objective_cost": algo_data.get("total_objective_cost", 0.0),
            "is_feasible": is_feas,
            "capacity_violations": cap_viol,
            "unserved_customers": unserved,
            "served_customers": algo_data.get("served_customers", (n - 1) - unserved),
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

    def _comparison_rank_key(item: Dict[str, Any]) -> Tuple:
        is_feas = (
            item.get("status") not in ("FAILED", "TIMED_OUT", "CANCELLED", "ERROR", "TIMEOUT") and
            not item.get("error") and
            item.get("is_feasible", False) and
            item.get("capacity_violations", 0) == 0 and
            item.get("unserved_customers", 0) == 0 and
            item.get("total_distance_km", 0.0) > 0.0 and
            item.get("vehicles_used", 0) > 0
        )
        feas_rank = 0 if is_feas else 1
        flagship_pref = 0 if item["id"] == "routeiq_cooperative" else 1
        return (
            feas_rank,
            item["unserved_customers"],
            item["capacity_violations"],
            item["total_distance_km"],
            flagship_pref,
            item["total_objective_cost"],
            item["execution_time_sec"]
        )

    comparison_items.sort(key=_comparison_rank_key)

    valid_items = [
        it for it in comparison_items
        if (
            it.get("status") not in ("FAILED", "TIMED_OUT", "CANCELLED", "ERROR", "TIMEOUT") and
            not it.get("error") and
            it.get("is_feasible", False) and
            it.get("capacity_violations", 0) == 0 and
            it.get("unserved_customers", 0) == 0 and
            it.get("total_distance_km", 0.0) > 0.0 and
            it.get("vehicles_used", 0) > 0
        )
    ]

    if valid_items:
        valid_items.sort(key=lambda x: (
            x["total_distance_km"],
            0 if x["id"] == "routeiq_cooperative" else 1,
            x["execution_time_sec"]
        ))
        best_item = valid_items[0]
        best_item["is_best"] = True
        best_reason = f"Lowest route distance ({best_item['total_distance_km']} km) with 100% stop coverage and 0 constraint violations"
        has_feasible = True
    elif comparison_items:
        best_item = None
        has_feasible = False
        if total_cust_demand > total_fleet_capacity:
            best_reason = f"Mathematically infeasible fleet: total customer demand ({total_cust_demand}) exceeds total fleet capacity ({total_fleet_capacity})."
        else:
            best_reason = "No feasible solution found among evaluated algorithms. All requested solvers failed or timed out."
    else:
        best_item = None
        has_feasible = False
        best_reason = "No solutions evaluated"

    summary_data = {
        "best_algorithm": best_item["id"] if best_item else None,
        "best_algorithm_name": best_item["name"] if best_item else None,
        "best_reason": best_reason,
        "best_feasible_distance_km": best_item["total_distance_km"] if best_item else None,
        "has_feasible_solution": has_feasible,
        "items": comparison_items,
    }

    if "routeiq_cooperative" in results and "ortools" in results:
        try:
            summary_data["route_identity_diagnostics"] = compute_route_identity_diagnostics(
                results["routeiq_cooperative"],
                results["ortools"]
            )
        except Exception as diag_err:
            logger.warning(f"Failed to compute route identity diagnostics: {diag_err}")

    # Compute comprehensive energy, fuel, carbon, and economic analysis across all algorithms
    try:
        energy_analysis = compute_full_energy_analysis(
            results=results,
            default_propulsion="diesel",
            baseline_algo="ortools",
            vehicle_capacity=float(total_fleet_capacity or 0.0),
            vehicle_profiles=vehicle_profiles,
        )
        summary_data["energy_analysis"] = energy_analysis

        # Enrich each comparison item with active energy profile metrics
        profiles = energy_analysis.get("profiles", {})
        comparisons = energy_analysis.get("comparisons", {})
        for item in comparison_items:
            a_id = item["id"]
            if a_id in profiles:
                item["energy_metrics"] = profiles[a_id]
            if a_id in comparisons:
                item["energy_comparison"] = comparisons[a_id]
    except Exception as energy_err:
        logger.warning(f"Failed to compute energy analysis: {energy_err}")

    return summary_data


def _format_job_status_response(job: Dict[str, Any]) -> Dict[str, Any]:
    """Format an active in-memory job into a JSON status response with stale-job watchdog."""
    now = time.time()
    elapsed = round(now - job["created_at"], 2) if "created_at" in job else 0.0
    solver_statuses = job.get("solver_statuses", {})
    to_run = job.get("selected_algorithms", [])
    total = len(to_run) if to_run else job.get("total_algorithms", 0)

    # Stale worker watchdog: if a job has had no progress for > 50s and is not completed,
    # finalize any lingering pending/running solvers to prevent frontend from hanging.
    last_update = job.get("updated_at", job.get("created_at", now))
    if job.get("status") in ("PARTIAL", "running", "RUNNING") and (now - last_update > 50.0):
        logger.warning(f"Job {job.get('job_id')} watchdog triggered: no update for {now - last_update:.1f}s. Finalizing.")
        for a in to_run:
            if solver_statuses.get(a) in ("pending", "running", None):
                solver_statuses[a] = "failed"
                job.setdefault("solver_errors", {})[a] = "Execution watchdog: solver exceeded deadline or worker stalled"
                if a not in job.setdefault("results", {}):
                    job["results"][a] = {
                        "success": False,
                        "error": "Execution watchdog: solver exceeded deadline or worker stalled",
                        "routes": [],
                        "status": "FAILED",
                        "execution_time_sec": round(now - last_update, 2),
                        "total_distance_km": 0.0,
                        "total_travel_time_min": 0.0,
                        "total_objective_cost": 0.0,
                        "capacity_violations": 0,
                        "unserved_customers": 0,
                        "served_customers": 0,
                        "is_feasible": False,
                        "algorithm": a,
                        "algorithm_name": a.upper(),
                    }
        job["status"] = "COMPLETED" if job.get("results") else "FAILED"
        job["completed_at"] = now
        job["updated_at"] = now

    results_to_send = dict(job.get("results", {}))

    # Canonical status counts
    successful_count = sum(
        1 for a in to_run
        if (
            solver_statuses.get(a) in ("SUCCESS", "success", "completed", "COMPLETED", "feasible", "FEASIBLE", "supremacy_winner", "SUPREMACY_WINNER", "optimal", "OPTIMAL")
            or (a in results_to_send and results_to_send[a].get("success") and results_to_send[a].get("is_feasible") and len(results_to_send[a].get("routes", [])) > 0)
        )
        and solver_statuses.get(a) not in ("FAILED", "failed", "TIMED_OUT", "timed_out", "TIMEOUT", "timeout", "CANCELLED", "cancelled", "ERROR", "error")
        and not results_to_send.get(a, {}).get("error")
    )
    failed_count = sum(
        1 for a in to_run
        if solver_statuses.get(a) in ("FAILED", "failed", "ERROR", "error")
        or (a in results_to_send and not results_to_send[a].get("success", True) and results_to_send[a].get("status") != "TIMED_OUT")
    )
    timed_out_count = sum(
        1 for a in to_run
        if solver_statuses.get(a) in ("TIMED_OUT", "timed_out", "TIMEOUT", "timeout")
        or (a in results_to_send and results_to_send[a].get("status") == "TIMED_OUT")
    )
    running_count = sum(1 for a in to_run if solver_statuses.get(a) in ("RUNNING", "running"))
    queued_count = sum(1 for a in to_run if solver_statuses.get(a) in ("QUEUED", "queued", "pending", "PENDING", None) and a not in results_to_send)
    evaluated_count = successful_count + failed_count + timed_out_count

    # Non-contradictory progress label
    if running_count > 0 or queued_count > 0:
        parts = [f"{successful_count}/{total} successful"]
        if running_count > 0:
            parts.append(f"{running_count} running")
        if queued_count > 0:
            parts.append(f"{queued_count} queued")
        if failed_count > 0:
            parts.append(f"{failed_count} failed")
        if timed_out_count > 0:
            parts.append(f"{timed_out_count} timed out")
        progress_label = f"Evaluating: {' · '.join(parts)}"
    else:
        if failed_count == 0 and timed_out_count == 0:
            progress_label = f"All {total} algorithms completed successfully."
        elif successful_count > 0:
            fail_details = []
            if failed_count > 0:
                fail_details.append(f"{failed_count} failed")
            if timed_out_count > 0:
                fail_details.append(f"{timed_out_count} timed out")
            progress_label = f"Evaluation completed: {successful_count} successful, {', '.join(fail_details)}."
        else:
            progress_label = f"Evaluation failed: All {total} algorithms failed or timed out."

    return {
        "job_id": job["job_id"],
        "experiment_id": job["experiment_id"],
        "status": job["status"],
        "selection_mode": job.get("selection_mode", "compare"),
        "selected_algorithms": to_run,
        "primary_algorithm": job.get("primary_algorithm", "ortools"),
        "completed_algorithms": successful_count,
        "total_algorithms": total,
        "successful_count": successful_count,
        "completed_count": successful_count,
        "evaluated_count": evaluated_count,
        "failed_count": failed_count,
        "timed_out_count": timed_out_count,
        "running_count": running_count,
        "queued_count": queued_count,
        "pending_count": queued_count,
        "progress_label": progress_label,
        "solver_statuses": solver_statuses,
        "solver_errors": job.get("solver_errors", {}),
        "results": results_to_send,
        "comparison_summary": job.get("comparison_summary", {}),
        "problem": job.get("problem", {}),
        "is_cancelled": job.get("is_cancelled", False),
        "error": job.get("error"),
        "elapsed_sec": elapsed,
    }


async def _run_background_solvers_for_job(
    job_id: str,
    experiment_id: str,
    to_run: List[str],
    primary_algo: str,
    n: int,
    num_vehicles: int,
    vehicle_capacity: float,
    classical_time_limit_sec: int,
    qaoa_depth: int,
    qaoa_shots: int,
    qaoa_optimizer: str,
    qaoa_penalty: float,
    random_seed: int,
    locations: List[Tuple[float, float]],
    demands_int: List[int],
    capacities: List[int],
    adjusted_matrix: np.ndarray,
    objective_weights: Dict[str, float],
    snapped_node_ids: List[int],
    road_warnings: List[str],
    total_cust_demand: int,
    total_fleet_capacity: int,
    route_geometry_cache: Dict[Tuple[int, ...], List[Dict[str, Any]]],
    physical_matrix: Optional[np.ndarray] = None,
    traffic_factor: float = 1.0,
    weather_factor: float = 1.0,
    service_time_per_stop_min: float = 0.0,
    vehicle_ranges: Optional[List[float]] = None,
    vehicle_profiles: Optional[List[Dict[str, Any]]] = None,
):
    """Progressive background solver worker executing remaining comparison algorithms with guaranteed terminal completion."""
    async with _job_semaphore:
        job = _active_jobs.get(job_id)
        if not job:
            return

        remaining_algos = [a for a in to_run if a != primary_algo]
        try:
            for algo in remaining_algos:
                if job.get("is_cancelled"):
                    logger.info(f"Job {job_id} cancelled by user/superseded. Terminating remaining solvers.")
                    break

                job["solver_statuses"][algo] = "running"
                job["updated_at"] = time.time()
                # Yield to event loop so status polling requests are served with sub-5ms latency
                await asyncio.sleep(0.05)

                try:
                    if algo == "qaoa":
                        # Timeout safeguard: max 35.0s for QAOA statevector simulation
                        try:
                            algo_res = await asyncio.wait_for(
                                asyncio.to_thread(
                                    _solve_single_algo,
                                    algo, n, num_vehicles, vehicle_capacity,
                                    classical_time_limit_sec, qaoa_depth, qaoa_shots,
                                    qaoa_optimizer, qaoa_penalty, random_seed,
                                    locations, demands_int, capacities, adjusted_matrix,
                                    objective_weights, snapped_node_ids, road_warnings,
                                    route_geometry_cache,
                                    physical_matrix,
                                    traffic_factor,
                                    weather_factor,
                                    service_time_per_stop_min,
                                    vehicle_ranges,
                                    vehicle_profiles,
                                ),
                                timeout=35.0
                            )
                        except asyncio.TimeoutError:
                            logger.warning(f"QAOA statevector simulation timed out after 35.0s for job {job_id}")
                            algo_res = {
                                "success": False,
                                "error": "QAOA statevector CPU simulation timed out (35.0s deadline)",
                                "routes": [],
                                "status": "TIMED_OUT",
                                "execution_time_sec": 35.0,
                                "total_distance_km": 0.0,
                                "total_travel_time_min": 0.0,
                                "total_objective_cost": 0.0,
                                "capacity_violations": 0,
                                "unserved_customers": n - 1,
                                "served_customers": 0,
                                "is_feasible": False,
                                "algorithm": "qaoa",
                                "algorithm_name": "QAOA Hybrid",
                                "category": "quantum_hybrid",
                                "category_label": "Quantum-Classical Simulation",
                                "compute_type": "QAOA with Qiskit Aer/statevector CPU simulation",
                            }
                    else:
                        try:
                            algo_res = await asyncio.wait_for(
                                asyncio.to_thread(
                                    _solve_single_algo,
                                    algo, n, num_vehicles, vehicle_capacity,
                                    classical_time_limit_sec, qaoa_depth, qaoa_shots,
                                    qaoa_optimizer, qaoa_penalty, random_seed,
                                    locations, demands_int, capacities, adjusted_matrix,
                                    objective_weights, snapped_node_ids, road_warnings,
                                    route_geometry_cache,
                                    physical_matrix,
                                    traffic_factor,
                                    weather_factor,
                                    service_time_per_stop_min,
                                    vehicle_ranges,
                                    vehicle_profiles,
                                ),
                                timeout=45.0
                            )
                        except asyncio.TimeoutError:
                            logger.warning(f"Solver {algo} timed out after 45s for job {job_id}")
                            algo_res = {
                                "success": False,
                                "error": f"Solver execution timed out (45.0s deadline)",
                                "routes": [],
                                "status": "TIMED_OUT",
                                "execution_time_sec": 45.0,
                                "total_distance_km": 0.0,
                                "total_travel_time_min": 0.0,
                                "total_objective_cost": 0.0,
                                "capacity_violations": 0,
                                "unserved_customers": n - 1,
                                "served_customers": 0,
                                "is_feasible": False,
                                "algorithm": algo,
                                "algorithm_name": algo.upper(),
                            }

                    job["results"][algo] = algo_res
                    if algo_res.get("status") == "TIMED_OUT":
                        job["solver_statuses"][algo] = "TIMED_OUT"
                        job["solver_errors"][algo] = algo_res.get("error")
                    elif algo_res.get("success", False) and algo_res.get("is_feasible", False) and len(algo_res.get("routes", [])) > 0:
                        job["solver_statuses"][algo] = "SUCCESS"
                    else:
                        job["solver_statuses"][algo] = "FAILED"
                        if algo_res.get("error"):
                            job["solver_errors"][algo] = algo_res.get("error")
                    job["completed_algorithms"] = sum(1 for a in to_run if job.get("solver_statuses", {}).get(a) == "SUCCESS")

                except Exception as exc:
                    logger.error(f"Solver {algo} raised exception in background job {job_id}: {exc}")
                    job["results"][algo] = {
                        "success": False,
                        "error": str(exc),
                        "routes": [],
                        "status": "FAILED",
                        "execution_time_sec": 0.0,
                        "total_distance_km": 0.0,
                        "total_travel_time_min": 0.0,
                        "total_objective_cost": 0.0,
                        "capacity_violations": 0,
                        "unserved_customers": n - 1,
                        "served_customers": 0,
                        "is_feasible": False,
                        "algorithm": algo,
                        "algorithm_name": algo.upper(),
                    }
                    job["solver_statuses"][algo] = "FAILED"
                    job["solver_errors"][algo] = str(exc)
                    job["completed_algorithms"] = sum(1 for a in to_run if job.get("solver_statuses", {}).get(a) == "SUCCESS")
                finally:
                    gc.collect()
                    curr_rss = _get_process_memory_mb()
                    if curr_rss > 485.0:
                        logger.info(f"Memory threshold exceeded ({curr_rss} MB > 485 MB). Evicting transient road caches.")
                        road_network_service.clear_transient_caches()
                        gc.collect()
                        try:
                            import ctypes
                            ctypes.CDLL("libc.so.6").malloc_trim(0)
                        except Exception:
                            pass

                # Update comparison summary incrementally after each finished algorithm (protected against unhandled exceptions)
                try:
                    job["comparison_summary"] = _build_comparison_summary(
                        to_run, job["results"], total_cust_demand, total_fleet_capacity, n
                    )
                except Exception as sum_err:
                    logger.warning(f"Failed to update incremental comparison summary for {algo}: {sum_err}")
                job["updated_at"] = time.time()

                # Incrementally persist result to DB so data survives any interruption
                try:
                    from app.db.session import async_session_factory
                    async with async_session_factory() as session:
                        exp_stmt = select(Experiment).where(Experiment.id == experiment_id)
                        exp_res = await session.execute(exp_stmt)
                        exp = exp_res.scalar_one_or_none()
                        if exp:
                            a_res = job["results"].get(algo, {})
                            er = ExperimentResult(
                                experiment_id=exp.id,
                                algorithm=algo,
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
                            )
                            session.add(er)
                            await session.commit()
                except Exception as inc_err:
                    logger.debug(f"Incremental DB persist note: {inc_err}")

                # Yield to event loop
                await asyncio.sleep(0.05)

        except Exception as outer_worker_err:
            logger.error(f"Background worker encountered unexpected fatal error in job {job_id}: {outer_worker_err}")
        finally:
            # ── GUARANTEED TERMINAL COMPLETION ──
            # Ensure every single requested algorithm reaches a final terminal state.
            # Never leave any algorithm in 'pending' or 'running'.
            is_cancelled = job.get("is_cancelled", False)
            for a in to_run:
                curr_s = job["solver_statuses"].get(a, "pending")
                if curr_s in ("pending", "running", None):
                    if is_cancelled:
                        job["solver_statuses"][a] = "CANCELLED"
                    else:
                        job["solver_statuses"][a] = "FAILED"
                        job.setdefault("solver_errors", {})[a] = "Worker terminated before solver execution"
                        if a not in job["results"]:
                            job["results"][a] = {
                                "success": False,
                                "error": "Worker terminated before solver execution",
                                "routes": [],
                                "status": "FAILED",
                                "execution_time_sec": 0.0,
                                "total_distance_km": 0.0,
                                "total_travel_time_min": 0.0,
                                "total_objective_cost": 0.0,
                                "capacity_violations": 0,
                                "unserved_customers": n - 1,
                                "served_customers": 0,
                                "is_feasible": False,
                                "algorithm": a,
                                "algorithm_name": a.upper(),
                            }

            job["completed_algorithms"] = sum(1 for a in to_run if job.get("solver_statuses", {}).get(a) == "SUCCESS")
            statuses = [job.get("solver_statuses", {}).get(a) for a in to_run]
            any_success = any(s in ("completed", "success", "COMPLETED", "SUCCESS") for s in statuses)
            all_success = all(s in ("completed", "success", "COMPLETED", "SUCCESS") for s in statuses)

            if is_cancelled:
                job["status"] = "CANCELLED"
            elif all_success:
                job["status"] = "COMPLETED"
            elif any_success:
                job["status"] = "COMPLETED_WITH_FAILURES"
            else:
                job["status"] = "FAILED"

            job["completed_at"] = time.time()
            job["updated_at"] = time.time()

            try:
                job["comparison_summary"] = _build_comparison_summary(
                    to_run, job["results"], total_cust_demand, total_fleet_capacity, n,
                    vehicle_profiles=vehicle_profiles
                )
            except Exception as final_sum_err:
                logger.warning(f"Final summary build error: {final_sum_err}")

            # Ensure every single result in job["results"] is persisted to DB before committing final status
            try:
                from app.db.session import async_session_factory
                async with async_session_factory() as session:
                    exp_stmt = select(Experiment).where(Experiment.id == experiment_id)
                    exp_res = await session.execute(exp_stmt)
                    exp = exp_res.scalar_one_or_none()
                    if exp:
                        res_stmt = select(ExperimentResult.algorithm).where(ExperimentResult.experiment_id == experiment_id)
                        existing_algos = set((await session.execute(res_stmt)).scalars().all())
                        for a in to_run:
                            if a in job.get("results", {}) and a not in existing_algos:
                                a_res = job["results"][a]
                                er = ExperimentResult(
                                    experiment_id=exp.id,
                                    algorithm=a,
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
                                )
                                session.add(er)
                        exp.status = job["status"]
                        await session.commit()
            except Exception as db_err:
                logger.warning(f"Could not finalize results & status in database: {db_err}")

            _evict_old_active_jobs()
            gc.collect()
            try:
                import ctypes
                ctypes.CDLL("libc.so.6").malloc_trim(0)
            except Exception:
                pass


# ─── Optimization Job Endpoints ──────────────────────────────────

@router.post("/optimization/jobs")
async def start_optimization_job(
    req: OptimizationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Asynchronous Optimization Job Runner.
    Computes first feasible route immediately (< 2.0s), returns job_id and status 'PARTIAL',
    and evaluates remaining comparison algorithms incrementally in the background.
    """
    t0 = time.time()
    (
        locations, demands, n, adjusted_matrix, snapped_node_ids,
        road_warnings, physical_matrix, objective_weights, demands_int,
        total_cust_demand, total_fleet_capacity, capacities,
        traffic_factor, weather_factor, num_dispatch_vehicles,
        vehicle_ranges, usable_vehicle_profiles
    ) = _prepare_optimization_problem(req)

    to_run, mode = _resolve_algorithms_to_run(req, n)
    if "routeiq_cooperative" in to_run:
        primary_algo = "routeiq_cooperative"
    elif mode == "compare" and "ortools" in to_run:
        primary_algo = "ortools"
    else:
        primary_algo = to_run[0] if to_run else "ortools"

    job_id = str(uuid.uuid4())
    now_utc = datetime.now(timezone.utc)
    experiment = Experiment(
        id=job_id,
        name=f"Job {now_utc.strftime('%Y%m%d_%H%M%S')}",
        timestamp=now_utc,
        algorithm=",".join(to_run),
        num_customers=req.num_customers,
        num_vehicles=num_dispatch_vehicles,
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
    await db.commit()

    # Cancel any older running jobs in _active_jobs to release resources and prevent worker queue blocking
    for old_jid, old_j in list(_active_jobs.items()):
        if old_j.get("status") in ("PARTIAL", "running", "RUNNING"):
            logger.info(f"Superseding older running job {old_jid} with new job {job_id}")
            old_j["is_cancelled"] = True

    route_geometry_cache: Dict[Tuple[int, ...], List[Dict[str, Any]]] = {}

    # Solve primary algorithm immediately (< 1.5s responsive deadline)
    primary_res = _solve_single_algo(
        primary_algo, n, num_dispatch_vehicles, req.vehicle_capacity,
        min(req.classical_time_limit_sec, 1), req.qaoa_depth, req.qaoa_shots,
        req.qaoa_optimizer, req.qaoa_penalty, req.random_seed,
        locations, demands_int, capacities, adjusted_matrix,
        objective_weights, snapped_node_ids, road_warnings,
        route_geometry_cache,
        physical_matrix,
        traffic_factor,
        weather_factor,
        req.service_time_per_stop_min,
        vehicle_ranges,
        usable_vehicle_profiles,
    )

    # Immediately persist primary algorithm result to database so it is NEVER missing in DB queries
    try:
        primary_er = ExperimentResult(
            experiment_id=experiment.id,
            algorithm=primary_algo,
            total_distance_km=primary_res.get("total_distance_km", 0.0),
            total_travel_time_min=primary_res.get("total_travel_time_min", 0.0),
            total_objective_cost=primary_res.get("total_objective_cost", 0.0),
            execution_time_sec=primary_res.get("execution_time_sec", 0.0),
            is_feasible=primary_res.get("is_feasible", False),
            capacity_violations=primary_res.get("capacity_violations", 0),
            unserved_customers=primary_res.get("unserved_customers", 0),
            routes=primary_res.get("routes", []),
            solver_log=primary_res.get("solver_log", ""),
            warnings=primary_res.get("warnings", []),
        )
        db.add(primary_er)
        await db.commit()
    except Exception as db_err:
        logger.warning(f"Could not persist primary solver result to database: {db_err}")
        await db.rollback()

    results = {primary_algo: primary_res}
    if primary_algo == "ortools":
        results["classical"] = primary_res

    solver_statuses = {a: "QUEUED" for a in to_run}
    is_primary_valid = (
        primary_res.get("success", False)
        and primary_res.get("is_feasible", False)
        and len(primary_res.get("routes", [])) > 0
    )
    solver_statuses[primary_algo] = "SUCCESS" if is_primary_valid else "FAILED"

    initial_summary = _build_comparison_summary(
        to_run, results, total_cust_demand, total_fleet_capacity, n,
        vehicle_profiles=usable_vehicle_profiles
    )

    is_single = len(to_run) <= 1
    initial_status = "COMPLETED" if (is_single and is_primary_valid) else ("FAILED" if (is_single and not is_primary_valid) else "PARTIAL")

    problem_dict = {
        "num_customers": n - 1,
        "num_vehicles": num_dispatch_vehicles,
        "depot": {"lat": locations[0][0], "lon": locations[0][1]},
        "traffic_factor": traffic_factor,
        "weather_factor": weather_factor,
        "vehicle_profiles": usable_vehicle_profiles,
        "locations": [{"lat": l[0], "lon": l[1], "demand": d}
                      for l, d in zip(locations, demands)],
    }

    primary_succ_count = 1 if is_primary_valid else 0
    primary_fail_count = 0 if is_primary_valid else 1

    job_record = {
        "job_id": job_id,
        "experiment_id": experiment.id,
        "status": initial_status,
        "selection_mode": mode,
        "selected_algorithms": to_run,
        "primary_algorithm": primary_algo,
        "completed_algorithms": primary_succ_count,
        "total_algorithms": len(to_run),
        "successful_count": primary_succ_count,
        "completed_count": primary_succ_count,
        "evaluated_count": 1,
        "failed_count": primary_fail_count,
        "timed_out_count": 0,
        "running_count": 0,
        "queued_count": max(0, len(to_run) - 1),
        "pending_count": max(0, len(to_run) - 1),
        "solver_statuses": solver_statuses,
        "solver_errors": {},
        "results": results,
        "comparison_summary": initial_summary,
        "problem": problem_dict,
        "is_cancelled": False,
        "created_at": time.time(),
        "updated_at": time.time(),
        "completed_at": time.time() if is_single else None,
        "error": None,
    }
    _active_jobs[job_id] = job_record
    _evict_old_active_jobs()

    # If comparison suite, launch progressive background worker
    if not is_single:
        asyncio.create_task(
            _run_background_solvers_for_job(
                job_id, experiment.id, to_run, primary_algo,
                n, num_dispatch_vehicles, req.vehicle_capacity,
                req.classical_time_limit_sec, req.qaoa_depth, req.qaoa_shots,
                req.qaoa_optimizer, req.qaoa_penalty, req.random_seed,
                locations, demands_int, capacities, adjusted_matrix,
                objective_weights, snapped_node_ids, road_warnings,
                total_cust_demand, total_fleet_capacity,
                route_geometry_cache,
                physical_matrix,
                traffic_factor,
                weather_factor,
                req.service_time_per_stop_min,
                vehicle_ranges,
                usable_vehicle_profiles,
            )
        )

    primary_name = primary_res.get("algorithm_name", primary_algo.upper())
    primary_dist = primary_res.get("total_distance_km", 0.0)
    primary_lat = round(time.time() - t0, 3)

    return {
        "job_id": job_id,
        "experiment_id": experiment.id,
        "status": initial_status,
        "selection_mode": mode,
        "selected_algorithms": to_run,
        "primary_algorithm": primary_algo,
        "completed_algorithms": primary_succ_count,
        "total_algorithms": len(to_run),
        "successful_count": primary_succ_count,
        "completed_count": primary_succ_count,
        "evaluated_count": 1,
        "failed_count": primary_fail_count,
        "timed_out_count": 0,
        "running_count": 0,
        "queued_count": max(0, len(to_run) - 1),
        "pending_count": max(0, len(to_run) - 1),
        "primary_latency_sec": primary_lat,
        "solver_statuses": solver_statuses,
        "results": results,
        "comparison_summary": initial_summary,
        "problem": problem_dict,
        "message": f"First feasible route ready in {primary_lat}s via {primary_name} ({primary_dist} km)." if is_primary_valid else f"Primary solver {primary_name} failed: {primary_res.get('error', 'Infeasible solution')}.",
    }


async def _get_optional_db():
    return None


@router.get("/optimization/jobs/{job_id}/status")
async def get_optimization_job_status(
    job_id: str,
    db: Optional[AsyncSession] = Depends(_get_optional_db),
):
    """Retrieve real-time status, incremental solver results, and progress metrics for an optimization job."""
    real_db = db if isinstance(db, AsyncSession) else None
    if job_id == "latest":
        if _active_jobs:
            latest_id = max(_active_jobs.keys(), key=lambda k: _active_jobs[k].get("created_at", 0))
            job = _active_jobs[latest_id]
            return _format_job_status_response(job)
        if real_db is not None:
            stmt = select(Experiment).order_by(Experiment.timestamp.desc()).limit(1)
            res = await real_db.execute(stmt)
            latest_exp = res.scalar_one_or_none()
            if latest_exp:
                job_id = latest_exp.id
            else:
                raise HTTPException(404, "No optimization jobs found.")
        else:
            from app.db.session import async_session_factory
            async with async_session_factory() as session:
                stmt = select(Experiment).order_by(Experiment.timestamp.desc()).limit(1)
                res = await session.execute(stmt)
                latest_exp = res.scalar_one_or_none()
                if latest_exp:
                    job_id = latest_exp.id
                else:
                    raise HTTPException(404, "No optimization jobs found.")

    if job_id in _active_jobs:
        job = _active_jobs[job_id]
        return _format_job_status_response(job)

    # Check database only if not in memory (e.g. process restart)
    if real_db is not None:
        exp_stmt = select(Experiment).where(Experiment.id == job_id)
        exp_res = await real_db.execute(exp_stmt)
        exp = exp_res.scalar_one_or_none()
        if not exp:
            raise HTTPException(404, f"Optimization job '{job_id}' not found.")

        res_stmt = select(ExperimentResult).where(ExperimentResult.experiment_id == job_id)
        res_rows = (await real_db.execute(res_stmt)).scalars().all()
        results = {r.algorithm: _result_to_dict(r) for r in res_rows}
        to_run = exp.algorithm.split(",") if exp.algorithm else list(results.keys())
    else:
        from app.db.session import async_session_factory
        async with async_session_factory() as session:
            exp_stmt = select(Experiment).where(Experiment.id == job_id)
            exp_res = await session.execute(exp_stmt)
            exp = exp_res.scalar_one_or_none()
            if not exp:
                raise HTTPException(404, f"Optimization job '{job_id}' not found.")

            res_stmt = select(ExperimentResult).where(ExperimentResult.experiment_id == job_id)
            res_rows = (await session.execute(res_stmt)).scalars().all()
            results = {r.algorithm: _result_to_dict(r) for r in res_rows}
            to_run = exp.algorithm.split(",") if exp.algorithm else list(results.keys())
    exp_status = (exp.status or "COMPLETED").upper()
    total = len(to_run)

    # Stale/Orphaned DB experiment watchdog:
    # If the experiment in DB is marked PARTIAL or RUNNING, but it is not currently active
    # in _active_jobs, then the process or worker running it died or was restarted.
    # Automatically resolve it to terminal state to prevent clients from hanging indefinitely.
    if exp_status in ("PARTIAL", "RUNNING", "running"):
        now_utc = datetime.now(timezone.utc)
        exp_time = exp.timestamp.replace(tzinfo=timezone.utc) if exp.timestamp and exp.timestamp.tzinfo is None else (exp.timestamp or now_utc)
        age_sec = (now_utc - exp_time).total_seconds()
        if age_sec > 40.0 or job_id not in _active_jobs:
            logger.info(f"Finalizing orphaned job {job_id} in database (age: {age_sec:.1f}s, not in active memory).")
            exp_status = "COMPLETED" if len(results) > 0 else "FAILED"
            exp.status = exp_status
            try:
                if real_db is not None:
                    await real_db.commit()
                else:
                    async with async_session_factory() as session:
                        e = await session.get(Experiment, exp.id)
                        if e:
                            e.status = exp_status
                            await session.commit()
            except Exception as upd_err:
                logger.debug(f"Failed to commit finalized status for orphaned exp: {upd_err}")

    # Build comprehensive solver status for every algorithm requested
    statuses = {}
    for a in to_run:
        if a in results:
            r = results[a]
            if r.get("status") == "TIMED_OUT":
                statuses[a] = "TIMED_OUT"
            elif r.get("success", False) and r.get("is_feasible", False) and len(r.get("routes", [])) > 0:
                statuses[a] = "SUCCESS"
            else:
                statuses[a] = "FAILED"
        else:
            if exp_status in ("COMPLETED", "FAILED", "CANCELLED"):
                statuses[a] = "FAILED"
            else:
                statuses[a] = "QUEUED"

    successful_count = sum(1 for s in statuses.values() if s == "SUCCESS")
    failed_count = sum(1 for s in statuses.values() if s in ("FAILED", "ERROR"))
    timed_out_count = sum(1 for s in statuses.values() if s in ("TIMED_OUT", "TIMEOUT"))
    running_count = sum(1 for s in statuses.values() if s == "RUNNING")
    queued_count = sum(1 for s in statuses.values() if s in ("QUEUED", "PENDING", "pending"))
    evaluated_count = successful_count + failed_count + timed_out_count

    if running_count > 0 or queued_count > 0:
        parts = [f"{successful_count}/{total} successful"]
        if running_count > 0:
            parts.append(f"{running_count} running")
        if queued_count > 0:
            parts.append(f"{queued_count} queued")
        if failed_count > 0:
            parts.append(f"{failed_count} failed")
        if timed_out_count > 0:
            parts.append(f"{timed_out_count} timed out")
        progress_label = f"Evaluating: {' · '.join(parts)}"
    else:
        if failed_count == 0 and timed_out_count == 0:
            progress_label = f"All {total} algorithms completed successfully."
        elif successful_count > 0:
            fail_details = []
            if failed_count > 0:
                fail_details.append(f"{failed_count} failed")
            if timed_out_count > 0:
                fail_details.append(f"{timed_out_count} timed out")
            progress_label = f"Evaluation completed: {successful_count} successful, {', '.join(fail_details)}."
        else:
            progress_label = f"Evaluation failed: All {total} algorithms failed or timed out."

    return {
        "job_id": job_id,
        "experiment_id": exp.id,
        "status": exp_status,
        "selection_mode": "compare",
        "selected_algorithms": to_run,
        "primary_algorithm": to_run[0] if to_run else "ortools",
        "completed_algorithms": successful_count,
        "total_algorithms": total,
        "successful_count": successful_count,
        "completed_count": successful_count,
        "evaluated_count": evaluated_count,
        "failed_count": failed_count,
        "timed_out_count": timed_out_count,
        "running_count": running_count,
        "queued_count": queued_count,
        "pending_count": queued_count,
        "progress_label": progress_label,
        "solver_statuses": statuses,
        "solver_errors": {},
        "results": results,
        "comparison_summary": _build_comparison_summary(to_run, results, 0, 0, exp.num_customers or 19) if results else {},
        "problem": {
            "num_customers": exp.num_customers,
            "num_vehicles": exp.num_vehicles,
            "depot_lat": exp.depot_lat,
            "depot_lon": exp.depot_lon,
            "vehicle_capacity": exp.vehicle_capacity,
        },
        "is_cancelled": exp_status == "CANCELLED",
        "error": exp.error_message or ("Process interrupted by server restart" if exp_status == "INTERRUPTED" else None),
        "elapsed_sec": 0.0,
    }


@router.post("/optimization/jobs/{job_id}/cancel")
async def cancel_optimization_job(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Cancel an active optimization job."""
    if job_id in _active_jobs:
        job = _active_jobs[job_id]
        job["is_cancelled"] = True
        job["status"] = "CANCELLED"
        job["updated_at"] = time.time()
        for algo, st in job["solver_statuses"].items():
            if st in ("pending", "running"):
                job["solver_statuses"][algo] = "cancelled"

        try:
            exp_stmt = select(Experiment).where(Experiment.id == job["experiment_id"])
            exp_res = await db.execute(exp_stmt)
            exp = exp_res.scalar_one_or_none()
            if exp:
                exp.status = "cancelled"
                await db.commit()
        except Exception:
            pass

        return {
            "job_id": job_id,
            "status": "CANCELLED",
            "message": "Optimization job cancelled successfully.",
        }

    exp_stmt = select(Experiment).where(Experiment.id == job_id)
    exp_res = await db.execute(exp_stmt)
    exp = exp_res.scalar_one_or_none()
    if exp:
        exp.status = "cancelled"
        await db.commit()
        return {
            "job_id": job_id,
            "status": "CANCELLED",
            "message": "Optimization experiment marked as cancelled in database.",
        }

    raise HTTPException(404, f"Job '{job_id}' not found.")


# ─── Synchronous Run Endpoint (Backward-Compatible) ──────────────

@router.post("/optimization/run")
async def run_optimization(
    req: OptimizationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Run optimization with specified algorithm or comparison suite synchronously."""
    t0 = time.time()
    (
        locations, demands, n, adjusted_matrix, snapped_node_ids,
        road_warnings, physical_matrix, objective_weights, demands_int,
        total_cust_demand, total_fleet_capacity, capacities,
        traffic_factor, weather_factor, num_dispatch_vehicles,
        vehicle_ranges, usable_vehicle_profiles
    ) = _prepare_optimization_problem(req)

    to_run, mode = _resolve_algorithms_to_run(req, n)

    # Create experiment record
    now_utc = datetime.now(timezone.utc)
    experiment = Experiment(
        id=str(uuid.uuid4()),
        name=f"Optimization {now_utc.strftime('%Y%m%d_%H%M%S')}",
        timestamp=now_utc,
        algorithm=",".join(to_run),
        num_customers=req.num_customers,
        num_vehicles=num_dispatch_vehicles,
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
    route_geometry_cache: Dict[Tuple[int, ...], List[Dict[str, Any]]] = {}

    try:
        for a in to_run:
            try:
                results[a] = _solve_single_algo(
                    a, n, num_dispatch_vehicles, req.vehicle_capacity,
                    req.classical_time_limit_sec, req.qaoa_depth, req.qaoa_shots,
                    req.qaoa_optimizer, req.qaoa_penalty, req.random_seed,
                    locations, demands_int, capacities, adjusted_matrix,
                    objective_weights, snapped_node_ids, road_warnings,
                    route_geometry_cache,
                    physical_matrix,
                    traffic_factor,
                    weather_factor,
                    req.service_time_per_stop_min,
                    vehicle_ranges,
                    usable_vehicle_profiles,
                )
            except Exception as exc:
                logger.error(f"Solver for {a} raised: {exc}")
                results[a] = {
                    "success": False,
                    "error": str(exc),
                    "routes": [],
                    "status": "FAILED",
                    "execution_time_sec": 0.0,
                    "total_distance_km": 0.0,
                    "total_travel_time_min": 0.0,
                    "total_objective_cost": 0.0,
                    "capacity_violations": 0,
                    "unserved_customers": n - 1,
                    "served_customers": 0,
                    "is_feasible": False,
                    "algorithm": a,
                    "algorithm_name": a.upper(),
                }
            finally:
                gc.collect()
            await asyncio.sleep(0.01)

        # Persist results
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

        summary = _build_comparison_summary(
            to_run, results, total_cust_demand, total_fleet_capacity, n,
            vehicle_profiles=usable_vehicle_profiles
        )

        if "ortools" in results and "classical" not in results:
            results["classical"] = results["ortools"]

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
            "best_feasible_algorithm": summary["best_algorithm"],
            "comparison_summary": summary,
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
        df = data_processor.customers_df.head(max(limit * 3, 200)).copy()
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


ALGO_CANONICAL_METADATA: Dict[str, Tuple[str, str, str, str]] = {
    "routeiq_cooperative": (
        "ROUTE/IQ Cooperative Engine",
        "cooperative",
        "Cooperative Hybrid (Spark Local + Classical + QAOA CPU Sim)",
        "Hybrid (Spark + QAOA + Adaptive Deep VND + ALNS)",
    ),
    "ortools": (
        "OR-Tools (CVRP)",
        "classical",
        "Classical",
        "Classical CPU",
    ),
    "clarke_wright": (
        "Clarke–Wright Savings",
        "classical",
        "Classical",
        "Classical CPU",
    ),
    "two_opt": (
        "2-opt Improvement",
        "classical",
        "Classical",
        "Classical CPU",
    ),
    "dijkstra": (
        "Dijkstra Shortest-Path",
        "classical",
        "Classical",
        "Classical CPU",
    ),
    "astar": (
        "A* Heuristic Search",
        "classical",
        "Classical",
        "Classical CPU",
    ),
    "tabu_search": (
        "Tabu Search Metaheuristic",
        "classical",
        "Classical",
        "Classical CPU",
    ),
    "kernighan_lin": (
        "Kernighan–Lin Bipartition",
        "classical",
        "Classical",
        "Classical CPU",
    ),
    "vnd": (
        "Variable Neighborhood Descent (VND)",
        "classical",
        "Classical",
        "Classical CPU",
    ),
    "qiga": (
        "Quantum-Inspired GA (QIGA/IQGA)",
        "quantum_inspired",
        "Quantum-Inspired Classical",
        "Classically Simulated Q-Bits (Classical CPU)",
    ),
    "qaoa": (
        "QAOA Hybrid",
        "quantum_hybrid",
        "Quantum-Classical Simulation",
        "QAOA with Qiskit Aer/statevector CPU simulation",
    ),
}


def _result_to_dict(r: ExperimentResult) -> dict:
    meta = ALGO_CANONICAL_METADATA.get(
        r.algorithm,
        (r.algorithm.upper(), "classical", "Classical", "Classical CPU")
    )
    dist = r.total_distance_km or 0.0
    tt_min = r.total_travel_time_min or 0.0
    driving_min = tt_min
    routes = r.routes or []
    srv_min = round(float(sum(rt.get("service_time_min", 0.0) for rt in routes)), 2)
    tot_duration = round(driving_min + srv_min, 2)
    imp_speed = round(float(dist / (driving_min / 60.0)), 1) if driving_min > 0 else 40.0
    op_speed = round(float(dist / (tot_duration / 60.0)), 1) if tot_duration > 0 else imp_speed

    return {
        "id": r.id,
        "algorithm": r.algorithm,
        "algorithm_name": meta[0],
        "category": meta[1],
        "category_label": meta[2],
        "compute_type": meta[3],
        "status": "COMPLETED" if r.is_feasible else ("FAILED" if (r.total_distance_km or 0) == 0 else "PENALIZED"),
        "total_distance_km": r.total_distance_km,
        "total_travel_time_min": r.total_travel_time_min,
        "driving_duration_min": driving_min,
        "service_duration_min": srv_min,
        "total_duration_min": tot_duration,
        "implied_speed_kmh": imp_speed,
        "operational_speed_kmh": op_speed,
        "speed_model": {
            "base_speed_kmh": 40.0,
            "effective_speed_kmh": imp_speed,
            "model_description": "NYC urban road transit model (25 mph statutory speed limit = 40.0 km/h baseline, adjusted for scenario traffic)",
        },
        "total_objective_cost": r.total_objective_cost,
        "execution_time_sec": r.execution_time_sec,
        "is_feasible": r.is_feasible,
        "capacity_violations": r.capacity_violations,
        "unserved_customers": r.unserved_customers,
        "routes": routes,
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
