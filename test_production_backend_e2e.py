"""
Production End-to-End Verification Script
Tests https://route-iq-backend.onrender.com/
"""
import requests
import json
import time
import sys

PROD_URL = "https://route-iq-backend.onrender.com"

def main():
    print("Testing Production Backend:", PROD_URL, flush=True)
    
    # 1. Health check
    h_res = requests.get(f"{PROD_URL}/health", timeout=30)
    print("1. Health Endpoint Status:", h_res.status_code, flush=True)
    h_data = h_res.json()
    print("   Version:", h_data.get("version"), flush=True)
    print("   Python Version:", h_data.get("python_version"), flush=True)
    print("   Environment:", h_data.get("environment"), flush=True)
    assert h_res.status_code == 200
    assert h_data.get("python_version") == "3.11.18"

    # 2. Algorithms registry
    a_res = requests.get(f"{PROD_URL}/api/optimization/algorithms", timeout=30)
    print("\n2. Algorithms Registry Status:", a_res.status_code, flush=True)
    a_data = a_res.json()
    count = a_data.get("count", 0)
    algorithms = a_data.get("algorithms", [])
    print(f"   Algorithm Count: {count}", flush=True)
    assert count == 11, f"Expected 11 algorithms, got {count}"
    alg_ids = [a["id"] for a in algorithms]
    print(f"   Registered IDs: {alg_ids}", flush=True)
    for required_id in ["routeiq_cooperative", "ortools", "clarke_wright", "two_opt", "dijkstra", "astar", "tabu_search", "kernighan_lin", "vnd", "qaoa", "qiga"]:
        assert required_id in alg_ids, f"Missing required algorithm: {required_id}"

    # Verify quantum simulation labeling
    qaoa_meta = next(a for a in algorithms if a["id"] == "qaoa")
    assert "simulation" in qaoa_meta["compute_type"].lower(), f"Invalid QAOA compute type: {qaoa_meta['compute_type']}"
    assert "cpu simulation" in qaoa_meta["description"].lower(), f"QAOA description must state CPU simulation: {qaoa_meta['description']}"

    # 3. 18-Stop Canonical NYC Benchmark Problem
    custom_stops = [
        {"lat": 40.7589, "lon": -73.9851, "demand": 5.0},
        {"lat": 40.7614, "lon": -73.9776, "demand": 5.0},
        {"lat": 40.7527, "lon": -73.9772, "demand": 5.0},
        {"lat": 40.7484, "lon": -73.9857, "demand": 5.0},
        {"lat": 40.7505, "lon": -73.9934, "demand": 5.0},
        {"lat": 40.7549, "lon": -73.9840, "demand": 5.0},
        {"lat": 40.7580, "lon": -73.9750, "demand": 5.0},
        {"lat": 40.7630, "lon": -73.9800, "demand": 5.0},
        {"lat": 40.7450, "lon": -73.9880, "demand": 5.0},
        {"lat": 40.7420, "lon": -73.9920, "demand": 5.0},
        {"lat": 40.7650, "lon": -73.9700, "demand": 5.0},
        {"lat": 40.7700, "lon": -73.9650, "demand": 5.0},
        {"lat": 40.7380, "lon": -73.9900, "demand": 5.0},
        {"lat": 40.7350, "lon": -73.9950, "demand": 5.0},
        {"lat": 40.7550, "lon": -73.9680, "demand": 5.0},
        {"lat": 40.7600, "lon": -73.9620, "demand": 5.0},
        {"lat": 40.7480, "lon": -73.9720, "demand": 5.0},
        {"lat": 40.7510, "lon": -73.9650, "demand": 5.0},
    ]
    base_payload = {
        "depot_lat": 40.7580,
        "depot_lon": -73.8292,
        "num_customers": 18,
        "num_vehicles": 3,
        "vehicle_capacity": 40,
        "custom_customers": custom_stops,
        "traffic_scenario": "normal",
        "weather_scenario": "clear"
    }

    # 4. Testing Single Optimization (OR-Tools, 18 stops)
    print("\n3. Testing Single Optimization (OR-Tools, 18 stops)...", flush=True)
    payload_ortools = dict(base_payload)
    payload_ortools["selection_mode"] = "custom"
    payload_ortools["selected_algorithms"] = ["ortools"]

    t0 = time.time()
    o_res = requests.post(f"{PROD_URL}/api/optimization/run", json=payload_ortools, timeout=180)
    dur = time.time() - t0
    print(f"   Response Status: {o_res.status_code} in {dur:.2f}s", flush=True)
    assert o_res.status_code == 200, f"Error: {o_res.text}"
    o_data = o_res.json()
    ortools_res = o_data.get("results", {}).get("ortools", {})
    routes = ortools_res.get("routes", [])
    visited = set()
    for r in routes:
        for s in r.get("customer_stops", []):
            visited.add(s)
    print(f"   OR-Tools returned {len(routes)} routes, {len(visited)}/18 stops visited", flush=True)
    print(f"   Total distance: {ortools_res.get('total_distance_km')} km, Status: {ortools_res.get('status')}", flush=True)
    assert len(visited) == 18, f"Expected 18 visited stops, got {len(visited)}"
    assert ortools_res.get("capacity_violations") == 0
    assert ortools_res.get("unserved_customers") == 0

    # 5. Testing Flagship Cooperative Solver
    print("\n4. Testing ROUTE/IQ Cooperative Engine (18 stops)...", flush=True)
    payload_coop = dict(base_payload)
    payload_coop["selection_mode"] = "recommended"
    payload_coop["selected_algorithms"] = ["routeiq_cooperative"]

    t0 = time.time()
    c_res = requests.post(f"{PROD_URL}/api/optimization/run", json=payload_coop, timeout=180)
    dur = time.time() - t0
    print(f"   Response Status: {c_res.status_code} in {dur:.2f}s", flush=True)
    assert c_res.status_code == 200, f"Error: {c_res.text}"
    c_data = c_res.json()
    coop_res = c_data.get("results", {}).get("routeiq_cooperative", {})
    c_routes = coop_res.get("routes", [])
    c_visited = set()
    for r in c_routes:
        for s in r.get("customer_stops", []):
            c_visited.add(s)
    print(f"   ROUTE/IQ Cooperative returned {len(c_routes)} routes, {len(c_visited)}/18 stops visited", flush=True)
    print(f"   Total distance: {coop_res.get('total_distance_km')} km, Status: {coop_res.get('status')}", flush=True)
    assert len(c_visited) == 18, f"Expected 18 visited stops, got {len(c_visited)}"
    assert coop_res.get("capacity_violations") == 0
    assert coop_res.get("unserved_customers") == 0

    # 6. Testing Full Comparison Suite (selection_mode: compare)
    print("\n5. Testing Compare All Suite (11 Algorithms on Live Production)...", flush=True)
    payload_cmp = dict(base_payload)
    payload_cmp["selection_mode"] = "compare"

    t0 = time.time()
    cmp_res = requests.post(f"{PROD_URL}/api/optimization/run", json=payload_cmp, timeout=240)
    dur = time.time() - t0
    print(f"   Compare Suite Status: {cmp_res.status_code} in {dur:.2f}s", flush=True)
    assert cmp_res.status_code == 200, f"Error: {cmp_res.text}"
    cmp_data = cmp_res.json()
    all_res = cmp_data.get("results", {})
    cmp_items = cmp_data.get("comparison_summary", {}).get("items", [])
    print(f"   Returned comparison results for {len(all_res)} algorithms, {len(cmp_items)} summary items:", flush=True)
    for item in cmp_items:
        alg_id = item["id"]
        served = item["served_customers"]
        unserved = item["unserved_customers"]
        cap_viol = item["capacity_violations"]
        dist = item["total_distance_km"]
        status = item["status"]
        print(f"     - [{alg_id}] {item['name']}: {served}/18 served ({unserved} unserved), {cap_viol} cap violations, dist: {dist} km, status: {status}", flush=True)
        assert served == 18, f"Algorithm {alg_id} served only {served}/18 stops!"
        assert unserved == 0, f"Algorithm {alg_id} has {unserved} unserved stops!"
        assert cap_viol == 0, f"Algorithm {alg_id} has {cap_viol} capacity violations!"

    print("\n" + "=" * 80, flush=True)
    print("ALL PRODUCTION E2E VERIFICATIONS PASSED WITH 100% STOP COVERAGE!", flush=True)
    print("=" * 80, flush=True)

if __name__ == "__main__":
    main()
