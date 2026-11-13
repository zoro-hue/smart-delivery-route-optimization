"""
Phase S: Industrial-Strength Asymmetric Directed Classical Solvers Suite.
Implements:
1. Directed 2-opt with explicit asymmetric reversal-cost recalculation.
2. Directed Relocate (1-0 Node Insertion).
3. Directed Node Swap (1-1 Node Exchange).
4. Or-opt (Segment Relocation of lengths 2 and 3 without reversal).
5. Variable Neighborhood Descent (VND).
6. Variable Neighborhood Search (VNS) / Iterated Local Search (ILS).
7. Exact Permutation Enumeration (K! Ground-Truth Evaluator).
"""

import time
import math
import itertools
from typing import Dict, Any, List, Tuple
import numpy as np


class AsymmetricDirectedLocalSearchSuite:
    """
    Complete algorithmic suite for asymmetric traveling salesperson and vehicle routing subproblems.
    All cost calculations strictly evaluate directed arc weights d(u, v).
    """

    @staticmethod
    def compute_directed_cost(
        perm: List[int],
        cost_matrix: np.ndarray,
        sub_locs: List[int],
        entry_idx: int,
        exit_idx: int
    ) -> float:
        """Computes true directed travel distance for a permutation sequence."""
        c = cost_matrix[entry_idx, sub_locs[perm[0]]]
        for i in range(len(perm) - 1):
            c += cost_matrix[sub_locs[perm[i]], sub_locs[perm[i + 1]]]
        c += cost_matrix[sub_locs[perm[-1]], exit_idx]
        return float(c)

    def exact_enumeration(
        self,
        cost_matrix: np.ndarray,
        sub_locs: List[int],
        entry_idx: int,
        exit_idx: int
    ) -> Dict[str, Any]:
        """Exhaustive ground truth evaluator for K <= 8."""
        t0 = time.perf_counter()
        K = len(sub_locs)
        all_perms = list(itertools.permutations(range(K)))
        best_perm = list(all_perms[0])
        best_cost = self.compute_directed_cost(best_perm, cost_matrix, sub_locs, entry_idx, exit_idx)

        for p in all_perms[1:]:
            c = self.compute_directed_cost(p, cost_matrix, sub_locs, entry_idx, exit_idx)
            if c < best_cost:
                best_cost = c
                best_perm = list(p)

        t_ms = (time.perf_counter() - t0) * 1000.0
        return {
            "best_perm": best_perm,
            "cost_km": round(best_cost, 4),
            "time_ms": round(t_ms, 4),
            "evaluations": len(all_perms)
        }

    def directed_2opt(
        self,
        seed_perm: List[int],
        cost_matrix: np.ndarray,
        sub_locs: List[int],
        entry_idx: int,
        exit_idx: int
    ) -> Dict[str, Any]:
        """Directed 2-opt edge exchange with full asymmetric path recalculation."""
        t0 = time.perf_counter()
        K = len(seed_perm)
        cur = list(seed_perm)
        cur_cost = self.compute_directed_cost(cur, cost_matrix, sub_locs, entry_idx, exit_idx)
        evals = 1
        improved = True

        while improved:
            improved = False
            for i in range(K - 1):
                for j in range(i + 1, K):
                    cand = cur[:i] + cur[i:j + 1][::-1] + cur[j + 1:]
                    c = self.compute_directed_cost(cand, cost_matrix, sub_locs, entry_idx, exit_idx)
                    evals += 1
                    if c < cur_cost - 1e-4:
                        cur_cost = c
                        cur = cand
                        improved = True
                        break
                if improved:
                    break

        t_ms = (time.perf_counter() - t0) * 1000.0
        return {"best_perm": cur, "cost_km": round(cur_cost, 4), "time_ms": round(t_ms, 4), "evaluations": evals}

    def relocate_search(
        self,
        seed_perm: List[int],
        cost_matrix: np.ndarray,
        sub_locs: List[int],
        entry_idx: int,
        exit_idx: int
    ) -> Dict[str, Any]:
        """Directed Relocate (1-0 insertion): Shifts node i to position j without path inversion."""
        t0 = time.perf_counter()
        K = len(seed_perm)
        cur = list(seed_perm)
        cur_cost = self.compute_directed_cost(cur, cost_matrix, sub_locs, entry_idx, exit_idx)
        evals = 1
        improved = True

        while improved:
            improved = False
            for i in range(K):
                for j in range(K):
                    if i != j:
                        cand = [x for k, x in enumerate(cur) if k != i]
                        cand.insert(j, cur[i])
                        c = self.compute_directed_cost(cand, cost_matrix, sub_locs, entry_idx, exit_idx)
                        evals += 1
                        if c < cur_cost - 1e-4:
                            cur_cost = c
                            cur = cand
                            improved = True
                            break
                if improved:
                    break

        t_ms = (time.perf_counter() - t0) * 1000.0
        return {"best_perm": cur, "cost_km": round(cur_cost, 4), "time_ms": round(t_ms, 4), "evaluations": evals}

    def swap_search(
        self,
        seed_perm: List[int],
        cost_matrix: np.ndarray,
        sub_locs: List[int],
        entry_idx: int,
        exit_idx: int
    ) -> Dict[str, Any]:
        """Directed Swap (1-1 exchange): Exchanges positions of node i and node j."""
        t0 = time.perf_counter()
        K = len(seed_perm)
        cur = list(seed_perm)
        cur_cost = self.compute_directed_cost(cur, cost_matrix, sub_locs, entry_idx, exit_idx)
        evals = 1
        improved = True

        while improved:
            improved = False
            for i in range(K - 1):
                for j in range(i + 1, K):
                    cand = list(cur)
                    cand[i], cand[j] = cand[j], cand[i]
                    c = self.compute_directed_cost(cand, cost_matrix, sub_locs, entry_idx, exit_idx)
                    evals += 1
                    if c < cur_cost - 1e-4:
                        cur_cost = c
                        cur = cand
                        improved = True
                        break
                if improved:
                    break

        t_ms = (time.perf_counter() - t0) * 1000.0
        return {"best_perm": cur, "cost_km": round(cur_cost, 4), "time_ms": round(t_ms, 4), "evaluations": evals}

    def or_opt_search(
        self,
        seed_perm: List[int],
        cost_matrix: np.ndarray,
        sub_locs: List[int],
        entry_idx: int,
        exit_idx: int,
        block_len: int = 2
    ) -> Dict[str, Any]:
        """Or-opt: Relocates consecutive block of length block_len without internal inversion."""
        t0 = time.perf_counter()
        K = len(seed_perm)
        if K <= block_len:
            return {"best_perm": list(seed_perm), "cost_km": self.compute_directed_cost(seed_perm, cost_matrix, sub_locs, entry_idx, exit_idx), "time_ms": 0.0, "evaluations": 1}

        cur = list(seed_perm)
        cur_cost = self.compute_directed_cost(cur, cost_matrix, sub_locs, entry_idx, exit_idx)
        evals = 1
        improved = True

        while improved:
            improved = False
            for i in range(K - block_len + 1):
                block = cur[i:i + block_len]
                rem = cur[:i] + cur[i + block_len:]
                for j in range(len(rem) + 1):
                    cand = rem[:j] + block + rem[j:]
                    c = self.compute_directed_cost(cand, cost_matrix, sub_locs, entry_idx, exit_idx)
                    evals += 1
                    if c < cur_cost - 1e-4:
                        cur_cost = c
                        cur = cand
                        improved = True
                        break
                if improved:
                    break

        t_ms = (time.perf_counter() - t0) * 1000.0
        return {"best_perm": cur, "cost_km": round(cur_cost, 4), "time_ms": round(t_ms, 4), "evaluations": evals}

    def variable_neighborhood_descent(
        self,
        seed_perm: List[int],
        cost_matrix: np.ndarray,
        sub_locs: List[int],
        entry_idx: int,
        exit_idx: int
    ) -> Dict[str, Any]:
        """
        VND: Successively explores Relocate -> Swap -> Or-opt (len=2) -> Directed 2-opt.
        Restarts to N1 upon any improvement.
        """
        t0 = time.perf_counter()
        K = len(seed_perm)
        cur = list(seed_perm)
        cur_cost = self.compute_directed_cost(cur, cost_matrix, sub_locs, entry_idx, exit_idx)
        total_evals = 1

        k = 1
        while k <= 4:
            improved = False

            if k == 1:
                # Relocate
                for i in range(K):
                    for j in range(K):
                        if i != j:
                            cand = [x for idx, x in enumerate(cur) if idx != i]
                            cand.insert(j, cur[i])
                            c = self.compute_directed_cost(cand, cost_matrix, sub_locs, entry_idx, exit_idx)
                            total_evals += 1
                            if c < cur_cost - 1e-4:
                                cur_cost = c
                                cur = cand
                                improved = True
                                break
                    if improved: break

            elif k == 2:
                # Swap
                for i in range(K - 1):
                    for j in range(i + 1, K):
                        cand = list(cur)
                        cand[i], cand[j] = cand[j], cand[i]
                        c = self.compute_directed_cost(cand, cost_matrix, sub_locs, entry_idx, exit_idx)
                        total_evals += 1
                        if c < cur_cost - 1e-4:
                            cur_cost = c
                            cur = cand
                            improved = True
                            break
                    if improved: break

            elif k == 3:
                # Or-opt len 2
                if K > 2:
                    for i in range(K - 1):
                        block = cur[i:i + 2]
                        rem = cur[:i] + cur[i + 2:]
                        for j in range(len(rem) + 1):
                            cand = rem[:j] + block + rem[j:]
                            c = self.compute_directed_cost(cand, cost_matrix, sub_locs, entry_idx, exit_idx)
                            total_evals += 1
                            if c < cur_cost - 1e-4:
                                cur_cost = c
                                cur = cand
                                improved = True
                                break
                        if improved: break

            elif k == 4:
                # Directed 2-opt
                for i in range(K - 1):
                    for j in range(i + 1, K):
                        cand = cur[:i] + cur[i:j + 1][::-1] + cur[j + 1:]
                        c = self.compute_directed_cost(cand, cost_matrix, sub_locs, entry_idx, exit_idx)
                        total_evals += 1
                        if c < cur_cost - 1e-4:
                            cur_cost = c
                            cur = cand
                            improved = True
                            break
                    if improved: break

            if improved:
                k = 1  # Restart to first neighborhood
            else:
                k += 1  # Proceed to next neighborhood

        t_ms = (time.perf_counter() - t0) * 1000.0
        return {
            "best_perm": cur,
            "cost_km": round(cur_cost, 4),
            "time_ms": round(t_ms, 4),
            "evaluations": total_evals
        }

    def variable_neighborhood_search(
        self,
        seed_perm: List[int],
        cost_matrix: np.ndarray,
        sub_locs: List[int],
        entry_idx: int,
        exit_idx: int,
        max_shaking_iter: int = 15
    ) -> Dict[str, Any]:
        """VNS / Iterated Local Search with random shaking and VND descent."""
        t0 = time.perf_counter()
        K = len(seed_perm)
        best = list(seed_perm)
        best_cost = self.compute_directed_cost(best, cost_matrix, sub_locs, entry_idx, exit_idx)
        total_evals = 1

        for _ in range(max_shaking_iter):
            # Shaking: random 2-swap
            shaken = list(best)
            idx1, idx2 = np.random.choice(K, 2, replace=False)
            shaken[idx1], shaken[idx2] = shaken[idx2], shaken[idx1]

            # Local search via VND
            vnd_res = self.variable_neighborhood_descent(shaken, cost_matrix, sub_locs, entry_idx, exit_idx)
            total_evals += vnd_res["evaluations"]

            if vnd_res["cost_km"] < best_cost - 1e-4:
                best_cost = vnd_res["cost_km"]
                best = vnd_res["best_perm"]

        t_ms = (time.perf_counter() - t0) * 1000.0
        return {
            "best_perm": best,
            "cost_km": round(best_cost, 4),
            "time_ms": round(t_ms, 4),
            "evaluations": total_evals
        }

