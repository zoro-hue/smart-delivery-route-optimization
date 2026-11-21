"""
Phase Z: Unified Hybrid Big Data + Quantum Computing Routing Engine (ROUTE/IQ v3).
Integrates:
- Pillar 1: Apache Spark 4.2.0 Spatial Preprocessing & Boundary Decomposition
- Pillar 2: Subspace XY-Mixer QAOA with Adaptive Gating Decision System
- Classical Foundation: OR-Tools / Clarke-Wright + Kernighan-Lin + Algorithmic VND
- Safety Envelope: Proposition 1 Incumbent-Preserving Acceptance Guardrail
"""

import os
import sys
import time
import math
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import pandas as pd

# Path resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from phase_v_independent_quantum_validation.prototypes.algorithmic_vnd import AlgorithmicVND
from phase_u_quantum_bipartition_validation.prototypes.classical_partition_solvers import (
    ClassicalPartitioningSuite
)
from phase_y_breakthrough_engineering.prototypes.advanced_quantum_formulations import (
    AdvancedQuantumFormulations
)

# Optional Spark integration
try:
    from app.services.bigdata_pipeline import ensure_spark_environment
    ensure_spark_environment()
    from pyspark.sql import SparkSession
    import pyspark.sql.functions as F
    HAS_PYSPARK = True
except Exception:
    HAS_PYSPARK = False


class UnifiedHybridRoutingEngine:
    """Production research prototype of the ROUTE/IQ dual-pillar hybrid routing architecture."""

    def __init__(self, use_spark: bool = True):
        self.use_spark = use_spark and HAS_PYSPARK
        self.classical_suite = ClassicalPartitioningSuite()

    # ─── 1. PILLAR 1: BIG DATA PREPROCESSING & BOUNDARY EXTRACTION ───────────

    def decompose_fleet_workload(
        self,
        df_stops: pd.DataFrame,
        depot_coords: Tuple[float, float],
        centroid_a: Tuple[float, float],
        centroid_b: Tuple[float, float],
        boundary_threshold: float = 0.03
    ) -> Dict[str, Any]:
        """
        Decomposes spatial fleet orders into vehicle clusters and identifies micro-boundary customers.
        Uses Apache Spark 4.2.0 if available, falling back to vectorized Pandas.
        """
        t0 = time.perf_counter()
        c_a = np.array(centroid_a)
        c_b = np.array(centroid_b)

        if self.use_spark:
            try:
                spark = SparkSession.builder \
                    .appName("ROUTEIQ_Unified_Decomposition") \
                    .master("local[*]") \
                    .config("spark.ui.enabled", "false") \
                    .getOrCreate()

                sdf = spark.createDataFrame(df_stops)
                sdf_dist = sdf \
                    .withColumn("d_lat_a", F.col("latitude") - F.lit(c_a[0])) \
                    .withColumn("d_lon_a", F.col("longitude") - F.lit(c_a[1])) \
                    .withColumn("dist_a", F.sqrt(F.col("d_lat_a")**2 + F.col("d_lon_a")**2)) \
                    .withColumn("d_lat_b", F.col("latitude") - F.lit(c_b[0])) \
                    .withColumn("d_lon_b", F.col("longitude") - F.lit(c_b[1])) \
                    .withColumn("dist_b", F.sqrt(F.col("d_lat_b")**2 + F.col("d_lon_b")**2)) \
                    .withColumn("diff_ab", F.abs(F.col("dist_a") - F.col("dist_b")))

                boundary_rows = sdf_dist.filter(F.col("diff_ab") < boundary_threshold).limit(16).collect()
                boundary_ids = [r["stop_id"] for r in boundary_rows]
                t_decomp_ms = (time.perf_counter() - t0) * 1000.0
                return {"boundary_ids": boundary_ids, "decomp_time_ms": t_decomp_ms, "engine": "Apache_Spark_4.2.0"}
            except Exception:
                pass

        # Fallback / Fast Vectorized In-Memory
        pts = df_stops[["latitude", "longitude"]].values
        da = np.linalg.norm(pts - c_a, axis=1)
        db = np.linalg.norm(pts - c_b, axis=1)
        diff = np.abs(da - db)
        mask = diff < boundary_threshold
        b_ids = df_stops[mask]["stop_id"].tolist()[:16]
        t_decomp_ms = (time.perf_counter() - t0) * 1000.0
        return {"boundary_ids": b_ids, "decomp_time_ms": t_decomp_ms, "engine": "Pandas_Vectorized"}

    # ─── 2. ADAPTIVE QUANTUM GATING (POLICY E) ───────────────────────────────

    @staticmethod
    def should_invoke_quantum(
        interaction_density: float,
        capacity_slack: float,
        qubo_initial_gap: float,
        gating_threshold: float = 1.65
    ) -> Tuple[bool, float]:
        """
        Learned gating classifier: predicts whether QAOA is likely to discover an improving cut.
        """
        score = 1.8 * interaction_density - 1.2 * capacity_slack + 0.05 * qubo_initial_gap
        invoke = bool(score >= gating_threshold)
        return invoke, round(score, 3)

    # ─── 3. COMPLETE PIPELINE ROUTE OPTIMIZATION ─────────────────────────────

    def optimize_fleet(
        self,
        dist_matrix: np.ndarray,
        demands: np.ndarray,
        cap_a: float,
        cap_b: float,
        c_a: np.ndarray,
        c_b: np.ndarray,
        allow_quantum: bool = True
    ) -> Dict[str, Any]:
        """
        Executes end-to-end optimization pipeline:
        1. Formulates boundary bipartitioning Hamiltonian.
        2. Computes classical baseline solutions (Kernighan-Lin, Multi-Start Local Search).
        3. Evaluates adaptive gating system.
        4. Invocates Subspace XY-Mixer QAOA if gated.
        5. Repairs capacity violations deterministically.
        6. Optimizes complete fleet tours with Algorithmic Variable Neighborhood Descent (VND).
        7. Enforces Proposition 1 Non-Degradation Guardrail.
        """
        t0_total = time.perf_counter()
        N = len(demands)

        # Build Interaction Matrix W and Centroid Biases
        cust_indices = list(range(1, N + 1))
        W = np.zeros((N, N))
        weights = []
        for i in range(N):
            for j in range(i + 1, N):
                d = dist_matrix[i + 1, j + 1]
                w = 5.0 / (d + 0.5)
                W[i, j] = w
                W[j, i] = w
                weights.append(w)

        d_ia = np.linalg.norm(dist_matrix[1:, 0] - 25.0)  # surrogate to centroid
        h_diff = np.zeros(N)
        for i in range(N):
            h_diff[i] = dist_matrix[i + 1, 0] * 0.1

        # QUBO Formulation
        delta_q = cap_a - cap_b
        lambda_c = 2.0
        Q = np.zeros((N, N))
        for i in range(N):
            for j in range(N):
                if i != j:
                    Q[i, j] = -W[i, j] + lambda_c * demands[i] * demands[j]
            Q[i, i] = h_diff[i] - 2.0 * lambda_c * delta_q * demands[i]

        # Stage 1: Classical Solvers
        t0_c = time.perf_counter()
        greedy_res = self.classical_suite.greedy_capacity_constrained(Q, demands, h_diff, cap_a, cap_b)
        mls_res = self.classical_suite.multistart_local_search(Q, demands, h_diff, cap_a, cap_b, restarts=20)
        kl_res = self.classical_suite.kernighan_lin_balanced(Q, demands, h_diff, cap_a, cap_b)
        t_c_ms = (time.perf_counter() - t0_c) * 1000.0

        p_classical = np.array(kl_res["partition"])
        ta_c, tb_c = self._to_tours(p_classical, dist_matrix)
        t0_vnd = time.perf_counter()
        opt_c = AlgorithmicVND.optimize_fleet_routes(ta_c, tb_c, demands, cap_a, cap_b, dist_matrix)
        dist_classical_best = opt_c["total_distance"]
        t_vnd_c_ms = (time.perf_counter() - t0_vnd) * 1000.0

        # Stage 2: Adaptive Gating
        interaction_density = float(np.mean(weights)) if weights else 1.0
        total_demand = float(np.sum(demands))
        capacity_slack = float((cap_a + cap_b - total_demand) / total_demand)
        qubo_initial_gap = float(greedy_res["qubo_cost"] - mls_res["qubo_cost"])

        invoke_q, gate_score = self.should_invoke_quantum(interaction_density, capacity_slack, qubo_initial_gap)
        if not allow_quantum:
            invoke_q = False

        # Stage 3: Quantum Execution (if invoked)
        t_q_ms = 0.0
        q_accepted = False
        dist_final = dist_classical_best
        winning_partition = p_classical
        rejection_reason = "QUANTUM_GATED_OUT" if not invoke_q else "PROPOSITION_1_REJECTED"

        if invoke_q:
            t0_q = time.perf_counter()
            h, J = np.diag(Q), np.copy(Q)
            np.fill_diagonal(J, 0)

            # Subspace XY-Mixer QAOA
            qres = AdvancedQuantumFormulations.simulate_sampling_generic(
                h, J, demands, cap_a, cap_b, shots=512, use_xy_mixer=True, fast_mode=True
            )
            raw_x = qres["best_x"]

            # Classical deterministic capacity repair
            p_repaired = np.array(self.classical_suite.repair_capacity_violations(list(raw_x), demands, cap_a, cap_b, h_diff))
            t_q_ms = (time.perf_counter() - t0_q) * 1000.0

            # Route evaluation via VND
            ta_q, tb_q = self._to_tours(p_repaired, dist_matrix)
            opt_q = AlgorithmicVND.optimize_fleet_routes(ta_q, tb_q, demands, cap_a, cap_b, dist_matrix)
            dist_q = opt_q["total_distance"]

            # Stage 4: Proposition 1 Guardrail
            if dist_q < dist_classical_best - 1e-4:
                q_accepted = True
                dist_final = dist_q
                winning_partition = p_repaired
                rejection_reason = "ACCEPTED_IMPROVEMENT"
            else:
                q_accepted = False
                dist_final = dist_classical_best
                winning_partition = p_classical
                rejection_reason = "SUBOPTIMAL_COST_REJECTED"

        total_time_ms = (time.perf_counter() - t0_total) * 1000.0

        return {
            "num_customers": N,
            "dist_final_km": round(float(dist_final), 2),
            "dist_classical_best_km": round(float(dist_classical_best), 2),
            "quantum_invoked": invoke_q,
            "quantum_accepted": q_accepted,
            "decision_score": gate_score,
            "rejection_reason": rejection_reason,
            "classical_time_ms": round(t_c_ms + t_vnd_c_ms, 2),
            "quantum_time_ms": round(t_q_ms, 2),
            "total_time_ms": round(total_time_ms, 2),
            "winning_partition": list(winning_partition)
        }

    @staticmethod
    def _to_tours(partition: np.ndarray, dist_matrix: np.ndarray) -> Tuple[List[int], List[int]]:
        nodes_a = [i + 1 for i, v in enumerate(partition) if v == 1]
        nodes_b = [i + 1 for i, v in enumerate(partition) if v == 0]

        def nn(nodes):
            if not nodes: return []
            t, curr, rem = [], 0, list(nodes)
            while rem:
                nxt = min(rem, key=lambda k: dist_matrix[curr, k])
                t.append(nxt)
                rem.remove(nxt)
                curr = nxt
            return t
        return nn(nodes_a), nn(nodes_b)

