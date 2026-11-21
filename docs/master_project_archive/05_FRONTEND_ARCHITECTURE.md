# ROUTE/IQ: Frontend Architecture & Interactive Visualization Engine
**Framework:** React 18.3 + TypeScript 5.2 + Vite 5.0  
**Styling & UI:** Tailwind CSS 3.4 + Lucide React  
**Geospatial Visualization:** Leaflet 1.9 + React-Leaflet 4.2  
**Production URL:** `https://route-iq-frontend-nine.vercel.app`  
**Audit Standard:** Frontend Architecture & Interactive State Review `[VERIFIED]`

---

## 1. Frontend Architectural Overview

The ROUTE/IQ user interface is engineered for real-time comparative visualization of multi-solver combinatorial routing. It bridges complex geospatial road-network geometry with dynamic algorithm comparison matrices, audio-visual feedback, and cloud synchronization diagnostics.

```
+-------------------------------------------------------------------------------+
|                               App.tsx (Root State)                            |
| - Navigation Bar (Active View, Health Probe, Connection Indicator)            |
| - Core Problem State (Stops, Vehicles, Depot, Traffic Multiplier, Weather)   |
| - Solver Results State (Results Map for 11 Solvers, Active Solver Selection) |
+-------------------------------------------------------------------------------+
         |                                |                               |
         v                                v                               v
+------------------+            +-------------------+           +------------------+
|   Sidebar.tsx    |            |   MapView.tsx     |           | ResultsView.tsx  |
| - Dataset Selector|           | - Leaflet Map     |           | - Scorecard Table|
| - Fleet Config   |            | - GeoJSON Polylines|          | - Best Feasible  |
| - Solver Multi-  |            | - Depot & Stops   |           | - 11 Solver Tabs |
|   Select Toggles |            | - Route Fit Bounds|           | - Metric Cards   |
+------------------+            +-------------------+           +------------------+
```

---

## 2. Component Hierarchy & Responsibilities

### 2.1 `Navbar.tsx` (Global Navigation & Backend Diagnostics)
- **Role:** Top-level navigation bar rendering view toggles (`Map View`, `Results & Comparison`, `Dataset Management`, `Algorithm Reference`).
- **Connection Diagnostics:** Probes `/api/health` with a 15-second heartbeat.
- **Visual Status Indicator:**
  - `Connected` (Emerald Pill): Backend responsive and healthy.
  - `Disconnected · Retry` (Rose Pill): Triggers when backend probes time out (e.g., during heavy single-thread solver execution on Render). Features click-to-retry capability.

### 2.2 `Sidebar.tsx` (Parameter Control & Job Submission)
- **Dataset Selection:** Allows choosing between registered NYC datasets or custom upload.
- **Fleet & Stop Sliders:** Dynamically configures customer stop count ($N \in [5, 50]$), fleet size ($K \in [2, 8]$), vehicle capacity ($Q \in [10, 50]$), and depot location.
- **Environmental Modifiers:** Sliders for Traffic Congestion Factor ($1.0\times$ to $2.5\times$) and Weather Impairment (Clear, Rain, Snow).
- **Solver Checkboxes:** Granular selection of which of the 11 algorithms to benchmark.

### 2.3 `MapView.tsx` (Geospatial Visualization Engine)
- **Leaflet Integration:** Embedded Leaflet map centered on New York City metropolitan coordinates (`[40.7128, -74.0060]`).
- **Layer Architecture:**
  1. Base Tile Layer: CartoDB Dark Matter / OpenStreetMap tiles.
  2. Depot Marker Layer: Distinctive crimson warehouse icon with operational capacity details.
  3. Customer Stop Markers: Numbered blue circle markers displaying order demand, arrival time window, and address.
  4. Per-Algorithm Polyline Layers: Renders actual road-network polyline coordinates retrieved from backend graph shortest paths.
- **Route Identity Decoupling:** Each algorithm is mapped to a dedicated visual color theme:
  - `ROUTE/IQ Cooperative`: Emerald Green (`#059669`, weight: 5, dashArray: none)
  - `OR-Tools`: Royal Blue (`#2563EB`, weight: 4)
  - `Clarke-Wright`: Amber (`#D97706`)
  - `2-opt`: Violet (`#7C3AED`)
  - `Tabu Search`: Purple (`#9333EA`)
  - `VND`: Cyan (`#0891B2`)
  - `Kernighan-Lin`: Teal (`#0D9488`)
  - `QAOA`: Indigo (`#4F46E5`, dashed)
  - `QIGA`: Fuchsia (`#C026D3`)
  - `Dijkstra`: Slate (`#64748B`)
  - `A*`: Stone (`#78716C`)

### 2.4 `ResultsView.tsx` (Scorecard & Comparative Analytics)
- **Best Feasible Solution Card:** Prominently highlights the winning algorithm with total distance (km), travel duration (minutes), stop coverage (100%), and constraint violation status (0 violations).
- **Comparative Scorecard Table:** Tabulates all 11 algorithms sorted by total road distance, displaying computation latency (ms), vehicle utilization, and improvement percentage relative to the classical incumbent.
- **Interactive Route Selector:** Allows user to click any algorithm tab to inspect its vehicle route breakdown and focus the map view on its specific geometry.

---

## 3. State Management & Lifecycle Protocol

### 3.1 Job Submission & Polling Engine
1. User clicks **"Run Optimization"** in `Sidebar.tsx`.
2. `App.tsx` dispatches `POST /api/optimization/run` with the payload.
3. Backend immediately returns `job_id` and synchronous primary result for `routeiq_cooperative`.
4. `App.tsx` activates polling loop via `setInterval` every 1,500 ms querying `GET /api/optimization/jobs/{job_id}/status`.
5. As background solvers complete on the backend, state updates progressively:
   - Status indicators update from `Queued` -> `Running` -> `Completed`.
   - Polyline geometries and metrics are merged into the React state tree.
6. When all 11 algorithms complete (or timeout), polling terminates and an audio chime notification fires.

### 3.2 Mobile Responsiveness & Layout
- Full responsive design via Tailwind breakpoints (`sm:`, `md:`, `lg:`, `xl:`).
- Slide-over mobile drawer for parameter adjustment on screens $< 1024$ px wide.
- Split-pane layout on desktop providing 35% control/scorecard pane and 65% interactive map canvas.
