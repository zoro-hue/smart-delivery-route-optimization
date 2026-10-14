import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import {
  History,
  Download,
  Trash2,
  Eye,
  CheckCircle2,
  XCircle,
  FileText,
  RotateCw,
  X,
} from 'lucide-react';
import { api } from '../services/api';

interface ExperimentHistoryProps {
  isActive?: boolean;
}

const formatTimestamp = (ts?: string | null) => {
  if (!ts) return 'N/A';
  try {
    const raw = String(ts).trim();
    // Ensure UTC indicator 'Z' so browser parses as UTC and displays user's proper local time
    const dateStr =
      raw.includes('Z') || raw.includes('+') || (raw.includes('-') && raw.length > 20)
        ? raw
        : `${raw.replace(' ', 'T')}Z`;
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) return raw;
    return date.toLocaleString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true,
    });
  } catch {
    return ts;
  }
};

export const ExperimentHistory: React.FC<ExperimentHistoryProps> = ({ isActive = true }) => {
  const [experiments, setExperiments] = useState<any[]>([]);
  const [selectedExp, setSelectedExp] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [viewingId, setViewingId] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [toastMsg, setToastMsg] = useState<string | null>(null);

  const fetchExperiments = async () => {
    setIsLoading(true);
    try {
      const data = await api.getExperiments(1, 50);
      setExperiments(data);
    } catch (err: any) {
      console.error('Failed to load experiments', err);
    } finally {
      setTimeout(() => setIsLoading(false), 300);
    }
  };

  useEffect(() => {
    if (isActive) {
      fetchExperiments();
    }
  }, [isActive]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && selectedExp) {
        setSelectedExp(null);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedExp]);

  const handleView = async (id: string) => {
    setViewingId(id);
    try {
      const details = await api.getExperimentDetails(id);
      setSelectedExp(details);
    } catch (err: any) {
      alert(`Failed to load experiment: ${err.response?.data?.detail || err.message}`);
    } finally {
      setViewingId(null);
    }
  };

  const handleDelete = async (id: string) => {
    if (deletingId) return;
    setDeletingId(id);
    const previous = [...experiments];
    setExperiments((prev) => prev.filter((e) => e.id !== id));
    if (selectedExp?.id === id) setSelectedExp(null);

    try {
      await api.deleteExperiment(id);
      setToastMsg('Experiment successfully deleted from database.');
      setTimeout(() => setToastMsg(null), 3500);
      await fetchExperiments();
    } catch (err: any) {
      console.error('Delete experiment error:', err);
      setExperiments(previous);
      alert(`Delete error: ${err.response?.data?.detail || err.message}`);
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-4 border-b border-black/10 dark:border-[#29292E]">
        <div>
          <div className="inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-[#777777] dark:text-[#A1A1AA] mb-1">
            <span className="h-1.5 w-1.5 rounded-full bg-[#B7FF00]" />
            <span>Audit & Benchmark Records</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-heading font-semibold text-[#080808] dark:text-[#F5F5F7]">
            Experiments
          </h1>
          <p className="text-xs text-[#777777] dark:text-[#71717A] mt-1 max-w-xl">
            Complete database of past classical and quantum optimization benchmark runs.
          </p>
        </div>

        <button
          onClick={fetchExperiments}
          disabled={isLoading}
          className="flex items-center gap-1.5 px-3 py-1.5 border border-black/10 dark:border-[#29292E] bg-white dark:bg-[#18181B] hover:bg-[#F4F4F2] dark:hover:bg-[#202024] rounded-xl text-xs font-bold text-[#080808] dark:text-[#F5F5F7] transition-all cursor-pointer disabled:opacity-50"
          title="Refresh History"
        >
          <RotateCw className={`h-3.5 w-3.5 ${isLoading ? 'animate-spin text-[#B7FF00]' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Toast Feedback Alert */}
      {toastMsg && (
        <div className="flex items-center gap-2 p-3 rounded-xl bg-[#22C55E]/15 border border-[#22C55E]/40 text-xs font-semibold text-[#080808] dark:text-[#B7FF00] animate-fadeIn">
          <CheckCircle2 className="h-4 w-4 text-[#22C55E] shrink-0" />
          <span>{toastMsg}</span>
        </div>
      )}

      {/* History Table */}
      <div className="bg-white dark:bg-[#111113] border border-black/10 dark:border-[#29292E] rounded-2xl shadow-xs overflow-hidden">
        <div className="px-5 py-3 border-b border-black/5 dark:border-[#29292E] bg-[#F4F4F2] dark:bg-[#18181B] flex items-center justify-between">
          <h3 className="text-xs font-bold uppercase tracking-wider text-[#080808] dark:text-[#F5F5F7]">
            Recorded Optimization Trials ({experiments.length})
          </h3>
        </div>

        {experiments.length === 0 ? (
          <div className="p-8 text-center text-[#777777] dark:text-[#A1A1AA]">
            <History className="h-8 w-8 mx-auto mb-2 text-[#777777]/50" />
            <p className="text-xs font-bold text-[#080808] dark:text-[#F5F5F7]">No saved optimization experiments found.</p>
            <p className="text-[11px] text-[#777777] dark:text-[#71717A] mt-1">
              Run route optimizations to record persistent experiment trials.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-white dark:bg-[#18181B] border-b border-black/5 dark:border-[#29292E] text-[#777777] dark:text-[#A1A1AA] font-bold text-[10px] uppercase">
                <tr>
                  <th className="py-2.5 px-3">Experiment ID</th>
                  <th className="py-2.5 px-3">Date / Timestamp</th>
                  <th className="py-2.5 px-3">Algorithm</th>
                  <th className="py-2.5 px-3">Customers</th>
                  <th className="py-2.5 px-3">Vehicles</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-black/5 dark:divide-[#29292E] text-[#171717] dark:text-[#F5F5F7]">
                {experiments.map((exp) => (
                  <tr key={exp.id} className="hover:bg-[#F4F4F2]/50 dark:hover:bg-[#18181B]/80 transition-colors">
                    <td className="py-2.5 px-3 font-mono font-bold text-[#080808] dark:text-[#F5F5F7]">
                      {exp.id.slice(0, 8)}...
                    </td>
                    <td className="py-2.5 px-3 text-[#777777] dark:text-[#A1A1AA] font-mono whitespace-nowrap">
                      {formatTimestamp(exp.timestamp)}
                    </td>
                    <td className="py-2.5 px-3 font-bold capitalize text-[#080808] dark:text-[#F5F5F7]">
                      {exp.algorithm}
                    </td>
                    <td className="py-2.5 px-3 font-bold">{exp.num_customers}</td>
                    <td className="py-2.5 px-3 font-bold">{exp.num_vehicles}</td>
                    <td className="py-2.5 px-3">
                      <span
                        className={`inline-block px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                          exp.status === 'completed'
                            ? 'bg-[#080808] dark:bg-[#B7FF00] text-[#B7FF00] dark:text-black'
                            : 'bg-[#F4F4F2] dark:bg-[#202024] text-[#777777] dark:text-[#A1A1AA]'
                        }`}
                      >
                        {exp.status}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-right space-x-1">
                      <button
                        onClick={() => handleView(exp.id)}
                        disabled={viewingId === exp.id}
                        className="p-1.5 rounded-lg text-[#080808] dark:text-[#F5F5F7] hover:bg-black/5 dark:hover:bg-[#202024] hover:text-[#22C55E] dark:hover:text-[#B7FF00] transition-colors cursor-pointer disabled:opacity-50"
                        title="View Details"
                      >
                        {viewingId === exp.id ? (
                          <RotateCw className="h-4 w-4 inline animate-spin text-[#B7FF00]" />
                        ) : (
                          <Eye className="h-4 w-4 inline" />
                        )}
                      </button>
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(exp.id);
                        }}
                        disabled={deletingId === exp.id}
                        className="p-1.5 rounded-lg text-[#777777] dark:text-[#71717A] hover:bg-red-50 dark:hover:bg-red-950/30 hover:text-red-600 dark:hover:text-red-400 transition-colors cursor-pointer disabled:opacity-50"
                        title="Delete experiment"
                      >
                        {deletingId === exp.id ? (
                          <RotateCw className="h-4 w-4 inline animate-spin text-red-500" />
                        ) : (
                          <Trash2 className="h-4 w-4 inline" />
                        )}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Selected Experiment Modal */}
      {selectedExp &&
        createPortal(
          <div
            className="fixed inset-0 bg-black/40 backdrop-blur-[2px] flex items-center justify-center p-4 sm:p-6 z-[99999] transition-opacity duration-150 animate-fadeIn"
            onClick={() => setSelectedExp(null)}
          >
            <div
              className="bg-white dark:bg-[#111113] border border-black/10 dark:border-[#29292E] rounded-3xl max-w-3xl w-full p-6 sm:p-8 shadow-2xl dark:shadow-[0_24px_64px_rgba(0,0,0,0.85)] space-y-6 max-h-[85vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Modal Header */}
              <div className="flex items-start justify-between pb-4 border-b border-black/10 dark:border-[#29292E]">
                <div className="space-y-1">
                  <div className="inline-flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full bg-[#B7FF00]" />
                    <span className="text-[11px] font-bold uppercase tracking-wider text-[#777777] dark:text-[#A1A1AA]">
                      Audit Record
                    </span>
                    <span
                      className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                        selectedExp.status === 'completed'
                          ? 'bg-[#080808] dark:bg-[#B7FF00] text-[#B7FF00] dark:text-black'
                          : 'bg-black/5 dark:bg-[#202024] text-[#777777] dark:text-[#A1A1AA]'
                      }`}
                    >
                      {selectedExp.status}
                    </span>
                  </div>
                  <h3 className="text-xl sm:text-2xl font-heading font-bold text-[#080808] dark:text-[#F5F5F7]">
                    Experiment Inspection
                  </h3>
                  <p className="text-xs font-mono text-[#777777] dark:text-[#71717A]">
                    ID: {selectedExp.id} · Created: {formatTimestamp(selectedExp.timestamp)}
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => {
                      const blob = new Blob([JSON.stringify(selectedExp, null, 2)], { type: 'application/json' });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement('a');
                      a.href = url;
                      a.download = `ROUTEIQ_Experiment_${selectedExp.id}.json`;
                      a.click();
                    }}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-black/10 dark:border-[#29292E] bg-white dark:bg-[#18181B] hover:bg-black/5 dark:hover:bg-[#202024] text-xs font-semibold text-[#080808] dark:text-[#F5F5F7] transition-all cursor-pointer"
                    title="Export raw JSON record"
                  >
                    <Download className="h-3.5 w-3.5" />
                    <span>Export JSON</span>
                  </button>
                  <button
                    onClick={() => setSelectedExp(null)}
                    className="h-8 w-8 rounded-full flex items-center justify-center bg-black/5 dark:bg-[#18181B] hover:bg-black/10 dark:hover:bg-[#202024] border border-transparent dark:border-[#29292E] text-[#080808] dark:text-[#F5F5F7] transition-colors cursor-pointer text-sm font-bold"
                    title="Close inspection"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              </div>

              {/* Parameters Overview Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                <div className="p-3.5 bg-black/5 dark:bg-[#18181B] rounded-2xl border border-black/5 dark:border-[#29292E] space-y-1">
                  <span className="text-[#777777] dark:text-[#71717A] block text-[10px] font-bold uppercase tracking-wider">
                    Algorithm
                  </span>
                  <span className="font-bold text-sm text-[#080808] dark:text-[#F5F5F7] capitalize block truncate">
                    {selectedExp.algorithm}
                  </span>
                </div>

                <div className="p-3.5 bg-black/5 dark:bg-[#18181B] rounded-2xl border border-black/5 dark:border-[#29292E] space-y-1">
                  <span className="text-[#777777] dark:text-[#71717A] block text-[10px] font-bold uppercase tracking-wider">
                    Fleet & Capacity
                  </span>
                  <span className="font-bold text-sm text-[#080808] dark:text-[#F5F5F7] block font-technical">
                    {selectedExp.num_vehicles} Veh · {selectedExp.vehicle_capacity || 50} cap
                  </span>
                </div>

                <div className="p-3.5 bg-black/5 dark:bg-[#18181B] rounded-2xl border border-black/5 dark:border-[#29292E] space-y-1">
                  <span className="text-[#777777] dark:text-[#71717A] block text-[10px] font-bold uppercase tracking-wider">
                    Customer Stops
                  </span>
                  <span className="font-bold text-sm text-[#080808] dark:text-[#F5F5F7] block font-technical">
                    {selectedExp.num_customers} Stops Assigned
                  </span>
                </div>

                <div className="p-3.5 bg-black/5 dark:bg-[#18181B] rounded-2xl border border-black/5 dark:border-[#29292E] space-y-1">
                  <span className="text-[#777777] dark:text-[#71717A] block text-[10px] font-bold uppercase tracking-wider">
                    Environment
                  </span>
                  <span className="font-bold text-sm text-[#080808] dark:text-[#F5F5F7] block capitalize truncate">
                    {selectedExp.traffic_scenario} / {selectedExp.weather_scenario || 'Clear'}
                  </span>
                </div>
              </div>

              {/* Results Output */}
              {selectedExp.results && Object.keys(selectedExp.results).length > 0 ? (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-[#080808] dark:text-[#F5F5F7]">
                      Solver Benchmarks & Route Solutions ({Object.keys(selectedExp.results).length})
                    </h4>
                  </div>

                  <div className="space-y-3">
                    {Object.entries(selectedExp.results).map(([algo, res]: [string, any]) => (
                      <div
                        key={algo}
                        className="p-5 border border-black/10 dark:border-[#29292E] rounded-2xl bg-black/[0.02] dark:bg-[#18181B] space-y-4 text-xs"
                      >
                        {/* Solver Header */}
                        <div className="flex items-center justify-between pb-2 border-b border-black/5 dark:border-[#29292E]">
                          <div className="flex items-center gap-2">
                            <span className="font-bold text-sm text-[#080808] dark:text-[#F5F5F7] capitalize">
                              {res.algorithm || algo}
                            </span>
                            {res.qubit_count && (
                              <span className="text-[10px] px-2 py-0.5 rounded-full bg-purple-500/10 text-purple-600 dark:text-purple-400 font-technical font-bold">
                                {res.qubit_count} Qubits
                              </span>
                            )}
                          </div>

                          <span
                            className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold flex items-center gap-1 ${
                              res.is_feasible
                                ? 'bg-[#22C55E]/15 text-[#22C55E]'
                                : 'bg-amber-500/15 text-amber-500'
                            }`}
                          >
                            <CheckCircle2 className="h-3 w-3 inline" />
                            <span>{res.is_feasible ? 'Feasible' : 'Penalized'}</span>
                          </span>
                        </div>

                        {/* Metrics 4-Col Grid */}
                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                          <div>
                            <span className="text-[10px] text-[#777777] dark:text-[#71717A] uppercase font-bold block">
                              Total Distance
                            </span>
                            <span className="font-technical text-base font-bold text-[#080808] dark:text-[#F5F5F7]">
                              {res.total_distance_km ? `${res.total_distance_km.toFixed(1)} km` : 'N/A'}
                            </span>
                          </div>

                          <div>
                            <span className="text-[10px] text-[#777777] dark:text-[#71717A] uppercase font-bold block">
                              Est. Travel Time
                            </span>
                            <span className="font-technical text-base font-bold text-[#080808] dark:text-[#F5F5F7]">
                              {res.total_travel_time_min ? `${Math.round(res.total_travel_time_min)} min` : 'N/A'}
                            </span>
                          </div>

                          <div>
                            <span className="text-[10px] text-[#777777] dark:text-[#71717A] uppercase font-bold block">
                              Solver Runtime
                            </span>
                            <span className="font-technical text-base font-bold text-[#080808] dark:text-[#F5F5F7]">
                              {res.execution_time_sec ? `${res.execution_time_sec.toFixed(3)}s` : 'N/A'}
                            </span>
                          </div>

                          <div>
                            <span className="text-[10px] text-[#777777] dark:text-[#71717A] uppercase font-bold block">
                              Violations
                            </span>
                            <span className="font-technical text-base font-bold text-[#080808] dark:text-[#F5F5F7]">
                              {res.capacity_violations || 0}
                            </span>
                          </div>
                        </div>

                        {/* Routes Summary if available */}
                        {res.routes && Array.isArray(res.routes) && res.routes.length > 0 && (
                          <div className="pt-2 border-t border-black/5 dark:border-[#29292E] space-y-2">
                            <span className="text-[10px] font-bold uppercase tracking-wider text-[#777777] dark:text-[#A1A1AA] block">
                              Assigned Fleet Routes ({res.routes.length} Vehicles)
                            </span>
                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                              {res.routes.map((r: any, rIdx: number) => (
                                <div
                                  key={r.vehicle_id || rIdx}
                                  className="p-2.5 rounded-xl bg-white dark:bg-[#202024] border border-black/5 dark:border-[#29292E] flex items-center justify-between text-xs"
                                >
                                  <div className="flex items-center gap-2">
                                    <span className="px-1.5 py-0.5 rounded-md bg-[#080808] text-[#B7FF00] font-technical font-bold text-[10px]">
                                      V{r.vehicle_id || rIdx + 1}
                                    </span>
                                    <span className="text-[#555555] dark:text-[#A1A1AA] text-[11px]">
                                      {r.waypoints?.length ? `${r.waypoints.length} stops` : 'Active'}
                                    </span>
                                  </div>
                                  <span className="font-technical font-semibold text-[#080808] dark:text-[#F5F5F7] text-[11px]">
                                    {r.distance_km?.toFixed(1)} km
                                  </span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="p-6 text-center text-[#777777] dark:text-[#A1A1AA] bg-black/5 dark:bg-[#18181B] rounded-2xl border border-black/5 dark:border-[#29292E]">
                  <p className="text-xs font-semibold">No detailed solver route data recorded for this entry.</p>
                </div>
              )}

              {/* Footer */}
              <div className="pt-2 flex justify-end gap-3 border-t border-black/10 dark:border-[#29292E]">
                <button
                  onClick={() => setSelectedExp(null)}
                  className="px-5 py-2.5 bg-[#080808] hover:bg-[#171717] dark:bg-[#B7FF00] dark:hover:bg-[#a5e600] text-[#B7FF00] dark:text-black rounded-xl text-xs font-bold transition-all cursor-pointer shadow-xs"
                >
                  Close Inspection
                </button>
              </div>
            </div>
          </div>,
          document.body
        )}
    </div>
  );
};
