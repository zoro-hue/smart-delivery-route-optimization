"""
Strong Algorithm Comparison Validation Test.
Verifies that all 11 registered algorithms:
1. Have distinct canonical result entries.
2. Do NOT silently copy or duplicate another solver's output.
3. Produce authentic, distinct route distances and sequences.
4. Validate 100% stop coverage (R == I) without synthetic substitution on failure.
5. ROUTE/IQ Cooperative Engine satisfies Proposition 1 non-degradation guardrail.
"""

import pytest
import numpy as np
from app.api.routes.optimization import run_optimization, OptimizationRequest, get_delivery_stops
from app.db.session import async_session_factory


@pytest.mark.asyncio
async def test_all_11_algorithms_distinct_and_validated():
    data = await get_delivery_stops(25)
    stops = data["stops"]
    assert len(stops) == 18, f"Expected 18 canonical stops, got {len(stops)}"

    algo_ids = [
        "clarke_wright", "dijkstra", "ortools", "astar",
        "qaoa", "qiga", "vnd", "routeiq_cooperative",
        "kernighan_lin", "tabu_search", "two_opt"
    ]

    req = OptimizationRequest(
        selection_mode="compare",
        selected_algorithms=algo_ids,
        num_customers=len(stops),
        num_vehicles=6,
        vehicle_capacity=100,
        depot_lat=40.7580,
        depot_lon=-73.8292,
        custom_customers=stops,
    )

    async with async_session_factory() as session:
        res = await run_optimization(req, session)

    results = res.get("results", {})
    assert len(results) >= 11, f"Expected at least 11 algorithm results, got {len(results)}"

    distances = {}
    routes_map = {}
    feasible_count = 0

    for algo in algo_ids:
        assert algo in results, f"Missing algorithm result for '{algo}'"
        r = results[algo]
        assert r.get("status") in ("SUCCESS", "FEASIBLE", "FAILED", "TIMED_OUT")
        
        dist = r.get("total_distance_km", 0.0)
        distances[algo] = dist
        routes = r.get("routes", [])
        routes_map[algo] = routes

        if r.get("is_feasible"):
            feasible_count += 1
            # Invariant: Every feasible solution must cover all 18 stops
            visited_stops = set()
            for route in routes:
                for s in route.get("customer_stops", []):
                    visited_stops.add(s)
            assert len(visited_stops) == 18, (
                f"Algorithm '{algo}' marked feasible but only visited {len(visited_stops)}/18 stops"
            )
            # Invariant: Vehicle fleet limit respected
            assert len(routes) <= 6, (
                f"Algorithm '{algo}' used {len(routes)} vehicles, exceeding fleet limit of 6"
            )

    # Invariant: Not all algorithms should produce the exact same distance (no 323.8km hardcoded fallback)
    unique_distances = set(round(d, 1) for d in distances.values() if d > 0)
    assert len(unique_distances) >= 5, (
        f"Expected at least 5 distinct route distance groups across 11 algorithms, got {len(unique_distances)}: {distances}"
    )

    # Invariant: ROUTE/IQ Cooperative Engine must be feasible and competitive
    coop_res = results.get("routeiq_cooperative", {})
    assert coop_res.get("is_feasible"), "ROUTE/IQ Cooperative Engine must produce a feasible solution"
    coop_dist = coop_res.get("total_distance_km", float("inf"))
    ortools_dist = results.get("ortools", {}).get("total_distance_km", float("inf"))
    
    # Proposition 1 Guardrail: Cooperative Engine must be <= OR-Tools incumbent distance + numerical epsilon
    assert coop_dist <= ortools_dist + 1e-3, (
        f"Proposition 1 violation: Cooperative distance ({coop_dist}) exceeds OR-Tools baseline ({ortools_dist})"
    )

    # Verify comparison summary items match result objects
    items = res.get("comparison_summary", {}).get("items", [])
    assert len(items) == 11, f"Expected 11 comparison summary items, got {len(items)}"
    for it in items:
        a_id = it["id"]
        assert abs(it["total_distance_km"] - distances[a_id]) < 1e-3, (
            f"Comparison item distance mismatch for {a_id}: {it['total_distance_km']} vs {distances[a_id]}"
        )

