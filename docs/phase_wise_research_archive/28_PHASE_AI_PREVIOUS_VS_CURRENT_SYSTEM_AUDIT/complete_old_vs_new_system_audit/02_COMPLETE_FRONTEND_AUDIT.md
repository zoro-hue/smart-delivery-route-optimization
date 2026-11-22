# 02 — COMPLETE FRONTEND ARCHITECTURE AND SUBSYSTEM AUDIT

**Project Title:** ROUTE/IQ: Smart Delivery Route Optimization Using Hybrid Big Data and Quantum Computing  
**Institution:** Department of Computer Science and Engineering, SRM University-AP  
**Original Version Baseline:** `main` at commit `a8eb849`  
**Current Research Baseline:** `research/journal-readiness` at commit `feb0920`  

---

## 1. Frontend Architectural Overview

The ROUTE/IQ frontend is a client-side Single Page Application (SPA) built with **React 19**, **TypeScript**, and **Vite 5**. It delivers an interactive geospatial dispatch console where dispatchers can configure delivery campaigns, explore Manhattan and Brooklyn street networks, simulate traffic congestion, select routing algorithms, and analyze turn-by-turn vehicle routes.

```
+----------------------------------------------------------------------------------------------------+
|                                    FRONTEND STACK INVENTORY                                        |
+----------------------------------------------------------------------------------------------------+
| Framework:            React 19.0.0 (Function components with Hooks)                                |
| Build Tool:           Vite 5.4.x (ESM bundling, Hot Module Replacement)                            |
| Language:             TypeScript 5.x (Strict typing enabled in tsconfig.json)                      |
| Styling:              Tailwind CSS 3.4.x with custom theme tokens & dark/light palettes            |
| Map Engine:           Leaflet 1.9.4 & React-Leaflet (CartoDB Positron / Dark Matter basemaps)      |
| HTTP Client:          Axios 1.7.x with environment-aware baseURL switching                         |
| Icons:                Lucide React (Vector SVG icon pack)                                          |
| Deployment Target:    Vercel Single Page Application with URL rewrite rules                        |
+----------------------------------------------------------------------------------------------------+
```

---

## 2. Frontend Structure & Application Initialization

### 2.1 Initialization Lifecycle
1. **`index.html`:** The HTML5 host template. Injects Google Fonts (Inter, JetBrains Mono) and sets up the root DOM node `<div id="root"></div>`.
2. **`frontend/src/main.tsx`:** The React entry point:
   - Mounts the application inside `React.StrictMode`.
   - Wraps the root with `ThemeProvider` (`frontend/src/context/ThemeContext.tsx`) and `SettingsProvider` (`frontend/src/context/SettingsContext.tsx`).
   - Renders `<App />`.
3. **`frontend/src/App.tsx`:** The root application coordinator:
   - Manages global state: `activeTab`, `datasets`, `analytics`, `backendHealth`, `lastResult`, `isScanning`, and `isRefreshing`.
   - Persists the active tab in browser `localStorage` under key `routeiq_active_tab` (defaults to `'overview'`).
   - Renders the global `<Navbar />` header and a dynamic tab container rendering the corresponding page component.

### 2.2 Navigation and Routing Architecture
Instead of utilizing a heavy client-side router like `react-router-dom`, ROUTE/IQ implements a **lightweight, tab-based state router** in `App.tsx`:
- Active tabs are tracked via a string state: `'overview'` | `'plan'` | `'datasets'` | `'results'` | `'experiments'` | `'settings'`.
- All tab panes remain instantiated in the DOM, toggled between `tab-pane-active` (visible) and `tab-pane-inactive` (`display: none`). This prevents expensive re-renders and preserves interactive map state and Leaflet canvas contexts when switching between tabs.
- When `activeTab === 'plan'`, the main container switches to full-bleed layout (`h-[calc(100dvh-4rem)] overflow-hidden`) to maximize interactive map canvas space.

### 2.3 State Management & Context Providers
- **`ThemeContext.tsx`:** Manages light/dark mode. Toggles the `dark` class on the root `document.documentElement` element. Persists preference in `localStorage.getItem('routeiq_theme')` (defaults to `'dark'`).
- **`SettingsContext.tsx`:** Centralizes dispatch parameters, default vehicle capacity ($Q = 100.0\text{ kg}$), default fleet count ($K = 4$), classical solver time limits (4s), and QAOA circuit parameters (depth $p=2$, shots 1024, penalty 100.0).
- **Authentication:** **Not implemented.** ROUTE/IQ is designed as an open research and internal dispatch cockpit; there are no user login screens, JWT tokens, or RBAC controls.

---

## 3. Detailed Page-by-Page Forensic Audit

The codebase contains **11 page components** in `frontend/src/pages/`. A critical forensic finding is that **6 pages are actively mounted** in the application navigation, while **5 pages are unmounted auxiliary components** retained from earlier iterations:

### 3.1 Actively Mounted Pages in `App.tsx`

| Page Name | File Path | User Capabilities & Key Features | API Endpoints Called | Internal State Maintained | What Changed from Original |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Overview Dashboard** | `frontend/src/pages/OverviewDashboard.tsx` (67.8 KB) | Landing page. Displays 3D rotating logistics hero cube, high-level fleet statistics (total orders, total distance, fleet capacity utilization), operational health badge, educational video lecture cards ("Watch and Learn"), and quick-start action cards. | `GET /api/analytics/summary`, `GET /api/health`, `POST /api/datasets/scan-workspace` | `activeTab`, `isScanning`, modal video playback state | Cleaned up in commit `82e3915`: removed mock dashboard demonstrations, retained verified educational lectures. |
| **Plan Workspace** | `frontend/src/pages/PlanWorkspace.tsx` (77.2 KB) | **The primary application workspace.** Full-bleed interactive Leaflet map. Allows selecting preset stops (18-stop Manhattan showcase, 10-stop Brooklyn cluster), clicking on map to add custom customer stops, dragging origin depot, configuring vehicle count ($K$), payload capacity ($Q$), traffic scenario, weather friction, classical time limits, and triggering optimization. | `POST /api/optimization/run`, `POST /api/optimization/estimate`, `GET /api/delivery-stops`, `GET /api/road-network` | `activeStops`, `depotCoords`, `capacity`, `vehicles`, `algorithm`, `selectionMode`, `trafficScenario`, `isOptimizing` | Refactored in `b8fc7f2` and `0538e3f`: added 4s responsive time limit, synchronized stop markers (1..18) with glowing 'D' depot marker. |
| **Dataset Management** | `frontend/src/pages/DatasetManagement.tsx` (25.3 KB) | Portal for managing delivery datasets. Features drag-and-drop CSV file upload, automated workspace scanning (`scan-workspace`), schema inspection, tabular row preview, column mapping modal, and Parquet ETL trigger. | `GET /api/datasets`, `POST /api/datasets/upload`, `POST /api/datasets/scan-workspace`, `POST /api/datasets/{id}/process`, `GET /api/datasets/{id}/preview` | `selectedDataset`, `previewRows`, `isUploading`, `isProcessing`, `columnMapping` | Updated in `3b2b40a`: added deterministic dataset IDs, resilient zip extraction, and interactive progress toasts. |
| **Results View** | `frontend/src/pages/ResultsView.tsx` (34.8 KB) | Renders computed route solutions. Interactive Leaflet map showing colored turn-by-turn road polylines per vehicle. Summary metrics cards (distance, time, capacity utilization). Per-vehicle route breakdown tabs showing sequential stop lists, parcel weights, and leg distances. | Reads `lastResult` passed via React props from `App.tsx` (cached in `localStorage`). | `selectedVehicleRoute`, `expandedStopIndex`, `mapViewMode` | Updated in `a8eb849`: aligned stop numbering (1..18) with Plan workspace and added glowing 'D' depot icon. |
| **Experiment History** | `frontend/src/pages/ExperimentHistory.tsx` (23.9 KB) | Historical log of all optimization executions. Paginated table showing timestamp, algorithm suite, customer count, fleet distance, travel time, and objective cost. Allows viewing detailed JSON logs, re-running runs, or exporting results. | `GET /api/experiments`, `GET /api/experiments/{id}`, `DELETE /api/experiments/{id}`, `GET /api/experiments/{id}/export` | `experimentsList`, `selectedExperiment`, `currentPage`, `pageSize`, `isExporting` | Preserved from original version; fully operational with SQLite/PostgreSQL persistence. |
| **System Settings** | `frontend/src/pages/SystemSettings.tsx` (17.5 KB) | Settings dashboard. Displays live backend environment health, Python and Qiskit versions, database engine type (SQLite vs PostgreSQL), API URL configuration, road network cache status, and default algorithm parameters. | `GET /api/health`, `GET /api/road-network` | `settingsForm`, `isSaving`, `connectionStatus` | Preserved from original version; reflects active configuration. |

### 3.2 Unmounted Auxiliary Pages in `frontend/src/pages/`

The following 5 pages exist in `frontend/src/pages/` but are **not imported into `App.tsx`**:

1. **`RouteOptimization.tsx` (57.6 KB):**  
   *Forensic Status:* **Historical Predecessor.** This was the original route planning and solver execution page before `PlanWorkspace.tsx` was written. It contains older forms and algorithm toggles. Superseded by `PlanWorkspace.tsx`.
2. **`ComparisonView.tsx` (10.0 KB):**  
   *Forensic Status:* **Auxiliary Benchmark View.** A side-by-side comparison component showing multi-algorithm bar charts and metric delta tables. Designed to accept an array of `OptimizationResponse` objects. Not linked in the top navbar.
3. **`DeliveryMapView.tsx` (10.0 KB):**  
   *Forensic Status:* **Standalone Map Component.** A dedicated full-screen map viewer for rendering raw road-network nodes and customer stops without planning controls.
4. **`DataQualityAnalytics.tsx` (5.7 KB):**  
   *Forensic Status:* **Auxiliary Dataset Quality Sub-View.** Displays missing-value histograms, coordinate bounds integrity, and outlier demand distributions for uploaded datasets.
5. **`TrafficView.tsx` (10.6 KB):**  
   *Forensic Status:* **Auxiliary Traffic Congestion Sub-View.** Renders NYC traffic sensor density and scenario impact multipliers.

---

## 4. UI Components and Functionality Audit

### 4.1 Leaflet Map Engine (`frontend/src/pages/PlanWorkspace.tsx` & `ResultsView.tsx`)
- Maps are instantiated dynamically using native `L.map` and Leaflet 1.9 APIs inside a `useEffect` hook referencing a DOM container ref (`mapContainerRef`).
- **Tile Layers:** Uses CartoDB Positron (`https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png`) in light mode and CartoDB Dark Matter (`https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png`) in dark mode.
- **Custom SVG Markers:**
  - **Depot Marker:** Rendered using `L.divIcon` with a distinctive glowing emerald circle and bold black letter **"D"**.
  - **Customer Stop Markers:** Numbered sequential circular badges (1..18) displaying parcel demand ($q_i\text{ kg}$) on hover tooltips.
  - **Turn-by-Turn Road Polylines:** Rendered using `L.polyline` with distinct vehicle colors (Indigo, Emerald, Amber, Rose) using coordinates traced from the NYC road graph.

### 4.2 Algorithm Selection Controls (`PlanWorkspace.tsx`)
The workspace provides three distinct algorithm selection modes:
1. **Recommended Mode:** Defaults to **Google OR-Tools (CVRP)**, the primary classical baseline.
2. **Compare Mode:** Simultaneously runs a benchmark suite across classical solvers (`ortools`, `clarke_wright`, `two_opt`, `dijkstra`, `astar`) and quantum-inspired (`qiga`). If customer count $N \le 8$, also enables `qaoa`.
3. **Custom Mode:** Allows individual multi-selection of algorithms via interactive toggle cards.

### 4.3 3D Hero Cube (`frontend/src/components/hero/LogisticsRouteCube.tsx`)
A custom interactive CSS 3D cube rendered on the Overview Dashboard. Features animated rotation displaying logistics metrics (distance, stops, vehicles, Qiskit quantum state) on its 6 faces.

---

## 5. Frontend-to-Backend Integration Layer (`frontend/src/services/api.ts`)

The API client abstracts all HTTP communication using Axios:

```typescript
const PRODUCTION_BACKEND_URL = 'https://route-iq-backend.onrender.com';
const rawApiUrl = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL;

const API_BASE = rawApiUrl
  ? (rawApiUrl.endsWith('/api') ? rawApiUrl : `${rawApiUrl.replace(/\/$/, '')}/api`)
  : (import.meta.env.PROD || isBrowserProd
      ? `${PRODUCTION_BACKEND_URL}/api`
      : '/api');

const http = axios.create({
  baseURL: API_BASE,
  timeout: 120000, // 2-minute timeout for complex quantum simulations
});
```

### 5.1 Key API Client Functions
- `api.runOptimization(params)`: Sends `POST /api/optimization/run`.
- `api.getDatasets()`: Sends `GET /api/datasets`.
- `api.scanWorkspace()`: Sends `POST /api/datasets/scan-workspace`.
- `api.uploadDataset(formData)`: Sends `POST /api/datasets/upload`.
- `api.getPreview(datasetId, rows)`: Sends `GET /api/datasets/{id}/preview`.
- `api.getAnalyticsSummary()`: Sends `GET /api/analytics/summary`.
- `api.checkHealth()`: Sends `GET /api/health`.
- `api.getExperiments(page, size)`: Sends `GET /api/experiments`.

### 5.2 Error Handling & Resilience
- **HTML Response Interception:** Detects if cloud proxy rewrites accidentally returned `<!doctype html>` (e.g. 404/502 error pages) and converts them into human-readable error messages.
- **Reprocess Fallback:** `api.reprocessDataset` executes a fallback chain (`extract` $\to$ `validate` $\to$ `process`) if a direct reprocess call fails.
