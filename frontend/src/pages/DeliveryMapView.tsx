import React, { useState } from 'react';
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Polyline,
} from 'react-leaflet';
import L from 'leaflet';
import {
  Filter,
} from 'lucide-react';
import { VehicleRoute } from '../types';

// Custom Map Pins matching strict palette (#080808, #B7FF2A, #171717, #FFFFFF)
const createMapPin = (bg: string, border: string, text: string, textColor: string) => {
  return L.divIcon({
    className: 'custom-map-pin',
    html: `<div style="background-color: ${bg}; border: 2px solid ${border}; color: ${textColor}; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 800; font-family: Inter, sans-serif; box-shadow: 0 4px 10px rgba(0,0,0,0.35);">${text}</div>`,
    iconSize: [28, 28],
    iconAnchor: [14, 14],
    popupAnchor: [0, -16],
  });
};

const depotIcon = createMapPin('#080808', '#B7FF2A', 'D', '#B7FF2A');
const customerIcon = createMapPin('#171717', '#FFFFFF', 'C', '#FFFFFF');

const ROUTE_COLORS = ['#080808', '#B7FF2A', '#171717', '#A4F51B', '#777777'];

interface MapViewProps {
  routes?: VehicleRoute[];
  depot?: { lat: number; lon: number };
  customerLocations?: Array<{ lat: number; lon: number; demand: number }>;
}

export const DeliveryMapView: React.FC<MapViewProps> = ({
  routes = [],
  depot = { lat: 40.7580, lon: -73.8292 },
  customerLocations = [],
}) => {
  const [selectedVehicle, setSelectedVehicle] = useState<number | 'all'>('all');

  const filteredRoutes =
    selectedVehicle === 'all'
      ? routes
      : routes.filter((r) => r.vehicle_id === selectedVehicle);

  const totalDistance = filteredRoutes.reduce((acc, r) => acc + (r.distance_km || 0), 0);

  return (
    <div className="space-y-4 pb-12">
      {/* Map Header & Controls */}
      <div className="bg-white border border-black/10 rounded-2xl p-4 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div>
          <h2 className="text-base font-bold text-[#080808]">
            Interactive Delivery Map
          </h2>
          <p className="text-xs text-[#777777]">
            Real GPS coordinates in NYC Metro area. Depot serving active customer clusters.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {routes.length > 0 && (
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-[#777777]" />
              <select
                value={selectedVehicle}
                onChange={(e) =>
                  setSelectedVehicle(e.target.value === 'all' ? 'all' : Number(e.target.value))
                }
                className="px-3 py-1.5 text-xs font-bold border border-black/10 rounded-xl bg-white text-[#080808]"
              >
                <option value="all">All Vehicles ({routes.length})</option>
                {routes.map((r, idx) => {
                  const dNum = idx + 1;
                  return (
                    <option key={`select-v-${dNum}-${idx}`} value={dNum}>
                      Driver #{dNum} ({r.distance_km.toFixed(1)} km)
                    </option>
                  );
                })}
              </select>
            </div>
          )}

          <div className="flex items-center gap-2 text-xs text-[#080808] bg-[#F4F4F2] px-3 py-1.5 rounded-xl border border-black/5 font-mono">
            <span>Planned Distance: <strong>{totalDistance.toFixed(2)} km</strong></span>
          </div>
        </div>
      </div>

      {/* Map Canvas and Sequence Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {/* Leaflet Map (75% width on large screens) */}
        <div className="lg:col-span-3 bg-white border border-black/10 rounded-2xl p-2 shadow-xs h-[580px] relative">
          <MapContainer
            center={[depot.lat, depot.lon]}
            zoom={12}
            scrollWheelZoom={true}
            className="h-full w-full rounded-xl"
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            {/* Depot Marker */}
            <Marker position={[depot.lat, depot.lon]} icon={depotIcon}>
              <Popup>
                <div className="text-xs font-sans">
                  <strong className="text-[#080808] font-bold">Central Logistics Depot</strong>
                  <br />
                  <span className="font-mono text-[#777777]">
                    {depot.lat.toFixed(4)}, {depot.lon.toFixed(4)}
                  </span>
                </div>
              </Popup>
            </Marker>

            {/* Customer Markers */}
            {customerLocations.map((c, i) => (
              <Marker key={i} position={[c.lat, c.lon]} icon={customerIcon}>
                <Popup>
                  <div className="text-xs font-sans">
                    <strong className="text-[#080808]">Customer Stop #{i + 1}</strong>
                    <br />
                    <span>Demand: {c.demand} units</span>
                  </div>
                </Popup>
              </Marker>
            ))}

            {/* Route Polylines */}
            {filteredRoutes.map((route, idx) => {
              const color = ROUTE_COLORS[idx % ROUTE_COLORS.length];
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
                    weight: 4,
                    opacity: 0.9,
                    dashArray: idx % 2 === 1 ? '5, 5' : undefined,
                  }}
                >
                  <Popup>
                    <div className="text-xs font-sans">
                      <strong className="text-[#080808]">Driver #{route.vehicle_id} Route</strong>
                      <br />
                      <span>Distance: {route.distance_km.toFixed(1)} km</span>
                    </div>
                  </Popup>
                </Polyline>
              );
            })}
          </MapContainer>

          {/* Map Legend Overlay */}
          <div className="absolute bottom-4 left-4 bg-white/95 backdrop-blur-md border border-black/10 px-3 py-2 rounded-xl text-[11px] shadow-md z-[1000] flex items-center gap-3">
            <span className="font-bold text-[#080808]">Legend:</span>
            <span className="flex items-center gap-1 font-medium">
              <span className="h-2.5 w-2.5 rounded-full bg-[#080808] border border-[#B7FF2A]" />
              <span>Depot</span>
            </span>
            <span className="flex items-center gap-1 font-medium">
              <span className="h-2.5 w-2.5 rounded-full bg-[#171717] border border-white" />
              <span>Customer Stop</span>
            </span>
            <span className="flex items-center gap-1 font-medium">
              <span className="h-2.5 w-2.5 rounded-full bg-[#B7FF2A] border border-black" />
              <span>Active Route</span>
            </span>
          </div>
        </div>

        {/* Route Sequence & Stops Panel (25% width) */}
        <div className="bg-white border border-black/10 rounded-2xl p-4 shadow-xs space-y-3 flex flex-col justify-between h-[580px]">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-[#080808] pb-2 border-b border-black/5">
              Assigned Route Sequences
            </h3>

            <div className="space-y-2 mt-3 overflow-y-auto max-h-[460px]">
              {filteredRoutes.length === 0 ? (
                <div className="text-center py-12 text-[#777777] text-xs">
                  <p>No active route solution yet.</p>
                  <p className="mt-1">Execute solver in Optimize workstation to view routes.</p>
                </div>
              ) : (
                filteredRoutes.map((route, idx) => {
                  const dNum = idx + 1;
                  return (
                    <div
                      key={`delivery-route-${dNum}-${idx}`}
                      className="p-3 rounded-xl border border-black/5 bg-[#F4F4F2] space-y-1.5"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div
                            className="h-3 w-3 rounded-full"
                            style={{ backgroundColor: ROUTE_COLORS[idx % ROUTE_COLORS.length] }}
                          />
                          <span className="text-xs font-bold text-[#080808]">
                            Driver #{dNum}
                          </span>
                        </div>
                        <span className="text-xs font-mono font-bold text-[#080808]">
                          {route.distance_km.toFixed(1)} km
                        </span>
                      </div>

                    <div className="text-[11px] text-[#777777]">
                      <span>{route.stops?.length || 0} stops sequence: </span>
                      <span className="font-mono text-[#080808]">
                        {route.stops?.join(' → ') || 'Depot'}
                      </span>
                    </div>
                  </div>
                );
              })
            )}
            </div>
          </div>

          <div className="p-3 rounded-xl bg-[#080808] text-white text-[11px] font-bold flex items-center justify-between">
            <span>Vehicles Dispatched</span>
            <span className="text-[#B7FF2A]">{filteredRoutes.length} Drivers</span>
          </div>
        </div>
      </div>
    </div>
  );
};
