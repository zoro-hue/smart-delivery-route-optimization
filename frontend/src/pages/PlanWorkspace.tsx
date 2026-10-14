import React, { useState, useEffect } from 'react';
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Polyline,
  useMapEvents,
  useMap,
  ZoomControl,
} from 'react-leaflet';
import L from 'leaflet';
import {
  Play,
  RotateCw,
  Plus,
  Trash2,
  MapPin,
  Crosshair,
  ChevronDown,
  ChevronUp,
  ChevronLeft,
  CheckCircle2,
  AlertTriangle,
  Layers,
  Edit3,
  X,
  Check,
  CheckSquare,
  Square,
  Activity,
  Compass,
  Sliders,
  Sparkles,
  Cpu,
  GitCompare,
  ArrowRight,
  Maximize2,
  Minimize2,
} from 'lucide-react';
import { OptimizationResponse, VehicleRoute } from '../types';
import { api } from '../services/api';
import { useSettings } from '../context/SettingsContext';
import { useTheme } from '../context/ThemeContext';
import { validateDeliveryCoordinate } from '../utils/geoValidation';

export interface AlgorithmConfigItem {
  id: string;
  name: string;
  group: 'classical' | 'quantum';
  groupLabel: string;
  role: string;
  badge: string;
  computeType: string;
  maxLimit?: number;
}

export const WORKSPACE_ALGORITHMS: AlgorithmConfigItem[] = [
  // Classical algorithms
  {
    id: 'dijkstra',
    name: 'Dijkstra',
    group: 'classical',
    groupLabel: 'Classical algorithms',
    role: 'Shortest-path baseline.',
    badge: 'Shortest-Path Baseline',
    computeType: 'Classical CPU',
  },
  {
    id: 'astar',
    name: 'A*',
    group: 'classical',
    groupLabel: 'Classical algorithms',
    role: 'Heuristic-based shortest-path search.',
    badge: 'Heuristic Search',
    computeType: 'Classical CPU',
  },
  {
    id: 'ortools',
    name: 'OR-Tools',
    group: 'classical',
    groupLabel: 'Classical algorithms',
    role: 'Classical vehicle routing optimization, using the configured routing solver.',
    badge: 'Primary VRP Optimizer',
    computeType: 'Classical CPU',
  },
  {
    id: 'clarke_wright',
    name: 'Clarke–Wright Savings',
    group: 'classical',
    groupLabel: 'Classical algorithms',
    role: 'Route construction heuristic.',
    badge: 'Construction Heuristic',
    computeType: 'Classical CPU',
  },
  {
    id: 'two_opt',
    name: '2-opt',
    group: 'classical',
    groupLabel: 'Classical algorithms',
    role: 'Route improvement heuristic.',
    badge: 'Route Improvement',
    computeType: 'Classical CPU',
  },
  // Quantum / quantum-classical algorithms
  {
    id: 'qaoa',
    name: 'QAOA',
    group: 'quantum',
    groupLabel: 'Quantum / quantum-classical algorithms',
    role: 'Hybrid quantum-classical optimization for supported, appropriately formulated routing instances.',
    badge: 'Hybrid Variational · Qiskit Simulator',
    computeType: 'Classical Statevector Simulator',
    maxLimit: 8,
  },
  {
    id: 'qiga',
    name: 'Quantum-Inspired Genetic Algorithm (QIGA/IQGA)',
    group: 'quantum',
    groupLabel: 'Quantum / quantum-classical algorithms',
    role: 'Quantum-inspired evolutionary optimization, simulated classically.',
    badge: 'Quantum-Inspired Evolutionary',
    computeType: 'Classically Simulated Q-Bit Amplitudes',
    maxLimit: 50,
  },
];

// ─── LEAFLET PIN FACTORIES (THEME-AWARE) ───────────────────────────────────
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

const createCustomerIcon = (index: number, isDark: boolean) =>
  L.divIcon({
    className: 'custom-map-pin-customer',
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

// Theme-tailored vibrant route palette: electric high-contrast neon in dark mode, crisp modern in light mode
const LIGHT_ROUTE_COLORS = ['#080808', '#0284C7', '#7C3AED', '#EA580C', '#059669', '#DB2777'];
const DARK_ROUTE_COLORS = ['#B7FF2A', '#00E5FF', '#FF6B00', '#E040FB', '#38BDF8', '#FACC15'];

export interface DeliveryStop {
  id: string;
  customer_id?: string;
  name: string;
  lat: number;
  lon: number;
  demand: number;
  service_time_min?: number;
  address?: string;
  status?: string;
  is_included: boolean;
}

export interface DiagnosticsData {
  total_dataset_rows: number;
  valid_coordinate_rows: number;
  duplicate_coordinates: number;
  invalid_coordinate_rows: number;
  source?: string;
}

interface PlanWorkspaceProps {
  onOptimizationComplete: (response: OptimizationResponse) => void;
  onNavigateToResults: () => void;
  lastResult: OptimizationResponse | null;
  isActive?: boolean;
}

// ─── MAP EVENT & FRAMING HELPERS ──────────────────────────────────────────

function MapClickHandler({
  mode,
  onSetDepot,
  onAddStop,
}: {
  mode: 'depot' | 'stop' | 'none';
  onSetDepot: (lat: number, lon: number) => void;
  onAddStop: (lat: number, lon: number) => void;
}) {
  useMapEvents({
    click(e) {
      if (mode === 'depot') {
        onSetDepot(e.latlng.lat, e.latlng.lng);
      } else if (mode === 'stop') {
        onAddStop(e.latlng.lat, e.latlng.lng);
      }
    },
  });
  return null;
}

function MapAutoFramer({
  depot,
  stops,
  isActive,
}: {
  depot: { lat: number; lon: number };
  stops: DeliveryStop[];
  isActive?: boolean;
}) {
  const map = useMap();

  useEffect(() => {
    if (isActive !== false) {
      const timer = setTimeout(() => {
        try {
          map.invalidateSize();
        } catch {}
      }, 80);
      return () => clearTimeout(timer);
    }
  }, [isActive, map]);

  useEffect(() => {
    try {
      const validDepotLat = !isNaN(depot?.lat) ? depot.lat : 40.7580;
      const validDepotLon = !isNaN(depot?.lon) ? depot.lon : -73.8292;
      const coords: [number, number][] = [
        [validDepotLat, validDepotLon],
        ...stops
          .filter((s) => !isNaN(s.lat) && !isNaN(s.lon))
          .map((s) => [s.lat, s.lon] as [number, number]),
      ];

      if (coords.length === 1) {
        map.setView(coords[0], 13, { animate: true });
      } else if (coords.length >= 2) {
        const bounds = L.latLngBounds(coords);
        if (bounds.isValid()) {
          map.fitBounds(bounds, { padding: [70, 70], maxZoom: 14, animate: true });
        }
      }
    } catch (e) {
      console.warn('MapAutoFramer error:', e);
    }
  }, [depot.lat, depot.lon, stops, map]);

  return null;
}

// Watches sidebar toggle and transitions to ensure Leaflet invalidates tile sizes smoothly
function MapResizeWatcher({
  sidebarOpen,
  isActive,
}: {
  sidebarOpen: boolean;
  isActive?: boolean;
}) {
  const map = useMap();

  useEffect(() => {
    const timer1 = setTimeout(() => {
      try {
        map.invalidateSize();
      } catch {}
    }, 150);
    const timer2 = setTimeout(() => {
      try {
        map.invalidateSize();
      } catch {}
    }, 350);
    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
    };
  }, [sidebarOpen, isActive, map]);

  return null;
}

// ─── PLAN WORKSPACE MAIN COMPONENT ────────────────────────────────────────
export const PlanWorkspace: React.FC<PlanWorkspaceProps> = ({
  onOptimizationComplete,
  onNavigateToResults,
  lastResult,
  isActive,
}) => {
  const { settings, updateSettings } = useSettings();
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  const activeRouteColors = isDark ? DARK_ROUTE_COLORS : LIGHT_ROUTE_COLORS;

  // Collapsible Sidebar State (Full-size dominant map workspace)
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(() => {
    return window.innerWidth >= 1024;
  });

  // Configurable Depot
  const [depot, setDepot] = useState<{ lat: number; lon: number; name: string }>(() => {
    const parsedLat = parseFloat(settings.depotLat);
    const parsedLon = parseFloat(settings.depotLon);
    const savedLat = !isNaN(parsedLat) ? parsedLat : 40.7580;
    const savedLon = !isNaN(parsedLon) ? parsedLon : -73.8292;
    const savedName = settings.depotName || 'Flushing Logistics Hub';
    return { lat: savedLat, lon: savedLon, name: savedName };
  });

  // Manual Depot Edit Modal State
  const [isEditingDepot, setIsEditingDepot] = useState<boolean>(false);
  const [manualDepotLat, setManualDepotLat] = useState<string>(depot.lat.toString());
  const [manualDepotLon, setManualDepotLon] = useState<string>(depot.lon.toString());
  const [manualDepotName, setManualDepotName] = useState<string>(depot.name);
  const [depotEditError, setDepotEditError] = useState<string | null>(null);

  const [clickMode, setClickMode] = useState<'depot' | 'stop' | 'none'>('none');

  // Delivery Stops State
  const [stops, setStops] = useState<DeliveryStop[]>(() => {
    try {
      const saved = localStorage.getItem('routeiq_workspace_stops');
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) {
          const validOnly = parsed.filter(
            (s: DeliveryStop) => validateDeliveryCoordinate(s.lat, s.lon).isValid
          );
          if (validOnly.length > 0) return validOnly;
        }
      }
    } catch {}
    return [];
  });
  const [isLoadingStops, setIsLoadingStops] = useState<boolean>(false);
  const [feedbackMessage, setFeedbackMessage] = useState<string | null>(null);

  // Diagnostics State
  const [diagnostics, setDiagnostics] = useState<DiagnosticsData>({
    total_dataset_rows: 1898,
    valid_coordinate_rows: 25,
    duplicate_coordinates: 0,
    invalid_coordinate_rows: 0,
    source: 'NYC Ingested Fleet & Physical Facilities',
  });

  // Stored routes from optimization
  const [activeRoutes, setActiveRoutes] = useState<VehicleRoute[]>(() => {
    try {
      const saved = localStorage.getItem('routeiq_workspace_routes');
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) return parsed;
      }
    } catch {}
    return [];
  });

  useEffect(() => {
    if (stops.length > 0) {
      try {
        localStorage.setItem('routeiq_workspace_stops', JSON.stringify(stops));
      } catch {}
    }
  }, [stops]);

  useEffect(() => {
    try {
      localStorage.setItem('routeiq_workspace_routes', JSON.stringify(activeRoutes));
    } catch {}
  }, [activeRoutes]);

  // Fleet & Constraints
  const [numVehicles, setNumVehicles] = useState<number>(settings.defaultVehicles);
  const [vehicleCapacity, setVehicleCapacity] = useState<number>(settings.defaultCapacity);

  // Algorithm Selection State
  const [selectionMode, setSelectionMode] = useState<'recommended' | 'custom' | 'compare'>(() => {
    return (localStorage.getItem('routeiq_selection_mode') as any) || 'recommended';
  });

  const [selectedAlgorithms, setSelectedAlgorithms] = useState<string[]>(() => {
    try {
      const saved = localStorage.getItem('routeiq_selected_algorithms');
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) return parsed;
      }
    } catch {}
    return ['ortools'];
  });

  const [displayedAlgo, setDisplayedAlgo] = useState<string>('ortools');
  const [executionResponse, setExecutionResponse] = useState<OptimizationResponse | null>(lastResult);

  const [algorithm, setAlgorithm] = useState<string>(() => {
    return localStorage.getItem('routeiq_algorithm') || 'classical';
  });
  const [trafficScenario, setTrafficScenario] = useState<string>('normal');

  // Advanced Solver & QAOA Options
  const [showAdvanced, setShowAdvanced] = useState<boolean>(false);
  const [qaoaDepth, setQaoaDepth] = useState<number>(settings.qaoaDepth);
  const [qaoaShots, setQaoaShots] = useState<number>(() => {
    return parseInt(localStorage.getItem('routeiq_qaoa_shots') || '1024', 10);
  });
  const [weightDistance, setWeightDistance] = useState<number>(settings.weightDistance);
  const [weightTime, setWeightTime] = useState<number>(settings.weightTime);

  useEffect(() => {
    localStorage.setItem('routeiq_algorithm', algorithm);
    localStorage.setItem('routeiq_selection_mode', selectionMode);
    localStorage.setItem('routeiq_selected_algorithms', JSON.stringify(selectedAlgorithms));
  }, [algorithm, selectionMode, selectedAlgorithms]);

  const handleToggleAlgorithm = (algoId: string) => {
    setSelectedAlgorithms((prev) => {
      let next: string[];
      if (prev.includes(algoId)) {
        if (prev.length === 1) return prev;
        next = prev.filter((id) => id !== algoId);
      } else {
        next = [...prev, algoId];
      }
      localStorage.setItem('routeiq_selected_algorithms', JSON.stringify(next));
      return next;
    });
  };

  useEffect(() => {
    setNumVehicles(settings.defaultVehicles);
    setVehicleCapacity(settings.defaultCapacity);
    const dLat = parseFloat(settings.depotLat);
    const dLon = parseFloat(settings.depotLon);
    if (!isNaN(dLat) && !isNaN(dLon)) {
      setDepot({ lat: dLat, lon: dLon, name: settings.depotName || 'Main NYC Logistics Hub' });
      setManualDepotLat(dLat.toString());
      setManualDepotLon(dLon.toString());
      setManualDepotName(settings.depotName || 'Main NYC Logistics Hub');
    }
    setNumVehicles(settings.defaultVehicles);
    setVehicleCapacity(settings.defaultCapacity);
    setQaoaDepth(settings.qaoaDepth);
    setWeightDistance(settings.weightDistance);
    setWeightTime(settings.weightTime);
  }, [settings]);

  // Execution State
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [validationError, setValidationError] = useState<string | null>(null);

  useEffect(() => {
    if (stops.length === 0) {
      loadStops();
    }
  }, []);

  useEffect(() => {
    if (lastResult?.results) {
      const best = lastResult.best_feasible_algorithm || lastResult.primary_algorithm;
      const routes =
        (best && lastResult.results[best]?.routes) ||
        lastResult.results.ortools?.routes ||
        lastResult.results.classical?.routes ||
        lastResult.results.qaoa?.routes ||
        Object.values(lastResult.results).find((r: any) => r.routes?.length > 0)?.routes ||
        [];
      if (routes.length > 0) {
        setActiveRoutes(routes);
      }
      if (best) {
        setDisplayedAlgo(best);
      }
      setExecutionResponse(lastResult);
    }
  }, [lastResult]);

  // Read customer and delivery coordinates from ingested data with geo/water validation
  const loadStops = async () => {
    setIsLoadingStops(true);
    setValidationError(null);
    try {
      const data = await api.getDeliveryStops(25);
      if (data?.stops) {
        const seen = new Set<string>();
        let dupes = 0;
        let invalids = 0;

        const parsedStops: DeliveryStop[] = [];

        data.stops.forEach((s: any, idx: number) => {
          let lat = Number(s.lat);
          let lon = Number(s.lon);

          if (lat < 0 && lon > 0) {
            const temp = lat;
            lat = lon;
            lon = temp;
          }

          // Geospatial validation against bounds and open water
          const geoCheck = validateDeliveryCoordinate(lat, lon);
          if (!geoCheck.isValid) {
            invalids++;
            return;
          }

          const key = `${lat.toFixed(4)},${lon.toFixed(4)}`;
          if (seen.has(key)) {
            dupes++;
          } else {
            seen.add(key);
          }

          parsedStops.push({
            id: s.id || `ORD-${1000 + idx}`,
            customer_id: s.customer_id || `CUST-${idx + 1}`,
            name: s.name || `Delivery Stop #${idx + 1}`,
            lat: parseFloat(lat.toFixed(6)),
            lon: parseFloat(lon.toFixed(6)),
            demand: Number(s.demand) > 0 ? Number(s.demand) : 10,
            service_time_min: s.service_time_min || 12,
            address: s.address || `NYC Delivery Sector #${100 + idx}`,
            status: 'valid',
            is_included: true,
          });
        });

        setStops(parsedStops);
        setActiveRoutes([]);

        if (data.diagnostics) {
          setDiagnostics({
            total_dataset_rows: data.diagnostics.total_dataset_rows || 1898,
            valid_coordinate_rows: parsedStops.length,
            duplicate_coordinates: dupes,
            invalid_coordinate_rows: invalids,
            source: data.diagnostics.source || 'NYC Ingested Fleet & Physical Facilities',
          });
        }

        setFeedbackMessage(`Loaded ${parsedStops.length} stops from ingested dataset.`);
        setTimeout(() => setFeedbackMessage(null), 3000);
      }
    } catch (err: any) {
      console.error('Failed to load stops:', err);
      setValidationError(`Failed to load stops from backend: ${err.message}`);
    } finally {
      setIsLoadingStops(false);
    }
  };

  // ─── DEPOT MANAGEMENT WITH WATER VALIDATION ────────────────────────────
  const handleSetDepotCoords = (lat: number, lon: number, name?: string) => {
    if (lat < 0 && lon > 0) {
      const temp = lat;
      lat = lon;
      lon = temp;
    }

    // Verify coordinate is not in water body
    const geoCheck = validateDeliveryCoordinate(lat, lon);
    if (!geoCheck.isValid) {
      const msg = geoCheck.error || 'Cannot place depot in water body.';
      setDepotEditError(msg);
      setValidationError(msg);
      return;
    }

    const updated = {
      lat: parseFloat(lat.toFixed(6)),
      lon: parseFloat(lon.toFixed(6)),
      name: name || `Origin Depot (${lat.toFixed(3)}, ${lon.toFixed(3)})`,
    };

    setDepot(updated);
    setManualDepotLat(updated.lat.toString());
    setManualDepotLon(updated.lon.toString());
    setManualDepotName(updated.name);
    setDepotEditError(null);

    updateSettings({
      depotLat: updated.lat.toString(),
      depotLon: updated.lon.toString(),
      depotName: updated.name,
    });

    setActiveRoutes([]);
    setClickMode('none');
    setIsEditingDepot(false);
    setFeedbackMessage(`Origin depot moved to ${updated.name}`);
    setTimeout(() => setFeedbackMessage(null), 3000);
  };

  const handleDeviceLocation = () => {
    if (!navigator.geolocation) {
      alert('Browser geolocation is not available.');
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        handleSetDepotCoords(
          pos.coords.latitude,
          pos.coords.longitude,
          'Current Device Location'
        );
      },
      (err) => alert(`Geolocation permission denied: ${err.message}`)
    );
  };

  const handleSaveManualDepot = () => {
    setDepotEditError(null);
    const lat = parseFloat(manualDepotLat);
    const lon = parseFloat(manualDepotLon);

    const geoCheck = validateDeliveryCoordinate(lat, lon);
    if (!geoCheck.isValid) {
      setDepotEditError(geoCheck.error || 'Coordinates fall in a water body or outside service area.');
      return;
    }

    handleSetDepotCoords(lat, lon, manualDepotName || 'Custom Logistics Depot');
  };

  // ─── STOP MANAGEMENT WITH WATER BODY VALIDATION ────────────────────────
  const handleAddStopFromMap = (lat: number, lon: number) => {
    // Check if clicked location is in open water (Hudson River, East River, Atlantic Ocean, etc.)
    const geoCheck = validateDeliveryCoordinate(lat, lon);
    if (!geoCheck.isValid) {
      setValidationError(
        geoCheck.error || 'Cannot place delivery stop in open water. Vehicles require road addresses.'
      );
      setClickMode('none');
      return;
    }

    const newStop: DeliveryStop = {
      id: `MAP-${Date.now().toString().slice(-4)}`,
      customer_id: `CUST-${stops.length + 1}`,
      name: `Customer Stop #${stops.length + 1}`,
      lat: parseFloat(lat.toFixed(6)),
      lon: parseFloat(lon.toFixed(6)),
      demand: 12,
      is_included: true,
    };
    setStops((prev) => [newStop, ...prev]);
    setActiveRoutes([]);
    setClickMode('none');
    setValidationError(null);
    setFeedbackMessage(`Added stop #${stops.length + 1} at [${lat.toFixed(4)}, ${lon.toFixed(4)}]`);
    setTimeout(() => setFeedbackMessage(null), 3000);
  };

  const handleToggleStop = (id: string) => {
    setStops((prev) =>
      prev.map((s) => (s.id === id ? { ...s, is_included: !s.is_included } : s))
    );
    setActiveRoutes([]);
  };

  const handleSelectAll = (select: boolean) => {
    setStops((prev) => prev.map((s) => ({ ...s, is_included: select })));
    setActiveRoutes([]);
  };

  const handleRemoveStop = (id: string) => {
    setStops((prev) => prev.filter((s) => s.id !== id));
    setActiveRoutes([]);
  };

  const handleResetStops = () => {
    loadStops();
  };

  const handleDemandChange = (id: string, demand: number) => {
    setStops((prev) =>
      prev.map((s) => (s.id === id ? { ...s, demand: Math.max(1, demand) } : s))
    );
    setActiveRoutes([]);
  };

  const activeStops = stops.filter((s) => s.is_included);

  // ─── OPTIMIZATION EXECUTION ──────────────────────────────────────────────
  const handleRunOptimization = async () => {
    setValidationError(null);

    if (activeStops.length < 1) {
      setValidationError('Please select at least 1 delivery stop before optimizing routes.');
      return;
    }

    // 1. Validate Origin Depot is not in a water body
    const depotCheck = validateDeliveryCoordinate(depot.lat, depot.lon);
    if (!depotCheck.isValid) {
      setValidationError(
        `Origin Depot Hub cannot be located in open water (${depotCheck.waterBodyName || 'water'}). Delivery dispatch hubs must be located on navigable roadways.`
      );
      return;
    }

    // 2. Validate all active stops are not in a water body
    for (let i = 0; i < activeStops.length; i++) {
      const s = activeStops[i];
      const stopCheck = validateDeliveryCoordinate(s.lat, s.lon);
      if (!stopCheck.isValid) {
        setValidationError(
          `Stop #${i + 1} (${s.name}) is located in open water (${stopCheck.waterBodyName || 'water'}). Road couriers cannot reach water body coordinates. Please relocate or exclude this stop.`
        );
        return;
      }
    }

    setIsRunning(true);
    try {
      const algosToRun =
        selectionMode === 'recommended'
          ? ['ortools']
          : selectionMode === 'compare'
          ? (selectedAlgorithms.length >= 2
              ? selectedAlgorithms
              : (activeStops.length <= 8
                  ? ['ortools', 'clarke_wright', 'two_opt', 'qiga', 'qaoa']
                  : ['ortools', 'clarke_wright', 'two_opt', 'dijkstra', 'astar', 'qiga']))
          : selectedAlgorithms.length > 0
          ? selectedAlgorithms
          : ['ortools'];

      const payload = {
        algorithm,
        selection_mode: selectionMode,
        selected_algorithms: algosToRun,
        num_customers: activeStops.length,
        num_vehicles: Number(numVehicles),
        vehicle_capacity: Number(vehicleCapacity),
        depot_lat: depot.lat,
        depot_lon: depot.lon,
        weight_distance: Number(weightDistance),
        weight_travel_time: Number(weightTime),
        traffic_scenario: trafficScenario,
        classical_time_limit_sec: 4,
        qaoa_depth: Number(qaoaDepth),
        qaoa_shots: Number(qaoaShots),
        custom_customers: activeStops.map((s) => ({
          id: s.id,
          customer_id: s.customer_id,
          name: s.name,
          lat: s.lat,
          lon: s.lon,
          demand: s.demand,
          address: s.address,
        })),
      };

      const res = await api.runOptimization(payload);
      setExecutionResponse(res);

      const bestAlgo =
        res?.best_feasible_algorithm || res?.primary_algorithm || algosToRun[0] || 'ortools';
      setDisplayedAlgo(bestAlgo);

      const computed =
        res?.results?.[bestAlgo]?.routes ||
        res?.results?.ortools?.routes ||
        res?.results?.classical?.routes ||
        (res?.results && Object.values(res.results).find((r: any) => r.routes?.length > 0)?.routes) || [];
      setActiveRoutes(computed);

      onOptimizationComplete(res);
      setFeedbackMessage(
        selectionMode === 'compare'
          ? `Comparative benchmark finished (${res?.comparison_summary?.items?.length || algosToRun.length} solvers). Best: ${res?.comparison_summary?.best_algorithm_name || bestAlgo}.`
          : `Optimization complete via ${res?.results?.[bestAlgo]?.algorithm_name || bestAlgo.toUpperCase()}!`
      );
      setTimeout(() => setFeedbackMessage(null), 5000);
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Optimization request failed';
      setValidationError(`Optimization failed: ${msg}`);
      setTimeout(() => {
        setValidationError((prev) => (prev?.includes(msg) ? null : prev));
      }, 10000);
    } finally {
      setIsRunning(false);
    }
  };

  const safeDepotLat = !isNaN(depot?.lat) ? depot.lat : 40.7580;
  const safeDepotLon = !isNaN(depot?.lon) ? depot.lon : -73.8292;

  return (
    <div className="relative w-full h-full overflow-hidden select-none bg-[#F4F4F2] dark:bg-[#09090B]">
      {/* ─── FULL-SIZE DOMINANT LEAFLET MAP WORKSPACE ─────────────────── */}
      <div className="absolute inset-0 w-full h-full z-0">
        <MapContainer
          center={[safeDepotLat, safeDepotLon]}
          zoom={12}
          zoomControl={false}
          scrollWheelZoom={true}
          style={{ height: '100%', width: '100%' }}
          className="h-full w-full"
        >
          {/* Zoom controls positioned top-right so they never collide with the left sidebar */}
          <ZoomControl position="topright" />

          {/* Standard OpenStreetMap tiles (free, keyless, with CSS tile-pane dark mode in dark mode) */}
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {/* Automatic map framing on depot and active stops */}
          <MapAutoFramer depot={depot} stops={activeStops} isActive={isActive} />

          {/* Resize watcher ensuring smooth invalidation on sidebar toggle */}
          <MapResizeWatcher sidebarOpen={sidebarOpen} isActive={isActive} />

          {/* Map click handler for placing depot or adding stops */}
          <MapClickHandler
            mode={clickMode}
            onSetDepot={handleSetDepotCoords}
            onAddStop={handleAddStopFromMap}
          />

          {/* Origin Depot Pin (Lime-Green 'D' marker) */}
          <Marker position={[depot.lat, depot.lon]} icon={getDepotIcon(isDark)}>
            <Popup>
              <div className="text-xs font-sans space-y-1">
                <div className="flex items-center gap-1.5">
                  <span className="h-2 w-2 rounded-full bg-[#B7FF2A] ring-1 ring-black" />
                  <strong className="text-[#080808] dark:text-white font-bold">Origin Depot Hub</strong>
                </div>
                <p className="font-semibold text-[#171717] dark:text-[#E4E4E7]">{depot.name}</p>
                <p className="font-technical text-[10px] text-[#777777] dark:text-[#A1A1AA]">
                  {depot.lat.toFixed(6)}, {depot.lon.toFixed(6)}
                </p>
                <span className="inline-block text-[10px] px-2 py-0.5 rounded-full bg-black text-[#B7FF2A] font-bold">
                  Route Dispatch Facility
                </span>
              </div>
            </Popup>
          </Marker>

          {/* Delivery Customer Markers */}
          {activeStops.map((stop, idx) => (
            <Marker
              key={stop.id}
              position={[stop.lat, stop.lon]}
              icon={createCustomerIcon(idx + 1, isDark)}
            >
              <Popup>
                <div className="text-xs font-sans space-y-1 p-0.5">
                  <div className="flex items-center justify-between gap-2 border-b border-black/10 dark:border-white/10 pb-1">
                    <strong className="text-[#080808] dark:text-white font-bold">
                      Stop #{idx + 1}: {stop.customer_id || stop.id}
                    </strong>
                    <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-black/5 dark:bg-white/10 text-[#777777] dark:text-[#A1A1AA]">
                      ORD: {stop.id}
                    </span>
                  </div>
                  <p className="font-semibold text-[#080808] dark:text-[#E4E4E7]">{stop.name}</p>
                  <p className="text-[11px] text-[#777777] dark:text-[#A1A1AA]">{stop.address}</p>
                  <div className="flex items-center justify-between text-[11px] pt-1">
                    <span className="font-technical text-[#777777] dark:text-[#A1A1AA]">
                      {stop.lat.toFixed(4)}, {stop.lon.toFixed(4)}
                    </span>
                    <span className="font-bold text-[#080808] dark:text-white px-2 py-0.5 rounded-full bg-[#B7FF2A]/20 text-[#080808] dark:text-[#B7FF2A]">
                      Demand: {stop.demand} units
                    </span>
                  </div>
                  <button
                    onClick={() => handleToggleStop(stop.id)}
                    className="w-full mt-2 py-1 rounded-lg text-[10px] font-bold bg-black/5 dark:bg-white/10 hover:bg-black/10 dark:hover:bg-white/20 text-red-600 dark:text-red-400 transition-colors cursor-pointer"
                  >
                    Exclude this stop
                  </button>
                </div>
              </Popup>
            </Marker>
          ))}

          {/* Computed Routes Polylines */}
          {activeRoutes.map((route, idx) => {
            const color = activeRouteColors[idx % activeRouteColors.length];
            const positions: [number, number][] = (route.waypoints || []).map((w) => [
              w.lat,
              w.lon,
            ]);

            if (positions.length < 2) return null;

            return (
              <Polyline
                key={idx}
                positions={positions}
                pathOptions={{
                  color,
                  weight: 4.5,
                  opacity: 0.95,
                  dashArray: idx % 2 === 1 ? '6, 6' : undefined,
                }}
              />
            );
          })}
        </MapContainer>
      </div>

      {/* ─── FLOATING TOP-CENTER WORKSPACE TOOLBAR ────────────────── */}
      <div className="absolute top-3 left-1/2 -translate-x-1/2 z-[1000] flex items-center gap-2 max-w-[calc(100vw-2rem)] flex-wrap justify-center pointer-events-auto transition-all duration-300 ease-out">
        {/* Contextual Primary Action: Run Optimization / Compare */}
        <button
          onClick={handleRunOptimization}
          disabled={isRunning || activeStops.length < 1}
          className="flex items-center gap-2 px-5 py-2.5 bg-[#080808] hover:bg-[#171717] dark:bg-[#B7FF2A] dark:hover:bg-[#a4f01d] text-[#B7FF2A] dark:text-[#080808] rounded-full text-xs font-heading font-bold shadow-xl transition-all cursor-pointer disabled:opacity-40 border border-[#B7FF2A]/20"
        >
          {isRunning ? (
            <>
              <RotateCw className="h-3.5 w-3.5 animate-spin text-[#B7FF2A] dark:text-[#080808]" />
              <span>Computing Solution...</span>
            </>
          ) : (
            <>
              <Play className="h-3.5 w-3.5 fill-current" />
              <span>
                {selectionMode === 'recommended'
                  ? `Run Optimization (${activeStops.length} Stops)`
                  : selectionMode === 'compare'
                  ? `Compare (${selectedAlgorithms.length} Solvers · ${activeStops.length} Stops)`
                  : `Run Optimization (${selectedAlgorithms.length} Algos · ${activeStops.length} Stops)`}
              </span>
            </>
          )}
        </button>

        {/* View in Results CTA when solution has been computed */}
        {executionResponse && !isRunning && (
          <button
            onClick={onNavigateToResults}
            className="flex items-center gap-1.5 px-4 py-2.5 bg-[#B7FF2A] hover:bg-[#a4f01d] text-black dark:text-black dark:!text-black rounded-full text-xs font-heading font-bold shadow-xl transition-all cursor-pointer border border-black/10"
            style={{ color: '#080808' }}
            title="Inspect computed solution in the Results tab"
          >
            <span className="text-black dark:text-black dark:!text-black" style={{ color: '#080808' }}>
              View Solution in Results
            </span>
            <ArrowRight className="h-3.5 w-3.5 text-black dark:text-black dark:!text-black" style={{ color: '#080808' }} />
          </button>
        )}

        {/* Reset Stops button */}
        <button
          onClick={loadStops}
          disabled={isLoadingStops}
          className="flex items-center gap-1.5 px-3.5 py-2.5 bg-white/70 dark:bg-[#18181B]/70 hover:bg-white text-[#171717] dark:text-[#F4F4F5] rounded-full text-xs font-heading font-semibold shadow-lg backdrop-blur-2xl border border-white/80 dark:border-white/10 transition-all cursor-pointer disabled:opacity-50"
          title="Reset delivery stops to default ingested dataset"
        >
          <RotateCw className={`h-3.5 w-3.5 ${isLoadingStops ? 'animate-spin text-[#22C55E]' : ''}`} />
          <span className="hidden sm:inline">Reset Stops</span>
        </button>

        {/* Comparison Route Switcher Toolbar */}
        {executionResponse?.comparison_summary && executionResponse.comparison_summary.items.length > 1 && (
          <div className="flex items-center gap-1 p-1 rounded-full bg-white/70 dark:bg-[#18181B]/70 backdrop-blur-2xl border border-white/80 dark:border-white/10 shadow-lg">
            {executionResponse.comparison_summary.items.map((item) => {
              const isSelected = displayedAlgo === item.id;
              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => {
                    setDisplayedAlgo(item.id);
                    const r = executionResponse.results[item.id]?.routes || [];
                    setActiveRoutes(r);
                  }}
                  className={`px-2.5 py-1 rounded-full text-[11px] font-heading font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
                    isSelected
                      ? 'bg-[#080808] dark:bg-[#B7FF2A] text-[#B7FF2A] dark:text-[#080808] shadow-xs'
                      : 'text-[#555555] dark:text-[#AAAAAA] hover:text-[#080808] dark:hover:text-white'
                  }`}
                >
                  <span>{item.name}</span>
                  <span className="font-technical text-[10px] opacity-80">
                    {item.total_distance_km.toFixed(1)} km
                  </span>
                  {item.is_best && (
                    <span className="h-1.5 w-1.5 rounded-full bg-[#22C55E]" title="Best Feasible Solution" />
                  )}
                </button>
              );
            })}

            <button
              type="button"
              onClick={onNavigateToResults}
              className="text-[11px] font-bold text-[#080808] dark:text-[#F4F4F5] hover:underline flex items-center gap-1 cursor-pointer px-2"
              title="View full comparative scorecards"
            >
              <span>Scorecard</span>
              <ArrowRight className="h-3 w-3" />
            </button>
          </div>
        )}
      </div>

      {/* ─── FLOATING COLLAPSIBLE PLANNING CONTROLS SIDEBAR ──────────── */}
      {sidebarOpen ? (
        <aside
          aria-label="Delivery Planning Controls"
          className="absolute top-3 left-3 bottom-3 w-[430px] max-w-[calc(100vw-1.5rem)] z-[1000] flex flex-col rounded-3xl bg-white/75 dark:bg-[#111113]/90 backdrop-blur-[28px] backdrop-saturate-[190%] border border-white/80 dark:border-[#29292E] shadow-[0_24px_64px_-12px_rgba(0,0,0,0.18),inset_0_1px_1px_rgba(255,255,255,0.85)] dark:shadow-[0_24px_64px_-12px_rgba(0,0,0,0.8),inset_0_1px_1px_rgba(255,255,255,0.06)] overflow-hidden transition-all duration-300 ease-out"
        >
          {/* Sidebar Header */}
          <div className="p-4 pb-3 border-b border-black/10 dark:border-[#29292E] flex items-center justify-between shrink-0 bg-white/50 dark:bg-[#111113]/60 backdrop-blur-md">
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-[#B7FF00]" />
              <h2 className="text-sm font-heading font-bold text-[#080808] dark:text-[#F5F5F7] uppercase tracking-wider">
                Planning Controls
              </h2>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-black/5 dark:bg-[#18181B] border border-transparent dark:border-[#29292E] font-bold text-[#555555] dark:text-[#A1A1AA]">
                {activeStops.length} Stops Active
              </span>
            </div>

            <button
              onClick={() => setSidebarOpen(false)}
              className="p-1.5 rounded-xl hover:bg-black/5 dark:hover:bg-white/10 text-[#777777] hover:text-[#080808] dark:hover:text-white transition-colors cursor-pointer flex items-center gap-1 text-xs font-semibold"
              title="Minimize controls to inspect full-size map workspace"
            >
              <span className="text-[11px] hidden sm:inline">Hide</span>
              <ChevronLeft className="h-4 w-4" />
            </button>
          </div>

          {/* Scrollable controls panel (all 5 sections) */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 pr-3">
            {/* 1. Origin Depot Facility */}
            <div className="bg-white/70 dark:bg-[#18181B] backdrop-blur-xl border border-white/75 dark:border-[#29292E] p-4 rounded-2xl space-y-3 shadow-[0_4px_16px_rgba(0,0,0,0.03),inset_0_1px_0_rgba(255,255,255,0.8)] dark:shadow-[0_4px_16px_rgba(0,0,0,0.4),inset_0_1px_0_rgba(255,255,255,0.05)]">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-[#080808] dark:text-[#F5F5F7] flex items-center gap-1.5">
                  <MapPin className="h-3.5 w-3.5 text-[#080808] dark:text-white" />
                  <span>Origin Depot Facility</span>
                </span>
                <button
                  onClick={handleDeviceLocation}
                  className="text-[11px] font-semibold text-[#171717] dark:text-[#AAAAAA] hover:text-[#080808] dark:hover:text-white flex items-center gap-1 cursor-pointer transition-colors"
                  title="Use device GPS location"
                >
                  <Crosshair className="h-3 w-3 text-[#B7FF2A]" />
                  <span>My Location</span>
                </button>
              </div>

              {/* Current Depot Coordinate Bar */}
              <div className="flex items-center justify-between text-xs py-2 px-3 rounded-xl bg-black/[0.04] dark:bg-white/[0.05] border border-black/[0.06] dark:border-white/[0.06]">
                <div className="flex items-center gap-2 min-w-0">
                  <span className="h-2 w-2 rounded-full bg-[#B7FF2A] ring-1 ring-black shrink-0" />
                  <span className="font-semibold text-[#080808] dark:text-white truncate max-w-[170px]" title={depot.name}>
                    {depot.name}
                  </span>
                </div>
                <span className="font-technical text-[10px] text-[#777777] dark:text-[#AAAAAA] shrink-0">
                  {depot.lat.toFixed(4)}, {depot.lon.toFixed(4)}
                </span>
              </div>

              {/* Depot Relocation Tools */}
              <div className="flex items-center gap-2 text-xs">
                <button
                  onClick={() => setClickMode(clickMode === 'depot' ? 'none' : 'depot')}
                  className={`flex-1 py-1.5 px-3 rounded-full text-xs font-semibold transition-all cursor-pointer flex items-center justify-center gap-1.5 ${
                    clickMode === 'depot'
                      ? 'bg-[#080808] dark:bg-[#B7FF2A] text-[#B7FF2A] dark:text-[#080808] shadow-xs'
                      : 'bg-black/5 dark:bg-white/5 hover:bg-black/10 text-[#171717] dark:text-[#F4F4F5]'
                  }`}
                >
                  <MapPin className="h-3.5 w-3.5" />
                  <span>{clickMode === 'depot' ? 'Click Map to Move' : 'Pick on Map'}</span>
                </button>

                <button
                  onClick={() => setIsEditingDepot(!isEditingDepot)}
                  className={`py-1.5 px-3 rounded-full text-xs font-semibold transition-all cursor-pointer flex items-center gap-1.5 ${
                    isEditingDepot
                      ? 'bg-[#080808] text-white'
                      : 'bg-black/5 dark:bg-white/5 hover:bg-black/10 text-[#171717] dark:text-[#F4F4F5]'
                  }`}
                >
                  <Edit3 className="h-3.5 w-3.5" />
                  <span>Edit Lat/Lon</span>
                </button>
              </div>

              {/* Manual Lat/Lon Edit Form */}
              {isEditingDepot && (
                <div className="p-3 rounded-xl bg-black/[0.03] dark:bg-white/[0.04] border border-black/10 dark:border-white/10 space-y-2.5 animate-fadeIn">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-[#080808] dark:text-white">Manual Depot Coordinates</span>
                    <button onClick={() => setIsEditingDepot(false)} className="text-[#777777] hover:text-[#080808]">
                      <X className="h-3.5 w-3.5" />
                    </button>
                  </div>

                  <div>
                    <label className="text-[10px] font-bold uppercase tracking-wider text-[#777777] block mb-0.5">
                      Facility Name
                    </label>
                    <input
                      type="text"
                      value={manualDepotName}
                      onChange={(e) => setManualDepotName(e.target.value)}
                      className="w-full px-2.5 py-1 text-xs glass-input rounded-xl text-[#080808] dark:text-[#F4F4F5] bg-white/85 dark:bg-[#202026]/90 border border-black/10 dark:border-white/12"
                      placeholder="e.g. Brooklyn Central Hub"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="text-[10px] font-bold uppercase tracking-wider text-[#777777] block mb-0.5">
                        Latitude
                      </label>
                      <input
                        type="number"
                        step="0.0001"
                        value={manualDepotLat}
                        onChange={(e) => setManualDepotLat(e.target.value)}
                        className="w-full px-2.5 py-1 text-xs font-technical glass-input rounded-xl text-[#080808] dark:text-[#F4F4F5] bg-white/85 dark:bg-[#202026]/90 border border-black/10 dark:border-white/12"
                      />
                    </div>
                    <div>
                      <label className="text-[10px] font-bold uppercase tracking-wider text-[#777777] block mb-0.5">
                        Longitude
                      </label>
                      <input
                        type="number"
                        step="0.0001"
                        value={manualDepotLon}
                        onChange={(e) => setManualDepotLon(e.target.value)}
                        className="w-full px-2.5 py-1 text-xs font-technical glass-input rounded-xl text-[#080808] dark:text-[#F4F4F5] bg-white/85 dark:bg-[#202026]/90 border border-black/10 dark:border-white/12"
                      />
                    </div>
                  </div>

                  {depotEditError && (
                    <p className="text-[11px] text-red-600 font-semibold">{depotEditError}</p>
                  )}

                  <div className="flex justify-end gap-2 pt-1">
                    <button
                      onClick={() => setIsEditingDepot(false)}
                      className="px-2.5 py-1 rounded-full text-xs font-semibold text-[#777777]"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleSaveManualDepot}
                      className="px-3.5 py-1 rounded-full text-xs font-bold bg-[#080808] text-[#B7FF2A]"
                    >
                      Apply Coordinates
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* 2. Fleet & Capacity Constraints */}
            <div className="bg-white/70 dark:bg-[#18181B] backdrop-blur-xl border border-white/75 dark:border-[#29292E] p-4 rounded-2xl space-y-3 shadow-[0_4px_16px_rgba(0,0,0,0.03),inset_0_1px_0_rgba(255,255,255,0.8)] dark:shadow-[0_4px_16px_rgba(0,0,0,0.4),inset_0_1px_0_rgba(255,255,255,0.05)]">
              <span className="text-xs font-bold uppercase tracking-wider text-[#080808] dark:text-[#F5F5F7] block">
                Fleet & Capacity Constraints
              </span>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs text-[#777777] dark:text-[#A1A1AA] block mb-1">
                    Vehicles: <strong className="text-[#080808] dark:text-[#F5F5F7] font-technical">{numVehicles}</strong>
                  </label>
                  <input
                    type="range"
                    min={1}
                    max={10}
                    value={numVehicles}
                    onChange={(e) => {
                      const v = parseInt(e.target.value, 10);
                      setNumVehicles(v);
                      updateSettings({ defaultVehicles: v });
                    }}
                    className="w-full accent-[#080808] dark:accent-[#B7FF00] h-1.5 bg-black/10 dark:bg-[#17171A] rounded-full cursor-pointer"
                  />
                </div>

                <div>
                  <label className="text-xs text-[#777777] dark:text-[#A1A1AA] block mb-1">
                    Vehicle Capacity (units)
                  </label>
                  <input
                    type="number"
                    min={10}
                    max={500}
                    value={vehicleCapacity}
                    onChange={(e) => {
                      const c = parseInt(e.target.value, 10) || 10;
                      setVehicleCapacity(c);
                      updateSettings({ defaultCapacity: c });
                    }}
                    className="w-full px-2.5 py-1 text-xs font-technical font-bold glass-input rounded-xl bg-white/85 dark:bg-[#17171A] border border-black/10 dark:border-[#29292E] text-[#080808] dark:text-[#F5F5F7]"
                  />
                </div>
              </div>
            </div>

            {/* 3. Optimization Algorithms Selection */}
            <div className="bg-white/70 dark:bg-[#18181B] backdrop-blur-xl border border-white/75 dark:border-[#29292E] p-4 rounded-2xl space-y-3 shadow-[0_4px_16px_rgba(0,0,0,0.03),inset_0_1px_0_rgba(255,255,255,0.8)] dark:shadow-[0_4px_16px_rgba(0,0,0,0.4),inset_0_1px_0_rgba(255,255,255,0.05)]">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-[#080808] dark:text-[#F5F5F7] flex items-center gap-1.5">
                  <Sliders className="h-3.5 w-3.5 text-[#080808] dark:text-white" />
                  <span>Optimization Algorithms</span>
                </span>
                <span className="text-[11px] text-[#777777] dark:text-[#A1A1AA] block mt-0.5">
                  Select classical heuristics, exact solvers, or quantum methods
                </span>
              </div>

              {/* Mode Switcher */}
              <div className="grid grid-cols-3 gap-1 p-1 rounded-xl bg-black/5 dark:bg-[#17171A] border border-transparent dark:border-[#29292E] text-xs font-bold">
                <button
                  type="button"
                  onClick={() => {
                    setSelectionMode('recommended');
                    setSelectedAlgorithms(['ortools']);
                    localStorage.setItem('routeiq_selection_mode', 'recommended');
                  }}
                  className={`py-1.5 px-1 rounded-lg text-center transition-all cursor-pointer ${
                    selectionMode === 'recommended'
                      ? 'bg-[#080808] dark:bg-[#202024] text-[#B7FF00] shadow-xs'
                      : 'text-[#555555] dark:text-[#A1A1AA] hover:text-[#080808] dark:hover:text-white'
                  }`}
                >
                  Recommended
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setSelectionMode('custom');
                    localStorage.setItem('routeiq_selection_mode', 'custom');
                    if (selectedAlgorithms.length === 0) setSelectedAlgorithms(['ortools']);
                  }}
                  className={`py-1.5 px-1 rounded-lg text-center transition-all cursor-pointer ${
                    selectionMode === 'custom'
                      ? 'bg-[#080808] dark:bg-[#202024] text-white dark:text-[#F5F5F7] shadow-xs'
                      : 'text-[#555555] dark:text-[#A1A1AA] hover:text-[#080808] dark:hover:text-white'
                  }`}
                >
                  Select
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setSelectionMode('compare');
                    localStorage.setItem('routeiq_selection_mode', 'compare');
                    if (selectedAlgorithms.length < 2) {
                      const compSet =
                        activeStops.length <= 8
                          ? ['ortools', 'clarke_wright', 'two_opt', 'qiga', 'qaoa']
                          : ['ortools', 'clarke_wright', 'two_opt', 'dijkstra', 'astar', 'qiga'];
                      setSelectedAlgorithms(compSet);
                    }
                  }}
                  className={`py-1.5 px-1 rounded-lg text-center transition-all cursor-pointer ${
                    selectionMode === 'compare'
                      ? 'bg-[#080808] dark:bg-[#202024] text-[#B7FF00] shadow-xs'
                      : 'text-[#555555] dark:text-[#A1A1AA] hover:text-[#080808] dark:hover:text-white'
                  }`}
                >
                  Compare
                </button>
              </div>

              {/* Mode 1: Recommended */}
              {selectionMode === 'recommended' && (
                <div className="p-3 rounded-xl bg-black/5 dark:bg-[#17171A] border border-black/5 dark:border-[#29292E] space-y-2 animate-fadeIn">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-xs text-[#080808] dark:text-[#F5F5F7]">Google OR-Tools CVRP Solver</span>
                    <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-[#B7FF00]/25 text-[#080808] dark:text-[#B7FF00] font-bold">
                      Default
                    </span>
                  </div>
                  <p className="text-[11px] text-[#666666] dark:text-[#A1A1AA] leading-snug">
                    Standard classical vehicle routing optimizer with guided local search.
                  </p>
                </div>
              )}

              {/* Mode 2 & 3: Custom / Compare List */}
              {(selectionMode === 'custom' || selectionMode === 'compare') && (
                <div className="space-y-3 animate-fadeIn">
                  {/* Classical algorithms */}
                  <div className="space-y-1.5">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-[#777777] dark:text-[#71717A] block">
                      Classical algorithms
                    </span>
                    {WORKSPACE_ALGORITHMS.filter((a) => a.group === 'classical').map((algo) => {
                      const isChecked = selectedAlgorithms.includes(algo.id);
                      return (
                        <div
                          key={algo.id}
                          onClick={() => handleToggleAlgorithm(algo.id)}
                          className={`flex items-start justify-between p-2 rounded-xl text-xs transition-all cursor-pointer border ${
                            isChecked
                              ? 'bg-white dark:bg-[#202024] border-[#080808] dark:border-[#B7FF00]/50 shadow-xs'
                              : 'bg-black/5 dark:bg-[#17171A] border-transparent dark:border-[#29292E]/60 hover:bg-black/10'
                          }`}
                        >
                          <div className="flex items-start gap-2 min-w-0">
                            <input
                              type="checkbox"
                              checked={isChecked}
                              onChange={() => handleToggleAlgorithm(algo.id)}
                              className="rounded accent-[#080808] dark:accent-[#B7FF00] cursor-pointer h-3.5 w-3.5 mt-0.5"
                            />
                            <div className="min-w-0">
                              <span className="font-bold text-[#080808] dark:text-[#F5F5F7] block">{algo.name}</span>
                              <p className="text-[10px] text-[#666666] dark:text-[#A1A1AA] leading-tight mt-0.5">
                                {algo.role}
                              </p>
                            </div>
                          </div>
                          <span className="text-[9px] font-technical text-[#777777] dark:text-[#A1A1AA] shrink-0 ml-1">
                            {algo.badge}
                          </span>
                        </div>
                      );
                    })}
                  </div>

                  {/* Quantum algorithms */}
                  <div className="space-y-1.5">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-[#777777] dark:text-[#71717A] block">
                      Quantum / Quantum-Classical
                    </span>
                    {WORKSPACE_ALGORITHMS.filter((a) => a.group === 'quantum').map((algo) => {
                      const isChecked = selectedAlgorithms.includes(algo.id);
                      const isQaoaOversize = algo.id === 'qaoa' && activeStops.length > 8;

                      return (
                        <div
                          key={algo.id}
                          onClick={() => handleToggleAlgorithm(algo.id)}
                          className={`flex items-start justify-between p-2 rounded-xl text-xs transition-all cursor-pointer border ${
                            isChecked
                              ? 'bg-white dark:bg-[#202024] border-[#080808] dark:border-[#B7FF00]/50 shadow-xs'
                              : 'bg-black/5 dark:bg-[#17171A] border-transparent dark:border-[#29292E]/60 hover:bg-black/10'
                          }`}
                        >
                          <div className="flex items-start gap-2 min-w-0">
                            <input
                              type="checkbox"
                              checked={isChecked}
                              onChange={() => handleToggleAlgorithm(algo.id)}
                              className="rounded accent-[#080808] dark:accent-[#B7FF00] cursor-pointer h-3.5 w-3.5 mt-0.5"
                            />
                            <div className="min-w-0">
                              <span className="font-bold text-[#080808] dark:text-[#F5F5F7] block">{algo.name}</span>
                              <p className="text-[10px] text-[#666666] dark:text-[#A1A1AA] leading-tight mt-0.5">
                                {algo.role}
                              </p>
                              {isQaoaOversize && (
                                <p className="text-[9px] text-[#D97706] font-semibold mt-0.5">
                                  ⚠️ QAOA evaluates primary 8-node subproblem.
                                </p>
                              )}
                            </div>
                          </div>
                          <span className="text-[9px] font-technical text-[#A855F7] shrink-0 ml-1">
                            {algo.badge}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>

            {/* 4. Delivery Stops Table */}
            <div className="bg-white/70 dark:bg-[#18181B] backdrop-blur-xl border border-white/75 dark:border-[#29292E] p-4 rounded-2xl space-y-3 shadow-[0_4px_16px_rgba(0,0,0,0.03),inset_0_1px_0_rgba(255,255,255,0.8)] dark:shadow-[0_4px_16px_rgba(0,0,0,0.4),inset_0_1px_0_rgba(255,255,255,0.05)]">
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-xs font-bold uppercase tracking-wider text-[#080808] dark:text-[#F5F5F7] block">
                    Delivery Stops
                  </span>
                  <span className="text-[11px] text-[#777777] dark:text-[#A1A1AA]">
                    {activeStops.length} of {stops.length} selected
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => handleSelectAll(activeStops.length !== stops.length)}
                    className="text-[11px] font-semibold text-[#171717] dark:text-[#A1A1AA] hover:text-[#080808] dark:hover:text-white underline cursor-pointer"
                  >
                    {activeStops.length === stops.length ? 'Deselect' : 'Select All'}
                  </button>

                  <button
                    type="button"
                    onClick={handleResetStops}
                    className="text-[11px] font-semibold text-[#555555] dark:text-[#A1A1AA] hover:text-[#080808] dark:hover:text-white cursor-pointer"
                    title="Reload default stops from dataset"
                  >
                    Reset
                  </button>

                  <button
                    onClick={() => setClickMode(clickMode === 'stop' ? 'none' : 'stop')}
                    className={`text-xs font-semibold px-2.5 py-1 rounded-full flex items-center gap-1 transition-all cursor-pointer ${
                      clickMode === 'stop'
                        ? 'bg-[#080808] dark:bg-[#B7FF00] text-[#B7FF00] dark:text-black shadow-xs'
                        : 'bg-black/5 dark:bg-[#17171A] border border-transparent dark:border-[#29292E] text-[#080808] dark:text-[#F5F5F7] hover:bg-black/10'
                    }`}
                  >
                    <Plus className="h-3 w-3" />
                    <span>{clickMode === 'stop' ? 'Click Map' : 'Add'}</span>
                  </button>
                </div>
              </div>

              {/* Scrollable List of Customer Stops */}
              <div className="max-h-[220px] overflow-y-auto space-y-1.5 pr-1">
                {stops.map((stop) => (
                  <div
                    key={stop.id}
                    className={`flex items-center justify-between py-1.5 px-2.5 rounded-xl text-xs transition-all ${
                      stop.is_included
                        ? 'bg-white/85 dark:bg-[#17171A] backdrop-blur-md border border-black/10 dark:border-[#29292E] shadow-xs'
                        : 'opacity-40 hover:opacity-75 bg-black/5 dark:bg-black/30'
                    }`}
                  >
                    <div className="flex items-center gap-2 min-w-0">
                      <input
                        type="checkbox"
                        checked={stop.is_included}
                        onChange={() => handleToggleStop(stop.id)}
                        className="rounded accent-[#080808] dark:accent-[#B7FF00] cursor-pointer h-3.5 w-3.5"
                      />

                      {stop.is_included && (
                        <span className="h-4 w-4 rounded-full bg-[#080808] dark:bg-[#B7FF00] text-white dark:text-black flex items-center justify-center font-technical font-bold text-[9px] shrink-0">
                          {activeStops.findIndex((s) => s.id === stop.id) + 1}
                        </span>
                      )}

                      <div className="min-w-0">
                        <p className="font-semibold text-[#080808] dark:text-[#F5F5F7] truncate max-w-[140px]" title={stop.name}>
                          {stop.name}
                        </p>
                        <p className="font-technical text-[9px] text-[#777777] dark:text-[#A1A1AA]">
                          {stop.lat.toFixed(4)}, {stop.lon.toFixed(4)}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-1.5 shrink-0">
                      <input
                        type="number"
                        min={1}
                        max={99}
                        value={stop.demand}
                        onChange={(e) => handleDemandChange(stop.id, parseInt(e.target.value, 10) || 1)}
                        className="w-10 text-center text-xs font-technical font-bold glass-input rounded-md py-0.5 bg-white/85 dark:bg-[#202024] border border-black/10 dark:border-[#29292E] text-[#080808] dark:text-[#F5F5F7]"
                        title="Customer demand units"
                      />

                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleRemoveStop(stop.id);
                        }}
                        className="text-[#777777] hover:text-red-600 p-0.5 rounded cursor-pointer"
                        title="Remove stop"
                      >
                        <Trash2 className="h-3 w-3" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 5. Advanced Solver & QAOA Parameters */}
            <div className="bg-white/70 dark:bg-[#18181B] backdrop-blur-xl border border-white/75 dark:border-[#29292E] p-4 rounded-2xl shadow-[0_4px_16px_rgba(0,0,0,0.03),inset_0_1px_0_rgba(255,255,255,0.8)] dark:shadow-[0_4px_16px_rgba(0,0,0,0.4),inset_0_1px_0_rgba(255,255,255,0.05)]">
              <button
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="flex items-center justify-between w-full text-xs font-bold text-[#080808] dark:text-[#F5F5F7] cursor-pointer"
              >
                <span>Advanced Solver & QAOA Parameters</span>
                {showAdvanced ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
              </button>

              {showAdvanced && (
                <div className="pt-3 mt-3 space-y-3 text-xs border-t border-black/10 dark:border-[#29292E]">
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="text-[#777777] dark:text-[#A1A1AA] block mb-1">QAOA Depth (p)</label>
                      <select
                        value={qaoaDepth}
                        onChange={(e) => setQaoaDepth(parseInt(e.target.value, 10))}
                        className="w-full px-2 py-1 glass-input rounded-xl bg-white/85 dark:bg-[#17171A] border border-black/10 dark:border-[#29292E] text-[#080808] dark:text-[#F5F5F7] font-technical text-xs"
                      >
                        <option value={1}>p = 1 (Standard)</option>
                        <option value={2}>p = 2 (Higher Fidelity)</option>
                      </select>
                    </div>

                    <div>
                      <label className="text-[#777777] dark:text-[#A1A1AA] block mb-1">Measurement Shots</label>
                      <select
                        value={qaoaShots}
                        onChange={(e) => setQaoaShots(parseInt(e.target.value, 10))}
                        className="w-full px-2 py-1 glass-input rounded-xl bg-white/85 dark:bg-[#17171A] border border-black/10 dark:border-[#29292E] text-[#080808] dark:text-[#F5F5F7] font-technical text-xs"
                      >
                        <option value={512}>512 shots</option>
                        <option value={1024}>1024 shots</option>
                        <option value={2048}>2048 shots</option>
                      </select>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="text-[#777777] dark:text-[#A1A1AA] block mb-1">Distance Weight</label>
                      <input
                        type="number"
                        step={0.1}
                        value={weightDistance}
                        onChange={(e) => setWeightDistance(parseFloat(e.target.value))}
                        className="w-full px-2 py-1 glass-input rounded-xl bg-white/85 dark:bg-[#17171A] border border-black/10 dark:border-[#29292E] text-[#080808] dark:text-[#F5F5F7] font-technical text-xs"
                      />
                    </div>

                    <div>
                      <label className="text-[#777777] dark:text-[#A1A1AA] block mb-1">Travel Time Weight</label>
                      <input
                        type="number"
                        step={0.1}
                        value={weightTime}
                        onChange={(e) => setWeightTime(parseFloat(e.target.value))}
                        className="w-full px-2 py-1 glass-input rounded-xl bg-white/85 dark:bg-[#17171A] border border-black/10 dark:border-[#29292E] text-[#080808] dark:text-[#F5F5F7] font-technical text-xs"
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Ingested Diagnostics Telemetry Footer */}
            <div className="p-3 rounded-2xl bg-black/[0.03] dark:bg-[#17171A] border border-black/5 dark:border-[#29292E] text-[11px] space-y-1">
              <span className="text-[10px] font-bold uppercase tracking-wider text-[#777777] dark:text-[#71717A] block">
                Ingested Telemetry
              </span>
              <div className="flex items-center justify-between text-[#555555] dark:text-[#A1A1AA]">
                <span>Total Dataset Rows:</span>
                <span className="font-technical font-bold text-[#080808] dark:text-[#F5F5F7]">
                  {diagnostics.total_dataset_rows.toLocaleString()}
                </span>
              </div>
              <div className="flex items-center justify-between text-[#555555] dark:text-[#A1A1AA]">
                <span>Active Map Markers:</span>
                <span className="font-technical font-bold text-[#080808] dark:text-[#F5F5F7]">
                  {activeStops.length + 1}
                </span>
              </div>
            </div>
          </div>

          {/* Sticky Sidebar Action Bar for Quick Execution on Desktop & Mobile */}
          <div className="p-3 bg-white/90 dark:bg-[#111113]/95 backdrop-blur-md border-t border-black/10 dark:border-[#29292E] flex items-center gap-2 shrink-0">
            <button
              onClick={handleRunOptimization}
              disabled={isRunning || activeStops.length < 1}
              className="flex-1 flex items-center justify-center gap-2 py-2.5 px-4 bg-[#080808] hover:bg-[#171717] dark:bg-[#B7FF2A] dark:hover:bg-[#a4f01d] text-[#B7FF2A] dark:text-[#080808] rounded-xl text-xs font-heading font-bold shadow-md transition-all cursor-pointer disabled:opacity-40 border border-[#B7FF2A]/20"
            >
              {isRunning ? (
                <>
                  <RotateCw className="h-3.5 w-3.5 animate-spin text-[#B7FF2A] dark:text-[#080808]" />
                  <span>Computing Solution...</span>
                </>
              ) : (
                <>
                  <Play className="h-3.5 w-3.5 fill-current" />
                  <span>Run Optimization ({activeStops.length} Stops)</span>
                </>
              )}
            </button>
            <button
              onClick={loadStops}
              disabled={isLoadingStops || isRunning}
              className="p-2.5 rounded-xl bg-black/5 dark:bg-[#18181B] hover:bg-black/10 text-[#171717] dark:text-[#F4F4F5] border border-black/10 dark:border-[#29292E] transition-all cursor-pointer disabled:opacity-50"
              title="Reset Stops"
            >
              <RotateCw className={`h-3.5 w-3.5 ${isLoadingStops ? 'animate-spin text-[#22C55E]' : ''}`} />
            </button>
          </div>
        </aside>
      ) : (
        /* Minimized Floating Button when Sidebar is Collapsed */
        <button
          onClick={() => setSidebarOpen(true)}
          className="absolute top-3 left-3 z-[1000] flex items-center gap-2.5 px-4 py-2.5 rounded-full bg-[#080808]/90 dark:bg-[#18181E]/90 hover:bg-[#080808] text-[#B7FF2A] backdrop-blur-[24px] backdrop-saturate-[180%] shadow-2xl border border-white/20 text-xs font-heading font-bold cursor-pointer transition-all duration-200 hover:scale-[1.02]"
          title="Open Delivery Planning Controls"
        >
          <Sliders className="h-3.5 w-3.5 text-[#B7FF2A]" />
          <span>Planning Controls</span>
          <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-[#B7FF2A]/20 text-[#B7FF2A] font-technical">
            {activeStops.length} Stops
          </span>
        </button>
      )}

      {/* ─── CLICK MODE BANNER OVERLAY ───────────────────────────────── */}
      {clickMode !== 'none' && (
        <div className="absolute top-16 left-1/2 -translate-x-1/2 bg-[#080808]/90 backdrop-blur-[24px] text-[#B7FF2A] py-2 px-5 rounded-full text-xs font-heading font-bold shadow-2xl z-[1000] flex items-center gap-3 border border-[#B7FF2A]/30">
          <span className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-[#B7FF2A] animate-ping" />
            {clickMode === 'depot'
              ? 'Click anywhere on the map roadway to place origin depot'
              : 'Click anywhere on the map roadway to place delivery stop'}
          </span>
          <button
            onClick={() => setClickMode('none')}
            className="text-white hover:text-white/80 cursor-pointer px-2 py-0.5 rounded-full bg-white/10 text-[10px]"
          >
            Cancel
          </button>
        </div>
      )}

      {/* ─── TOAST / VALIDATION ALERTS ──────────────────────────────── */}
      {validationError && (
        <div
          className={`absolute top-16 z-[1000] flex items-center gap-2 px-4 py-2.5 rounded-2xl bg-red-600/90 backdrop-blur-xl text-white text-xs font-heading font-semibold shadow-2xl border border-red-400 animate-fadeIn max-w-md transition-all duration-300 ${
            sidebarOpen ? 'left-1/2 -translate-x-1/2 lg:left-[calc(50%+215px)]' : 'left-1/2 -translate-x-1/2'
          }`}
        >
          <AlertTriangle className="h-4 w-4 shrink-0" />
          <span className="flex-1">{validationError}</span>
          <button onClick={() => setValidationError(null)} className="p-0.5 hover:bg-white/20 rounded cursor-pointer">
            <X className="h-3.5 w-3.5" />
          </button>
        </div>
      )}

      {feedbackMessage && (
        <div
          className={`absolute top-16 z-[1000] flex items-center gap-2 px-4 py-2 rounded-full bg-[#080808]/90 backdrop-blur-xl text-[#B7FF2A] text-xs font-heading font-bold shadow-xl border border-[#B7FF2A]/30 animate-fadeIn transition-all duration-300 ${
            sidebarOpen ? 'left-1/2 -translate-x-1/2 lg:left-[calc(50%+215px)]' : 'left-1/2 -translate-x-1/2'
          }`}
        >
          <CheckCircle2 className="h-3.5 w-3.5 text-[#B7FF2A]" />
          <span>{feedbackMessage}</span>
        </div>
      )}

      {/* ─── FLOATING BOTTOM-RIGHT MAP LEGEND ────────────────────────── */}
      <div className="absolute bottom-4 right-4 bg-white/75 dark:bg-[#18181E]/80 backdrop-blur-[24px] backdrop-saturate-[180%] border border-white/80 dark:border-white/10 px-4 py-2 rounded-2xl text-[11px] z-[990] flex items-center gap-3 shadow-[0_8px_24px_rgba(0,0,0,0.08),inset_0_1px_0_rgba(255,255,255,0.85)] dark:shadow-[0_8px_24px_rgba(0,0,0,0.5),inset_0_1px_0_rgba(255,255,255,0.1)]">
        <span className="font-bold text-[#080808] dark:text-white">Legend:</span>
        <span className="flex items-center gap-1.5 font-medium">
          <span className="h-3 w-3 rounded-full bg-[#B7FF2A] border border-[#080808] flex items-center justify-center text-[7px] font-bold text-black">
            D
          </span>
          <span>Depot</span>
        </span>
        <span className="flex items-center gap-1.5 font-medium">
          <span className="h-3 w-3 rounded-full bg-[#080808] border border-white flex items-center justify-center text-[7px] font-bold text-white">
            #
          </span>
          <span>Customer Stops ({activeStops.length})</span>
        </span>
        {activeRoutes.length > 0 && (
          <span className="flex items-center gap-1.5 font-bold text-[#080808] dark:text-white">
            <span className="h-2.5 w-2.5 rounded-full bg-[#B7FF2A] border border-black" />
            <span>{activeRoutes.length} Computed Routes</span>
          </span>
        )}
      </div>
    </div>
  );
};
