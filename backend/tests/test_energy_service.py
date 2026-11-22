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
    # Fuel cost: 9.5 L * $1.15/L = $10.925 -> 10.92 (banker's rounding)
    assert res["fuel_energy_cost_usd"] == 10.92
    # Total operational cost: fuel ($10.92) + maintenance (100km * $0.35 = $35) + labor (2.5h * $22 = $55) + dispatch ($15) = $115.92
    assert res["operational_cost_usd"] == 115.92


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
    # Energy cost: 28.0 kWh * $0.18/kWh = $5.04
    assert res["fuel_energy_cost_usd"] == 5.04
    # Total operational cost: electricity ($5.04) + maintenance ($35) + labor ($55) + dispatch ($15) = $110.04
    assert res["operational_cost_usd"] == 110.04


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
    """Verify comparison when target saves resources vs baseline (negative delta, positive savings %)."""
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
    # delta_energy = selected - baseline = 100 - 110 = -10.0 kWh (negative: saved)
    assert comp["delta_distance_km"] == -10.0
    assert comp["delta_fuel_litres"] == -1.0
    assert comp["delta_energy_kwh"] == -10.0
    assert comp["pct_energy_savings"] == pytest.approx(9.09, abs=0.01)
    # co2_abatement = baseline - selected = 35.86 - 32.60 = +3.26 kg (positive: avoided)
    assert comp["co2_abatement_kg"] == 3.26
    # fleet_cost_saved = baseline - selected = 12.65 - 11.50 = +1.15 USD (positive: saved)
    assert comp["fleet_cost_saved_usd"] == 1.15
    assert comp["status_label"] == "RESOURCE_SAVING"
    assert "Reduces energy consumption by 9.09% (-10.0 kWh) and avoids 3.26 kg CO2" in comp["impact_summary"]


def test_energy_comparison_identical():
    """Verify comparison when target route is identical to baseline (zero delta, zero savings %)."""
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
    assert comp["delta_energy_kwh"] == 0.0
    assert comp["pct_energy_savings"] == 0.0
    assert comp["co2_abatement_kg"] == 0.0
    assert comp["fleet_cost_saved_usd"] == 0.0
    assert comp["status_label"] == "IDENTICAL_TO_BASELINE"
    assert comp["impact_summary"] == "Identical resource consumption and emissions to baseline"


def test_energy_comparison_penalty():
    """Verify comparison when target is worse than baseline (positive delta, negative savings %)."""
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
    # delta_energy = selected - baseline = 150 - 100 = +50.0 kWh (positive: additional consumed)
    assert comp["delta_distance_km"] == 50.0
    assert comp["delta_energy_kwh"] == 50.0
    assert comp["pct_energy_savings"] == -50.0
    # co2_abatement = 32.60 - 48.90 = -16.30 kg (negative: additional emissions)
    assert comp["co2_abatement_kg"] == -16.30
    # fleet_cost_saved = 11.50 - 17.25 = -5.75 USD (negative: additional cost)
    assert comp["fleet_cost_saved_usd"] == -5.75
    assert comp["status_label"] == "RESOURCE_DEFICIT"
    assert "Increases energy consumption by 50.0% (+50.0 kWh) over baseline" in comp["impact_summary"]


def test_energy_comparison_zero_or_missing_baseline():
    """Verify graceful handling when baseline has zero or missing energy."""
    baseline = {
        "algorithm_id": "empty_baseline",
        "total_distance_km": 0.0,
        "energy_consumption_kwh": 0.0,
        "total_co2_kg": 0.0,
        "operational_cost_usd": 0.0,
    }
    target = {
        "algorithm_id": "selected",
        "total_distance_km": 50.0,
        "energy_consumption_kwh": 50.0,
        "total_co2_kg": 16.30,
        "operational_cost_usd": 65.0,
    }
    comp = compute_energy_comparison(target, baseline)
    assert comp["delta_energy_kwh"] == 50.0
    assert comp["pct_energy_savings"] == 0.0  # Safe division by zero
    assert comp["co2_abatement_kg"] == -16.30
    assert comp["fleet_cost_saved_usd"] == -65.0
    assert comp["status_label"] == "RESOURCE_DEFICIT"


def test_multi_vehicle_different_propulsions():
    """Verify accurate aggregation across multiple vehicles with heterogeneous propulsion types."""
    vehicle_profiles = [
        {"vehicle_id": "V1", "powertrain": "diesel", "max_payload_kg": 1000.0, "cost_per_km_usd": 0.35},
        {"vehicle_id": "V2", "powertrain": "electric", "max_payload_kg": 800.0, "cost_per_km_usd": 0.25},
        {"vehicle_id": "V3", "powertrain": "hybrid", "max_payload_kg": 900.0, "cost_per_km_usd": 0.30},
        {"vehicle_id": "V4", "powertrain": "petrol", "max_payload_kg": 1000.0, "cost_per_km_usd": 0.38},
    ]
    algo_data = {
        "algorithm_name": "Heterogeneous Fleet Routing",
        "is_feasible": True,
        "routes": [
            {"vehicle_id": 1, "distance_km": 50.0, "load": 200.0, "total_duration_min": 60.0, "customer_stops": [1, 2]},
            {"vehicle_id": 2, "distance_km": 40.0, "load": 150.0, "total_duration_min": 45.0, "customer_stops": [3, 4]},
            {"vehicle_id": 3, "distance_km": 30.0, "load": 100.0, "total_duration_min": 40.0, "customer_stops": [5, 6]},
            {"vehicle_id": 4, "distance_km": 60.0, "load": 250.0, "total_duration_min": 75.0, "customer_stops": [7, 8]},
        ],
    }
    profile = compute_algorithm_energy_profile(
        "custom_hetero",
        algo_data,
        vehicle_profiles=vehicle_profiles
    )
    assert len(profile["vehicle_breakdowns"]) == 4
    assert profile["total_distance_km"] == 180.0
    assert profile["total_duration_min"] == 220.0
    assert profile["vehicle_breakdowns"][0]["propulsion_type"] == "diesel"
    assert profile["vehicle_breakdowns"][1]["propulsion_type"] == "electric"
    assert profile["vehicle_breakdowns"][2]["propulsion_type"] == "hybrid"
    assert profile["vehicle_breakdowns"][3]["propulsion_type"] == "petrol"
    # EV produces 0 direct tailpipe emissions
    assert profile["vehicle_breakdowns"][1]["direct_tailpipe_co2_kg"] == 0.0
    assert profile["vehicle_breakdowns"][1]["indirect_grid_co2_kg"] > 0.0
    # Total energy and cost are aggregated across all 4 powertrains
    assert profile["energy_consumption_kwh"] > 0.0
    assert profile["operational_cost_usd"] > 0.0


def test_negative_co2_abatement():
    """Verify negative CO2 abatement when selected route generates more emissions than baseline."""
    baseline = {
        "algorithm_id": "baseline_clean",
        "total_distance_km": 80.0,
        "energy_consumption_kwh": 70.0,
        "total_co2_kg": 15.0,
        "operational_cost_usd": 20.0,
    }
    target = {
        "algorithm_id": "target_dirty",
        "total_distance_km": 90.0,
        "energy_consumption_kwh": 85.0,
        "total_co2_kg": 25.5,
        "operational_cost_usd": 24.0,
    }
    comp = compute_energy_comparison(target, baseline)
    # co2_abatement = 15.0 - 25.5 = -10.5 kg (negative: 10.5 kg extra CO2 generated)
    assert comp["co2_abatement_kg"] == -10.5
    assert comp["delta_co2_kg"] == 10.5
    assert comp["is_saving"] is False


def test_independent_energy_and_monetary_cost_outcomes():
    """
    Verify that energy savings and cost savings are computed independently
    and not inferred from one another.
    Scenario: Selected route uses less energy, but costs more (e.g., due to overtime driver labor or higher vehicle fixed dispatch rate).
    """
    baseline = {
        "algorithm_id": "baseline_fast_driver",
        "total_distance_km": 100.0,
        "energy_consumption_kwh": 100.0,
        "total_co2_kg": 30.0,
        "operational_cost_usd": 40.0,  # Cheaper overall cost despite higher energy
    }
    target = {
        "algorithm_id": "selected_eco_slow_labor",
        "total_distance_km": 90.0,
        "energy_consumption_kwh": 80.0,  # 20 kWh energy SAVED
        "total_co2_kg": 24.0,            # 6 kg CO2 ABATED
        "operational_cost_usd": 55.0,    # Higher labor / vehicle rate causes cost DEFICIT
    }
    comp = compute_energy_comparison(target, baseline)
    # Energy is saved: delta_energy < 0, pct_energy_savings > 0
    assert comp["delta_energy_kwh"] == -20.0
    assert comp["pct_energy_savings"] == 20.0
    assert comp["is_saving"] is True
    # CO2 is abated: co2_abatement > 0
    assert comp["co2_abatement_kg"] == 6.0
    # BUT monetary cost is a deficit: fleet_cost_saved < 0
    assert comp["fleet_cost_saved_usd"] == -15.0
    assert comp["delta_cost_usd"] == 15.0
    assert comp["pct_cost_savings"] == -37.5


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
    assert flagship["delta_distance_km"] == -5.0
    assert flagship["delta_energy_kwh"] < 0.0


def test_scientific_data_tags():
    """Verify all metrics carry peer-reviewed scientific classification tags."""
    assert DATA_TAGS["distance"] == "MEASURED"
    assert DATA_TAGS["duration"] == "ESTIMATED"
    assert DATA_TAGS["fuel_consumption"] == "ESTIMATED"
    assert DATA_TAGS["energy_consumption"] == "ESTIMATED"
    assert DATA_TAGS["co2_emissions"] == "ESTIMATED"
    assert DATA_TAGS["vehicle_propulsion_model"] == "ASSUMED"
    assert DATA_TAGS["grid_carbon_intensity"] == "ASSUMED"
