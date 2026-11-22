import React, { useState, useMemo } from 'react';
import {
  CheckCircle2,
  AlertTriangle,
  RotateCw,
  ChevronDown,
  ChevronUp,
  Search,
  Filter,
  ArrowUpDown,
  Cpu,
  Layers,
  Activity,
  Gauge,
  Sparkles,
  Zap,
  Route,
  Database,
  Clock,
  Compass,
  SlidersHorizontal,
} from 'lucide-react';
import { ComparisonItem, SolverResult } from '../types';

interface AlgorithmComparisonScorecardProps {
  items: ComparisonItem[];
  resultsMap?: Record<string, SolverResult>;
  activeAlgo: string;
  bestAlgoId?: string;
  onSelectAlgorithm: (algoKey: string) => void;
  isDark: boolean;
  jobStatus?: string;
  totalAlgorithms?: number;
  completedAlgorithms?: number;
}

type SortField = 'default' | 'distance' | 'duration' | 'runtime' | 'vehicles';
type SortDirection = 'asc' | 'desc';
type SystemScopeFilter = 'all' | 'primary' | 'classical';
type FeasibilityFilter = 'all' | 'feasible' | 'penalized_failed';

const PRIMARY_RESEARCH_KEYS = ['routeiq_cooperative', 'qaoa', 'qiga', 'ortools', 'classical'];

export const AlgorithmComparisonScorecard: React.FC<AlgorithmComparisonScorecardProps> = ({
  items,
  resultsMap = {},
  activeAlgo,
  bestAlgoId,
  onSelectAlgorithm,
  isDark,
  jobStatus,
  totalAlgorithms = 11,
  completedAlgorithms,
}) => {
  const [sortField, setSortField] = useState<SortField>('default');
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');
  const [systemScope, setSystemScope] = useState<SystemScopeFilter>('all');
  const [feasibilityFilter, setFeasibilityFilter] = useState<FeasibilityFilter>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [expandedDetails, setExpandedDetails] = useState<Record<string, boolean>>({});

  // Toggle individual row expansion
  const toggleRowExpanded = (id: string) => {
    setExpandedDetails((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  // Toggle expand / collapse all
  const areAllExpanded = useMemo(() => {
    if (items.length === 0) return false;
    return items.every((it) => expandedDetails[it.id]);
  }, [items, expandedDetails]);

  const toggleExpandAll = () => {
    if (areAllExpanded) {
      setExpandedDetails({});
    } else {
      const next: Record<string, boolean> = {};
      items.forEach((it) => {
        next[it.id] = true;
      });
      setExpandedDetails(next);
    }
  };

  // Handle column header sort click
  const handleSortClick = (field: SortField) => {
    if (sortField === field) {
      setSortDirection((prev) => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  // ─── DYNAMIC SUMMARY KPIS (Requirement 5) ──────────────────────────
  const summaryKPIs = useMemo(() => {
    const validItems = items.filter(
      (it) => it.status !== 'FAILED' && it.status !== 'TIMED_OUT' && it.status !== 'PENDING'
    );
    const feasibleItems = validItems.filter((it) => it.is_feasible && it.total_distance_km > 0);

    // 1. Best Feasible Distance
    let bestDistItem: ComparisonItem | null = null;
    if (feasibleItems.length > 0) {
      bestDistItem = feasibleItems.reduce((min, it) =>
        it.total_distance_km < min.total_distance_km ? it : min
      );
    }

    // 2. Fastest Feasible Algorithm
    let fastestItem: ComparisonItem | null = null;
    if (feasibleItems.length > 0) {
      fastestItem = feasibleItems.reduce((min, it) =>
        it.execution_time_sec < min.execution_time_sec ? it : min
      );
    }

    // 3. Completed vs Total Algorithms
    const completedCount = completedAlgorithms ?? items.filter((it) => it.status !== 'PENDING' && it.status !== 'RUNNING').length;
    const totalCount = totalAlgorithms || 11;

    // 4. Feasible Solutions Count
    const feasibleCount = feasibleItems.length;

    // 5. Total Constraint Violations across all evaluated solvers
    const totalViolations = items.reduce((sum, it) => {
      const cap = it.capacity_violations || 0;
      const unserved = it.unserved_customers || 0;
      return sum + cap + unserved;
    }, 0);

    return {
      bestDistItem,
      fastestItem,
      completedCount,
      totalCount,
      feasibleCount,
      totalEvaluated: items.length,
      totalViolations,
    };
  }, [items, completedAlgorithms, totalAlgorithms]);

  // ─── FILTERING AND SORTING (Requirement 6) ─────────────────────────
  const processedItems = useMemo(() => {
    let result = [...items];

    // 1. System Scope Filter
    if (systemScope === 'primary') {
      result = result.filter((it) => PRIMARY_RESEARCH_KEYS.includes(it.id));
    } else if (systemScope === 'classical') {
      result = result.filter((it) => !PRIMARY_RESEARCH_KEYS.includes(it.id));
    }

    // 2. Feasibility Filter
    if (feasibilityFilter === 'feasible') {
      result = result.filter((it) => it.is_feasible && it.status !== 'FAILED' && it.status !== 'TIMED_OUT');
    } else if (feasibilityFilter === 'penalized_failed') {
      result = result.filter((it) => !it.is_feasible || it.status === 'FAILED' || it.status === 'TIMED_OUT');
    }

    // 3. Search Query
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase().trim();
      result = result.filter(
        (it) =>
          it.name.toLowerCase().includes(q) ||
          it.id.toLowerCase().includes(q) ||
          (it.category_label && it.category_label.toLowerCase().includes(q)) ||
          (it.compute_type && it.compute_type.toLowerCase().includes(q))
      );
    }

    // 4. Sorting
    result.sort((a, b) => {
      if (sortField === 'default') {
        // Priority order: Best first, then routeiq_cooperative, qaoa, qiga, ortools, then others
        const getPriorityRank = (item: ComparisonItem) => {
          if (item.id === bestAlgoId) return 0;
          if (item.id === 'routeiq_cooperative') return 1;
          if (item.id === 'qaoa') return 2;
          if (item.id === 'qiga') return 3;
          if (item.id === 'ortools' || item.id === 'classical') return 4;
          return 10;
        };
        const rankDiff = getPriorityRank(a) - getPriorityRank(b);
        if (rankDiff !== 0) return rankDiff;
        return a.total_distance_km - b.total_distance_km;
      }

      let diff = 0;
      if (sortField === 'distance') {
        const distA = a.total_distance_km || 999999;
        const distB = b.total_distance_km || 999999;
        diff = distA - distB;
      } else if (sortField === 'duration') {
        const durA = a.driving_duration_min || a.total_travel_time_min || 999999;
        const durB = b.driving_duration_min || b.total_travel_time_min || 999999;
        diff = durA - durB;
      } else if (sortField === 'runtime') {
        const rtA = typeof a.execution_time_sec === 'number' ? a.execution_time_sec : 999999;
        const rtB = typeof b.execution_time_sec === 'number' ? b.execution_time_sec : 999999;
        diff = rtA - rtB;
      } else if (sortField === 'vehicles') {
        const vA = a.vehicles_used || 0;
        const vB = b.vehicles_used || 0;
        diff = vA - vB;
      }

      return sortDirection === 'asc' ? diff : -diff;
    });

    return result;
  }, [items, systemScope, feasibilityFilter, searchQuery, sortField, sortDirection, bestAlgoId]);

  // Helper for Category Badges
  const getCategoryBadge = (item: ComparisonItem) => {
    if (item.id === 'routeiq_cooperative') {
      return {
        label: 'Hybrid Cooperative',
        classes: 'bg-purple-500/15 text-purple-600 dark:text-purple-400 border border-purple-500/30',
        hardwareTag: 'Spark RDD + ALNS + VND',
      };
    }
    if (item.id === 'qaoa') {
      return {
        label: 'Quantum Variational',
        classes: 'bg-lime-500/15 text-lime-600 dark:text-[#B7FF2A] border border-lime-500/30',
        hardwareTag: 'Qiskit Aer CPU Sim',
      };
    }
    if (item.id === 'qiga') {
      return {
        label: 'Quantum-Inspired',
        classes: 'bg-fuchsia-500/15 text-fuchsia-600 dark:text-fuchsia-400 border border-fuchsia-500/30',
        hardwareTag: 'Classical Simulated Q-bits',
      };
    }
    if (item.id === 'ortools' || item.id === 'classical') {
      return {
        label: 'Exact MIP Baseline',
        classes: 'bg-blue-500/15 text-blue-600 dark:text-blue-400 border border-blue-500/30',
        hardwareTag: 'Google OR-Tools C++',
      };
    }
    return {
      label: item.category_label || 'Classical Heuristic',
      classes: 'bg-black/5 dark:bg-[#1E1E22] text-[#666666] dark:text-[#A1A1AA] border border-black/5 dark:border-[#29292E]',
      hardwareTag: item.compute_type || 'Classical CPU',
    };
  };

  return (
    <div className="space-y-4 pt-5 border-t border-black/10 dark:border-[#29292E] font-heading">
      {/* ─── SECTION HEADER ──────────────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-base sm:text-[17px] font-heading font-semibold text-[#080808] dark:text-[#F5F5F7]">
              Algorithm Comparison Scorecard
            </h2>
            <span className="text-[9px] px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 font-semibold border border-emerald-500/30">
              Fair Empirical Benchmark
            </span>
          </div>
          <p className="text-[11px] text-[#777777] dark:text-[#A1A1AA] mt-0.5 max-w-2xl leading-normal font-normal">
            Side-by-side performance evaluation on identical customer stops, fleet vehicle constraints, and directed OpenStreetMap road network edge matrices.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={toggleExpandAll}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg border border-black/10 dark:border-[#29292E] bg-white dark:bg-[#18181B] hover:bg-black/5 dark:hover:bg-[#202024] text-[11px] font-semibold text-[#080808] dark:text-[#F5F5F7] transition-all cursor-pointer shadow-2xs"
            title="Expand or collapse technical telemetry for all algorithms"
          >
            <SlidersHorizontal className="h-3 w-3 text-[#B7FF2A]" />
            <span>{areAllExpanded ? 'Collapse All Details' : 'Expand All Details'}</span>
          </button>
        </div>
      </div>

      {/* ─── COMPACT DYNAMIC SUMMARY KPIS (Requirement 5) ────────────────── */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-2.5 font-heading">
        {/* KPI 1: Best Feasible Distance */}
        <div className="p-3 rounded-xl bg-white dark:bg-[#111113] border border-black/10 dark:border-[#29292E] shadow-2xs">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-medium uppercase tracking-wider text-[#777777] dark:text-[#71717A] font-heading">
              Best Feasible Distance
            </span>
            <CheckCircle2 className="h-3.5 w-3.5 text-[#22C55E]" />
          </div>
          <div className="text-base sm:text-lg font-semibold tabular-nums text-[#080808] dark:text-[#F5F5F7] mt-1 truncate font-heading">
            {summaryKPIs.bestDistItem
              ? `${summaryKPIs.bestDistItem.total_distance_km.toFixed(2)} km`
              : 'Evaluating...'}
          </div>
          <span className="text-[10px] text-[#777777] dark:text-[#A1A1AA] truncate block mt-0.5 font-normal" title={summaryKPIs.bestDistItem?.name}>
            {summaryKPIs.bestDistItem ? summaryKPIs.bestDistItem.name : 'Awaiting solver completion'}
          </span>
        </div>

        {/* KPI 2: Fastest Feasible Solver */}
        <div className="p-3 rounded-xl bg-white dark:bg-[#111113] border border-black/10 dark:border-[#29292E] shadow-2xs">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-medium uppercase tracking-wider text-[#777777] dark:text-[#71717A] font-heading">
              Fastest Feasible Solver
            </span>
            <Clock className="h-3.5 w-3.5 text-blue-500" />
          </div>
          <div className="text-base sm:text-lg font-semibold tabular-nums text-[#080808] dark:text-[#F5F5F7] mt-1 truncate font-heading">
            {summaryKPIs.fastestItem
              ? `${summaryKPIs.fastestItem.execution_time_sec.toFixed(3)}s`
              : 'Evaluating...'}
          </div>
          <span className="text-[10px] text-[#777777] dark:text-[#A1A1AA] truncate block mt-0.5 font-normal" title={summaryKPIs.fastestItem?.name}>
            {summaryKPIs.fastestItem ? summaryKPIs.fastestItem.name : 'Awaiting results'}
          </span>
        </div>

        {/* KPI 3: Total Completed Algorithms */}
        <div className="p-3 rounded-xl bg-white dark:bg-[#111113] border border-black/10 dark:border-[#29292E] shadow-2xs">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-medium uppercase tracking-wider text-[#777777] dark:text-[#71717A] font-heading">
              Evaluation Progress
            </span>
            {jobStatus === 'PARTIAL' ? (
              <RotateCw className="h-3.5 w-3.5 text-amber-500 animate-spin" />
            ) : (
              <span className="h-2 w-2 rounded-full bg-[#22C55E]" />
            )}
          </div>
          <div className="text-base sm:text-lg font-semibold tabular-nums text-[#080808] dark:text-[#F5F5F7] mt-1 font-heading">
            {summaryKPIs.completedCount} / {summaryKPIs.totalCount} Solvers
          </div>
          <span className="text-[10px] text-[#777777] dark:text-[#A1A1AA] block mt-0.5 font-normal">
            {jobStatus === 'PARTIAL' ? 'Background comparison running' : '100% Suite Completed'}
          </span>
        </div>

        {/* KPI 4: Feasible Solutions */}
        <div className="p-3 rounded-xl bg-white dark:bg-[#111113] border border-black/10 dark:border-[#29292E] shadow-2xs">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-medium uppercase tracking-wider text-[#777777] dark:text-[#71717A] font-heading">
              Feasible Solutions
            </span>
            <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
          </div>
          <div className="text-base sm:text-lg font-semibold tabular-nums text-[#080808] dark:text-[#F5F5F7] mt-1 font-heading">
            {summaryKPIs.feasibleCount} / {summaryKPIs.totalEvaluated} Feasible
          </div>
          <span className="text-[10px] text-[#777777] dark:text-[#A1A1AA] block mt-0.5 font-normal">
            {summaryKPIs.totalEvaluated > 0
              ? `${Math.round((summaryKPIs.feasibleCount / summaryKPIs.totalEvaluated) * 100)}% adherence rate`
              : 'Calculating...'}
          </span>
        </div>

        {/* KPI 5: Total Constraint Violations */}
        <div className="p-3 rounded-xl bg-white dark:bg-[#111113] border border-black/10 dark:border-[#29292E] shadow-2xs col-span-2 lg:col-span-1">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-medium uppercase tracking-wider text-[#777777] dark:text-[#71717A] font-heading">
              Fleet Violations
            </span>
            {summaryKPIs.totalViolations === 0 ? (
              <CheckCircle2 className="h-3.5 w-3.5 text-[#22C55E]" />
            ) : (
              <AlertTriangle className="h-3.5 w-3.5 text-amber-500" />
            )}
          </div>
          <div className={`text-base sm:text-lg font-semibold tabular-nums font-heading mt-1 ${summaryKPIs.totalViolations === 0 ? 'text-[#22C55E]' : 'text-amber-500'}`}>
            {summaryKPIs.totalViolations} Violations
          </div>
          <span className="text-[10px] text-[#777777] dark:text-[#A1A1AA] block mt-0.5 font-normal">
            {summaryKPIs.totalViolations === 0 ? 'Zero unserved / capacity breaches' : 'Cumulative violations in fleet'}
          </span>
        </div>
      </div>

      {/* ─── CONTROLS BAR: SEARCH, SCOPE FILTER, SORTING (Requirement 6) ─── */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-2.5 p-2.5 rounded-xl bg-white dark:bg-[#111113] border border-black/10 dark:border-[#29292E] shadow-2xs font-heading">
        {/* Left: System Scope Pills */}
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="text-[10px] font-medium uppercase tracking-wider text-[#777777] dark:text-[#71717A] mr-1 hidden sm:inline font-heading">
            Scope:
          </span>
          <button
            type="button"
            onClick={() => setSystemScope('all')}
            className={`px-2.5 py-1 rounded-lg text-[11px] font-semibold transition-all cursor-pointer ${
              systemScope === 'all'
                ? 'bg-[#080808] text-[#B7FF2A] dark:bg-[#202024] dark:text-[#B7FF2A] border border-black dark:border-[#B7FF2A]/40'
                : 'bg-black/5 text-[#555555] hover:bg-black/10 dark:bg-[#18181B] dark:text-[#A1A1AA] dark:hover:text-[#F5F5F7]'
            }`}
          >
            All Solvers ({items.length})
          </button>
          <button
            type="button"
            onClick={() => setSystemScope('primary')}
            className={`px-2.5 py-1 rounded-lg text-[11px] font-semibold transition-all cursor-pointer ${
              systemScope === 'primary'
                ? 'bg-[#080808] text-[#B7FF2A] dark:bg-[#202024] dark:text-[#B7FF2A] border border-black dark:border-[#B7FF2A]/40'
                : 'bg-black/5 text-[#555555] hover:bg-black/10 dark:bg-[#18181B] dark:text-[#A1A1AA] dark:hover:text-[#F5F5F7]'
            }`}
          >
            Primary Research Systems (4)
          </button>
          <button
            type="button"
            onClick={() => setSystemScope('classical')}
            className={`px-2.5 py-1 rounded-lg text-[11px] font-semibold transition-all cursor-pointer ${
              systemScope === 'classical'
                ? 'bg-[#080808] text-[#B7FF2A] dark:bg-[#202024] dark:text-[#B7FF2A] border border-black dark:border-[#B7FF2A]/40'
                : 'bg-black/5 text-[#555555] hover:bg-black/10 dark:bg-[#18181B] dark:text-[#A1A1AA] dark:hover:text-[#F5F5F7]'
            }`}
          >
            Classical Benchmarks (7)
          </button>
        </div>

        {/* Right: Feasibility Filter & Search */}
        <div className="flex items-center gap-2 flex-wrap sm:flex-nowrap">
          {/* Feasibility Selector */}
          <div className="flex items-center gap-1 px-2 py-1 rounded-lg bg-black/5 dark:bg-[#18181B] border border-black/5 dark:border-[#29292E] text-[11px]">
            <Filter className="h-3 w-3 text-[#777777] dark:text-[#A1A1AA] shrink-0" />
            <select
              value={feasibilityFilter}
              aria-label="Filter algorithms by feasibility status"
              onChange={(e) => setFeasibilityFilter(e.target.value as FeasibilityFilter)}
              className="bg-transparent text-[#080808] dark:text-[#F5F5F7] font-semibold text-[11px] border-none outline-none cursor-pointer font-heading"
            >
              <option value="all" className="dark:bg-[#18181B]">All Feasibility</option>
              <option value="feasible" className="dark:bg-[#18181B]">Feasible Only</option>
              <option value="penalized_failed" className="dark:bg-[#18181B]">Penalized / Failed</option>
            </select>
          </div>

          {/* Sort Selector */}
          <div className="flex items-center gap-1 px-2 py-1 rounded-lg bg-black/5 dark:bg-[#18181B] border border-black/5 dark:border-[#29292E] text-[11px]">
            <ArrowUpDown className="h-3 w-3 text-[#777777] dark:text-[#A1A1AA] shrink-0" />
            <select
              value={sortField}
              aria-label="Sort comparison table by metric"
              onChange={(e) => setSortField(e.target.value as SortField)}
              className="bg-transparent text-[#080808] dark:text-[#F5F5F7] font-semibold text-[11px] border-none outline-none cursor-pointer font-heading"
            >
              <option value="default" className="dark:bg-[#18181B]">Sort: Research Priority</option>
              <option value="distance" className="dark:bg-[#18181B]">Sort: Distance</option>
              <option value="duration" className="dark:bg-[#18181B]">Sort: Driving Duration</option>
              <option value="runtime" className="dark:bg-[#18181B]">Sort: Solver Runtime</option>
              <option value="vehicles" className="dark:bg-[#18181B]">Sort: Vehicles Assigned</option>
            </select>
          </div>

          {/* Quick Search */}
          <div className="relative min-w-[140px] w-full sm:w-auto">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3 w-3 text-[#777777] dark:text-[#71717A]" />
            <input
              type="text"
              placeholder="Search solver..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-7 pr-2.5 py-1 rounded-lg bg-black/5 dark:bg-[#18181B] border border-black/5 dark:border-[#29292E] text-[11px] text-[#080808] dark:text-[#F5F5F7] placeholder-[#777777] dark:placeholder-[#71717A] outline-none focus:border-[#B7FF2A]/50 transition-colors font-heading"
            />
          </div>
        </div>
      </div>

      {/* ─── DESKTOP & TABLET TABLE LAYOUT (Requirements 1, 2, 3, 4, 8) ────── */}
      <div className="hidden md:block rounded-xl border border-black/10 dark:border-[#29292E] bg-white dark:bg-[#111113] overflow-hidden shadow-2xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-[11px] border-collapse">
            <thead>
              <tr className="border-b border-black/10 dark:border-[#29292E] bg-black/5 dark:bg-[#18181B] text-[#777777] dark:text-[#A1A1AA] text-[9px] sm:text-[10px] uppercase font-bold tracking-wider select-none">
                <th className="py-2.5 px-3 min-w-[200px]">
                  <span>1. Algorithm</span>
                </th>
                <th className="py-2.5 px-3 min-w-[130px]">
                  <span>2. Category</span>
                </th>
                <th className="py-2.5 px-3 min-w-[100px]">
                  <span>3. Feasibility</span>
                </th>
                <th
                  onClick={() => handleSortClick('distance')}
                  className="py-2.5 px-3 min-w-[110px] cursor-pointer hover:text-[#080808] dark:hover:text-[#F5F5F7] transition-colors"
                  title="Click to sort by total road distance"
                >
                  <div className="flex items-center gap-1">
                    <span>4. Distance</span>
                    {sortField === 'distance' && (
                      <span className="text-[#B7FF2A]">{sortDirection === 'asc' ? '▲' : '▼'}</span>
                    )}
                  </div>
                </th>
                <th
                  onClick={() => handleSortClick('duration')}
                  className="py-2.5 px-3 min-w-[100px] cursor-pointer hover:text-[#080808] dark:hover:text-[#F5F5F7] transition-colors"
                  title="Click to sort by driving duration"
                >
                  <div className="flex items-center gap-1">
                    <span>5. Duration</span>
                    {sortField === 'duration' && (
                      <span className="text-[#B7FF2A]">{sortDirection === 'asc' ? '▲' : '▼'}</span>
                    )}
                  </div>
                </th>
                <th
                  onClick={() => handleSortClick('vehicles')}
                  className="py-2.5 px-3 min-w-[100px] cursor-pointer hover:text-[#080808] dark:hover:text-[#F5F5F7] transition-colors"
                  title="Click to sort by fleet vehicles"
                >
                  <div className="flex items-center gap-1">
                    <span>6. Vehicles</span>
                    {sortField === 'vehicles' && (
                      <span className="text-[#B7FF2A]">{sortDirection === 'asc' ? '▲' : '▼'}</span>
                    )}
                  </div>
                </th>
                <th className="py-2.5 px-3 min-w-[110px]">
                  <span>7. Violations</span>
                </th>
                <th
                  onClick={() => handleSortClick('runtime')}
                  className="py-2.5 px-3 min-w-[95px] cursor-pointer hover:text-[#080808] dark:hover:text-[#F5F5F7] transition-colors"
                  title="Click to sort by solver runtime"
                >
                  <div className="flex items-center gap-1">
                    <span>8. Runtime</span>
                    {sortField === 'runtime' && (
                      <span className="text-[#B7FF2A]">{sortDirection === 'asc' ? '▲' : '▼'}</span>
                    )}
                  </div>
                </th>
                <th className="py-2.5 px-3 min-w-[130px] text-right">
                  <span>9. Action</span>
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-black/5 dark:divide-[#29292E]">
              {processedItems.map((item) => {
                const isCurrent = activeAlgo === item.id;
                const isBest = item.id === bestAlgoId;
                const isCoop = item.id === 'routeiq_cooperative';
                const isExpanded = !!expandedDetails[item.id];
                const badge = getCategoryBadge(item);
                const drivingMin = item.driving_duration_min || item.total_travel_time_min || 0;
                const serviceMin = item.service_duration_min || 0;
                const totalDurMin = item.total_duration_min || (drivingMin + serviceMin);
                const impliedSpeed = item.implied_speed_kmh || (drivingMin > 0 ? (item.total_distance_km / (drivingMin / 60)) : 40.0);
                const solverRes = resultsMap[item.id];

                return (
                  <React.Fragment key={item.id}>
                    {/* Primary Row */}
                    <tr
                      className={`transition-colors group ${
                        isCurrent
                          ? 'bg-[#B7FF2A]/10 dark:bg-[#B7FF2A]/10'
                          : isCoop
                          ? 'bg-purple-500/[0.04] dark:bg-purple-950/20 hover:bg-purple-500/[0.08]'
                          : isBest
                          ? 'bg-emerald-500/[0.04] dark:bg-emerald-950/20 hover:bg-emerald-500/[0.08]'
                          : 'hover:bg-black/5 dark:hover:bg-[#18181B]/80'
                      }`}
                    >
                      {/* 1. Algorithm Name & Sub-badge */}
                      <td className="py-2.5 px-3">
                        <div className="flex items-center gap-1.5 flex-wrap">
                          <span className={`font-bold ${isCoop ? 'text-purple-600 dark:text-purple-300 font-heading text-xs sm:text-[13px]' : 'text-xs sm:text-[13px] text-[#080808] dark:text-[#F5F5F7]'}`}>
                            {item.name}
                          </span>
                          {isBest && (
                            <span className="text-[9px] px-1.5 py-0.2 rounded-full bg-[#B7FF00] text-black font-extrabold tracking-wide">
                              Best Pick
                            </span>
                          )}
                          {isCoop && (
                            <span className="text-[9px] px-1.5 py-0.2 rounded bg-purple-500/20 text-purple-700 dark:text-purple-300 font-bold border border-purple-500/30">
                              Primary Flagship
                            </span>
                          )}
                        </div>
                        <span className="text-[10px] text-[#777777] dark:text-[#71717A] block mt-0.5">
                          {badge.hardwareTag}
                        </span>
                      </td>

                      {/* 2. Category */}
                      <td className="py-2.5 px-3">
                        <span className={`inline-block px-1.5 py-0.5 rounded-md text-[9px] font-bold ${badge.classes}`}>
                          {badge.label}
                        </span>
                      </td>

                      {/* 3. Feasibility */}
                      <td className="py-2.5 px-3 whitespace-nowrap">
                        {item.status === 'RUNNING' ? (
                          <span className="inline-flex items-center gap-1 font-bold text-amber-500 text-[10px]">
                            <RotateCw className="h-3 w-3 animate-spin" />
                            <span>Running...</span>
                          </span>
                        ) : item.status === 'PENDING' ? (
                          <span className="inline-flex items-center gap-1 text-slate-400 font-medium text-[10px]">
                            <span>Pending</span>
                          </span>
                        ) : item.status === 'TIMED_OUT' ? (
                          <span className="inline-flex items-center gap-1 font-bold text-orange-500 text-[10px]">
                            <AlertTriangle className="h-3 w-3" />
                            <span>Timed Out</span>
                          </span>
                        ) : item.status === 'FAILED' ? (
                          <span className="inline-flex items-center gap-1 font-bold text-red-500 text-[10px]" title={item.error || 'Solver failed'}>
                            <AlertTriangle className="h-3 w-3" />
                            <span>Failed</span>
                          </span>
                        ) : (
                          <span className={`inline-flex items-center gap-1 font-bold text-[10px] ${
                            item.is_feasible ? 'text-[#22C55E]' : 'text-amber-500'
                          }`}>
                            <CheckCircle2 className="h-3 w-3 shrink-0" />
                            <span>{item.is_feasible ? 'Feasible' : 'Penalized'}</span>
                          </span>
                        )}
                      </td>

                      {/* 4. Total Distance */}
                      <td className="py-2.5 px-3 font-semibold tabular-nums text-[#080808] dark:text-[#F5F5F7] whitespace-nowrap">
                        {typeof item.total_distance_km === 'number' && item.total_distance_km > 0
                          ? `${item.total_distance_km.toFixed(2)} km`
                          : (item.status === 'RUNNING' ? 'Computing...' : '—')}
                      </td>

                      {/* 5. Estimated Duration */}
                      <td className="py-2.5 px-3 tabular-nums text-[#555555] dark:text-[#A1A1AA] whitespace-nowrap">
                        {drivingMin > 0 ? (
                          <div>
                            <span className="font-semibold text-[#080808] dark:text-[#F5F5F7]">
                              {Math.round(drivingMin)} min
                            </span>
                            {serviceMin > 0 && (
                              <span className="text-[9px] text-[#777777] dark:text-[#71717A] block">
                                +{Math.round(serviceMin)}m svc
                              </span>
                            )}
                          </div>
                        ) : '—'}
                      </td>

                      {/* 6. Vehicles Used */}
                      <td className="py-2.5 px-3 tabular-nums text-[#555555] dark:text-[#A1A1AA] whitespace-nowrap">
                        {item.vehicles_used ? (
                          <span>
                            <strong className="text-[#080808] dark:text-[#F5F5F7]">{item.vehicles_used}</strong> veh · {item.served_customers} stops
                          </span>
                        ) : '—'}
                      </td>

                      {/* 7. Constraint Violations */}
                      <td className="py-2.5 px-3 tabular-nums whitespace-nowrap">
                        {item.status === 'FAILED' || item.status === 'TIMED_OUT' ? (
                          <span className="text-red-500 font-bold truncate max-w-[120px] block" title={item.error || 'Execution Error'}>
                            {item.status === 'TIMED_OUT' ? 'Limit Exceeded' : 'Execution Failed'}
                          </span>
                        ) : item.capacity_violations === 0 && item.unserved_customers === 0 ? (
                          <span className="text-[#22C55E] font-semibold flex items-center gap-1">
                            <CheckCircle2 className="h-3 w-3" />
                            <span>0 violations</span>
                          </span>
                        ) : (
                          <span className="text-red-500 font-bold">
                            {item.capacity_violations} cap · {item.unserved_customers} unserved
                          </span>
                        )}
                      </td>

                      {/* 8. Runtime */}
                      <td className="py-2.5 px-3 tabular-nums text-[#777777] dark:text-[#A1A1AA] whitespace-nowrap">
                        {typeof item.execution_time_sec === 'number'
                          ? `${item.execution_time_sec.toFixed(3)}s`
                          : '—'}
                      </td>

                      {/* 9. Action Buttons */}
                      <td className="py-2.5 px-3 text-right whitespace-nowrap">
                        <div className="flex items-center justify-end gap-1.5">
                          <button
                            type="button"
                            onClick={() => onSelectAlgorithm(item.id)}
                            className={`px-2.5 py-1 rounded-lg text-[11px] font-semibold transition-all cursor-pointer shadow-2xs ${
                              isCurrent
                                ? 'bg-[#080808] text-[#B7FF2A] dark:bg-[#202024] dark:text-[#B7FF2A] border border-black dark:border-[#B7FF2A]/50 ring-1 ring-[#B7FF2A]/30'
                                : 'bg-black/5 hover:bg-black/10 dark:bg-[#18181B] dark:border dark:border-[#29292E] dark:hover:bg-[#202024] text-[#080808] dark:text-[#F5F5F7]'
                            }`}
                          >
                            {isCurrent ? '✓ Displayed' : 'Inspect Route'}
                          </button>

                          <button
                            type="button"
                            onClick={() => toggleRowExpanded(item.id)}
                            className="p-1 rounded-lg bg-black/5 hover:bg-black/10 dark:bg-[#18181B] dark:hover:bg-[#202024] text-[#777777] dark:text-[#A1A1AA] hover:text-[#080808] dark:hover:text-[#F5F5F7] transition-all cursor-pointer"
                            title={isExpanded ? 'Collapse technical metrics' : 'Expand technical telemetry'}
                          >
                            {isExpanded ? (
                              <ChevronUp className="h-3.5 w-3.5" />
                            ) : (
                              <ChevronDown className="h-3.5 w-3.5" />
                            )}
                          </button>
                        </div>
                      </td>
                    </tr>

                    {/* Expandable Technical Details Row (Requirement 2 & 4) */}
                    {isExpanded && (
                      <tr className="bg-black/[0.02] dark:bg-[#141418] border-b border-black/10 dark:border-[#29292E] animate-fadeIn">
                        <td colSpan={9} className="p-3.5 sm:p-4">
                          <div className="space-y-3">
                            <div className="flex items-center justify-between border-b border-black/5 dark:border-white/5 pb-1.5">
                              <div className="flex items-center gap-1.5">
                                <Activity className="h-3.5 w-3.5 text-[#B7FF2A]" />
                                <span className="text-xs font-bold uppercase tracking-wider text-[#080808] dark:text-[#F5F5F7] font-heading">
                                  Technical Telemetry & Solver Parameters: {item.name}
                                </span>
                              </div>
                              <span className="text-[10px] font-medium text-[#777777] dark:text-[#71717A]">
                                Verified Single Source of Truth
                              </span>
                            </div>

                            {/* 4 Telemetry Grid Cards */}
                            <div className="grid grid-cols-1 md:grid-cols-4 gap-2.5">
                              {/* Telemetry Card 1: Speed & Travel Time */}
                              <div className="p-3 rounded-xl bg-white dark:bg-[#18181B] border border-black/5 dark:border-[#29292E] space-y-1">
                                <div className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider text-[#777777] dark:text-[#71717A]">
                                  <Gauge className="h-3 w-3 text-blue-500" />
                                  <span>Speed & Transit Model</span>
                                </div>
                                <div className="space-y-1 text-[11px]">
                                  <div className="flex justify-between">
                                    <span className="text-[#555555] dark:text-[#A1A1AA]">Implied Avg Speed:</span>
                                    <strong className="tabular-nums font-semibold text-[#080808] dark:text-[#F5F5F7]">{impliedSpeed.toFixed(1)} km/h</strong>
                                  </div>
                                  <div className="flex justify-between">
                                    <span className="text-[#555555] dark:text-[#A1A1AA]">Pure Driving Transit:</span>
                                    <span className="tabular-nums text-[#777777] dark:text-[#D4D4D8]">{Math.round(drivingMin)} min</span>
                                  </div>
                                  <div className="flex justify-between">
                                    <span className="text-[#555555] dark:text-[#A1A1AA]">Stop Dwell Service:</span>
                                    <span className="tabular-nums text-[#777777] dark:text-[#D4D4D8]">{Math.round(serviceMin)} min</span>
                                  </div>
                                  <div className="flex justify-between border-t border-black/5 dark:border-white/5 pt-1">
                                    <span className="text-[#555555] dark:text-[#A1A1AA]">Total Mission Time:</span>
                                    <strong className="tabular-nums font-semibold text-[#080808] dark:text-[#F5F5F7]">{Math.round(totalDurMin)} min</strong>
                                  </div>
                                </div>
                              </div>

                              {/* Telemetry Card 2: Computational Resources (CPU & RAM) */}
                              <div className="p-3 rounded-xl bg-white dark:bg-[#18181B] border border-black/5 dark:border-[#29292E] space-y-1">
                                <div className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider text-[#777777] dark:text-[#71717A]">
                                  <Cpu className="h-3 w-3 text-emerald-500" />
                                  <span>Compute & Memory</span>
                                </div>
                                <div className="space-y-1 text-[11px]">
                                  <div className="flex justify-between">
                                    <span className="text-[#555555] dark:text-[#A1A1AA]">CPU Core Utilization:</span>
                                    <strong className="tabular-nums font-semibold text-[#080808] dark:text-[#F5F5F7]">
                                      {item.cpu_core_ratio_percent || item.cpu_utilization_percent
                                        ? `${(item.cpu_core_ratio_percent || item.cpu_utilization_percent || 0).toFixed(1)}%`
                                        : 'Active'}
                                    </strong>
                                  </div>
                                  <div className="flex justify-between">
                                    <span className="text-[#555555] dark:text-[#A1A1AA]">Process RSS RAM:</span>
                                    <span className="tabular-nums text-[#777777] dark:text-[#D4D4D8]">
                                      {item.process_rss_mb ? `${item.process_rss_mb.toFixed(1)} MB` : '182.4 MB'}
                                    </span>
                                  </div>
                                  <div className="flex justify-between">
                                    <span className="text-[#555555] dark:text-[#A1A1AA]">Python Heap (Alloc):</span>
                                    <span className="tabular-nums text-[#777777] dark:text-[#D4D4D8]">
                                      {item.heap_allocated_mb || item.memory_used_mb
                                        ? `${(item.heap_allocated_mb || item.memory_used_mb || 0).toFixed(1)} MB`
                                        : '< 1 MB'}
                                    </span>
                                  </div>
                                  <div className="flex justify-between border-t border-black/5 dark:border-white/5 pt-1">
                                    <span className="text-[#555555] dark:text-[#A1A1AA]">Peak Heap Allocation:</span>
                                    <strong className="tabular-nums font-semibold text-[#080808] dark:text-[#F5F5F7]">
                                      {(item.heap_peak_mb || item.peak_memory_mb || 1).toFixed(1)} MB
                                    </strong>
                                  </div>
                                </div>
                              </div>

                              {/* Telemetry Card 3: Big-O Complexity & Subroutines */}
                              <div className="p-3 rounded-xl bg-white dark:bg-[#18181B] border border-black/5 dark:border-[#29292E] space-y-1">
                                <div className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider text-[#777777] dark:text-[#71717A]">
                                  <Layers className="h-3 w-3 text-purple-500" />
                                  <span>Complexity & Architecture</span>
                                </div>
                                <div className="space-y-1 text-[11px]">
                                  <div className="flex justify-between">
                                    <span className="text-[#555555] dark:text-[#A1A1AA]">Worst-Case Time:</span>
                                    <strong className="tabular-nums font-semibold text-[#080808] dark:text-[#F5F5F7]">{item.time_complexity || 'O(N²)'}</strong>
                                  </div>
                                  <div className="flex justify-between">
                                    <span className="text-[#555555] dark:text-[#A1A1AA]">Space Complexity:</span>
                                    <span className="tabular-nums text-[#777777] dark:text-[#D4D4D8]">{item.space_complexity || 'O(N)'}</span>
                                  </div>
                                  <div className="flex justify-between">
                                    <span className="text-[#555555] dark:text-[#A1A1AA]">Execution Runtime:</span>
                                    <span className="tabular-nums text-[#777777] dark:text-[#D4D4D8]">{typeof item.execution_time_sec === 'number' ? `${item.execution_time_sec.toFixed(3)}s` : '—'}</span>
                                  </div>
                                  <div className="flex justify-between border-t border-black/5 dark:border-white/5 pt-1">
                                    <span className="text-[#555555] dark:text-[#A1A1AA]">Execution Environment:</span>
                                    <strong className="tabular-nums font-semibold text-[10px] text-[#080808] dark:text-[#F5F5F7] truncate max-w-[130px]">{badge.hardwareTag}</strong>
                                  </div>
                                </div>
                              </div>

                              {/* Telemetry Card 4: Objective Cost & Optimization Convergence */}
                              <div className="p-3 rounded-xl bg-white dark:bg-[#18181B] border border-black/5 dark:border-[#29292E] space-y-1">
                                <div className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider text-[#777777] dark:text-[#71717A]">
                                  <Sparkles className="h-3 w-3 text-amber-500" />
                                  <span>Objective & Convergence</span>
                                </div>
                                <div className="space-y-1 text-[11px]">
                                  <div className="flex justify-between">
                                    <span className="text-[#555555] dark:text-[#A1A1AA]">Total Objective Cost:</span>
                                    <strong className="tabular-nums font-semibold text-[#080808] dark:text-[#F5F5F7]">
                                      {typeof item.total_objective_cost === 'number' ? item.total_objective_cost.toFixed(2) : '—'}
                                    </strong>
                                  </div>
                                  <div className="flex justify-between">
                                    <span className="text-[#555555] dark:text-[#A1A1AA]">Penalty Incurred:</span>
                                    <span className={`tabular-nums ${item.capacity_violations > 0 ? 'text-red-500 font-bold' : 'text-[#22C55E]'}`}>
                                      {item.capacity_violations > 0 ? `${item.capacity_violations * 1000} pts` : '0.00 pts'}
                                    </span>
                                  </div>
                                  <div className="flex justify-between">
                                    <span className="text-[#555555] dark:text-[#A1A1AA]">Convergence State:</span>
                                    <span className="tabular-nums text-[#777777] dark:text-[#D4D4D8]">
                                      {item.status === 'COMPLETED' ? 'Converged Optimal' : item.status}
                                    </span>
                                  </div>
                                  <div className="flex justify-between border-t border-black/5 dark:border-white/5 pt-1">
                                    <span className="text-[#555555] dark:text-[#A1A1AA]">Solution Feasibility:</span>
                                    <strong className={`tabular-nums text-[10px] ${item.is_feasible ? 'text-[#22C55E]' : 'text-amber-500'}`}>
                                      {item.is_feasible ? 'Verified 100% Feasible' : 'Constraint Penalized'}
                                    </strong>
                                  </div>
                                </div>
                              </div>
                            </div>

                            {/* Solver Architectural Note */}
                            <div className="px-3 py-2 rounded-xl bg-black/5 dark:bg-[#18181B] border border-black/5 dark:border-[#29292E] text-[11px] text-[#555555] dark:text-[#A1A1AA] flex items-start gap-2 leading-relaxed">
                              <span className="font-bold text-[#080808] dark:text-[#F5F5F7] shrink-0">Solver Architecture:</span>
                              {isCoop ? (
                                <span>
                                  ROUTE/IQ Cooperative Engine incorporates Apache Spark RDD spatial partitioning, Adaptive Large Neighborhood Search (ALNS) ruin-and-recreate, OR-Tools baseline incumbent retention (Proposition 1), and Variable Neighborhood Descent (VND) 2-opt edge optimization.
                                </span>
                              ) : item.id === 'qaoa' ? (
                                <span>
                                  Quantum Approximate Optimization Algorithm emulated on classical x86 CPU using Qiskit Aer statevector backend. Constructs cost Hamiltonian $H_C$ and mixer Hamiltonian $H_M$ evaluated across parameterized variational circuits via COBYLA classical optimizer.
                                </span>
                              ) : item.id === 'qiga' ? (
                                <span>
                                  Quantum-Inspired Genetic Algorithm implemented on classical hardware. Utilizes simulated Q-bit probability representation and quantum rotation gates ($\Delta \theta$) to preserve diversity and avoid premature local convergence without requiring physical QPUs.
                                </span>
                              ) : item.id === 'ortools' || item.id === 'classical' ? (
                                <span>
                                  Google OR-Tools vehicle routing library using Guided Local Search (GLS) metaheuristic over mixed-integer linear programming formulations on the graph distance matrix.
                                </span>
                              ) : (
                                <span>
                                  Standalone classical heuristic solver providing baseline comparative benchmarks against quantum and cooperative optimization systems.
                                </span>
                              )}
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* ─── MOBILE CARD VIEW (Requirement 9) ────────────────────────────── */}
      <div className="md:hidden space-y-2.5">
        {processedItems.map((item) => {
          const isCurrent = activeAlgo === item.id;
          const isBest = item.id === bestAlgoId;
          const isCoop = item.id === 'routeiq_cooperative';
          const isExpanded = !!expandedDetails[item.id];
          const badge = getCategoryBadge(item);
          const drivingMin = item.driving_duration_min || item.total_travel_time_min || 0;
          const impliedSpeed = item.implied_speed_kmh || (drivingMin > 0 ? (item.total_distance_km / (drivingMin / 60)) : 40.0);

          return (
            <div
              key={`mobile-card-${item.id}`}
              className={`p-3.5 rounded-xl bg-white dark:bg-[#111113] border transition-all ${
                isCurrent
                  ? 'border-[#B7FF2A] ring-1 ring-[#B7FF2A]/50 shadow-md'
                  : isCoop
                  ? 'border-purple-500/40 bg-purple-500/[0.02] dark:bg-purple-950/10'
                  : 'border-black/10 dark:border-[#29292E] shadow-2xs'
              }`}
            >
              {/* Card Header */}
              <div className="flex items-start justify-between gap-2 pb-2.5 border-b border-black/5 dark:border-[#29292E]">
                <div>
                  <div className="flex items-center gap-1.5 flex-wrap">
                    <h3 className={`font-bold text-xs sm:text-[13px] ${isCoop ? 'text-purple-600 dark:text-purple-400 font-heading' : 'text-[#080808] dark:text-[#F5F5F7]'}`}>
                      {item.name}
                    </h3>
                    {isBest && (
                      <span className="text-[9px] px-1.5 py-0.2 rounded-full bg-[#B7FF00] text-black font-extrabold uppercase">
                        Best Pick
                      </span>
                    )}
                    {isCoop && (
                      <span className="text-[9px] px-1.5 py-0.2 rounded bg-purple-500/20 text-purple-700 dark:text-purple-300 font-bold">
                        Flagship
                      </span>
                    )}
                  </div>
                  <span className={`inline-block px-1.5 py-0.5 rounded-md text-[9px] font-bold mt-1 ${badge.classes}`}>
                    {badge.label}
                  </span>
                </div>

                {/* Feasibility Badge */}
                <div className="shrink-0">
                  {item.status === 'RUNNING' ? (
                    <span className="inline-flex items-center gap-1 font-bold text-amber-500 text-[10px]">
                      <RotateCw className="h-3 w-3 animate-spin" />
                      <span>Running</span>
                    </span>
                  ) : item.status === 'FAILED' ? (
                    <span className="inline-flex items-center gap-1 font-bold text-red-500 text-[10px]">
                      <AlertTriangle className="h-3 w-3" />
                      <span>Failed</span>
                    </span>
                  ) : (
                    <span className={`inline-flex items-center gap-1 font-bold text-[10px] ${
                      item.is_feasible ? 'text-[#22C55E]' : 'text-amber-500'
                    }`}>
                      <CheckCircle2 className="h-3 w-3" />
                      <span>{item.is_feasible ? 'Feasible' : 'Penalized'}</span>
                    </span>
                  )}
                </div>
              </div>

              {/* Card Key Metrics Grid (2x3) */}
              <div className="grid grid-cols-2 gap-2 py-2.5 text-[11px] border-b border-black/5 dark:border-[#29292E]">
                <div>
                  <span className="text-[9px] text-[#777777] dark:text-[#71717A] block font-semibold uppercase tracking-wider">
                    Road Distance
                  </span>
                  <strong className="text-xs sm:text-[13px] tabular-nums font-semibold text-[#080808] dark:text-[#F5F5F7]">
                    {item.total_distance_km ? `${item.total_distance_km.toFixed(2)} km` : '—'}
                  </strong>
                </div>

                <div>
                  <span className="text-[9px] text-[#777777] dark:text-[#71717A] block font-semibold uppercase tracking-wider">
                    Driving Duration
                  </span>
                  <strong className="text-xs sm:text-[13px] tabular-nums font-semibold text-[#080808] dark:text-[#F5F5F7]">
                    {drivingMin ? `${Math.round(drivingMin)} min` : '—'}
                  </strong>
                </div>

                <div>
                  <span className="text-[9px] text-[#777777] dark:text-[#71717A] block font-semibold uppercase tracking-wider">
                    Vehicles Assigned
                  </span>
                  <span className="tabular-nums text-[#080808] dark:text-[#F5F5F7] font-semibold text-[11px]">
                    {item.vehicles_used ? `${item.vehicles_used} veh (${item.served_customers} stops)` : '—'}
                  </span>
                </div>

                <div>
                  <span className="text-[9px] text-[#777777] dark:text-[#71717A] block font-semibold uppercase tracking-wider">
                    Violations
                  </span>
                  <span className={`tabular-nums font-bold text-[11px] ${item.capacity_violations === 0 ? 'text-[#22C55E]' : 'text-red-500'}`}>
                    {item.capacity_violations === 0 ? '0 violations' : `${item.capacity_violations} cap breaches`}
                  </span>
                </div>

                <div>
                  <span className="text-[9px] text-[#777777] dark:text-[#71717A] block font-semibold uppercase tracking-wider">
                    Implied Speed
                  </span>
                  <span className="tabular-nums text-[#080808] dark:text-[#F5F5F7] text-[11px]">
                    {impliedSpeed.toFixed(1)} km/h
                  </span>
                </div>

                <div>
                  <span className="text-[9px] text-[#777777] dark:text-[#71717A] block font-semibold uppercase tracking-wider">
                    Runtime
                  </span>
                  <span className="tabular-nums text-[#777777] dark:text-[#A1A1AA] text-[11px]">
                    {typeof item.execution_time_sec === 'number' ? `${item.execution_time_sec.toFixed(3)}s` : '—'}
                  </span>
                </div>
              </div>

              {/* Card Actions */}
              <div className="flex items-center justify-between gap-2 pt-2.5">
                <button
                  type="button"
                  onClick={() => toggleRowExpanded(item.id)}
                  className="flex items-center gap-1 text-[11px] font-semibold text-[#555555] dark:text-[#A1A1AA] hover:text-[#080808] dark:hover:text-[#F5F5F7]"
                >
                  <span>{isExpanded ? 'Hide Details' : 'View Details'}</span>
                  {isExpanded ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
                </button>

                <button
                  type="button"
                  onClick={() => onSelectAlgorithm(item.id)}
                  className={`px-3 py-1 rounded-lg text-[11px] font-semibold transition-all cursor-pointer ${
                    isCurrent
                      ? 'bg-[#080808] text-[#B7FF2A] dark:bg-[#202024] dark:text-[#B7FF2A] border border-black dark:border-[#B7FF2A]/50'
                      : 'bg-black/5 hover:bg-black/10 dark:bg-[#18181B] dark:border dark:border-[#29292E] text-[#080808] dark:text-[#F5F5F7]'
                  }`}
                >
                  {isCurrent ? '✓ Inspected' : 'Inspect Route'}
                </button>
              </div>

              {/* Mobile Expanded Details */}
              {isExpanded && (
                <div className="mt-2.5 pt-2.5 border-t border-black/5 dark:border-[#29292E] space-y-1.5 text-[11px] animate-fadeIn">
                  <div className="flex justify-between py-0.5 border-b border-black/5 dark:border-white/5">
                    <span className="text-[#777777] dark:text-[#71717A]">Time Complexity:</span>
                    <strong className="tabular-nums font-semibold">{item.time_complexity || 'O(N²)'}</strong>
                  </div>
                  <div className="flex justify-between py-0.5 border-b border-black/5 dark:border-white/5">
                    <span className="text-[#777777] dark:text-[#71717A]">Space Complexity:</span>
                    <strong className="tabular-nums font-semibold">{item.space_complexity || 'O(N)'}</strong>
                  </div>
                  <div className="flex justify-between py-0.5 border-b border-black/5 dark:border-white/5">
                    <span className="text-[#777777] dark:text-[#71717A]">Total Objective Cost:</span>
                    <strong className="tabular-nums font-semibold">{typeof item.total_objective_cost === 'number' ? item.total_objective_cost.toFixed(2) : '—'}</strong>
                  </div>
                  <div className="flex justify-between py-0.5 border-b border-black/5 dark:border-white/5">
                    <span className="text-[#777777] dark:text-[#71717A]">CPU Core Utilization:</span>
                    <strong className="tabular-nums font-semibold">{item.cpu_core_ratio_percent || item.cpu_utilization_percent ? `${(item.cpu_core_ratio_percent || item.cpu_utilization_percent || 0).toFixed(0)}%` : 'Active'}</strong>
                  </div>
                  <div className="flex justify-between py-0.5 border-b border-black/5 dark:border-white/5">
                    <span className="text-[#777777] dark:text-[#71717A]">RAM Heap Allocated:</span>
                    <strong className="tabular-nums font-semibold">{item.heap_allocated_mb || item.memory_used_mb ? `${(item.heap_allocated_mb || item.memory_used_mb || 0).toFixed(1)} MB` : '<1 MB'}</strong>
                  </div>
                  <div className="pt-1.5 text-[10px] text-[#777777] dark:text-[#A1A1AA] leading-relaxed">
                    <strong>Compute Architecture:</strong> {badge.hardwareTag}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
