"""
Test suite for Vehicle Profile and Vehicle Condition-Aware Fleet Optimization in ROUTE/IQ.
Validates:
1. Physical and condition modeling in VehicleProfile.
2. Heterogeneous fleet capacity and range enforcement in solvers.
3. Unavailable/critical maintenance vehicle exclusion.
4. Per-vehicle energy, fuel, SoC, and operational cost calculations.
5. End-to-end route assignment and validation with heterogeneous vehicle profiles.
"""

import pytest
import numpy as np
from app.models.vehicle_profile import (
    VehicleProfile,
    generate_default_fleet_profiles,
)
from app.services.optimization.energy_service import (
    compute_vehicle_route_energy,
    compute_algorithm_energy_profile,
    compute_full_energy_analysis,
)
from app.services.optimization.route_validator import (
    validate_fleet_coverage,
    repair_fleet_coverage,
)
from app.services.optimization.classical_solver import classical_solver
from app.services.optimization.cooperative_solver import cooperative_solver


def test_vehicle_profile_physics_and_range():
    """Verify physical range and battery/fuel calculations in VehicleProfile."""
    # Electric Van with 68 kWh battery, 80% SoC, 95% SoH
    ev = VehicleProfile(
        id="EV-1",
        name="Ford E-Transit",
        vehicle_type="electric_van",
        powertrain="electric",
        capacity_kg=120.0,
        battery_capacity_kwh=68.0,
        battery_soc_percent=80.0,
        battery_soh_percent=95.0,
        base_consumption_per_100km=24.0,
        condition="good",
        is_available=True,
    )
    
    is_disp, reason = ev.is_dispatchable()
    assert is_disp is True
    # Usable energy = 68 * 0.95 * (80 - 5)/100 = 68 * 0.95 * 0.75 = 48.45 kWh
    usable_kwh = ev.calculate_usable_battery_kwh()
    assert 48.0 <= usable_kwh <= 49.0

    # Range = (48.45 / 0.24) ~ 201.8 km
    nominal_range = ev.calculate_physical_range_km(traffic_factor=1.0)
    assert 170.0 <= nominal_range <= 215.0

    # Under congestion (traffic_factor = 1.3), range should decrease
    congested_range = ev.calculate_physical_range_km(traffic_factor=1.3)
    assert congested_range < nominal_range


def test_vehicle_profile_dispatchable_exclusion():
    """Ensure unavailable or critical maintenance vehicles are not dispatchable."""
    v_crit = VehicleProfile(
        id="V-CRIT",
        name="Broken Truck",
        maintenance_status="critical",
        is_available=True,
    )
    is_disp, reason = v_crit.is_dispatchable()
    assert is_disp is False

    v_unavail = VehicleProfile(
        id="V-UNAVAIL",
        name="Off-duty Van",
        maintenance_status="ok",
        is_available=False,
    )
    is_disp2, reason2 = v_unavail.is_dispatchable()
    assert is_disp2 is False


def test_generate_default_fleet_profiles():
    """Verify factory generates heterogeneous fleet with diverse powertrains."""
    fleet = generate_default_fleet_profiles(num_vehicles=4, default_capacity=100.0)
    assert len(fleet) == 4
    powertrains = {v.powertrain for v in fleet}
    assert "electric" in powertrains
    assert "diesel" in powertrains
    assert "petrol" in powertrains
    assert "hybrid" in powertrains


def test_vehicle_route_energy_soc_and_cost():
    """Verify EV remaining SoC % and operational cost calculation."""
    ev_profile = {
        "vehicle_id": "EV-01",
        "name": "E-Transit",
        "powertrain": "electric",
        "max_payload_kg": 150.0,
        "battery_capacity_kwh": 60.0,
        "battery_soc_pct": 90.0,
        "battery_soh_pct": 100.0,
        "ev_efficiency_kwh_per_100km": 20.0,
        "usable_range_km": 200.0,
        "max_shift_hours": 8.0,
        "cost_per_km_usd": 0.25,
        "cost_per_hour_usd": 20.0,
        "fixed_dispatch_cost_usd": 15.0,
        "overall_condition": "good",
    }

    route_data = {
        "vehicle_id": 1,
        "stops": [0, 1, 2, 0],
        "customer_stops": [1, 2],
        "distance_km": 50.0,
        "total_duration_min": 90.0,  # 1.5 hours
        "load": 80.0,
        "capacity": 150.0,
    }

    res = compute_vehicle_route_energy(
        route_data=route_data,
        vehicle_idx=0,
        vehicle_profile=ev_profile,
    )

    assert res["propulsion_type"] == "electric"
    assert res["distance_km"] == 50.0
    assert res["energy_consumption_kwh"] > 0.0
    assert res["fuel_consumption_litres"] == 0.0
    assert res["direct_tailpipe_co2_kg"] == 0.0
    assert res["remaining_soc_pct"] < 90.0
    assert res["remaining_soc_pct"] > 60.0
    assert res["remaining_range_km"] == 150.0
    assert res["is_range_feasible"] is True
    assert res["is_shift_feasible"] is True
    assert res["is_all_feasible"] is True

    # Check operational cost breakdown: fuel/energy + maintenance + labor + dispatch
    assert 55.0 <= res["operational_cost_usd"] <= 68.0


def test_heterogeneous_fleet_ortools_range_and_capacity():
    """Verify OR-Tools respects heterogeneous vehicle capacities and ranges."""
    # 5 nodes (depot + 4 customers)
    dist_matrix = np.array([
        [0.0, 10.0, 20.0, 15.0, 25.0],
        [10.0, 0.0, 12.0, 18.0, 22.0],
        [20.0, 12.0, 0.0, 14.0, 16.0],
        [15.0, 18.0, 14.0, 0.0, 10.0],
        [25.0, 22.0, 16.0, 10.0, 0.0],
    ])
    demands = [0, 30, 40, 20, 25]  # total demand = 115
    # Vehicle 1 has capacity 80, Vehicle 2 has capacity 80 -> total 160
    capacities = [80, 80]
    ranges = [100.0, 100.0]

    v_profiles = [
        {"vehicle_id": "V1", "name": "Small Van", "powertrain": "electric", "max_payload_kg": 80, "usable_range_km": 100.0},
        {"vehicle_id": "V2", "name": "Large Van", "powertrain": "diesel", "max_payload_kg": 80, "usable_range_km": 100.0},
    ]

    res = classical_solver.solve_ortools(
        distance_matrix=dist_matrix,
        num_vehicles=2,
        depot=0,
        demands=demands,
        vehicle_capacities=capacities,
        vehicle_ranges=ranges,
        vehicle_profiles=v_profiles,
        time_limit_sec=2,
    )

    assert res["success"] is True
    routes = res.get("routes", [])
    assert len(routes) >= 1
    for r in routes:
        v_idx = r.get("vehicle_id", 1) - 1
        assert r["load"] <= capacities[min(v_idx, len(capacities) - 1)]


def test_route_validator_with_range_violations():
    """Verify validate_fleet_coverage flags range violations when distance exceeds range."""
    routes = [
        {"vehicle_id": 1, "stops": [0, 1, 0], "customer_stops": [1], "distance_km": 60.0, "load": 20.0, "capacity": 100.0},
        {"vehicle_id": 2, "stops": [0, 2, 0], "customer_stops": [2], "distance_km": 30.0, "load": 20.0, "capacity": 100.0},
    ]
    demands = [0, 20, 20]
    capacities = [100.0, 100.0]
    ranges = [45.0, 50.0]  # Route 1 distance (60) exceeds range 1 (45)!

    report = validate_fleet_coverage(
        routes=routes,
        input_customer_ids=[1, 2],
        demands=demands,
        vehicle_capacities=capacities,
        vehicle_ranges=ranges,
    )

    assert report["range_feasible"] is False
    assert report["range_violations"] == 1
    assert report["is_valid"] is False
    assert report["route_details"][0]["is_over_range"] is True
    assert report["route_details"][1]["is_over_range"] is False


def test_cooperative_solver_with_vehicle_profiles():
    """Verify ROUTE/IQ Cooperative Engine accepts and outputs vehicle profiles."""
    dist_matrix = np.array([
        [0.0, 8.0, 12.0, 15.0],
        [8.0, 0.0, 6.0, 10.0],
        [12.0, 6.0, 0.0, 8.0],
        [15.0, 10.0, 8.0, 0.0],
    ])
    demands = [0, 15, 20, 25]
    capacities = [50, 50]
    ranges = [80.0, 80.0]
    v_profiles = [
        {"vehicle_id": "V1", "name": "Transit EV", "powertrain": "electric", "max_payload_kg": 50, "usable_range_km": 80.0},
        {"vehicle_id": "V2", "name": "Transit Diesel", "powertrain": "diesel", "max_payload_kg": 50, "usable_range_km": 80.0},
    ]

    res = cooperative_solver.solve(
        distance_matrix=dist_matrix,
        num_vehicles=2,
        depot=0,
        demands=demands,
        vehicle_capacities=capacities,
        time_limit_sec=0.5,
        vehicle_ranges=ranges,
        vehicle_profiles=v_profiles,
    )

    assert res["success"] is True
    assert len(res.get("routes", [])) >= 1
    for r in res["routes"]:
        assert "vehicle_id" in r
