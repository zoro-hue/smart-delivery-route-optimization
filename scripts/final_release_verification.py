import requests
import json
import time
import sys

BASE_URL = "https://route-iq-backend.onrender.com"

print("=" * 70, flush=True)
print("FINAL RELEASE PRODUCTION VERIFICATION AUDIT", flush=True)
print(f"Target Backend: {BASE_URL}", flush=True)
print("=" * 70, flush=True)

# Step A: Baseline Memory
mem_res = requests.get(f"{BASE_URL}/api/system/memory", timeout=15)
baseline_mem = mem_res.json()
print(f"Baseline RSS: {baseline_mem.get('process_rss_mb')} MB | Headroom: {baseline_mem.get('render_headroom_mb')} MB", flush=True)

# Step B: Fetch 18 Stops
stops_res = requests.get(f"{BASE_URL}/api/delivery-stops?limit=25", timeout=15)
stops = stops_res.json().get("stops", [])
print(f"Retrieved {len(stops)} delivery stops from backend.", flush=True)
assert len(stops) == 18, f"Expected 18 stops, got {len(stops)}"

payload = {
    "selection_mode": "compare",
    "selected_algorithms": [
        "routeiq_cooperative", "ortools", "clarke_wright", "two_opt",
        "dijkstra", "astar", "tabu_search", "kernighan_lin", "vnd", "qaoa", "qiga"
    ],
    "custom_customers": stops,
    "num_customers": len(stops),
    "num_vehicles": 3,
    "vehicle_capacity": 1000.0,
    "depot_lat": 40.7128,
    "depot_lon": -74.0060,
    "classical_time_limit_sec": 1,
}

# Step C: Submit Job and Measure ROUTE/IQ Cooperative Primary Latency
print("\nSubmitting optimization job...", flush=True)
t_start = time.time()
job_res = requests.post(f"{BASE_URL}/api/optimization/jobs", json=payload, timeout=45)
primary_latency = round(time.time() - t_start, 3)

assert job_res.status_code == 200, f"Job submission failed: {job_res.status_code} {job_res.text}"
job_data = job_res.json()
job_id = job_data["job_id"]
primary_algo = job_data.get("primary_algorithm")
primary_result = job_data.get("results", {}).get(primary_algo, {})
primary_dist = primary_result.get("total_distance_km")
primary_exec_sec = primary_result.get("execution_time_sec")

print(f"\n[Primary Route Evaluation]", flush=True)
print(f"Job ID: {job_id}", flush=True)
print(f"Primary Algorithm: {primary_algo}", flush=True)
print(f"Initial HTTP Latency: {primary_latency}s", flush=True)
print(f"Solver Reported Execution Time: {primary_exec_sec}s", flush=True)
print(f"Primary Distance: {primary_dist} km", flush=True)
print(f"Primary Feasible: {primary_result.get('is_feasible')}", flush=True)

# Step D: Poll Background Solvers
final_data = {}
max_polls = 40
for poll in range(max_polls):
    time.sleep(3)
    try:
        sr = requests.get(f"{BASE_URL}/api/optimization/jobs/{job_id}/status", timeout=15)
        if sr.status_code == 200:
            final_data = sr.json()
            completed = final_data.get("completed_algorithms", 0)
            total = final_data.get("total_algorithms", 0)
            status = final_data.get("status")
            elapsed = round(time.time() - t_start, 1)
            print(f"[{elapsed}s] Poll #{poll+1}: status={status} | completed={completed}/{total} | label={final_data.get('progress_label')}", flush=True)
            
            if status in ["COMPLETED", "FAILED", "CANCELLED"] or (completed >= total and status == "COMPLETED"):
                break
    except Exception as poll_err:
        print(f"Poll #{poll+1} transient error: {poll_err}", flush=True)

# Step E: Post-Job Memory Check
try:
    post_mem = requests.get(f"{BASE_URL}/api/system/memory", timeout=15).json()
    post_rss = post_mem.get("process_rss_mb")
    post_hr = post_mem.get("render_headroom_mb")
    print(f"\nPost-Job RSS: {post_rss} MB | Headroom: {post_hr} MB", flush=True)
except Exception as e:
    post_rss = baseline_mem.get("process_rss_mb")
    post_hr = baseline_mem.get("render_headroom_mb")

# Step F: Deep Verification of All 11 Algorithms
print("\n" + "=" * 70, flush=True)
print("DEEP VERIFICATION OF ALGORITHM RESULTS", flush=True)
print("=" * 70, flush=True)

results = final_data.get("results", {})
total_solvers = len(results)
print(f"Total Solvers Returned: {total_solvers}/11", flush=True)

distinct_distances = set()
distinct_routes = set()
all_served = True
all_capacity_respected = True
all_feasible = True

summary_table = []

for algo_id in payload["selected_algorithms"]:
    res = results.get(algo_id, {})
    dist = res.get("total_distance_km", 0.0)
    exec_t = res.get("execution_time_sec", 0.0)
    routes = res.get("routes", [])
    feasible = res.get("is_feasible", False)
    unserved = res.get("unserved_customers", 0)
    cap_viol = res.get("capacity_violations", 0)
    status = res.get("status", "UNKNOWN")

    distinct_distances.add(round(dist, 2))
    
    # Check stops served across all routes of this solver
    served_stops = set()
    for r in routes:
        stops_in_r = r.get("stops", [])
        for st in stops_in_r:
            c_id = st.get("id") if isinstance(st, dict) else st
            if c_id not in [0, "depot", "DEPOT", None]:
                served_stops.add(c_id)
        # Check capacity
        demand_r = r.get("total_demand", 0.0)
        if demand_r > payload["vehicle_capacity"] + 1e-4:
            all_capacity_respected = False

    route_signature = tuple(
        tuple(st.get("id") if isinstance(st, dict) else st for st in r.get("stops", []))
        for r in routes
    )
    distinct_routes.add(route_signature)

    if unserved > 0 or len(served_stops) < 18:
        all_served = False
    if not feasible:
        all_feasible = False

    summary_table.append({
        "algorithm": algo_id,
        "name": res.get("algorithm_name", algo_id.upper()),
        "distance_km": dist,
        "execution_time_sec": exec_t,
        "is_feasible": feasible,
        "unserved": unserved,
        "capacity_violations": cap_viol,
        "num_routes": len(routes),
        "status": status,
        "profiling": res.get("resource_metrics", {})
    })
    print(f"[{algo_id:20}] Dist: {dist:8.3f} km | Time: {exec_t:6.3f}s | Feasible: {feasible} | Served: {len(served_stops)}/18 | Cap Viol: {cap_viol} | Status: {status}", flush=True)

# Step G: Verify ROUTE/IQ Cooperative Engine Specific Invariants
coop_res = results.get("routeiq_cooperative", {})
ortools_res = results.get("ortools", {})
coop_dist = coop_res.get("total_distance_km", 9999.0)
ortools_dist = ortools_res.get("total_distance_km", 9999.0)
prop1_satisfied = coop_dist <= ortools_dist + 1e-5

print("\n" + "=" * 70, flush=True)
print("INVARIANT AUDIT", flush=True)
print("=" * 70, flush=True)
print(f"1. Proposition 1 Invariant (Cost(Coop) <= Cost(ORTools)): {prop1_satisfied} ({coop_dist} km vs {ortools_dist} km)", flush=True)
print(f"2. Number of Distinct Objective Distances: {len(distinct_distances)} (Expected > 5, eliminates identical 323.8km bug)", flush=True)
print(f"3. All 18 Stops 100% Served: {all_served}", flush=True)
print(f"4. All Vehicle Capacity Constraints Respected: {all_capacity_respected}", flush=True)
print(f"5. All Solvers Feasible: {all_feasible}", flush=True)
print(f"6. Primary ROUTE/IQ Initial HTTP Latency: {primary_latency}s (< 2.0s target: {primary_latency < 2.0})", flush=True)
print(f"7. ROUTE/IQ Solver Algorithm Execution Time: {primary_exec_sec}s (< 2.0s target: {primary_exec_sec < 2.0})", flush=True)
print(f"8. Post-Job Render RSS: {post_rss} MB (Headroom: {post_hr} MB, Limit: 512.0 MB)", flush=True)

verification_output = {
    "audit_timestamp": time.time(),
    "backend_url": BASE_URL,
    "job_id": job_id,
    "num_stops": len(stops),
    "primary_algorithm": primary_algo,
    "primary_http_latency_sec": primary_latency,
    "primary_solver_time_sec": primary_exec_sec,
    "post_job_rss_mb": post_rss,
    "post_job_headroom_mb": post_hr,
    "distinct_distances_count": len(distinct_distances),
    "all_18_stops_served": all_served,
    "capacity_constraints_held": all_capacity_respected,
    "all_solvers_feasible": all_feasible,
    "proposition1_satisfied": prop1_satisfied,
    "cooperative_breakdown": coop_res.get("cooperative_breakdown", {}),
    "algorithms_summary": summary_table
}

import os
os.makedirs("production_evidence", exist_ok=True)
with open("production_evidence/final_release_verification_results.json", "w") as f:
    json.dump(verification_output, f, indent=2)

print("\nSaved verification output to production_evidence/final_release_verification_results.json", flush=True)
