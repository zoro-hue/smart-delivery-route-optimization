"""
ROUTE/IQ Advanced Neighborhood Search & ALNS Engine.
Implements:
1. Intra-route Asymmetric 2-opt.
2. Inter-route 2-opt* (Tail swap & Cross-reverse).
3. Inter-route Or-opt (Block relocation for lengths 1, 2, 3).
4. Inter-route Cross-Exchange (Block swap for lengths 1-2).
5. Inter-route Relocate & Swap.
6. Deep Variable Neighborhood Descent (VND).
7. Adaptive Large Neighborhood Search (ALNS Ruin-and-Recreate):
   - Shaw Spatial Removal (correlated proximity)
   - Worst-Detour Removal (high marginal cost)
   - Random Removal
   - Regret-2 & Best Insertion
"""

import math
import copy
import random
from typing import List, Tuple, Dict, Any, Optional
import numpy as np


class RouteEvaluator:
    """Fast, memory-efficient route evaluation utilities."""

    @staticmethod
    def tour_length(tour: List[int], dist_matrix: np.ndarray, depot: int = 0) -> float:
        if not tour:
            return 0.0
        d = dist_matrix[depot, tour[0]]
        for i in range(len(tour) - 1):
            d += dist_matrix[tour[i], tour[i + 1]]
        d += dist_matrix[tour[-1], depot]
        return float(d)

    @classmethod
    def fleet_distance(cls, routes: List[List[int]], dist_matrix: np.ndarray, depot: int = 0) -> float:
        return float(sum(cls.tour_length(r, dist_matrix, depot) for r in routes))


class AdvancedNeighborhoodSearch:
    """Production-grade metaheuristic neighborhood operators for CVRP."""

    @classmethod
    def run_2opt(cls, tour: List[int], dist_matrix: np.ndarray, depot: int = 0) -> List[int]:
        """Intra-route 2-opt edge inversion."""
        best_tour = list(tour)
        best_dist = RouteEvaluator.tour_length(best_tour, dist_matrix, depot)
        n = len(best_tour)
        if n < 3:
            return best_tour

        improved = True
        while improved:
            improved = False
            for i in range(n - 1):
                for j in range(i + 1, n):
                    cand = best_tour[:i] + best_tour[i:j + 1][::-1] + best_tour[j + 1:]
                    cand_dist = RouteEvaluator.tour_length(cand, dist_matrix, depot)
                    if cand_dist < best_dist - 1e-4:
                        best_dist = cand_dist
                        best_tour = cand
                        improved = True
                        break
                if improved:
                    break
        return best_tour

    @classmethod
    def run_two_opt_star(
        cls,
        tour_a: List[int],
        tour_b: List[int],
        cap_a: float,
        cap_b: float,
        demands: List[int],
        dist_matrix: np.ndarray,
        depot: int = 0,
    ) -> Tuple[List[int], List[int], bool]:
        """
        Inter-route 2-opt* (tail swap operator):
        Replaces edges (a_i, a_{i+1}) and (b_j, b_{j+1}) by:
        1. Forward tail swap: a[:i] + b[j:] and b[:j] + a[i:]
        2. Cross-reverse swap: a[:i] + rev(b[:j]) and rev(a[i:]) + b[j:]
        """
        best_dist = RouteEvaluator.tour_length(tour_a, dist_matrix, depot) + RouteEvaluator.tour_length(tour_b, dist_matrix, depot)
        best_a = list(tour_a)
        best_b = list(tour_b)

        len_a = len(tour_a)
        len_b = len(tour_b)

        for i in range(len_a + 1):
            for j in range(len_b + 1):
                # Variant 1: Forward tail swap
                cand_a1 = tour_a[:i] + tour_b[j:]
                cand_b1 = tour_b[:j] + tour_a[i:]
                if sum(demands[c] for c in cand_a1) <= cap_a and sum(demands[c] for c in cand_b1) <= cap_b:
                    d1 = RouteEvaluator.tour_length(cand_a1, dist_matrix, depot) + RouteEvaluator.tour_length(cand_b1, dist_matrix, depot)
                    if d1 < best_dist - 1e-4:
                        return cand_a1, cand_b1, True

                # Variant 2: Cross-reverse swap
                cand_a2 = tour_a[:i] + tour_b[:j][::-1]
                cand_b2 = tour_a[i:][::-1] + tour_b[j:]
                if sum(demands[c] for c in cand_a2) <= cap_a and sum(demands[c] for c in cand_b2) <= cap_b:
                    d2 = RouteEvaluator.tour_length(cand_a2, dist_matrix, depot) + RouteEvaluator.tour_length(cand_b2, dist_matrix, depot)
                    if d2 < best_dist - 1e-4:
                        return cand_a2, cand_b2, True

        return best_a, best_b, False

    @classmethod
    def run_or_opt_inter(
        cls,
        tour_a: List[int],
        tour_b: List[int],
        cap_a: float,
        cap_b: float,
        demands: List[int],
        dist_matrix: np.ndarray,
        depot: int = 0,
    ) -> Tuple[List[int], List[int], bool]:
        """
        Inter-route Or-opt: Relocates contiguous chains of 1, 2, or 3 stops between routes.
        """
        best_dist = RouteEvaluator.tour_length(tour_a, dist_matrix, depot) + RouteEvaluator.tour_length(tour_b, dist_matrix, depot)

        # Transfer from A to B
        for seg_len in (1, 2, 3):
            for i in range(len(tour_a) - seg_len + 1):
                seg = tour_a[i:i + seg_len]
                seg_dem = sum(demands[c] for c in seg)
                rem_a = tour_a[:i] + tour_a[i + seg_len:]
                if sum(demands[c] for c in tour_b) + seg_dem <= cap_b:
                    for pos in range(len(tour_b) + 1):
                        cand_b = tour_b[:pos] + seg + tour_b[pos:]
                        d = RouteEvaluator.tour_length(rem_a, dist_matrix, depot) + RouteEvaluator.tour_length(cand_b, dist_matrix, depot)
                        if d < best_dist - 1e-4:
                            return rem_a, cand_b, True
                        if seg_len > 1:
                            cand_b_rev = tour_b[:pos] + seg[::-1] + tour_b[pos:]
                            d_rev = RouteEvaluator.tour_length(rem_a, dist_matrix, depot) + RouteEvaluator.tour_length(cand_b_rev, dist_matrix, depot)
                            if d_rev < best_dist - 1e-4:
                                return rem_a, cand_b_rev, True

        # Transfer from B to A
        for seg_len in (1, 2, 3):
            for j in range(len(tour_b) - seg_len + 1):
                seg = tour_b[j:j + seg_len]
                seg_dem = sum(demands[c] for c in seg)
                rem_b = tour_b[:j] + tour_b[j + seg_len:]
                if sum(demands[c] for c in tour_a) + seg_dem <= cap_a:
                    for pos in range(len(tour_a) + 1):
                        cand_a = tour_a[:pos] + seg + tour_a[pos:]
                        d = RouteEvaluator.tour_length(cand_a, dist_matrix, depot) + RouteEvaluator.tour_length(rem_b, dist_matrix, depot)
                        if d < best_dist - 1e-4:
                            return cand_a, rem_b, True
                        if seg_len > 1:
                            cand_a_rev = tour_a[:pos] + seg[::-1] + tour_a[pos:]
                            d_rev = RouteEvaluator.tour_length(cand_a_rev, dist_matrix, depot) + RouteEvaluator.tour_length(rem_b, dist_matrix, depot)
                            if d_rev < best_dist - 1e-4:
                                return cand_a_rev, rem_b, True

        return tour_a, tour_b, False

    @classmethod
    def run_cross_exchange(
        cls,
        tour_a: List[int],
        tour_b: List[int],
        cap_a: float,
        cap_b: float,
        demands: List[int],
        dist_matrix: np.ndarray,
        depot: int = 0,
    ) -> Tuple[List[int], List[int], bool]:
        """
        Inter-route Cross-Exchange: Swaps a chain of length 1-2 from A with a chain of length 1-2 from B.
        """
        best_dist = RouteEvaluator.tour_length(tour_a, dist_matrix, depot) + RouteEvaluator.tour_length(tour_b, dist_matrix, depot)

        for l_a in (1, 2):
            for l_b in (1, 2):
                for i in range(len(tour_a) - l_a + 1):
                    seg_a = tour_a[i:i + l_a]
                    dem_a = sum(demands[c] for c in seg_a)
                    rem_a = tour_a[:i] + tour_a[i + l_a:]
                    for j in range(len(tour_b) - l_b + 1):
                        seg_b = tour_b[j:j + l_b]
                        dem_b = sum(demands[c] for c in seg_b)
                        rem_b = tour_b[:j] + tour_b[j + l_b:]

                        if (sum(demands[c] for c in rem_a) + dem_b <= cap_a and
                            sum(demands[c] for c in rem_b) + dem_a <= cap_b):
                            cand_a = rem_a[:i] + seg_b + rem_a[i:]
                            cand_b = rem_b[:j] + seg_a + rem_b[j:]
                            d = RouteEvaluator.tour_length(cand_a, dist_matrix, depot) + RouteEvaluator.tour_length(cand_b, dist_matrix, depot)
                            if d < best_dist - 1e-4:
                                return cand_a, cand_b, True

        return tour_a, tour_b, False

    @classmethod
    def deep_vnd(
        cls,
        routes: List[List[int]],
        capacities: List[float],
        demands: List[int],
        dist_matrix: np.ndarray,
        depot: int = 0,
        max_iterations: int = 35,
    ) -> List[List[int]]:
        """
        Hierarchical Variable Neighborhood Descent:
        Neighborhood 1: 2-opt* (cross-route tail swaps)
        Neighborhood 2: Or-opt (cross-route segment relocations)
        Neighborhood 3: Cross-Exchange (cross-route segment swaps)
        Neighborhood 4: Intra-route 2-opt
        """
        cur_routes = [list(r) for r in routes]
        improved = True
        iterations = 0

        while improved and iterations < max_iterations:
            improved = False
            iterations += 1

            for i in range(len(cur_routes)):
                for j in range(i + 1, len(cur_routes)):
                    cap_i = capacities[i] if i < len(capacities) else 100.0
                    cap_j = capacities[j] if j < len(capacities) else 100.0

                    # 1. 2-opt*
                    ra, rb, imp = cls.run_two_opt_star(cur_routes[i], cur_routes[j], cap_i, cap_j, demands, dist_matrix, depot)
                    if imp:
                        cur_routes[i] = cls.run_2opt(ra, dist_matrix, depot)
                        cur_routes[j] = cls.run_2opt(rb, dist_matrix, depot)
                        improved = True
                        break

                    # 2. Or-opt
                    ra, rb, imp = cls.run_or_opt_inter(cur_routes[i], cur_routes[j], cap_i, cap_j, demands, dist_matrix, depot)
                    if imp:
                        cur_routes[i] = cls.run_2opt(ra, dist_matrix, depot)
                        cur_routes[j] = cls.run_2opt(rb, dist_matrix, depot)
                        improved = True
                        break

                    # 3. Cross-Exchange
                    ra, rb, imp = cls.run_cross_exchange(cur_routes[i], cur_routes[j], cap_i, cap_j, demands, dist_matrix, depot)
                    if imp:
                        cur_routes[i] = cls.run_2opt(ra, dist_matrix, depot)
                        cur_routes[j] = cls.run_2opt(rb, dist_matrix, depot)
                        improved = True
                        break

                if improved:
                    break

        for k in range(len(cur_routes)):
            cur_routes[k] = cls.run_2opt(cur_routes[k], dist_matrix, depot)

        return cur_routes

    @classmethod
    def alns_ruin_and_recreate(
        cls,
        incumbent_routes: List[List[int]],
        capacities: List[float],
        demands: List[int],
        dist_matrix: np.ndarray,
        depot: int = 0,
        max_iterations: int = 30,
        seed: int = 42,
    ) -> List[List[int]]:
        """
        Adaptive Large Neighborhood Search (ALNS Ruin-and-Recreate):
        - Shaw spatial proximity removal
        - Worst-detour removal
        - Regret-2 reinsertion
        - Deep VND polishing
        """
        rng = random.Random(seed)
        best_routes = [list(r) for r in incumbent_routes]
        best_dist = RouteEvaluator.fleet_distance(best_routes, dist_matrix, depot)
        cur_routes = copy.deepcopy(best_routes)

        all_customers = [c for r in incumbent_routes for c in r]
        n_cust = len(all_customers)
        if n_cust < 4:
            return best_routes

        for it in range(max_iterations):
            k_rem = min(6, max(2, int(n_cust * 0.25)))

            # Ruin Operator Selection
            if it % 2 == 0:
                # Shaw spatial removal
                seed_c = rng.choice(all_customers)
                sorted_by_d = sorted([c for c in all_customers if c != seed_c], key=lambda c: dist_matrix[seed_c, c])
                removed = [seed_c] + sorted_by_d[:k_rem - 1]
            else:
                # Worst detour removal
                detours = []
                for r in cur_routes:
                    r_cost = RouteEvaluator.tour_length(r, dist_matrix, depot)
                    for node in r:
                        rem_r = [x for x in r if x != node]
                        detour = r_cost - RouteEvaluator.tour_length(rem_r, dist_matrix, depot)
                        detours.append((detour, node))
                detours.sort(key=lambda x: x[0], reverse=True)
                removed = [node for _, node in detours[:k_rem]]

            # Remove from routes
            ruined = [[c for c in r if c not in removed] for r in cur_routes]
            unassigned = list(removed)
            rng.shuffle(unassigned)

            # Recreate Operator: Regret-2 Insertion
            while unassigned:
                best_cust, max_regret, best_v, best_pos = None, -float("inf"), None, None
                for c in unassigned:
                    ins_costs = []
                    for v, r in enumerate(ruined):
                        cap_v = capacities[v] if v < len(capacities) else 100.0
                        if sum(demands[k] for k in r) + demands[c] <= cap_v:
                            c_r = RouteEvaluator.tour_length(r, dist_matrix, depot)
                            best_i_c, best_i_p = float("inf"), 0
                            for pos in range(len(r) + 1):
                                cand = r[:pos] + [c] + r[pos:]
                                del_c = RouteEvaluator.tour_length(cand, dist_matrix, depot) - c_r
                                if del_c < best_i_c:
                                    best_i_c, best_i_p = del_c, pos
                            ins_costs.append((best_i_c, v, best_i_p))

                    if not ins_costs:
                        continue
                    ins_costs.sort(key=lambda x: x[0])
                    regret = ins_costs[1][0] - ins_costs[0][0] if len(ins_costs) > 1 else ins_costs[0][0] * 2.0
                    if regret > max_regret:
                        max_regret, best_cust, best_v, best_pos = regret, c, ins_costs[0][1], ins_costs[0][2]

                if best_cust is not None:
                    ruined[best_v].insert(best_pos, best_cust)
                    unassigned.remove(best_cust)
                else:
                    for c in list(unassigned):
                        min_v = min(range(len(ruined)), key=lambda idx: sum(demands[k] for k in ruined[idx]))
                        ruined[min_v].append(c)
                        unassigned.remove(c)

            # Deep VND Polish
            polished = cls.deep_vnd(ruined, capacities, demands, dist_matrix, depot)
            pol_dist = RouteEvaluator.fleet_distance(polished, dist_matrix, depot)

            if pol_dist < best_dist - 1e-4:
                best_dist = pol_dist
                best_routes = copy.deepcopy(polished)
                cur_routes = copy.deepcopy(polished)
            elif pol_dist < best_dist * 1.03:
                cur_routes = copy.deepcopy(polished)

        return best_routes
