import React, { useState, useEffect } from 'react';
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Polyline,
  useMap,
} from 'react-leaflet';
import L from 'leaflet';
import {
  Download,
  ArrowRight,
  Route,
  CheckCircle2,
  GitCompare,
  BarChart3,
  Layers,
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
} from 'recharts';
import { OptimizationResponse, VehicleRoute } from '../types';
import { useSettings } from '../context/SettingsContext';
import { useTheme } from '../context/ThemeContext';

const getDepotIcon = (isDark: boolean) =>
  L.divIcon({
    className: 'custom-map-pin-depot',
    html: `<div style="background-color: #B7FF2A; border: 2.5px solid ${
      isDark ? '#000000' : '#080808'
    }; color: #080808; width: 34px; height: 34px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 15px; font-weight: 900; font-family: 'JetBrains Mono', monospace; box-shadow: ${
      isDark
        ? '0 0 24px rgba(183, 255, 42, 0.7), 0 4px 14px rgba(0,0,0,0.8)'
        : '0 4px 16px rgba(0,0,0,0.35)'
    };">D</div>`,
    iconSize: [34, 34],
    iconAnchor: [17, 17],
    popupAnchor: [0, -18],
  });

const LIGHT_ROUTE_COLORS = ['#080808', '#0284C7', '#7C3AED', '#EA580C', '#059669', '#DB2777'];
const DARK_ROUTE_COLORS = ['#B7FF2A', '#00E5FF', '#FF6B00', '#E040FB', '#38BDF8', '#FACC15'];

interface ResultsViewProps {
  result: OptimizationResponse | null;
  onNavigateToPlan: () => void;
  isActive?: boolean;
}

function MapResizer({ isActive }: { isActive?: boolean }) {
  const map = useMap();
  useEffect(() => {
    if (isActive !== false) {
      const timer = setTimeout(() => {
        map.invalidateSize();
      }, 60);
      return () => clearTimeout(timer);
    }
  }, [isActive, map]);
  return null;
}

export const ResultsView: React.FC<ResultsViewProps> = ({
  result,
  onNavigateToPlan,
  isActive,
}) => {
  const { settings } = useSettings();
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  const activeRouteColors = isDark ? DARK_ROUTE_COLORS : LIGHT_ROUTE_COLORS;

  const createCustomerIcon = (index: number, isDark: boolean) => {
  return L.divIcon({
    className: 'custom-customer-pin',
    html: `<div style="background-color: ${
      isDark ? '#141418' : '#080808'
    }; border: 2px solid ${
      isDark ? '#B7FF2A' : '#FFFFFF'
    }; color: ${
      isDark ? '#B7FF2A' : '#FFFFFF'
    }; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 800; font-family: 'JetBrains Mono', monospace; box-shadow: ${
      isDark ? '0 0 12px rgba(183,255,42,0.3), 0 4px 12px rgba(0,0,0,0.6)' : '0 4px 14px rgba(0,0,0,0.3)'
    };">${index}</div>`,
    iconSize: [28, 28],
    iconAnchor: [14, 14],
    popupAnchor: [0, -16],
  });
};

const createVehicleIcon = (vehicleId: number, color: string, isDark: boolean) => {
  const isLime = color.toUpperCase() === '#B7FF2A';
  return L.divIcon({
    className: 'custom-vehicle-pin',
    html: `<div style="background-color: ${color}; border: 2px solid ${
      isDark ? '#000000' : '#FFFFFF'
    }; color: ${
      isLime ? '#080808' : '#FFFFFF'
    }; min-width: 32px; height: 24px; padding: 0 6px; border-radius: 9999px; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 900; font-family: 'JetBrains Mono', monospace; box-shadow: 0 4px 14px rgba(0,0,0,0.4); text-transform: uppercase;">V${vehicleId}</div>`,
    iconSize: [36, 24],
    iconAnchor: [18, 12],
    popupAnchor: [0, -14],
  });
};

  // Extract all executed algorithms from result.results (filter out duplicate aliases)
  const resultsMap = result?.results || {};
  const algoKeys = Object.keys(resultsMap).filter(
    (k) => !(k === 'classical' && resultsMap.ortools)
  );

  const initialAlgo =
    result?.best_feasible_algorithm && resultsMap[result.best_feasible_algorithm]
      ? result.best_feasible_algorithm
      : result?.primary_algorithm && resultsMap[result.primary_algorithm]
      ? result.primary_algorithm
      : algoKeys.includes('ortools')
      ? 'ortools'
      : algoKeys[0] || 'classical';

  const [activeAlgo, setActiveAlgo] = useState<string>(initialAlgo);

  // Sync if result changes
  useEffect(() => {
    if (result) {
      const best =
        result.best_feasible_algorithm && resultsMap[result.best_feasible_algorithm]
          ? result.best_feasible_algorithm
          : result.primary_algorithm && resultsMap[result.primary_algorithm]
          ? result.primary_algorithm
          : algoKeys.includes('ortools')
          ? 'ortools'
          : algoKeys[0] || 'classical';
      setActiveAlgo(best);
    }
  }, [result]);

  if (!result || algoKeys.length === 0) {
    return (
      <div className="py-20 text-center space-y-4">
        <h2 className="text-2xl font-bold text-[#080808] dark:text-[#F5F5F7]">No Route Results Yet</h2>
        <p className="text-xs text-[#777777] dark:text-[#A1A1AA] max-w-sm mx-auto">
          Execute an optimization solver run in the Plan workspace to inspect routes, driver schedules, and benchmarks.
        </p>
        <button
          onClick={onNavigateToPlan}
          className="px-6 py-2.5 bg-[#080808] hover:bg-[#171717] dark:bg-[#B7FF00] dark:hover:bg-[#a5e600] text-[#B7FF00] dark:text-black rounded-full text-xs font-bold transition-all cursor-pointer shadow-sm"
        >
          Open Plan Workspace
        </button>
      </div>
    );
  }

  const currentResult = resultsMap[activeAlgo] || resultsMap.classical || Object.values(resultsMap)[0];
  const comparisonItems = result.comparison_summary?.items || [];
  const bestAlgoId = result.best_feasible_algorithm || result.comparison_summary?.best_algorithm;
  const bestAlgoItem = comparisonItems.find((it) => it.id === bestAlgoId);

  // Handle Export CSV
  const handleExportCSV = () => {
    const routes = currentResult?.routes || [];
    let csv = 'Vehicle,Stop_Sequence,Stop_Index,Latitude,Longitude,Type\n';
    routes.forEach((route, vIdx) => {
      route.waypoints?.forEach((wp, sIdx) => {
        csv += `Vehicle_${vIdx + 1},${sIdx + 1},${wp.index},${wp.lat},${wp.lon},${wp.type}\n`;
      });
    });

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ROUTEIQ_${activeAlgo}_Routes_${Date.now()}.csv`;
    a.click();
  };

  // Handle Export JSON
  const handleExportJSON = () => {
    const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ROUTEIQ_Experiment_${result.experiment_id}.json`;
    a.click();
  };

  // Chart data across executed algorithms
  const chartData = (comparisonItems.length > 0 ? comparisonItems : algoKeys.map((k) => ({
    id: k,
    name: resultsMap[k]?.algorithm_name || k.toUpperCase(),
    total_distance_km: resultsMap[k]?.total_distance_km || 0,
    total_travel_time_min: resultsMap[k]?.total_travel_time_min || 0,
    execution_time_sec: resultsMap[k]?.execution_time_sec || 0,
    is_feasible: resultsMap[k]?.is_feasible || false,
  }))).map((it) => ({
    name: it.name.replace(' (CVRP)', '').replace(' (QIGA/IQGA)', ''),
    'Distance (km)': Number(it.total_distance_km.toFixed(1)),
    'Time (min)': Math.round(it.total_travel_time_min),
    'Runtime (s)': Number(it.execution_time_sec.toFixed(2)),
  }));

  const depotPos: [number, number] = [
    result.problem?.depot?.lat || 40.7580,
    result.problem?.depot?.lon || -73.8292,
  ];

  return (
    <div className="space-y-8 pb-16">
      {/* Editorial Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-4 border-b border-black/10 dark:border-[#29292E]">
        <div>
          <div className="inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-[#777777] dark:text-[#A1A1AA] mb-1">
            <span className="h-1.5 w-1.5 rounded-full bg-[#B7FF00]" />
            <span>Optimization & Benchmark Results</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-heading font-semibold text-[#080808] dark:text-[#F5F5F7]">
            Results
          </h1>
          <p className="text-xs text-[#777777] dark:text-[#71717A] mt-1 font-technical">
            Experiment ID: {result.experiment_id} · Total Execution: {result.execution_time_sec.toFixed(2)}s · Solvers Executed: {algoKeys.length}
          </p>
        </div>

        <div className="flex items-center gap-2 sm:gap-3 flex-wrap">
          <button
            onClick={onNavigateToPlan}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl border border-black/10 dark:border-[#29292E] bg-white dark:bg-[#18181B] hover:bg-black/5 dark:hover:bg-[#202024] text-xs font-semibold text-[#080808] dark:text-[#F5F5F7] transition-all cursor-pointer"
            title="Return to interactive Plan map workspace"
          >
            <Route className="h-3.5 w-3.5" />
            <span>Plan Workspace</span>
          </button>
          {/* Export Actions */}
          <button
            onClick={handleExportCSV}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl border border-black/10 dark:border-[#29292E] bg-white dark:bg-[#18181B] hover:bg-black/5 dark:hover:bg-[#202024] text-xs font-semibold text-[#080808] dark:text-[#F5F5F7] transition-all cursor-pointer"
            title="Download CSV turn-by-turn route coordinates"
          >
            <Download className="h-3.5 w-3.5" />
            <span>Export CSV</span>
          </button>
          <button
            onClick={handleExportJSON}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-[#080808] hover:bg-[#171717] dark:bg-[#B7FF00] dark:hover:bg-[#a5e600] text-[#B7FF00] dark:text-black text-xs font-bold transition-all cursor-pointer shadow-xs"
            title="Export full benchmark JSON payload"
          >
            <Download className="h-3.5 w-3.5" />
            <span>Export JSON</span>
          </button>
        </div>
      </div>

      {/* ─── BEST FEASIBLE SOLUTION CALLOUT (Requirement 4) ──────────── */}
      {bestAlgoItem && (
        <div className="p-4 rounded-2xl bg-white dark:bg-[#111113] border border-[#22C55E]/40 dark:border-[#22C55E]/30 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-3 animate-fadeIn">
          <div className="flex items-start sm:items-center gap-3">
            <div className="h-9 w-9 rounded-full bg-[#22C55E]/20 text-[#22C55E] flex items-center justify-center shrink-0">
              <CheckCircle2 className="h-5 w-5 text-[#22C55E]" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-sm text-[#080808] dark:text-[#F5F5F7]">
                  Best Feasible Solution: {bestAlgoItem.name}
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#B7FF00] text-black font-bold">
                  Recommended Feasible Pick
                </span>
              </div>
              <p className="text-xs text-[#555555] dark:text-[#A1A1AA] mt-0.5">
                {result.comparison_summary?.best_reason || 'Verified 100% capacity and delivery coverage with minimal distance.'} (Distance: <strong>{bestAlgoItem.total_distance_km.toFixed(2)} km</strong>, Est. Duration: <strong>{Math.round(bestAlgoItem.total_travel_time_min)} min</strong>, Violations: <strong>0</strong>)
              </p>
            </div>
          </div>

          {activeAlgo !== bestAlgoItem.id && (
            <button
              onClick={() => setActiveAlgo(bestAlgoItem.id)}
              className="px-4 py-1.5 rounded-xl bg-[#080808] text-[#B7FF00] dark:bg-[#18181B] dark:hover:bg-[#202024] dark:border dark:border-[#29292E] text-xs font-bold hover:bg-[#171717] transition-all cursor-pointer shrink-0"
            >
              Inspect Route
            </button>
          )}
        </div>
      )}

      {/* ─── ALGORITHM SELECTION PILLS ─────────────────────────────────── */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold uppercase tracking-wider text-[#777777] dark:text-[#A1A1AA]">
            Active Solver Route View
          </span>
          <span className="text-[11px] text-[#777777] dark:text-[#71717A]">
            Click any algorithm to inspect its route map and driver schedules
          </span>
        </div>

        <div className="flex flex-wrap items-center gap-2 p-1.5 rounded-2xl bg-black/5 dark:bg-[#111113] border border-black/5 dark:border-[#29292E] text-xs">
          {algoKeys.map((key) => {
            const data = resultsMap[key];
            const isSelected = activeAlgo === key;
            const isBest = key === bestAlgoId;
            const algoName = data?.algorithm_name || key.toUpperCase();

            return (
              <button
                key={key}
                onClick={() => setActiveAlgo(key)}
                className={`px-3.5 py-2 rounded-xl font-bold transition-all cursor-pointer flex items-center gap-2 ${
                  isSelected
                    ? 'bg-[#080808] text-[#B7FF00] dark:bg-[#202024] dark:text-[#B7FF00] border border-black dark:border-[#B7FF00]/40 shadow-xs'
                    : 'bg-white text-[#171717] hover:bg-black/5 dark:bg-[#18181B] dark:text-[#A1A1AA] dark:hover:text-[#F5F5F7] dark:hover:bg-[#202024] border border-black/5 dark:border-[#29292E]'
                }`}
              >
                <span>{algoName}</span>
                <span className="font-technical text-[10px] opacity-80">
                  {data?.total_distance_km ? `${data.total_distance_km.toFixed(1)} km` : ''}
                </span>
                {isBest && (
                  <span
                    className="h-2 w-2 rounded-full bg-[#B7FF00]"
                    title="Best Feasible Solution"
                  />
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* ─── ACTIVE METRICS FOR SELECTED ALGORITHM ─────────────────────── */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 py-3 border-y border-black/10 dark:border-[#29292E]">
        <div>
          <span className="text-[11px] font-bold uppercase tracking-wider text-[#777777] dark:text-[#71717A] block">
            Selected Algorithm
          </span>
          <div className="text-base sm:text-lg font-bold text-[#080808] dark:text-[#F5F5F7] mt-0.5 truncate" title={currentResult?.algorithm_name}>
            {currentResult?.algorithm_name || activeAlgo.toUpperCase()}
          </div>
          <span className="text-[10px] text-[#777777] dark:text-[#A1A1AA] font-technical uppercase">
            {currentResult?.compute_type || currentResult?.category || 'Classical CPU'}
          </span>
        </div>

        <div className="border-l border-black/10 dark:border-[#29292E] pl-4 sm:pl-6">
          <span className="text-[11px] font-bold uppercase tracking-wider text-[#777777] dark:text-[#71717A] block">
            Total Distance
          </span>
          <div className="text-lg sm:text-xl font-bold text-[#080808] dark:text-[#F5F5F7] font-technical mt-0.5">
            {currentResult?.total_distance_km.toFixed(1)} km
          </div>
        </div>

        <div className="border-l border-black/10 dark:border-[#29292E] pl-4 sm:pl-6">
          <span className="text-[11px] font-bold uppercase tracking-wider text-[#777777] dark:text-[#71717A] block">
            Estimated Duration
          </span>
          <div className="text-lg sm:text-xl font-bold text-[#080808] dark:text-[#F5F5F7] font-technical mt-0.5">
            {Math.round(currentResult?.total_travel_time_min || 0)} min
          </div>
        </div>

        <div className="border-l border-black/10 dark:border-[#29292E] pl-4 sm:pl-6">
          <span className="text-[11px] font-bold uppercase tracking-wider text-[#777777] dark:text-[#71717A] block">
            Vehicles Assigned
          </span>
          <div className="text-lg sm:text-xl font-bold text-[#080808] dark:text-[#F5F5F7] font-technical mt-0.5">
            {currentResult?.routes.length || settings.defaultVehicles} Drivers
          </div>
          <span className="text-[10px] text-[#777777] dark:text-[#A1A1AA] font-technical">
            {result.problem?.num_vehicles
              ? `${currentResult?.routes.length || 0} of ${result.problem.num_vehicles} fleet active${
                  (result.problem.num_vehicles - (currentResult?.routes.length || 0)) > 0
                    ? ` (${result.problem.num_vehicles - (currentResult?.routes.length || 0)} surplus)`
                    : ''
                }`
              : 'Active fleet routes'}
          </span>
        </div>

        <div className="border-l border-black/10 dark:border-[#29292E] pl-4 sm:pl-6">
          <span className="text-[11px] font-bold uppercase tracking-wider text-[#777777] dark:text-[#71717A] block">
            Feasibility Status
          </span>
          <div className="text-lg sm:text-xl font-bold text-[#080808] dark:text-[#F5F5F7] font-technical mt-0.5 flex items-center gap-1.5">
            <span>{currentResult?.is_feasible ? 'Feasible' : 'Penalized'}</span>
            <CheckCircle2 className={`h-4 w-4 inline ${currentResult?.is_feasible ? 'text-[#22C55E]' : 'text-amber-500'}`} />
          </div>
          <span className="text-[10px] text-[#777777] dark:text-[#A1A1AA] font-technical">
            Runtime: {currentResult?.execution_time_sec?.toFixed(3)}s
          </span>
        </div>
      </div>

      {/* ─── MAIN RESULTS LAYOUT: MAP & DRIVER SEQUENCES ──────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Route Map (7 cols) */}
        <div className="lg:col-span-7 h-[580px] rounded-3xl overflow-hidden relative shadow-sm border border-black/10 dark:border-[#29292E] bg-[#F4F4F2] dark:bg-[#111113]">
          <MapContainer
            center={depotPos}
            zoom={12}
            scrollWheelZoom={true}
            className="h-full w-full"
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <MapResizer isActive={isActive} />

            {/* Origin Depot Pin (Lime-Green 'D' marker with zIndexOffset to remain prominent) */}
            <Marker position={depotPos} icon={getDepotIcon(isDark)} zIndexOffset={1000}>
              <Popup>
                <div className="text-xs font-sans space-y-1">
                  <div className="flex items-center gap-1.5">
                    <span className="h-2 w-2 rounded-full bg-[#B7FF2A] ring-1 ring-black" />
                    <strong className="text-[#080808] dark:text-white font-bold">Origin Depot Hub (D)</strong>
                  </div>
                  <p className="font-technical text-[10px] text-[#777777] dark:text-[#A1A1AA]">
                    {depotPos[0].toFixed(6)}, {depotPos[1].toFixed(6)}
                  </p>
                  <span className="inline-block text-[10px] px-2 py-0.5 rounded-full bg-black text-[#B7FF2A] font-bold">
                    Route Dispatch Facility
                  </span>
                </div>
              </Popup>
            </Marker>

            {/* Customer Delivery Pins (Numbered 1, 2, 3... 18) - Skip index 0 which is the Origin Depot */}
            {result.problem?.locations?.slice(1).map((loc, idx) => (
              <Marker key={idx + 1} position={[loc.lat, loc.lon]} icon={createCustomerIcon(idx + 1, isDark)}>
                <Popup>
                  <div className="text-xs font-sans">
                    <strong className="text-[#080808] dark:text-[#F5F5F7]">Customer Delivery Stop #{idx + 1}</strong>
                    <br />
                    <span className="text-[#555555] dark:text-[#A1A1AA]">Demand: {loc.demand} units</span>
                  </div>
                </Popup>
              </Marker>
            ))}

            {/* Vehicle Routes Polylines & Driver Badges (V1, V2...) */}
            {currentResult?.routes.map((route, rIdx) => {
              const color = activeRouteColors[rIdx % activeRouteColors.length];
              const driverNumber = rIdx + 1;
              const positions =
                route.waypoints?.map((w) => [w.lat, w.lon] as [number, number]) || [];
              const midPoint = positions.length > 2 ? positions[Math.floor(positions.length / 2)] : positions[0];

              return (
                <React.Fragment key={`map-route-${driverNumber}-${rIdx}`}>
                  {positions.length > 1 && (
                    <Polyline
                      positions={positions}
                      color={color}
                      weight={4.5}
                      opacity={0.95}
                      dashArray={rIdx % 2 === 1 ? '5, 5' : undefined}
                    />
                  )}
                  {midPoint && (
                    <Marker position={midPoint} icon={createVehicleIcon(driverNumber, color, isDark)}>
                      <Popup>
                        <div className="text-xs font-sans">
                          <strong className="text-[#080808] dark:text-[#F5F5F7]">Fleet Vehicle Driver V{driverNumber}</strong>
                          <br />
                          <span className="text-[#555555] dark:text-[#A1A1AA]">Distance: {route.distance_km.toFixed(1)} km</span>
                          <br />
                          <span className="text-[#555555] dark:text-[#A1A1AA]">Load: {Math.round(route.load || 0)} units</span>
                        </div>
                      </Popup>
                    </Marker>
                  )}
                </React.Fragment>
              );
            })}
          </MapContainer>

          {/* Floating Map Legend Overlay */}
          <div className="absolute bottom-4 left-4 glass-overlay bg-white/80 dark:!bg-[#18181B]/95 border border-black/10 dark:!border-[#29292E] text-[#080808] dark:!text-[#F5F5F7] px-4 py-2.5 rounded-2xl text-[11px] z-[1000] flex items-center gap-3 shadow-lg backdrop-blur-xl">
            <span className="font-bold text-[#080808] dark:text-[#F5F5F7]">Legend:</span>
            <span className="flex items-center gap-1.5 font-medium text-[#171717] dark:text-[#F5F5F7]">
              <span className="h-3 w-3 rounded-full bg-[#B7FF00] border border-black flex items-center justify-center text-[7px] font-bold text-black">
                D
              </span>
              <span>Origin Hub</span>
            </span>
            <span className="flex items-center gap-1.5 font-medium text-[#171717] dark:text-[#F5F5F7]">
              <span className="h-3 w-3 rounded-full bg-[#080808] dark:bg-[#141418] border border-white dark:border-[#B7FF00] flex items-center justify-center text-[7px] font-bold text-white dark:text-[#B7FF00]">
                #
              </span>
              <span>Customer Stops (1, 2, 3...)</span>
            </span>
            <span className="flex items-center gap-1.5 font-medium text-[#171717] dark:text-[#F5F5F7]">
              <span className="px-1.5 py-0.5 rounded-full bg-[#080808] text-[#B7FF00] border border-[#B7FF00] text-[9px] font-technical font-bold">
                V1..Vn
              </span>
              <span>Fleet Vehicles</span>
            </span>
          </div>
        </div>

        {/* Right Route Sequence & Comparative Benchmark (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* Driver Schedule Sequences */}
          <div className="space-y-3 pb-5 border-b border-black/10 dark:border-[#29292E]">
            <span className="text-xs font-bold uppercase tracking-wider text-[#080808] dark:text-[#F5F5F7] block">
              Driver Vehicle Schedules ({currentResult?.algorithm_name || activeAlgo})
            </span>

            <div className="space-y-2 max-h-[260px] overflow-y-auto pr-1">
              {currentResult?.routes.map((route: VehicleRoute, idx: number) => {
                const color = activeRouteColors[idx % activeRouteColors.length];
                const driverNumber = idx + 1;
                return (
                  <div
                    key={`schedule-driver-${driverNumber}-${idx}`}
                    className="py-2.5 px-3 rounded-xl bg-white/70 dark:bg-[#18181B] backdrop-blur-md border border-black/5 dark:border-[#29292E] space-y-1.5 transition-colors"
                  >
                    <div className="flex items-center justify-between text-xs">
                      <div className="flex items-center gap-2">
                        <div
                          className="h-3 w-3 rounded-full shrink-0"
                          style={{ backgroundColor: color }}
                        />
                        <span className="font-bold text-[#080808] dark:text-[#F5F5F7]">Driver #{driverNumber}</span>
                        <span className="text-[11px] text-[#777777] dark:text-[#A1A1AA]">
                          ({Math.max(0, route.stops.length - 2)} stops)
                        </span>
                      </div>
                      <span className="font-technical font-bold text-[#080808] dark:text-[#B7FF00]">
                        {route.distance_km.toFixed(1)} km
                      </span>
                    </div>

                    <div className="text-[11px] text-[#777777] dark:text-[#A1A1AA] font-technical">
                      Stop sequence: {route.stops.map((s) => (s === 0 ? 'D' : `#${s}`)).join(' → ')}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Comparative Metrics Chart */}
          {chartData.length > 1 && (
            <div className="space-y-3">
              <span className="text-xs font-bold uppercase tracking-wider text-[#080808] dark:text-[#F5F5F7] block">
                Comparative Route Distance (km)
              </span>

              <div className="h-56 w-full pt-2">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData}>
                    <XAxis
                      dataKey="name"
                      tick={{ fontSize: 10, fill: isDark ? '#A1A1AA' : '#171717' }}
                      stroke={isDark ? '#29292E' : 'rgba(0,0,0,0.1)'}
                    />
                    <YAxis
                      tick={{ fontSize: 10, fill: isDark ? '#A1A1AA' : '#171717' }}
                      stroke={isDark ? '#29292E' : 'rgba(0,0,0,0.1)'}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: isDark ? '#18181B' : '#FFFFFF',
                        borderColor: isDark ? '#29292E' : 'rgba(0,0,0,0.1)',
                        color: isDark ? '#F5F5F7' : '#080808',
                        borderRadius: '12px',
                        boxShadow: '0 8px 24px rgba(0,0,0,0.5)',
                      }}
                      itemStyle={{ color: isDark ? '#B7FF00' : '#080808', fontWeight: 600 }}
                    />
                    <Bar
                      dataKey="Distance (km)"
                      fill={isDark ? '#B7FF00' : '#080808'}
                      radius={[4, 4, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* ─── ALGORITHM COMPARISON SCORECARD TABLE (Requirement 4) ──────── */}
      {comparisonItems.length > 0 && (
        <div className="space-y-4 pt-6 border-t border-black/10 dark:border-[#29292E]">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <h2 className="text-xl font-heading font-semibold text-[#080808] dark:text-[#F5F5F7]">
                Algorithm Comparison Scorecard
              </h2>
              <p className="text-xs text-[#777777] dark:text-[#A1A1AA] mt-0.5">
                Side-by-side performance evaluation on identical stops, fleet capacity, and road network metrics.
              </p>
            </div>
            <span className="text-[11px] font-technical text-[#777777] dark:text-[#71717A]">
              Fair Benchmark · Same Graph & Matrix
            </span>
          </div>

          <div className="overflow-x-auto rounded-2xl border border-black/10 dark:border-[#29292E] bg-white dark:bg-[#111113]">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-black/10 dark:border-[#29292E] bg-black/5 dark:bg-[#18181B] text-[#777777] dark:text-[#A1A1AA] text-[10px] uppercase font-bold tracking-wider">
                  <th className="py-3 px-4">Algorithm & Category</th>
                  <th className="py-3 px-4">Feasibility</th>
                  <th className="py-3 px-4">Total Distance</th>
                  <th className="py-3 px-4">Duration</th>
                  <th className="py-3 px-4">Vehicles / Coverage</th>
                  <th className="py-3 px-4">Violations</th>
                  <th className="py-3 px-4">Objective Cost</th>
                  <th className="py-3 px-4">Runtime</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-black/5 dark:divide-[#29292E]">
                {comparisonItems.map((item) => {
                  const isCurrent = activeAlgo === item.id;
                  const isBest = item.id === bestAlgoId;

                  return (
                    <tr
                      key={item.id}
                      className={`hover:bg-black/5 dark:hover:bg-[#18181B]/80 transition-colors ${
                        isBest ? 'bg-[#B7FF00]/5 dark:bg-[#B7FF00]/5' : ''
                      }`}
                    >
                      {/* Name & Category */}
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-[#080808] dark:text-[#F5F5F7]">{item.name}</span>
                          {isBest && (
                            <span className="text-[9px] px-2 py-0.5 rounded-full bg-[#B7FF00] text-black font-bold">
                              Best Feasible
                            </span>
                          )}
                        </div>
                        <span className="text-[10px] text-[#777777] dark:text-[#A1A1AA] font-technical block mt-0.5">
                          {item.category_label} · {item.compute_type}
                        </span>
                      </td>

                      {/* Feasibility */}
                      <td className="py-3 px-4">
                        <span className={`inline-flex items-center gap-1 font-bold ${
                          item.is_feasible ? 'text-[#22C55E]' : 'text-amber-500'
                        }`}>
                          <CheckCircle2 className="h-3.5 w-3.5" />
                          <span>{item.is_feasible ? 'Feasible' : 'Penalized'}</span>
                        </span>
                      </td>

                      {/* Total Distance */}
                      <td className="py-3 px-4 font-technical font-bold text-[#080808] dark:text-[#F5F5F7]">
                        {item.total_distance_km.toFixed(2)} km
                      </td>

                      {/* Travel Time */}
                      <td className="py-3 px-4 font-technical text-[#555555] dark:text-[#A1A1AA]">
                        {Math.round(item.total_travel_time_min)} min
                      </td>

                      {/* Vehicles & Coverage */}
                      <td className="py-3 px-4 font-technical text-[#555555] dark:text-[#A1A1AA]">
                        {item.vehicles_used} vehicles · {item.served_customers} stops
                      </td>

                      {/* Violations */}
                      <td className="py-3 px-4 font-technical">
                        {item.capacity_violations === 0 && item.unserved_customers === 0 ? (
                          <span className="text-[#22C55E] font-bold">0 violations</span>
                        ) : (
                          <span className="text-red-500 font-bold">
                            {item.capacity_violations} cap / {item.unserved_customers} unserved
                          </span>
                        )}
                      </td>

                      {/* Objective Cost */}
                      <td className="py-3 px-4 font-technical font-bold text-[#080808] dark:text-[#F5F5F7]">
                        {item.total_objective_cost.toFixed(2)}
                      </td>

                      {/* Runtime */}
                      <td className="py-3 px-4 font-technical text-[#777777] dark:text-[#A1A1AA]">
                        {item.execution_time_sec.toFixed(3)}s
                      </td>

                      {/* View Action */}
                      <td className="py-3 px-4 text-right">
                        <button
                          onClick={() => setActiveAlgo(item.id)}
                          className={`px-3 py-1 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                            isCurrent
                              ? 'bg-[#080808] text-[#B7FF00] dark:bg-[#202024] dark:text-[#B7FF00] border border-black dark:border-[#B7FF00]/40'
                              : 'bg-black/5 hover:bg-black/10 dark:bg-[#18181B] dark:border dark:border-[#29292E] dark:hover:bg-[#202024] text-[#080808] dark:text-[#F5F5F7]'
                          }`}
                        >
                          {isCurrent ? 'Viewing' : 'View Map'}
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
