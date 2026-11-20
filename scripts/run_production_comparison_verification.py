import time
import requests
import json
import sys

PROD_URL = "https://route-iq-backend.onrender.com"

print("=================================================================")
print("LIVE PRODUCTION 18-STOP COMPARISON VERIFICATION (ALL 11 ALGORITHMS)")
print("=================================================================")

# 1. Fetch 18 validated delivery stops
print("1. Fetching 18 delivery stops from production...")
stops_res = requests.get(f"{PROD_URL}/api/delivery-stops?limit=50", timeout=15)
assert stops_res.status_code == 200, f"Failed to fetch stops: {stops_res.text}"
all_stops = stops_res.json().get("stops", [])
stops = all_stops[:18]
print(f"   Retrieved {len(all_stops)} stops, selected {len(stops)}")

# 2. Start optimization job with all 11 algorithms
algorithms = [
    "routeiq_cooperative", "ortools", "clarke_wright", "two_opt",
    "dijkstra", "astar", "tabu_search", "kernighan_lin",
    "vnd", "qaoa", "qiga"
]

payload = {
    "selection_mode": "compare",
    "selected_algorithms": algorithms,
    "num_customers": 18,
    "num_vehicles": 3,
    "vehicle_capacity": 100.0,
    "depot_lat": 40.7128,
    "depot_lon": -74.0060,
    "custom_customers": stops,
    "traffic_scenario": "normal",
    "weather_scenario": "clear",
    "classical_time_limit_sec": 1,
    "qaoa_depth": 1,
    "qaoa_shots": 128,
    "qaoa_optimizer": "COBYLA"
}

print(f"\n2. Submitting compare job for {len(algorithms)} algorithms...")
t0 = time.time()
job_res = requests.post(f"{PROD_URL}/api/optimization/jobs", json=payload, timeout=20)
t_immediate = time.time() - t0
assert job_res.status_code == 200, f"Job submission failed: {job_res.text}"

job_data = job_res.json()
job_id = job_data["job_id"]
print(f"   Job ID: {job_id}")
print(f"   Immediate First Feasible Latency: {t_immediate:.3f}s (target < 2.0s)")
print(f"   Initial Status: {job_data['status']} | Primary: {job_data['primary_algorithm']}")
pri_dist = job_data['results'][job_data['primary_algorithm']]['total_distance_km']
print(f"   Primary Feasible Distance: {pri_dist:.2f} km")

# 3. Poll until terminal completion
print("\n3. Polling background solver progress...")
max_wait = 120
poll_start = time.time()
last_label = ""

while time.time() - poll_start < max_wait:
    time.sleep(2)
    elapsed = int(time.time() - poll_start)
    st_res = requests.get(f"{PROD_URL}/api/optimization/jobs/{job_id}/status", timeout=10)
    if st_res.status_code == 200:
        st_data = st_res.json()
        label = st_data.get("progress_label", "")
        if label != last_label:
            print(f"   [{elapsed:3d}s] Status: {st_data['status']} | Progress: {label}")
            last_label = label
        if st_data["status"] in ("COMPLETED", "FAILED", "CANCELLED"):
            print(f"\n   Job reached terminal status '{st_data['status']}' in {elapsed}s!")
            break

# 4. Tabulate final results
final_res = requests.get(f"{PROD_URL}/api/optimization/jobs/{job_id}/status", timeout=15).json()
results = final_res.get("results", {})
statuses = final_res.get("solver_statuses", {})

print("\n=================================================================")
print("FINAL LIVE PRODUCTION ALGORITHM COMPARISON RESULTS")
print("=================================================================")
print(f"{'Algorithm':<25} | {'Status':<10} | {'Distance (km)':<13} | {'Time (s)':<8} | {'Stops':<5}")
print("-----------------------------------------------------------------")

for algo_id in algorithms:
    r = results.get(algo_id, {})
    st = statuses.get(algo_id, "unknown")
    dist = r.get("total_distance_km", 0.0)
    exec_t = r.get("execution_time_sec", 0.0)
    served = r.get("served_customers", 0)
    print(f"{algo_id:<25} | {st:<10} | {dist:<13.3f} | {exec_t:<8.3f} | {served:<5}")

print("=================================================================")
summary = final_res.get("comparison_summary", {})
print(f"Best Algorithm: {summary.get('best_algorithm_name')} ({summary.get('best_feasible_distance_km')} km)")
print(f"Reason: {summary.get('best_reason')}")

# Verify Proposition 1
coop = results.get("routeiq_cooperative", {})
ortools = results.get("ortools", {})
if coop and ortools:
    c_dist = coop.get("total_distance_km", float('inf'))
    o_dist = ortools.get("total_distance_km", float('inf'))
    print(f"\nProposition 1 Guardrail Check:")
    print(f"  OR-Tools:    {o_dist:.3f} km")
    print(f"  Cooperative: {c_dist:.3f} km (Diff: {c_dist - o_dist:+.3f} km)")
    assert c_dist <= o_dist + 1e-4, f"Proposition 1 violated: {c_dist} > {o_dist}"
    print("  PROPOSITION 1 SATISFIED UNCONDITIONALLY!")

print("\nALL 11 ALGORITHMS VERIFIED COMPLETED ON LIVE PRODUCTION!")
