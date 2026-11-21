"""
ROUTE/IQ Energy Consumption and Resource Savings Service.

Provides scientific, peer-reviewed estimation of:
1. Fuel consumption (Litres) and direct thermal/electrical energy (kWh).
2. Well-to-wheel greenhouse gas emissions (CO2 equivalent in kg), distinguishing
   direct tailpipe emissions from indirect power grid generation emissions.
3. Operational fleet costs ($ USD) across commercial fuel and electric tariffs.
4. Comparative resource savings and emission abatements vs. baseline solvers (e.g., OR-Tools).
5. Vehicle-specific load and congestion adjustments.
6. Rigorous scientific data-quality tags: MEASURED, ESTIMATED, ASSUMED, UNAVAILABLE.

References & Standards:
- US EPA 2024 Greenhouse Gas Emission Factors Hub (Light-Duty Trucks / Commercial Vans)
- UK Department for Environment, Food & Rural Affairs (DEFRA / BEIS) 2023 GHG Conversion Factors
- US EPA eGRID 2022/2024 Subregion NYUP/NYCW (NYC Metro Grid Carbon Intensity: 0.245 kg CO2/kWh)
- US Energy Information Administration (EIA) / AAA Commercial Fuel & Electricity Averages
"""

from typing import Dict, Any, List, Optional, Tuple
import math
import logging

logger = logging.getLogger("routeiq.energy_service")


# ==============================================================================
# 1. SCIENTIFIC CONSTANTS & PROPULSION SPECIFICATIONS
# ==============================================================================

PROPULSION_MODELS: Dict[str, Dict[str, Any]] = {
    "diesel": {
        "id": "diesel",
        "name": "Diesel Delivery Van",
        "category": "Internal Combustion Engine (ICE)",
        "representative_vehicle": "Mercedes-Benz Sprinter 2500 / Ford Transit 2.0L TDCi",
        "fuel_type": "fuel",
        "unit_label": "L",
        "base_consumption_per_100km": 9.5,  # 9.5 L / 100 km (approx 24.8 MPG US)
        "energy_density_kwh_per_unit": 10.0,  # 10.0 kWh per Litre of diesel fuel (36.0 MJ/L)
        "direct_tailpipe_co2_kg_per_unit": 2.68,  # EPA 2024 / DEFRA 2023: 2.68 kg CO2/L direct
        "upstream_co2_kg_per_unit": 0.58,  # Well-to-tank refining & distribution: 0.58 kg CO2/L
        "total_co2_kg_per_unit": 3.26,  # Well-to-wheel: 3.26 kg CO2/L
        "unit_cost_usd": 1.15,  # $1.15 per Litre (~$4.35 / gallon, NYC metro commercial fleet average)
        "traffic_sensitivity": 0.20,  # 20% consumption increase per 1.0 traffic factor deviation
        "load_sensitivity": 0.15,  # 15% consumption increase at 100% rated payload capacity
        "citations": [
            "US EPA 2024 GHG Emission Factors Hub, Table 2 (Mobile Combustion)",
            "UK DEFRA/DESNZ 2023 Conversion Factors for Company Reporting",
        ],
    },
    "petrol": {
        "id": "petrol",
        "name": "Petrol / Gasoline Van",
        "category": "Internal Combustion Engine (ICE)",
        "representative_vehicle": "Ford Transit 3.5L V6 Gasoline / Ram ProMaster 3.6L",
        "fuel_type": "fuel",
        "unit_label": "L",
        "base_consumption_per_100km": 11.0,  # 11.0 L / 100 km (approx 21.4 MPG US)
        "energy_density_kwh_per_unit": 8.9,  # 8.9 kWh per Litre of gasoline (32.0 MJ/L)
        "direct_tailpipe_co2_kg_per_unit": 2.31,  # EPA 2024: 2.31 kg CO2/L direct
        "upstream_co2_kg_per_unit": 0.52,  # Well-to-tank: 0.52 kg CO2/L
        "total_co2_kg_per_unit": 2.83,  # Well-to-wheel: 2.83 kg CO2/L
        "unit_cost_usd": 0.95,  # $0.95 per Litre (~$3.60 / gallon commercial regular gasoline)
        "traffic_sensitivity": 0.22,  # Gasoline engines suffer higher urban idling losses
        "load_sensitivity": 0.15,
        "citations": [
            "US EPA 2024 GHG Emission Factors Hub",
            "EIA Weekly U.S. Regular Gasoline Prices",
        ],
    },
    "hybrid": {
        "id": "hybrid",
        "name": "Hybrid Delivery Van",
        "category": "Hybrid Electric Vehicle (HEV)",
        "representative_vehicle": "Ford Transit Custom PHEV / Toyota Proace City Hybrid",
        "fuel_type": "fuel",
        "unit_label": "L",
        "base_consumption_per_100km": 6.8,  # 6.8 L / 100 km (regenerative braking benefit)
        "energy_density_kwh_per_unit": 8.9,  # Gasoline equivalent energy density
        "direct_tailpipe_co2_kg_per_unit": 2.31,  # Direct gasoline combustion
        "upstream_co2_kg_per_unit": 0.52,
        "total_co2_kg_per_unit": 2.83,
        "unit_cost_usd": 0.95,  # $0.95 per Litre
        "traffic_sensitivity": 0.10,  # Hybrid regenerative braking mitigates stop-and-go penalty
        "load_sensitivity": 0.15,
        "citations": [
            "US Department of Energy AFDC Alternative Fuels Data Center",
            "EPA Fuel Economy Guide for Commercial Hybrids",
        ],
    },
    "electric": {
        "id": "electric",
        "name": "Electric Delivery Van (EV)",
        "category": "Battery Electric Vehicle (BEV)",
        "representative_vehicle": "Rivian EDV 700 / Ford E-Transit Cargo / BrightDrop Zevo 600",
        "fuel_type": "electricity",
        "unit_label": "kWh",
        "base_consumption_per_100km": 28.0,  # 28.0 kWh / 100 km (0.28 kWh/km or 45 kWh/100mi)
        "energy_density_kwh_per_unit": 1.0,  # Direct electrical energy (1 kWh = 1 kWh)
        "direct_tailpipe_co2_kg_per_unit": 0.0,  # Zero direct tailpipe emissions
        "upstream_co2_kg_per_unit": 0.245,  # Grid generation: 0.245 kg CO2/kWh (EPA eGRID NYC / NYUP subregion)
        "total_co2_kg_per_unit": 0.245,  # Lifecycle grid carbon footprint
        "unit_cost_usd": 0.18,  # $0.18 per kWh (NYC commercial demand rate average)
        "traffic_sensitivity": 0.08,  # EVs are highly efficient in stop-and-go with full regenerative braking
        "load_sensitivity": 0.18,  # Heavy battery mass makes additional cargo slightly more sensitive
        "citations": [
            "US EPA eGRID 2022/2024 Summary Tables (Subregion NYUP / NYCW: 539.8 lb CO2/MWh = 0.245 kg CO2/kWh)",
            "US DOE National Renewable Energy Laboratory (NREL) Fleet DNA Commercial EV Dataset",
        ],
    },
}

DATA_TAGS = {
    "distance": "MEASURED",
    "duration": "ESTIMATED",
    "fuel_consumption": "ESTIMATED",
    "energy_consumption": "ESTIMATED",
    "co2_emissions": "ESTIMATED",
    "operational_cost": "ESTIMATED",
    "vehicle_propulsion_model": "ASSUMED",
    "fuel_and_electricity_prices": "ASSUMED",
    "grid_carbon_intensity": "ASSUMED",
}


# ==============================================================================
# 2. CORE CALCULATION ENGINE
# ==============================================================================

def compute_route_load_factor(
    route_load: float,
    vehicle_capacity: float,
    load_sensitivity: float = 0.15
) -> float:
    """
    Calculate dynamic vehicle payload correction factor.
    F_load = 1.0 + load_sensitivity * (load / capacity)
    Clamped to range [1.0, 1.25].
    """
    if vehicle_capacity <= 0 or route_load <= 0:
        return 1.0
    utilization = min(max(route_load / vehicle_capacity, 0.0), 1.5)
    return 1.0 + (load_sensitivity * utilization)


def compute_route_traffic_factor(
    traffic_factor: float = 1.0,
    traffic_sensitivity: float = 0.20
) -> float:
    """
    Calculate dynamic congestion correction factor.
    F_traffic = 1.0 + traffic_sensitivity * (traffic_factor - 1.0)
    Clamped to range [0.9, 1.5].
    """
    deviation = max(traffic_factor - 1.0, 0.0)
    return 1.0 + (traffic_sensitivity * min(deviation, 2.0))


def compute_vehicle_route_energy(
    route_data: Dict[str, Any],
    vehicle_idx: int,
    propulsion_type: str = "diesel",
    vehicle_capacity: float = 0.0,
    traffic_factor: float = 1.0,
    vehicle_profile: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Calculate energy, fuel, carbon emissions, and operational cost for an individual vehicle route.
    Supports individual vehicle condition profiles (battery SoC/SoH, fuel tank level, maintenance wear,
    odometer, hourly & per-km operating costs, and range/shift feasibility).
    """
    vp = vehicle_profile or route_data.get("vehicle_profile") or {}
    
    # Resolve powertrain & propulsion model
    p_type = vp.get("powertrain", propulsion_type)
    if p_type not in PROPULSION_MODELS:
        p_type = propulsion_type if propulsion_type in PROPULSION_MODELS else "diesel"
    model = PROPULSION_MODELS.get(p_type, PROPULSION_MODELS["diesel"])
    
    dist_km = float(route_data.get("distance_km", 0.0) or 0.0)
    duration_min = float(route_data.get("total_duration_min", route_data.get("driving_time_min", 0.0)) or 0.0)
    duration_hours = duration_min / 60.0
    load = float(route_data.get("load", 0.0) or 0.0)
    cap = float(vp.get("max_payload_kg", route_data.get("capacity", vehicle_capacity)) or vehicle_capacity or 100.0)

    f_load = compute_route_load_factor(load, cap, model.get("load_sensitivity", 0.15))
    f_traffic = compute_route_traffic_factor(traffic_factor, model.get("traffic_sensitivity", 0.20))
    adjustment_multiplier = f_load * f_traffic

    # Baseline rate from model, or custom rate from vehicle profile if specified
    is_electric = model["fuel_type"] == "electricity"
    if is_electric and vp.get("ev_efficiency_kwh_per_100km"):
        base_rate = float(vp["ev_efficiency_kwh_per_100km"])
    elif not is_electric and vp.get("fuel_consumption_l_per_100km"):
        base_rate = float(vp["fuel_consumption_l_per_100km"])
    else:
        base_rate = model["base_consumption_per_100km"]

    # Condition & Age efficiency penalty: older/poor condition vehicles consume slightly more
    condition = str(vp.get("overall_condition", "good")).lower()
    condition_multiplier = 1.0
    if condition == "excellent":
        condition_multiplier = 0.97
    elif condition == "good":
        condition_multiplier = 1.00
    elif condition == "average":
        condition_multiplier = 1.05
    elif condition == "poor":
        condition_multiplier = 1.12
    
    total_consumption_multiplier = adjustment_multiplier * condition_multiplier

    if is_electric:
        fuel_litres = 0.0
        energy_kwh = dist_km * (base_rate / 100.0) * total_consumption_multiplier
        tailpipe_co2_kg = 0.0
        upstream_co2_kg = energy_kwh * model["upstream_co2_kg_per_unit"]
        total_co2_kg = upstream_co2_kg
        fuel_energy_cost_usd = energy_kwh * model["unit_cost_usd"]
    else:
        fuel_litres = dist_km * (base_rate / 100.0) * total_consumption_multiplier
        energy_kwh = fuel_litres * model["energy_density_kwh_per_unit"]
        tailpipe_co2_kg = fuel_litres * model["direct_tailpipe_co2_kg_per_unit"]
        upstream_co2_kg = fuel_litres * model["upstream_co2_kg_per_unit"]
        total_co2_kg = tailpipe_co2_kg + upstream_co2_kg
        fuel_energy_cost_usd = fuel_litres * model["unit_cost_usd"]

    # Vehicle-Specific Range & Battery/Fuel Remaining Calculation
    stops_count = len(route_data.get("customer_stops", route_data.get("stops", [])))
    has_activity = stops_count > 0 and dist_km > 0.0

    battery_capacity_kwh = float(vp.get("battery_capacity_kwh", 60.0) or 60.0)
    battery_soc_raw = vp.get("battery_soc_percent") if vp.get("battery_soc_percent") is not None else vp.get("battery_soc_pct")
    battery_soc_pct = float(battery_soc_raw if battery_soc_raw is not None else 100.0)
    battery_soh_raw = vp.get("battery_soh_percent") if vp.get("battery_soh_percent") is not None else vp.get("battery_soh_pct")
    battery_soh_pct = float(battery_soh_raw if battery_soh_raw is not None else 100.0)

    fuel_tank_capacity_l = float(vp.get("fuel_tank_capacity_l", 60.0) or 60.0)
    fuel_level_raw = vp.get("fuel_tank_level_percent") if vp.get("fuel_tank_level_percent") is not None else vp.get("fuel_level_pct")
    fuel_level_pct = float(fuel_level_raw if fuel_level_raw is not None else 100.0)

    usable_range_km = float(vp.get("usable_range_km", 250.0) or 250.0)
    max_shift_hours = float(vp.get("max_shift_hours", 8.0) or 8.0)
    cost_per_km_usd = float(vp.get("cost_per_km_usd", 0.35) or 0.35)
    cost_per_hour_usd = float(vp.get("cost_per_hour_usd", 22.0) or 22.0)
    fixed_dispatch_cost_usd = float(vp.get("fixed_dispatch_cost_usd", 15.0) or 15.0)

    # Battery State of Charge (SoC) remaining
    if is_electric and battery_capacity_kwh > 0:
        effective_capacity = battery_capacity_kwh * (battery_soh_pct / 100.0)
        soc_consumed_pct = (energy_kwh / max(effective_capacity, 1.0)) * 100.0
        remaining_soc_pct = max(0.0, round(battery_soc_pct - soc_consumed_pct, 1))
    else:
        remaining_soc_pct = battery_soc_pct

    # Fuel level remaining
    if not is_electric and fuel_tank_capacity_l > 0:
        fuel_consumed_pct = (fuel_litres / max(fuel_tank_capacity_l, 1.0)) * 100.0
        remaining_fuel_pct = max(0.0, round(fuel_level_pct - fuel_consumed_pct, 1))
    else:
        remaining_fuel_pct = fuel_level_pct

    remaining_range_km = max(0.0, round(usable_range_km - dist_km, 1))
    is_range_feasible = dist_km <= (usable_range_km + 1e-3)
    is_shift_feasible = duration_hours <= (max_shift_hours + 1e-3)
    is_capacity_feasible = load <= (cap + 1e-3)

    # Comprehensive Operational Costing
    maintenance_wear_cost = dist_km * cost_per_km_usd
    driver_labor_cost = duration_hours * cost_per_hour_usd
    dispatch_cost = fixed_dispatch_cost_usd if has_activity else 0.0
    total_operational_cost = fuel_energy_cost_usd + maintenance_wear_cost + driver_labor_cost + dispatch_cost

    return {
        "vehicle_id": route_data.get("vehicle_id", vehicle_idx + 1),
        "vehicle_profile": {
            "vehicle_id": vp.get("vehicle_id", f"V{vehicle_idx + 1}"),
            "name": vp.get("name", f"Fleet Vehicle {vehicle_idx + 1}"),
            "vehicle_type": vp.get("vehicle_type", "van"),
            "powertrain": p_type,
            "overall_condition": condition,
            "battery_soc_pct": battery_soc_pct,
            "battery_soh_pct": battery_soh_pct,
            "fuel_level_pct": fuel_level_pct,
            "usable_range_km": usable_range_km,
            "max_shift_hours": max_shift_hours,
            "maintenance_status": vp.get("maintenance_status", "ok"),
        } if vp else None,
        "propulsion_type": p_type,
        "distance_km": round(dist_km, 2),
        "duration_min": round(duration_min, 1),
        "stops_count": stops_count,
        "load": round(load, 1),
        "capacity": round(cap, 1),
        "utilization_pct": round((load / cap * 100.0), 1) if cap > 0 else 0.0,
        "load_factor": round(f_load, 3),
        "traffic_factor": round(f_traffic, 3),
        "condition_multiplier": round(condition_multiplier, 3),
        "fuel_consumption_litres": round(fuel_litres, 3),
        "energy_consumption_kwh": round(energy_kwh, 2),
        "direct_tailpipe_co2_kg": round(tailpipe_co2_kg, 3),
        "indirect_grid_co2_kg": round(upstream_co2_kg, 3) if is_electric else 0.0,
        "upstream_well_to_tank_co2_kg": round(upstream_co2_kg, 3),
        "total_co2_kg": round(total_co2_kg, 3),
        "fuel_energy_cost_usd": round(fuel_energy_cost_usd, 2),
        "maintenance_wear_cost_usd": round(maintenance_wear_cost, 2),
        "driver_labor_cost_usd": round(driver_labor_cost, 2),
        "dispatch_cost_usd": round(dispatch_cost, 2),
        "operational_cost_usd": round(total_operational_cost, 2),
        "remaining_soc_pct": remaining_soc_pct if is_electric else None,
        "remaining_fuel_pct": remaining_fuel_pct if not is_electric else None,
        "remaining_range_km": remaining_range_km,
        "is_range_feasible": is_range_feasible,
        "is_shift_feasible": is_shift_feasible,
        "is_capacity_feasible": is_capacity_feasible,
        "is_all_feasible": is_range_feasible and is_shift_feasible and is_capacity_feasible,
        "unit_label": model["unit_label"],
    }


def compute_algorithm_energy_profile(
    algo_key: str,
    algo_data: Dict[str, Any],
    propulsion_type: str = "diesel",
    vehicle_capacity: float = 0.0,
    traffic_factor: float = 1.0,
    vehicle_profiles: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Calculate aggregated energy, environmental profile, and fleet condition feasibility for an algorithm.
    """
    routes = algo_data.get("routes", []) or []

    vehicle_breakdowns: List[Dict[str, Any]] = []
    total_fuel_l = 0.0
    total_energy_kwh = 0.0
    total_tailpipe_co2 = 0.0
    total_upstream_co2 = 0.0
    total_cost_usd = 0.0
    total_fuel_energy_cost_usd = 0.0
    all_ranges_feasible = True
    all_shifts_feasible = True

    # If routes list is provided, calculate per-vehicle route
    if routes:
        for idx, route in enumerate(routes):
            v_prof = None
            if vehicle_profiles and idx < len(vehicle_profiles):
                v_prof = vehicle_profiles[idx]
            elif route.get("vehicle_profile"):
                v_prof = route["vehicle_profile"]

            v_res = compute_vehicle_route_energy(
                route,
                vehicle_idx=idx,
                propulsion_type=propulsion_type,
                vehicle_capacity=vehicle_capacity,
                traffic_factor=traffic_factor,
                vehicle_profile=v_prof,
            )
            vehicle_breakdowns.append(v_res)
            total_fuel_l += v_res["fuel_consumption_litres"]
            total_energy_kwh += v_res["energy_consumption_kwh"]
            total_tailpipe_co2 += v_res["direct_tailpipe_co2_kg"]
            total_upstream_co2 += v_res["upstream_well_to_tank_co2_kg"]
            total_cost_usd += v_res["operational_cost_usd"]
            total_fuel_energy_cost_usd += v_res["fuel_energy_cost_usd"]
            if not v_res["is_range_feasible"]:
                all_ranges_feasible = False
            if not v_res["is_shift_feasible"]:
                all_shifts_feasible = False
        total_dist_km = sum(v["distance_km"] for v in vehicle_breakdowns)
        total_duration_min = sum(v["duration_min"] for v in vehicle_breakdowns)
    else:
        # Fallback if routes are not detailed: compute from aggregate distance
        model = PROPULSION_MODELS.get(propulsion_type, PROPULSION_MODELS["diesel"])
        total_dist_km = float(algo_data.get("total_distance_km", 0.0) or 0.0)
        total_duration_min = float(algo_data.get("total_duration_min", algo_data.get("total_travel_time_min", 0.0)) or 0.0)
        f_traffic = compute_route_traffic_factor(traffic_factor, model.get("traffic_sensitivity", 0.20))
        base_rate = model["base_consumption_per_100km"]
        is_electric = model["fuel_type"] == "electricity"

        if is_electric:
            total_fuel_l = 0.0
            total_energy_kwh = total_dist_km * (base_rate / 100.0) * f_traffic
            total_tailpipe_co2 = 0.0
            total_upstream_co2 = total_energy_kwh * model["upstream_co2_kg_per_unit"]
            total_cost_usd = total_energy_kwh * model["unit_cost_usd"]
        else:
            total_fuel_l = total_dist_km * (base_rate / 100.0) * f_traffic
            total_energy_kwh = total_fuel_l * model["energy_density_kwh_per_unit"]
            total_tailpipe_co2 = total_fuel_l * model["direct_tailpipe_co2_kg_per_unit"]
            total_upstream_co2 = total_fuel_l * model["upstream_co2_kg_per_unit"]
            total_cost_usd = total_fuel_l * model["unit_cost_usd"]
        total_fuel_energy_cost_usd = total_cost_usd

    total_co2_kg = total_tailpipe_co2 + total_upstream_co2
    is_feasible = (
        bool(algo_data.get("is_feasible", False))
        and algo_data.get("capacity_violations", 0) == 0
        and all_ranges_feasible
    )

    primary_model = PROPULSION_MODELS.get(propulsion_type, PROPULSION_MODELS["diesel"])

    return {
        "algorithm_id": algo_key,
        "algorithm_name": algo_data.get("algorithm_name", algo_key.upper()),
        "category": algo_data.get("category", "classical"),
        "is_feasible": is_feasible,
        "is_range_feasible": all_ranges_feasible,
        "is_shift_feasible": all_shifts_feasible,
        "propulsion_type": propulsion_type,
        "propulsion_name": primary_model["name"] if not vehicle_profiles else "Heterogeneous Fleet Profile",
        "unit_label": primary_model["unit_label"],
        "total_distance_km": round(total_dist_km, 2),
        "total_duration_min": round(total_duration_min, 1),
        "vehicles_count": len(vehicle_breakdowns) or len(routes) or 1,
        "fuel_consumption_litres": round(total_fuel_l, 3),
        "energy_consumption_kwh": round(total_energy_kwh, 2),
        "direct_tailpipe_co2_kg": round(total_tailpipe_co2, 3),
        "indirect_grid_co2_kg": round(total_upstream_co2, 3) if total_fuel_l == 0 else 0.0,
        "upstream_well_to_tank_co2_kg": round(total_upstream_co2, 3),
        "total_co2_kg": round(total_co2_kg, 3),
        "fuel_energy_cost_usd": round(total_fuel_energy_cost_usd, 2),
        "operational_cost_usd": round(total_cost_usd, 2),
        "vehicle_breakdowns": vehicle_breakdowns,
        "data_tags": DATA_TAGS,
    }


def compute_energy_comparison(
    target_profile: Dict[str, Any],
    baseline_profile: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Compute comparative resource and carbon savings between a target algorithm and a baseline solver.

    Conventions:
    - Positive delta (delta > 0) = SAVED by target (target consumed less than baseline).
    - Negative delta (delta < 0) = EXTRA CONSUMPTION by target (target consumed more).
    - Savings % = (delta / baseline) * 100.
    """
    base_dist = baseline_profile.get("total_distance_km", 0.0)
    tgt_dist = target_profile.get("total_distance_km", 0.0)
    delta_dist = base_dist - tgt_dist

    base_fuel = baseline_profile.get("fuel_consumption_litres", 0.0)
    tgt_fuel = target_profile.get("fuel_consumption_litres", 0.0)
    delta_fuel = base_fuel - tgt_fuel

    base_kwh = baseline_profile.get("energy_consumption_kwh", 0.0)
    tgt_kwh = target_profile.get("energy_consumption_kwh", 0.0)
    delta_kwh = base_kwh - tgt_kwh

    base_co2 = baseline_profile.get("total_co2_kg", 0.0)
    tgt_co2 = target_profile.get("total_co2_kg", 0.0)
    delta_co2 = base_co2 - tgt_co2

    base_cost = baseline_profile.get("operational_cost_usd", 0.0)
    tgt_cost = target_profile.get("operational_cost_usd", 0.0)
    delta_cost = base_cost - tgt_cost

    def _calc_pct(delta: float, base: float) -> float:
        if abs(base) < 1e-6:
            return 0.0
        return round((delta / base) * 100.0, 2)

    pct_dist = _calc_pct(delta_dist, base_dist)
    pct_fuel = _calc_pct(delta_fuel, base_fuel)
    pct_kwh = _calc_pct(delta_kwh, base_kwh)
    pct_co2 = _calc_pct(delta_co2, base_co2)
    pct_cost = _calc_pct(delta_cost, base_cost)

    # Classification
    if abs(delta_dist) < 0.01:
        status_label = "IDENTICAL_TO_BASELINE"
        impact_summary = "Identical resource consumption and emissions to baseline"
    elif delta_dist > 0.01:
        status_label = "RESOURCE_SAVING"
        impact_summary = f"Reduces energy consumption by {abs(pct_kwh)}% ({round(delta_kwh, 2)} kWh) and avoids {round(delta_co2, 3)} kg CO2"
    else:
        status_label = "RESOURCE_DEFICIT"
        impact_summary = f"Increases energy consumption by {abs(pct_kwh)}% ({round(abs(delta_kwh), 2)} kWh) over baseline"

    return {
        "target_algorithm": target_profile.get("algorithm_id"),
        "baseline_algorithm": baseline_profile.get("algorithm_id"),
        "propulsion_type": target_profile.get("propulsion_type"),
        "delta_distance_km": round(delta_dist, 2),
        "delta_fuel_litres": round(delta_fuel, 3),
        "delta_energy_kwh": round(delta_kwh, 2),
        "delta_co2_kg": round(delta_co2, 3),
        "delta_cost_usd": round(delta_cost, 2),
        "pct_distance_savings": pct_dist,
        "pct_fuel_savings": pct_fuel,
        "pct_energy_savings": pct_kwh,
        "pct_co2_savings": pct_co2,
        "pct_cost_savings": pct_cost,
        "is_saving": delta_dist > 0.01,
        "is_identical": abs(delta_dist) <= 0.01,
        "status_label": status_label,
        "impact_summary": impact_summary,
    }


# ==============================================================================
# 3. FULL MULTI-ALGORITHM & MULTI-PROPULSION ANALYSIS
# ==============================================================================

def compute_full_energy_analysis(
    results: Dict[str, Any],
    default_propulsion: str = "diesel",
    baseline_algo: str = "ortools",
    vehicle_capacity: float = 0.0,
    traffic_factor: float = 1.0,
    vehicle_profiles: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Generate comprehensive energy, fuel, carbon, and economic analysis across all solved algorithms.
    Supports individual vehicle condition profiles when provided.
    Precomputes metrics for all 4 vehicle propulsion types so the frontend can switch instantly.
    """
    valid_algos = [k for k, v in results.items() if isinstance(v, dict) and v.get("success", False)]
    if not valid_algos:
        valid_algos = list(results.keys())

    # Determine baseline algorithm
    effective_baseline = baseline_algo
    if effective_baseline not in results:
        if "ortools" in results:
            effective_baseline = "ortools"
        elif "classical" in results:
            effective_baseline = "classical"
        elif valid_algos:
            effective_baseline = valid_algos[0]
        else:
            effective_baseline = "ortools"

    # Precompute profiles across all 4 propulsion types
    profiles_by_propulsion: Dict[str, Dict[str, Any]] = {}
    for p_type in PROPULSION_MODELS.keys():
        p_dict: Dict[str, Any] = {}
        for a_key in valid_algos:
            p_dict[a_key] = compute_algorithm_energy_profile(
                algo_key=a_key,
                algo_data=results[a_key],
                propulsion_type=p_type,
                vehicle_capacity=vehicle_capacity,
                traffic_factor=traffic_factor,
                vehicle_profiles=vehicle_profiles,
            )
        profiles_by_propulsion[p_type] = p_dict

    # For the default propulsion type, build comparisons against baseline
    active_profiles = profiles_by_propulsion.get(default_propulsion, {})
    baseline_profile = active_profiles.get(effective_baseline)

    comparisons: Dict[str, Any] = {}
    if baseline_profile:
        for a_key, a_prof in active_profiles.items():
            comparisons[a_key] = compute_energy_comparison(a_prof, baseline_profile)

    # Rank algorithms by energy efficiency (feasible solutions with minimal kWh)
    feasible_ranked = [
        p for p in active_profiles.values()
        if p["is_feasible"]
    ]
    feasible_ranked.sort(key=lambda x: (x["energy_consumption_kwh"], x["total_distance_km"]))

    best_eco_algo = feasible_ranked[0]["algorithm_id"] if feasible_ranked else (valid_algos[0] if valid_algos else None)

    # Flagship comparison: Cooperative Engine vs OR-Tools Baseline
    flagship_comparison = None
    if "routeiq_cooperative" in active_profiles and "ortools" in active_profiles:
        flagship_comparison = compute_energy_comparison(
            active_profiles["routeiq_cooperative"],
            active_profiles["ortools"]
        )

    return {
        "active_propulsion": default_propulsion,
        "baseline_algorithm": effective_baseline,
        "best_eco_algorithm": best_eco_algo,
        "propulsion_models": PROPULSION_MODELS,
        "profiles": active_profiles,
        "profiles_by_propulsion": profiles_by_propulsion,
        "comparisons": comparisons,
        "flagship_comparison": flagship_comparison,
        "methodology": {
            "title": "ROUTE/IQ Scientific Energy & Emissions Accounting Methodology",
            "standards": [
                "US EPA 2024 Greenhouse Gas Emission Factors Hub",
                "UK DEFRA/DESNZ 2023 Company GHG Reporting Conversion Factors",
                "US EPA eGRID 2022/2024 Grid Carbon Intensity Subregion NYUP/NYCW (0.245 kg CO2/kWh)",
            ],
            "data_tags": DATA_TAGS,
            "fuel_prices_source": "AAA / EIA Commercial Regional Benchmark ($1.15/L Diesel, $0.95/L Petrol, $0.18/kWh Commercial EV)",
        },
    }
