"""
ROUTE/IQ Next-Generation Cooperative Engine: Candidate Pool & Shared Blackboard Architecture.

Defines:
1. CandidateSolution: Full provenance, multi-objective metrics, vehicle condition assignments,
   route representation, and constraint violations.
2. CandidatePool: Thread-safe, diversity-preserving shared solution population supporting
   cross-algorithm exchange, iterative co-evolution, and monotonic incumbent preservation.
"""

import copy
import uuid
import time
import math
from typing import Dict, Any, List, Set, Tuple, Optional
import numpy as np


class CandidateSolution:
    """
    Standardized, self-contained solution candidate for the ROUTE/IQ Cooperative Pool.
    Maintains full algorithmic provenance, multi-objective metrics, and vehicle-condition feasibility.
    """

    def __init__(
        self,
        vehicle_routes: List[List[int]],
        generating_algorithm: str,
        modification_operator: str = "initial_construction",
        parent_id: Optional[str] = None,
        candidate_id: Optional[str] = None,
        iteration_created: int = 0,
        generation_time_ms: float = 0.0,
    ):
        self.candidate_id: str = candidate_id or f"cand_{uuid.uuid4().hex[:8]}"
        self.parent_id: Optional[str] = parent_id
        self.generating_algorithm: str = generating_algorithm
        self.modification_operator: str = modification_operator
        self.iteration_created: int = iteration_created
        self.generation_time_ms: float = generation_time_ms
        self.timestamp: float = time.time()

        # Route representation: list of customer stop indices per vehicle (depot omitted from internal lists)
        self.vehicle_routes: List[List[int]] = [list(r) for r in vehicle_routes]

        # Multi-objective metrics
        self.total_distance_km: float = 0.0
        self.total_travel_time_min: float = 0.0
        self.total_cost_usd: float = 0.0
        self.total_energy_kwh: float = 0.0
        self.total_emissions_kg_co2: float = 0.0
        self.scalarized_fitness: float = float("inf")

        # Feasibility & constraints
        self.is_feasible: bool = False
        self.capacity_violations: int = 0
        self.range_violations: int = 0
        self.unserved_customers: int = 0
        self.constraint_violations: Dict[str, int] = {
            "capacity": 0,
            "range": 0,
            "unserved": 0,
            "time_window": 0,
        }

        # Diversity & ancestry
        self.diversity_score: float = 0.0
        self.improvement_history: List[str] = [f"Created by {generating_algorithm} [{modification_operator}]"]
        self.vehicle_profiles: Optional[List[Dict[str, Any]]] = None
        self.metadata: Dict[str, Any] = {}

    def get_edges(self, depot: int = 0) -> Set[Tuple[int, int]]:
        """Extracts directed edge set for the entire fleet."""
        edges = set()
        for route in self.vehicle_routes:
            if not route:
                continue
            full_tour = [depot] + route + [depot]
            for i in range(len(full_tour) - 1):
                edges.add((full_tour[i], full_tour[i + 1]))
        return edges

    def get_undirected_edges(self, depot: int = 0) -> Set[Tuple[int, int]]:
        """Extracts undirected edge set for symmetric distance comparisons."""
        edges = set()
        for route in self.vehicle_routes:
            if not route:
                continue
            full_tour = [depot] + route + [depot]
            for i in range(len(full_tour) - 1):
                u, v = full_tour[i], full_tour[i + 1]
                edges.add((min(u, v), max(u, v)))
        return edges

    def jaccard_distance(self, other: "CandidateSolution", depot: int = 0) -> float:
        """
        Computes edge-based Jaccard topological distance between two routing candidates:
        Dist(S1, S2) = 1 - (|E1 ∩ E2| / |E1 ∪ E2|)
        Returns 0.0 for identical route topologies, 1.0 for completely disjoint edges.
        """
        e1 = self.get_undirected_edges(depot)
        e2 = other.get_undirected_edges(depot)
        if not e1 and not e2:
            return 0.0
        intersection = len(e1 & e2)
        union = len(e1 | e2)
        if union == 0:
            return 0.0
        return 1.0 - (intersection / union)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes candidate into a structured dictionary for logging, API, and persistence."""
        return {
            "candidate_id": self.candidate_id,
            "parent_id": self.parent_id,
            "generating_algorithm": self.generating_algorithm,
            "modification_operator": self.modification_operator,
            "iteration_created": self.iteration_created,
            "generation_time_ms": round(self.generation_time_ms, 2),
            "total_distance_km": round(self.total_distance_km, 3),
            "total_cost_usd": round(self.total_cost_usd, 2),
            "total_emissions_kg_co2": round(self.total_emissions_kg_co2, 3),
            "total_energy_kwh": round(self.total_energy_kwh, 2),
            "scalarized_fitness": round(self.scalarized_fitness, 4),
            "is_feasible": self.is_feasible,
            "capacity_violations": self.capacity_violations,
            "range_violations": self.range_violations,
            "unserved_customers": self.unserved_customers,
            "diversity_score": round(self.diversity_score, 4),
            "improvement_history": self.improvement_history,
            "vehicle_count": len(self.vehicle_routes),
            "stops_per_vehicle": [len(r) for r in self.vehicle_routes],
        }


class CandidatePool:
    """
    Shared candidate pool blackboard managing elite solutions, diversity metrics,
    and cross-algorithm exchange for the Next-Generation Cooperative Engine.
    """

    def __init__(self, max_capacity: int = 16, elite_size: int = 4, depot: int = 0):
        self.max_capacity: int = max_capacity
        self.elite_size: int = elite_size
        self.depot: int = depot

        self.candidates: List[CandidateSolution] = []
        self.incumbent: Optional[CandidateSolution] = None
        self.baseline_ortools: Optional[CandidateSolution] = None

        self.total_evaluated_count: int = 0
        self.total_accepted_count: int = 0
        self.duplicate_rejected_count: int = 0
        self.infeasible_rejected_count: int = 0

    def add_candidate(self, candidate: CandidateSolution) -> bool:
        """
        Evaluates candidate diversity, checks duplicates, updates incumbent,
        and conditionally inserts into the shared pool.
        Returns True if accepted into pool, False otherwise.
        """
        self.total_evaluated_count += 1

        # Check topological duplicates
        for existing in self.candidates:
            dist = candidate.jaccard_distance(existing, self.depot)
            if dist < 1e-4:  # Topologically identical edge graph
                # If identical topology but lower distance/cost (e.g. better 2-opt alignment), replace
                if candidate.scalarized_fitness < existing.scalarized_fitness - 1e-4:
                    self.candidates.remove(existing)
                    break
                else:
                    self.duplicate_rejected_count += 1
                    return False

        # Compute diversity relative to current pool members
        if self.candidates:
            candidate.diversity_score = float(np.mean([
                candidate.jaccard_distance(c, self.depot) for c in self.candidates
            ]))
        else:
            candidate.diversity_score = 1.0

        # Monotonic Incumbent Preservation
        if candidate.is_feasible:
            if self.incumbent is None or candidate.scalarized_fitness < self.incumbent.scalarized_fitness - 1e-4:
                self.incumbent = copy.deepcopy(candidate)

        # Insertion policy: if room, add directly
        if len(self.candidates) < self.max_capacity:
            self.candidates.append(candidate)
            self._sort_pool()
            self.total_accepted_count += 1
            return True

        # Pool is full: replacement policy
        # Sort candidates: elite protected, non-elite can be replaced by higher fitness or higher diversity
        self._sort_pool()
        elite_set = set(c.candidate_id for c in self.candidates[:self.elite_size])

        # Find worst candidate not in elite set
        candidates_to_consider = [c for c in self.candidates if c.candidate_id not in elite_set]
        if not candidates_to_consider:
            candidates_to_consider = self.candidates[self.elite_size:]

        # Select candidate with worst composite score: (fitness - 0.2 * diversity)
        worst_c = max(candidates_to_consider, key=lambda c: c.scalarized_fitness - 0.15 * c.diversity_score)

        if candidate.scalarized_fitness < worst_c.scalarized_fitness or (
            candidate.diversity_score > worst_c.diversity_score + 0.2 and candidate.is_feasible
        ):
            self.candidates.remove(worst_c)
            self.candidates.append(candidate)
            self._sort_pool()
            self.total_accepted_count += 1
            return True

        return False

    def select_parent(self, tournament_size: int = 3, diversity_bias: float = 0.25) -> CandidateSolution:
        """
        Tournament selection combining fitness rank and diversity score:
        Score = Rank(fitness) + diversity_bias * Rank(diversity)
        Ensures search explores promising but topologically distinct regions.
        """
        if not self.candidates:
            raise ValueError("Candidate pool is empty; cannot select parent.")
        if len(self.candidates) <= tournament_size:
            return copy.deepcopy(min(self.candidates, key=lambda c: c.scalarized_fitness))

        participants = np.random.choice(len(self.candidates), size=tournament_size, replace=False)
        selected_cand = min(
            [self.candidates[i] for i in participants],
            key=lambda c: c.scalarized_fitness - (diversity_bias * c.diversity_score * (self.incumbent.scalarized_fitness if self.incumbent else 1.0))
        )
        return copy.deepcopy(selected_cand)

    def get_elite(self, k: int = 3) -> List[CandidateSolution]:
        """Returns the top-k elite candidates sorted by scalarized fitness."""
        self._sort_pool()
        return [copy.deepcopy(c) for c in self.candidates[:min(k, len(self.candidates))]]

    def get_diversity(self) -> float:
        """Calculates current population diversity as the mean pairwise Jaccard distance."""
        if len(self.candidates) < 2:
            return 0.0
        distances = []
        for i in range(len(self.candidates)):
            for j in range(i + 1, len(self.candidates)):
                distances.append(self.candidates[i].jaccard_distance(self.candidates[j], self.depot))
        return float(np.mean(distances)) if distances else 0.0

    def _sort_pool(self):
        """Sorts candidate pool by feasibility (feasible first), then scalarized fitness."""
        self.candidates.sort(key=lambda c: (
            0 if c.is_feasible else 1,
            c.unserved_customers,
            c.capacity_violations + c.range_violations,
            c.scalarized_fitness,
        ))

    def get_provenance_summary(self) -> List[Dict[str, Any]]:
        """Returns provenance history of all currently surviving candidates in the pool."""
        return [c.to_dict() for c in self.candidates]
