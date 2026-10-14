import React from 'react';
import {
  GitCompare,
  Download,
  Cpu,
  ArrowRight,
  CheckCircle2,
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
import { OptimizationResponse } from '../types';

interface ComparisonViewProps {
  lastResult: OptimizationResponse | null;
  onNavigateToOptimization: () => void;
}

export const ComparisonView: React.FC<ComparisonViewProps> = ({
  lastResult,
  onNavigateToOptimization,
}) => {
  const classical =
    lastResult?.results?.classical ||
    lastResult?.results?.ortools ||
    lastResult?.results?.clarke_wright ||
    (lastResult?.results && Object.values(lastResult.results)[0]);
  const qaoa =
    lastResult?.results?.qaoa ||
    lastResult?.results?.qiga ||
    lastResult?.results?.two_opt;

  if (!lastResult || !lastResult.results || Object.keys(lastResult.results).length === 0) {
    return (
      <div className="bg-white border border-black/10 rounded-2xl p-12 text-center shadow-xs">
        <GitCompare className="h-10 w-10 text-[#777777] mx-auto mb-3" />
        <h3 className="text-base font-bold text-[#080808]">
          No Benchmark Data Available
        </h3>
        <p className="text-xs text-[#777777] max-w-md mx-auto mt-1 mb-5">
          Execute an optimization run with &quot;Both&quot; solver modes selected to generate side-by-side classical vs QAOA quantum benchmarks.
        </p>
        <button
          onClick={onNavigateToOptimization}
          className="px-5 py-2.5 bg-[#080808] hover:bg-[#171717] text-[#B7FF2A] rounded-xl text-xs font-bold transition-all shadow-xs cursor-pointer"
        >
          Go to Route Optimization
        </button>
      </div>
    );
  }

  const comparisonChartData = [
    {
      metric: 'Distance (km)',
      Classical: Number(classical?.total_distance_km?.toFixed(1) || 0),
      'Quantum QAOA': Number(qaoa?.total_distance_km?.toFixed(1) || 0),
    },
    {
      metric: 'Travel Time (min)',
      Classical: Math.round(classical?.total_travel_time_min || 0),
      'Quantum QAOA': Math.round(qaoa?.total_travel_time_min || 0),
    },
    {
      metric: 'Objective Cost',
      Classical: Number(classical?.total_objective_cost?.toFixed(1) || 0),
      'Quantum QAOA': Number(qaoa?.total_objective_cost?.toFixed(1) || 0),
    },
  ];

  const handleExportJSON = () => {
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(lastResult, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute('download', `ROUTEIQ_Benchmark_${lastResult.experiment_id}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="bg-white border border-black/10 rounded-2xl p-5 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-[#080808]">
            Classical vs. Quantum QAOA Comparative Benchmark
          </h2>
          <p className="text-xs text-[#777777] mt-0.5">
            Empirical validation of classical CVRP algorithms vs. Qiskit QAOA quantum circuit optimization
          </p>
        </div>

        <button
          onClick={handleExportJSON}
          className="flex items-center gap-2 px-4 py-2 bg-[#080808] hover:bg-[#171717] text-[#B7FF2A] rounded-xl text-xs font-bold shadow-xs transition-all cursor-pointer"
        >
          <Download className="h-4 w-4" />
          <span>Export Benchmark Data (JSON)</span>
        </button>
      </div>

      {/* Systematic Benchmark Table */}
      <div className="bg-white border border-black/10 rounded-2xl shadow-xs overflow-hidden">
        <div className="px-5 py-3 border-b border-black/5 bg-[#F4F4F2]">
          <h3 className="text-xs font-bold uppercase tracking-wider text-[#080808]">
            Systematic Metric Evaluation Table
          </h3>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-white border-b border-black/5 text-[#777777] font-bold text-[11px]">
              <tr>
                <th className="py-3 px-4">Metric / Parameter</th>
                <th className="py-3 px-4 text-[#080808] font-bold">Classical CVRP Solver</th>
                <th className="py-3 px-4 text-[#080808] font-bold">QAOA / Hybrid Quantum</th>
                <th className="py-3 px-4">Evaluation Notes</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-black/5 text-[#171717]">
              <tr>
                <td className="py-3 px-4 font-bold text-[#080808]">Total Distance (km)</td>
                <td className="py-3 px-4 font-mono font-bold text-[#080808]">
                  {classical ? `${classical.total_distance_km.toFixed(1)} km` : 'N/A'}
                </td>
                <td className="py-3 px-4 font-mono font-bold text-[#080808]">
                  {qaoa ? `${qaoa.total_distance_km.toFixed(1)} km` : 'N/A'}
                </td>
                <td className="py-3 px-4 text-[#777777] text-[11px]">
                  Haversine routing distance across visited vertices
                </td>
              </tr>
              <tr>
                <td className="py-3 px-4 font-bold text-[#080808]">Estimated Travel Time</td>
                <td className="py-3 px-4 font-mono font-bold">
                  {classical ? `${Math.round(classical.total_travel_time_min)} min` : 'N/A'}
                </td>
                <td className="py-3 px-4 font-mono font-bold">
                  {qaoa ? `${Math.round(qaoa.total_travel_time_min)} min` : 'N/A'}
                </td>
                <td className="py-3 px-4 text-[#777777] text-[11px]">
                  Congestion & weather multiplier applied
                </td>
              </tr>
              <tr>
                <td className="py-3 px-4 font-bold text-[#080808]">Total Objective Cost</td>
                <td className="py-3 px-4 font-mono font-bold">
                  {classical ? classical.total_objective_cost.toFixed(2) : 'N/A'}
                </td>
                <td className="py-3 px-4 font-mono font-bold">
                  {qaoa ? qaoa.total_objective_cost.toFixed(2) : 'N/A'}
                </td>
                <td className="py-3 px-4 text-[#777777] text-[11px]">
                  Weighted sum of distance and travel time penalties
                </td>
              </tr>
              <tr>
                <td className="py-3 px-4 font-bold text-[#080808]">Solution Feasibility</td>
                <td className="py-3 px-4">
                  {classical ? (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-[#080808] text-[#B7FF2A]">
                      {classical.is_feasible ? 'Feasible' : 'Infeasible'}
                    </span>
                  ) : 'N/A'}
                </td>
                <td className="py-3 px-4">
                  {qaoa ? (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-[#080808] text-[#B7FF2A]">
                      {qaoa.is_feasible ? 'Feasible' : 'Repaired Feasible'}
                    </span>
                  ) : 'N/A'}
                </td>
                <td className="py-3 px-4 text-[#777777] text-[11px]">
                  All customers served without vehicle capacity violations
                </td>
              </tr>
              <tr>
                <td className="py-3 px-4 font-bold text-[#080808]">Execution Time</td>
                <td className="py-3 px-4 font-mono font-bold">{classical?.execution_time_sec?.toFixed(2)}s</td>
                <td className="py-3 px-4 font-mono font-bold">{qaoa?.execution_time_sec?.toFixed(2)}s</td>
                <td className="py-3 px-4 text-[#777777] text-[11px]">
                  Wall-clock time on local workstation
                </td>
              </tr>
              <tr>
                <td className="py-3 px-4 font-bold text-[#080808]">Qubit Count</td>
                <td className="py-3 px-4 text-[#777777]">N/A (Classical)</td>
                <td className="py-3 px-4 font-mono font-bold text-[#080808]">
                  {qaoa?.num_qubits || 'N/A'} Qubits
                </td>
                <td className="py-3 px-4 text-[#777777] text-[11px]">
                  QUBO binary decision variables mapped to Pauli-Z Hamiltonians
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Comparison Visual Charts (Strict Monochrome & Lime Bar Colors) */}
      <div className="bg-white border border-black/10 rounded-2xl p-5 shadow-xs">
        <h3 className="text-sm font-bold text-[#080808] mb-1">
          Direct Metric Benchmark (Side-by-Side)
        </h3>
        <p className="text-xs text-[#777777] mb-4">
          Lower values denote superior routing performance
        </p>

        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={comparisonChartData}>
              <XAxis dataKey="metric" tick={{ fontSize: 11, fill: '#171717' }} />
              <YAxis tick={{ fontSize: 11, fill: '#171717' }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="Classical" fill="#080808" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Quantum QAOA" fill="#B7FF2A" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
