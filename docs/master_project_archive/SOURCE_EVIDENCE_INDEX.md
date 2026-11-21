# ROUTE/IQ: Source Code Traceability & Evidence Verification Index
**Audit Standard:** Line-by-Line Codebase Traceability to Literature & Claims `[VERIFIED]`  
**Active Commit Reference:** `93e8771` on `research/next-generation-cooperative-engine`

---

## 1. Algorithmic Evidence Mapping Matrix

| Claim / Algorithmic Concept | File Path in Repository | Exact Function / Class | Literature Citation Key | Verification Status |
|---|---|---|---|---|
| **ALNS Ruin & Recreate Engine** | `backend/app/core/nextgen_cooperative_engine.py` | `NextGenCooperativeEngine.run_optimization()` | Pisinger & Ropke (2007) | `[VERIFIED]` |
| **Shaw Relatedness Removal** | `backend/app/core/nextgen_cooperative_engine.py` | `_shaw_removal()` | Shaw (1998) | `[VERIFIED]` |
| **Worst-Cost Removal** | `backend/app/core/nextgen_cooperative_engine.py` | `_worst_removal()` | Ropke & Pisinger (2006) | `[VERIFIED]` |
| **Regret-3 Opportunity Insertion** | `backend/app/core/nextgen_cooperative_engine.py` | `_regret_insertion(regret_k=3)` | Ropke & Pisinger (2006) | `[VERIFIED]` |
| **Proposition 1 Guardrail** | `backend/app/core/nextgen_cooperative_engine.py` | Line ~320 (`if cand_cost < incumbent_cost:`) | Talbi (2009) [TA09] | `[VERIFIED]` |
| **Multi-Armed Bandit (UCB1)** | `backend/app/core/adaptive_controller.py` | `AdaptiveCooperativeController.select_arm()` | Auer et al. (2002) [AC02] | `[VERIFIED]` |
| **QAOA with XY-Mixers** | `backend/app/core/qaoa_solver.py` | `build_xy_mixer_circuit()` | Hadfield et al. (2019) [HA19] | `[VERIFIED]` |
| **PySpark Polar Sweep** | `backend/app/core/spark_preprocessor.py` | `SparkWorkloadOrganizer.partition_workload()` | Gillett & Miller (1974) [GM74] | `[VERIFIED]` |
| **Boundary Buffer Heuristic** | `backend/app/core/spark_preprocessor.py` | `identify_boundary_customers()` | ROUTE/IQ Innovation | `[VERIFIED]` |
| **BPR Congestion Formula** | `backend/app/services/road_network.py` | `RoadNetworkGraph.get_travel_time_bpr()` | Bureau of Public Roads (1964) | `[VERIFIED]` |
| **cKDTree Spatial Snapping** | `backend/app/services/road_network.py` | `RoadNetworkGraph.snap_to_nearest_node()` | Bentley (1975) | `[VERIFIED]` |
| **CSR Matrix Caching** | `backend/app/services/road_network.py` | `load_csr_matrices()` | SciPy Sparse Format | `[VERIFIED]` |
| **Google OR-Tools Baseline** | `backend/app/core/ortools_solver.py` | `solve_cvrp_ortools()` | Google Developers (2024) | `[VERIFIED]` |
| **Clarke-Wright Savings** | `backend/app/core/clarkewright_solver.py` | `solve_clarke_wright()` | Clarke & Wright (1964) [CW64] | `[VERIFIED]` |
| **2-opt Local Search** | `backend/app/core/two_opt.py` | `two_opt_route()` | Croes (1958) [CR58] | `[VERIFIED]` |
| **Variable Neighborhood Descent** | `backend/app/core/vnd_solver.py` | `solve_vnd()` | Hansen & Mladenović (2001) [HM01] | `[VERIFIED]` |
| **Tabu Search** | `backend/app/core/tabu_search.py` | `solve_tabu_search()` | Glover (1986) [GL86] | `[VERIFIED]` |
