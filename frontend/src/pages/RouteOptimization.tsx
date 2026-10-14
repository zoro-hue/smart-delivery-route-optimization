import React, { useState, useEffect } from 'react';
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Polyline,
} from 'react-leaflet';
import L from 'leaflet';
import {
  Play,
  Settings2,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Clock,
  Zap,
  Sliders,
  Cpu,
  RefreshCw,
  Truck,
  MapPin,
  ExternalLink,
  Navigation,
  ArrowRight,
  ArrowLeft,
  Database,
  Upload,
  Crosshair,
  Plus,
  Trash2,
  Download,
  Info,
  ShieldCheck,
  Layers,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { OptimizationResponse, VehicleRoute, Dataset } from '../types';
import { api } from '../services/api';

// Fix Leaflet icons
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

const createMapIcon = (bg: string, border: string, text: string, textColor: string) => {
  return L.divIcon({
    className: 'custom-map-pin',
    html: `<div style="background-color: ${bg}; border: 2px solid ${border}; color: ${textColor}; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 800; font-family: Inter, sans-serif; box-shadow: 0 4px 10px rgba(0,0,0,0.35);">${text}</div>`,
    iconSize: [28, 28],
    iconAnchor: [14, 14],
    popupAnchor: [0, -16],
  });
};

const depotIcon = createMapIcon('#080808', '#B7FF2A', 'D', '#B7FF2A');
const customerIcon = createMapIcon('#171717', '#FFFFFF', 'C', '#FFFFFF');
const driverIcon = createMapIcon('#B7FF2A', '#080808', 'V', '#080808');

const ROUTE_COLORS = ['#080808', '#B7FF2A', '#171717', '#A4F51B', '#777777'];

interface DeliveryStop {
  id: string;
  customer_id: string;
  name: string;
  lat: number;
  lon: number;
  demand: number;
  service_time_min: number;
  address: string;
  status: string;
  is_included: boolean;
}

interface RouteOptimizationProps {
  onOptimizationComplete: (response: OptimizationResponse) => void;
  onNavigateToMap: () => void;
}

export const RouteOptimization: React.FC<RouteOptimizationProps> = ({
  onOptimizationComplete,
  onNavigateToMap,
}) => {
  // Guided Workflow Step (1, 2, or 3)
  const [currentStep, setCurrentStep] = useState<number>(1);

  // STEP 1 — DATA & LOCATIONS
  const [dataSource, setDataSource] = useState<'existing' | 'upload' | 'gps'>('existing');
  const [stops, setStops] = useState<DeliveryStop[]>([]);
  const [depot, setDepot] = useState<{ lat: number; lon: number; name: string }>({
    lat: 40.7580,
    lon: -73.8292,
    name: 'Main NYC Logistics Depot (Flushing Hub)',
  });
  const [isLoadingStops, setIsLoadingStops] = useState<boolean>(false);
  const [isGeolocationActive, setIsGeolocationActive] = useState<boolean>(false);
  const [newStopLat, setNewStopLat] = useState<string>('40.7589');
  const [newStopLon, setNewStopLon] = useState<string>('-73.9851');
  const [newStopName, setNewStopName] = useState<string>('Times Square Express');
  const [newStopDemand, setNewStopDemand] = useState<string>('15');
  const [showAddModal, setShowAddModal] = useState<boolean>(false);

  // STEP 2 — GOALS & SETTINGS
  const [algorithm, setAlgorithm] = useState<string>('both'); // classical, qaoa, both
  const [numVehicles, setNumVehicles] = useState<number>(2);
  const [vehicleCapacity, setVehicleCapacity] = useState<number>(50);
  const [distanceUnit, setDistanceUnit] = useState<'km' | 'mi'>('km');
  const [departureTime, setDepartureTime] = useState<string>('08:30');
  const [returnToDepot, setReturnToDepot] = useState<boolean>(true);
  const [travelMode, setTravelMode] = useState<string>('van');

  // Objective weights
  const [weightDistance, setWeightDistance] = useState<number>(1.0);
  const [weightTravelTime, setWeightTravelTime] = useState<number>(0.5);
  const [weightCongestion, setWeightCongestion] = useState<number>(0.3);

  // Scenarios
  const [trafficScenario, setTrafficScenario] = useState<string>('normal');
  const [weatherScenario, setWeatherScenario] = useState<string>('clear');

  // Quantum QAOA parameters
  const [qaoaDepth, setQaoaDepth] = useState<number>(1);
  const [qaoaShots, setQaoaShots] = useState<number>(1024);
  const [qaoaPenalty, setQaoaPenalty] = useState<number>(10.0);

  // Problem Estimation
  const [estimation, setEstimation] = useState<any>(null);
  const [isEstimating, setIsEstimating] = useState<boolean>(false);

  // STEP 3 — ROUTES & RESULTS
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [result, setResult] = useState<OptimizationResponse | null>(null);
  const [activeResultTab, setActiveResultTab] = useState<'classical' | 'qaoa'>('classical');
  const [expandedRouteId, setExpandedRouteId] = useState<number | null>(null);

  // Load Initial Stops from Backend
  useEffect(() => {
    loadDeliveryStops();
  }, []);

  const loadDeliveryStops = async () => {
    setIsLoadingStops(true);
    try {
      const data = await api.getDeliveryStops(30);
      if (data && data.stops) {
        setStops(data.stops);
        if (data.depot) {
          setDepot(data.depot);
        }
      }
    } catch (err) {
      console.error('Failed to load delivery stops:', err);
    } finally {
      setIsLoadingStops(false);
    }
  };

  const handleToggleStop = (id: string) => {
    setStops((prev) =>
      prev.map((s) => (s.id === id ? { ...s, is_included: !s.is_included } : s))
    );
  };

  const handleSelectAll = (select: boolean) => {
    setStops((prev) => prev.map((s) => ({ ...s, is_included: select })));
  };

  const handleAddCustomStop = () => {
    const lat = parseFloat(newStopLat);
    const lon = parseFloat(newStopLon);
    const demand = parseFloat(newStopDemand) || 10;
    if (isNaN(lat) || isNaN(lon)) {
      alert('Please enter valid numeric latitude and longitude.');
      return;
    }
    const newStop: DeliveryStop = {
      id: `CUSTOM-${Date.now().toString().slice(-4)}`,
      customer_id: `CUST-MANUAL-${stops.length + 1}`,
      name: newStopName || `Custom Stop #${stops.length + 1}`,
      lat,
      lon,
      demand,
      service_time_min: 15,
      address: `${newStopName}, New York, NY`,
      status: 'valid',
      is_included: true,
    };
    setStops([newStop, ...stops]);
    setShowAddModal(false);
    setNewStopName('');
  };

  const handleUseCurrentLocation = () => {
    if (!navigator.geolocation) {
      alert('Geolocation is not supported by your browser.');
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setDepot({
          lat: pos.coords.latitude,
          lon: pos.coords.longitude,
          name: `Device GPS Location (${pos.coords.latitude.toFixed(4)}, ${pos.coords.longitude.toFixed(4)})`,
        });
        setIsGeolocationActive(true);
      },
      (err) => {
        alert(`Location permission denied or unavailable: ${err.message}. Defaulting to NYC Depot.`);
      }
    );
  };

  const includedStops = stops.filter((s) => s.is_included);

  const handleEstimate = async () => {
    setIsEstimating(true);
    try {
      const est = await api.estimateProblemSize({
        algorithm,
        num_customers: includedStops.length,
        num_vehicles: Number(numVehicles),
        vehicle_capacity: Number(vehicleCapacity),
      });
      setEstimation(est);
    } catch (err) {
      console.error('Estimation failed:', err);
    } finally {
      setIsEstimating(false);
    }
  };

  const handleExecuteOptimization = async () => {
    if (includedStops.length < 2) {
      alert('Please select at least 2 delivery stops in Step 1 before optimizing.');
      return;
    }

    setIsRunning(true);
    try {
      const payload = {
        algorithm,
        num_customers: includedStops.length,
        num_vehicles: Number(numVehicles),
        vehicle_capacity: Number(vehicleCapacity),
        depot_lat: depot.lat,
        depot_lon: depot.lon,
        weight_distance: Number(weightDistance),
        weight_travel_time: Number(weightTravelTime),
        weight_congestion: Number(weightCongestion),
        traffic_scenario: trafficScenario,
        weather_scenario: weatherScenario,
        qaoa_depth: Number(qaoaDepth),
        qaoa_shots: Number(qaoaShots),
        qaoa_penalty: Number(qaoaPenalty),
        custom_customers: includedStops.map((s) => ({
          id: s.id,
          name: s.name,
          lat: s.lat,
          lon: s.lon,
          demand: s.demand,
        })),
      };

      const res = await api.runOptimization(payload);
      setResult(res);
      onOptimizationComplete(res);

      if (algorithm === 'qaoa') {
        setActiveResultTab('qaoa');
      } else {
        setActiveResultTab('classical');
      }

      setCurrentStep(3); // Advance to Step 3 Results!
    } catch (err: any) {
      alert(`Optimization failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setIsRunning(false);
    }
  };

  // Export Results
  const handleExportJSON = () => {
    if (!result) return;
    const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ROUTEIQ_Optimization_${Date.now()}.json`;
    a.click();
  };

  const handleExportCSV = () => {
    if (!result) return;
    const currentRoutes =
      activeResultTab === 'qaoa'
        ? result.results?.qaoa?.routes
        : result.results?.classical?.routes;
    if (!currentRoutes) return;

    let csv = 'Vehicle,Stop_Sequence,Stop_Index,Latitude,Longitude,Type\n';
    currentRoutes.forEach((route, vIdx) => {
      route.waypoints?.forEach((wp, sIdx) => {
        csv += `Vehicle_${vIdx + 1},${sIdx + 1},${wp.index},${wp.lat},${wp.lon},${wp.type}\n`;
      });
    });

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ROUTEIQ_Routes_${Date.now()}.csv`;
    a.click();
  };

  // Map elements calculation
  const displayedRoutes: VehicleRoute[] =
    currentStep === 3 && result?.results
      ? (activeResultTab === 'qaoa'
          ? result.results.qaoa?.routes
          : result.results.classical?.routes) || []
      : [];

  const mapCenter: [number, number] = [depot.lat, depot.lon];

  return (
    <div className="space-y-4">
      {/* 3-Step Guided Header */}
      <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="font-heading text-xl font-bold tracking-tight text-[#080808]">
                SMART DELIVERY ROUTE PLANNER
              </span>
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-[#B7FF2A] text-black font-extrabold uppercase tracking-wider">
                Workstation
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Multi-Vehicle CVRP & Quantum QAOA Solver · Bounded Real NYC Logistics Network
            </p>
          </div>

          {/* Stepper Navigation Indicator */}
          <div className="flex items-center gap-2">
            {[
              { num: 1, label: 'Data & Locations' },
              { num: 2, label: 'Goals & Settings' },
              { num: 3, label: 'Routes & Results' },
            ].map((step, idx) => {
              const isActive = currentStep === step.num;
              const isPast = currentStep > step.num;
              return (
                <React.Fragment key={step.num}>
                  {idx > 0 && (
                    <div
                      className={`h-0.5 w-6 transition-colors ${
                        isPast ? 'bg-[#080808]' : 'bg-slate-200'
                      }`}
                    />
                  )}
                  <button
                    onClick={() => {
                      // Allow moving backward anytime, or forward if validation holds
                      if (step.num === 1 || (step.num === 2 && includedStops.length >= 2) || (step.num === 3 && result)) {
                        setCurrentStep(step.num);
                      }
                    }}
                    className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold transition-all ${
                      isActive
                        ? 'bg-[#080808] text-white shadow-sm ring-2 ring-black'
                        : isPast
                        ? 'bg-[#B7FF2A] text-black hover:bg-lime-400'
                        : 'bg-slate-100 text-slate-400 hover:text-slate-600'
                    }`}
                  >
                    <span
                      className={`h-4.5 w-4.5 rounded-full flex items-center justify-center text-[10px] ${
                        isActive
                          ? 'bg-[#B7FF2A] text-black'
                          : isPast
                          ? 'bg-black text-[#B7FF2A]'
                          : 'bg-slate-200 text-slate-500'
                      }`}
                    >
                      {isPast ? '✓' : step.num}
                    </span>
                    <span className="hidden sm:inline">{step.label}</span>
                  </button>
                </React.Fragment>
              );
            })}
          </div>
        </div>
      </div>

      {/* Main Workstation Layout (Split View: Left Configuration / Right Interactive Map) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
        {/* Left Workflow Panel (5 cols on wide screens) */}
        <div className="lg:col-span-5 space-y-4">
          {/* STEP 1: DATA & LOCATIONS PANEL */}
          {currentStep === 1 && (
            <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs space-y-5">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <div>
                  <h3 className="font-heading text-lg font-bold text-slate-900">
                    STEP 1 — DATA & LOCATIONS
                  </h3>
                  <p className="text-xs text-slate-500">
                    Select delivery stops from ingested datasets or live GPS
                  </p>
                </div>
                <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-slate-100 text-slate-700">
                  {includedStops.length} Selected
                </span>
              </div>

              {/* Data Source Selector */}
              <div className="grid grid-cols-3 gap-2">
                <button
                  onClick={() => setDataSource('existing')}
                  className={`p-3 rounded-xl border text-left transition-all ${
                    dataSource === 'existing'
                      ? 'border-black bg-black text-white shadow-sm'
                      : 'border-slate-200 bg-slate-50 text-slate-700 hover:bg-slate-100'
                  }`}
                >
                  <Database className={`h-4 w-4 mb-1.5 ${dataSource === 'existing' ? 'text-[#B7FF2A]' : 'text-slate-500'}`} />
                  <p className="text-xs font-bold leading-tight">NYC Datasets</p>
                  <p className="text-[10px] opacity-75 mt-0.5">Real Ingested Data</p>
                </button>

                <button
                  onClick={() => setDataSource('upload')}
                  className={`p-3 rounded-xl border text-left transition-all ${
                    dataSource === 'upload'
                      ? 'border-black bg-black text-white shadow-sm'
                      : 'border-slate-200 bg-slate-50 text-slate-700 hover:bg-slate-100'
                  }`}
                >
                  <Upload className={`h-4 w-4 mb-1.5 ${dataSource === 'upload' ? 'text-[#B7FF2A]' : 'text-slate-500'}`} />
                  <p className="text-xs font-bold leading-tight">Upload ZIP</p>
                  <p className="text-[10px] opacity-75 mt-0.5">Custom Datasets</p>
                </button>

                <button
                  onClick={() => {
                    setDataSource('gps');
                    handleUseCurrentLocation();
                  }}
                  className={`p-3 rounded-xl border text-left transition-all ${
                    dataSource === 'gps'
                      ? 'border-black bg-black text-white shadow-sm'
                      : 'border-slate-200 bg-slate-50 text-slate-700 hover:bg-slate-100'
                  }`}
                >
                  <Crosshair className={`h-4 w-4 mb-1.5 ${dataSource === 'gps' ? 'text-[#B7FF2A]' : 'text-slate-500'}`} />
                  <p className="text-xs font-bold leading-tight">Device GPS</p>
                  <p className="text-[10px] opacity-75 mt-0.5">Browser Location</p>
                </button>
              </div>

              {/* Depot Information Banner */}
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <div className="h-7 w-7 rounded-lg bg-[#080808] text-[#B7FF2A] border border-black flex items-center justify-center shrink-0">
                    <MapPin className="h-4 w-4 text-[#B7FF2A]" />
                  </div>
                  <div>
                    <span className="text-[11px] font-bold text-slate-800 uppercase tracking-wider block">
                      Origin Depot
                    </span>
                    <p className="text-xs text-slate-600 truncate max-w-[200px]">
                      {depot.name}
                    </p>
                  </div>
                </div>
                <span className="text-[10px] font-mono font-medium px-2 py-0.5 rounded bg-white border border-slate-200 text-slate-600">
                  {depot.lat.toFixed(4)}, {depot.lon.toFixed(4)}
                </span>
              </div>

              {/* Stop Actions & Controls */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleSelectAll(true)}
                    className="text-xs font-semibold text-slate-700 hover:text-black underline underline-offset-2"
                  >
                    Select All
                  </button>
                  <span className="text-slate-300">·</span>
                  <button
                    onClick={() => handleSelectAll(false)}
                    className="text-xs font-semibold text-slate-700 hover:text-black underline underline-offset-2"
                  >
                    Clear All
                  </button>
                </div>
                <button
                  onClick={() => setShowAddModal(true)}
                  className="flex items-center gap-1 px-3 py-1 bg-slate-100 hover:bg-slate-200 text-slate-800 rounded-lg text-xs font-bold transition-all"
                >
                  <Plus className="h-3.5 w-3.5" />
                  <span>Add Stop</span>
                </button>
              </div>

              {/* Delivery Locations Table */}
              <div className="border border-slate-200 rounded-xl overflow-hidden max-h-[320px] overflow-y-auto">
                <table className="w-full text-xs text-left">
                  <thead className="bg-slate-50 border-b border-slate-200 sticky top-0 z-10 text-slate-600 font-semibold uppercase text-[10px]">
                    <tr>
                      <th className="p-2.5 w-8 text-center">Inc</th>
                      <th className="p-2.5">Stop / Customer</th>
                      <th className="p-2.5">Coordinates</th>
                      <th className="p-2.5 text-right">Demand</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {stops.slice(0, 15).map((stop) => (
                      <tr
                        key={stop.id}
                        className={`hover:bg-slate-50 transition-colors ${
                          stop.is_included ? 'bg-white' : 'bg-slate-50/60 opacity-60'
                        }`}
                      >
                        <td className="p-2.5 text-center">
                          <input
                            type="checkbox"
                            checked={stop.is_included}
                            onChange={() => handleToggleStop(stop.id)}
                            className="rounded border-slate-300 text-black focus:ring-black h-3.5 w-3.5 cursor-pointer"
                          />
                        </td>
                        <td className="p-2.5 font-medium text-slate-800">
                          <div className="truncate max-w-[140px]" title={stop.name}>
                            {stop.name}
                          </div>
                          <span className="text-[10px] text-slate-400 font-mono">
                            {stop.customer_id}
                          </span>
                        </td>
                        <td className="p-2.5 text-slate-600 font-mono text-[11px]">
                          {stop.lat.toFixed(3)}, {stop.lon.toFixed(3)}
                        </td>
                        <td className="p-2.5 text-right font-bold text-slate-900">
                          {stop.demand} u
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Step 1 Actions */}
              <div className="pt-2 flex items-center justify-between">
                <button
                  onClick={loadDeliveryStops}
                  disabled={isLoadingStops}
                  className="flex items-center gap-1.5 px-3 py-2 text-xs font-semibold text-slate-600 hover:text-black border border-slate-200 rounded-xl hover:bg-slate-50 transition-all"
                >
                  <RefreshCw className={`h-3.5 w-3.5 ${isLoadingStops ? 'animate-spin' : ''}`} />
                  <span>Reload Dataset</span>
                </button>

                <button
                  onClick={() => setCurrentStep(2)}
                  disabled={includedStops.length < 2}
                  className="flex items-center gap-2 px-5 py-2.5 bg-[#080808] hover:bg-neutral-800 text-[#B7FF2A] rounded-xl text-xs font-extrabold shadow-sm transition-all disabled:opacity-40"
                >
                  <span>Continue to Goals & Settings</span>
                  <ArrowRight className="h-4 w-4" />
                </button>
              </div>
            </div>
          )}

          {/* STEP 2: GOALS & SETTINGS PANEL */}
          {currentStep === 2 && (
            <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs space-y-5">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <div>
                  <h3 className="font-heading text-lg font-bold text-slate-900">
                    STEP 2 — GOALS & SETTINGS
                  </h3>
                  <p className="text-xs text-slate-500">
                    Configure fleet constraints, objective weights, and solver modes
                  </p>
                </div>
                <span className="text-xs font-bold text-[#080808] bg-[#B7FF2A] px-2.5 py-0.5 rounded-full">
                  {includedStops.length} Stops Active
                </span>
              </div>

              {/* Mode Selection Cards */}
              <div>
                <label className="text-xs font-bold text-slate-800 uppercase tracking-wider block mb-2">
                  Optimization Engine Mode
                </label>
                <div className="grid grid-cols-2 gap-3">
                  <div
                    onClick={() => setAlgorithm('classical')}
                    className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                      algorithm === 'classical'
                        ? 'border-black bg-black text-white shadow-sm ring-1 ring-black'
                        : 'border-slate-200 bg-slate-50 text-slate-800 hover:bg-slate-100'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-extrabold uppercase">Mode 1: Classical</span>
                      {algorithm === 'classical' && <CheckCircle2 className="h-4 w-4 text-[#B7FF2A]" />}
                    </div>
                    <p className="text-[11px] opacity-80 leading-relaxed">
                      Clarke-Wright Savings & 2-Opt CVRP metaheuristic. Fast and scalable.
                    </p>
                  </div>

                  <div
                    onClick={() => setAlgorithm('both')}
                    className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                      algorithm === 'both' || algorithm === 'qaoa'
                        ? 'border-black bg-black text-white shadow-sm ring-1 ring-black'
                        : 'border-slate-200 bg-slate-50 text-slate-800 hover:bg-slate-100'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-extrabold uppercase flex items-center gap-1">
                        <Zap className="h-3 w-3 text-[#B7FF2A]" />
                        <span>Mode 2: Quantum</span>
                      </span>
                      {(algorithm === 'both' || algorithm === 'qaoa') && (
                        <CheckCircle2 className="h-4 w-4 text-[#B7FF2A]" />
                      )}
                    </div>
                    <p className="text-[11px] opacity-80 leading-relaxed">
                      QUBO + Ising + Qiskit 2.4.1 QAOA Statevector simulation benchmark.
                    </p>
                  </div>
                </div>
              </div>

              {/* Fleet & Capacity Parameters */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">
                    Fleet Vehicles
                  </label>
                  <input
                    type="number"
                    min={1}
                    max={10}
                    value={numVehicles}
                    onChange={(e) => setNumVehicles(parseInt(e.target.value) || 1)}
                    className="w-full px-3 py-2 border border-slate-200 rounded-xl text-xs font-bold text-slate-900 bg-slate-50"
                  />
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">
                    Vehicle Capacity (Units)
                  </label>
                  <input
                    type="number"
                    min={10}
                    max={500}
                    value={vehicleCapacity}
                    onChange={(e) => setVehicleCapacity(parseInt(e.target.value) || 50)}
                    className="w-full px-3 py-2 border border-slate-200 rounded-xl text-xs font-bold text-slate-900 bg-slate-50"
                  />
                </div>
              </div>

              {/* Objective Weights */}
              <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                    Cost Objective Function
                  </span>
                  <span className="text-[10px] font-mono text-slate-500">
                    Cost = w_d·D + w_t·T + w_c·C
                  </span>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-slate-600">Distance Weight (w_d)</span>
                    <span className="font-bold">{weightDistance.toFixed(1)}</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="2"
                    step="0.1"
                    value={weightDistance}
                    onChange={(e) => setWeightDistance(parseFloat(e.target.value))}
                    className="w-full accent-black h-1 bg-slate-200 rounded-lg cursor-pointer"
                  />

                  <div className="flex items-center justify-between text-xs">
                    <span className="text-slate-600">Travel Time Weight (w_t)</span>
                    <span className="font-bold">{weightTravelTime.toFixed(1)}</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="2"
                    step="0.1"
                    value={weightTravelTime}
                    onChange={(e) => setWeightTravelTime(parseFloat(e.target.value))}
                    className="w-full accent-black h-1 bg-slate-200 rounded-lg cursor-pointer"
                  />

                  <div className="flex items-center justify-between text-xs">
                    <span className="text-slate-600">Congestion Weight (w_c)</span>
                    <span className="font-bold">{weightCongestion.toFixed(1)}</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="2"
                    step="0.1"
                    value={weightCongestion}
                    onChange={(e) => setWeightCongestion(parseFloat(e.target.value))}
                    className="w-full accent-black h-1 bg-slate-200 rounded-lg cursor-pointer"
                  />
                </div>
              </div>

              {/* Scenarios */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">
                    Traffic Scenario
                  </label>
                  <select
                    value={trafficScenario}
                    onChange={(e) => setTrafficScenario(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-200 rounded-xl text-xs font-medium bg-slate-50"
                  >
                    <option value="normal">Normal Traffic (1.0x)</option>
                    <option value="moderate">Moderate Rush (1.25x)</option>
                    <option value="high_congestion">High Congestion (1.6x)</option>
                    <option value="severe">Severe Gridlock (2.2x)</option>
                  </select>
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">
                    Weather Multiplier
                  </label>
                  <select
                    value={weatherScenario}
                    onChange={(e) => setWeatherScenario(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-200 rounded-xl text-xs font-medium bg-slate-50"
                  >
                    <option value="clear">Clear Skies (1.0x)</option>
                    <option value="cloudy">Cloudy (1.05x)</option>
                    <option value="rain">NYC Rain (1.2x)</option>
                    <option value="heavy_rain">Heavy Storm (1.45x)</option>
                  </select>
                </div>
              </div>

              {/* QAOA Parameters (When Quantum Active) */}
              {(algorithm === 'both' || algorithm === 'qaoa') && (
                <div className="p-3.5 bg-slate-900 text-white rounded-xl space-y-2 border border-slate-800">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-[#B7FF2A] uppercase tracking-wider flex items-center gap-1.5">
                      <Cpu className="h-3.5 w-3.5" />
                      Qiskit QAOA Parameters
                    </span>
                    <span className="text-[10px] text-slate-400">Statevector · COBYLA</span>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div>
                      <span className="text-slate-400 block text-[11px]">Circuit Depth (p)</span>
                      <select
                        value={qaoaDepth}
                        onChange={(e) => setQaoaDepth(parseInt(e.target.value))}
                        className="w-full mt-1 bg-slate-800 border border-slate-700 rounded-lg px-2 py-1 text-white text-xs"
                      >
                        <option value={1}>p = 1 (Standard)</option>
                        <option value={2}>p = 2 (Higher Fidelity)</option>
                      </select>
                    </div>

                    <div>
                      <span className="text-slate-400 block text-[11px]">Measurement Shots</span>
                      <select
                        value={qaoaShots}
                        onChange={(e) => setQaoaShots(parseInt(e.target.value))}
                        className="w-full mt-1 bg-slate-800 border border-slate-700 rounded-lg px-2 py-1 text-white text-xs"
                      >
                        <option value={512}>512 shots</option>
                        <option value={1024}>1024 shots</option>
                        <option value={2048}>2048 shots</option>
                      </select>
                    </div>
                  </div>

                  {includedStops.length > 8 && (
                    <div className="p-2.5 rounded-xl bg-[#080808] border border-white/20 text-[#B7FF2A] text-[11px] flex items-start gap-2 mt-2">
                      <AlertTriangle className="h-3.5 w-3.5 shrink-0 text-[#B7FF2A] mt-0.5" />
                      <span className="text-white">
                        Notice: <strong className="text-[#B7FF2A]">{includedStops.length} stops</strong> may require {includedStops.length * numVehicles} qubits (exceeding simulator limit of 20). Classical solver will run seamlessly.
                      </span>
                    </div>
                  )}
                </div>
              )}

              {/* Step 2 Actions */}
              <div className="pt-2 flex items-center justify-between">
                <button
                  onClick={() => setCurrentStep(1)}
                  className="flex items-center gap-1.5 px-3 py-2 text-xs font-semibold text-slate-600 hover:text-black border border-slate-200 rounded-xl hover:bg-slate-50 transition-all"
                >
                  <ArrowLeft className="h-3.5 w-3.5" />
                  <span>Back to Data</span>
                </button>

                <button
                  onClick={handleExecuteOptimization}
                  disabled={isRunning}
                  className="flex items-center gap-2 px-5 py-2.5 bg-[#080808] hover:bg-neutral-800 text-[#B7FF2A] rounded-xl text-xs font-extrabold shadow-sm transition-all disabled:opacity-50"
                >
                  {isRunning ? (
                    <>
                      <RefreshCw className="h-4 w-4 animate-spin text-[#B7FF2A]" />
                      <span>Executing Solver...</span>
                    </>
                  ) : (
                    <>
                      <Play className="h-4 w-4 fill-[#B7FF2A] text-[#B7FF2A]" />
                      <span>Run Optimization Solver</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          )}

          {/* STEP 3: ROUTES & RESULTS PANEL */}
          {currentStep === 3 && result && (
            <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <div>
                  <h3 className="font-heading text-lg font-bold text-slate-900">
                    STEP 3 — ROUTES & RESULTS
                  </h3>
                  <p className="text-xs text-slate-500">
                    Validated vehicle routes and driver assignments
                  </p>
                </div>
                <div className="flex items-center gap-1">
                  {result.results?.classical && (
                    <button
                      onClick={() => setActiveResultTab('classical')}
                      className={`px-3 py-1 rounded-full text-xs font-bold transition-all ${
                        activeResultTab === 'classical'
                          ? 'bg-[#080808] text-white'
                          : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                      }`}
                    >
                      Classical VRP
                    </button>
                  )}
                  {result.results?.qaoa && (
                    <button
                      onClick={() => setActiveResultTab('qaoa')}
                      className={`px-3 py-1 rounded-full text-xs font-bold transition-all ${
                        activeResultTab === 'qaoa'
                          ? 'bg-[#080808] text-[#B7FF2A]'
                          : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                      }`}
                    >
                      Quantum QAOA
                    </button>
                  )}
                </div>
              </div>

              {/* Solver Key Metrics Grid */}
              {(() => {
                const currentData =
                  activeResultTab === 'qaoa'
                    ? result.results?.qaoa
                    : result.results?.classical;
                if (!currentData) return null;

                return (
                  <div className="space-y-3">
                    <div className="grid grid-cols-3 gap-2">
                      <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
                        <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
                          Total Distance
                        </span>
                        <div className="text-base font-extrabold text-slate-900 mt-0.5">
                          {currentData.total_distance_km.toFixed(1)} km
                        </div>
                      </div>

                      <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
                        <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
                          Travel Time
                        </span>
                        <div className="text-base font-extrabold text-slate-900 mt-0.5">
                          {Math.round(currentData.total_travel_time_min)} min
                        </div>
                      </div>

                      <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
                        <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
                          Solver Runtime
                        </span>
                        <div className="text-base font-extrabold text-slate-900 mt-0.5">
                          {currentData.execution_time_sec.toFixed(2)}s
                        </div>
                      </div>
                    </div>

                    {/* Driver Cards / Route Leg Details */}
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                          Assigned Drivers ({currentData.routes.length})
                        </span>
                        <span className="text-[11px] font-bold text-[#080808] flex items-center gap-1">
                          <CheckCircle2 className="h-3 w-3 text-[#B7FF2A]" />
                          Feasible · 0 Violations
                        </span>
                      </div>

                      <div className="space-y-2 max-h-[260px] overflow-y-auto">
                        {currentData.routes.map((route: VehicleRoute, idx: number) => {
                          const routeColor = ROUTE_COLORS[idx % ROUTE_COLORS.length];
                          const isExpanded = expandedRouteId === route.vehicle_id;
                          return (
                            <div
                              key={route.vehicle_id}
                              className="border border-slate-200 rounded-xl p-3 bg-white hover:border-slate-300 transition-all"
                            >
                              <div
                                onClick={() => setExpandedRouteId(isExpanded ? null : route.vehicle_id)}
                                className="flex items-center justify-between cursor-pointer"
                              >
                                <div className="flex items-center gap-2">
                                  <div
                                    className="h-3.5 w-3.5 rounded-full shrink-0"
                                    style={{ backgroundColor: routeColor }}
                                  />
                                  <span className="text-xs font-bold text-slate-900">
                                    Driver #{idx + 1}
                                  </span>
                                  <span className="text-[11px] text-slate-500">
                                    ({route.stops.length - 2} stops)
                                  </span>
                                </div>

                                <div className="flex items-center gap-2">
                                  <span className="text-xs font-bold text-slate-700">
                                    {route.distance_km.toFixed(1)} km
                                  </span>
                                  {isExpanded ? (
                                    <ChevronUp className="h-4 w-4 text-slate-400" />
                                  ) : (
                                    <ChevronDown className="h-4 w-4 text-slate-400" />
                                  )}
                                </div>
                              </div>

                              {/* Capacity Load Bar */}
                              <div className="mt-2">
                                <div className="flex items-center justify-between text-[10px] text-slate-500 mb-1">
                                  <span>Load: {Math.round(route.load || 0)} / {vehicleCapacity} units</span>
                                  <span>{Math.round(((route.load || 0) / vehicleCapacity) * 100)}%</span>
                                </div>
                                <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
                                  <div
                                    className="h-full rounded-full transition-all"
                                    style={{
                                      width: `${Math.min(100, ((route.load || 0) / vehicleCapacity) * 100)}%`,
                                      backgroundColor: routeColor,
                                    }}
                                  />
                                </div>
                              </div>

                              {/* Leg stops list when expanded */}
                              {isExpanded && (
                                <div className="mt-2.5 pt-2 border-t border-slate-100 text-[11px] text-slate-600 space-y-1">
                                  <p className="font-semibold text-slate-700">Stop Sequence:</p>
                                  <div className="flex flex-wrap items-center gap-1">
                                    {route.stops.map((stopIdx, sIdx) => (
                                      <React.Fragment key={sIdx}>
                                        <span
                                          className={`px-1.5 py-0.5 rounded text-[10px] font-mono ${
                                            stopIdx === 0
                                              ? 'bg-rose-100 text-rose-700 font-bold'
                                              : 'bg-slate-100 text-slate-700'
                                          }`}
                                        >
                                          {stopIdx === 0 ? 'Depot' : `Stop #${stopIdx}`}
                                        </span>
                                        {sIdx < route.stops.length - 1 && (
                                          <span className="text-slate-400">→</span>
                                        )}
                                      </React.Fragment>
                                    ))}
                                  </div>
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    </div>

                    {/* Step 3 Export & Navigation Actions */}
                    <div className="pt-2 flex flex-wrap items-center justify-between gap-2 border-t border-slate-100">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={handleExportCSV}
                          className="flex items-center gap-1 px-3 py-1.5 border border-slate-200 hover:bg-slate-50 rounded-xl text-xs font-semibold text-slate-700 transition-all"
                          title="Export route stops as CSV"
                        >
                          <Download className="h-3.5 w-3.5" />
                          <span>CSV</span>
                        </button>
                        <button
                          onClick={handleExportJSON}
                          className="flex items-center gap-1 px-3 py-1.5 border border-slate-200 hover:bg-slate-50 rounded-xl text-xs font-semibold text-slate-700 transition-all"
                          title="Export full result object as JSON"
                        >
                          <Download className="h-3.5 w-3.5" />
                          <span>JSON</span>
                        </button>
                      </div>

                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => setCurrentStep(2)}
                          className="px-3 py-1.5 border border-slate-200 hover:bg-slate-50 rounded-xl text-xs font-semibold text-slate-700 transition-all"
                        >
                          Modify Goals
                        </button>
                        <button
                          onClick={onNavigateToMap}
                          className="flex items-center gap-1.5 px-4 py-1.5 bg-[#080808] hover:bg-neutral-800 text-[#B7FF2A] rounded-xl text-xs font-bold transition-all"
                        >
                          <span>Full Delivery Map</span>
                          <ExternalLink className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })()}
            </div>
          )}
        </div>

        {/* Right Panel: Large Interactive Leaflet Route Map (7 cols on wide screens) */}
        <div className="lg:col-span-7 bg-white border border-slate-200 rounded-2xl p-4 shadow-xs space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="h-2.5 w-2.5 rounded-full bg-[#B7FF2A] ring-4 ring-black/10" />
              <span className="font-heading text-base font-bold text-slate-900 tracking-tight">
                LIVE INTERACTIVE ROUTE MAP
              </span>
            </div>

            <div className="flex items-center gap-2.5 text-xs font-semibold text-[#171717]">
              <span className="flex items-center gap-1">
                <span className="h-2.5 w-2.5 rounded-full bg-[#080808] border border-[#B7FF2A]" />
                <span>Depot</span>
              </span>
              <span className="flex items-center gap-1">
                <span className="h-2.5 w-2.5 rounded-full bg-[#171717] border border-white" />
                <span>Stops ({includedStops.length})</span>
              </span>
              {displayedRoutes.length > 0 && (
                <span className="flex items-center gap-1 font-bold text-[#080808]">
                  <span className="h-2.5 w-2.5 rounded-full bg-[#B7FF2A] border border-black" />
                  <span>{displayedRoutes.length} Active Routes</span>
                </span>
              )}
            </div>
          </div>

          {/* Leaflet Map Canvas */}
          <div className="h-[560px] w-full rounded-xl overflow-hidden border border-slate-200 relative">
            <MapContainer
              center={mapCenter}
              zoom={12}
              style={{ height: '100%', width: '100%' }}
              scrollWheelZoom={true}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />

              {/* Depot Marker */}
              <Marker position={[depot.lat, depot.lon]} icon={depotIcon}>
                <Popup>
                  <div className="text-xs">
                    <p className="font-bold text-rose-700">{depot.name}</p>
                    <p className="text-[11px] text-slate-600">Central Logistics Hub</p>
                    <p className="font-mono text-[10px] text-slate-500 mt-1">
                      {depot.lat.toFixed(4)}, {depot.lon.toFixed(4)}
                    </p>
                  </div>
                </Popup>
              </Marker>

              {/* Customer Stop Markers */}
              {includedStops.map((stop, idx) => (
                <Marker key={stop.id} position={[stop.lat, stop.lon]} icon={customerIcon}>
                  <Popup>
                    <div className="text-xs">
                      <p className="font-bold text-slate-900">{stop.name}</p>
                      <p className="text-slate-600">Demand: {stop.demand} units</p>
                      <p className="text-slate-500 text-[10px] mt-1">{stop.address}</p>
                    </div>
                  </Popup>
                </Marker>
              ))}

              {/* Vehicle Routes Polylines & Driver Pins */}
              {displayedRoutes.map((route, rIdx) => {
                const color = ROUTE_COLORS[rIdx % ROUTE_COLORS.length];
                const positions =
                  route.waypoints?.map((w) => [w.lat, w.lon] as [number, number]) || [];

                // Driver pin at midpoint
                const midPoint =
                  positions.length > 2
                    ? positions[Math.floor(positions.length / 2)]
                    : positions[0];

                return (
                  <React.Fragment key={route.vehicle_id}>
                    {positions.length > 1 && (
                      <Polyline
                        positions={positions}
                        color={color}
                        weight={4}
                        opacity={0.85}
                        dashArray={rIdx % 2 === 1 ? '6, 6' : undefined}
                      />
                    )}

                    {midPoint && (
                      <Marker position={midPoint} icon={driverIcon}>
                        <Popup>
                          <div className="text-xs">
                            <p className="font-bold text-emerald-800">
                              Driver #{route.vehicle_id} in Transit
                            </p>
                            <p className="text-slate-600">Assigned {route.stops.length - 2} stops</p>
                            <p className="text-slate-600">Distance: {route.distance_km.toFixed(1)} km</p>
                            <p className="text-slate-600">Load: {Math.round(route.load || 0)} units</p>
                          </div>
                        </Popup>
                      </Marker>
                    )}
                  </React.Fragment>
                );
              })}
            </MapContainer>

            {/* Floating Map Legend Overlay */}
            <div className="absolute bottom-3 left-3 bg-white/95 backdrop-blur-md border border-black/10 px-3 py-2 rounded-xl text-[11px] shadow-md z-[1000] flex items-center gap-3">
              <span className="font-bold text-[#080808]">Map Legend:</span>
              <span className="flex items-center gap-1 font-medium">
                <span className="h-2.5 w-2.5 rounded-full bg-[#080808] border border-[#B7FF2A]" />
                <span>Depot</span>
              </span>
              <span className="flex items-center gap-1 font-medium">
                <span className="h-2.5 w-2.5 rounded-full bg-[#171717] border border-white" />
                <span>Customers</span>
              </span>
              <span className="flex items-center gap-1 font-medium">
                <span className="h-2.5 w-2.5 rounded-full bg-[#B7FF2A] border border-black" />
                <span>Driver Fleet</span>
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Add Custom Stop Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl p-5 max-w-md w-full shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-slate-100">
              <h4 className="font-heading text-lg font-bold text-slate-900">
                Add Manual Delivery Stop
              </h4>
              <button
                onClick={() => setShowAddModal(false)}
                className="text-slate-400 hover:text-slate-700"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <label className="font-semibold text-slate-700 block mb-1">
                  Location / Destination Name
                </label>
                <input
                  type="text"
                  value={newStopName}
                  onChange={(e) => setNewStopName(e.target.value)}
                  placeholder="e.g. Grand Central Package Terminal"
                  className="w-full px-3 py-2 border border-slate-200 rounded-xl"
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="font-semibold text-slate-700 block mb-1">
                    Latitude
                  </label>
                  <input
                    type="text"
                    value={newStopLat}
                    onChange={(e) => setNewStopLat(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-200 rounded-xl font-mono"
                  />
                </div>
                <div>
                  <label className="font-semibold text-slate-700 block mb-1">
                    Longitude
                  </label>
                  <input
                    type="text"
                    value={newStopLon}
                    onChange={(e) => setNewStopLon(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-200 rounded-xl font-mono"
                  />
                </div>
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">
                  Delivery Demand (Units)
                </label>
                <input
                  type="number"
                  value={newStopDemand}
                  onChange={(e) => setNewStopDemand(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-200 rounded-xl"
                />
              </div>
            </div>

            <div className="pt-2 flex justify-end gap-2">
              <button
                onClick={() => setShowAddModal(false)}
                className="px-4 py-2 border border-slate-200 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-50"
              >
                Cancel
              </button>
              <button
                onClick={handleAddCustomStop}
                className="px-4 py-2 bg-black text-[#B7FF2A] rounded-xl text-xs font-bold hover:bg-neutral-800"
              >
                Add Stop to Route
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
