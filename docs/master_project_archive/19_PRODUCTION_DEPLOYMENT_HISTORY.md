# ROUTE/IQ: Production Deployment History & Cloud Infrastructure
**Backend Cloud Provider:** Render Cloud (`route-iq-backend.onrender.com`)  
**Frontend Cloud Provider:** Vercel Edge Network (`route-iq-frontend-nine.vercel.app`)  
**Staging Environment:** Render Staging (`routeiq-backend-staging.onrender.com`)  
**Audit Standard:** Cloud Systems Engineering & Deployment Verification `[VERIFIED]`

---

## 1. Production Architecture Overview

ROUTE/IQ operates as a decoupled cloud microservice architecture:

```
[ User Browser / Mobile Client ]
              |
              | HTTPS (Port 443)
              v
+-------------------------------------------------------------+
| VERCEL EDGE CDN                                             |
| route-iq-frontend-nine.vercel.app                           |
| - Global Anycast CDN, React 18 SPA, Vite Static Assets      |
| - Vercel Rewrite Proxy: /api/* -> Render Backend            |
+-------------------------------------------------------------+
              |
              | HTTPS (Port 443)
              v
+-------------------------------------------------------------+
| RENDER WEB SERVICE                                          |
| route-iq-backend.onrender.com                               |
| - Python 3.11 Runtime, Uvicorn ASGI, FastAPI                |
| - Resource Ceilings: 0.5 Virtual CPU, 512 MB Physical RAM   |
| - In-Memory CSR Road Graph + SQLite WAL Job DB              |
+-------------------------------------------------------------+
```

---

## 2. Infrastructure Constraints & Cloud Hardening

### 2.1 Render Free-Tier Hardware Limits
- **CPU:** Shared single-core virtual CPU.
- **Physical Memory:** 512 MB strict ceiling. Exceeding 512 MB triggers immediate Linux kernel Out-Of-Memory termination (`SIGKILL 137`).
- **Cold-Start Inactivity Spin-Down:** Free instances spin down after 15 minutes of zero traffic. First incoming request triggers a container cold start taking 30–50 seconds.
- **FastAPI / Render Safeguards:**
  - Startup memory optimized from 1,240 MB to 280 MB via CSR sparse matrix loading.
  - Health check endpoint `/api/health` engineered to execute in $< 5$ ms to satisfy Render's container health probes.
  - Job execution decoupled into fast-path synchronous primary solver and async worker thread-pool to prevent ASGI event loop blocking.

### 2.2 Vercel Frontend Edge Deployment
- **Build Tool:** Vite 5.0 with TypeScript compilation.
- **Vercel API Configuration (`vercel.json`):**
  Configured with transparent reverse-proxy rewrites routing `/api/:path*` to `https://route-iq-backend.onrender.com/api/:path*`, completely eliminating browser Cross-Origin Resource Sharing (CORS) preflight latencies.
