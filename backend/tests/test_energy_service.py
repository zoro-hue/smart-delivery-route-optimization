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
    assert "Saves 9.09% energy (-10.0 kWh) and avoids 3.26 kg CO2" in comp["impact_summary"]


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
    assert "Increases energy consumption by 50.0% (+50.0 kWh) and adds 16.3 kg CO2" in comp["impact_summary"]


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


def test_energy_saving_with_increased_co2():
    """Verify mixed-outcome handling when selected route saves energy but emits more CO2."""
    baseline = {
        "algorithm_id": "baseline_gas_clean",
        "total_distance_km": 100.0,
        "energy_consumption_kwh": 120.0,
        "total_co2_kg": 20.0,
        "operational_cost_usd": 30.0,
    }
    target = {
        "algorithm_id": "selected_ice_efficient",
        "total_distance_km": 90.0,
        "energy_consumption_kwh": 100.0,  # 20 kWh energy saved (delta_energy = -20 kWh)
        "total_co2_kg": 28.0,             # 8 kg more CO2 (co2_abatement = -8 kg)
        "operational_cost_usd": 25.0,
    }
    comp = compute_energy_comparison(target, baseline)
    assert comp["delta_energy_kwh"] == -20.0
    assert comp["pct_energy_savings"] == pytest.approx(16.67, abs=0.01)
    assert comp["co2_abatement_kg"] == -8.0
    assert comp["status_label"] == "MIXED_OUTCOME"
    assert "Saves 16.67% energy (-20.0 kWh) but adds 8.0 kg CO2" in comp["impact_summary"]


def test_energy_deficit_with_reduced_co2():
    """Verify mixed-outcome handling when selected route uses more energy but avoids CO2."""
    baseline = {
        "algorithm_id": "baseline_ice_dirty",
        "total_distance_km": 90.0,
        "energy_consumption_kwh": 90.0,
        "total_co2_kg": 35.0,
        "operational_cost_usd": 30.0,
    }
    target = {
        "algorithm_id": "selected_ev_heavy_grid",
        "total_distance_km": 95.0,
        "energy_consumption_kwh": 100.0,  # 10 kWh more energy (delta_energy = +10 kWh)
        "total_co2_kg": 24.5,             # 10.5 kg CO2 avoided (co2_abatement = +10.5 kg)
        "operational_cost_usd": 28.0,
    }
    comp = compute_energy_comparison(target, baseline)
    assert comp["delta_energy_kwh"] == 10.0
    assert comp["pct_energy_savings"] == pytest.approx(-11.11, abs=0.01)
    assert comp["co2_abatement_kg"] == 10.5
    assert comp["status_label"] == "MIXED_OUTCOME"
    assert "Uses 11.11% more energy (+10.0 kWh) but avoids 10.5 kg CO2" in comp["impact_summary"]


def test_baseline_switching_selected_unchanged():
    """Verify that switching comparison baselines updates deltas while selected-route metrics remain completely invariant."""
    selected = {
        "algorithm_id": "routeiq_cooperative",
        "total_distance_km": 227.69,
        "energy_consumption_kwh": 170.77,
        "fuel_consumption_litres": 15.201,
        "total_co2_kg": 52.704,
        "operational_cost_usd": 288.71,
    }
    base_qiga = {
        "algorithm_id": "qiga",
        "total_distance_km": 354.34,
        "energy_consumption_kwh": 241.14,
        "fuel_consumption_litres": 20.038,
        "total_co2_kg": 73.267,
        "operational_cost_usd": 403.99,
    }
    base_qaoa = {
        "algorithm_id": "qaoa",
        "total_distance_km": 247.98,
        "energy_consumption_kwh": 160.22,
        "fuel_consumption_litres": 12.618,
        "total_co2_kg": 47.989,
        "operational_cost_usd": 301.56,
    }
    base_coop = dict(selected)

    comp_qiga = compute_energy_comparison(selected, base_qiga)
    comp_qaoa = compute_energy_comparison(selected, base_qaoa)
    comp_coop = compute_energy_comparison(selected, base_coop)

    # Selected-route underlying values have not changed
    assert selected["energy_consumption_kwh"] == 170.77
    assert selected["fuel_consumption_litres"] == 15.201
    assert selected["total_co2_kg"] == 52.704
    assert selected["operational_cost_usd"] == 288.71

    # QIGA comparison: Energy saved (-70.37 kWh), CO2 avoided (+20.563 kg), Cost saved ($115.28)
    assert comp_qiga["delta_energy_kwh"] == -70.37
    assert comp_qiga["co2_abatement_kg"] == 20.563
    assert comp_qiga["fleet_cost_saved_usd"] == 115.28
    assert comp_qiga["status_label"] == "RESOURCE_SAVING"

    # QAOA comparison: Energy deficit (+10.55 kWh), CO2 extra emissions (-4.715 kg), Cost saved ($12.85)
    assert comp_qaoa["delta_energy_kwh"] == 10.55
    assert comp_qaoa["co2_abatement_kg"] == -4.715
    assert comp_qaoa["fleet_cost_saved_usd"] == 12.85
    assert comp_qaoa["status_label"] == "RESOURCE_DEFICIT"

    # Cooperative comparison: Identical route (0 delta)
    assert comp_coop["delta_energy_kwh"] == 0.0
    assert comp_coop["co2_abatement_kg"] == 0.0
    assert comp_coop["fleet_cost_saved_usd"] == 0.0
    assert comp_coop["status_label"] == "IDENTICAL_TO_BASELINE"


PRODUCTION_JOB_COOP_DATA = {
    "algorithm_name": "ROUTE/IQ Cooperative Engine",
    "is_feasible": True,
    "routes": [
        {
            "vehicle_id": 1,
            "distance_km": 51.43,
            "load": 47.0,
            "capacity": 50,
            "total_duration_min": 77.14,
            "customer_stops": [1, 2],
            "vehicle_profile": {
                "name": "Vehicle 1 (Ford E-Transit BEV)",
                "vehicle_type": "electric_van",
                "powertrain": "electric",
                "capacity_kg": 60,
                "cargo_volume_m3": 12,
                "condition": "excellent",
                "age_years": 1.5,
                "odometer_km": 28000,
                "maintenance_status": "ok",
                "is_available": True,
                "battery_capacity_kwh": 68,
                "battery_soc_percent": 90,
                "battery_soh_percent": 97,
                "base_consumption_per_100km": 26,
                "max_range_km": 210,
                "max_operating_hours": 8,
                "cost_per_km_usd": 0.24,
                "cost_per_hour_usd": 22,
                "fixed_dispatch_cost_usd": 12,
                "id": "veh-1",
            },
        },
        {
            "vehicle_id": 2,
            "distance_km": 55.276,
            "load": 60.0,
            "capacity": 50,
            "total_duration_min": 82.91,
            "customer_stops": [3, 4],
            "vehicle_profile": {
                "name": "Vehicle 2 (Mercedes Sprinter Diesel)",
                "vehicle_type": "van",
                "powertrain": "diesel",
                "capacity_kg": 75,
                "cargo_volume_m3": 14,
                "condition": "good",
                "age_years": 3,
                "odometer_km": 65000,
                "maintenance_status": "ok",
                "is_available": True,
                "fuel_tank_capacity_l": 75,
                "fuel_level_percent": 80,
                "base_consumption_per_100km": 9.5,
                "max_range_km": 280,
                "max_operating_hours": 9,
                "cost_per_km_usd": 0.38,
                "cost_per_hour_usd": 22,
                "fixed_dispatch_cost_usd": 18,
                "id": "veh-2",
            },
        },
        {
            "vehicle_id": 3,
            "distance_km": 50.004,
            "load": 50.0,
            "capacity": 50,
            "total_duration_min": 75.01,
            "customer_stops": [5, 6],
            "vehicle_profile": {
                "name": "Vehicle 3 (Ford Transit 3.5L Petrol)",
                "vehicle_type": "van",
                "powertrain": "petrol",
                "capacity_kg": 50,
                "cargo_volume_m3": 10,
                "condition": "average",
                "age_years": 4.5,
                "odometer_km": 92000,
                "maintenance_status": "service_recommended",
                "is_available": True,
                "fuel_tank_capacity_l": 80,
                "fuel_level_percent": 70,
                "base_consumption_per_100km": 11.2,
                "max_range_km": 240,
                "max_operating_hours": 8,
                "cost_per_km_usd": 0.42,
                "cost_per_hour_usd": 20,
                "fixed_dispatch_cost_usd": 15,
                "id": "veh-3",
            },
        },
        {
            "vehicle_id": 4,
            "distance_km": 34.524,
            "load": 47.0,
            "capacity": 50,
            "total_duration_min": 51.79,
            "customer_stops": [7, 8],
            "vehicle_profile": {
                "name": "Vehicle 4 (Transit Custom PHEV)",
                "vehicle_type": "van",
                "powertrain": "hybrid",
                "capacity_kg": 55,
                "cargo_volume_m3": 11,
                "condition": "good",
                "age_years": 2,
                "odometer_km": 42000,
                "maintenance_status": "ok",
                "is_available": True,
                "battery_capacity_kwh": 14,
                "battery_soc_percent": 85,
                "battery_soh_percent": 96,
                "fuel_tank_capacity_l": 54,
                "fuel_level_percent": 85,
                "base_consumption_per_100km": 6.8,
                "max_range_km": 300,
                "max_operating_hours": 8.5,
                "cost_per_km_usd": 0.32,
                "cost_per_hour_usd": 22,
                "fixed_dispatch_cost_usd": 14,
                "id": "veh-4",
            },
        },
        {
            "vehicle_id": 5,
            "distance_km": 36.462,
            "load": 44.0,
            "capacity": 50,
            "total_duration_min": 54.69,
            "customer_stops": [9, 10],
            "vehicle_profile": {
                "name": "Vehicle 5 (Ford E-Transit BEV)",
                "vehicle_type": "electric_van",
                "powertrain": "electric",
                "capacity_kg": 60,
                "cargo_volume_m3": 12,
                "condition": "excellent",
                "age_years": 1.5,
                "odometer_km": 28000,
                "maintenance_status": "ok",
                "is_available": True,
                "battery_capacity_kwh": 68,
                "battery_soc_percent": 90,
                "battery_soh_percent": 97,
                "base_consumption_per_100km": 26,
                "max_range_km": 210,
                "max_operating_hours": 8,
                "cost_per_km_usd": 0.24,
                "cost_per_hour_usd": 22,
                "fixed_dispatch_cost_usd": 12,
                "id": "veh-5",
            },
        },
    ],
}


def test_fleet_weighted_consumption_rates():
    """Verify that heterogeneous fleet of 5 vehicles produces exact 6.68 L/100km fleet-weighted average."""
    profile = compute_algorithm_energy_profile("routeiq_cooperative", PRODUCTION_JOB_COOP_DATA)
    assert profile["total_distance_km"] == pytest.approx(227.69, abs=0.05)
    # Total fuel = 0 (EV) + 6.196 (Diesel) + 6.326 (Petrol) + 2.679 (Hybrid) + 0 (EV) = 15.201 L
    assert profile["fuel_consumption_litres"] == pytest.approx(15.20, abs=0.02)
    # Weighted rate = 15.201 / 227.696 * 100 = 6.676... approx 6.68 L/100km
    weighted_rate = (profile["fuel_consumption_litres"] / (profile["total_distance_km"] / 100.0))
    assert weighted_rate == pytest.approx(6.68, abs=0.02)


def test_cost_breakdown_reconciliation():
    """Verify that fleet operating cost reconciles fuel/power ($20.84) + wear ($74.14) + labor ($122.73) + dispatch ($71.00) = $288.71."""
    profile = compute_algorithm_energy_profile("routeiq_cooperative", PRODUCTION_JOB_COOP_DATA)
    assert profile["fuel_energy_cost_usd"] == pytest.approx(20.84, abs=0.05)
    assert profile["maintenance_wear_cost_usd"] == pytest.approx(74.14, abs=0.05)
    assert profile["driver_labor_cost_usd"] == pytest.approx(122.72, abs=0.05)
    assert profile["dispatch_cost_usd"] == pytest.approx(71.00, abs=0.05)
    assert profile["operational_cost_usd"] == pytest.approx(288.71, abs=0.05)


def test_scientific_data_tags():
    """Verify all metrics carry peer-reviewed scientific classification tags."""
    assert DATA_TAGS["distance"] == "MEASURED"
    assert DATA_TAGS["duration"] == "ESTIMATED"
    assert DATA_TAGS["fuel_consumption"] == "ESTIMATED"
    assert DATA_TAGS["energy_consumption"] == "ESTIMATED"
    assert DATA_TAGS["co2_emissions"] == "ESTIMATED"
    assert DATA_TAGS["vehicle_propulsion_model"] == "ASSUMED"
    assert DATA_TAGS["grid_carbon_intensity"] == "ASSUMED"
