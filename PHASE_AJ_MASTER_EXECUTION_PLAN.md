# PHASE AJ: MASTER EXECUTION PLAN
## ROUTE/IQ — Journal Readiness, GitHub Publication, and Automated Deployment

**Evaluation Standard:** Applied Systems & Operations Research (IEEE Access / Applied Soft Computing)  
**Current Branch:** `research/phase-ae-backend-integration`  
**Current Commit:** `242c3f5`  
**Protected Main Branch:** `a8eb849988201d7929566f331c1ae3afac09b632` (Strictly Protected)  
**Remote Origin:** `https://github.com/zoro-hue/smart-delivery-route-optimization.git`  
**Date:** November 2026

---

## 1. Stage 1 Comprehensive Audit & Status Assessment

An exhaustive inspection of repository state, Git branches, configuration files, test suites, and documentation reveals the following audit findings:

### 1.1 Documentation & Prior Phase Inventory
- **Phase AI (Architecture & System Comparison):** **COMPLETE.** 8 comprehensive documents created and committed (`PHASE_AI_PREVIOUS_ARCHITECTURE.md`, `PHASE_AI_CURRENT_ARCHITECTURE.md`, `PHASE_AI_PREVIOUS_VS_CURRENT_TECH_STACK.md`, `PHASE_AI_PREVIOUS_VS_CURRENT_WORKFLOW.md`, `PHASE_AI_ALGORITHM_COMPARISON.md`, `PHASE_AI_FEATURE_EVOLUTION.md`, `PHASE_AI_RESEARCH_CONTRIBUTION_EVOLUTION.md`, `PHASE_AI_MASTER_PREVIOUS_VS_CURRENT_COMPARISON.md`).
- **Phase AH:** No dedicated Phase AH files exist; work progresses directly from Phase AI into Phase AJ.
- **Phase AG (Practical Research Novelty & Journal Suitability):** **COMPLETE.** 4 documents created and committed (`PHASE_AG_PRACTICAL_RESEARCH_NOVELTY.md`, `PHASE_AG_RESEARCH_CONTRIBUTIONS.md`, `PHASE_AG_JOURNAL_READINESS_ASSESSMENT.md`, `PHASE_AG_DEFENSIBLE_NOVELTY_STATEMENT.md`).
- **Phase AF (Independent Research Novelty Proof or Disproof):** **COMPLETE.** 4 documents created and committed (`PHASE_AF_SYSTEMATIC_LITERATURE_REVIEW.md`, `PHASE_AF_CONTRIBUTION_BY_CONTRIBUTION_AUDIT.md`, `PHASE_AF_NOVELTY_PROOF_OR_DISPROOF.md`, `PHASE_AF_FINAL_NOVELTY_VERDICT.md`).

### 1.2 Repository Codebase & Test Inventory
- **Backend Code:** Fully functional FastAPI service (`backend/app/main.py`), OR-Tools CVRP solver, Qiskit 2.4.1 QAOA statevector candidate generator, PySpark 4.2.0 preprocessor, adaptive MAB controller, algorithmic VND polisher, and Proposition 1 guardrail.
- **Backend Test Suites:**
  - `backend/tests/`: 6 test files covering optimization, pipelines, QAOA, QGAR, RB-QCD, and Spark preprocessor.
  - `phase_ae_backend_integration/tests/`: 13 passing regression tests verifying universal stop coverage ($R == I$), immutable fleet constraints ($K, C$), Proposition 1 non-degradation, and psutil/tracemalloc resource metrics.
  - Overall existing backend regression test count: 70 passing tests.
- **Frontend Code:** React 19 (`19.2.8`), Vite 8 (`8.3.0`), Leaflet GIS (`1.9.4`), TailwindCSS (`3.4.17`), Recharts. Production build verified clean via `tsc -b && vite build`.
- **Automated Browser Tests:** 10/10 automated Selenium browser verification checks executed with full screenshot logs (`browser_evidence/`).

### 1.3 Deployment Configuration Inventory & Discovered Issues
- **Frontend Deployment:**
  - Production URL: `https://route-iq-frontend-nine.vercel.app/`
  - Vercel config (`vercel.json`): Configured with API rewrite to `https://route-iq-backend.onrender.com/api/:path*` and SPA rewrite to `/index.html`.
- **Backend Deployment:**
  - Production URL: `https://route-iq-backend.onrender.com`
  - Render blueprint (`render.yaml`): Specifies Docker runtime pointing to `./backend/Dockerfile`.
- **CRITICAL DEPLOYMENT ISSUE DISCOVERED (Docker Build Context):**
  - In `backend/Dockerfile` and root `Dockerfile`, the Docker build context executes:
    ```dockerfile
    COPY backend/requirements.txt ./requirements.txt
    RUN pip install --no-cache-dir -r requirements.txt
    COPY backend/ ./
    ```
  - However, in the current evolved architecture, `backend/app/services/optimization/cooperative_solver.py` imports modules from root folders outside `backend/`:
    - `phase_ab_cooperative_optimization_engine`
    - `phase_v_independent_quantum_validation`
    - `phase_u_quantum_bipartition_validation`
  - **Risk:** If built in Docker as currently configured without copying these root modules or configuring `PYTHONPATH`, the containerized backend on Render would crash with `ModuleNotFoundError: No module named 'phase_ab_cooperative_optimization_engine'`.
  - **Mitigation Requirement (Stage 4 & 7):** Ensure root `Dockerfile` and `render.yaml` copy required research modules into the container image or package them into `backend/app/services/optimization/cooperative/`.

### 1.4 Security & Secrets Inventory
- `frontend/.env.production` contains only public URLs (`https://route-iq-backend.onrender.com`).
- `backend/.env.example` contains only placeholder credentials.
- No active `.env` files are tracked in Git.
- `.gitignore` properly excludes `__pycache__`, `*.pyc`, `node_modules`, `*.db`, `dist/`, and local temporary artifacts.

---

## 2. Completed vs Incomplete vs Unverified Tasks

| Task Description | Current Status | Verification State | Assigned Stage |
|---|---|---|---|
| Phase AI architecture comparison and tech stack audit | **COMPLETED** | Verified in Git (`242c3f5`) | Stage 1 |
| Phase AF & AG novelty proofs, literature review, and defense guides | **COMPLETED** | Verified in Git (`7708eee`, `09528f8`) | Stage 1 |
| Review of existing test suites and deployment files | **COMPLETED** | Inspected in Stage 1 | Stage 1 |
| Master Execution Plan (`PHASE_AJ_MASTER_EXECUTION_PLAN.md`) | **IN PROGRESS** | Authoring now | Stage 1 |
| Standard CVRPLIB benchmark evaluation scripts & repeated trials | **INCOMPLETE** | Ready for execution | Stage 2 |
| Component ablation matrix & Spark scalability curve | **INCOMPLETE** | Ready for execution | Stage 2 |
| Complete Journal Manuscript (`ROUTE_IQ_FINAL_JOURNAL_MANUSCRIPT.md`) | **INCOMPLETE** | Ready for drafting | Stage 2 |
| Backend & Frontend regression verification test run | **UNVERIFIED** | Must be re-run cleanly | Stage 3 |
| Production Dockerfile & build context fix for Render | **INCOMPLETE** | Identified in Stage 1 | Stage 4 & 7 |
| Security scan for credentials, tokens, and gitignore audit | **INCOMPLETE** | Ready for Stage 4 | Stage 4 |
| Push verified research branch to GitHub remote | **PENDING GATE** | Requires Gate 1 approval | Stage 5 |
| Vercel frontend deployment inspection and sync | **PENDING GATE** | Requires Gate 2 approval | Stage 6 |
| Render backend deployment inspection and container fix | **PENDING GATE** | Requires Gate 2 approval | Stage 7 |
| Production smoke testing against live URLs | **PENDING GATE** | Requires Gate 3 approval | Stage 8 & 9 |

---

## 3. Ten-Stage Master Roadmap & Strict Approval Gates

```
+----------------------------------------------------------------------------------------------------+
|                                      TEN-STAGE ROADMAP & GATES                                     |
+----------------------------------------------------------------------------------------------------+
|  STAGE 1: Review Existing Work & Master Execution Plan (CURRENT STAGE)                             |
|  - Inventory code, tests, docs, Git branches, and deployment configs.                             |
|  - Identify Docker build context issue and unverified components.                                  |
|  - Output: PHASE_AJ_MASTER_EXECUTION_PLAN.md                                                       |
|                                                                                                    |
|  STAGE 2: Journal Research Readiness & Manuscript Preparation                                      |
|  - Execute CVRPLIB benchmark scripts (Augerat/Uchoa instances).                                    |
|  - Document multi-seed statistical variance (mean ± std dev).                                      |
|  - Execute component ablation (OR-Tools vs OR-Tools+VND vs Coop Engine).                           |
|  - Author complete manuscript: ROUTE_IQ_FINAL_JOURNAL_MANUSCRIPT.md & Readiness Report.            |
|                                                                                                    |
|  STAGE 3: Final Full-Stack Application Audit                                                       |
|  - Run full backend regression suite (all 70 tests).                                               |
|  - Run frontend production build (`npm run build`).                                                |
|  - Re-verify 100% stop coverage, fleet constraints, and resource telemetry.                       |
|  - Output: PHASE_AJ_FINAL_TEST_REPORT.md                                                           |
|                                                                                                    |
|  STAGE 4: Security & Repository Cleanup                                                            |
|  - Scan for API keys, tokens, and credentials.                                                     |
|  - Fix Dockerfile build context so Render container includes all cooperative dependencies.         |
|  - Verify .gitignore and update README.md.                                                         |
|                                                                                                    |
|  🛑 APPROVAL GATE 1: USER APPROVAL FOR GITHUB PUBLICATION                                         |
|  - Stop, present complete audit findings, and request approval to push research branch.           |
|                                                                                                    |
|  STAGE 5: GitHub Publication                                                                       |
|  - Push verified `research/phase-ae-backend-integration` to GitHub origin.                         |
|  - Output: PHASE_AJ_GITHUB_PUBLICATION_REPORT.md                                                   |
|                                                                                                    |
|  🛑 APPROVAL GATE 2: USER APPROVAL FOR DEPLOYMENT TRIGGER                                         |
|  - Stop, review staging/deployment strategy, and obtain approval before affecting production.     |
|                                                                                                    |
|  STAGE 6: Automatic Frontend Deployment (Vercel)                                                    |
|  - Verify Vercel build, environment variables, and rewrite rules.                                  |
|  - Output: PHASE_AJ_VERCEL_DEPLOYMENT_REPORT.md                                                    |
|                                                                                                    |
|  STAGE 7: Automatic Backend Deployment (Render)                                                    |
|  - Deploy updated Docker container with root module packaging.                                     |
|  - Verify health check probe (/health).                                                            |
|  - Output: PHASE_AJ_RENDER_DEPLOYMENT_REPORT.md                                                    |
|                                                                                                    |
|  STAGE 8 & 9: Production Acceptance & Smoke Testing                                               |
|  - Execute live API requests and map verification against https://route-iq-backend.onrender.com.   |
|  - Verify https://route-iq-frontend-nine.vercel.app/ in browser.                                   |
|  - Output: PHASE_AJ_PRODUCTION_ACCEPTANCE_REPORT.md                                                |
|                                                                                                    |
|  STAGE 10: Final Consolidation & Delivery                                                          |
|  - Final presentation to user with all commit hashes, live URLs, and publication assets.           |
+----------------------------------------------------------------------------------------------------+
```

---

## 4. Stage 1 Execution Sign-Off

- **Stage 1 Status:** **COMPLETED.**
- **No changes have been pushed to GitHub.**
- **Protected `main` branch remains untouched at `a8eb849`.**
- **No production deployments have been triggered.**
- **Critical finding logged:** Dockerfile build context dependency packaging must be resolved before backend deployment to prevent container startup failures on Render.
