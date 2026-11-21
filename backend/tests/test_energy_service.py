"""
Unit tests for ROUTE/IQ Energy Consumption & Resource Savings Service.
Verifies physical and emission constants, load/traffic adjustments, multi-vehicle aggregation,
baseline comparisons, and scientific tagging.
"""

import pytest
from app.services.optimization.energy_service import (
    PROPULSION_MODELS,
    DATA_TAGS,
    compute_route_load_factor,
    compute_route_traffic_factor,
    compute_vehicle_route_energy,
    compute_algorithm_energy_profile,
    compute_energy_comparison,
    compute_full_energy_analysis,
)


def test_propulsion_models_presence():
    """Verify all 4 required propulsion categories are defined with valid physical constants."""
    assert "diesel" in PROPULSION_MODELS
    assert "petrol" in PROPULSION_MODELS
    assert "hybrid" in PROPULSION_MODELS
    assert "electric" in PROPULSION_MODELS

    diesel = PROPULSION_MODELS["diesel"]
    assert diesel["base_consumption_per_100km"] == 9.5
    assert diesel["energy_density_kwh_per_unit"] == 10.0
    assert diesel["direct_tailpipe_co2_kg_per_unit"] == 2.68
    assert diesel["unit_cost_usd"] == 1.15

    electric = PROPULSION_MODELS["electric"]
    assert electric["base_consumption_per_100km"] == 28.0
    assert electric["direct_tailpipe_co2_kg_per_unit"] == 0.0
    assert electric["upstream_co2_kg_per_unit"] == 0.245
    assert electric["unit_cost_usd"] == 0.18


def test_route_load_and_traffic_adjustments():
    """Verify dynamic payload and congestion adjustment factors."""
    # Zero load or zero capacity returns 1.0
    assert compute_route_load_factor(0.0, 100.0) == 1.0
    assert compute_route_load_factor(50.0, 0.0) == 1.0

    # 100% capacity utilization gives 1.0 + 0.15 = 1.15
    f_load_full = compute_route_load_factor(100.0, 100.0)
    assert abs(f_load_full - 1.15) < 1e-4

    # 50% capacity gives 1.0 + 0.15 * 0.5 = 1.075
    f_load_half = compute_route_load_factor(50.0, 100.0)
    assert abs(f_load_half - 1.075) < 1e-4

    # Congestion adjustment
    assert compute_route_traffic_factor(1.0) == 1.0
    # 25% traffic slowdown (1.25) gives 1.0 + 0.20 * 0.25 = 1.05
    f_traffic = compute_route_traffic_factor(1.25)
    assert abs(f_traffic - 1.05) < 1e-4


def test_vehicle_route_energy_diesel():
    """Verify diesel van calculations for a standard 100 km route."""
    route = {
        "vehicle_id": 1,
        "distance_km": 100.0,
        "total_duration_min": 150.0,
        "load": 0.0,
        "capacity": 100.0,
        "customer_stops": [1, 2, 3],
    }
    res = compute_vehicle_route_energy(route, vehicle_idx=0, propulsion_type="diesel", traffic_factor=1.0)
    # At 100 km nominal: 9.5 L
    assert res["fuel_consumption_litres"] == 9.5
    # Energy: 9.5 L * 10 kWh/L = 95.0 kWh
    assert res["energy_consumption_kwh"] == 95.0
    # Tailpipe CO2: 9.5 L * 2.68 kg/L = 25.46 kg
    assert res["direct_tailpipe_co2_kg"] == 25.46
    # Total CO2: 9.5 L * 3.26 kg/L = 30.97 kg
    assert res["total_co2_kg"] == 30.97
    # Cost: 9.5 L * $1.15/L = $10.925 -> 10.92 (banker's rounding)
    assert res["operational_cost_usd"] == 10.92


def test_vehicle_route_energy_electric():
    """Verify EV van calculations for a 100 km route."""
    route = {
        "vehicle_id": 1,
        "distance_km": 100.0,
        "total_duration_min": 150.0,
        "load": 0.0,
        "capacity": 100.0,
        "customer_stops": [1, 2],
    }
    res = compute_vehicle_route_energy(route, vehicle_idx=0, propulsion_type="electric", traffic_factor=1.0)
    # Fuel is 0.0 L
    assert res["fuel_consumption_litres"] == 0.0
    # Energy: 28.0 kWh
    assert res["energy_consumption_kwh"] == 28.0
    # Direct tailpipe CO2 is 0.0
    assert res["direct_tailpipe_co2_kg"] == 0.0
    # Grid generation CO2: 28.0 * 0.245 = 6.86 kg
    assert res["total_co2_kg"] == 6.86
    # Cost: 28.0 kWh * $0.18/kWh = $5.04
    assert res["operational_cost_usd"] == 5.04


def test_algorithm_energy_profile_multi_vehicle():
    """Verify aggregation across multiple vehicle routes."""
    algo_data = {
        "algorithm_name": "ROUTE/IQ Cooperative Engine",
        "is_feasible": True,
        "capacity_violations": 0,
        "routes": [
            {"vehicle_id": 1, "distance_km": 40.0, "load": 20.0, "capacity": 50.0, "total_duration_min": 60.0},
            {"vehicle_id": 2, "distance_km": 60.0, "load": 30.0, "capacity": 50.0, "total_duration_min": 90.0},
        ],
    }
    profile = compute_algorithm_energy_profile("routeiq_cooperative", algo_data, propulsion_type="diesel")
    assert profile["total_distance_km"] == 100.0
    assert len(profile["vehicle_breakdowns"]) == 2
    assert profile["total_duration_min"] == 150.0
    assert profile["fuel_consumption_litres"] > 9.5  # Greater than base due to cargo load


def test_energy_comparison_savings():
    """Verify comparison when target saves resources vs baseline."""
    baseline = {
        "algorithm_id": "ortools",
        "total_distance_km": 110.0,
        "fuel_consumption_litres": 11.0,
        "energy_consumption_kwh": 110.0,
        "total_co2_kg": 35.86,
        "operational_cost_usd": 12.65,
        "propulsion_type": "diesel",
    }
    target = {
        "algorithm_id": "routeiq_cooperative",
        "total_distance_km": 100.0,
        "fuel_consumption_litres": 10.0,
        "energy_consumption_kwh": 100.0,
        "total_co2_kg": 32.60,
        "operational_cost_usd": 11.50,
        "propulsion_type": "diesel",
    }
    comp = compute_energy_comparison(target, baseline)
    assert comp["is_saving"] is True
    assert comp["is_identical"] is False
    assert comp["delta_distance_km"] == 10.0
    assert comp["delta_fuel_litres"] == 1.0
    assert comp["delta_energy_kwh"] == 10.0
    assert comp["pct_energy_savings"] == pytest.approx(9.09, abs=0.01)
    assert comp["status_label"] == "RESOURCE_SAVING"


def test_energy_comparison_identical():
    """Verify comparison when target route is identical to baseline."""
    baseline = {
        "algorithm_id": "ortools",
        "total_distance_km": 100.0,
        "fuel_consumption_litres": 10.0,
        "energy_consumption_kwh": 100.0,
        "total_co2_kg": 32.60,
        "operational_cost_usd": 11.50,
        "propulsion_type": "diesel",
    }
    target = dict(baseline)
    target["algorithm_id"] = "routeiq_cooperative"

    comp = compute_energy_comparison(target, baseline)
    assert comp["is_saving"] is False
    assert comp["is_identical"] is True
    assert comp["delta_distance_km"] == 0.0
    assert comp["pct_energy_savings"] == 0.0
    assert comp["status_label"] == "IDENTICAL_TO_BASELINE"


def test_energy_comparison_penalty():
    """Verify comparison when target is worse than baseline."""
    baseline = {
        "algorithm_id": "ortools",
        "total_distance_km": 100.0,
        "fuel_consumption_litres": 10.0,
        "energy_consumption_kwh": 100.0,
        "total_co2_kg": 32.60,
        "operational_cost_usd": 11.50,
        "propulsion_type": "diesel",
    }
    target = {
        "algorithm_id": "dijkstra",
        "total_distance_km": 150.0,
        "fuel_consumption_litres": 15.0,
        "energy_consumption_kwh": 150.0,
        "total_co2_kg": 48.90,
        "operational_cost_usd": 17.25,
        "propulsion_type": "diesel",
    }
    comp = compute_energy_comparison(target, baseline)
    assert comp["is_saving"] is False
    assert comp["is_identical"] is False
    assert comp["delta_distance_km"] == -50.0
    assert comp["pct_energy_savings"] == -50.0
    assert comp["status_label"] == "RESOURCE_DEFICIT"


def test_full_energy_analysis_all_propulsions():
    """Verify compute_full_energy_analysis precomputes all 4 propulsion types."""
    results = {
        "ortools": {
            "success": True,
            "algorithm_name": "Google OR-Tools",
            "is_feasible": True,
            "capacity_violations": 0,
            "total_distance_km": 100.0,
            "routes": [{"vehicle_id": 1, "distance_km": 100.0, "load": 50.0, "capacity": 100.0}],
        },
        "routeiq_cooperative": {
            "success": True,
            "algorithm_name": "ROUTE/IQ Cooperative Engine",
            "is_feasible": True,
            "capacity_violations": 0,
            "total_distance_km": 95.0,
            "routes": [{"vehicle_id": 1, "distance_km": 95.0, "load": 50.0, "capacity": 100.0}],
        },
    }
    analysis = compute_full_energy_analysis(results, default_propulsion="diesel", baseline_algo="ortools")
    assert "profiles_by_propulsion" in analysis
    assert len(analysis["profiles_by_propulsion"]) == 4
    for p in ["diesel", "petrol", "hybrid", "electric"]:
        assert p in analysis["profiles_by_propulsion"]
        assert "routeiq_cooperative" in analysis["profiles_by_propulsion"][p]

    assert analysis["best_eco_algorithm"] == "routeiq_cooperative"
    flagship = analysis["flagship_comparison"]
    assert flagship is not None
    assert flagship["is_saving"] is True
    assert flagship["delta_distance_km"] == 5.0


def test_scientific_data_tags():
    """Verify all metrics carry peer-reviewed scientific classification tags."""
    assert DATA_TAGS["distance"] == "MEASURED"
    assert DATA_TAGS["duration"] == "ESTIMATED"
    assert DATA_TAGS["fuel_consumption"] == "ESTIMATED"
    assert DATA_TAGS["energy_consumption"] == "ESTIMATED"
    assert DATA_TAGS["co2_emissions"] == "ESTIMATED"
    assert DATA_TAGS["vehicle_propulsion_model"] == "ASSUMED"
    assert DATA_TAGS["grid_carbon_intensity"] == "ASSUMED"
