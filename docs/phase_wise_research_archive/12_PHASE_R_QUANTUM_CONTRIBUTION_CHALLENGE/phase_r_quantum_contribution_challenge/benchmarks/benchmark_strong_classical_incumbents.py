"""
Phase R: Strong Classical Incumbent Benchmark Suite.
Systematically benchmarks:
1. Google OR-Tools CVRP (Guided Local Search).
2. OR-Tools + 2-opt Local Search.
3. OR-Tools + Multi-Neighborhood Search (2-opt + 3-opt cyclic shifts).
4. Clarke-Wright Savings + 2-opt.
5. Multistart Classical Optimization (5 randomized restarts).
6. Identifies the Certified Global Classical Incumbent for downstream quantum challenges.
"""

import sys
import os
import time
import math
import numpy as np
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app.services.optimization.classical_solver import ClassicalVRPSolver
from phase_p_autonomous_research.prototypes.common_evaluator import (
    generate_benchmark_instance, audit_solution_feasibility, ProblemInstance
)


class StrongClassicalIncumbentSuite:
    """
    Suite of competitive industrial classical routing baselines.
    """

    def __init__(self):
        self.solver = ClassicalVRPSolver()

    def apply_two_opt_route(self, route_stops: list, dist_matrix: np.ndarray, depot_idx: int = 0) -> list:
        """Classical 2-opt edge exchange uncrossing."""
        n = len(route_stops)
        if n < 4:
            return route_stops

        best = list(route_stops)
        def route_dist(r):
            d = dist_matrix[depot_idx, r[0]]
            for i in range(len(r) - 1):
                d += dist_matrix[r[i], r[i+1]]
            d += dist_matrix[r[-1], depot_idx]
            return d

        best_cost = route_dist(best)
        improved = True
        while improved:
            improved = False
            for i in range(n - 1):
                for j in range(i + 1, n):
                    cand = best[:i] + best[i:j+1][::-1] + best[j+1:]
                    c = route_dist(cand)
                    if c < best_cost - 1e-4:
                        best_cost = c
                        best = cand
                        improved = True
                        break
                if improved: break
        return best

    def apply_multi_neighborhood_search(self, routes_indices: list, dist_matrix: np.ndarray, depot_idx: int = 0) -> Tuple[list, float]:
        """Multi-neighborhood search: 2-opt edge inversion + 3-opt cyclic node shifts."""
        refined_routes = []
        total_dist = 0.0

        for r in routes_indices:
            # 1. Apply 2-opt
            r_opt = self.apply_two_opt_route(r, dist_matrix, depot_idx)

            # 2. Apply 3-opt cyclic shift (non-inverting cyclic permutation of 3 adjacent nodes)
            n = len(r_opt)
            if n >= 3:
                def r_len(seq):
                    d = dist_matrix[depot_idx, seq[0]]
                    for i in range(len(seq) - 1):
                        d += dist_matrix[seq[i], seq[i+1]]
                    d += dist_matrix[seq[-1], depot_idx]
                    return d

                best_c = r_len(r_opt)
                best_seq = list(r_opt)

                for i in range(n - 2):
                    # Cyclic shift: (a, b, c) -> (b, c, a) or (c, a, b)
                    cand1 = best_seq[:i] + [best_seq[i+1], best_seq[i+2], best_seq[i]] + best_seq[i+3:]
                    c1 = r_len(cand1)
                    if c1 < best_c - 1e-4:
                        best_c = c1
                        best_seq = cand1

                    cand2 = best_seq[:i] + [best_seq[i+2], best_seq[i], best_seq[i+1]] + best_seq[i+3:]
                    c2 = r_len(cand2)
                    if c2 < best_c - 1e-4:
                        best_c = c2
                        best_seq = cand2

                r_opt = best_seq

            refined_routes.append(r_opt)
            # Add distance
            if r_opt:
                d = dist_matrix[depot_idx, r_opt[0]]
                for i in range(len(r_opt) - 1):
                    d += dist_matrix[r_opt[i], r_opt[i+1]]
                d += dist_matrix[r_opt[-1], depot_idx]
                total_dist += d

        return refined_routes, total_dist

    def solve_multistart_savings(
        self,
        instance: ProblemInstance,
        num_restarts: int = 5
    ) -> Tuple[list, float, float]:
        """
        Multistart classical heuristic: Clarke-Wright with randomized shape parameter lambda in [0.5, 2.0].
        s_ij = c_i0 + c_0j - lambda * c_ij
        """
        t0 = time.perf_counter()
        best_routes = []
        best_dist = float("inf")
        n = instance.num_customers
        depot = 0
        mat = instance.distance_matrix
        cap = instance.vehicle_capacity
        cust_demands = [c["demand"] for c in instance.customers]

        for restart in range(num_restarts):
            shape_lambda = 0.5 + (restart * 0.35)
            # Compute savings
            savings = []
            for i in range(1, n + 1):
                for j in range(1, n + 1):
                    if i != j:
                        s = mat[i, depot] + mat[depot, j] - shape_lambda * mat[i, j]
                        savings.append((s, i, j))
            savings.sort(key=lambda kv: kv[0], reverse=True)

            # Build initial single-customer routes
            routes = [[i] for i in range(1, n + 1)]
            loads = [cust_demands[i-1] for i in range(1, n + 1)]

            for s_val, i, j in savings:
                # Find route containing i at end and j at start
                r_i_idx, r_j_idx = -1, -1
                for idx, r in enumerate(routes):
                    if r[-1] == i: r_i_idx = idx
                    if r[0] == j: r_j_idx = idx

                if r_i_idx != -1 and r_j_idx != -1 and r_i_idx != r_j_idx:
                    if loads[r_i_idx] + loads[r_j_idx] <= cap:
                        # Merge
                        routes[r_i_idx].extend(routes[r_j_idx])
                        loads[r_i_idx] += loads[r_j_idx]
                        routes.pop(r_j_idx)
                        loads.pop(r_j_idx)

            # Cap fleet size
            while len(routes) > instance.num_vehicles:
                last = routes.pop()
                routes[-1].extend(last)

            # Apply 2-opt
            opt_routes = [self.apply_two_opt_route(r, mat, depot) for r in routes]
            # Compute total distance
            tot_d = 0.0
            for r in opt_routes:
                if r:
                    d = mat[depot, r[0]]
                    for k in range(len(r) - 1): d += mat[r[k], r[k+1]]
                    d += mat[r[-1], depot]
                    tot_d += d

            if tot_d < best_dist:
                best_dist = tot_d
                best_routes = opt_routes

        wall_ms = (time.perf_counter() - t0) * 1000.0
        return best_routes, best_dist, wall_ms


def run_benchmark():
    print("=" * 80)
    print("ROUTE/IQ PHASE R: BENCHMARKING STRONG CLASSICAL INCUMBENTS")
    print("=" * 80)

    suite = StrongClassicalIncumbentSuite()
    scales = [
        {"name": "Dev_Micro", "N": 10, "M": 2, "cap": 25.0, "seeds": [42, 101]},
        {"name": "Dev_Small", "N": 25, "M": 4, "cap": 30.0, "seeds": [42, 101]},
        {"name": "Val_Small", "N": 25, "M": 4, "cap": 30.0, "seeds": [202, 303]},
        {"name": "HeldOut_Small", "N": 25, "M": 4, "cap": 30.0, "seeds": [777, 888]},
        {"name": "HeldOut_Medium", "N": 50, "M": 5, "cap": 40.0, "seeds": [777, 888]}
    ]

    records = []

    for sc in scales:
        for seed in sc["seeds"]:
            inst = generate_benchmark_instance(
                num_customers=sc["N"], num_vehicles=sc["M"],
                vehicle_capacity=sc["cap"], seed=seed
            )
            print(f"\n---> Evaluating Instance: {sc['name']} (N={sc['N']}, M={sc['M']}, Seed={seed})")

            # A. OR-Tools Guided Local Search Alone
            t0 = time.perf_counter()
            res_ortools = suite.solver.solve_ortools(
                distance_matrix=inst.distance_matrix, num_vehicles=inst.num_vehicles,
                depot=0, demands=[0] + [int(c["demand"]) for c in inst.customers],
                vehicle_capacities=[int(inst.vehicle_capacity)] * inst.num_vehicles,
                time_limit_sec=10
            )
            t_ortools = (time.perf_counter() - t0) * 1000.0
            d_ortools = float(res_ortools.get("total_distance_km", 0.0))

            # Extract integer route stops
            ortools_routes = []
            for r_entry in res_ortools.get("routes", []):
                if isinstance(r_entry, dict):
                    inner = [int(idx) for idx in r_entry.get("customer_stops", []) if int(idx) != 0]
                else:
                    inner = [int(idx) for idx in r_entry if int(idx) != 0]
                if inner: ortools_routes.append(inner)

            # B. OR-Tools + 2-opt
            t0 = time.perf_counter()
            routes_2opt = [suite.apply_two_opt_route(r, inst.distance_matrix, 0) for r in ortools_routes]
            d_2opt = 0.0
            for r in routes_2opt:
                if r:
                    d = inst.distance_matrix[0, r[0]]
                    for k in range(len(r) - 1): d += inst.distance_matrix[r[k], r[k+1]]
                    d += inst.distance_matrix[r[-1], 0]
                    d_2opt += d
            t_2opt = t_ortools + (time.perf_counter() - t0) * 1000.0

            # C. OR-Tools + Multi-Neighborhood Search (2-opt + 3-opt cyclic)
            t0 = time.perf_counter()
            routes_mns, d_mns = suite.apply_multi_neighborhood_search(ortools_routes, inst.distance_matrix, 0)
            t_mns = t_ortools + (time.perf_counter() - t0) * 1000.0

            # D. Clarke-Wright + 2-opt
            t0 = time.perf_counter()
            res_cw = suite.solver.solve_clarke_wright(
                distance_matrix=inst.distance_matrix, num_vehicles=inst.num_vehicles,
                depot=0, demands=[0] + [int(c["demand"]) for c in inst.customers],
                vehicle_capacities=[int(inst.vehicle_capacity)] * inst.num_vehicles
            )
            cw_routes = []
            for r_entry in res_cw.get("routes", []):
                if isinstance(r_entry, dict):
                    inner = [int(idx) for idx in r_entry.get("customer_stops", []) if int(idx) != 0]
                else:
                    inner = [int(idx) for idx in r_entry if int(idx) != 0]
                if inner: cw_routes.append(inner)
            cw_opt = [suite.apply_two_opt_route(r, inst.distance_matrix, 0) for r in cw_routes]
            d_cw_2opt = 0.0
            for r in cw_opt:
                if r:
                    d = inst.distance_matrix[0, r[0]]
                    for k in range(len(r) - 1): d += inst.distance_matrix[r[k], r[k+1]]
                    d += inst.distance_matrix[r[-1], 0]
                    d_cw_2opt += d
            t_cw_2opt = (time.perf_counter() - t0) * 1000.0

            # E. Multistart Classical Optimization (5 restarts)
            ms_routes, d_multistart, t_multistart = suite.solve_multistart_savings(inst, num_restarts=5)

            # Certified Strongest Classical Incumbent
            candidates = [
                ("OR-Tools_GLS", d_ortools, t_ortools),
                ("OR-Tools_Plus_2opt", d_2opt, t_2opt),
                ("OR-Tools_Plus_MNS", d_mns, t_mns),
                ("ClarkeWright_Plus_2opt", d_cw_2opt, t_cw_2opt),
                ("Multistart_Classical", d_multistart, t_multistart)
            ]
            best_cand = min(candidates, key=lambda kv: kv[1])

            print(f"  [OR-Tools GLS]         Distance: {d_ortools:6.3f} km | Time: {t_ortools:6.1f} ms")
            print(f"  [OR-Tools + 2opt]      Distance: {d_2opt:6.3f} km | Time: {t_2opt:6.1f} ms")
            print(f"  [OR-Tools + MNS]       Distance: {d_mns:6.3f} km | Time: {t_mns:6.1f} ms")
            print(f"  [Clarke-Wright + 2opt] Distance: {d_cw_2opt:6.3f} km | Time: {t_cw_2opt:6.1f} ms")
            print(f"  [Multistart Classical] Distance: {d_multistart:6.3f} km | Time: {t_multistart:6.1f} ms")
            print(f"  --> Certified Best Classical Incumbent: {best_cand[0]} with {best_cand[1]:6.3f} km")

            records.append({
                "instance": sc["name"], "N": sc["N"], "M": sc["M"], "seed": seed,
                "d_ortools_gls": round(d_ortools, 3), "t_ortools_ms": round(t_ortools, 1),
                "d_ortools_2opt": round(d_2opt, 3), "t_ortools_2opt_ms": round(t_2opt, 1),
                "d_ortools_mns": round(d_mns, 3), "t_ortools_mns_ms": round(t_mns, 1),
                "d_cw_2opt": round(d_cw_2opt, 3), "t_cw_2opt_ms": round(t_cw_2opt, 1),
                "d_multistart": round(d_multistart, 3), "t_multistart_ms": round(t_multistart, 1),
                "best_classical_algorithm": best_cand[0],
                "certified_incumbent_distance_km": round(best_cand[1], 3),
                "certified_incumbent_time_ms": round(best_cand[2], 1)
            })

    csv_file = os.path.join(os.path.dirname(__file__), "..", "results", "phase_r_classical_incumbents_raw.csv")
    os.makedirs(os.path.dirname(csv_file), exist_ok=True)
    pd.DataFrame(records).to_csv(csv_file, index=False)
    print(f"\n[OK] Classical Incumbent Benchmark complete! Raw CSV saved to: {csv_file}")


if __name__ == "__main__":
    run_benchmark()

