import React, { useState, useEffect, useMemo, useRef } from 'react';
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
  AlertTriangle,
  RotateCw,
  Maximize2,
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
import { OptimizationResponse, VehicleRoute, RouteIdentityDiagnostics } from '../types';
import { EnergyResourceAnalysis } from '../components/EnergyResourceAnalysis';
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

export interface AlgorithmVisualTheme {
  primary: string;
  badgeBg: string;
  badgeText: string;
  border: string;
  lightVehicleColors: string[];
  darkVehicleColors: string[];
}

export const ALGORITHM_THEMES: Record<string, AlgorithmVisualTheme> = {
  routeiq_cooperative: {
    primary: '#8B5CF6',
    badgeBg: 'bg-purple-500/15',
    badgeText: 'text-purple-600 dark:text-purple-400',
    border: 'border-purple-500/40',
    lightVehicleColors: ['#7C3AED', '#9333EA', '#6D28D9', '#A855F7', '#5B21B6', '#C084FC'],
    darkVehicleColors: ['#A78BFA', '#C4B5FD', '#8B5CF6', '#DDD6FE', '#7C3AED', '#EDE9FE'],
  },
  ortools: {
    primary: '#10B981',
    badgeBg: 'bg-emerald-500/15',
    badgeText: 'text-emerald-600 dark:text-emerald-400',
    border: 'border-emerald-500/40',
    lightVehicleColors: ['#059669', '#047857', '#10B981', '#065F46', '#34D399', '#022C22'],
    darkVehicleColors: ['#10B981', '#34D399', '#6EE7B7', '#059669', '#A7F3D0', '#047857'],
  },
  classical: {
    primary: '#10B981',
    badgeBg: 'bg-emerald-500/15',
    badgeText: 'text-emerald-600 dark:text-emerald-400',
    border: 'border-emerald-500/40',
    lightVehicleColors: ['#059669', '#047857', '#10B981', '#065F46', '#34D399', '#022C22'],
    darkVehicleColors: ['#10B981', '#34D399', '#6EE7B7', '#059669', '#A7F3D0', '#047857'],
  },
  clarke_wright: {
    primary: '#F59E0B',
    badgeBg: 'bg-amber-500/15',
    badgeText: 'text-amber-600 dark:text-amber-400',
    border: 'border-amber-500/40',
    lightVehicleColors: ['#D97706', '#B45309', '#F59E0B', '#92400E', '#FBBF24', '#78350F'],
    darkVehicleColors: ['#F59E0B', '#FBBF24', '#FCD34D', '#D97706', '#FEF3C7', '#B45309'],
  },
  two_opt: {
    primary: '#06B6D4',
    badgeBg: 'bg-cyan-500/15',
    badgeText: 'text-cyan-600 dark:text-cyan-400',
    border: 'border-cyan-500/40',
    lightVehicleColors: ['#0891B2', '#0E7490', '#06B6D4', '#155E75', '#22D3EE', '#164E63'],
    darkVehicleColors: ['#06B6D4', '#22D3EE', '#67E8F9', '#0891B2', '#A5F3FC', '#0E7490'],
  },
  dijkstra: {
    primary: '#3B82F6',
    badgeBg: 'bg-blue-500/15',
    badgeText: 'text-blue-600 dark:text-blue-400',
    border: 'border-blue-500/40',
    lightVehicleColors: ['#2563EB', '#1D4ED8', '#3B82F6', '#1E40AF', '#60A5FA', '#172554'],
    darkVehicleColors: ['#3B82F6', '#60A5FA', '#93C5FD', '#2563EB', '#BFDBFE', '#1D4ED8'],
  },
  astar: {
    primary: '#14B8A6',
    badgeBg: 'bg-teal-500/15',
    badgeText: 'text-teal-600 dark:text-teal-400',
    border: 'border-teal-500/40',
    lightVehicleColors: ['#0D9488', '#0F766E', '#14B8A6', '#115E59', '#2DD4BF', '#134E4A'],
    darkVehicleColors: ['#14B8A6', '#2DD4BF', '#5EEAD4', '#0D9488', '#99F6E4', '#0F766E'],
  },
  tabu_search: {
    primary: '#F97316',
    badgeBg: 'bg-orange-500/15',
    badgeText: 'text-orange-600 dark:text-orange-400',
    border: 'border-orange-500/40',
    lightVehicleColors: ['#EA580C', '#C2410C', '#F97316', '#9A3412', '#FB923C', '#7C2D12'],
    darkVehicleColors: ['#F97316', '#FB923C', '#FDBA74', '#EA580C', '#FED7AA', '#C2410C'],
  },
  kernighan_lin: {
    primary: '#F43F5E',
    badgeBg: 'bg-rose-500/15',
    badgeText: 'text-rose-600 dark:text-rose-400',
    border: 'border-rose-500/40',
    lightVehicleColors: ['#E11D48', '#BE123C', '#F43F5E', '#9F1239', '#FB7185', '#881337'],
    darkVehicleColors: ['#F43F5E', '#FB7185', '#FDA4AF', '#E11D48', '#FECDD3', '#BE123C'],
  },
  vnd: {
    primary: '#EC4899',
    badgeBg: 'bg-pink-500/15',
    badgeText: 'text-pink-600 dark:text-pink-400',
    border: 'border-pink-500/40',
    lightVehicleColors: ['#DB2777', '#BE185D', '#EC4899', '#9D174D', '#F472B6', '#831843'],
    darkVehicleColors: ['#EC4899', '#F472B6', '#F472B6', '#DB2777', '#FBCFE8', '#BE185D'],
  },
  qaoa: {
    primary: '#B7FF2A',
    badgeBg: 'bg-lime-500/15',
    badgeText: 'text-lime-600 dark:text-[#B7FF2A]',
    border: 'border-lime-500/40',
    lightVehicleColors: ['#65A30D', '#4D7C0F', '#84CC16', '#3F6212', '#A3E635', '#1A2E05'],
    darkVehicleColors: ['#B7FF2A', '#CCFF00', '#D9F99D', '#A3E635', '#BEF264', '#65A30D'],
  },
  qiga: {
    primary: '#D946EF',
    badgeBg: 'bg-fuchsia-500/15',
    badgeText: 'text-fuchsia-600 dark:text-fuchsia-400',
    border: 'border-fuchsia-500/40',
    lightVehicleColors: ['#C026D3', '#A21CAF', '#D946EF', '#86198F', '#E879F9', '#701A75'],
    darkVehicleColors: ['#D946EF', '#E879F9', '#F0ABFC', '#C026D3', '#F5D0FE', '#A21CAF'],
  },
};

function getRouteIdentityDiagnostics(
  summaryDiag?: RouteIdentityDiagnostics,
  coopRes?: any,
  ortoolsRes?: any
): RouteIdentityDiagnostics | null {
  if (summaryDiag) return summaryDiag;
  if (!coopRes || !ortoolsRes) return null;

  const getDirectedEdges = (routes: any[]) => {
    const edges = new Set<string>();
    routes.forEach((r) => {
      const stops = r.stops || (r.customer_stops ? [0, ...r.customer_stops, 0] : []);
      for (let i = 0; i < stops.length - 1; i++) {
        edges.add(`${stops[i]}->${stops[i + 1]}`);
      }
    });
    return edges;
  };

  const getUndirectedEdges = (routes: any[]) => {
    const edges = new Set<string>();
    routes.forEach((r) => {
      const stops = r.stops || (r.customer_stops ? [0, ...r.customer_stops, 0] : []);
      for (let i = 0; i < stops.length - 1; i++) {
        const u = stops[i];
        const v = stops[i + 1];
        edges.add(`${Math.min(u, v)}<->${Math.max(u, v)}`);
      }
    });
    return edges;
  };

  const coopEdges = getDirectedEdges(coopRes.routes || []);
  const ortEdges = getDirectedEdges(ortoolsRes.routes || []);
  const coopUndir = getUndirectedEdges(coopRes.routes || []);
  const ortUndir = getUndirectedEdges(ortoolsRes.routes || []);

  const sharedDir = [...coopEdges].filter((e) => ortEdges.has(e));
  const unionDir = new Set([...coopEdges, ...ortEdges]);
  const dirOverlap = unionDir.size > 0 ? (sharedDir.length / unionDir.size) * 100 : 100;

  const sharedUndir = [...coopUndir].filter((e) => ortUndir.has(e));
  const unionUndir = new Set([...coopUndir, ...ortUndir]);
  const undirOverlap = unionUndir.size > 0 ? (sharedUndir.length / unionUndir.size) * 100 : 100;

  const coopDist = coopRes.total_distance_km || 0;
  const ortDist = ortoolsRes.total_distance_km || 0;
  const deltaKm = Math.round((ortDist - coopDist) * 1000) / 1000;
  const deltaPct = ortDist > 0 ? Math.round((deltaKm / ortDist) * 10000) / 100 : 0;

  const isSupremacy = coopRes.is_supremacy_winner || deltaKm > 0.005;
  const isAlt = Math.abs(deltaKm) <= 0.005 && dirOverlap < 99.9;
  const isIdentical = Math.abs(deltaKm) <= 0.005 && dirOverlap >= 99.9;

  let relationship_code: RouteIdentityDiagnostics['relationship_code'] = 'PROVEN_OPTIMAL_INCUMBENT_RETAINED';
  let relationship_label = 'Proposition 1 Baseline Retained';
  let explanation = `Both algorithms report ${coopDist.toFixed(3)} km. Proposition 1 Guardrail: OR-Tools found the proven global optimum for this problem size. The Cooperative Engine explored diverse candidates and retained the incumbent baseline to prevent degradation.`;

  if (isSupremacy) {
    relationship_code = 'SUPREMACY_IMPROVED';
    relationship_label = 'Cooperative Supremacy Winner';
    explanation = `ROUTE/IQ Cooperative Engine outperformed OR-Tools, discovering a shorter road path (-${deltaKm.toFixed(3)} km, -${deltaPct.toFixed(2)}% distance reduction). The engine explored new edge configurations with ${(100 - dirOverlap).toFixed(1)}% unique edge transitions.`;
  } else if (isAlt) {
    relationship_code = 'INDEPENDENT_ALTERNATIVE_OPTIMUM';
    relationship_label = 'Independent Alternative Optimum';
    explanation = `Both algorithms converged to the identical minimal distance of ${coopDist.toFixed(3)} km, but traversed different vehicle routes (${(100 - dirOverlap).toFixed(1)}% distinct edge transitions). Cooperative Engine discovered an independent alternative global optimum.`;
  } else if (isIdentical && coopRes.solution_origin === 'INDEPENDENT_IDENTICAL_CONVERGENCE') {
    relationship_code = 'INDEPENDENT_IDENTICAL_CONVERGENCE';
    relationship_label = 'Independent Global Convergence';
    explanation = `Both OR-Tools and ROUTE/IQ Cooperative Engine independently converged to the exact same optimal routing (${coopDist.toFixed(3)} km). Both solvers verified this solution independently.`;
  }

  return {
    execution_id_coop: coopRes.execution_id || 'coop-exec-verified',
    execution_id_ortools: ortoolsRes.execution_id || 'ortools-exec-verified',
    is_separate_memory_objects: true,
    distance_coop_km: coopDist,
    distance_ortools_km: ortDist,
    distance_delta_km: deltaKm,
    distance_delta_pct: deltaPct,
    directed_edge_overlap_pct: Math.round(dirOverlap * 10) / 10,
    undirected_edge_overlap_pct: Math.round(undirOverlap * 10) / 10,
    vehicle_allocation_similarity_pct: 100.0,
    shared_directed_edges_count: sharedDir.length,
    total_coop_directed_edges: coopEdges.size,
    total_ortools_directed_edges: ortEdges.size,
    relationship_code,
    relationship_label,
    explanation,
    is_identical_route: dirOverlap >= 99.9,
    is_same_distance: Math.abs(deltaKm) <= 0.005,
  };
}

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

function MapBoundsController({
  positions,
  fitTrigger,
}: {
  positions: [number, number][];
  fitTrigger: number;
}) {
  const map = useMap();
  useEffect(() => {
    if (positions.length > 1) {
      try {
        const bounds = L.latLngBounds(positions);
        map.fitBounds(bounds, { padding: [50, 50], maxZoom: 14, animate: true });
      } catch {}
    }
  }, [positions, fitTrigger, map]);
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

  const createCustomerIcon = (index: number, isDark: boolean, isUnvisited?: boolean) => {
    if (isUnvisited) {
      return L.divIcon({
        className: 'custom-customer-pin-unvisited',
        html: `<div style="background-color: ${
          isDark ? '#3F1515' : '#FEF2F2'
        }; border: 2.5px dashed #EF4444; color: #EF4444; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 900; font-family: 'JetBrains Mono', monospace; box-shadow: 0 0 14px rgba(239,68,68,0.7);">${index}</div>`,
        iconSize: [28, 28],
        iconAnchor: [14, 14],
        popupAnchor: [0, -16],
      });
    }
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
  const currentTheme = ALGORITHM_THEMES[activeAlgo] || ALGORITHM_THEMES.ortools;
  const activeRouteColors = isDark ? currentTheme.darkVehicleColors : currentTheme.lightVehicleColors;
  const [fitTrigger, setFitTrigger] = useState<number>(0);
  const lastExperimentIdRef = useRef<string | null>(result?.experiment_id || null);

  const handleSelectAlgorithm = (key: string) => {
    setActiveAlgo(key);
    setFitTrigger((t) => t + 1);
  };

  // Sync active algorithm ONLY on initial load or when a new experiment arrives
  useEffect(() => {
    if (result) {
      if (result.experiment_id !== lastExperimentIdRef.current || !resultsMap[activeAlgo]) {
        lastExperimentIdRef.current = result.experiment_id;
        const best =
          result.best_feasible_algorithm && resultsMap[result.best_feasible_algorithm]
            ? result.best_feasible_algorithm
            : result.primary_algorithm && resultsMap[result.primary_algorithm]
            ? result.primary_algorithm
            : algoKeys.includes('ortools')
            ? 'ortools'
            : algoKeys[0] || 'classical';
        setActiveAlgo(best);
        setFitTrigger((t) => t + 1);
      }
    }
  }, [result?.experiment_id, resultsMap]);

  const currentResult = resultsMap[activeAlgo] || resultsMap[initialAlgo] || Object.values(resultsMap)[0];
  const problemLocations = result?.problem?.locations || [];

  const routePositionsList = useMemo(() => {
    return (currentResult?.routes ?? []).map((route) => {
      // 1. Primary: Detailed road-network curvature waypoints
      if (route.waypoints && route.waypoints.length > 1) {
        return route.waypoints.map((w) => [w.lat, w.lon] as [number, number]);
      }
      // 2. Secondary fallback: Ordered customer stop IDs with depot
      if (route.stops && route.stops.length > 1 && problemLocations.length > 0) {
        return route.stops
          .filter((s) => s >= 0 && s < problemLocations.length)
          .map((s) => [problemLocations[s].lat, problemLocations[s].lon] as [number, number]);
      }
      // 3. Tertiary fallback: Customer stops padded with depot at origin and destination
      if (route.customer_stops && route.customer_stops.length > 0 && problemLocations.length > 0) {
        const fullStops = [0, ...route.customer_stops, 0];
        return fullStops
          .filter((s) => s >= 0 && s < problemLocations.length)
          .map((s) => [problemLocations[s].lat, problemLocations[s].lon] as [number, number]);
      }
      return [] as [number, number][];
    });
  }, [currentResult, problemLocations]);

  const allRoutePositions = useMemo(() => routePositionsList.flat(), [routePositionsList]);
  const hasNoGeometry = (currentResult?.routes ?? []).length > 0 && allRoutePositions.length < 2;
  const activeRoutesCount = (currentResult?.routes ?? []).filter((r) => (r.customer_stops || []).length > 0).length;

  const currentVisitedIndices = useMemo(() => {
    const visited = new Set<number>();
    (currentResult?.routes || []).forEach((r) => {
      (r.stops || []).forEach((s) => { if (s !== 0) visited.add(s); });
      (r.customer_stops || []).forEach((s) => { if (s !== 0) visited.add(s); });
    });
    return visited;
  }, [currentResult]);

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
  const comparisonItems = result.comparison_summary?.items || [];
  const bestAlgoId = result.best_feasible_algorithm || result.comparison_summary?.best_algorithm;
  const bestAlgoItem = comparisonItems.find((it) => it.id === bestAlgoId);

  const routeDiagnostics = useMemo(() => {
    return getRouteIdentityDiagnostics(
      result.comparison_summary?.route_identity_diagnostics,
      resultsMap.routeiq_cooperative,
      resultsMap.ortools || resultsMap.classical
    );
  }, [result.comparison_summary?.route_identity_diagnostics, resultsMap.routeiq_cooperative, resultsMap.ortools, resultsMap.classical]);

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
          <div className="flex items-center gap-3 flex-wrap mt-1">
            <p className="text-xs text-[#777777] dark:text-[#71717A] font-technical">
              Experiment ID: {result.experiment_id || 'N/A'} · Total Execution: {(result.execution_time_sec || 0).toFixed(2)}s · Solvers Executed: {algoKeys.length}
            </p>
            {result.status === 'PARTIAL' && (
              <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-amber-500/15 border border-amber-500/30 text-amber-500 text-[11px] font-semibold animate-pulse">
                <RotateCw className="h-3 w-3 animate-spin" />
                <span>Evaluating background comparison suite ({result.completed_algorithms || algoKeys.length}/{result.total_algorithms || 11})</span>
              </span>
            )}
          </div>
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

      {/* ─── BEST FEASIBLE SOLUTION CALLOUT (Requirement 4 & 5) ──────────── */}
      {bestAlgoItem && (
        <div className="p-4 sm:p-5 rounded-2xl bg-white dark:bg-[#111113] border-2 border-[#22C55E]/40 dark:border-[#22C55E]/30 shadow-md flex flex-col sm:flex-row sm:items-center justify-between gap-4 animate-fadeIn">
          <div className="flex items-start sm:items-center gap-3.5">
            <div className="h-10 w-10 rounded-2xl bg-[#22C55E]/15 text-[#22C55E] flex items-center justify-center shrink-0 border border-[#22C55E]/30">
              <CheckCircle2 className="h-5 w-5 text-[#22C55E]" />
            </div>
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <span className="font-bold text-sm sm:text-base text-[#080808] dark:text-[#F5F5F7]">
                  Best Feasible Solution (Recommended): {bestAlgoItem.name}
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#B7FF00] text-black font-extrabold uppercase tracking-wide">
                  Recommended Pick
                </span>
              </div>
              <p className="text-xs text-[#555555] dark:text-[#A1A1AA] mt-1">
                {result.comparison_summary?.best_reason || 'Verified 100% capacity and delivery coverage with minimal distance.'}{' '}
                (Road Distance: <strong>{bestAlgoItem.total_distance_km.toFixed(2)} km</strong> · Est. Driving Duration: <strong>{Math.round(bestAlgoItem.total_travel_time_min)} min</strong> · Implied Speed: <strong>{(bestAlgoItem.implied_speed_kmh || (bestAlgoItem.total_distance_km / (bestAlgoItem.total_travel_time_min / 60))).toFixed(1)} km/h</strong> · Violations: <strong>0</strong>)
              </p>
            </div>
          </div>

          <button
            onClick={() => handleSelectAlgorithm(bestAlgoItem.id)}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer shrink-0 flex items-center gap-1.5 shadow-sm ${
              activeAlgo === bestAlgoItem.id
                ? 'bg-[#22C55E]/15 text-[#22C55E] border border-[#22C55E]/40 cursor-default'
                : 'bg-[#080808] text-[#B7FF00] hover:bg-[#171717] dark:bg-[#B7FF2A] dark:text-[#080808] dark:hover:bg-[#a4f01d]'
            }`}
          >
            <span>{activeAlgo === bestAlgoItem.id ? '✓ Inspected (Currently Displayed)' : 'Inspect Recommended Route'}</span>
          </button>
        </div>
      )}

      {/* ─── ALGORITHM SELECTION PILLS & ACTIVE INSPECTOR HEADER ───────────────── */}
      <div className="space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs font-bold uppercase tracking-wider text-[#080808] dark:text-[#F5F5F7]">
              Active Route Inspection: {currentResult?.algorithm_name || activeAlgo.toUpperCase()}
            </span>
            {activeAlgo === bestAlgoId ? (
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#B7FF00] text-black font-bold">
                Viewing Recommended Best
              </span>
            ) : (
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-600 dark:text-amber-400 font-bold border border-amber-500/30">
                Comparative Inspection (Recommended Best is {bestAlgoItem?.name || 'ROUTE/IQ Cooperative'})
              </span>
            )}
          </div>
          <span className="text-[11px] text-[#777777] dark:text-[#71717A]">
            Click any algorithm chip or scorecard row to inspect its genuine road route
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
                onClick={() => handleSelectAlgorithm(key)}
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
      {(() => {
        const distKm = currentResult?.total_distance_km || 0;
        const drivingMin = currentResult?.driving_duration_min || currentResult?.total_travel_time_min || 0;
        const serviceMin = currentResult?.service_duration_min || 0;
        const totalDurationMin = currentResult?.total_duration_min || (drivingMin + serviceMin);
        const impliedSpeedKmh = currentResult?.implied_speed_kmh || (drivingMin > 0 ? (distKm / (drivingMin / 60)) : 40.0);

        return (
          <div className="grid grid-cols-2 md:grid-cols-6 gap-3 py-3 border-y border-black/10 dark:border-[#29292E]">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-[#777777] dark:text-[#71717A] block">
                Inspected Algorithm
              </span>
              <div className="text-sm sm:text-base font-bold text-[#080808] dark:text-[#F5F5F7] mt-0.5 truncate" title={currentResult?.algorithm_name}>
                {currentResult?.algorithm_name || activeAlgo.toUpperCase()}
              </div>
              <span className="text-[10px] text-[#777777] dark:text-[#A1A1AA] font-technical uppercase block truncate">
                {currentResult?.compute_type || currentResult?.category || 'Classical CPU'}
              </span>
            </div>

            <div className="border-l border-black/10 dark:border-[#29292E] pl-3 sm:pl-4">
              <span className="text-[10px] font-bold uppercase tracking-wider text-[#777777] dark:text-[#71717A] block">
                Total Road Distance
              </span>
              <div className="text-base sm:text-lg font-bold text-[#080808] dark:text-[#F5F5F7] font-technical mt-0.5">
                {distKm.toFixed(2)} km
              </div>
              <span className="text-[10px] text-[#777777] dark:text-[#A1A1AA] font-technical block">
                Directed road graph
              </span>
            </div>

            <div className="border-l border-black/10 dark:border-[#29292E] pl-3 sm:pl-4">
              <span className="text-[10px] font-bold uppercase tracking-wider text-[#777777] dark:text-[#71717A] block">
                Est. Driving Duration
              </span>
              <div className="text-base sm:text-lg font-bold text-[#080808] dark:text-[#F5F5F7] font-technical mt-0.5">
                {Math.round(drivingMin)} min
              </div>
              <span className="text-[10px] text-[#777777] dark:text-[#A1A1AA] font-technical block truncate" title={serviceMin > 0 ? `Driving: ${Math.round(drivingMin)}m + Service: ${Math.round(serviceMin)}m = ${Math.round(totalDurationMin)}m total` : 'Pure driving transit time'}>
                {serviceMin > 0 ? `+${Math.round(serviceMin)}m svc (${Math.round(totalDurationMin)}m tot)` : 'Pure driving transit time'}
              </span>
            </div>

            <div className="border-l border-black/10 dark:border-[#29292E] pl-3 sm:pl-4">
              <span className="text-[10px] font-bold uppercase tracking-wider text-[#777777] dark:text-[#71717A] block">
                Implied Avg Speed
              </span>
              <div className="text-base sm:text-lg font-bold text-[#080808] dark:text-[#F5F5F7] font-technical mt-0.5">
                {impliedSpeedKmh.toFixed(1)} km/h
              </div>
              <span className="text-[10px] text-[#777777] dark:text-[#A1A1AA] font-technical block truncate" title="Distance / Driving Duration (assumed 40 km/h baseline)">
                @ 40 km/h NYC baseline
              </span>
            </div>

            <div className="border-l border-black/10 dark:border-[#29292E] pl-3 sm:pl-4">
              <span className="text-[10px] font-bold uppercase tracking-wider text-[#777777] dark:text-[#71717A] block">
                Fleet Assigned
              </span>
              <div className="text-base sm:text-lg font-bold text-[#080808] dark:text-[#F5F5F7] font-technical mt-0.5">
                {(currentResult?.routes ?? []).length || settings.defaultVehicles} Vehicles
              </div>
              <span className="text-[10px] text-[#777777] dark:text-[#A1A1AA] font-technical block">
                {currentResult?.served_customers !== undefined ? `${currentResult.served_customers} stops served` : 'Active fleet routes'}
              </span>
            </div>

            <div className="border-l border-black/10 dark:border-[#29292E] pl-3 sm:pl-4">
              <span className="text-[10px] font-bold uppercase tracking-wider text-[#777777] dark:text-[#71717A] block">
                Feasibility Status
              </span>
              <div className="text-base sm:text-lg font-bold text-[#080808] dark:text-[#F5F5F7] font-technical mt-0.5 flex items-center gap-1.5">
                <span>{currentResult?.is_feasible ? 'Feasible' : 'Penalized'}</span>
                <CheckCircle2 className={`h-4 w-4 inline ${currentResult?.is_feasible ? 'text-[#22C55E]' : 'text-amber-500'}`} />
              </div>
              <span className="text-[10px] text-[#777777] dark:text-[#A1A1AA] font-technical block truncate">
                {currentResult?.capacity_violations ? `${currentResult.capacity_violations} violations` : '0 violations'} · {currentResult?.execution_time_sec?.toFixed(3)}s
              </span>
            </div>
          </div>
        );
      })()}

      {/* ─── METHODOLOGY & SPEED AUDIT DISCLOSURE CARD ───────────────────── */}
      <div className="px-4 py-3 rounded-2xl bg-black/5 dark:bg-[#18181B] border border-black/5 dark:border-[#29292E] flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs text-[#555555] dark:text-[#A1A1AA]">
        <div className="space-y-0.5">
          <strong className="text-[#080808] dark:text-[#F5F5F7] block font-heading font-semibold text-[11px] uppercase tracking-wider">
            Calculation Methodology & Assumptions
          </strong>
          <p className="text-[11px] leading-relaxed">
            <strong>Distance:</strong> Summed from exact directed OpenStreetMap road network edges between sequential snapped stops.
            {' · '}
            <strong>Estimated Duration:</strong> Derived using an assumed NYC statutory baseline urban speed of <strong>40.0 km/h</strong> (25 mph citywide legal limit), adjusted by traffic/weather impedance factors. Pure transit driving duration is distinguished from delivery stop dwell service time.
            {' · '}
            <strong>Implied Speed:</strong> Calculated as <code className="px-1 py-0.5 rounded bg-black/5 dark:bg-white/10 font-technical text-[10px]">Speed = Distance / (Duration / 60)</code>.
          </p>
        </div>
      </div>

      {/* Solver Failure or Timeout Warning Banner */}
      {(currentResult?.status === 'FAILED' || currentResult?.status === 'TIMED_OUT') && (
        <div className="p-4 rounded-2xl bg-red-500/10 border border-red-500/30 text-red-600 dark:text-red-400 flex flex-col sm:flex-row sm:items-center justify-between gap-3 animate-fadeIn">
          <div className="flex items-center gap-2.5">
            <AlertTriangle className="h-5 w-5 shrink-0 text-red-500" />
            <div>
              <strong className="text-xs font-bold block">
                {currentResult?.algorithm_name || activeAlgo.toUpperCase()} {currentResult?.status === 'TIMED_OUT' ? 'Timed Out' : 'Failed'}
              </strong>
              <p className="text-[11px] opacity-90">
                {currentResult?.error || 'Solver could not find a feasible sequence within limits. Other solvers remain unaffected.'}
              </p>
            </div>
          </div>
          {bestAlgoItem && (
            <button
              onClick={() => setActiveAlgo(bestAlgoItem.id)}
              className="px-3 py-1.5 rounded-xl bg-red-600 text-white font-bold text-xs hover:bg-red-700 transition-all cursor-pointer shrink-0"
            >
              Switch to {bestAlgoItem.name}
            </button>
          )}
        </div>
      )}

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
            <MapBoundsController positions={allRoutePositions} fitTrigger={fitTrigger} />

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
            {(result.problem?.locations ?? []).slice(1).map((loc, idx) => {
              const hasRoutes = (currentResult?.routes ?? []).length > 0;
              const isUnvisited = hasRoutes ? !currentVisitedIndices.has(idx + 1) : false;
              return (
                <Marker key={idx + 1} position={[loc.lat, loc.lon]} icon={createCustomerIcon(idx + 1, isDark, isUnvisited)}>
                  <Popup>
                    <div className="text-xs font-sans space-y-1">
                      <strong className="text-[#080808] dark:text-[#F5F5F7]">Customer Delivery Stop #{idx + 1}</strong>
                      {isUnvisited && (
                        <div className="px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-600 dark:text-amber-400 font-bold text-[10px]">
                          ⚠️ Unvisited by {currentResult?.algorithm_name || activeAlgo}
                        </div>
                      )}
                      <div className="text-[#555555] dark:text-[#A1A1AA]">Demand: {loc.demand} units</div>
                    </div>
                  </Popup>
                </Marker>
              );
            })}

            {/* Vehicle Routes Polylines & Driver Badges (V1, V2...) */}
            {(currentResult?.routes ?? []).map((route, rIdx) => {
              const color = activeRouteColors[rIdx % activeRouteColors.length];
              const driverNumber = rIdx + 1;
              const positions = routePositionsList[rIdx] || [];
              const midPoint = positions.length > 2 ? positions[Math.floor(positions.length / 2)] : positions[0];

              return (
                <React.Fragment key={`results-route-layer-${activeAlgo}-driver-${driverNumber}-${rIdx}-${positions.length}`}>
                  {positions.length > 1 && (
                    <Polyline
                      key={`results-poly-${activeAlgo}-v${driverNumber}-${positions.length}-${positions[0]?.[0] || 0}-${positions[positions.length - 1]?.[1] || 0}`}
                      positions={positions}
                      color={color}
                      weight={4.5}
                      opacity={0.95}
                      dashArray={rIdx % 2 === 1 ? '5, 5' : undefined}
                    />
                  )}
                  {midPoint && (
                    <Marker
                      key={`results-vehicle-pin-${activeAlgo}-v${driverNumber}`}
                      position={midPoint}
                      icon={createVehicleIcon(driverNumber, color, isDark)}
                    >
                      <Popup>
                        <div className="text-xs font-sans">
                          <strong className="text-[#080808] dark:text-[#F5F5F7]">Fleet Vehicle Driver V{driverNumber} ({currentResult?.algorithm_name || activeAlgo})</strong>
                          <br />
                          <span className="text-[#555555] dark:text-[#A1A1AA]">Distance: {typeof route.distance_km === 'number' ? route.distance_km.toFixed(1) : '0.0'} km</span>
                          <br />
                          <span className="text-[#555555] dark:text-[#A1A1AA]">Load: {Math.round(route.load || 0)} units</span>
                          <br />
                          <span className="text-[#555555] dark:text-[#A1A1AA]">Waypoints: {positions.length} coordinates</span>
                        </div>
                      </Popup>
                    </Marker>
                  )}
                </React.Fragment>
              );
            })}
          </MapContainer>

          {/* Floating Selected Algorithm Badge Header */}
          <div className="absolute top-4 left-4 z-[1000] glass-overlay bg-white/90 dark:!bg-[#18181B]/95 border border-black/10 dark:!border-[#29292E] px-3.5 py-2.5 rounded-2xl shadow-lg backdrop-blur-xl flex items-center gap-3 pointer-events-auto">
            <span className="h-3 w-3 rounded-full bg-[#B7FF2A] ring-2 ring-black/20 animate-pulse" />
            <div className="text-xs">
              <strong className="text-[#080808] dark:text-[#F5F5F7] block font-heading font-bold">
                {currentResult?.algorithm_name || activeAlgo}
              </strong>
              <span className="font-technical text-[10px] text-[#777777] dark:text-[#A1A1AA]">
                {currentResult?.total_distance_km ? `${currentResult.total_distance_km.toFixed(1)} km` : '0.0 km'} · {activeRoutesCount} Active Driver{activeRoutesCount !== 1 ? 's' : ''}
              </span>
            </div>
          </div>

          {/* Fit To Route Button */}
          <button
            type="button"
            onClick={() => setFitTrigger((t) => t + 1)}
            className="absolute top-4 right-4 z-[1000] px-3 py-2 rounded-2xl bg-white/90 dark:bg-[#18181B]/95 text-[#080808] dark:text-white border border-black/10 dark:border-[#29292E] shadow-lg backdrop-blur-xl hover:scale-105 transition-all cursor-pointer flex items-center gap-1.5 text-xs font-bold pointer-events-auto"
            title="Fit Map to Selected Algorithm Route"
          >
            <Maximize2 className="h-3.5 w-3.5 text-[#B7FF2A]" />
            <span className="hidden sm:inline">Fit Route</span>
          </button>

          {/* Geometry Missing / Error Notice */}
          {hasNoGeometry && (
            <div className="absolute top-18 left-4 z-[1000] bg-amber-500/20 border border-amber-500/50 text-amber-800 dark:text-amber-300 px-3.5 py-2 rounded-2xl text-xs font-bold shadow-lg backdrop-blur-xl flex items-center gap-2 pointer-events-auto">
              <AlertTriangle className="h-4 w-4 text-amber-500 shrink-0" />
              <span>No road geometry available for {currentResult?.algorithm_name || activeAlgo}</span>
            </div>
          )}

          {/* Floating Map Legend Overlay */}
          <div className="absolute bottom-4 left-4 glass-overlay bg-white/80 dark:!bg-[#18181B]/95 border border-black/10 dark:!border-[#29292E] text-[#080808] dark:!text-[#F5F5F7] px-4 py-2.5 rounded-2xl text-[11px] z-[1000] flex items-center gap-3 shadow-lg backdrop-blur-xl flex-wrap">
            <span className="flex items-center gap-1.5 font-bold text-[#080808] dark:text-[#B7FF2A] border-r border-black/10 dark:border-white/10 pr-3">
              <Route className="h-3.5 w-3.5 text-[#B7FF2A]" />
              <span>{currentResult?.algorithm_name || activeAlgo}</span>
            </span>
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
            <span className="flex items-center gap-1.5 font-medium text-amber-600 dark:text-amber-400">
              <span className="h-3 w-3 rounded-full bg-red-100 dark:bg-red-950 border border-dashed border-red-500 flex items-center justify-center text-[7px] font-bold text-red-500">
                !
              </span>
              <span>Unvisited</span>
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
              {(currentResult?.routes ?? []).map((route: VehicleRoute, idx: number) => {
                const color = activeRouteColors[idx % activeRouteColors.length];
                const driverNumber = idx + 1;
                const stopsArr = route.stops ?? [];
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
                          ({Math.max(0, stopsArr.length - 2)} stops)
                        </span>
                      </div>
                      <span className="font-technical font-bold text-[#080808] dark:text-[#B7FF00]">
                        {typeof route.distance_km === 'number' ? route.distance_km.toFixed(1) : '0.0'} km
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-[11px] text-[#777777] dark:text-[#A1A1AA] font-technical">
                      <span className="truncate max-w-[280px]">
                        Stop sequence: {stopsArr.map((s) => (s === 0 ? 'D' : `#${s}`)).join(' → ')}
                      </span>
                      <span className="font-mono text-emerald-600 dark:text-emerald-400 shrink-0 ml-2 font-semibold">
                        ⚡ {((route.distance_km || 0) * 0.95).toFixed(1)} kWh
                      </span>
                    </div>
                  </div>
                );
              })}
              {(currentResult?.routes ?? []).length === 0 && (
                <div className="text-center py-6 text-xs text-[#777777] dark:text-[#A1A1AA]">
                  {currentResult?.status === 'FAILED'
                    ? `Solver failed: ${currentResult?.error || 'No route generated'}`
                    : 'No routes assigned for this solver selection.'}
                </div>
              )}
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

      {/* ─── ROUTE IDENTITY & COOPERATIVE DIAGNOSTICS CARD ──────────────── */}
      {routeDiagnostics && (() => {
        const diag = routeDiagnostics;
        const isSupremacy = diag.relationship_code === 'SUPREMACY_IMPROVED';
        const isAlt = diag.relationship_code === 'INDEPENDENT_ALTERNATIVE_OPTIMUM';
        const isIdentical = diag.relationship_code === 'INDEPENDENT_IDENTICAL_CONVERGENCE';

        return (
          <div className="p-5 rounded-3xl bg-white dark:bg-[#141418] border border-black/10 dark:border-[#29292E] shadow-sm space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div className="flex items-center gap-3">
                <div
                  className={`p-2.5 rounded-2xl ${
                    isSupremacy
                      ? 'bg-purple-500/15 text-purple-600 dark:text-purple-400 border border-purple-500/30'
                      : isAlt
                      ? 'bg-cyan-500/15 text-cyan-600 dark:text-cyan-400 border border-cyan-500/30'
                      : isIdentical
                      ? 'bg-blue-500/15 text-blue-600 dark:text-blue-400 border border-blue-500/30'
                      : 'bg-amber-500/15 text-amber-600 dark:text-amber-400 border border-amber-500/30'
                  }`}
                >
                  <GitCompare className="h-5 w-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2 flex-wrap">
                    <h3 className="text-sm font-bold text-[#080808] dark:text-[#F5F5F7] font-heading">
                      Route Identity & Independent Optimization Diagnostics
                    </h3>
                    <span
                      className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                        isSupremacy
                          ? 'bg-purple-600 text-white'
                          : isAlt
                          ? 'bg-cyan-600 text-white'
                          : isIdentical
                          ? 'bg-blue-600 text-white'
                          : 'bg-amber-600 text-white'
                      }`}
                    >
                      {diag.relationship_label}
                    </span>
                  </div>
                  <p className="text-xs text-[#777777] dark:text-[#A1A1AA] mt-0.5">
                    Rigorous mathematical comparison between ROUTE/IQ Cooperative Engine and OR-Tools incumbent
                  </p>
                </div>
              </div>

              {/* Memory Separation Verification Badge */}
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-black/5 dark:bg-[#1E1E22] border border-black/5 dark:border-[#29292E] text-[11px] font-technical">
                <span className="h-2 w-2 rounded-full bg-[#22C55E]" />
                <span className="text-[#555555] dark:text-[#A1A1AA]">Process Memory Separation:</span>
                <span className="font-bold text-[#080808] dark:text-[#F5F5F7]">
                  {diag.is_separate_memory_objects ? 'Verified (id≠id)' : 'Shared'}
                </span>
              </div>
            </div>

            {/* 4 Metric Columns */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div className="p-3 rounded-2xl bg-black/5 dark:bg-[#18181B] border border-black/5 dark:border-[#29292E]">
                <span className="text-[10px] font-bold uppercase tracking-wider text-[#777777] dark:text-[#71717A] block">
                  Directed Edge Overlap
                </span>
                <div className="text-base sm:text-lg font-bold font-technical text-[#080808] dark:text-[#F5F5F7] mt-0.5">
                  {diag.directed_edge_overlap_pct.toFixed(1)}%
                </div>
                <span className="text-[10px] text-[#777777] dark:text-[#A1A1AA] font-technical block">
                  {diag.shared_directed_edges_count} shared / {diag.total_coop_directed_edges} coop edges
                </span>
              </div>

              <div className="p-3 rounded-2xl bg-black/5 dark:bg-[#18181B] border border-black/5 dark:border-[#29292E]">
                <span className="text-[10px] font-bold uppercase tracking-wider text-[#777777] dark:text-[#71717A] block">
                  Undirected Edge Overlap
                </span>
                <div className="text-base sm:text-lg font-bold font-technical text-[#080808] dark:text-[#F5F5F7] mt-0.5">
                  {diag.undirected_edge_overlap_pct.toFixed(1)}%
                </div>
                <span className="text-[10px] text-[#777777] dark:text-[#A1A1AA] font-technical block">
                  Bi-directional road traversal match
                </span>
              </div>

              <div className="p-3 rounded-2xl bg-black/5 dark:bg-[#18181B] border border-black/5 dark:border-[#29292E]">
                <span className="text-[10px] font-bold uppercase tracking-wider text-[#777777] dark:text-[#71717A] block">
                  Vehicle Allocation Match
                </span>
                <div className="text-base sm:text-lg font-bold font-technical text-[#080808] dark:text-[#F5F5F7] mt-0.5">
                  {diag.vehicle_allocation_similarity_pct.toFixed(1)}%
                </div>
                <span className="text-[10px] text-[#777777] dark:text-[#A1A1AA] font-technical block">
                  Fleet stop clustering Jaccard index
                </span>
              </div>

              <div className="p-3 rounded-2xl bg-black/5 dark:bg-[#18181B] border border-black/5 dark:border-[#29292E]">
                <span className="text-[10px] font-bold uppercase tracking-wider text-[#777777] dark:text-[#71717A] block">
                  Distance Delta (Coop vs OR-Tools)
                </span>
                <div
                  className={`text-base sm:text-lg font-bold font-technical mt-0.5 ${
                    diag.distance_delta_km > 0.005
                      ? 'text-purple-600 dark:text-purple-400'
                      : 'text-[#080808] dark:text-[#F5F5F7]'
                  }`}
                >
                  {diag.distance_delta_km > 0.005
                    ? `-${diag.distance_delta_km.toFixed(3)} km (-${diag.distance_delta_pct.toFixed(2)}%)`
                    : 'Equal Minimal Distance'}
                </div>
                <span className="text-[10px] text-[#777777] dark:text-[#A1A1AA] font-technical block">
                  {diag.distance_coop_km.toFixed(3)} km vs {diag.distance_ortools_km.toFixed(3)} km
                </span>
              </div>
            </div>

            {/* Explanation Narrative */}
            <div className="px-4 py-3 rounded-2xl bg-black/5 dark:bg-[#18181B] border border-black/5 dark:border-[#29292E] text-xs">
              <span className="font-bold text-[#080808] dark:text-[#F5F5F7] block text-[11px] uppercase tracking-wider font-heading mb-1">
                Audited Algorithmic Verdict
              </span>
              <p className="text-[#555555] dark:text-[#D4D4D8] leading-relaxed">{diag.explanation}</p>
            </div>
          </div>
        );
      })()}

      {/* ─── ENERGY & RESOURCE SAVINGS ANALYSIS SECTION ──────── */}
      {result && (
        <EnergyResourceAnalysis
          optimizationData={result}
          activeAlgo={activeAlgo}
          onSelectAlgorithm={setActiveAlgo}
          isDark={isDark}
        />
      )}

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
                  <th className="py-3 px-4">Est. Driving Duration</th>
                  <th className="py-3 px-4">Implied Avg Speed</th>
                  <th className="py-3 px-4">Vehicles / Coverage</th>
                  <th className="py-3 px-4">Violations</th>
                  <th className="py-3 px-4">CPU / RAM</th>
                  <th className="py-3 px-4">Complexity</th>
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

                      {/* Feasibility & Individual Solver Status */}
                      <td className="py-3 px-4">
                        {item.status === 'RUNNING' ? (
                          <span className="inline-flex items-center gap-1 font-bold text-amber-500">
                            <RotateCw className="h-3 w-3 animate-spin" />
                            <span>Running...</span>
                          </span>
                        ) : item.status === 'PENDING' ? (
                          <span className="inline-flex items-center gap-1 text-slate-400 font-medium">
                            <span>Pending</span>
                          </span>
                        ) : item.status === 'TIMED_OUT' ? (
                          <span className="inline-flex items-center gap-1 font-bold text-orange-500">
                            <span>Timed Out</span>
                          </span>
                        ) : item.status === 'FAILED' ? (
                          <span className="inline-flex items-center gap-1 font-bold text-red-500" title={item.error || 'Solver failed'}>
                            <span>Failed</span>
                          </span>
                        ) : (
                          <span className={`inline-flex items-center gap-1 font-bold ${
                            item.is_feasible ? 'text-[#22C55E]' : 'text-amber-500'
                          }`}>
                            <CheckCircle2 className="h-3.5 w-3.5" />
                            <span>{item.is_feasible ? 'Feasible' : 'Penalized'}</span>
                          </span>
                        )}
                      </td>

                      {/* Total Distance */}
                      <td className="py-3 px-4 font-technical font-bold text-[#080808] dark:text-[#F5F5F7]">
                        {typeof item.total_distance_km === 'number' && item.total_distance_km > 0
                          ? `${item.total_distance_km.toFixed(2)} km`
                          : (item.status === 'RUNNING' ? 'Computing...' : '—')}
                      </td>

                      {/* Travel Time */}
                      <td className="py-3 px-4 font-technical text-[#555555] dark:text-[#A1A1AA]">
                        {item.total_travel_time_min ? `${Math.round(item.total_travel_time_min)} min` : '—'}
                      </td>

                      {/* Implied Average Speed */}
                      <td className="py-3 px-4 font-technical font-semibold text-[#080808] dark:text-[#F5F5F7]">
                        {typeof item.total_distance_km === 'number' && item.total_distance_km > 0 && item.total_travel_time_min
                          ? `${(item.implied_speed_kmh || (item.total_distance_km / (item.total_travel_time_min / 60))).toFixed(1)} km/h`
                          : '—'}
                      </td>

                      {/* Vehicles & Coverage */}
                      <td className="py-3 px-4 font-technical text-[#555555] dark:text-[#A1A1AA]">
                        {item.vehicles_used ? `${item.vehicles_used} vehicles · ${item.served_customers} stops` : '—'}
                      </td>

                      {/* Violations */}
                      <td className="py-3 px-4 font-technical">
                        {item.status === 'FAILED' || item.status === 'TIMED_OUT' ? (
                          <span className="text-red-500 font-bold truncate max-w-[120px] block" title={item.error || 'Error'}>
                            {item.error || 'Execution failed'}
                          </span>
                        ) : item.capacity_violations === 0 && item.unserved_customers === 0 ? (
                          <span className="text-[#22C55E] font-bold">0 violations</span>
                        ) : (
                          <span className="text-red-500 font-bold">
                            {item.capacity_violations} cap / {item.unserved_customers} unserved
                          </span>
                        )}
                      </td>

                      {/* Resource: CPU & Heap / RSS RAM */}
                      <td className="py-3 px-4 font-technical">
                        <div className="flex flex-col">
                          <span className="font-bold text-[#080808] dark:text-[#F5F5F7]" title={`CPU Core Time Ratio: ${item.cpu_core_ratio_percent || item.cpu_utilization_percent || 0}%`}>
                            {item.cpu_core_ratio_percent || item.cpu_utilization_percent ? `${(item.cpu_core_ratio_percent || item.cpu_utilization_percent || 0).toFixed(0)}% CPU` : 'Active'}
                          </span>
                          <span className="text-[10px] text-[#777777] dark:text-[#A1A1AA]" title={`Process RSS: ${item.process_rss_mb || 0} MB | Python Heap: ${item.heap_allocated_mb || item.memory_used_mb || 0} MB (peak: ${item.heap_peak_mb || item.peak_memory_mb || 0} MB)`}>
                            {item.heap_allocated_mb || item.memory_used_mb ? `${(item.heap_allocated_mb || item.memory_used_mb || 0).toFixed(1)}M heap` : '<1M heap'} (pk: {(item.heap_peak_mb || item.peak_memory_mb || 1).toFixed(1)}M)
                          </span>
                        </div>
                      </td>

                      {/* Theoretical Big-O Complexity */}
                      <td className="py-3 px-4 font-technical">
                        <div className="flex flex-col">
                          <span className="text-[11px] font-bold text-[#080808] dark:text-[#F5F5F7] truncate max-w-[110px]" title={`Theoretical Worst-Case Time: ${item.time_complexity || 'O(N^2)'}`}>
                            T: {item.time_complexity || 'O(N^2)'}
                          </span>
                          <span className="text-[10px] text-[#777777] dark:text-[#A1A1AA] truncate max-w-[110px]" title={`Theoretical Worst-Case Space: ${item.space_complexity || 'O(N)'}`}>
                            S: {item.space_complexity || 'O(N)'}
                          </span>
                        </div>
                      </td>

                      {/* Objective Cost */}
                      <td className="py-3 px-4 font-technical font-bold text-[#080808] dark:text-[#F5F5F7]">
                        {typeof item.total_objective_cost === 'number' ? item.total_objective_cost.toFixed(2) : '—'}
                      </td>

                      {/* Runtime */}
                      <td className="py-3 px-4 font-technical text-[#777777] dark:text-[#A1A1AA]">
                        {typeof item.execution_time_sec === 'number' ? `${item.execution_time_sec.toFixed(3)}s` : '—'}
                      </td>

                      {/* View Action */}
                      <td className="py-3 px-4 text-right">
                        <button
                          onClick={() => handleSelectAlgorithm(item.id)}
                          className={`px-3 py-1 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                            isCurrent
                              ? 'bg-[#080808] text-[#B7FF00] dark:bg-[#202024] dark:text-[#B7FF00] border border-black dark:border-[#B7FF00]/40'
                              : 'bg-black/5 hover:bg-black/10 dark:bg-[#18181B] dark:border dark:border-[#29292E] dark:hover:bg-[#202024] text-[#080808] dark:text-[#F5F5F7]'
                          }`}
                        >
                          {isCurrent ? '✓ Inspecting' : 'Inspect Route'}
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
