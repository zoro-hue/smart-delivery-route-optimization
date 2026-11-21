import React, { useState, useMemo } from 'react';
import {
  Zap,
  Fuel,
  Leaf,
  DollarSign,
  TrendingDown,
  TrendingUp,
  Info,
  ChevronDown,
  ChevronUp,
  ShieldCheck,
  Flame,
  BatteryCharging,
  Gauge,
  Check,
  Sparkles,
  Truck,
  RotateCcw,
  AlertCircle,
} from 'lucide-react';
import {
  VehiclePropulsionType,
  OptimizationResponse,
  VehicleRoute,
  ComparisonItem,
  FullEnergyAnalysis,
  AlgorithmEnergyProfile,
} from '../types';
import {
  PROPULSION_MODELS_FRONTEND,
  calculateAlgorithmEnergyProfile,
  calculateEnergyComparison,
  formatKwh,
  formatLitres,
  formatCo2Kg,
  formatUsd,
  formatPct,
} from '../services/energy';

interface EnergyResourceAnalysisProps {
  optimizationData: OptimizationResponse;
  activeAlgo: string;
  onSelectAlgorithm?: (algoId: string) => void;
  isDark?: boolean;
}

export const EnergyResourceAnalysis: React.FC<EnergyResourceAnalysisProps> = ({
  optimizationData,
  activeAlgo,
  onSelectAlgorithm,
  isDark = true,
}) => {
  const [selectedPropulsion, setSelectedPropulsion] = useState<VehiclePropulsionType>('diesel');
  const [customBaseline, setCustomBaseline] = useState<string>('ortools');
  const [showMethodology, setShowMethodology] = useState<boolean>(false);
  const [showAllVehicles, setShowAllVehicles] = useState<boolean>(false);

  const comparisonSummary = optimizationData?.comparison_summary;
  const items: ComparisonItem[] = useMemo(
    () => comparisonSummary?.items || [],
    [comparisonSummary]
  );
  const results = optimizationData?.results || {};
  const problem = optimizationData?.problem || { num_vehicles: 3, vehicle_capacity: 100 };
  const vehicleCapacity = Number(problem?.vehicle_capacity || 100);
  const trafficFactor = Number(problem?.traffic_factor || 1.0);

  // Compute or extract profiles for all algorithms under the selected propulsion type
  const profilesMap: Record<string, AlgorithmEnergyProfile> = useMemo(() => {
    // If backend provided precomputed profiles_by_propulsion, check it first
    const backendAnalysis: FullEnergyAnalysis | undefined = comparisonSummary?.energy_analysis;
    if (
      backendAnalysis?.profiles_by_propulsion &&
      backendAnalysis.profiles_by_propulsion[selectedPropulsion]
    ) {
      return backendAnalysis.profiles_by_propulsion[selectedPropulsion];
    }

    // Otherwise compute dynamically client-side for zero latency
    const map: Record<string, AlgorithmEnergyProfile> = {};
    items.forEach((item) => {
      const algoResult = results[item.id];
      const routes: VehicleRoute[] = algoResult?.routes || [];
      const dist = item.total_distance_km || algoResult?.total_distance_km || 0;
      const dur = item.total_duration_min || item.total_travel_time_min || 0;
      map[item.id] = calculateAlgorithmEnergyProfile(
        item.id,
        item.name,
        item.category,
        routes,
        dist,
        dur,
        item.is_feasible,
        selectedPropulsion,
        vehicleCapacity,
        trafficFactor
      );
    });

    // Also include activeAlgo if not in items
    if (activeAlgo && !map[activeAlgo] && results[activeAlgo]) {
      const res = results[activeAlgo];
      map[activeAlgo] = calculateAlgorithmEnergyProfile(
        activeAlgo,
        res.algorithm_name || activeAlgo.toUpperCase(),
        res.category || 'classical',
        res.routes || [],
        res.total_distance_km || 0,
        res.total_duration_min || res.total_travel_time_min || 0,
        res.is_feasible,
        selectedPropulsion,
        vehicleCapacity,
        trafficFactor
      );
    }
    return map;
  }, [comparisonSummary, selectedPropulsion, items, results, activeAlgo, vehicleCapacity, trafficFactor]);

  // Active algorithm profile
  const activeProfile = profilesMap[activeAlgo] || profilesMap['routeiq_cooperative'] || Object.values(profilesMap)[0];

  // Baseline algorithm profile
  const effectiveBaselineId = customBaseline in profilesMap ? customBaseline : (items[0]?.id || 'ortools');
  const baselineProfile = profilesMap[effectiveBaselineId] || activeProfile;

  // Comparison between active and baseline
  const comparison = useMemo(() => {
    if (!activeProfile || !baselineProfile) return null;
    return calculateEnergyComparison(activeProfile, baselineProfile);
  }, [activeProfile, baselineProfile]);

  // Model specs
  const activeModel = PROPULSION_MODELS_FRONTEND[selectedPropulsion];

  const getPropulsionIcon = (type: VehiclePropulsionType) => {
    switch (type) {
      case 'diesel':
        return <Fuel className="w-4 h-4 text-amber-500" />;
      case 'petrol':
        return <Flame className="w-4 h-4 text-orange-500" />;
      case 'hybrid':
        return <Zap className="w-4 h-4 text-teal-400" />;
      case 'electric':
        return <BatteryCharging className="w-4 h-4 text-[#B7FF2A]" />;
    }
  };

  if (!activeProfile) {
    return null;
  }

  const isSaving = comparison?.is_saving ?? false;
  const isIdentical = comparison?.is_identical ?? true;
  const isDeficit = !isSaving && !isIdentical;

  return (
    <div className="mt-6 rounded-2xl bg-white dark:bg-[#101014] border border-black/10 dark:border-white/10 p-4 sm:p-5 shadow-2xs">
      {/* Header & Badges */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 pb-4 border-b border-black/5 dark:border-white/5 font-heading">
        <div>
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-[#B7FF2A]/15 text-black dark:text-[#B7FF2A] border border-[#B7FF2A]/30">
              <Leaf className="w-3 h-3" /> Green Logistics & Decarbonization
            </span>
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[9px] font-normal bg-black/5 dark:bg-white/5 text-[#555555] dark:text-[#A1A1AA] border border-black/5 dark:border-white/5">
              <ShieldCheck className="w-3 h-3 text-[#B7FF2A]" /> EPA 2024 · DEFRA · eGRID NYC
            </span>
          </div>
          <h2 className="text-base sm:text-[17px] font-semibold tracking-tight text-[#080808] dark:text-white font-heading">
            Energy & Resource Savings Analysis
          </h2>
          <p className="text-[11px] sm:text-xs text-[#666666] dark:text-[#8E8E93] mt-0.5 max-w-2xl leading-relaxed font-normal">
            Quantifying fuel, thermal/electrical energy, well-to-wheel greenhouse emissions, and operational cost savings across vehicle propulsion technologies.
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2 self-start md:self-center">
          <button
            onClick={() => setShowMethodology(!showMethodology)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-[11px] font-semibold border border-black/10 dark:border-white/10 bg-black/[0.02] dark:bg-white/[0.02] hover:bg-black/5 dark:hover:bg-white/5 text-[#555555] dark:text-[#A1A1AA] transition-colors cursor-pointer"
          >
            <Info className="w-3 h-3 text-blue-400" />
            {showMethodology ? 'Hide Methodology' : 'Methodology & Factors'}
          </button>
        </div>
      </div>

      {/* Interactive Controls Bar: Propulsion Selector & Baseline Selector */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-3 py-3.5 border-b border-black/5 dark:border-white/5 items-center font-heading">
        {/* Propulsion Type Buttons */}
        <div className="lg:col-span-8">
          <span className="text-[10px] font-medium uppercase tracking-wider text-[#777777] dark:text-[#8E8E93] block mb-1.5 font-heading">
            Vehicle Propulsion Architecture
          </span>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {(['diesel', 'petrol', 'hybrid', 'electric'] as VehiclePropulsionType[]).map((pType) => {
              const model = PROPULSION_MODELS_FRONTEND[pType];
              const isSelected = selectedPropulsion === pType;
              return (
                <button
                  key={pType}
                  onClick={() => setSelectedPropulsion(pType)}
                  className={`flex flex-col text-left p-2.5 rounded-xl border transition-all cursor-pointer ${
                    isSelected
                      ? 'bg-black/5 dark:bg-white/10 border-[#B7FF2A] shadow-2xs'
                      : 'border-black/5 dark:border-white/5 bg-transparent hover:bg-black/[0.02] dark:hover:bg-white/[0.03]'
                  }`}
                >
                  <div className="flex items-center justify-between mb-0.5">
                    <span className="p-1 rounded-lg bg-black/5 dark:bg-white/5">
                      {getPropulsionIcon(pType)}
                    </span>
                    {isSelected && <Check className="w-3 h-3 text-[#B7FF2A]" />}
                  </div>
                  <span className="text-[11px] font-semibold text-[#080808] dark:text-white truncate">
                    {model.name.replace(' Delivery Van', '')}
                  </span>
                  <span className="text-[9px] text-[#777777] dark:text-[#8E8E93] font-normal tabular-nums">
                    {model.baseConsumptionPer100km} {model.unitLabel}/100km
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Baseline Selector */}
        <div className="lg:col-span-4 bg-black/[0.02] dark:bg-white/[0.02] p-2.5 sm:p-3 rounded-xl border border-black/5 dark:border-white/5">
          <label className="text-[10px] font-medium uppercase tracking-wider text-[#777777] dark:text-[#8E8E93] block mb-1 font-heading">
            Comparison Baseline Solver
          </label>
          <div className="flex items-center gap-2">
            <select
              value={effectiveBaselineId}
              aria-label="Comparison baseline solver"
              onChange={(e) => setCustomBaseline(e.target.value)}
              className="w-full bg-white dark:bg-[#18181C] border border-black/10 dark:border-white/10 rounded-lg px-2.5 py-1.5 text-[11px] font-medium text-[#080808] dark:text-white focus:outline-none focus:ring-1 focus:ring-[#B7FF2A] cursor-pointer font-heading"
            >
              {items.map((it) => (
                <option key={it.id} value={it.id}>
                  {it.name} ({it.total_distance_km} km)
                </option>
              ))}
            </select>
          </div>
          <p className="text-[9px] text-[#777777] dark:text-[#8E8E93] mt-1 leading-tight font-normal">
            Selected route will be evaluated against this baseline.
          </p>
        </div>
      </div>

      {/* Hero Comparative Resource Savings Banner */}
      {comparison && (
        <div className="my-4 font-heading">
          <div
            className={`p-3.5 sm:p-4 rounded-xl border flex flex-col md:flex-row items-start md:items-center justify-between gap-3 transition-all ${
              isSaving
                ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-950 dark:text-emerald-100'
                : isIdentical
                ? 'bg-blue-500/10 border-blue-500/30 text-blue-950 dark:text-blue-100'
                : 'bg-amber-500/10 border-amber-500/30 text-amber-950 dark:text-amber-100'
            }`}
          >
            <div className="flex items-center gap-3">
              <div
                className={`p-2 rounded-xl ${
                  isSaving
                    ? 'bg-emerald-500/20 text-emerald-600 dark:text-emerald-400'
                    : isIdentical
                    ? 'bg-blue-500/20 text-blue-600 dark:text-blue-400'
                    : 'bg-amber-500/20 text-amber-600 dark:text-amber-400'
                }`}
              >
                {isSaving ? (
                  <TrendingDown className="w-4 h-4" />
                ) : isIdentical ? (
                  <Gauge className="w-4 h-4" />
                ) : (
                  <TrendingUp className="w-4 h-4" />
                )}
              </div>
              <div>
                <div className="flex items-center gap-1.5 flex-wrap">
                  <span className="text-[10px] font-semibold uppercase tracking-wider px-1.5 py-0.5 rounded bg-black/10 dark:bg-white/10">
                    {comparison.status_label.replace(/_/g, ' ')}
                  </span>
                  <span className="text-[10px] text-[#555555] dark:text-[#A1A1AA] font-normal">
                    vs. {profilesMap[effectiveBaselineId]?.algorithm_name || effectiveBaselineId}
                  </span>
                </div>
                <h3 className="text-xs sm:text-sm font-semibold mt-0.5 font-heading">
                  {comparison.impact_summary}
                </h3>
              </div>
            </div>

            {/* Savings Quick Metric Pills */}
            <div className="flex items-center gap-2 flex-wrap">
              <div className="px-2.5 py-1.5 rounded-lg bg-white/60 dark:bg-black/40 border border-black/5 dark:border-white/5 text-right">
                <span className="text-[9px] text-[#777777] dark:text-[#8E8E93] uppercase block font-normal">
                  Energy Delta
                </span>
                <span
                  className={`text-xs font-semibold tabular-nums font-heading ${
                    comparison.delta_energy_kwh > 0
                      ? 'text-emerald-600 dark:text-emerald-400'
                      : comparison.delta_energy_kwh < 0
                      ? 'text-amber-600 dark:text-amber-400'
                      : 'text-gray-500'
                  }`}
                >
                  {comparison.delta_energy_kwh > 0 ? '-' : comparison.delta_energy_kwh < 0 ? '+' : ''}
                  {Math.abs(comparison.delta_energy_kwh)} kWh ({formatPct(comparison.pct_energy_savings)})
                </span>
              </div>

              <div className="px-2.5 py-1.5 rounded-lg bg-white/60 dark:bg-black/40 border border-black/5 dark:border-white/5 text-right">
                <span className="text-[9px] text-[#777777] dark:text-[#8E8E93] uppercase block font-normal">
                  CO₂ Abatement
                </span>
                <span
                  className={`text-xs font-semibold tabular-nums font-heading ${
                    comparison.delta_co2_kg > 0
                      ? 'text-emerald-600 dark:text-emerald-400'
                      : comparison.delta_co2_kg < 0
                      ? 'text-amber-600 dark:text-amber-400'
                      : 'text-gray-500'
                  }`}
                >
                  {comparison.delta_co2_kg > 0 ? '-' : comparison.delta_co2_kg < 0 ? '+' : ''}
                  {Math.abs(comparison.delta_co2_kg)} kg
                </span>
              </div>

              <div className="px-2.5 py-1.5 rounded-lg bg-white/60 dark:bg-black/40 border border-black/5 dark:border-white/5 text-right">
                <span className="text-[9px] text-[#777777] dark:text-[#8E8E93] uppercase block font-normal">
                  Fleet Cost Saved
                </span>
                <span
                  className={`text-xs font-semibold tabular-nums font-heading ${
                    comparison.delta_cost_usd > 0
                      ? 'text-emerald-600 dark:text-emerald-400'
                      : comparison.delta_cost_usd < 0
                      ? 'text-amber-600 dark:text-amber-400'
                      : 'text-gray-500'
                  }`}
                >
                  {comparison.delta_cost_usd >= 0 ? '+' : ''}
                  {formatUsd(comparison.delta_cost_usd)}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 4 Primary Resource Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mb-5 font-heading">
        {/* 1. Thermal & Electrical Energy */}
        <div className="p-3.5 rounded-xl bg-black/[0.02] dark:bg-white/[0.02] border border-black/5 dark:border-white/5 relative overflow-hidden">
          <div className="flex items-center justify-between text-[#777777] dark:text-[#8E8E93] mb-1.5">
            <span className="text-[10px] font-medium uppercase tracking-wider font-heading">
              Total Energy Consumption
            </span>
            <span className="text-[9px] px-1.5 py-0.5 rounded bg-black/5 dark:bg-white/10 text-amber-500 font-semibold">
              ESTIMATED
            </span>
          </div>
          <div className="flex items-baseline gap-1.5">
            <span className="text-xl sm:text-2xl font-semibold tabular-nums text-[#080808] dark:text-white font-heading">
              {activeProfile.energy_consumption_kwh.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })}
            </span>
            <span className="text-[11px] font-normal text-[#777777] dark:text-[#8E8E93]">kWh</span>
          </div>
          <div className="mt-2 flex items-center justify-between text-[10px] text-[#777777] dark:text-[#8E8E93] pt-1.5 border-t border-black/5 dark:border-white/5 font-normal">
            <span>Thermal/Electrical Equivalent</span>
            <span className="font-medium tabular-nums">
              {(activeProfile.energy_consumption_kwh * 3.6).toFixed(1)} MJ
            </span>
          </div>
        </div>

        {/* 2. Fuel Consumption */}
        <div className="p-3.5 rounded-xl bg-black/[0.02] dark:bg-white/[0.02] border border-black/5 dark:border-white/5 relative overflow-hidden">
          <div className="flex items-center justify-between text-[#777777] dark:text-[#8E8E93] mb-1.5">
            <span className="text-[10px] font-medium uppercase tracking-wider font-heading">
              {activeModel.fuelType === 'electricity' ? 'Direct Battery Draw' : 'Fuel Consumption'}
            </span>
            <span className="text-[9px] px-1.5 py-0.5 rounded bg-black/5 dark:bg-white/10 text-amber-500 font-semibold">
              ESTIMATED
            </span>
          </div>
          <div className="flex items-baseline gap-1.5">
            <span className="text-xl sm:text-2xl font-semibold tabular-nums text-[#080808] dark:text-white font-heading">
              {activeModel.fuelType === 'electricity'
                ? activeProfile.energy_consumption_kwh.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })
                : activeProfile.fuel_consumption_litres.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </span>
            <span className="text-[11px] font-normal text-[#777777] dark:text-[#8E8E93]">
              {activeModel.unitLabel}
            </span>
          </div>
          <div className="mt-2 flex items-center justify-between text-[10px] text-[#777777] dark:text-[#8E8E93] pt-1.5 border-t border-black/5 dark:border-white/5 font-normal">
            <span>Rate per 100 km</span>
            <span className="font-medium tabular-nums">
              {activeProfile.total_distance_km > 0
                ? (
                    (activeModel.fuelType === 'electricity' ? activeProfile.energy_consumption_kwh : activeProfile.fuel_consumption_litres) /
                    (activeProfile.total_distance_km / 100.0)
                  ).toFixed(2)
                : activeModel.baseConsumptionPer100km}{' '}
              {activeModel.unitLabel}/100km
            </span>
          </div>
        </div>

        {/* 3. CO2 Emissions */}
        <div className="p-3.5 rounded-xl bg-black/[0.02] dark:bg-white/[0.02] border border-black/5 dark:border-white/5 relative overflow-hidden">
          <div className="flex items-center justify-between text-[#777777] dark:text-[#8E8E93] mb-1.5">
            <span className="text-[10px] font-medium uppercase tracking-wider font-heading">
              Well-to-Wheel CO₂e
            </span>
            <span className="text-[9px] px-1.5 py-0.5 rounded bg-black/5 dark:bg-white/10 text-amber-500 font-semibold">
              ESTIMATED
            </span>
          </div>
          <div className="flex items-baseline gap-1.5">
            <span className="text-xl sm:text-2xl font-semibold tabular-nums text-[#080808] dark:text-white font-heading">
              {activeProfile.total_co2_kg.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </span>
            <span className="text-[11px] font-normal text-[#777777] dark:text-[#8E8E93]">kg CO₂</span>
          </div>
          <div className="mt-2 flex items-center justify-between text-[10px] text-[#777777] dark:text-[#8E8E93] pt-1.5 border-t border-black/5 dark:border-white/5 font-normal">
            <span>
              {activeModel.fuelType === 'electricity' ? 'Indirect Grid Gen' : 'Tailpipe Combustion'}
            </span>
            <span className="font-medium tabular-nums">
              {activeModel.fuelType === 'electricity'
                ? `${activeProfile.indirect_grid_co2_kg.toFixed(2)} kg`
                : `${activeProfile.direct_tailpipe_co2_kg.toFixed(2)} kg`}
            </span>
          </div>
        </div>

        {/* 4. Fleet Operational Cost */}
        <div className="p-3.5 rounded-xl bg-black/[0.02] dark:bg-white/[0.02] border border-black/5 dark:border-white/5 relative overflow-hidden">
          <div className="flex items-center justify-between text-[#777777] dark:text-[#8E8E93] mb-1.5">
            <span className="text-[10px] font-medium uppercase tracking-wider font-heading">
              Trip Energy Cost
            </span>
            <span className="text-[9px] px-1.5 py-0.5 rounded bg-black/5 dark:bg-white/10 text-purple-400 font-semibold">
              ASSUMED
            </span>
          </div>
          <div className="flex items-baseline gap-1.5">
            <span className="text-xl sm:text-2xl font-semibold tabular-nums text-[#080808] dark:text-white font-heading">
              {formatUsd(activeProfile.operational_cost_usd)}
            </span>
            <span className="text-[11px] font-normal text-[#777777] dark:text-[#8E8E93]">USD</span>
          </div>
          <div className="mt-2 flex items-center justify-between text-[10px] text-[#777777] dark:text-[#8E8E93] pt-1.5 border-t border-black/5 dark:border-white/5 font-normal">
            <span>Tariff Rate</span>
            <span className="font-medium tabular-nums">
              ${activeModel.unitCostUsd.toFixed(2)} / {activeModel.unitLabel}
            </span>
          </div>
        </div>
      </div>
      {/* Vehicle-wise Breakdown Accordion */}
      {activeProfile.vehicle_breakdowns && activeProfile.vehicle_breakdowns.length > 0 && (
        <div className="mb-4 rounded-xl border border-black/5 dark:border-white/5 bg-black/[0.01] dark:bg-white/[0.01] overflow-hidden font-heading">
          <button
            onClick={() => setShowAllVehicles(!showAllVehicles)}
            className="w-full flex items-center justify-between p-3 text-left hover:bg-black/[0.02] dark:hover:bg-white/[0.02] transition-colors cursor-pointer"
          >
            <div className="flex items-center gap-2">
              <Truck className="w-3.5 h-3.5 text-[#B7FF2A]" />
              <span className="text-xs font-semibold text-[#080808] dark:text-white font-heading">
                Vehicle-Specific Resource Schedules ({activeProfile.vehicle_breakdowns.length} Vehicles)
              </span>
              <span className="text-[9px] px-1.5 py-0.2 rounded-full bg-black/5 dark:bg-white/10 text-[#777777] dark:text-[#A1A1AA] font-normal">
                Payload & Congestion Corrected
              </span>
            </div>
            {showAllVehicles ? (
              <ChevronUp className="w-3.5 h-3.5 text-[#777777]" />
            ) : (
              <ChevronDown className="w-3.5 h-3.5 text-[#777777]" />
            )}
          </button>

          {showAllVehicles && (
            <div className="p-3 pt-0 overflow-x-auto">
              <table className="w-full text-left text-[11px] tabular-nums font-heading">
                <thead>
                  <tr className="border-b border-black/5 dark:border-white/5 text-[#777777] dark:text-[#8E8E93] text-[9px] uppercase tracking-wider font-semibold">
                    <th className="py-2 px-2.5">Vehicle Profile</th>
                    <th className="py-2 px-2.5">Powertrain</th>
                    <th className="py-2 px-2.5">Distance & Range</th>
                    <th className="py-2 px-2.5">Remaining Energy / Fuel</th>
                    <th className="py-2 px-2.5">Payload (Demand)</th>
                    <th className="py-2 px-2.5">Energy (kWh)</th>
                    <th className="py-2 px-2.5">CO₂ (kg)</th>
                    <th className="py-2 px-2.5">Total Cost</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-black/5 dark:divide-white/5 font-normal">
                  {activeProfile.vehicle_breakdowns.map((vb, idx) => {
                    const vp = vb.vehicle_profile;
                    const pType = vp?.powertrain || vb.propulsion_type || 'diesel';
                    const isEv = pType === 'electric';
                    const isRangeFeasible = vb.is_range_feasible ?? (vb.remaining_range_km === undefined || (vb.remaining_range_km !== undefined && vb.remaining_range_km >= 0));

                    return (
                      <tr key={idx} className="hover:bg-black/[0.02] dark:hover:bg-white/[0.02]">
                        <td className="py-2 px-2.5">
                          <div className="flex flex-col">
                            <span className="font-semibold text-[#080808] dark:text-white">
                              {vp?.name || `Vehicle ${vb.vehicle_id}`}
                            </span>
                            <div className="flex items-center gap-1 mt-0.5">
                              <span className="text-[9px] px-1 py-0.2 rounded bg-black/5 dark:bg-white/10 text-[#777777] dark:text-[#A1A1AA] capitalize font-normal">
                                {vp?.condition || 'Good'} condition
                              </span>
                              {!isRangeFeasible && (
                                <span className="text-[9px] px-1 py-0.2 rounded bg-red-500/15 text-red-500 font-semibold">
                                  Range Exceeded
                                </span>
                              )}
                            </div>
                          </div>
                        </td>
                        <td className="py-2 px-2.5">
                          <span className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[9px] font-semibold capitalize ${
                            isEv
                              ? 'bg-[#B7FF2A]/15 text-emerald-600 dark:text-[#B7FF2A]'
                              : pType === 'hybrid'
                              ? 'bg-teal-500/15 text-teal-600 dark:text-teal-400'
                              : 'bg-amber-500/15 text-amber-600 dark:text-amber-400'
                          }`}>
                            {isEv ? '⚡ Electric' : pType === 'hybrid' ? '🌿 Hybrid' : pType === 'petrol' ? '⛽ Petrol' : '🛢️ Diesel'}
                          </span>
                        </td>
                        <td className="py-2 px-2.5 text-[#555555] dark:text-[#A1A1AA]">
                          <div>{vb.distance_km} km</div>
                          {vb.remaining_range_km !== undefined && (
                            <div className="text-[9px] text-emerald-600 dark:text-emerald-400">
                              {vb.remaining_range_km} km left
                            </div>
                          )}
                        </td>
                        <td className="py-2 px-2.5 text-[#555555] dark:text-[#A1A1AA]">
                          {isEv && vb.remaining_soc_pct !== null && vb.remaining_soc_pct !== undefined ? (
                            <div className="flex items-center gap-1 font-semibold text-emerald-600 dark:text-emerald-400">
                              <BatteryCharging className="w-3 h-3" />
                              <span>{vb.remaining_soc_pct}% SoC</span>
                            </div>
                          ) : vb.remaining_fuel_pct !== null && vb.remaining_fuel_pct !== undefined ? (
                            <div className="flex items-center gap-1 font-semibold text-amber-500">
                              <Fuel className="w-3 h-3" />
                              <span>{vb.remaining_fuel_pct}% Fuel</span>
                            </div>
                          ) : (
                            <span>—</span>
                          )}
                        </td>
                        <td className="py-2 px-2.5 text-[#555555] dark:text-[#A1A1AA]">
                          {vb.load} / {vb.capacity} ({vb.utilization_pct}%)
                        </td>
                        <td className="py-2 px-2.5 font-semibold text-emerald-600 dark:text-emerald-400">
                          {vb.energy_consumption_kwh} kWh
                        </td>
                        <td className="py-2 px-2.5 text-[#555555] dark:text-[#A1A1AA]">
                          {vb.total_co2_kg} kg
                        </td>
                        <td className="py-2 px-2.5 font-semibold text-[#080808] dark:text-white">
                          {formatUsd(vb.operational_cost_usd)}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Comprehensive Algorithm Resource Comparison Table */}
      <div className="rounded-xl border border-black/5 dark:border-white/5 bg-black/[0.01] dark:bg-white/[0.01] overflow-hidden font-heading">
        <div className="p-3 border-b border-black/5 dark:border-white/5 flex items-center justify-between flex-wrap gap-2">
          <div className="flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-purple-400" />
            <h4 className="text-xs font-semibold text-[#080808] dark:text-white font-heading">
              Fleetwide Resource Comparison ({items.length} Evaluated Solvers)
            </h4>
          </div>
          <span className="text-[10px] text-[#777777] dark:text-[#8E8E93] font-normal">
            Propulsion: <strong className="text-[#080808] dark:text-white font-semibold">{activeModel.name}</strong> · Baseline: <strong className="text-[#080808] dark:text-white font-semibold">{profilesMap[effectiveBaselineId]?.algorithm_name || effectiveBaselineId}</strong>
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-[11px] tabular-nums font-heading">
            <thead>
              <tr className="border-b border-black/5 dark:border-white/5 text-[#777777] dark:text-[#8E8E93] text-[9px] uppercase tracking-wider font-semibold bg-black/[0.02] dark:bg-white/[0.02]">
                <th className="py-2.5 px-3">Algorithm</th>
                <th className="py-2.5 px-2.5">Feasibility</th>
                <th className="py-2.5 px-2.5 text-right">Distance</th>
                <th className="py-2.5 px-2.5 text-right">Energy</th>
                <th className="py-2.5 px-2.5 text-right">Fuel ({activeModel.unitLabel})</th>
                <th className="py-2.5 px-2.5 text-right">CO₂ (kg)</th>
                <th className="py-2.5 px-2.5 text-right">Cost ($)</th>
                <th className="py-2.5 px-3 text-right">Savings vs Baseline</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-black/5 dark:divide-white/5 font-normal">
              {items.map((it) => {
                const prof = profilesMap[it.id];
                if (!prof) return null;
                const comp = calculateEnergyComparison(prof, baselineProfile);
                const isCurrentActive = it.id === activeAlgo;
                const isFlagship = it.id === 'routeiq_cooperative';

                return (
                  <tr
                    key={it.id}
                    onClick={() => onSelectAlgorithm && onSelectAlgorithm(it.id)}
                    className={`cursor-pointer transition-colors ${
                      isCurrentActive
                        ? 'bg-[#B7FF2A]/10 dark:bg-[#B7FF2A]/15 font-semibold'
                        : 'hover:bg-black/[0.02] dark:hover:bg-white/[0.02]'
                    }`}
                  >
                    <td className="py-2.5 px-3">
                      <div className="flex items-center gap-1.5">
                        {isFlagship && (
                          <span className="w-1.5 h-1.5 rounded-full bg-purple-500 animate-pulse" />
                        )}
                        <span className="font-semibold text-[#080808] dark:text-white">
                          {prof.algorithm_name}
                        </span>
                        {it.id === effectiveBaselineId && (
                          <span className="text-[9px] px-1 py-0.2 rounded bg-black/10 dark:bg-white/10 text-[#777777] font-normal">
                            BASELINE
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="py-2.5 px-2.5">
                      {prof.is_feasible ? (
                        <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-medium">
                          Feasible
                        </span>
                      ) : (
                        <span className="text-[10px] text-amber-500 font-semibold">
                          Penalized
                        </span>
                      )}
                    </td>
                    <td className="py-2.5 px-2.5 text-right text-[#555555] dark:text-[#A1A1AA]">
                      {prof.total_distance_km} km
                    </td>
                    <td className="py-2.5 px-2.5 text-right font-semibold text-emerald-600 dark:text-emerald-400">
                      {prof.energy_consumption_kwh.toFixed(1)} kWh
                    </td>
                    <td className="py-2.5 px-2.5 text-right text-[#555555] dark:text-[#A1A1AA]">
                      {activeModel.fuelType === 'electricity'
                        ? `${prof.energy_consumption_kwh.toFixed(1)}`
                        : `${prof.fuel_consumption_litres.toFixed(2)}`}
                    </td>
                    <td className="py-2.5 px-2.5 text-right text-[#555555] dark:text-[#A1A1AA]">
                      {prof.total_co2_kg.toFixed(2)}
                    </td>
                    <td className="py-2.5 px-2.5 text-right font-medium text-[#080808] dark:text-white">
                      {formatUsd(prof.operational_cost_usd)}
                    </td>
                    <td className="py-2.5 px-3 text-right">
                      <span
                        className={`inline-block px-1.5 py-0.5 rounded text-[10px] font-semibold ${
                          comp.delta_energy_kwh > 0.01
                            ? 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400'
                            : comp.delta_energy_kwh < -0.01
                            ? 'bg-amber-500/15 text-amber-600 dark:text-amber-400'
                            : 'text-gray-500 dark:text-gray-400'
                        }`}
                      >
                        {comp.delta_energy_kwh > 0.01
                          ? `+${comp.pct_energy_savings}%`
                          : comp.delta_energy_kwh < -0.01
                          ? `${comp.pct_energy_savings}%`
                          : '0.0%'}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Methodology & Scientific Standards Drawer */}
      {showMethodology && (
        <div className="mt-4 p-4 rounded-xl bg-black/[0.03] dark:bg-white/[0.03] border border-black/10 dark:border-white/10 text-[11px] leading-relaxed space-y-2.5">
          <div className="flex items-center gap-1.5 text-xs font-bold text-[#080808] dark:text-white font-heading">
            <Info className="w-3.5 h-3.5 text-blue-400" />
            <span>Scientific Emissions & Energy Accounting Methodology</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
            <div>
              <h5 className="font-semibold text-[#080808] dark:text-white mb-0.5 text-[11px]">
                Vehicle Propulsion Constants & Factors:
              </h5>
              <ul className="list-disc pl-4 space-y-0.5 text-[#555555] dark:text-[#A1A1AA]">
                <li>
                  <strong>Diesel Van:</strong> 9.5 L/100 km, 10.0 kWh/L thermal density, 2.68 kg CO₂/L direct combustion (US EPA 2024 / DEFRA 2023), 0.58 kg CO₂/L upstream refining. $1.15/L ($4.35/gal).
                </li>
                <li>
                  <strong>Petrol Van:</strong> 11.0 L/100 km, 8.9 kWh/L, 2.31 kg CO₂/L direct, 0.52 kg CO₂/L upstream. $0.95/L ($3.60/gal).
                </li>
                <li>
                  <strong>Hybrid Van:</strong> 6.8 L/100 km with regenerative braking urban mitigation (traffic sensitivity 0.10).
                </li>
                <li>
                  <strong>Electric EV:</strong> 28.0 kWh/100 km (0.28 kWh/km), 0.0 kg direct tailpipe CO₂, 0.245 kg CO₂/kWh indirect generation emissions (EPA eGRID 2022/2024 NYUP/NYCW subregion). $0.18/kWh commercial power rate.
                </li>
              </ul>
            </div>

            <div>
              <h5 className="font-semibold text-[#080808] dark:text-white mb-0.5 text-[11px]">
                Dynamic Load & Traffic Corrections:
              </h5>
              <ul className="list-disc pl-4 space-y-0.5 text-[#555555] dark:text-[#A1A1AA]">
                <li>
                  <strong>Payload Adjustment:</strong> F_load = 1.0 + 0.15 × (Demand / Fleet_Capacity). Up to 15% energy penalty under full rated cargo load.
                </li>
                <li>
                  <strong>Traffic Slowdown:</strong> F_traffic = 1.0 + 0.20 × (Traffic_Factor - 1.0). Accounts for urban stop-and-go idling and braking losses.
                </li>
                <li>
                  <strong>Scientific Data Provenance:</strong> Distance = <code>COMPUTED</code> (verified road network graph paths); Duration, Fuel & Energy = <code>ESTIMATED</code> (physical models & traffic factors); QAOA = <code>SIMULATED</code> (classical CPU statevector emulation); Vehicle specs, Fuel prices & Grid carbon = <code>ASSUMED</code>.
                </li>
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
