"""
ROUTE/IQ Advanced Neighborhood Search & Next-Generation ALNS Engine.
Implements:
1. Intra-route Asymmetric 2-opt.
2. Inter-route 2-opt* (Tail swap & Cross-reverse).
3. Inter-route Or-opt (Block relocation for lengths 1, 2, 3).
4. Inter-route Cross-Exchange (Block swap for lengths 1-2).
5. Inter-route Relocate & Pairwise Swap.
6. 3-Route Cyclic Ejection Chains.
7. Deep Variable Neighborhood Descent (Hierarchical VND).
8. Adaptive Large Neighborhood Search (ALNS Ruin-and-Recreate) with MAB:
   - Destroy 1: Multi-Attribute Shaw Relatedness Removal (distance, demand, route, angle)
   - Destroy 2: Worst-Detour Removal (high marginal cost)
   - Destroy 3: Route-Segment Destruction (contiguous chain erase)
   - Destroy 4: Dynamic Boundary Customer Destruction (adjacent route boundary)
   - Destroy 5: Random Removal (entropy injection)
   - Repair 1: Regret-3 Insertion with Capacity Feasibility
   - Repair 2: Regret-2 Insertion with Capacity Feasibility
   - Repair 3: Cheapest Feasible Insertion
9. Multi-Solution Elite Population Pool with Diversity Management & Anti-Stagnation Perturbation.
"""

import math
import copy
import random
import time
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
        iterations = 0
        while improved and iterations < 50:
            improved = False
            iterations += 1
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
    def run_relocate_inter(
        cls,
        tour_a: List[int],
        tour_b: List[int],
        cap_a: float,
        cap_b: float,
        demands: List[int],
        dist_matrix: np.ndarray,
        depot: int = 0,
    ) -> Tuple[List[int], List[int], bool]:
        """Single customer relocation between two routes."""
        best_dist = RouteEvaluator.tour_length(tour_a, dist_matrix, depot) + RouteEvaluator.tour_length(tour_b, dist_matrix, depot)
        
        # Move node from A to B
        for i, node in enumerate(tour_a):
            if sum(demands[c] for c in tour_b) + demands[node] <= cap_b:
                rem_a = tour_a[:i] + tour_a[i + 1:]
                for pos in range(len(tour_b) + 1):
                    cand_b = tour_b[:pos] + [node] + tour_b[pos:]
                    d = RouteEvaluator.tour_length(rem_a, dist_matrix, depot) + RouteEvaluator.tour_length(cand_b, dist_matrix, depot)
                    if d < best_dist - 1e-4:
                        return rem_a, cand_b, True

        # Move node from B to A
        for j, node in enumerate(tour_b):
            if sum(demands[c] for c in tour_a) + demands[node] <= cap_a:
                rem_b = tour_b[:j] + tour_b[j + 1:]
                for pos in range(len(tour_a) + 1):
                    cand_a = tour_a[:pos] + [node] + tour_a[pos:]
                    d = RouteEvaluator.tour_length(cand_a, dist_matrix, depot) + RouteEvaluator.tour_length(rem_b, dist_matrix, depot)
                    if d < best_dist - 1e-4:
                        return cand_a, rem_b, True

        return tour_a, tour_b, False

    @classmethod
    def run_swap_inter(
        cls,
        tour_a: List[int],
        tour_b: List[int],
        cap_a: float,
        cap_b: float,
        demands: List[int],
        dist_matrix: np.ndarray,
        depot: int = 0,
    ) -> Tuple[List[int], List[int], bool]:
        """Pairwise single customer swap between two routes."""
        best_dist = RouteEvaluator.tour_length(tour_a, dist_matrix, depot) + RouteEvaluator.tour_length(tour_b, dist_matrix, depot)
        load_a = sum(demands[c] for c in tour_a)
        load_b = sum(demands[c] for c in tour_b)

        for i, na in enumerate(tour_a):
            for j, nb in enumerate(tour_b):
                if load_a - demands[na] + demands[nb] <= cap_a and load_b - demands[nb] + demands[na] <= cap_b:
                    cand_a = list(tour_a)
                    cand_b = list(tour_b)
                    cand_a[i] = nb
                    cand_b[j] = na
                    d = RouteEvaluator.tour_length(cand_a, dist_matrix, depot) + RouteEvaluator.tour_length(cand_b, dist_matrix, depot)
                    if d < best_dist - 1e-4:
                        return cand_a, cand_b, True

        return tour_a, tour_b, False

    @classmethod
    def run_ejection_chain_3(
        cls,
        routes: List[List[int]],
        capacities: List[float],
        demands: List[int],
        dist_matrix: np.ndarray,
        depot: int = 0,
    ) -> Tuple[List[List[int]], bool]:
        """
        Fast targeted 3-route cyclic ejection chain: A -> B -> C -> A.
        Identifies boundary nodes with high marginal detour and tests cyclic reassignment.
        """
        K = len(routes)
        if K < 3:
            return routes, False

        loads = [sum(demands[c] for c in r) for r in routes]

        # Pre-select top candidate node with highest detour from each non-empty route
        best_cand_per_route = {}
        for r_idx, r in enumerate(routes):
            if len(r) >= 2:
                r_cost = RouteEvaluator.tour_length(r, dist_matrix, depot)
                best_node = None
                best_sav = -float("inf")
                for node in r:
                    rem = [x for x in r if x != node]
                    sav = r_cost - RouteEvaluator.tour_length(rem, dist_matrix, depot)
                    if sav > best_sav:
                        best_sav = sav
                        best_node = node
                if best_node is not None:
                    best_cand_per_route[r_idx] = best_node

        eligible = list(best_cand_per_route.keys())
        if len(eligible) < 3:
            return routes, False

        # Test cyclic triples
        for i_a in range(len(eligible)):
            a = eligible[i_a]
            na = best_cand_per_route[a]
            da = demands[na]
            for i_b in range(len(eligible)):
                if i_b == i_a:
                    continue
                b = eligible[i_b]
                nb = best_cand_per_route[b]
                db = demands[nb]
                for i_c in range(len(eligible)):
                    if i_c == i_a or i_c == i_b:
                        continue
                    c = eligible[i_c]
                    nc = best_cand_per_route[c]
                    dc = demands[nc]

                    # Capacity check
                    if (loads[a] - da + dc <= capacities[a] and
                        loads[b] - db + da <= capacities[b] and
                        loads[c] - dc + db <= capacities[c]):

                        sub_old = (RouteEvaluator.tour_length(routes[a], dist_matrix, depot) +
                                   RouteEvaluator.tour_length(routes[b], dist_matrix, depot) +
                                   RouteEvaluator.tour_length(routes[c], dist_matrix, depot))

                        new_ra = [x for x in routes[a] if x != na] + [nc]
                        new_rb = [x for x in routes[b] if x != nb] + [na]
                        new_rc = [x for x in routes[c] if x != nc] + [nb]

                        opt_ra = cls.run_2opt(new_ra, dist_matrix, depot)
                        opt_rb = cls.run_2opt(new_rb, dist_matrix, depot)
                        opt_rc = cls.run_2opt(new_rc, dist_matrix, depot)

                        sub_new = (RouteEvaluator.tour_length(opt_ra, dist_matrix, depot) +
                                   RouteEvaluator.tour_length(opt_rb, dist_matrix, depot) +
                                   RouteEvaluator.tour_length(opt_rc, dist_matrix, depot))

                        if sub_new < sub_old - 1e-4:
                            new_routes = [list(r) for r in routes]
                            new_routes[a] = opt_ra
                            new_routes[b] = opt_rb
                            new_routes[c] = opt_rc
                            return new_routes, True

        return routes, False

    @classmethod
    def deep_vnd(
        cls,
        routes: List[List[int]],
        capacities: List[float],
        demands: List[int],
        dist_matrix: np.ndarray,
        depot: int = 0,
        max_iterations: int = 40,
    ) -> List[List[int]]:
        """
        Hierarchical Variable Neighborhood Descent:
        Neighborhood 1: 2-opt* (cross-route tail swaps)
        Neighborhood 2: Or-opt inter (cross-route segment relocations lengths 1-3)
        Neighborhood 3: Cross-Exchange (cross-route segment swaps lengths 1-2)
        Neighborhood 4: Inter-route Relocate & Swap
        Neighborhood 5: 3-Route Cyclic Ejection Chains
        Neighborhood 6: Intra-route 2-opt
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

                    # 2. Or-opt inter
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

                    # 4. Relocate & Swap
                    ra, rb, imp = cls.run_relocate_inter(cur_routes[i], cur_routes[j], cap_i, cap_j, demands, dist_matrix, depot)
                    if imp:
                        cur_routes[i] = cls.run_2opt(ra, dist_matrix, depot)
                        cur_routes[j] = cls.run_2opt(rb, dist_matrix, depot)
                        improved = True
                        break

                    ra, rb, imp = cls.run_swap_inter(cur_routes[i], cur_routes[j], cap_i, cap_j, demands, dist_matrix, depot)
                    if imp:
                        cur_routes[i] = cls.run_2opt(ra, dist_matrix, depot)
                        cur_routes[j] = cls.run_2opt(rb, dist_matrix, depot)
                        improved = True
                        break

                if improved:
                    break

            # 5. Ejection chain across 3 routes
            if not improved and len(cur_routes) >= 3:
                cur_routes, imp_ej = cls.run_ejection_chain_3(cur_routes, capacities, demands, dist_matrix, depot)
                if imp_ej:
                    improved = True

        for k in range(len(cur_routes)):
            cur_routes[k] = cls.run_2opt(cur_routes[k], dist_matrix, depot)

        return cur_routes

    # ── Ruin (Destroy) Operators ────────────────────────────────────

    @classmethod
    def destroy_shaw_relatedness(
        cls,
        routes: List[List[int]],
        dist_matrix: np.ndarray,
        demands: List[int],
        locations: Optional[List[Tuple[float, float]]],
        k_rem: int,
        depot: int,
        rng: random.Random,
        p_randomness: float = 3.0,
    ) -> List[int]:
        """
        Multi-attribute Shaw relatedness removal:
        Combines geographic road distance, customer demand similarity,
        route co-occurrence, and polar angular similarity.
        """
        all_custs = [c for r in routes for c in r]
        if len(all_custs) <= k_rem:
            return list(all_custs)

        node_to_route = {c: r_idx for r_idx, r in enumerate(routes) for c in r}
        max_dist = float(np.max(dist_matrix)) if np.max(dist_matrix) > 0 else 1.0
        max_dem = max(demands) if max(demands) > 0 else 1.0

        depot_loc = locations[depot] if locations and len(locations) > depot else (0.0, 0.0)
        angles = {}
        if locations and len(locations) >= len(dist_matrix):
            for c in all_custs:
                angles[c] = math.atan2(locations[c][0] - depot_loc[0], locations[c][1] - depot_loc[1])

        # Pick seed customer
        seed_c = rng.choice(all_custs)
        removed = [seed_c]

        while len(removed) < k_rem:
            # Pick reference customer from already removed set
            ref_c = rng.choice(removed)
            candidates = [c for c in all_custs if c not in removed]

            def relatedness(cand: int) -> float:
                d_term = dist_matrix[ref_c, cand] / max_dist
                q_term = abs(demands[ref_c] - demands[cand]) / max_dem
                r_term = 0.0 if node_to_route[ref_c] == node_to_route[cand] else 0.5
                ang_term = 0.0
                if angles:
                    d_ang = abs(angles[ref_c] - angles[cand])
                    ang_term = min(d_ang, 2 * math.pi - d_ang) / math.pi
                return 0.45 * d_term + 0.20 * q_term + 0.20 * r_term + 0.15 * ang_term

            candidates.sort(key=relatedness)
            idx = int((rng.random() ** p_randomness) * len(candidates))
            idx = min(idx, len(candidates) - 1)
            removed.append(candidates[idx])

        return removed

    @classmethod
    def destroy_worst_detour(
        cls,
        routes: List[List[int]],
        dist_matrix: np.ndarray,
        k_rem: int,
        depot: int,
        rng: random.Random,
        p_randomness: float = 3.0,
    ) -> List[int]:
        """Worst-detour removal: removes customers with highest marginal detour savings."""
        detours = []
        for r in routes:
            r_cost = RouteEvaluator.tour_length(r, dist_matrix, depot)
            for node in r:
                rem_r = [x for x in r if x != node]
                detour = r_cost - RouteEvaluator.tour_length(rem_r, dist_matrix, depot)
                detours.append((detour, node))

        detours.sort(key=lambda x: x[0], reverse=True)
        if len(detours) <= k_rem:
            return [n for _, n in detours]

        removed = []
        rem_set = set()
        while len(removed) < k_rem and detours:
            idx = int((rng.random() ** p_randomness) * len(detours))
            idx = min(idx, len(detours) - 1)
            node = detours.pop(idx)[1]
            if node not in rem_set:
                rem_set.add(node)
                removed.append(node)

        return removed

    @classmethod
    def destroy_route_segment(
        cls,
        routes: List[List[int]],
        dist_matrix: np.ndarray,
        k_rem: int,
        rng: random.Random,
    ) -> List[int]:
        """Route-segment destruction: erases contiguous customer chains to enable relocation."""
        non_empty = [r for r in routes if len(r) >= 2]
        if not non_empty:
            all_custs = [c for r in routes for c in r]
            return rng.sample(all_custs, min(k_rem, len(all_custs)))

        target_r = rng.choice(non_empty)
        seg_len = min(len(target_r), max(2, k_rem // 2))
        start_idx = rng.randint(0, len(target_r) - seg_len)
        removed = list(target_r[start_idx:start_idx + seg_len])

        # Find second adjacent route
        other_routes = [r for r in non_empty if r is not target_r]
        if other_routes and len(removed) < k_rem:
            second_r = rng.choice(other_routes)
            rem_needed = k_rem - len(removed)
            seg2_len = min(len(second_r), rem_needed)
            start2 = rng.randint(0, len(second_r) - seg2_len)
            removed.extend(second_r[start2:start2 + seg2_len])

        return removed

    @classmethod
    def destroy_boundary_customers(
        cls,
        routes: List[List[int]],
        dist_matrix: np.ndarray,
        locations: Optional[List[Tuple[float, float]]],
        k_rem: int,
        depot: int,
        rng: random.Random,
    ) -> List[int]:
        """Boundary customer destruction: targets customers situated near the partition border of two routes."""
        active_routes = [r for r in routes if len(r) >= 2]
        if len(active_routes) < 2:
            all_c = [c for r in routes for c in r]
            return rng.sample(all_c, min(k_rem, len(all_c)))

        # Find pair of routes with closest centroids
        centroids = []
        for r in active_routes:
            if locations and len(locations) >= len(dist_matrix):
                lat = float(np.mean([locations[c][0] for c in r]))
                lon = float(np.mean([locations[c][1] for c in r]))
                centroids.append((lat, lon))
            else:
                dist_dep = float(np.mean([dist_matrix[depot, c] for c in r]))
                centroids.append((dist_dep, 0.0))

        min_pair = (0, 1)
        min_c_dist = float("inf")
        for i in range(len(active_routes)):
            for j in range(i + 1, len(active_routes)):
                cd = math.hypot(centroids[i][0] - centroids[j][0], centroids[i][1] - centroids[j][1])
                if cd < min_c_dist:
                    min_c_dist = cd
                    min_pair = (i, j)

        ra, rb = active_routes[min_pair[0]], active_routes[min_pair[1]]
        ca, cb = centroids[min_pair[0]], centroids[min_pair[1]]

        def border_score(c, own_c, other_c):
            if locations and len(locations) >= len(dist_matrix):
                loc = locations[c]
                return math.hypot(loc[0] - other_c[0], loc[1] - other_c[1]) - math.hypot(loc[0] - own_c[0], loc[1] - own_c[1])
            return dist_matrix[depot, c]

        border_a = sorted(ra, key=lambda c: border_score(c, ca, cb))
        border_b = sorted(rb, key=lambda c: border_score(c, cb, ca))

        half_k = max(1, k_rem // 2)
        removed = border_a[:half_k] + border_b[:k_rem - half_k]
        return removed

    @classmethod
    def destroy_random(cls, routes: List[List[int]], k_rem: int, rng: random.Random) -> List[int]:
        """Uniform random customer removal for entropy injection."""
        all_custs = [c for r in routes for c in r]
        return rng.sample(all_custs, min(k_rem, len(all_custs)))

    # ── Recreate (Repair) Operators ─────────────────────────────────

    @classmethod
    def repair_regret_k(
        cls,
        ruined_routes: List[List[int]],
        unassigned: List[int],
        capacities: List[float],
        demands: List[int],
        dist_matrix: np.ndarray,
        depot: int,
        k_regret: int = 2,
    ) -> List[List[int]]:
        """
        Regret-k (k=2 or k=3) insertion repair heuristic.
        Computes the regret of not inserting customer into their best vehicle.
        """
        routes = [list(r) for r in ruined_routes]
        unassigned_pool = list(unassigned)

        while unassigned_pool:
            best_cust = None
            max_regret = -float("inf")
            best_v = None
            best_pos = None

            for c in unassigned_pool:
                ins_costs = []
                for v, r in enumerate(routes):
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
                if k_regret >= 3 and len(ins_costs) >= 3:
                    regret = (ins_costs[1][0] - ins_costs[0][0]) + (ins_costs[2][0] - ins_costs[0][0])
                elif len(ins_costs) >= 2:
                    regret = ins_costs[1][0] - ins_costs[0][0]
                else:
                    regret = ins_costs[0][0] * 2.0

                if regret > max_regret:
                    max_regret = regret
                    best_cust = c
                    best_v = ins_costs[0][1]
                    best_pos = ins_costs[0][2]

            if best_cust is not None:
                routes[best_v].insert(best_pos, best_cust)
                unassigned_pool.remove(best_cust)
            else:
                # If tight capacity prevents standard feasible insertion, place into vehicle with minimal load
                for c in list(unassigned_pool):
                    min_v = min(range(len(routes)), key=lambda idx: sum(demands[k] for k in routes[idx]))
                    routes[min_v].append(c)
                    unassigned_pool.remove(c)

        return routes

    @classmethod
    def repair_cheapest_insertion(
        cls,
        ruined_routes: List[List[int]],
        unassigned: List[int],
        capacities: List[float],
        demands: List[int],
        dist_matrix: np.ndarray,
        depot: int,
    ) -> List[List[int]]:
        """Greedy cheapest feasible insertion repair."""
        routes = [list(r) for r in ruined_routes]
        unassigned_pool = list(unassigned)

        while unassigned_pool:
            best_cust, min_del, best_v, best_pos = None, float("inf"), None, None
            for c in unassigned_pool:
                for v, r in enumerate(routes):
                    cap_v = capacities[v] if v < len(capacities) else 100.0
                    if sum(demands[k] for k in r) + demands[c] <= cap_v:
                        c_r = RouteEvaluator.tour_length(r, dist_matrix, depot)
                        for pos in range(len(r) + 1):
                            cand = r[:pos] + [c] + r[pos:]
                            del_c = RouteEvaluator.tour_length(cand, dist_matrix, depot) - c_r
                            if del_c < min_del:
                                min_del, best_cust, best_v, best_pos = del_c, c, v, pos

            if best_cust is not None:
                routes[best_v].insert(best_pos, best_cust)
                unassigned_pool.remove(best_cust)
            else:
                for c in list(unassigned_pool):
                    min_v = min(range(len(routes)), key=lambda idx: sum(demands[k] for k in routes[idx]))
                    routes[min_v].append(c)
                    unassigned_pool.remove(c)

        return routes

    # ── Next-Generation Adaptive Large Neighborhood Search Engine ─────

    @classmethod
    def alns_ruin_and_recreate(
        cls,
        incumbent_routes: List[List[int]],
        capacities: List[float],
        demands: List[int],
        dist_matrix: np.ndarray,
        depot: int = 0,
        locations: Optional[List[Tuple[float, float]]] = None,
        max_iterations: int = 35,
        seed: int = 42,
    ) -> List[List[int]]:
        """
        Next-Generation Multi-Armed Bandit ALNS Engine:
        - 5 Ruin Operators: Shaw Relatedness, Worst Detour, Route Segment, Boundary Customer, Random.
        - 3 Recreate Operators: Regret-3, Regret-2, Cheapest Feasible.
        - Multi-Armed Bandit adaptive weights with exponential smoothing.
        - Elite population pool with diversity checks.
        - Stagnation detection and anti-trapping perturbation.
        """
        rng = random.Random(seed)
        best_routes = [list(r) for r in incumbent_routes]
        best_dist = RouteEvaluator.fleet_distance(best_routes, dist_matrix, depot)
        cur_routes = copy.deepcopy(best_routes)

        all_customers = [c for r in incumbent_routes for c in r]
        n_cust = len(all_customers)
        if n_cust < 4:
            return best_routes

        # Multi-Armed Bandit Operator Tracking
        destroy_ops = ["shaw", "worst", "segment", "boundary", "random"]
        repair_ops = ["regret_3", "regret_2", "cheapest"]

        destroy_weights = {op: 1.0 for op in destroy_ops}
        repair_weights = {op: 1.0 for op in repair_ops}
        destroy_scores = {op: 0.0 for op in destroy_ops}
        repair_scores = {op: 0.0 for op in repair_ops}
        destroy_attempts = {op: 1 for op in destroy_ops}
        repair_attempts = {op: 1 for op in repair_ops}

        # Elite Population Pool (Size 4)
        elite_pool = [copy.deepcopy(best_routes)]
        stagnation_counter = 0

        # Rewards
        SIGMA_1 = 5.0  # New global best
        SIGMA_2 = 3.0  # Better than current
        SIGMA_3 = 1.0  # Accepted non-degrading move
        DECAY_LAMBDA = 0.80

        def select_op(weights_dict: Dict[str, float]) -> str:
            total_w = sum(weights_dict.values())
            r_val = rng.uniform(0.0, total_w)
            cum = 0.0
            for op, w in weights_dict.items():
                cum += w
                if r_val <= cum:
                    return op
            return list(weights_dict.keys())[0]

        t_alns_start = time.perf_counter()
        max_alns_sec = 0.8  # Bounded latency to ensure sub-2.0s responsive execution

        for it in range(max_iterations):
            if time.perf_counter() - t_alns_start > max_alns_sec:
                break
            # Dynamic removal fraction: 15% - 35% of stops
            k_fraction = rng.uniform(0.15, 0.35)
            k_rem = min(max(2, int(n_cust * k_fraction)), min(8, n_cust - 1))

            # Select operators via MAB
            d_op = select_op(destroy_weights)
            r_op = select_op(repair_weights)

            destroy_attempts[d_op] += 1
            repair_attempts[r_op] += 1

            # 1. Execute Destroy
            if d_op == "shaw":
                removed = cls.destroy_shaw_relatedness(cur_routes, dist_matrix, demands, locations, k_rem, depot, rng)
            elif d_op == "worst":
                removed = cls.destroy_worst_detour(cur_routes, dist_matrix, k_rem, depot, rng)
            elif d_op == "segment":
                removed = cls.destroy_route_segment(cur_routes, dist_matrix, k_rem, rng)
            elif d_op == "boundary":
                removed = cls.destroy_boundary_customers(cur_routes, dist_matrix, locations, k_rem, depot, rng)
            else:
                removed = cls.destroy_random(cur_routes, k_rem, rng)

            ruined = [[c for c in r if c not in removed] for r in cur_routes]
            unassigned = list(removed)
            rng.shuffle(unassigned)

            # 2. Execute Repair
            if r_op == "regret_3":
                repaired = cls.repair_regret_k(ruined, unassigned, capacities, demands, dist_matrix, depot, k_regret=3)
            elif r_op == "regret_2":
                repaired = cls.repair_regret_k(ruined, unassigned, capacities, demands, dist_matrix, depot, k_regret=2)
            else:
                repaired = cls.repair_cheapest_insertion(ruined, unassigned, capacities, demands, dist_matrix, depot)

            # 3. Fast polish with intra-route 2-opt
            polished = [cls.run_2opt(r, dist_matrix, depot) for r in repaired]
            pol_dist = RouteEvaluator.fleet_distance(polished, dist_matrix, depot)

            # If strictly improving or highly promising, apply hierarchical deep VND polish
            if pol_dist < best_dist - 1e-4:
                polished = cls.deep_vnd(polished, capacities, demands, dist_matrix, depot, max_iterations=6)
                pol_dist = RouteEvaluator.fleet_distance(polished, dist_matrix, depot)

            # 4. Evaluation & Adaptive Reward Updates
            reward = 0.0
            if pol_dist < best_dist - 1e-4:
                # Discovered new global optimum
                reward = SIGMA_1
                best_dist = pol_dist
                best_routes = copy.deepcopy(polished)
                cur_routes = copy.deepcopy(polished)
                stagnation_counter = 0

                # Insert into elite pool if distinct
                if not any(cls._routes_equal(polished, ep) for ep in elite_pool):
                    if len(elite_pool) >= 4:
                        elite_pool.pop(0)
                    elite_pool.append(copy.deepcopy(polished))

            elif pol_dist < RouteEvaluator.fleet_distance(cur_routes, dist_matrix, depot) - 1e-4:
                # Improved current solution
                reward = SIGMA_2
                cur_routes = copy.deepcopy(polished)
                stagnation_counter = 0
            elif pol_dist < best_dist * 1.025:
                # Accepted non-degrading exploration move
                reward = SIGMA_3
                cur_routes = copy.deepcopy(polished)
                stagnation_counter += 1
            else:
                stagnation_counter += 1

            destroy_scores[d_op] += reward
            repair_scores[r_op] += reward

            # Update MAB weights periodically (every 5 iterations)
            if (it + 1) % 5 == 0:
                for op in destroy_ops:
                    perf = destroy_scores[op] / max(1, destroy_attempts[op])
                    destroy_weights[op] = DECAY_LAMBDA * destroy_weights[op] + (1 - DECAY_LAMBDA) * (1.0 + perf)
                    destroy_scores[op] = 0.0
                    destroy_attempts[op] = 1

                for op in repair_ops:
                    perf = repair_scores[op] / max(1, repair_attempts[op])
                    repair_weights[op] = DECAY_LAMBDA * repair_weights[op] + (1 - DECAY_LAMBDA) * (1.0 + perf)
                    repair_scores[op] = 0.0
                    repair_attempts[op] = 1

            # 5. Anti-Stagnation Perturbation
            if stagnation_counter >= 5 and elite_pool:
                stagnation_counter = 0
                # Restart from a random elite solution and apply heavy ruin
                cur_routes = copy.deepcopy(rng.choice(elite_pool))
                k_perturb = min(max(3, int(n_cust * 0.40)), n_cust - 1)
                p_removed = cls.destroy_random(cur_routes, k_perturb, rng)
                p_ruined = [[c for c in r if c not in p_removed] for r in cur_routes]
                cur_routes = cls.repair_regret_k(p_ruined, p_removed, capacities, demands, dist_matrix, depot, k_regret=2)

        return best_routes

    @staticmethod
    def _routes_equal(r1: List[List[int]], r2: List[List[int]]) -> bool:
        if len(r1) != len(r2):
            return False
        return all(a == b for a, b in zip(r1, r2))
