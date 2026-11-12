# Phase AO: Vercel Preview Deployment & Infrastructure Audit

## 1. Executive Summary

Phase AO independently audits the live deployment status of ROUTE/IQ following the push of commit `dfb0cdf` (Phase AN) to branch `research/phase-ae-backend-integration`.

### Crucial Scientific Finding:
1. **Frontend Vercel Preview Deployment:** Vercel automatically built and deployed commit `dfb0cdf867dcea6db4215d0c52d168c6fd1a056a` to the preview environment (`route-iq-frontend-git-resear-ab06c0-jagujayanth6-2705s-projects.vercel.app`). The Vercel deployment status is **`Ready`** and the GitHub commit status reports `success`.
2. **Backend Target URL:** Both `frontend/src/services/api.ts` (production configuration) and `vercel.json` (serverless reverse proxy) point all `/api/*` traffic to `https://route-iq-backend.onrender.com`.
3. **Live Backend Divergence:** Live HTTP probes to `https://route-iq-backend.onrender.com/api/optimization/algorithms` confirm that the production Render backend is **running commit `a8eb849` (`main`)**, serving only **7 legacy algorithms** (missing `routeiq_cooperative`, `tabu_search`, `kernighan_lin`, and `vnd`).
4. **Authentic Scientific Candor:** In strict adherence to scientific honesty, **we do NOT claim that the new 11-algorithm backend or Phase AM/AN route repair code is active on live Render production**. Render only updates when Pull Request #1 is formally merged into protected `main`. Furthermore, the preview Vercel frontend enforces team deployment protection (authentication wall).

---

## 2. Vercel Preview Deployment Verification

### 2.1 Git and PR Deployment Metadata
- **Repository:** `zoro-hue/smart-delivery-route-optimization`
- **Active Research Branch:** `research/phase-ae-backend-integration`
- **Latest Commit SHA:** `dfb0cdf867dcea6db4215d0c52d168c6fd1a056a`
- **Pull Request:** PR #1 (*"ROUTE/IQ: Cooperative Big Data and Hybrid Quantum-Classical Route Optimization"*)
- **PR Status:** `open` (strictly unmerged)
- **Vercel Bot Deployment Confirmation:**
  - **Project:** `route-iq-frontend`
  - **Deployment ID:** `AzL55rNvyzhDL2V9Tg3agvTufdtW`
  - **Status:** `Ready` / `DEPLOYED`
  - **Timestamp:** `2026-11-12T15:55:43.624Z`
  - **Preview URL:** `https://route-iq-frontend-git-resear-ab06c0-jagujayanth6-2705s-projects.vercel.app`
  - **Commit Status on GitHub:**
    ```json
    {
      "context": "Vercel",
      "state": "success",
      "target_url": "https://vercel.com/jagujayanth6-2705s-projects/route-iq-frontend/AzL55rNvyzhDL2V9Tg3agvTufdtW"
    }
    ```

### 2.2 Preview Frontend Protection
- Probing `https://route-iq-frontend-git-resear-ab06c0-jagujayanth6-2705s-projects.vercel.app` returns `HTTP 200` with `<title>Login – Vercel</title>` due to Vercel Team Deployment Protection.
- The production frontend at `https://route-iq-frontend-nine.vercel.app/` serves the public Single-Page Application (`<title>ROUTEIQ — Smart Delivery Route Optimization | Hybrid Big Data + Quantum Computing</title>`) running from `main` (`a8eb849`).

---

## 3. Backend Routing & Infrastructure Audit

### 3.1 Reverse Proxy & API Base URL
In `frontend/src/services/api.ts` (lines 6–18):
```typescript
const PRODUCTION_BACKEND_URL = 'https://route-iq-backend.onrender.com';
const rawApiUrl = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL;

const API_BASE = rawApiUrl
  ? (rawApiUrl.endsWith('/api') ? rawApiUrl : `${rawApiUrl.replace(/\/$/, '')}/api`)
  : (import.meta.env.PROD || isBrowserProd
      ? `${PRODUCTION_BACKEND_URL}/api`
      : '/api');
```
In `vercel.json` (lines 1–12):
```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://route-iq-backend.onrender.com/api/:path*"
    },
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```
Conclusion: Every frontend environment (production or Vercel preview) directs its backend API requests to `https://route-iq-backend.onrender.com`.

### 3.2 Live Render Production Backend State
A live probe was executed against `https://route-iq-backend.onrender.com`:
- **Endpoint:** `GET /health`
  ```json
  {
    "status": "healthy",
    "app": "Smart Delivery Route Optimization",
    "version": "2.0.0",
    "environment": "production",
    "python_version": "3.11.17",
    "qiskit_version": "2.4.1",
    "database": "sqlite"
  }
  ```
- **Endpoint:** `GET /api/optimization/algorithms`
  ```json
  {
    "status": "success",
    "count": 7,
    "algorithms": [
      {"id": "ortools", "name": "OR-Tools", "category": "classical", "compute_type": "Classical CPU"},
      {"id": "clarke_wright", "name": "Clarke–Wright Savings", "category": "classical", "compute_type": "Classical CPU"},
      {"id": "two_opt", "name": "2-opt", "category": "classical", "compute_type": "Classical CPU"},
      {"id": "dijkstra", "name": "Dijkstra", "category": "classical", "compute_type": "Classical CPU"},
      {"id": "astar", "name": "A*", "category": "classical", "compute_type": "Classical CPU"},
      {"id": "qaoa", "name": "QAOA", "category": "quantum_hybrid", "compute_type": "Classical Statevector Simulation (Qiskit)"},
      {"id": "qiga", "name": "Quantum-Inspired Genetic Algorithm (QIGA/IQGA)", "category": "quantum_inspired", "compute_type": "Classically Simulated Q-Bits"}
    ]
  }
  ```

### 3.3 Diagnostic Comparison: Live Render vs. Research Branch
| Attribute | Live Production Backend (Render) | Research Branch (`dfb0cdf`) | Status |
| :--- | :--- | :--- | :---: |
| **Commit HEAD** | `a8eb849` (`main`) | `dfb0cdf` (`research/phase-ae-backend-integration`) | Divergent |
| **Registered Algorithms** | 7 algorithms | **11 algorithms** | Divergent |
| **ROUTE/IQ Cooperative Engine** | Not deployed | **Active & Verified** (`routeiq_cooperative`) | Researched |
| **Standalone Metaheuristics** | None | **Active** (`tabu_search`, `kernighan_lin`, `vnd`) | Researched |
| **Universal Delivery Coverage** | Standard OR-Tools only | **Strict $R == I$ Enforced** across all 11 algorithms | Researched |
| **Excess-Route Merging** | Naive / Unvalidated | **Capacity-Aware Insertion & Road Reachability** | Researched |
| **Quantum Terminology** | Legacy labels (`"Simulated Q-Bits"`) | **Strict Scientific Candor** (`"QAOA with Qiskit Aer/statevector CPU simulation"`) | Researched |

---

## 4. Verification Gate Compliance

1. **Did we modify protected `main`?** **NO.** `origin/main` remains strictly pinned at `a8eb849988201d7929566f331c1ae3afac09b632`.
2. **Did we merge PR #1?** **NO.** PR #1 remains open and untriggered.
3. **Did we trigger production deployment?** **NO.** No manual deploys or branch rebases were executed.
4. **Is the live preview connected to the new backend?** **NO.** The live preview frontend is linked via `vercel.json` to the production Render backend, which currently runs `main`. Live validation of the new backend must occur locally or via isolated test containers until the faculty approves merging PR #1.
