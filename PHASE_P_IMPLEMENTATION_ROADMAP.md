# ROUTE/IQ — PHASE P: MODULAR IMPLEMENTATION ROADMAP & SSDI SPECIFICATION
**Step-by-Step Engineering Plan for Future Implementation Without Breaking Existing APIs**

---

## 1. Modular Phased Roadmap (P.1 through P.5)

To ensure software stability, each component is specified as an independent, decoupled module with dedicated regression unit tests:

```
┌────────────────────────────────────────────────────────────────────────┐
│ Phase P.1: Classical Bottleneck & Seed Extractor                       │
│ - Module: backend/app/services/optimization/bottleneck_extractor.py    │
│ - Tasks: Planar crossing detector, stagnation monitor, subproblem cut  │
│ - Tests: tests/test_bottleneck_extractor.py                            │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Phase P.2: Warm-Start QAOA Engine with XY Mixers                       │
│ - Module: backend/app/services/optimization/qaoa_cooperative.py        │
│ - Tasks: Permutation initialization, Pauli ATSP, Qiskit Aer statevector│
│ - Tests: tests/test_qaoa_cooperative.py                                │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Phase P.3: Classically-Seeded QIGA Engine                              │
│ - Module: backend/app/services/optimization/qiga_seeded_optimizer.py   │
│ - Tasks: Amplitude bias, dynamic rotation gates, catastrophe operator  │
│ - Tests: tests/test_qiga_seeded_optimizer.py                           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Phase P.4: Adaptive Feedback Controller & QGAR Reconstructor           │
│ - Module: backend/app/services/optimization/hybrid_feedback_controller.py
│ - Tasks: Dispatch decision matrix, multi-fragment stitch, 2-opt polish │
│ - Tests: tests/test_hybrid_feedback_controller.py                      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Phase P.5: Unified Incumbent Manager & API Bridge                      │
│ - Module: backend/app/services/optimization/incumbent_manager.py       │
│ - Tasks: Monotonic non-degradation check, FastAPI route registration   │
│ - Tests: tests/test_cooperative_hybrid_end_to_end.py                   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Detailed Module Specifications

### Module P.1: Bottleneck & Seed Extractor
- **File:** `backend/app/services/optimization/bottleneck_extractor.py`
- **Functions:**
  - `detect_planar_crossings(route, coordinates) -> List[Tuple[int, int]]`
  - `compute_segment_detour_ratio(route, road_matrix, haversine_matrix) -> float`
  - `extract_subproblem(route, start_idx, length=4) -> SubproblemObject`
- **Output:** Standardized subproblem dictionary with pinned boundary nodes.

### Module P.2: Warm-Start QAOA Engine
- **File:** `backend/app/services/optimization/qaoa_cooperative.py`
- **Functions:**
  - `build_atsp_ising_hamiltonian(distance_matrix, entry_node, exit_node)`
  - `create_xy_mixer_circuit(num_qubits, steps=4)`
  - `initialize_permutation_state(circuit, seed_permutation)`
  - `execute_qaoa_aer(circuit, cost_h, mixer_h, p=1, shots=1024) -> QAOResult`
  - `decode_hungarian_permutation(sampled_matrix) -> List[int]`

### Module P.3: Classically-Seeded QIGA Engine
- **File:** `backend/app/services/optimization/qiga_seeded_optimizer.py`
- **Functions:**
  - `initialize_qbit_population_from_seeds(seeds, pop_size=30, bias=0.85)`
  - `apply_quantum_rotation_gates(population, best_individual, angle_lookup)`
  - `apply_catastrophe_operator_if_stagnant(population, entropy_threshold)`
  - `repair_permutation_chromosome(raw_bits) -> ValidTour`

### Module P.4: Adaptive Feedback Controller
- **File:** `backend/app/services/optimization/hybrid_feedback_controller.py`
- **Functions:**
  - `dispatch_subproblem(subproblem, signals, time_budget) -> EngineType`
  - `stitch_fragments_dynamic_programming(fragments, depot) -> CompleteRoute`
  - `apply_cooperative_local_search(stitched_route, road_matrix) -> RefinedRoute`

### Module P.5: Incumbent Manager & API Bridge
- **File:** `backend/app/services/optimization/incumbent_manager.py`
- **Functions:**
  - `audit_route_feasibility(candidate_route, customer_demands, vehicle_capacity)`
  - `enforce_monotonic_incumbent_guardrail(candidate, incumbent) -> CertifiedRoute`
  - `format_fastapi_response(certified_route, telemetry) -> Dict[str, Any]`

---

## 3. The Smallest Scientifically Defensible Implementation (SSDI)

If full implementation resources are constrained, what is the **smallest minimal viable implementation (MVI)** that can definitively test the core scientific hypothesis?

### SSDI Architecture Specification:
1. **Scope:** Focus strictly on \(N = 25\) and \(N = 50\) delivery scales with \(M = 3\) to \(5\) vehicles.
2. **Pillar 1:** Verified single-machine polar sweep partitioning (eliminating cluster setup complexity while retaining identical mathematical logic).
3. **Pillar 2:** QAOA on Qiskit Aer (\(K = 4\), 16 logical qubits) initialized at the classical 2-opt tour using an XY mixer.
4. **Classical Layer:** Google OR-Tools CVRP provides the starting global solution and benchmark.
5. **Incumbent Guardrail:** Deterministic rejection rule ensuring \(\text{Cost}(R_{\text{final}}) \le \text{Cost}(R_{\text{OR-Tools}})\).
6. **Eliminated in SSDI:** Omit QIGA and distributed Spark cluster deployment initially; isolate QAOA vs OR-Tools on bottleneck sub-tours.

**Why SSDI is Scientifically Sufficient:**  
This minimal core directly answers the primary question: *Does quantum-assisted permutation exploration improve upon a classical 2-opt optimal subproblem under fair conditions?*

---

## 4. Non-Negotiable Protection Constraints for Future Coding

1. **Frontend Directory Immutability:** Never modify any file in `frontend/`.
2. **Default API Behavior:** Default solver in `OptimizationRequest` remains `ortools`.
3. **Container Memory Budget:** Memory footprint must stay below 220 MB on cloud nodes without JVM.
4. **Transparent Telemetry:** Always report classical simulator status (`AerSimulator`); never claim QPU execution.

