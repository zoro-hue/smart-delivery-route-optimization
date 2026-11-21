"""
ROUTE/IQ Next-Generation Cooperative Engine: Vehicle-Condition-Aware Evaluator.
Formalizes heterogeneous fleet vehicle condition constraints, EV battery health (SoH/SoC),
operating range physics, maintenance status risk factors, and multi-objective scalarization.
"""

import copy
import math
import logging
from typing import Dict, Any, List, Tuple, Optional
import numpy as np

logger = logging.getLogger(__name__)


class VehicleConditionEvaluator:
    """
    Evaluates fleet routing candidates under explicit heterogeneous vehicle conditions.
    Computes distance, driving time, energy (fuel and kWh), operating costs, emissions,
    and enforces range/capacity feasibility penalties.
    """

    def __init__(
        self,
        vehicle_profiles: Optional[List[Dict[str, Any]]] = None,
        num_vehicles: int = 3,
        default_capacity: float = 100.0,
        alpha_distance: float = 0.40,
        alpha_cost: float = 0.25,
        alpha_energy: float = 0.20,
        alpha_emissions: float = 0.15,
    ):
        self.num_vehicles: int = num_vehicles
        self.default_capacity: float = default_capacity

        # Multi-objective weights (normalized to 1.0)
        self.alpha_distance: float = alpha_distance
        self.alpha_cost: float = alpha_cost
        self.alpha_energy: float = alpha_energy
        self.alpha_emissions: float = alpha_emissions

        # Normalization baselines
        self.base_distance_km: float = 100.0
        self.base_cost_usd: float = 50.0
        self.base_energy_kwh: float = 40.0
        self.base_emissions_kg: float = 25.0

        # Build normalized profile models
        self.profiles: List[Dict[str, Any]] = self._normalize_profiles(vehicle_profiles, num_vehicles)

    def _normalize_profiles(
        self, raw_profiles: Optional[List[Dict[str, Any]]], count: int
    ) -> List[Dict[str, Any]]:
        """Parses and computes physical usable limits for each vehicle in fleet."""
        profiles = []
        for i in range(count):
            p = copy.deepcopy(raw_profiles[i]) if raw_profiles and i < len(raw_profiles) else {}

            vehicle_type = p.get("vehicle_type", "van")
            powertrain = p.get("powertrain", "diesel" if i % 2 == 1 else "electric")
            capacity_kg = float(p.get("capacity_kg", self.default_capacity))
            condition = p.get("condition", "good")
            maint_status = p.get("maintenance_status", "ok")
            is_available = p.get("is_available", True) and (maint_status != "critical")

            # EV Battery & Usable Range Physics
            if powertrain == "electric":
                nom_battery = float(p.get("battery_capacity_kwh", 68.0))
                soh = float(p.get("battery_soh_percent", 96.0))  # State of Health
                soc = float(p.get("battery_soc_percent", 90.0))  # State of Charge
                base_consump = float(p.get("base_consumption_per_100km", 26.0))  # kWh/100km

                # Actual usable capacity scaled by degradation (SoH)
                usable_battery_kwh = nom_battery * (soh / 100.0)
                # Electrical energy available scaled by charge (SoC)
                avail_energy_kwh = usable_battery_kwh * (soc / 100.0)
                # Feasible operating range
                usable_range_km = (avail_energy_kwh / max(1.0, base_consump)) * 100.0

                cost_per_km = float(p.get("cost_per_km_usd", 0.22))
                cost_per_hr = float(p.get("cost_per_hour_usd", 22.0))
                fixed_cost = float(p.get("fixed_dispatch_cost_usd", 12.0))
                emission_factor = float(p.get("emission_factor_kg_per_km", 0.0))  # 0 tailpipe
            else:
                # ICE / Petrol / Diesel / Hybrid
                tank_cap = float(p.get("fuel_tank_capacity_l", 75.0))
                fuel_level = float(p.get("fuel_level_percent", 80.0))
                base_consump = float(p.get("base_consumption_per_100km", 10.0))  # L/100km
                avail_fuel_l = tank_cap * (fuel_level / 100.0)
                usable_range_km = (avail_fuel_l / max(0.1, base_consump)) * 100.0

                cost_per_km = float(p.get("cost_per_km_usd", 0.38 if powertrain == "diesel" else 0.42))
                cost_per_hr = float(p.get("cost_per_hour_usd", 22.0))
                fixed_cost = float(p.get("fixed_dispatch_cost_usd", 16.0))
                # Diesel: ~2.68 kg CO2/L; Petrol: ~2.31 kg CO2/L
                emission_rate = 2.68 if powertrain == "diesel" else 2.31
                emission_factor = (base_consump / 100.0) * emission_rate

            # Maintenance wear factor (service recommended incurs 15% cost/fuel penalty)
            wear_factor = 1.15 if maint_status == "service_recommended" else 1.0

            profiles.append({
                "vehicle_index": i,
                "vehicle_id": p.get("id", f"veh-{i+1}"),
                "name": p.get("name", f"Vehicle {i+1} ({powertrain.title()})"),
                "vehicle_type": vehicle_type,
                "powertrain": powertrain,
                "capacity_kg": capacity_kg,
                "condition": condition,
                "maintenance_status": maint_status,
                "is_available": is_available,
                "usable_range_km": round(usable_range_km, 2),
                "cost_per_km_usd": cost_per_km * wear_factor,
                "cost_per_hour_usd": cost_per_hr,
                "fixed_dispatch_cost_usd": fixed_cost,
                "emission_factor_kg_per_km": emission_factor,
                "base_consumption_per_100km": base_consump * wear_factor,
            })
        return profiles

    def set_normalization_baselines(
        self,
        base_distance_km: float,
        base_cost_usd: float = 50.0,
        base_energy_kwh: float = 40.0,
        base_emissions_kg: float = 25.0,
    ):
        """Calibrates dimensionless normalization scalars using the initial baseline incumbent."""
        self.base_distance_km = max(1.0, float(base_distance_km))
        self.base_cost_usd = max(1.0, float(base_cost_usd))
        self.base_energy_kwh = max(1.0, float(base_energy_kwh))
        self.base_emissions_kg = max(1.0, float(base_emissions_kg))

    def evaluate_candidate(
        self,
        vehicle_routes: List[List[int]],
        dist_matrix: np.ndarray,
        demands: List[int],
        depot: int = 0,
        travel_time_matrix: Optional[np.ndarray] = None,
        input_cust_ids: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """
        Evaluates a complete fleet routing candidate against all vehicle constraints.
        Computes distance, duration, costs, emissions, energy, violations, and scalarized fitness:
        F(S) = α1*(D/D0) + α2*(C/C0) + α3*(E/E0) + α4*(M/M0) + Penalties
        """
        n = dist_matrix.shape[0]
        if input_cust_ids is None:
            input_cust_ids = [i for i in range(n) if i != depot]

        total_distance_km = 0.0
        total_driving_time_min = 0.0
        total_cost_usd = 0.0
        total_energy_kwh = 0.0
        total_emissions_kg = 0.0

        capacity_violations = 0
        range_violations = 0
        all_visited = []

        route_details = []

        for v_idx in range(len(vehicle_routes)):
            stops = vehicle_routes[v_idx]
            prof = self.profiles[v_idx] if v_idx < len(self.profiles) else self.profiles[0]

            if not stops:
                route_details.append({
                    "vehicle_id": prof["vehicle_id"],
                    "distance_km": 0.0,
                    "cost_usd": 0.0,
                    "is_feasible": True,
                })
                continue

            all_visited.extend(stops)

            # 1. Route Distance
            full_tour = [depot] + stops + [depot]
            r_dist = 0.0
            r_time_min = 0.0
            for i in range(len(full_tour) - 1):
                u, v = full_tour[i], full_tour[i + 1]
                d = dist_matrix[u, v]
                r_dist += d
                if travel_time_matrix is not None:
                    r_time_min += travel_time_matrix[u, v]
                else:
                    # Default 35 km/h urban speed = 1.714 min/km
                    r_time_min += (d / 35.0) * 60.0

            # 2. Capacity Check
            load = sum(demands[c] for c in stops if c < len(demands))
            cap = prof["capacity_kg"]
            if load > cap + 1e-4:
                capacity_violations += int(math.ceil(load - cap))

            # 3. Range Check
            usable_range = prof["usable_range_km"]
            if r_dist > usable_range + 1e-4:
                range_violations += 1

            # 4. Energy & Emissions
            if prof["powertrain"] == "electric":
                r_energy_kwh = (r_dist / 100.0) * prof["base_consumption_per_100km"]
                r_emissions_kg = 0.0  # Zero tailpipe
            else:
                liters = (r_dist / 100.0) * prof["base_consumption_per_100km"]
                # Convert diesel/gasoline energy to equivalent kWh (1 L diesel ≈ 10 kWh)
                r_energy_kwh = liters * 9.8
                r_emissions_kg = r_dist * prof["emission_factor_kg_per_km"]

            # 5. Operating Cost
            r_cost_usd = (
                prof["fixed_dispatch_cost_usd"]
                + r_dist * prof["cost_per_km_usd"]
                + (r_time_min / 60.0) * prof["cost_per_hour_usd"]
            )

            total_distance_km += r_dist
            total_driving_time_min += r_time_min
            total_cost_usd += r_cost_usd
            total_energy_kwh += r_energy_kwh
            total_emissions_kg += r_emissions_kg

            route_details.append({
                "vehicle_id": prof["vehicle_id"],
                "distance_km": round(r_dist, 3),
                "driving_time_min": round(r_time_min, 2),
                "load": load,
                "capacity": cap,
                "usable_range_km": usable_range,
                "is_range_feasible": r_dist <= usable_range + 1e-4,
                "cost_usd": round(r_cost_usd, 2),
                "energy_kwh": round(r_energy_kwh, 2),
                "emissions_kg": round(r_emissions_kg, 3),
            })

        # Unserved customers check
        unserved_count = len(set(input_cust_ids) - set(all_visited))
        duplicate_count = len(all_visited) - len(set(all_visited))
        unserved_count += duplicate_count

        is_feasible = (
            capacity_violations == 0
            and range_violations == 0
            and unserved_count == 0
        )

        # Dimensionless multi-objective score
        norm_dist = total_distance_km / self.base_distance_km
        norm_cost = total_cost_usd / self.base_cost_usd
        norm_energy = total_energy_kwh / self.base_energy_kwh
        norm_emiss = total_emissions_kg / self.base_emissions_kg

        base_fitness = (
            self.alpha_distance * norm_dist
            + self.alpha_cost * norm_cost
            + self.alpha_energy * norm_energy
            + self.alpha_emissions * norm_emiss
        )

        # Penalty terms for infeasibility
        penalty = (
            10.0 * capacity_violations
            + 25.0 * range_violations
            + 50.0 * unserved_count
        )

        scalarized_fitness = base_fitness + penalty

        return {
            "total_distance_km": round(total_distance_km, 3),
            "total_driving_time_min": round(total_driving_time_min, 2),
            "total_cost_usd": round(total_cost_usd, 2),
            "total_energy_kwh": round(total_energy_kwh, 2),
            "total_emissions_kg_co2": round(total_emissions_kg, 3),
            "scalarized_fitness": round(scalarized_fitness, 4),
            "is_feasible": is_feasible,
            "capacity_violations": capacity_violations,
            "range_violations": range_violations,
            "unserved_customers": unserved_count,
            "route_details": route_details,
        }

    def compute_fleet_heterogeneity_index(self) -> float:
        """
        Computes fleet heterogeneity metric H in [0, 1] based on capacity and range dispersion:
        H = 0.5 * (std(Capacity) / mean(Capacity)) + 0.5 * (std(Range) / mean(Range))
        """
        caps = [p["capacity_kg"] for p in self.profiles]
        ranges = [p["usable_range_km"] for p in self.profiles]
        cv_cap = float(np.std(caps) / max(1.0, np.mean(caps))) if caps else 0.0
        cv_range = float(np.std(ranges) / max(1.0, np.mean(ranges))) if ranges else 0.0
        return min(1.0, 0.5 * cv_cap + 0.5 * cv_range)
