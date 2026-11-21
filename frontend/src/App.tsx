import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Navbar } from './components/layout/Navbar';
import { OverviewDashboard } from './pages/OverviewDashboard';
import { PlanWorkspace } from './pages/PlanWorkspace';
import { DatasetManagement } from './pages/DatasetManagement';
import { ResultsView } from './pages/ResultsView';
import { ExperimentHistory } from './pages/ExperimentHistory';
import { SystemSettings } from './pages/SystemSettings';
import { ErrorBoundary } from './components/ErrorBoundary';
import { api } from './services/api';
import { Dataset, AnalyticsSummary, OptimizationResponse, DatasetSyncStatus } from './types';

export type ConnectionStatus = 'CONNECTING' | 'CONNECTED' | 'DEGRADED' | 'DISCONNECTED';

export const App: React.FC = () => {
  // Navigation tabs: overview (home) | plan | datasets | results | experiments | settings
  const [activeTab, setActiveTab] = useState<string>(() => {
    return localStorage.getItem('routeiq_active_tab') || 'overview';
  });

  const handleSelectTab = (tab: string) => {
    setActiveTab(tab);
    try {
      localStorage.setItem('routeiq_active_tab', tab);
    } catch {}
  };

  const [datasets, setDatasets] = useState<Dataset[]>(() => {
    try {
      const cached = localStorage.getItem('routeiq_cached_datasets');
      if (cached) {
        const parsed = JSON.parse(cached);
        if (Array.isArray(parsed) && parsed.length > 0) return parsed;
      }
    } catch {}
    return [];
  });
  const [isDatasetsLoading, setIsDatasetsLoading] = useState<boolean>(true);
  const [datasetsError, setDatasetsError] = useState<string | null>(null);
  const [datasetSyncStatus, setDatasetSyncStatus] = useState<DatasetSyncStatus>('CONNECTING');
  const [lastDatasetSyncTime, setLastDatasetSyncTime] = useState<string | null>(() => {
    try {
      return localStorage.getItem('routeiq_last_synced_at') || null;
    } catch {
      return null;
    }
  });
  const [backendConfirmedIds, setBackendConfirmedIds] = useState<string[]>(() => {
    try {
      const stored = localStorage.getItem('routeiq_confirmed_dataset_ids');
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  });
  const activeSyncControllerRef = useRef<AbortController | null>(null);

  const [analytics, setAnalytics] = useState<AnalyticsSummary | null>(null);
  const [backendHealth, setBackendHealth] = useState<any>(null);
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('CONNECTING');
  const [connectionLatencyMs, setConnectionLatencyMs] = useState<number | null>(null);
  const reconnectAttemptRef = useRef<number>(0);
  const reconnectTimerRef = useRef<any>(null);
  const consecutiveHealthFailuresRef = useRef<number>(0);
  const [lastResult, setLastResult] = useState<OptimizationResponse | null>(null);
  const [isScanning, setIsScanning] = useState<boolean>(false);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);

  useEffect(() => {
    if (lastResult) {
      try {
        localStorage.setItem('routeiq_last_result', JSON.stringify(lastResult));
      } catch {}
    }
  }, [lastResult]);

  const checkConnection = useCallback(async (isManual = false) => {
    if (isManual) {
      setConnectionStatus('CONNECTING');
    }
    const t0 = performance.now();
    try {
      const hl = await api.checkHealth();
      const latency = Math.round(performance.now() - t0);
      setConnectionLatencyMs(latency);
      setBackendHealth(hl);
      reconnectAttemptRef.current = 0;
      consecutiveHealthFailuresRef.current = 0;
      if (latency > 3500) {
        setConnectionStatus('DEGRADED');
      } else {
        setConnectionStatus('CONNECTED');
      }
      return true;
    } catch (err: any) {
      console.warn('[ROUTE/IQ Connection] Health check failed:', err?.message || err);
      consecutiveHealthFailuresRef.current += 1;
      setConnectionLatencyMs(null);
      setBackendHealth(null);
      // Check if an optimization job is currently active
      const hasActiveJob = !!localStorage.getItem('routeiq_active_job_id');
      // If an active job is polling or this is only the first failure, flag as DEGRADED instead of immediately displaying DISCONNECTED
      if (hasActiveJob || consecutiveHealthFailuresRef.current < 2) {
        setConnectionStatus('DEGRADED');
      } else {
        setConnectionStatus('DISCONNECTED');
      }
      return false;
    }
  }, []);

  const refreshData = async () => {
    setIsRefreshing(true);
    setIsDatasetsLoading(true);
    setDatasetsError(null);
    setDatasetSyncStatus('SYNCING');

    // Cancel any in-flight sync request to prevent overlapping stale responses
    if (activeSyncControllerRef.current) {
      try {
        activeSyncControllerRef.current.abort();
      } catch {}
    }
    const controller = new AbortController();
    activeSyncControllerRef.current = controller;

    try {
      const [ds, an, hl] = await Promise.allSettled([
        api.getDatasets(controller.signal),
        api.getAnalyticsSummary(),
        api.checkHealth(),
      ]);

      if (ds.status === 'fulfilled') {
        const confirmedIds = ds.value.map((d) => d.id);
        const taggedDatasets = ds.value.map((d) => ({
          ...d,
          is_cached: false,
          sync_source: 'backend' as const,
          last_synced_at: new Date().toISOString(),
        }));
        setDatasets(taggedDatasets);
        setBackendConfirmedIds(confirmedIds);
        setDatasetsError(null);
        const nowIso = new Date().toISOString();
        setLastDatasetSyncTime(nowIso);
        setDatasetSyncStatus(connectionStatus === 'DEGRADED' ? 'DEGRADED' : 'CONNECTED');
        try {
          localStorage.setItem('routeiq_cached_datasets', JSON.stringify(taggedDatasets));
          localStorage.setItem('routeiq_confirmed_dataset_ids', JSON.stringify(confirmedIds));
          localStorage.setItem('routeiq_last_synced_at', nowIso);
        } catch {}
      } else {
        const isAbort = ds.reason?.name === 'CanceledError' || ds.reason?.message === 'canceled';
        if (!isAbort) {
          const msg = ds.reason?.response?.data?.detail || ds.reason?.message || 'Failed to sync with backend datasets';
          setDatasetsError(msg);
          setDatasetSyncStatus(connectionStatus === 'DISCONNECTED' ? 'DISCONNECTED' : 'ERROR');
          // Mark existing datasets as cached so user is clearly informed
          setDatasets((prev) =>
            prev.map((d) => ({
              ...d,
              is_cached: true,
              sync_source: 'cache' as const,
            }))
          );
          console.error('Data refresh datasets error:', ds.reason);
        }
      }

      if (an.status === 'fulfilled') setAnalytics(an.value);
      if (hl.status === 'fulfilled') {
        setBackendHealth(hl.value);
        setConnectionStatus('CONNECTED');
      } else {
        setConnectionStatus('DISCONNECTED');
      }
    } catch (e) {
      console.error('Data refresh error:', e);
    } finally {
      setIsDatasetsLoading(false);
      setTimeout(() => setIsRefreshing(false), 400);
    }
  };

  const handleRetryConnection = useCallback(async () => {
    if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current);
    reconnectAttemptRef.current = 0;
    const ok = await checkConnection(true);
    if (ok) {
      refreshData();
    }
  }, [checkConnection]);

  // Automated background recovery & periodic heartbeat
  useEffect(() => {
    let isMounted = true;

    const scheduleNextProbe = (status: ConnectionStatus) => {
      if (!isMounted) return;
      if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current);

      let delayMs = 45000; // Heartbeat when connected
      if (status === 'DISCONNECTED') {
        // Exponential backoff: 5s, 10s, 20s, max 30s
        const attempt = reconnectAttemptRef.current;
        delayMs = Math.min(5000 * Math.pow(2, Math.min(attempt, 2)), 30000);
        reconnectAttemptRef.current += 1;
      } else if (status === 'DEGRADED') {
        delayMs = 15000;
      }

      reconnectTimerRef.current = setTimeout(async () => {
        if (!isMounted) return;
        const ok = await checkConnection(false);
        scheduleNextProbe(ok ? 'CONNECTED' : 'DISCONNECTED');
      }, delayMs);
    };

    // Initial check
    checkConnection(false).then((ok) => {
      scheduleNextProbe(ok ? 'CONNECTED' : 'DISCONNECTED');
    });

    return () => {
      isMounted = false;
      if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current);
    };
  }, [checkConnection]);

  useEffect(() => {
    refreshData();
  }, []);

  const handleScanWorkspace = async () => {
    setIsScanning(true);
    setDatasetsError(null);
    try {
      const res = await api.scanWorkspace();
      await refreshData();
      if (res?.message) {
        alert(res.message);
      }
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Auto-discovery error';
      setDatasetsError(`Ingestion error: ${msg}`);
      alert(`Auto-discovery error: ${msg}`);
    } finally {
      setIsScanning(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F4F4F2] dark:bg-[#000000] text-[#171717] dark:text-[#F5F5F7] flex flex-col font-sans transition-colors duration-200">
      {/* Unified Top Navigation Header with Centered Glassmorphic Nav */}
      <Navbar
        connectionStatus={connectionStatus}
        connectionLatencyMs={connectionLatencyMs}
        onRetryConnection={handleRetryConnection}
        isBackendHealthy={!!backendHealth}
        activeTab={activeTab}
        onSelectTab={handleSelectTab}
        datasetCount={datasets.length}
        onScanWorkspace={handleScanWorkspace}
        onRefresh={refreshData}
        isScanning={isScanning}
        isRefreshing={isRefreshing}
        onNavigateHome={() => handleSelectTab('overview')}
      />

      {/* Main Content Container (Full-bleed workspace for Plan, Editorial layout for other views) */}
      <main
        className={`flex-1 w-full ${
          activeTab === 'plan'
            ? 'p-0 h-[calc(100dvh-4rem)] max-h-[calc(100dvh-4rem)] overflow-hidden relative'
            : 'max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4'
        }`}
      >
        <div className={activeTab === 'overview' ? 'tab-pane-active' : 'tab-pane-inactive'}>
          <ErrorBoundary fallbackTitle="System Overview Dashboard">
            <OverviewDashboard
              analytics={analytics}
              datasets={datasets}
              backendHealth={backendHealth}
              onNavigate={(tab) => handleSelectTab(tab === 'optimization' ? 'plan' : tab)}
              onScanDatasets={handleScanWorkspace}
              isScanning={isScanning}
            />
          </ErrorBoundary>
        </div>

        <div className={activeTab === 'plan' ? 'tab-pane-active absolute inset-0 w-full h-full' : 'tab-pane-inactive'}>
          <ErrorBoundary fallbackTitle="Delivery Planning Map Workspace">
            <PlanWorkspace
              onOptimizationComplete={(res) => {
                setLastResult(res);
                refreshData();
              }}
              onNavigateToResults={() => handleSelectTab('results')}
              lastResult={lastResult}
              isActive={activeTab === 'plan'}
            />
          </ErrorBoundary>
        </div>

        <div className={activeTab === 'datasets' ? 'tab-pane-active' : 'tab-pane-inactive'}>
          <ErrorBoundary fallbackTitle="Dataset Management Workspace">
            <DatasetManagement
              datasets={datasets}
              syncStatus={datasetSyncStatus}
              lastSyncedAt={lastDatasetSyncTime}
              backendConfirmedIds={backendConfirmedIds}
              onRefresh={refreshData}
              onScanDatasets={handleScanWorkspace}
              isScanning={isScanning}
              isLoading={isDatasetsLoading}
              isRefreshing={isRefreshing}
              error={datasetsError}
            />
          </ErrorBoundary>
        </div>

        <div className={activeTab === 'results' ? 'tab-pane-active' : 'tab-pane-inactive'}>
          <ErrorBoundary fallbackTitle="Route Optimization Results Workspace">
            <ResultsView
              result={lastResult}
              onNavigateToPlan={() => handleSelectTab('plan')}
              isActive={activeTab === 'results'}
            />
          </ErrorBoundary>
        </div>

        <div className={activeTab === 'experiments' ? 'tab-pane-active' : 'tab-pane-inactive'}>
          <ErrorBoundary fallbackTitle="Experiment History Workspace">
            <ExperimentHistory isActive={activeTab === 'experiments'} />
          </ErrorBoundary>
        </div>

        <div className={activeTab === 'settings' ? 'tab-pane-active' : 'tab-pane-inactive'}>
          <ErrorBoundary fallbackTitle="System Settings Workspace">
            <SystemSettings
              backendHealth={backendHealth}
              onRefreshHealth={refreshData}
              onSettingsApplied={refreshData}
            />
          </ErrorBoundary>
        </div>
      </main>
    </div>
  );
};

export default App;
