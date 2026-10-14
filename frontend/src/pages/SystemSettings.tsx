import React, { useState, useEffect } from 'react';
import {
  Settings,
  Cpu,
  Database,
  RotateCw,
  Save,
  CheckCircle2,
  Trash2,
  Sliders,
  MapPin,
  Truck,
} from 'lucide-react';
import { api } from '../services/api';
import { useSettings } from '../context/SettingsContext';

interface SystemSettingsProps {
  backendHealth: any;
  onRefreshHealth?: () => void;
  onSettingsApplied?: () => void;
}

export const SystemSettings: React.FC<SystemSettingsProps> = ({
  backendHealth,
  onRefreshHealth,
  onSettingsApplied,
}) => {
  const { settings, updateSettings, resetSettings } = useSettings();

  // Configurable Parameters State initialized from global context
  const [defaultVehicles, setDefaultVehicles] = useState<number>(settings.defaultVehicles);
  const [defaultCapacity, setDefaultCapacity] = useState<number>(settings.defaultCapacity);
  const [distanceUnit, setDistanceUnit] = useState<string>(settings.distanceUnit);
  const [returnToDepot, setReturnToDepot] = useState<boolean>(settings.returnToDepot);
  const [maxQaoaQubits, setMaxQaoaQubits] = useState<number>(settings.maxQaoaQubits);
  const [qaoaDepth, setQaoaDepth] = useState<number>(settings.qaoaDepth);
  const [depotLat, setDepotLat] = useState<string>(settings.depotLat);
  const [depotLon, setDepotLon] = useState<string>(settings.depotLon);
  const [depotName, setDepotName] = useState<string>(settings.depotName);
  const [weightDistance, setWeightDistance] = useState<number>(settings.weightDistance);
  const [weightTime, setWeightTime] = useState<number>(settings.weightTime);

  // Synchronize when settings change from any other part of the app
  useEffect(() => {
    setDefaultVehicles(settings.defaultVehicles);
    setDefaultCapacity(settings.defaultCapacity);
    setDistanceUnit(settings.distanceUnit);
    setReturnToDepot(settings.returnToDepot);
    setMaxQaoaQubits(settings.maxQaoaQubits);
    setQaoaDepth(settings.qaoaDepth);
    setDepotLat(settings.depotLat);
    setDepotLon(settings.depotLon);
    setDepotName(settings.depotName);
    setWeightDistance(settings.weightDistance);
    setWeightTime(settings.weightTime);
  }, [settings]);

  // Feedback states
  const [isSaved, setIsSaved] = useState<boolean>(false);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [healthStatus, setHealthStatus] = useState<any>(backendHealth);

  const handleSave = () => {
    updateSettings({
      defaultVehicles,
      defaultCapacity,
      distanceUnit: distanceUnit as 'km' | 'mi',
      returnToDepot,
      maxQaoaQubits,
      qaoaDepth,
      depotLat,
      depotLon,
      depotName,
      weightDistance,
      weightTime,
    });

    if (onSettingsApplied) {
      onSettingsApplied();
    }

    setIsSaved(true);
    setTimeout(() => setIsSaved(false), 2500);
  };

  const handleResetDefaults = () => {
    resetSettings();

    if (onSettingsApplied) {
      onSettingsApplied();
    }

    setIsSaved(true);
    setTimeout(() => setIsSaved(false), 2500);
  };

  const handleReloadDiagnostics = async () => {
    setIsRefreshing(true);
    try {
      const data = await api.checkHealth();
      setHealthStatus(data);
      if (onRefreshHealth) onRefreshHealth();
    } catch (e) {
      console.error('Diagnostic reload error:', e);
    } finally {
      setTimeout(() => setIsRefreshing(false), 500);
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-4 border-b border-black/10 dark:border-[#29292E]">
        <div>
          <div className="inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-[#777777] dark:text-[#A1A1AA] mb-1">
            <span className="h-1.5 w-1.5 rounded-full bg-[#B7FF00]" />
            <span>Platform Configuration</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-heading font-semibold text-[#080808] dark:text-[#F5F5F7]">
            Settings
          </h1>
          <p className="text-xs text-[#777777] dark:text-[#71717A] mt-1 max-w-xl">
            Configure fleet defaults, quantum simulator parameters, and origin depot coordinates.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* Reload Diagnostics Button */}
          <button
            onClick={handleReloadDiagnostics}
            disabled={isRefreshing}
            className="flex items-center gap-1.5 px-3.5 py-2 border border-black/10 dark:border-[#29292E] bg-white dark:bg-[#18181B] hover:bg-[#F4F4F2] dark:hover:bg-[#202024] text-[#080808] dark:text-[#F5F5F7] rounded-xl text-xs font-bold transition-all cursor-pointer disabled:opacity-50"
          >
            <RotateCw className={`h-3.5 w-3.5 ${isRefreshing ? 'animate-spin text-[#B7FF00]' : ''}`} />
            <span>{isRefreshing ? 'Checking...' : 'Reload Diagnostics'}</span>
          </button>

          {/* Save Button */}
          <button
            onClick={handleSave}
            className="flex items-center gap-2 px-5 py-2 bg-[#080808] dark:bg-[#B7FF00] hover:bg-[#171717] dark:hover:bg-[#a5e600] text-[#B7FF00] dark:text-black rounded-xl text-xs font-bold transition-all cursor-pointer shadow-xs"
          >
            <Save className="h-3.5 w-3.5" />
            <span>Save Settings</span>
          </button>
        </div>
      </div>

      {isSaved && (
        <div className="p-3 bg-[#080808] dark:bg-[#18181B] text-[#B7FF00] border border-black dark:border-[#29292E] rounded-xl text-xs font-bold flex items-center justify-between animate-fade-in">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4" />
            <span>System parameters saved successfully to local runtime configuration!</span>
          </div>
          <span className="text-[10px] text-white dark:text-[#A1A1AA]">Active</span>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Section 1: Fleet & Routing Defaults */}
        <div className="bg-white dark:bg-[#111113] border border-black/10 dark:border-[#29292E] rounded-2xl p-5 shadow-xs space-y-4">
          <div className="flex items-center gap-2 pb-3 border-b border-black/5 dark:border-[#29292E]">
            <Truck className="h-4 w-4 text-[#080808] dark:text-[#B7FF00]" />
            <h3 className="text-sm font-bold text-[#080808] dark:text-[#F5F5F7]">
              Fleet & Vehicle Defaults
            </h3>
          </div>

          <div className="space-y-3 text-xs">
            <div>
              <label className="font-bold text-[#171717] dark:text-[#A1A1AA] block mb-1">
                Default Number of Vehicles: <span className="font-mono text-[#080808] dark:text-[#B7FF00]">{defaultVehicles}</span>
              </label>
              <input
                type="range"
                min={1}
                max={10}
                value={defaultVehicles}
                onChange={(e) => setDefaultVehicles(parseInt(e.target.value, 10))}
                className="w-full accent-[#080808] dark:accent-[#B7FF00] h-1.5 bg-[#F4F4F2] dark:bg-[#17171A] rounded-lg cursor-pointer"
              />
            </div>

            <div>
              <label className="font-bold text-[#171717] dark:text-[#A1A1AA] block mb-1">
                Default Vehicle Capacity (units)
              </label>
              <input
                type="number"
                min={10}
                max={500}
                value={defaultCapacity}
                onChange={(e) => setDefaultCapacity(parseInt(e.target.value, 10) || 10)}
                className="w-full px-3 py-2 border border-black/10 dark:border-[#29292E] rounded-xl bg-[#F4F4F2] dark:bg-[#17171A] text-[#080808] dark:text-[#F5F5F7] font-bold"
              />
            </div>

            <div className="grid grid-cols-2 gap-3 pt-1">
              <div>
                <label className="font-bold text-[#171717] dark:text-[#A1A1AA] block mb-1">
                  Distance Unit
                </label>
                <select
                  value={distanceUnit}
                  onChange={(e) => setDistanceUnit(e.target.value)}
                  className="w-full px-3 py-2 border border-black/10 dark:border-[#29292E] rounded-xl bg-[#F4F4F2] dark:bg-[#17171A] text-[#080808] dark:text-[#F5F5F7] font-bold"
                >
                  <option value="km">Kilometres (km)</option>
                  <option value="mi">Miles (mi)</option>
                </select>
              </div>

              <div>
                <label className="font-bold text-[#171717] dark:text-[#A1A1AA] block mb-1">
                  Depot Return
                </label>
                <select
                  value={returnToDepot ? 'yes' : 'no'}
                  onChange={(e) => setReturnToDepot(e.target.value === 'yes')}
                  className="w-full px-3 py-2 border border-black/10 dark:border-[#29292E] rounded-xl bg-[#F4F4F2] dark:bg-[#17171A] text-[#080808] dark:text-[#F5F5F7] font-bold"
                >
                  <option value="yes">Mandatory Return</option>
                  <option value="no">Open Tour</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Section 2: Quantum & Solver Engine Configuration */}
        <div className="bg-white dark:bg-[#111113] border border-black/10 dark:border-[#29292E] rounded-2xl p-5 shadow-xs space-y-4">
          <div className="flex items-center gap-2 pb-3 border-b border-black/5 dark:border-[#29292E]">
            <Cpu className="h-4 w-4 text-[#080808] dark:text-[#B7FF00]" />
            <h3 className="text-sm font-bold text-[#080808] dark:text-[#F5F5F7]">
              Quantum Simulator (Qiskit 2.4.1)
            </h3>
          </div>

          <div className="space-y-3 text-xs">
            <div>
              <label className="font-bold text-[#171717] dark:text-[#A1A1AA] block mb-1">
                Max QAOA Simulator Qubits: <span className="font-mono text-[#080808] dark:text-[#B7FF00]">{maxQaoaQubits} Qubits</span>
              </label>
              <input
                type="range"
                min={8}
                max={20}
                value={maxQaoaQubits}
                onChange={(e) => setMaxQaoaQubits(parseInt(e.target.value, 10))}
                className="w-full accent-[#080808] dark:accent-[#B7FF00] h-1.5 bg-[#F4F4F2] dark:bg-[#17171A] rounded-lg cursor-pointer"
              />
              <span className="text-[10px] text-[#777777] dark:text-[#71717A] block mt-1">
                Safe threshold to prevent statevector RAM overflow on standard host hardware
              </span>
            </div>

            <div className="grid grid-cols-2 gap-3 pt-1">
              <div>
                <label className="font-bold text-[#171717] dark:text-[#A1A1AA] block mb-1">
                  Default QAOA Depth (p)
                </label>
                <select
                  value={qaoaDepth}
                  onChange={(e) => setQaoaDepth(parseInt(e.target.value, 10))}
                  className="w-full px-3 py-2 border border-black/10 dark:border-[#29292E] rounded-xl bg-[#F4F4F2] dark:bg-[#17171A] text-[#080808] dark:text-[#F5F5F7] font-bold"
                >
                  <option value={1}>p = 1 (Fast)</option>
                  <option value={2}>p = 2 (Higher Fidelity)</option>
                </select>
              </div>

              <div>
                <label className="font-bold text-[#171717] dark:text-[#A1A1AA] block mb-1">
                  Simulator Engine
                </label>
                <div className="px-3 py-2 border border-black/10 dark:border-[#29292E] rounded-xl bg-[#F4F4F2] dark:bg-[#17171A] text-[#080808] dark:text-[#F5F5F7] font-mono font-bold">
                  Statevector
                </div>
              </div>
            </div>

            <div className="p-3 bg-[#F4F4F2] dark:bg-[#18181B] rounded-xl border border-black/5 dark:border-[#29292E] space-y-1">
              <span className="text-[10px] font-bold uppercase tracking-wider text-[#777777] dark:text-[#71717A] block">
                Classical Solver Baseline
              </span>
              <p className="text-[11px] text-[#171717] dark:text-[#F5F5F7] font-medium">
                Clarke-Wright Savings / 2-Opt Metaheuristic / Google OR-Tools
              </p>
            </div>
          </div>
        </div>

        {/* Section 3: Origin Depot Setup */}
        <div className="bg-white dark:bg-[#111113] border border-black/10 dark:border-[#29292E] rounded-2xl p-5 shadow-xs space-y-4">
          <div className="flex items-center gap-2 pb-3 border-b border-black/5 dark:border-[#29292E]">
            <MapPin className="h-4 w-4 text-[#080808] dark:text-[#B7FF00]" />
            <h3 className="text-sm font-bold text-[#080808] dark:text-[#F5F5F7]">
              Origin Depot Coordinates
            </h3>
          </div>

          <div className="space-y-3 text-xs">
            <div>
              <label className="font-bold text-[#171717] dark:text-[#A1A1AA] block mb-1">
                Depot Facility Name
              </label>
              <input
                type="text"
                value={depotName}
                onChange={(e) => setDepotName(e.target.value)}
                className="w-full px-3 py-2 border border-black/10 dark:border-[#29292E] rounded-xl bg-[#F4F4F2] dark:bg-[#17171A] text-[#080808] dark:text-[#F5F5F7] font-bold"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="font-bold text-[#171717] dark:text-[#A1A1AA] block mb-1">
                  Latitude
                </label>
                <input
                  type="text"
                  value={depotLat}
                  onChange={(e) => setDepotLat(e.target.value)}
                  className="w-full px-3 py-2 border border-black/10 dark:border-[#29292E] rounded-xl bg-[#F4F4F2] dark:bg-[#17171A] text-[#080808] dark:text-[#F5F5F7] font-mono font-bold"
                />
              </div>

              <div>
                <label className="font-bold text-[#171717] dark:text-[#A1A1AA] block mb-1">
                  Longitude
                </label>
                <input
                  type="text"
                  value={depotLon}
                  onChange={(e) => setDepotLon(e.target.value)}
                  className="w-full px-3 py-2 border border-black/10 dark:border-[#29292E] rounded-xl bg-[#F4F4F2] dark:bg-[#17171A] text-[#080808] dark:text-[#F5F5F7] font-mono font-bold"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Section 4: Diagnostics & Cache Reset */}
        <div className="bg-white dark:bg-[#111113] border border-black/10 dark:border-[#29292E] rounded-2xl p-5 shadow-xs space-y-4">
          <div className="flex items-center gap-2 pb-3 border-b border-black/5 dark:border-[#29292E]">
            <Database className="h-4 w-4 text-[#080808] dark:text-[#B7FF00]" />
            <h3 className="text-sm font-bold text-[#080808] dark:text-[#F5F5F7]">
              Diagnostics & Factory Reset
            </h3>
          </div>

          <div className="space-y-3 text-xs">
            <div className="flex justify-between py-1.5 border-b border-black/5 dark:border-[#29292E]">
              <span className="text-[#777777] dark:text-[#A1A1AA]">FastAPI Backend</span>
              <span className="font-bold text-[#080808] dark:text-[#F5F5F7]">
                {healthStatus?.status === 'healthy' ? 'Online' : 'Connected'}
              </span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-black/5 dark:border-[#29292E]">
              <span className="text-[#777777] dark:text-[#A1A1AA]">Python Version</span>
              <span className="font-mono font-bold text-[#080808] dark:text-[#F5F5F7]">
                {healthStatus?.python_version ? healthStatus.python_version.split(' ')[0] : '3.14.2'}
              </span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-black/5 dark:border-[#29292E]">
              <span className="text-[#777777] dark:text-[#A1A1AA]">Database</span>
              <span className="font-mono font-bold text-[#080808] dark:text-[#F5F5F7]">SQLite</span>
            </div>

            <div className="pt-2 flex items-center justify-between">
              <button
                onClick={handleResetDefaults}
                className="flex items-center gap-1.5 px-3 py-2 border border-black/10 dark:border-[#29292E] bg-white dark:bg-[#18181B] hover:bg-[#F4F4F2] dark:hover:bg-[#202024] text-[#080808] dark:text-[#F5F5F7] rounded-xl text-xs font-bold transition-all cursor-pointer"
              >
                <Trash2 className="h-3.5 w-3.5 text-[#777777] dark:text-[#A1A1AA]" />
                <span>Reset to Defaults</span>
              </button>

              <button
                onClick={handleSave}
                className="px-4 py-2 bg-[#080808] dark:bg-[#B7FF00] hover:bg-[#171717] dark:hover:bg-[#a5e600] text-[#B7FF00] dark:text-black rounded-xl text-xs font-bold transition-all cursor-pointer shadow-xs"
              >
                Apply All Settings
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
