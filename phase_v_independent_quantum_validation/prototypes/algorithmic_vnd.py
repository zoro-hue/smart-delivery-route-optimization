"""
Algorithmic Variable Neighborhood Descent (VND) for Vehicle Routing & Partitioning.
Executes real intra-route 2-opt, inter-route customer Relocate, and inter-route customer Swap.
Does NOT rely on synthetic scalar multipliers.
"""

import copy
import numpy as np
from typing import List, Tuple, Dict, Any


class AlgorithmicVND:
    """Deterministic Variable Neighborhood Descent for 2-vehicle delivery routing."""

    @staticmethod
    def compute_tour_length(tour: List[int], dist_matrix: np.ndarray, depot_idx: int = 0) -> float:
        """Computes distance of tour: depot -> tour nodes -> depot."""
        if not tour:
            return 0.0
        d = dist_matrix[depot_idx, tour[0]]
        for i in range(len(tour) - 1):
            d += dist_matrix[tour[i], tour[i + 1]]
        d += dist_matrix[tour[-1], depot_idx]
        return float(d)

    @classmethod
    def run_2opt(cls, tour: List[int], dist_matrix: np.ndarray, depot_idx: int = 0) -> List[int]:
        """Intra-route 2-opt edge inversion."""
        best_tour = list(tour)
        best_dist = cls.compute_tour_length(best_tour, dist_matrix, depot_idx)
        n = len(best_tour)
        if n < 3:
            return best_tour

        improved = True
        while improved:
            improved = False
            for i in range(n - 1):
                for j in range(i + 1, n):
                    # Invert segment from i to j
                    new_tour = best_tour[:i] + best_tour[i:j + 1][::-1] + best_tour[j + 1:]
                    new_dist = cls.compute_tour_length(new_tour, dist_matrix, depot_idx)
                    if new_dist < best_dist - 1e-4:
                        best_dist = new_dist
                        best_tour = new_tour
                        improved = True
                        break
                if improved:
                    break
        return best_tour

    @classmethod
    def run_relocate(
        cls,
        tour_a: List[int],
        tour_b: List[int],
        demands: np.ndarray,
        cap_a: float,
        cap_b: float,
        dist_matrix: np.ndarray,
        depot_idx: int = 0
    ) -> Tuple[List[int], List[int], bool]:
        """Inter-route relocate: shifts one node from one tour to the other if capacity permits and cost reduces."""
        best_dist = cls.compute_tour_length(tour_a, dist_matrix, depot_idx) + cls.compute_tour_length(tour_b, dist_matrix, depot_idx)
        best_a = list(tour_a)
        best_b = list(tour_b)
        improved = False

        # Try A -> B
        for i, node in enumerate(tour_a):
            node_dem = demands[node - 1] if node > 0 else 0
            cur_b_load = sum(demands[k - 1] for k in tour_b if k > 0)
            if cur_b_load + node_dem <= cap_b:
                cand_a = tour_a[:i] + tour_a[i + 1:]
                # Try all insertion positions in B
                for pos in range(len(tour_b) + 1):
                    cand_b = tour_b[:pos] + [node] + tour_b[pos:]
                    new_dist = cls.compute_tour_length(cand_a, dist_matrix, depot_idx) + cls.compute_tour_length(cand_b, dist_matrix, depot_idx)
                    if new_dist < best_dist - 1e-4:
                        best_dist = new_dist
                        best_a = cand_a
                        best_b = cand_b
                        improved = True
                        return best_a, best_b, True

        # Try B -> A
        for j, node in enumerate(tour_b):
            node_dem = demands[node - 1] if node > 0 else 0
            cur_a_load = sum(demands[k - 1] for k in tour_a if k > 0)
            if cur_a_load + node_dem <= cap_a:
                cand_b = tour_b[:j] + tour_b[j + 1:]
                for pos in range(len(tour_a) + 1):
                    cand_a = tour_a[:pos] + [node] + tour_a[pos:]
                    new_dist = cls.compute_tour_length(cand_a, dist_matrix, depot_idx) + cls.compute_tour_length(cand_b, dist_matrix, depot_idx)
                    if new_dist < best_dist - 1e-4:
                        best_dist = new_dist
                        best_a = cand_a
                        best_b = cand_b
                        improved = True
                        return best_a, best_b, True

        return best_a, best_b, False

    @classmethod
    def run_swap(
        cls,
        tour_a: List[int],
        tour_b: List[int],
        demands: np.ndarray,
        cap_a: float,
        cap_b: float,
        dist_matrix: np.ndarray,
        depot_idx: int = 0
    ) -> Tuple[List[int], List[int], bool]:
        """Inter-route swap: exchanges one node from A with one node from B."""
        best_dist = cls.compute_tour_length(tour_a, dist_matrix, depot_idx) + cls.compute_tour_length(tour_b, dist_matrix, depot_idx)
        best_a = list(tour_a)
        best_b = list(tour_b)

        for i, node_a in enumerate(tour_a):
            dem_a = demands[node_a - 1] if node_a > 0 else 0
            for j, node_b in enumerate(tour_b):
                dem_b = demands[node_b - 1] if node_b > 0 else 0
                load_a = sum(demands[k - 1] for k in tour_a if k > 0) - dem_a + dem_b
                load_b = sum(demands[k - 1] for k in tour_b if k > 0) - dem_b + dem_a
                if load_a <= cap_a and load_b <= cap_b:
                    cand_a = list(tour_a)
                    cand_b = list(tour_b)
                    cand_a[i] = node_b
                    cand_b[j] = node_a
                    new_dist = cls.compute_tour_length(cand_a, dist_matrix, depot_idx) + cls.compute_tour_length(cand_b, dist_matrix, depot_idx)
                    if new_dist < best_dist - 1e-4:
                        best_a = cand_a
                        best_b = cand_b
                        return best_a, best_b, True

        return best_a, best_b, False

    @classmethod
    def optimize_fleet_routes(
        cls,
        tour_a: List[int],
        tour_b: List[int],
        demands: np.ndarray,
        cap_a: float,
        cap_b: float,
        dist_matrix: np.ndarray,
        depot_idx: int = 0,
        max_iter: int = 50
    ) -> Dict[str, Any]:
        """Executes full Variable Neighborhood Descent (2-opt -> Relocate -> Swap) until local optimality."""
        cur_a = cls.run_2opt(tour_a, dist_matrix, depot_idx)
        cur_b = cls.run_2opt(tour_b, dist_matrix, depot_idx)

        improved = True
        iterations = 0
        while improved and iterations < max_iter:
            improved = False
            iterations += 1

            # Neighborhood 1: Relocate
            cand_a, cand_b, rel_imp = cls.run_relocate(cur_a, cur_b, demands, cap_a, cap_b, dist_matrix, depot_idx)
            if rel_imp:
                cur_a = cls.run_2opt(cand_a, dist_matrix, depot_idx)
                cur_b = cls.run_2opt(cand_b, dist_matrix, depot_idx)
                improved = True
                continue

            # Neighborhood 2: Swap
            cand_a, cand_b, swap_imp = cls.run_swap(cur_a, cur_b, demands, cap_a, cap_b, dist_matrix, depot_idx)
            if swap_imp:
                cur_a = cls.run_2opt(cand_a, dist_matrix, depot_idx)
                cur_b = cls.run_2opt(cand_b, dist_matrix, depot_idx)
                improved = True
                continue

        final_dist = cls.compute_tour_length(cur_a, dist_matrix, depot_idx) + cls.compute_tour_length(cur_b, dist_matrix, depot_idx)
        return {
            "tour_a": cur_a,
            "tour_b": cur_b,
            "total_distance": round(final_dist, 4),
            "iterations": iterations
        }
