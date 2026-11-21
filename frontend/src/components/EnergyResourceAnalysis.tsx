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
    <div className="mt-8 rounded-3xl bg-white dark:bg-[#101014] border border-black/10 dark:border-white/10 p-6 sm:p-8 shadow-sm">
      {/* Header & Badges */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-black/5 dark:border-white/5">
        <div>
          <div className="flex items-center gap-2.5 mb-1.5 flex-wrap">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-[#B7FF2A]/15 text-black dark:text-[#B7FF2A] border border-[#B7FF2A]/30">
              <Leaf className="w-3.5 h-3.5" /> Green Logistics & Fleet Decarbonization
            </span>
            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-mono font-medium bg-black/5 dark:bg-white/5 text-[#555555] dark:text-[#A1A1AA] border border-black/5 dark:border-white/5">
              <ShieldCheck className="w-3 h-3 text-[#B7FF2A]" /> EPA 2024 · DEFRA · eGRID NYC
            </span>
          </div>
          <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-[#080808] dark:text-white font-technical">
            Energy & Resource Savings Analysis
          </h2>
          <p className="text-xs sm:text-sm text-[#666666] dark:text-[#8E8E93] mt-1 max-w-2xl leading-relaxed">
            Quantifying fuel, thermal/electrical energy, well-to-wheel greenhouse emissions, and operational cost savings across vehicle propulsion technologies.
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2 self-start md:self-center">
          <button
            onClick={() => setShowMethodology(!showMethodology)}
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-medium border border-black/10 dark:border-white/10 bg-black/[0.02] dark:bg-white/[0.02] hover:bg-black/5 dark:hover:bg-white/5 text-[#555555] dark:text-[#A1A1AA] transition-colors"
          >
            <Info className="w-3.5 h-3.5 text-blue-400" />
            {showMethodology ? 'Hide Methodology' : 'Methodology & Factors'}
          </button>
        </div>
      </div>

      {/* Interactive Controls Bar: Propulsion Selector & Baseline Selector */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 py-5 border-b border-black/5 dark:border-white/5 items-center">
        {/* Propulsion Type Buttons */}
        <div className="lg:col-span-8">
          <span className="text-[11px] font-bold uppercase tracking-wider text-[#777777] dark:text-[#8E8E93] block mb-2 font-technical">
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
                  className={`flex flex-col text-left p-3 rounded-2xl border transition-all ${
                    isSelected
                      ? 'bg-black/5 dark:bg-white/10 border-[#B7FF2A] shadow-sm'
                      : 'border-black/5 dark:border-white/5 bg-transparent hover:bg-black/[0.02] dark:hover:bg-white/[0.03]'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="p-1 rounded-lg bg-black/5 dark:bg-white/5">
                      {getPropulsionIcon(pType)}
                    </span>
                    {isSelected && <Check className="w-3.5 h-3.5 text-[#B7FF2A]" />}
                  </div>
                  <span className="text-xs font-bold text-[#080808] dark:text-white truncate">
                    {model.name.replace(' Delivery Van', '')}
                  </span>
                  <span className="text-[10px] font-mono text-[#777777] dark:text-[#8E8E93] mt-0.5">
                    {model.baseConsumptionPer100km} {model.unitLabel}/100km
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Baseline Selector */}
        <div className="lg:col-span-4 bg-black/[0.02] dark:bg-white/[0.02] p-3.5 rounded-2xl border border-black/5 dark:border-white/5">
          <label className="text-[11px] font-bold uppercase tracking-wider text-[#777777] dark:text-[#8E8E93] block mb-1.5 font-technical">
            Comparison Baseline Solver
          </label>
          <div className="flex items-center gap-2">
            <select
              value={effectiveBaselineId}
              onChange={(e) => setCustomBaseline(e.target.value)}
              className="w-full bg-white dark:bg-[#18181C] border border-black/10 dark:border-white/10 rounded-xl px-3 py-2 text-xs font-medium text-[#080808] dark:text-white focus:outline-none focus:ring-1 focus:ring-[#B7FF2A]"
            >
              {items.map((it) => (
                <option key={it.id} value={it.id}>
                  {it.name} ({it.total_distance_km} km)
                </option>
              ))}
            </select>
          </div>
          <p className="text-[10px] text-[#777777] dark:text-[#8E8E93] mt-1.5 leading-tight">
            Selected route will be evaluated against this baseline.
          </p>
        </div>
      </div>

      {/* Hero Comparative Resource Savings Banner */}
      {comparison && (
        <div className="my-6">
          <div
            className={`p-5 rounded-2xl border flex flex-col md:flex-row items-start md:items-center justify-between gap-4 transition-all ${
              isSaving
                ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-950 dark:text-emerald-100'
                : isIdentical
                ? 'bg-blue-500/10 border-blue-500/30 text-blue-950 dark:text-blue-100'
                : 'bg-amber-500/10 border-amber-500/30 text-amber-950 dark:text-amber-100'
            }`}
          >
            <div className="flex items-center gap-3.5">
              <div
                className={`p-3 rounded-2xl ${
                  isSaving
                    ? 'bg-emerald-500/20 text-emerald-600 dark:text-emerald-400'
                    : isIdentical
                    ? 'bg-blue-500/20 text-blue-600 dark:text-blue-400'
                    : 'bg-amber-500/20 text-amber-600 dark:text-amber-400'
                }`}
              >
                {isSaving ? (
                  <TrendingDown className="w-6 h-6" />
                ) : isIdentical ? (
                  <Gauge className="w-6 h-6" />
                ) : (
                  <TrendingUp className="w-6 h-6" />
                )}
              </div>
              <div>
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-xs font-mono font-bold uppercase tracking-wider px-2 py-0.5 rounded-md bg-black/10 dark:bg-white/10">
                    {comparison.status_label.replace(/_/g, ' ')}
                  </span>
                  <span className="text-xs text-[#555555] dark:text-[#A1A1AA]">
                    vs. {profilesMap[effectiveBaselineId]?.algorithm_name || effectiveBaselineId}
                  </span>
                </div>
                <h3 className="text-base sm:text-lg font-bold mt-0.5 font-technical">
                  {comparison.impact_summary}
                </h3>
              </div>
            </div>

            {/* Savings Quick Metric Pills */}
            <div className="flex items-center gap-2 sm:gap-3 flex-wrap">
              <div className="px-3.5 py-2 rounded-xl bg-white/60 dark:bg-black/40 border border-black/5 dark:border-white/5 text-right">
                <span className="text-[10px] text-[#777777] dark:text-[#8E8E93] uppercase font-mono block">
                  Energy Delta
                </span>
                <span
                  className={`text-sm font-bold font-mono ${
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

              <div className="px-3.5 py-2 rounded-xl bg-white/60 dark:bg-black/40 border border-black/5 dark:border-white/5 text-right">
                <span className="text-[10px] text-[#777777] dark:text-[#8E8E93] uppercase font-mono block">
                  CO₂ Abatement
                </span>
                <span
                  className={`text-sm font-bold font-mono ${
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

              <div className="px-3.5 py-2 rounded-xl bg-white/60 dark:bg-black/40 border border-black/5 dark:border-white/5 text-right">
                <span className="text-[10px] text-[#777777] dark:text-[#8E8E93] uppercase font-mono block">
                  Fleet Cost Saved
                </span>
                <span
                  className={`text-sm font-bold font-mono ${
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
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {/* 1. Thermal & Electrical Energy */}
        <div className="p-5 rounded-2xl bg-black/[0.02] dark:bg-white/[0.02] border border-black/5 dark:border-white/5 relative overflow-hidden">
          <div className="flex items-center justify-between text-[#777777] dark:text-[#8E8E93] mb-2">
            <span className="text-[11px] font-bold uppercase tracking-wider font-technical">
              Total Energy Consumption
            </span>
            <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-black/5 dark:bg-white/10 text-amber-500 font-semibold">
              ESTIMATED
            </span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl sm:text-3xl font-extrabold font-mono text-[#080808] dark:text-white">
              {activeProfile.energy_consumption_kwh.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })}
            </span>
            <span className="text-xs font-semibold text-[#777777] dark:text-[#8E8E93]">kWh</span>
          </div>
          <div className="mt-2.5 flex items-center justify-between text-[11px] text-[#777777] dark:text-[#8E8E93] pt-2 border-t border-black/5 dark:border-white/5">
            <span>Thermal/Electrical Equivalent</span>
            <span className="font-mono font-medium">
              {(activeProfile.energy_consumption_kwh * 3.6).toFixed(1)} MJ
            </span>
          </div>
        </div>

        {/* 2. Fuel Consumption (or Battery Draw for EV) */}
        <div className="p-5 rounded-2xl bg-black/[0.02] dark:bg-white/[0.02] border border-black/5 dark:border-white/5 relative overflow-hidden">
          <div className="flex items-center justify-between text-[#777777] dark:text-[#8E8E93] mb-2">
            <span className="text-[11px] font-bold uppercase tracking-wider font-technical">
              {activeModel.fuelType === 'electricity' ? 'Direct Battery Draw' : 'Fuel Consumption'}
            </span>
            <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-black/5 dark:bg-white/10 text-amber-500 font-semibold">
              ESTIMATED
            </span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl sm:text-3xl font-extrabold font-mono text-[#080808] dark:text-white">
              {activeModel.fuelType === 'electricity'
                ? activeProfile.energy_consumption_kwh.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })
                : activeProfile.fuel_consumption_litres.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </span>
            <span className="text-xs font-semibold text-[#777777] dark:text-[#8E8E93]">
              {activeModel.unitLabel}
            </span>
          </div>
          <div className="mt-2.5 flex items-center justify-between text-[11px] text-[#777777] dark:text-[#8E8E93] pt-2 border-t border-black/5 dark:border-white/5">
            <span>Rate per 100 km</span>
            <span className="font-mono font-medium">
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
        <div className="p-5 rounded-2xl bg-black/[0.02] dark:bg-white/[0.02] border border-black/5 dark:border-white/5 relative overflow-hidden">
          <div className="flex items-center justify-between text-[#777777] dark:text-[#8E8E93] mb-2">
            <span className="text-[11px] font-bold uppercase tracking-wider font-technical">
              Well-to-Wheel CO₂e
            </span>
            <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-black/5 dark:bg-white/10 text-amber-500 font-semibold">
              ESTIMATED
            </span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl sm:text-3xl font-extrabold font-mono text-[#080808] dark:text-white">
              {activeProfile.total_co2_kg.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </span>
            <span className="text-xs font-semibold text-[#777777] dark:text-[#8E8E93]">kg CO₂</span>
          </div>
          <div className="mt-2.5 flex items-center justify-between text-[11px] text-[#777777] dark:text-[#8E8E93] pt-2 border-t border-black/5 dark:border-white/5">
            <span>
              {activeModel.fuelType === 'electricity' ? 'Indirect Grid Gen' : 'Tailpipe Combustion'}
            </span>
            <span className="font-mono font-medium">
              {activeModel.fuelType === 'electricity'
                ? `${activeProfile.indirect_grid_co2_kg.toFixed(2)} kg`
                : `${activeProfile.direct_tailpipe_co2_kg.toFixed(2)} kg`}
            </span>
          </div>
        </div>

        {/* 4. Fleet Operational Cost */}
        <div className="p-5 rounded-2xl bg-black/[0.02] dark:bg-white/[0.02] border border-black/5 dark:border-white/5 relative overflow-hidden">
          <div className="flex items-center justify-between text-[#777777] dark:text-[#8E8E93] mb-2">
            <span className="text-[11px] font-bold uppercase tracking-wider font-technical">
              Trip Energy Cost
            </span>
            <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-black/5 dark:bg-white/10 text-purple-400 font-semibold">
              ASSUMED
            </span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl sm:text-3xl font-extrabold font-mono text-[#080808] dark:text-white">
              {formatUsd(activeProfile.operational_cost_usd)}
            </span>
            <span className="text-xs font-semibold text-[#777777] dark:text-[#8E8E93]">USD</span>
          </div>
          <div className="mt-2.5 flex items-center justify-between text-[11px] text-[#777777] dark:text-[#8E8E93] pt-2 border-t border-black/5 dark:border-white/5">
            <span>Tariff Rate</span>
            <span className="font-mono font-medium">
              ${activeModel.unitCostUsd.toFixed(2)} / {activeModel.unitLabel}
            </span>
          </div>
        </div>
      </div>

      {/* Vehicle-wise Breakdown Accordion */}
      {activeProfile.vehicle_breakdowns && activeProfile.vehicle_breakdowns.length > 0 && (
        <div className="mb-6 rounded-2xl border border-black/5 dark:border-white/5 bg-black/[0.01] dark:bg-white/[0.01] overflow-hidden">
          <button
            onClick={() => setShowAllVehicles(!showAllVehicles)}
            className="w-full flex items-center justify-between p-4 text-left hover:bg-black/[0.02] dark:hover:bg-white/[0.02] transition-colors"
          >
            <div className="flex items-center gap-2.5">
              <Truck className="w-4 h-4 text-[#B7FF2A]" />
              <span className="text-xs sm:text-sm font-bold text-[#080808] dark:text-white font-technical">
                Vehicle-Specific Resource Schedules ({activeProfile.vehicle_breakdowns.length} Vehicles)
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-black/5 dark:bg-white/10 text-[#777777] dark:text-[#A1A1AA]">
                Payload & Congestion Corrected
              </span>
            </div>
            {showAllVehicles ? (
              <ChevronUp className="w-4 h-4 text-[#777777]" />
            ) : (
              <ChevronDown className="w-4 h-4 text-[#777777]" />
            )}
          </button>

          {showAllVehicles && (
            <div className="p-4 pt-0 overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead>
                  <tr className="border-b border-black/5 dark:border-white/5 text-[#777777] dark:text-[#8E8E93] text-[10px] uppercase font-technical">
                    <th className="py-2.5 px-3">Vehicle Profile</th>
                    <th className="py-2.5 px-3">Powertrain</th>
                    <th className="py-2.5 px-3">Distance & Range</th>
                    <th className="py-2.5 px-3">Remaining Energy / Fuel</th>
                    <th className="py-2.5 px-3">Payload (Demand)</th>
                    <th className="py-2.5 px-3">Energy (kWh)</th>
                    <th className="py-2.5 px-3">CO₂ (kg)</th>
                    <th className="py-2.5 px-3">Total Cost</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-black/5 dark:divide-white/5">
                  {activeProfile.vehicle_breakdowns.map((vb, idx) => {
                    const vp = vb.vehicle_profile;
                    const pType = vp?.powertrain || vb.propulsion_type || 'diesel';
                    const isEv = pType === 'electric';
                    const isRangeFeasible = vb.is_range_feasible ?? (vb.remaining_range_km === undefined || (vb.remaining_range_km !== undefined && vb.remaining_range_km >= 0));

                    return (
                      <tr key={idx} className="hover:bg-black/[0.02] dark:hover:bg-white/[0.02]">
                        <td className="py-2.5 px-3">
                          <div className="flex flex-col">
                            <span className="font-bold text-[#080808] dark:text-white">
                              {vp?.name || `Vehicle ${vb.vehicle_id}`}
                            </span>
                            <div className="flex items-center gap-1.5 mt-0.5">
                              <span className="text-[9px] font-technical px-1.5 py-0.2 rounded bg-black/5 dark:bg-white/10 text-[#777777] dark:text-[#A1A1AA] capitalize">
                                {vp?.condition || 'Good'} condition
                              </span>
                              {!isRangeFeasible && (
                                <span className="text-[9px] font-technical px-1.5 py-0.2 rounded bg-red-500/15 text-red-500 font-bold">
                                  Range Exceeded
                                </span>
                              )}
                            </div>
                          </div>
                        </td>
                        <td className="py-2.5 px-3">
                          <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-technical font-semibold capitalize ${
                            isEv
                              ? 'bg-[#B7FF2A]/15 text-emerald-600 dark:text-[#B7FF2A]'
                              : pType === 'hybrid'
                              ? 'bg-teal-500/15 text-teal-600 dark:text-teal-400'
                              : 'bg-amber-500/15 text-amber-600 dark:text-amber-400'
                          }`}>
                            {isEv ? '⚡ Electric' : pType === 'hybrid' ? '🌿 Hybrid' : pType === 'petrol' ? '⛽ Petrol' : '🛢️ Diesel'}
                          </span>
                        </td>
                        <td className="py-2.5 px-3 text-[#555555] dark:text-[#A1A1AA]">
                          <div>{vb.distance_km} km</div>
                          {vb.remaining_range_km !== undefined && (
                            <div className="text-[10px] text-emerald-600 dark:text-emerald-400">
                              {vb.remaining_range_km} km left
                            </div>
                          )}
                        </td>
                        <td className="py-2.5 px-3 text-[#555555] dark:text-[#A1A1AA]">
                          {isEv && vb.remaining_soc_pct !== null && vb.remaining_soc_pct !== undefined ? (
                            <div className="flex items-center gap-1.5 font-bold text-emerald-600 dark:text-emerald-400">
                              <BatteryCharging className="w-3.5 h-3.5" />
                              <span>{vb.remaining_soc_pct}% SoC</span>
                            </div>
                          ) : vb.remaining_fuel_pct !== null && vb.remaining_fuel_pct !== undefined ? (
                            <div className="flex items-center gap-1.5 font-bold text-amber-500">
                              <Fuel className="w-3.5 h-3.5" />
                              <span>{vb.remaining_fuel_pct}% Fuel</span>
                            </div>
                          ) : (
                            <span>—</span>
                          )}
                        </td>
                        <td className="py-2.5 px-3 text-[#555555] dark:text-[#A1A1AA]">
                          {vb.load} / {vb.capacity} ({vb.utilization_pct}%)
                        </td>
                        <td className="py-2.5 px-3 font-semibold text-emerald-600 dark:text-emerald-400">
                          {vb.energy_consumption_kwh} kWh
                        </td>
                        <td className="py-2.5 px-3 text-[#555555] dark:text-[#A1A1AA]">
                          {vb.total_co2_kg} kg
                        </td>
                        <td className="py-2.5 px-3 font-semibold text-[#080808] dark:text-white">
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
      <div className="rounded-2xl border border-black/5 dark:border-white/5 bg-black/[0.01] dark:bg-white/[0.01] overflow-hidden">
        <div className="p-4 border-b border-black/5 dark:border-white/5 flex items-center justify-between flex-wrap gap-2">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-purple-400" />
            <h4 className="text-xs sm:text-sm font-bold text-[#080808] dark:text-white font-technical">
              Fleetwide Resource Comparison ({items.length} Evaluated Solvers)
            </h4>
          </div>
          <span className="text-[10px] text-[#777777] dark:text-[#8E8E93]">
            Propulsion: <strong className="text-[#080808] dark:text-white">{activeModel.name}</strong> · Baseline: <strong className="text-[#080808] dark:text-white">{profilesMap[effectiveBaselineId]?.algorithm_name || effectiveBaselineId}</strong>
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-black/5 dark:border-white/5 text-[#777777] dark:text-[#8E8E93] text-[10px] uppercase font-technical bg-black/[0.02] dark:bg-white/[0.02]">
                <th className="py-3 px-4">Algorithm</th>
                <th className="py-3 px-3">Feasibility</th>
                <th className="py-3 px-3 text-right">Distance</th>
                <th className="py-3 px-3 text-right">Energy</th>
                <th className="py-3 px-3 text-right">Fuel ({activeModel.unitLabel})</th>
                <th className="py-3 px-3 text-right">CO₂ (kg)</th>
                <th className="py-3 px-3 text-right">Cost ($)</th>
                <th className="py-3 px-4 text-right">Savings vs Baseline</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-black/5 dark:divide-white/5">
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
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        {isFlagship && (
                          <span className="w-2 h-2 rounded-full bg-purple-500 animate-pulse" />
                        )}
                        <span className="font-bold text-[#080808] dark:text-white">
                          {prof.algorithm_name}
                        </span>
                        {it.id === effectiveBaselineId && (
                          <span className="text-[9px] px-1.5 py-0.2 rounded bg-black/10 dark:bg-white/10 text-[#777777] font-mono">
                            BASELINE
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="py-3 px-3">
                      {prof.is_feasible ? (
                        <span className="text-[10px] text-emerald-600 dark:text-emerald-400">
                          Feasible
                        </span>
                      ) : (
                        <span className="text-[10px] text-amber-500 font-semibold">
                          Penalized
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-3 text-right text-[#555555] dark:text-[#A1A1AA]">
                      {prof.total_distance_km} km
                    </td>
                    <td className="py-3 px-3 text-right font-semibold text-emerald-600 dark:text-emerald-400">
                      {prof.energy_consumption_kwh.toFixed(1)} kWh
                    </td>
                    <td className="py-3 px-3 text-right text-[#555555] dark:text-[#A1A1AA]">
                      {activeModel.fuelType === 'electricity'
                        ? `${prof.energy_consumption_kwh.toFixed(1)}`
                        : `${prof.fuel_consumption_litres.toFixed(2)}`}
                    </td>
                    <td className="py-3 px-3 text-right text-[#555555] dark:text-[#A1A1AA]">
                      {prof.total_co2_kg.toFixed(2)}
                    </td>
                    <td className="py-3 px-3 text-right font-medium text-[#080808] dark:text-white">
                      {formatUsd(prof.operational_cost_usd)}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <span
                        className={`inline-block px-2 py-0.5 rounded text-[11px] font-bold ${
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
        <div className="mt-6 p-5 rounded-2xl bg-black/[0.03] dark:bg-white/[0.03] border border-black/10 dark:border-white/10 text-xs leading-relaxed space-y-3">
          <div className="flex items-center gap-2 text-sm font-bold text-[#080808] dark:text-white font-technical">
            <Info className="w-4 h-4 text-blue-400" />
            <span>Scientific Emissions & Energy Accounting Methodology</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
            <div>
              <h5 className="font-bold text-[#080808] dark:text-white mb-1">
                Vehicle Propulsion Constants & Factors:
              </h5>
              <ul className="list-disc pl-4 space-y-1 text-[#555555] dark:text-[#A1A1AA]">
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
              <h5 className="font-bold text-[#080808] dark:text-white mb-1">
                Dynamic Load & Traffic Corrections:
              </h5>
              <ul className="list-disc pl-4 space-y-1 text-[#555555] dark:text-[#A1A1AA]">
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
