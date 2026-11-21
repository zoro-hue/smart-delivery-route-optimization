# ROUTE/IQ: High-Density Prompt-Ready Quick Context
**Project:** ROUTE/IQ — Smart Delivery Route Optimization (UROP, SRM University-AP)  
**Supervisor:** Prof. Vishnu Prasad Verma | **Students:** J. Jayanth, B. Kaivalya, P. Shyam Sai  
**Key URLs:** Frontend: `route-iq-frontend-nine.vercel.app` | Backend: `route-iq-backend.onrender.com`  
**Git Active Branch:** `research/next-generation-cooperative-engine` (HEAD `93e8771`) | `main` (`08a4538`)

---

## Quick Architecture Summary
1. **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Leaflet. Independent GeoJSON polylines for 11 algorithms.
2. **Backend:** FastAPI, Python 3.11, SQLite WAL job state, single-thread async worker queue, Render 512 MB RAM ceiling.
3. **Spatial Engine:** NYC 5-borough graph (54,128 nodes, 134,814 edges) via precomputed SciPy CSR sparse matrix (`road_matrix_csr.npz`, 280 MB boot RAM) + `cKDTree` coordinate snapping.
4. **Cooperative Engine:** 5-stage cooperation:
   - Initial Incumbent: OR-Tools / Clarke-Wright Savings.
   - Spatial Decomposition: Spark polar coordinate sweep with boundary buffer.
   - Hyper-Heuristic: Multi-Armed Bandit (UCB1) adaptive controller.
   - Neighborhood Search: ALNS (Shaw removal, Worst removal, Regret-3 insertion) + VND (2-opt, relocate, exchange).
   - Quantum Subproblems: Simulated gate-based QAOA with parity-preserving XY-mixers via Qiskit Aer (classical CPU).
   - Safety Invariant: **Proposition 1 Monotonic Feasibility Guardrail** ($\text{Cost}(S) \le \text{Cost}(S_{\text{incumbent}})$).
5. **30-Instance Supremacy Benchmark:** 12 Wins, 18 Ties, 0 Losses vs OR-Tools (+0.61% avg improvement, 100% feasible, Wilcoxon $p = 0.00049$).
