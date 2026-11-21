/**
 * ROUTE/IQ Energy & Resource Savings Service (Frontend Engine)
 *
 * Implements scientific calculation of:
 * - Fuel consumption (L) and thermal/electrical energy (kWh)
 * - Tailpipe CO2 emissions vs indirect power grid emissions (kg CO2e)
 * - Commercial operational costs ($ USD)
 * - Comparative resource savings & emission abatements vs baseline solvers
 * - Real-time vehicle propulsion profile switching (Diesel, Petrol, Hybrid, Electric EV)
 *
 * References:
 * - US EPA 2024 GHG Emission Factors Hub
 * - UK DEFRA / BEIS 2023 Company GHG Reporting
 * - US EPA eGRID 2022/2024 Subregion NYUP/NYCW (NYC Grid Factor: 0.245 kg CO2/kWh)
 */

import {
  VehiclePropulsionType,
  VehicleRouteEnergy,
  AlgorithmEnergyProfile,
  EnergyComparison,
  VehicleRoute,
} from '../types';

export interface PropulsionModelConfig {
  id: VehiclePropulsionType;
  name: string;
  category: string;
  representativeVehicle: string;
  fuelType: 'fuel' | 'electricity';
  unitLabel: string;
  baseConsumptionPer100km: number;
  energyDensityKwhPerUnit: number;
  directTailpipeCo2KgPerUnit: number;
  upstreamCo2KgPerUnit: number;
  totalCo2KgPerUnit: number;
  unitCostUsd: number;
  trafficSensitivity: number;
  loadSensitivity: number;
  badgeColor: string;
  iconName: string;
}

export const PROPULSION_MODELS_FRONTEND: Record<VehiclePropulsionType, PropulsionModelConfig> = {
  diesel: {
    id: 'diesel',
    name: 'Diesel Delivery Van',
    category: 'Internal Combustion Engine (ICE)',
    representativeVehicle: 'Mercedes-Benz Sprinter 2500 / Ford Transit 2.0L TDCi',
    fuelType: 'fuel',
    unitLabel: 'L',
    baseConsumptionPer100km: 9.5,
    energyDensityKwhPerUnit: 10.0,
    directTailpipeCo2KgPerUnit: 2.68,
    upstreamCo2KgPerUnit: 0.58,
    totalCo2KgPerUnit: 3.26,
    unitCostUsd: 1.15,
    trafficSensitivity: 0.20,
    loadSensitivity: 0.15,
    badgeColor: 'border-amber-500/40 text-amber-500 bg-amber-500/10',
    iconName: 'Fuel',
  },
  petrol: {
    id: 'petrol',
    name: 'Petrol / Gasoline Van',
    category: 'Internal Combustion Engine (ICE)',
    representativeVehicle: 'Ford Transit 3.5L V6 Gasoline / Ram ProMaster',
    fuelType: 'fuel',
    unitLabel: 'L',
    baseConsumptionPer100km: 11.0,
    energyDensityKwhPerUnit: 8.9,
    directTailpipeCo2KgPerUnit: 2.31,
    upstreamCo2KgPerUnit: 0.52,
    totalCo2KgPerUnit: 2.83,
    unitCostUsd: 0.95,
    trafficSensitivity: 0.22,
    loadSensitivity: 0.15,
    badgeColor: 'border-orange-500/40 text-orange-500 bg-orange-500/10',
    iconName: 'Flame',
  },
  hybrid: {
    id: 'hybrid',
    name: 'Hybrid Delivery Van',
    category: 'Hybrid Electric Vehicle (HEV)',
    representativeVehicle: 'Ford Transit Custom PHEV / Toyota Proace City Hybrid',
    fuelType: 'fuel',
    unitLabel: 'L',
    baseConsumptionPer100km: 6.8,
    energyDensityKwhPerUnit: 8.9,
    directTailpipeCo2KgPerUnit: 2.31,
    upstreamCo2KgPerUnit: 0.52,
    totalCo2KgPerUnit: 2.83,
    unitCostUsd: 0.95,
    trafficSensitivity: 0.10,
    loadSensitivity: 0.15,
    badgeColor: 'border-teal-500/40 text-teal-500 bg-teal-500/10',
    iconName: 'Zap',
  },
  electric: {
    id: 'electric',
    name: 'Electric Delivery Van (EV)',
    category: 'Battery Electric Vehicle (BEV)',
    representativeVehicle: 'Rivian EDV 700 / Ford E-Transit Cargo / BrightDrop',
    fuelType: 'electricity',
    unitLabel: 'kWh',
    baseConsumptionPer100km: 28.0,
    energyDensityKwhPerUnit: 1.0,
    directTailpipeCo2KgPerUnit: 0.0,
    upstreamCo2KgPerUnit: 0.245,
    totalCo2KgPerUnit: 0.245,
    unitCostUsd: 0.18,
    trafficSensitivity: 0.08,
    loadSensitivity: 0.18,
    badgeColor: 'border-[#B7FF2A]/50 text-[#B7FF2A] bg-[#B7FF2A]/10',
    iconName: 'BatteryCharging',
  },
};

export const SCIENTIFIC_DATA_TAGS = {
  distance: 'MEASURED' as const,
  duration: 'ESTIMATED' as const,
  fuel_consumption: 'ESTIMATED' as const,
  energy_consumption: 'ESTIMATED' as const,
  co2_emissions: 'ESTIMATED' as const,
  operational_cost: 'ESTIMATED' as const,
  vehicle_propulsion_model: 'ASSUMED' as const,
  fuel_and_electricity_prices: 'ASSUMED' as const,
  grid_carbon_intensity: 'ASSUMED' as const,
};

export function computeRouteLoadFactor(
  routeLoad: number,
  vehicleCapacity: number,
  loadSensitivity: number = 0.15
): number {
  if (vehicleCapacity <= 0 || routeLoad <= 0) return 1.0;
  const utilization = Math.min(Math.max(routeLoad / vehicleCapacity, 0.0), 1.5);
  return 1.0 + loadSensitivity * utilization;
}

export function computeRouteTrafficFactor(
  trafficFactor: number = 1.0,
  trafficSensitivity: number = 0.20
): number {
  const deviation = Math.max(trafficFactor - 1.0, 0.0);
  return 1.0 + trafficSensitivity * Math.min(deviation, 2.0);
}

export function calculateVehicleRouteEnergy(
  route: VehicleRoute,
  vehicleIdx: number,
  propulsionType: VehiclePropulsionType = 'diesel',
  vehicleCapacity: number = 0,
  trafficFactor: number = 1.0
): VehicleRouteEnergy {
  const model = PROPULSION_MODELS_FRONTEND[propulsionType] || PROPULSION_MODELS_FRONTEND.diesel;
  const distKm = Number(route.distance_km || 0);
  const durationMin = Number(route.total_duration_min || route.driving_time_min || 0);
  const load = Number(route.load || 0);
  const cap = Number(route.capacity || vehicleCapacity || 0);

  const fLoad = computeRouteLoadFactor(load, cap, model.loadSensitivity);
  const fTraffic = computeRouteTrafficFactor(trafficFactor, model.trafficSensitivity);
  const totalMultiplier = fLoad * fTraffic;

  const isElectric = model.fuelType === 'electricity';
  let fuelLitres = 0;
  let energyKwh = 0;
  let tailpipeCo2 = 0;
  let upstreamCo2 = 0;
  let costUsd = 0;

  if (isElectric) {
    fuelLitres = 0;
    energyKwh = distKm * (model.baseConsumptionPer100km / 100.0) * totalMultiplier;
    tailpipeCo2 = 0;
    upstreamCo2 = energyKwh * model.upstreamCo2KgPerUnit;
    costUsd = energyKwh * model.unitCostUsd;
  } else {
    fuelLitres = distKm * (model.baseConsumptionPer100km / 100.0) * totalMultiplier;
    energyKwh = fuelLitres * model.energyDensityKwhPerUnit;
    tailpipeCo2 = fuelLitres * model.directTailpipeCo2KgPerUnit;
    upstreamCo2 = fuelLitres * model.upstreamCo2KgPerUnit;
    costUsd = fuelLitres * model.unitCostUsd;
  }

  const totalCo2 = tailpipeCo2 + upstreamCo2;
  const vp = route.vehicle_profile;
  const usableRange = vp?.max_range_km || 250.0;
  const remainingRange = Math.max(0, Math.round((usableRange - distKm) * 10) / 10);
  const isRangeFeasible = distKm <= usableRange + 0.01;

  let remainingSoc = null;
  let remainingFuel = null;
  if (isElectric && vp?.battery_capacity_kwh) {
    const effCap = vp.battery_capacity_kwh * ((vp.battery_soh_percent || 100) / 100.0);
    const socConsumed = (energyKwh / Math.max(effCap, 1.0)) * 100.0;
    remainingSoc = Math.max(0, Math.round(((vp.battery_soc_percent || 100) - socConsumed) * 10) / 10);
  } else if (!isElectric && vp?.fuel_tank_capacity_l) {
    const fuelConsumed = (fuelLitres / Math.max(vp.fuel_tank_capacity_l, 1.0)) * 100.0;
    remainingFuel = Math.max(0, Math.round(((vp.fuel_level_percent || 100) - fuelConsumed) * 10) / 10);
  }

  return {
    vehicle_id: route.vehicle_id || vehicleIdx + 1,
    vehicle_profile: vp,
    distance_km: Math.round(distKm * 100) / 100,
    duration_min: Math.round(durationMin * 10) / 10,
    stops_count: (route.customer_stops || route.stops || []).length,
    load: Math.round(load * 10) / 10,
    capacity: Math.round(cap * 10) / 10,
    utilization_pct: cap > 0 ? Math.round((load / cap) * 1000) / 10 : 0,
    load_factor: Math.round(fLoad * 1000) / 1000,
    traffic_factor: Math.round(fTraffic * 1000) / 1000,
    fuel_consumption_litres: Math.round(fuelLitres * 1000) / 1000,
    energy_consumption_kwh: Math.round(energyKwh * 100) / 100,
    direct_tailpipe_co2_kg: Math.round(tailpipeCo2 * 1000) / 1000,
    indirect_grid_co2_kg: isElectric ? Math.round(upstreamCo2 * 1000) / 1000 : 0,
    upstream_well_to_tank_co2_kg: Math.round(upstreamCo2 * 1000) / 1000,
    total_co2_kg: Math.round(totalCo2 * 1000) / 1000,
    operational_cost_usd: Math.round(costUsd * 100) / 100,
    remaining_soc_pct: remainingSoc,
    remaining_fuel_pct: remainingFuel,
    remaining_range_km: remainingRange,
    is_range_feasible: isRangeFeasible,
    is_shift_feasible: (durationMin / 60.0) <= (vp?.max_operating_hours || 8.0),
    is_all_feasible: isRangeFeasible && load <= cap + 0.01,
    unit_label: model.unitLabel,
  };
}

export function calculateAlgorithmEnergyProfile(
  algoId: string,
  algoName: string,
  category: string,
  routes: VehicleRoute[],
  totalDistanceKm: number,
  totalDurationMin: number,
  isFeasible: boolean,
  propulsionType: VehiclePropulsionType = 'diesel',
  vehicleCapacity: number = 0,
  trafficFactor: number = 1.0
): AlgorithmEnergyProfile {
  const model = PROPULSION_MODELS_FRONTEND[propulsionType] || PROPULSION_MODELS_FRONTEND.diesel;
  const breakdowns: VehicleRouteEnergy[] = [];

  let totalFuel = 0;
  let totalKwh = 0;
  let totalTailpipe = 0;
  let totalUpstream = 0;
  let totalCost = 0;

  if (routes && routes.length > 0) {
    routes.forEach((r, idx) => {
      const v = calculateVehicleRouteEnergy(r, idx, propulsionType, vehicleCapacity, trafficFactor);
      breakdowns.push(v);
      totalFuel += v.fuel_consumption_litres;
      totalKwh += v.energy_consumption_kwh;
      totalTailpipe += v.direct_tailpipe_co2_kg;
      totalUpstream += v.upstream_well_to_tank_co2_kg;
      totalCost += v.operational_cost_usd;
    });
  } else {
    // Fallback if individual routes missing
    const fTraffic = computeRouteTrafficFactor(trafficFactor, model.trafficSensitivity);
    const dist = totalDistanceKm || 0;
    const isElectric = model.fuelType === 'electricity';
    if (isElectric) {
      totalFuel = 0;
      totalKwh = dist * (model.baseConsumptionPer100km / 100.0) * fTraffic;
      totalTailpipe = 0;
      totalUpstream = totalKwh * model.upstreamCo2KgPerUnit;
      totalCost = totalKwh * model.unitCostUsd;
    } else {
      totalFuel = dist * (model.baseConsumptionPer100km / 100.0) * fTraffic;
      totalKwh = totalFuel * model.energyDensityKwhPerUnit;
      totalTailpipe = totalFuel * model.directTailpipeCo2KgPerUnit;
      totalUpstream = totalFuel * model.upstreamCo2KgPerUnit;
      totalCost = totalFuel * model.unitCostUsd;
    }
  }

  const totalCo2 = totalTailpipe + totalUpstream;
  const finalDist = breakdowns.length > 0 ? breakdowns.reduce((sum, v) => sum + v.distance_km, 0) : totalDistanceKm;
  const finalDuration = breakdowns.length > 0 ? breakdowns.reduce((sum, v) => sum + v.duration_min, 0) : totalDurationMin;

  return {
    algorithm_id: algoId,
    algorithm_name: algoName,
    category,
    is_feasible: isFeasible,
    propulsion_type: propulsionType,
    propulsion_name: model.name,
    unit_label: model.unitLabel,
    total_distance_km: Math.round(finalDist * 100) / 100,
    total_duration_min: Math.round(finalDuration * 10) / 10,
    vehicles_count: breakdowns.length || (routes ? routes.length : 1),
    fuel_consumption_litres: Math.round(totalFuel * 1000) / 1000,
    energy_consumption_kwh: Math.round(totalKwh * 100) / 100,
    direct_tailpipe_co2_kg: Math.round(totalTailpipe * 1000) / 1000,
    indirect_grid_co2_kg: model.fuelType === 'electricity' ? Math.round(totalUpstream * 1000) / 1000 : 0,
    upstream_well_to_tank_co2_kg: Math.round(totalUpstream * 1000) / 1000,
    total_co2_kg: Math.round(totalCo2 * 1000) / 1000,
    operational_cost_usd: Math.round(totalCost * 100) / 100,
    vehicle_breakdowns: breakdowns,
    data_tags: SCIENTIFIC_DATA_TAGS,
  };
}

export function calculateEnergyComparison(
  target: AlgorithmEnergyProfile,
  baseline: AlgorithmEnergyProfile
): EnergyComparison {
  const deltaDist = baseline.total_distance_km - target.total_distance_km;
  const deltaFuel = baseline.fuel_consumption_litres - target.fuel_consumption_litres;
  const deltaKwh = baseline.energy_consumption_kwh - target.energy_consumption_kwh;
  const deltaCo2 = baseline.total_co2_kg - target.total_co2_kg;
  const deltaCost = baseline.operational_cost_usd - target.operational_cost_usd;

  const pct = (delta: number, base: number) => {
    if (Math.abs(base) < 1e-6) return 0.0;
    return Math.round((delta / base) * 10000) / 100;
  };

  const pctDist = pct(deltaDist, baseline.total_distance_km);
  const pctFuel = pct(deltaFuel, baseline.fuel_consumption_litres);
  const pctKwh = pct(deltaKwh, baseline.energy_consumption_kwh);
  const pctCo2 = pct(deltaCo2, baseline.total_co2_kg);
  const pctCost = pct(deltaCost, baseline.operational_cost_usd);

  let statusLabel: 'RESOURCE_SAVING' | 'RESOURCE_DEFICIT' | 'IDENTICAL_TO_BASELINE' = 'IDENTICAL_TO_BASELINE';
  let impactSummary = 'Identical resource consumption to baseline';

  if (Math.abs(deltaDist) > 0.01) {
    if (deltaDist > 0) {
      statusLabel = 'RESOURCE_SAVING';
      impactSummary = `Saves ${Math.abs(pctKwh)}% energy (${Math.round(deltaKwh * 10) / 10} kWh) and avoids ${Math.round(deltaCo2 * 100) / 100} kg CO2`;
    } else {
      statusLabel = 'RESOURCE_DEFICIT';
      impactSummary = `Uses ${Math.abs(pctKwh)}% more energy (+${Math.round(Math.abs(deltaKwh) * 10) / 10} kWh) than baseline`;
    }
  }

  return {
    target_algorithm: target.algorithm_id,
    baseline_algorithm: baseline.algorithm_id,
    propulsion_type: target.propulsion_type,
    delta_distance_km: Math.round(deltaDist * 100) / 100,
    delta_fuel_litres: Math.round(deltaFuel * 1000) / 1000,
    delta_energy_kwh: Math.round(deltaKwh * 100) / 100,
    delta_co2_kg: Math.round(deltaCo2 * 1000) / 1000,
    delta_cost_usd: Math.round(deltaCost * 100) / 100,
    pct_distance_savings: pctDist,
    pct_fuel_savings: pctFuel,
    pct_energy_savings: pctKwh,
    pct_co2_savings: pctCo2,
    pct_cost_savings: pctCost,
    is_saving: deltaDist > 0.01,
    is_identical: Math.abs(deltaDist) <= 0.01,
    status_label: statusLabel,
    impact_summary: impactSummary,
  };
}

// Formatters
export function formatKwh(val: number): string {
  return `${val.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })} kWh`;
}

export function formatLitres(val: number): string {
  return `${val.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} L`;
}

export function formatCo2Kg(val: number): string {
  return `${val.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} kg CO₂`;
}

export function formatUsd(val: number): string {
  return `$${val.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

export function formatPct(val: number): string {
  const sign = val > 0 ? '+' : '';
  return `${sign}${val.toFixed(1)}%`;
}
