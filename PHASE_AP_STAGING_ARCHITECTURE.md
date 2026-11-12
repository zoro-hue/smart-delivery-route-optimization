# Phase AP: Isolated Staging Architecture & Environment Topology

## 1. Executive Summary

Phase AP establishes an isolated staging architecture for ROUTE/IQ. This architecture connects the Vercel research preview environment directly to an independent Render staging backend running the latest code from `research/phase-ae-backend-integration` (commit `dfb0cdf` and subsequent commits), while ensuring the live production application on `main` remains untouched and protected.

---

## 2. Root Cause Analysis: Why Preview Requests Reached Production

During Phase AO, live network probes confirmed that the Vercel preview deployment was calling the production Render backend (`https://route-iq-backend.onrender.com`), which returned only 7 legacy algorithms instead of the 11 research algorithms.

Comprehensive code and configuration inspection revealed the exact tri-fold root cause:

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                      PREVIOUS PREVIEW ROUTING PATH                               │
│                                                                                  │
│  [ Vercel Preview Frontend ]                                                     │
│   (research branch build)                                                        │
│           │                                                                      │
│           ├─ 1. Vite loads frontend/.env.production at compile time              │
│           │     (VITE_API_URL=https://route-iq-backend.onrender.com)             │
│           │                                                                      │
│           ├─ 2. api.ts resolves API_BASE to https://route-iq-backend.onrender.com│
│           │     and falls back to PRODUCTION_BACKEND_URL                         │
│           │                                                                      │
│           └─ 3. vercel.json rewrite hardcodes destination:                       │
│                 https://route-iq-backend.onrender.com/api/:path*                 │
│                                                                                  │
│                                    ▼                                             │
│                   [ Render Production Backend (main) ]                           │
│                      (7 legacy algorithms, a8eb849)                              │
└──────────────────────────────────────────────────────────────────────────────────┘
```

1. **Compile-Time Inlining via `frontend/.env.production`:**
   Vite’s production build (`vite build`) automatically loads `frontend/.env.production`. That file contained:
   ```env
   VITE_API_URL=https://route-iq-backend.onrender.com
   VITE_API_BASE_URL=https://route-iq-backend.onrender.com
   ```
   Unless overridden by an explicit Vercel environment variable, this baked the production Render URL directly into the compiled JavaScript bundle (`dist/assets/index-*.js`).
2. **Hardcoded Fallback in `frontend/src/services/api.ts`:**
   `api.ts` defined:
   ```typescript
   const PRODUCTION_BACKEND_URL = 'https://route-iq-backend.onrender.com';
   ...
   const API_BASE = rawApiUrl
     ? ...
     : (import.meta.env.PROD || isBrowserProd
         ? `${PRODUCTION_BACKEND_URL}/api`
         : '/api');
   ```
   When running in any remote browser (`isBrowserProd == true`), it defaulted unconditionally to the production backend.
3. **Static Reverse Proxy in `vercel.json`:**
   Both root `vercel.json` and `frontend/vercel.json` contained:
   ```json
   {
     "source": "/api/:path*",
     "destination": "https://route-iq-backend.onrender.com/api/:path*"
   }
   ```
   Because Vercel rewrites in `vercel.json` are static across all deployments, any relative `/api` calls were automatically forwarded to Render production.

---

## 3. Isolated Dual-Environment Architecture

To eliminate this coupling, ROUTE/IQ implements strict environment segregation:

```
══════════════════════════════════════════════════════════════════════════════════════
                            DUAL-ENVIRONMENT TOPOLOGY
══════════════════════════════════════════════════════════════════════════════════════

 [ PRODUCTION ENVIRONMENT — PROTECTED & UNCHANGED ]
 ───────────────────────────────────────────────────
  Git Branch:         main (a8eb849988201d7929566f331c1ae3afac09b632)
  Vercel Frontend:    https://route-iq-frontend-nine.vercel.app
  Render Backend:     https://route-iq-backend.onrender.com
  Database:           Production SQLite / PostgreSQL (routeiq.db)
  Algorithm Count:    7 Legacy Algorithms
  Status:             100% Locked; Zero Changes

 [ RESEARCH STAGING ENVIRONMENT — ISOLATED & AUTONOMOUS ]
 ────────────────────────────────────────────────────────
  Git Branch:         research/phase-ae-backend-integration (dfb0cdf+)
  Vercel Frontend:    https://route-iq-frontend-git-resear-*.vercel.app (Preview)
  Render Backend:     https://route-iq-backend-staging.onrender.com (New Service)
  Database:           Isolated Staging SQLite (staging_routeiq.db)
  Algorithm Count:    11 Canonical Algorithms (Cooperative + Standalone Metaheuristics)
  Route Repair:       Universal Coverage R == I + Capacity-Aware Merging
  Quantum Candor:     QAOA with Qiskit Aer/statevector CPU simulation
  Status:             Configured & Prepared for Activation
══════════════════════════════════════════════════════════════════════════════════════
```

---

## 4. Key Isolation Guarantees

1. **Independent Git Branch Triggers:**
   - Production (`routeiq-backend`) rebuilds ONLY when commits land on `main`.
   - Staging (`routeiq-backend-staging`) rebuilds automatically when commits are pushed to `research/phase-ae-backend-integration`.
2. **Zero Cross-Environment Contamination:**
   - Database isolation: Staging uses `DATABASE_URL=sqlite+aiosqlite:///./staging_routeiq.db`. It never reads or writes to the production database.
   - Secrets isolation: Staging does not share or expose production credentials.
3. **Fail-Safe Preview API Routing (No Silent Fallback):**
   - `frontend/src/services/api.ts` actively inspects `window.location.hostname`.
   - If on a Vercel preview domain (`route-iq-frontend-*.vercel.app`), it strictly routes to `https://route-iq-backend-staging.onrender.com/api`.
   - If staging is unavailable, the application logs an explicit warning in the console. It **never falls back to production**.
4. **CORS Boundary Compliance:**
   - Backend CORS in `backend/app/main.py` matches `^https:\/\/.*\.vercel\.app$`, allowing both production and preview Vercel domains while rejecting unauthorized origins.
