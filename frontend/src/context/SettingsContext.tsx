import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export interface AppSettings {
  defaultVehicles: number;
  defaultCapacity: number;
  distanceUnit: 'km' | 'mi';
  returnToDepot: boolean;
  maxQaoaQubits: number;
  qaoaDepth: number;
  depotLat: string;
  depotLon: string;
  depotName: string;
  weightDistance: number;
  weightTime: number;
}

export const DEFAULT_SETTINGS: AppSettings = {
  defaultVehicles: 2,
  defaultCapacity: 50,
  distanceUnit: 'km',
  returnToDepot: true,
  maxQaoaQubits: 20,
  qaoaDepth: 1,
  depotLat: '40.7580',
  depotLon: '-73.8292',
  depotName: 'Main NYC Logistics Hub',
  weightDistance: 1.0,
  weightTime: 0.5,
};

interface SettingsContextType {
  settings: AppSettings;
  updateSettings: (partial: Partial<AppSettings>) => void;
  resetSettings: () => void;
}

const SettingsContext = createContext<SettingsContextType | undefined>(undefined);

const loadSettingsFromStorage = (): AppSettings => {
  try {
    const rawVehicles =
      localStorage.getItem('routeiq_default_vehicles') ||
      localStorage.getItem('routeiq_num_vehicles');
    const parsedVehicles = rawVehicles ? parseInt(rawVehicles, 10) : NaN;

    const rawCapacity =
      localStorage.getItem('routeiq_default_capacity') ||
      localStorage.getItem('routeiq_vehicle_capacity');
    const parsedCapacity = rawCapacity ? parseInt(rawCapacity, 10) : NaN;

    const rawUnit = localStorage.getItem('routeiq_distance_unit');
    const rawReturn = localStorage.getItem('routeiq_return_to_depot');
    const rawQubits = localStorage.getItem('routeiq_max_qaoa_qubits');
    const rawDepth = localStorage.getItem('routeiq_qaoa_depth');
    const rawDepotLat = localStorage.getItem('routeiq_depot_lat');
    const rawDepotLon = localStorage.getItem('routeiq_depot_lon');
    const rawDepotName = localStorage.getItem('routeiq_depot_name');
    const rawWeightDist = localStorage.getItem('routeiq_w_distance');
    const rawWeightTime = localStorage.getItem('routeiq_w_time');

    return {
      defaultVehicles: !isNaN(parsedVehicles) && parsedVehicles > 0 ? parsedVehicles : DEFAULT_SETTINGS.defaultVehicles,
      defaultCapacity: !isNaN(parsedCapacity) && parsedCapacity > 0 ? parsedCapacity : DEFAULT_SETTINGS.defaultCapacity,
      distanceUnit: rawUnit === 'mi' ? 'mi' : 'km',
      returnToDepot: rawReturn !== null ? rawReturn !== 'false' : DEFAULT_SETTINGS.returnToDepot,
      maxQaoaQubits: rawQubits ? parseInt(rawQubits, 10) || 20 : DEFAULT_SETTINGS.maxQaoaQubits,
      qaoaDepth: rawDepth ? parseInt(rawDepth, 10) || 1 : DEFAULT_SETTINGS.qaoaDepth,
      depotLat: rawDepotLat || DEFAULT_SETTINGS.depotLat,
      depotLon: rawDepotLon || DEFAULT_SETTINGS.depotLon,
      depotName: rawDepotName || DEFAULT_SETTINGS.depotName,
      weightDistance: rawWeightDist ? parseFloat(rawWeightDist) || 1.0 : DEFAULT_SETTINGS.weightDistance,
      weightTime: rawWeightTime ? parseFloat(rawWeightTime) || 0.5 : DEFAULT_SETTINGS.weightTime,
    };
  } catch (err) {
    console.error('Failed to load settings from storage:', err);
    return DEFAULT_SETTINGS;
  }
};

const saveSettingsToStorage = (s: AppSettings) => {
  try {
    localStorage.setItem('routeiq_default_vehicles', s.defaultVehicles.toString());
    localStorage.setItem('routeiq_num_vehicles', s.defaultVehicles.toString());
    localStorage.setItem('routeiq_default_capacity', s.defaultCapacity.toString());
    localStorage.setItem('routeiq_vehicle_capacity', s.defaultCapacity.toString());
    localStorage.setItem('routeiq_distance_unit', s.distanceUnit);
    localStorage.setItem('routeiq_return_to_depot', s.returnToDepot.toString());
    localStorage.setItem('routeiq_max_qaoa_qubits', s.maxQaoaQubits.toString());
    localStorage.setItem('routeiq_qaoa_depth', s.qaoaDepth.toString());
    localStorage.setItem('routeiq_depot_lat', s.depotLat);
    localStorage.setItem('routeiq_depot_lon', s.depotLon);
    localStorage.setItem('routeiq_depot_name', s.depotName);
    localStorage.setItem('routeiq_w_distance', s.weightDistance.toString());
    localStorage.setItem('routeiq_w_time', s.weightTime.toString());

    window.dispatchEvent(
      new CustomEvent('routeiq_settings_updated', {
        detail: {
          vehicles: s.defaultVehicles,
          capacity: s.defaultCapacity,
          depotLat: parseFloat(s.depotLat),
          depotLon: parseFloat(s.depotLon),
          depotName: s.depotName,
          weightDistance: s.weightDistance,
          weightTime: s.weightTime,
          qaoaDepth: s.qaoaDepth,
          distanceUnit: s.distanceUnit,
          returnToDepot: s.returnToDepot,
          maxQaoaQubits: s.maxQaoaQubits,
        },
      })
    );
  } catch (err) {
    console.error('Failed to persist settings:', err);
  }
};

export const SettingsProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [settings, setSettings] = useState<AppSettings>(loadSettingsFromStorage);

  const updateSettings = (partial: Partial<AppSettings>) => {
    setSettings((prev) => {
      const next = { ...prev, ...partial };
      saveSettingsToStorage(next);
      return next;
    });
  };

  const resetSettings = () => {
    saveSettingsToStorage(DEFAULT_SETTINGS);
    setSettings(DEFAULT_SETTINGS);
  };

  // Sync across windows or storage changes
  useEffect(() => {
    const handleStorage = (e: StorageEvent) => {
      if (e.key && e.key.startsWith('routeiq_')) {
        setSettings(loadSettingsFromStorage());
      }
    };
    window.addEventListener('storage', handleStorage);
    return () => window.removeEventListener('storage', handleStorage);
  }, []);

  return (
    <SettingsContext.Provider value={{ settings, updateSettings, resetSettings }}>
      {children}
    </SettingsContext.Provider>
  );
};

export const useSettings = (): SettingsContextType => {
  const context = useContext(SettingsContext);
  if (!context) {
    throw new Error('useSettings must be used within a SettingsProvider');
  }
  return context;
};
