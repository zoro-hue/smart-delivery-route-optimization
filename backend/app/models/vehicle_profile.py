"""
ROUTE/IQ Vehicle Profile and Condition Model.

Defines the mathematical, physical, and operational specification of individual
fleet vehicles for condition-aware vehicle routing optimization.

Includes:
1. Basic Identification: Vehicle ID, Name, Category (Van, Truck, Car, Electric Van).
2. Powertrain & Energy: Diesel, Petrol, Hybrid, Electric (BEV).
3. Payload & Volumetric Capacity: Max payload in kg, optional cargo volume in m³.
4. Vehicle Condition & Health:
   - Condition rating: Excellent, Good, Average, Poor.
   - Vehicle age (years) and cumulative odometer (km).
   - Maintenance status: OK, Service Recommended, Overdue, Critical.
   - Availability toggle: Available vs Out of Service.
5. Battery & State of Charge (for EV and Hybrid):
   - Nameplate battery capacity (kWh).
   - Current State of Charge (SoC %).
   - Battery State of Health (SoH %).
   - Calculated usable battery capacity.
6. Fuel & Tank Level (for Combustion and Hybrid):
   - Tank capacity (Litres).
   - Current fuel level (%).
7. Physics-Calibrated Range & Consumption:
   - Base consumption (L/100km or kWh/100km).
   - Maximum operational range on current charge/fuel.
   - Max driver shift / operating hours (hours).
8. Operating Economics:
   - Variable maintenance & operating cost per km ($/km).
   - Driver cost per hour ($/hr).
   - Fixed vehicle dispatch / mobilization cost ($).
"""

from typing import Optional, Dict, Any, Tuple, List
from pydantic import BaseModel, Field


class VehicleProfile(BaseModel):
    id: str = Field(..., description="Unique vehicle identifier, e.g. 'veh-1'")
    name: str = Field(..., description="Human-readable vehicle name, e.g. 'Delivery Van 1 (E-Transit)'")
    vehicle_type: str = Field("van", description="Vehicle category: car, van, truck, electric_van")
    powertrain: str = Field("diesel", description="Powertrain type: diesel, petrol, hybrid, electric")

    # Capacity constraints
    capacity_kg: float = Field(100.0, gt=0, description="Maximum payload capacity in kg / units")
    cargo_volume_m3: Optional[float] = Field(10.0, ge=0, description="Optional cargo volume in cubic meters")

    # Vehicle condition & maintenance telemetry
    condition: str = Field("good", description="Overall condition: excellent, good, average, poor")
    age_years: float = Field(3.0, ge=0, description="Vehicle age in years")
    odometer_km: float = Field(45000.0, ge=0, description="Cumulative odometer reading in km")
    maintenance_status: str = Field("ok", description="Maintenance status: ok, service_recommended, overdue, critical")
    is_available: bool = Field(True, description="Availability flag: True if ready for dispatch, False if grounded")

    # Electric / Battery parameters (used when powertrain in ('electric', 'hybrid'))
    battery_capacity_kwh: float = Field(68.0, ge=0, description="Total nameplate battery capacity in kWh")
    battery_soc_percent: float = Field(90.0, ge=0, le=100, description="Current State of Charge (0-100%)")
    battery_soh_percent: float = Field(95.0, ge=0, le=100, description="Battery State of Health (0-100%)")

    # Combustion / Fuel parameters (used when powertrain in ('diesel', 'petrol', 'hybrid'))
    fuel_tank_capacity_l: float = Field(70.0, ge=0, description="Fuel tank capacity in Litres")
    fuel_level_percent: float = Field(85.0, ge=0, le=100, description="Current fuel tank level (0-100%)")

    # Operational characteristics & physical limits
    base_consumption_per_100km: float = Field(9.5, gt=0, description="Nominal fuel (L/100km) or electricity (kWh/100km)")
    max_range_km: float = Field(250.0, gt=0, description="Maximum operational range on current charge/fuel in km")
    average_speed_kmh: float = Field(40.0, gt=0, description="Expected operational travel speed in km/h")
    max_operating_hours: float = Field(8.0, gt=0, description="Maximum continuous shift or driver duration in hours")

    # Operational economics & costs
    cost_per_km_usd: float = Field(0.35, ge=0, description="Variable maintenance and tire/wear cost per km ($)")
    cost_per_hour_usd: float = Field(22.0, ge=0, description="Driver wage and shift overhead cost per hour ($)")
    fixed_dispatch_cost_usd: float = Field(15.0, ge=0, description="Fixed mobilization cost per dispatched trip ($)")

    def calculate_usable_battery_kwh(self, reserve_margin_pct: float = 5.0) -> float:
        """
        Calculate usable battery capacity taking into account battery State of Health (aging degradation)
        and current State of Charge, minus a reserve margin to prevent roadside battery depletion.
        """
        if self.powertrain not in ("electric", "hybrid"):
            return 0.0
        # Usable = Capacity * (SoH / 100) * max(0, (SoC - reserve) / 100)
        health_factor = max(0.1, min(1.0, self.battery_soh_percent / 100.0))
        effective_capacity = self.battery_capacity_kwh * health_factor
        usable_soc = max(0.0, (self.battery_soc_percent - reserve_margin_pct) / 100.0)
        return round(effective_capacity * usable_soc, 2)

    def calculate_usable_fuel_litres(self, reserve_margin_pct: float = 5.0) -> float:
        """Calculate usable fuel taking into account current fuel level minus reserve margin."""
        if self.powertrain not in ("diesel", "petrol", "hybrid"):
            return 0.0
        usable_level = max(0.0, (self.fuel_level_percent - reserve_margin_pct) / 100.0)
        return round(self.fuel_tank_capacity_l * usable_level, 2)

    def calculate_physical_range_km(
        self,
        traffic_factor: float = 1.0,
        load_pct: float = 0.5,
    ) -> float:
        """
        Physics-calibrated feasible operating range based on usable energy/fuel,
        base consumption, traffic congestion penalty, and cargo payload factor.
        """
        traffic_sensitivity = 0.20
        load_sensitivity = 0.15
        adjustment = (1.0 + (traffic_factor - 1.0) * traffic_sensitivity) * (1.0 + load_pct * load_sensitivity)
        eff_consumption = max(0.01, (self.base_consumption_per_100km / 100.0) * adjustment)

        if self.powertrain == "electric":
            usable_kwh = self.calculate_usable_battery_kwh()
            computed_range = usable_kwh / eff_consumption
        elif self.powertrain in ("diesel", "petrol"):
            usable_l = self.calculate_usable_fuel_litres()
            computed_range = usable_l / eff_consumption
        else:  # hybrid
            usable_kwh = self.calculate_usable_battery_kwh()
            usable_l = self.calculate_usable_fuel_litres()
            # Hybrid blends electric and ICE range
            electric_range = usable_kwh / max(0.01, (eff_consumption * 0.7))
            fuel_range = usable_l / eff_consumption
            computed_range = electric_range + fuel_range

        # Bound by user-specified max_range_km if explicitly set lower
        final_range = min(computed_range, self.max_range_km) if self.max_range_km > 0 else computed_range
        return round(max(0.0, final_range), 1)

    def is_dispatchable(self) -> Tuple[bool, Optional[str]]:
        """
        Determine whether this vehicle is eligible for route assignment.
        Returns (is_dispatchable, reason_if_not).
        """
        if not self.is_available:
            return False, f"Vehicle '{self.name}' is marked unavailable (out of service)."
        if self.maintenance_status == "critical":
            return False, f"Vehicle '{self.name}' has critical maintenance overdue and cannot be dispatched."
        if self.powertrain == "electric" and self.battery_soc_percent <= 5.0:
            return False, f"Vehicle '{self.name}' battery charge ({self.battery_soc_percent}%) is below minimum 5% reserve."
        if self.powertrain in ("diesel", "petrol") and self.fuel_level_percent <= 5.0:
            return False, f"Vehicle '{self.name}' fuel level ({self.fuel_level_percent}%) is below minimum 5% reserve."
        return True, None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "veh-1",
                "name": "Van 1 (Ford E-Transit BEV)",
                "vehicle_type": "electric_van",
                "powertrain": "electric",
                "capacity_kg": 120.0,
                "cargo_volume_m3": 12.0,
                "condition": "good",
                "age_years": 2.0,
                "odometer_km": 35000.0,
                "maintenance_status": "ok",
                "is_available": True,
                "battery_capacity_kwh": 68.0,
                "battery_soc_percent": 85.0,
                "battery_soh_percent": 96.0,
                "base_consumption_per_100km": 28.0,
                "max_range_km": 190.0,
                "max_operating_hours": 8.0,
                "cost_per_km_usd": 0.28,
            }
        }


def generate_default_fleet_profiles(num_vehicles: int, default_capacity: float = 100.0) -> List[VehicleProfile]:
    """
    Generate realistic heterogeneous fleet profiles for K vehicles with varied powertrains and physical condition telemetry.
    """
    templates = [
        {
            "name_suffix": "(Ford E-Transit BEV)",
            "vehicle_type": "electric_van",
            "powertrain": "electric",
            "capacity_kg": default_capacity * 1.2,
            "cargo_volume_m3": 12.0,
            "condition": "excellent",
            "age_years": 1.5,
            "odometer_km": 28000.0,
            "maintenance_status": "ok",
            "is_available": True,
            "battery_capacity_kwh": 68.0,
            "battery_soc_percent": 90.0,
            "battery_soh_percent": 97.0,
            "base_consumption_per_100km": 26.0,
            "max_range_km": 210.0,
            "max_operating_hours": 8.0,
            "cost_per_km_usd": 0.24,
            "cost_per_hour_usd": 22.0,
            "fixed_dispatch_cost_usd": 12.0,
        },
        {
            "name_suffix": "(Mercedes Sprinter Diesel)",
            "vehicle_type": "van",
            "powertrain": "diesel",
            "capacity_kg": default_capacity * 1.5,
            "cargo_volume_m3": 14.0,
            "condition": "good",
            "age_years": 3.0,
            "odometer_km": 65000.0,
            "maintenance_status": "ok",
            "is_available": True,
            "fuel_tank_capacity_l": 75.0,
            "fuel_level_percent": 80.0,
            "base_consumption_per_100km": 9.5,
            "max_range_km": 280.0,
            "max_operating_hours": 9.0,
            "cost_per_km_usd": 0.38,
            "cost_per_hour_usd": 22.0,
            "fixed_dispatch_cost_usd": 18.0,
        },
        {
            "name_suffix": "(Ford Transit 3.5L Petrol)",
            "vehicle_type": "van",
            "powertrain": "petrol",
            "capacity_kg": default_capacity * 1.0,
            "cargo_volume_m3": 10.0,
            "condition": "average",
            "age_years": 4.5,
            "odometer_km": 92000.0,
            "maintenance_status": "service_recommended",
            "is_available": True,
            "fuel_tank_capacity_l": 80.0,
            "fuel_level_percent": 70.0,
            "base_consumption_per_100km": 11.2,
            "max_range_km": 240.0,
            "max_operating_hours": 8.0,
            "cost_per_km_usd": 0.42,
            "cost_per_hour_usd": 20.0,
            "fixed_dispatch_cost_usd": 15.0,
        },
        {
            "name_suffix": "(Transit Custom PHEV)",
            "vehicle_type": "van",
            "powertrain": "hybrid",
            "capacity_kg": default_capacity * 1.1,
            "cargo_volume_m3": 11.0,
            "condition": "good",
            "age_years": 2.0,
            "odometer_km": 42000.0,
            "maintenance_status": "ok",
            "is_available": True,
            "battery_capacity_kwh": 14.0,
            "battery_soc_percent": 85.0,
            "battery_soh_percent": 96.0,
            "fuel_tank_capacity_l": 54.0,
            "fuel_level_percent": 85.0,
            "base_consumption_per_100km": 6.8,
            "max_range_km": 300.0,
            "max_operating_hours": 8.5,
            "cost_per_km_usd": 0.32,
            "cost_per_hour_usd": 22.0,
            "fixed_dispatch_cost_usd": 14.0,
        },
    ]

    profiles = []
    for i in range(num_vehicles):
        tpl = templates[i % len(templates)]
        v_id = f"veh-{i + 1}"
        p = VehicleProfile(
            id=v_id,
            name=f"Vehicle {i + 1} {tpl['name_suffix']}",
            vehicle_type=tpl["vehicle_type"],
            powertrain=tpl["powertrain"],
            capacity_kg=float(tpl["capacity_kg"]),
            cargo_volume_m3=tpl.get("cargo_volume_m3", 10.0),
            condition=tpl.get("condition", "good"),
            age_years=tpl.get("age_years", 3.0),
            odometer_km=tpl.get("odometer_km", 40000.0),
            maintenance_status=tpl.get("maintenance_status", "ok"),
            is_available=tpl.get("is_available", True),
            battery_capacity_kwh=tpl.get("battery_capacity_kwh", 0.0),
            battery_soc_percent=tpl.get("battery_soc_percent", 0.0),
            battery_soh_percent=tpl.get("battery_soh_percent", 0.0),
            fuel_tank_capacity_l=tpl.get("fuel_tank_capacity_l", 0.0),
            fuel_level_percent=tpl.get("fuel_level_percent", 0.0),
            base_consumption_per_100km=tpl.get("base_consumption_per_100km", 10.0),
            max_range_km=tpl.get("max_range_km", 250.0),
            max_operating_hours=tpl.get("max_operating_hours", 8.0),
            cost_per_km_usd=tpl.get("cost_per_km_usd", 0.35),
            cost_per_hour_usd=tpl.get("cost_per_hour_usd", 22.0),
            fixed_dispatch_cost_usd=tpl.get("fixed_dispatch_cost_usd", 15.0),
        )
        profiles.append(p)
    return profiles
