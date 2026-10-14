import React, { useState, useEffect } from 'react';
import { Navbar } from './components/layout/Navbar';
import { OverviewDashboard } from './pages/OverviewDashboard';
import { PlanWorkspace } from './pages/PlanWorkspace';
import { DatasetManagement } from './pages/DatasetManagement';
import { ResultsView } from './pages/ResultsView';
import { ExperimentHistory } from './pages/ExperimentHistory';
import { SystemSettings } from './pages/SystemSettings';
import { ErrorBoundary } from './components/ErrorBoundary';
import { api } from './services/api';
import { Dataset, AnalyticsSummary, OptimizationResponse } from './types';

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

  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [isDatasetsLoading, setIsDatasetsLoading] = useState<boolean>(true);
  const [datasetsError, setDatasetsError] = useState<string | null>(null);
  const [analytics, setAnalytics] = useState<AnalyticsSummary | null>(null);
  const [backendHealth, setBackendHealth] = useState<any>(null);
  const [lastResult, setLastResult] = useState<OptimizationResponse | null>(() => {
    try {
      const saved = localStorage.getItem('routeiq_last_result');
      if (saved) return JSON.parse(saved);
    } catch {}
    return null;
  });
  const [isScanning, setIsScanning] = useState<boolean>(false);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);

  useEffect(() => {
    if (lastResult) {
      try {
        localStorage.setItem('routeiq_last_result', JSON.stringify(lastResult));
      } catch {}
    }
  }, [lastResult]);

  const refreshData = async () => {
    setIsRefreshing(true);
    try {
      const [ds, an, hl] = await Promise.allSettled([
        api.getDatasets(),
        api.getAnalyticsSummary(),
        api.checkHealth(),
      ]);

      if (ds.status === 'fulfilled') {
        setDatasets(ds.value);
        setDatasetsError(null);
      } else {
        const msg = ds.reason?.response?.data?.detail || ds.reason?.message || 'Failed to load datasets';
        setDatasetsError(msg);
        console.error('Data refresh datasets error:', ds.reason);
      }

      if (an.status === 'fulfilled') setAnalytics(an.value);
      if (hl.status === 'fulfilled') setBackendHealth(hl.value);
    } catch (e) {
      console.error('Data refresh error:', e);
    } finally {
      setIsDatasetsLoading(false);
      setTimeout(() => setIsRefreshing(false), 400);
    }
  };

  useEffect(() => {
    refreshData();
  }, []);

  const handleScanWorkspace = async () => {
    setIsScanning(true);
    setDatasetsError(null);
    try {
      await api.scanWorkspace();
      await refreshData();
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
          <OverviewDashboard
            analytics={analytics}
            datasets={datasets}
            backendHealth={backendHealth}
            onNavigate={(tab) => handleSelectTab(tab === 'optimization' ? 'plan' : tab)}
            onScanDatasets={handleScanWorkspace}
            isScanning={isScanning}
          />
        </div>

        <div className={activeTab === 'plan' ? 'tab-pane-active h-full w-full relative' : 'tab-pane-inactive'}>
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
          <DatasetManagement
            datasets={datasets}
            onRefresh={refreshData}
            onScanDatasets={handleScanWorkspace}
            isScanning={isScanning}
            isLoading={isDatasetsLoading}
            error={datasetsError}
          />
        </div>

        <div className={activeTab === 'results' ? 'tab-pane-active' : 'tab-pane-inactive'}>
          <ResultsView
            result={lastResult}
            onNavigateToPlan={() => handleSelectTab('plan')}
            isActive={activeTab === 'results'}
          />
        </div>

        <div className={activeTab === 'experiments' ? 'tab-pane-active' : 'tab-pane-inactive'}>
          <ExperimentHistory isActive={activeTab === 'experiments'} />
        </div>

        <div className={activeTab === 'settings' ? 'tab-pane-active' : 'tab-pane-inactive'}>
          <SystemSettings
            backendHealth={backendHealth}
            onRefreshHealth={refreshData}
            onSettingsApplied={refreshData}
          />
        </div>
      </main>
    </div>
  );
};

export default App;
