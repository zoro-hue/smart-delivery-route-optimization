# Phase AP: Render Staging Backend Configuration Blueprint

## 1. Specification Overview

This document specifies the exact configuration for provisioning the isolated **Render Staging Web Service** for ROUTE/IQ.

- **Service Name:** `routeiq-backend-staging`
- **Render URL:** `https://routeiq-backend-staging.onrender.com`
- **Source Repository:** `https://github.com/zoro-hue/smart-delivery-route-optimization`
- **Target Git Branch:** `research/phase-ae-backend-integration`
- **Runtime Environment:** `Docker`
- **Region:** `oregon` (US West)
- **Instance Plan:** `Free`
- **Health Check Endpoint:** `/health`
- **Root Directory / Build Context:** `.` (Repository root)
- **Dockerfile Path:** `./backend/Dockerfile`

---

## 2. Environment Variables Specification

The staging service requires the following environment variables, configured in `render.staging.yaml` and Render Dashboard:

| Key | Value | Purpose / Rationale |
| :--- | :--- | :--- |
| `ENVIRONMENT` | `staging` | Marks application state as staging; disables verbose development logging while enabling research features. |
| `DEBUG` | `false` | Prevents leaking tracebacks in HTTP error bodies. |
| `PORT` | `8000` | Standard internal container port exposed to Render's reverse proxy. |
| `ALLOWED_ORIGINS` | `https://*,http://localhost:5173` | Allows requests from HTTPS origins and local development. |
| `CORS_ORIGIN_REGEX` | `^https:\/\/.*\.vercel\.app$\|^https:\/\/.*\.netlify\.app$\|^https:\/\/.*\.onrender\.com$` | Permits dynamic CORS from all Vercel preview domains (`*.vercel.app`) without hardcoding ephemeral preview URLs. |
| `DATABASE_URL` | `sqlite+aiosqlite:///./staging_routeiq.db` | **Complete Database Isolation:** Uses an independent SQLite database for staging experiments, ensuring zero modification of production data. |
| `MALLOC_ARENA_MAX` | `2` | Linux glibc memory optimization preventing memory fragmentation on 512MB RAM free-tier instances. |
| `PYTHONMALLOC` | `malloc` | Direct OS memory allocation for compatibility with `malloc_trim`. |

---

## 3. Blueprint Manifest (`render.staging.yaml`)

The manifest has been created at the root of the repository:

```yaml
# ROUTE/IQ — Render Isolated Staging Backend Blueprint
# ══════════════════════════════════════════════════════════════════════
# Deploys strictly from branch: research/phase-ae-backend-integration
# Completely isolated from the production service (routeiq-backend on main)
# ══════════════════════════════════════════════════════════════════════

services:
  - type: web
    name: routeiq-backend-staging
    runtime: docker
    plan: free
    region: oregon
    branch: research/phase-ae-backend-integration
    dockerfilePath: ./backend/Dockerfile
    dockerContext: .
    healthCheckPath: /health
    envVars:
      - key: ENVIRONMENT
        value: staging
      - key: DEBUG
        value: "false"
      - key: PORT
        value: "8000"
      - key: ALLOWED_ORIGINS
        value: "https://*,http://localhost:5173"
      - key: CORS_ORIGIN_REGEX
        value: "^https:\\/\\/.*\\.vercel\\.app$|^https:\\/\\/.*\\.netlify\\.app$|^https:\\/\\/.*\\.onrender\\.com$"
      - key: DATABASE_URL
        value: "sqlite+aiosqlite:///./staging_routeiq.db"
      - key: MALLOC_ARENA_MAX
        value: "2"
      - key: PYTHONMALLOC
        value: "malloc"
```

---

## 4. Provisioning Procedures

### Option A: Render Web Dashboard (Recommended — Zero Risk to Production)
1. Log in to [dashboard.render.com](https://dashboard.render.com).
2. Click **New +** $\rightarrow$ **Web Service**.
3. Select the repository `zoro-hue/smart-delivery-route-optimization`.
4. Configure the service settings:
   - **Name:** `routeiq-backend-staging`
   - **Branch:** `research/phase-ae-backend-integration`
   - **Region:** `Oregon (US West)`
   - **Runtime:** `Docker`
   - **Dockerfile Path:** `./backend/Dockerfile`
   - **Docker Build Context:** `.` (or leave blank for repository root)
   - **Instance Type:** `Free`
5. Under **Advanced Settings**, add the environment variables listed in Section 2 above.
6. Set **Health Check Path** to `/health`.
7. Click **Create Web Service**.

### Option B: Render Blueprint Deployment
1. In the Render Dashboard, select **Blueprints** $\rightarrow$ **New Blueprint Instance**.
2. Connect `zoro-hue/smart-delivery-route-optimization`.
3. Set the Blueprint Path to `render.staging.yaml` and branch to `research/phase-ae-backend-integration`.
4. Render will preview the new service `routeiq-backend-staging` and provision it without altering `routeiq-backend`.

---

## 5. Post-Activation Verification Protocol

Once provisioned, the staging service will be verified using the following automated probes:

1. **Health Probe:**
   ```bash
   curl -s -i https://routeiq-backend-staging.onrender.com/health
   ```
   *Expected Response:* `HTTP 200 OK`, `{"status": "healthy", "version": "2.0.0", "environment": "staging", ...}`
2. **Algorithm Registry Probe:**
   ```bash
   curl -s https://routeiq-backend-staging.onrender.com/api/optimization/algorithms
   ```
   *Expected Response:* `HTTP 200 OK`, `count: 11`, confirming all 11 algorithms including `routeiq_cooperative`, `tabu_search`, `kernighan_lin`, and `vnd`.
3. **Optimization Execution Probe (18-Stop Test Case):**
   ```bash
   curl -s -X POST https://routeiq-backend-staging.onrender.com/api/optimization/run \
     -H "Content-Type: application/json" \
     -d @test_payload_18_stops.json
   ```
   *Expected Response:* `HTTP 200 OK`, `status: "FEASIBLE"`, 18 served stops, 0 dropped stops, 0 capacity violations.

