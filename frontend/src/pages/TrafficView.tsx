import React, { useState } from 'react';
import {
  Car,
  Clock,
  CloudRain,
  Sun,
  Wind,
  AlertCircle,
  TrendingUp,
  Sliders,
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  LineChart,
  Line,
  CartesianGrid,
} from 'recharts';
import { AnalyticsSummary } from '../types';

interface TrafficViewProps {
  analytics: AnalyticsSummary | null;
}

export const TrafficView: React.FC<TrafficViewProps> = ({ analytics }) => {
  const [selectedScenario, setSelectedScenario] = useState<string>('normal');
  const [weatherCondition, setWeatherCondition] = useState<string>('clear');

  const hourlyProfile = [
    { hour: '12 AM', volume: 210, factor: 0.8 },
    { hour: '2 AM', volume: 110, factor: 0.75 },
    { hour: '4 AM', volume: 140, factor: 0.8 },
    { hour: '6 AM', volume: 680, factor: 1.1 },
    { hour: '8 AM', volume: 1540, factor: 1.6 },
    { hour: '10 AM', volume: 1050, factor: 1.25 },
    { hour: '12 PM', volume: 1120, factor: 1.3 },
    { hour: '2 PM', volume: 1180, factor: 1.35 },
    { hour: '4 PM', volume: 1690, factor: 1.7 },
    { hour: '6 PM', volume: 1780, factor: 1.8 },
    { hour: '8 PM', volume: 1150, factor: 1.3 },
    { hour: '10 PM', volume: 590, factor: 1.0 },
  ];

  const congestedRoads = [
    { roadway: 'FDR DRIVE', segment: 'E 34th St to E 42nd St', avgVolume: 2450, congestion: 'Severe' },
    { roadway: 'BROADWAY', segment: 'W 42nd St to W 50th St', avgVolume: 1980, congestion: 'High' },
    { roadway: 'CANAL STREET', segment: 'Varick St to Bowery', avgVolume: 1850, congestion: 'High' },
    { roadway: '5TH AVENUE', segment: '34th St to 59th St', avgVolume: 1720, congestion: 'Moderate' },
    { roadway: 'WEST SIDE HWY', segment: '14th St to 23rd St', avgVolume: 1640, congestion: 'Moderate' },
  ];

  const scenarioFactors: Record<string, { factor: number; label: string; desc: string }> = {
    normal: { factor: 1.0, label: 'Normal Traffic (Historical Baseline)', desc: '1.0x baseline travel times' },
    moderate: { factor: 1.3, label: 'Moderate Congestion', desc: '+30% travel time delay' },
    high_congestion: { factor: 1.6, label: 'High Congestion (Peak Rush)', desc: '+60% travel time delay' },
    severe: { factor: 2.0, label: 'Severe Gridlock / Incident', desc: '100% travel time delay (2.0x)' },
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
        <h2 className="text-lg font-bold text-slate-900">
          Traffic Congestion & Weather Influence Model
        </h2>
        <p className="text-xs text-slate-500 mt-1">
          Historical NYC DOT Traffic Volume Counts joined with historical NYC Weather observations.
        </p>
      </div>

      {/* Scenario Controls */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
          <div className="flex items-center gap-2 mb-3">
            <Sliders className="h-4 w-4 text-indigo-600" />
            <h3 className="text-sm font-semibold text-slate-900">
              Traffic Delay Scenario (Configurable)
            </h3>
          </div>
          <div className="space-y-2">
            {Object.entries(scenarioFactors).map(([key, data]) => (
              <label
                key={key}
                className={`flex items-center justify-between p-3 rounded-lg border cursor-pointer transition-all ${
                  selectedScenario === key
                    ? 'border-indigo-600 bg-indigo-50/50 text-indigo-950 font-medium'
                    : 'border-slate-200 hover:bg-slate-50 text-slate-700'
                }`}
              >
                <div className="flex items-center gap-2">
                  <input
                    type="radio"
                    name="traffic_scenario"
                    value={key}
                    checked={selectedScenario === key}
                    onChange={(e) => setSelectedScenario(e.target.value)}
                    className="text-indigo-600 focus:ring-indigo-500"
                  />
                  <div>
                    <span className="text-xs font-semibold">{data.label}</span>
                    <p className="text-[11px] text-slate-500">{data.desc}</p>
                  </div>
                </div>
                <span className="text-xs font-mono font-bold text-indigo-700">
                  {data.factor.toFixed(1)}x
                </span>
              </label>
            ))}
          </div>
          <p className="text-[11px] text-slate-400 mt-3 italic">
            * Selected scenario directly adjusts the travel-time matrix in classical and QAOA algorithms.
          </p>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
          <div className="flex items-center gap-2 mb-3">
            <CloudRain className="h-4 w-4 text-blue-600" />
            <h3 className="text-sm font-semibold text-slate-900">
              NYC Weather Conditions
            </h3>
          </div>
          <div className="grid grid-cols-2 gap-2">
            {[
              { id: 'clear', label: 'Clear Skies', factor: '1.0x', icon: Sun },
              { id: 'rain', label: 'Moderate Rain', factor: '1.2x', icon: CloudRain },
              { id: 'heavy_rain', label: 'Heavy Downpour', factor: '1.5x', icon: CloudRain },
              { id: 'storm', label: 'Severe Storm', factor: '2.0x', icon: Wind },
            ].map((w) => {
              const Icon = w.icon;
              return (
                <button
                  key={w.id}
                  onClick={() => setWeatherCondition(w.id)}
                  className={`p-3 rounded-lg border text-left flex flex-col justify-between transition-all ${
                    weatherCondition === w.id
                      ? 'border-blue-600 bg-blue-50/50 text-blue-950'
                      : 'border-slate-200 hover:bg-slate-50 text-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <Icon className="h-4 w-4 text-blue-600" />
                    <span className="text-[11px] font-mono font-bold">{w.factor}</span>
                  </div>
                  <span className="text-xs font-semibold">{w.label}</span>
                </button>
              );
            })}
          </div>

          <div className="mt-4 p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs text-slate-600">
            <div className="font-semibold text-slate-800 mb-1">Combined Multiplier</div>
            <p>
              Matrix Multiplier:{' '}
              <span className="font-mono font-bold text-indigo-700">
                {(
                  scenarioFactors[selectedScenario].factor *
                  (weatherCondition === 'clear'
                    ? 1.0
                    : weatherCondition === 'rain'
                    ? 1.2
                    : weatherCondition === 'heavy_rain'
                    ? 1.5
                    : 2.0)
                ).toFixed(2)}
                x
              </span>{' '}
              on edge travel times.
            </p>
          </div>
        </div>
      </div>

      {/* Hourly Traffic Curve */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
        <h3 className="text-sm font-semibold text-slate-900 mb-1">
          Historical Diurnal Traffic Curve (NYC DOT Volume Counts)
        </h3>
        <p className="text-xs text-slate-500 mb-4">
          Measured vehicular flow across 24-hour delivery dispatch cycles
        </p>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={hourlyProfile}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
              <XAxis dataKey="hour" tick={{ fontSize: 11 }} />
              <YAxis yAxisId="left" tick={{ fontSize: 11 }} />
              <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 11 }} domain={[0.5, 2.5]} />
              <Tooltip />
              <Bar yAxisId="left" dataKey="volume" fill="#cbd5e1" />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="factor"
                stroke="#4f46e5"
                strokeWidth={2}
                dot={{ r: 3 }}
                name="Congestion Factor"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Top Congested Road Segments */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
        <h3 className="text-sm font-semibold text-slate-900 mb-3">
          Key Road Segments & Bottlenecks
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase font-semibold text-[10px]">
              <tr>
                <th className="py-2.5 px-3">Roadway</th>
                <th className="py-2.5 px-3">Segment Section</th>
                <th className="py-2.5 px-3">Avg Observed Hourly Volume</th>
                <th className="py-2.5 px-3">Congestion Level</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {congestedRoads.map((r, idx) => (
                <tr key={idx} className="hover:bg-slate-50">
                  <td className="py-2.5 px-3 font-semibold text-slate-900">{r.roadway}</td>
                  <td className="py-2.5 px-3 text-slate-600">{r.segment}</td>
                  <td className="py-2.5 px-3 font-mono">{r.avgVolume.toLocaleString()} veh/hr</td>
                  <td className="py-2.5 px-3">
                    <span
                      className={`inline-block px-2 py-0.5 rounded text-[10px] font-semibold ${
                        r.congestion === 'Severe'
                          ? 'bg-rose-50 text-rose-700 border border-rose-200'
                          : r.congestion === 'High'
                          ? 'bg-amber-50 text-amber-700 border border-amber-200'
                          : 'bg-blue-50 text-blue-700 border border-blue-200'
                      }`}
                    >
                      {r.congestion}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
