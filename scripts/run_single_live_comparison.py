import requests
import json
import time

BASE_URL = "https://route-iq-backend.onrender.com"
stops_res = requests.get(f"{BASE_URL}/api/delivery-stops?limit=25", timeout=15)
stops = stops_res.json().get("stops", [])
print(f"Fetched {len(stops)} stops from backend.", flush=True)

payload = {
    "selection_mode": "compare",
    "custom_customers": stops,
    "num_customers": len(stops),
    "num_vehicles": 3,
    "vehicle_capacity": 1000.0,
    "depot_lat": 40.7128,
    "depot_lon": -74.0060,
    "classical_time_limit_sec": 1,
}

t0 = time.time()
r = requests.post(f"{BASE_URL}/api/optimization/jobs", json=payload, timeout=30)
r.raise_for_status()
job = r.json()
job_id = job["job_id"]
primary = job.get("primary_algorithm", "ortools")
primary_dist = job.get("results", {}).get(primary, {}).get("total_distance_km")
print(f"Job {job_id} created in {round(time.time()-t0, 2)}s | Status: {job.get('status')} | Primary: {primary} ({primary_dist} km)", flush=True)

sdata = {}
for poll in range(40):
    time.sleep(3)
    sr = requests.get(f"{BASE_URL}/api/optimization/jobs/{job_id}/status", timeout=15)
    sdata = sr.json()
    status = sdata.get("status")
    completed = sdata.get("completed_algorithms", 0)
    total = sdata.get("total_algorithms", 0)
    label = sdata.get("progress_label", "")
    print(f"[{round(time.time()-t0, 1)}s] Status: {status} | Progress: {label} | Solvers: {completed}/{total}", flush=True)
    if status in ["COMPLETED", "FAILED", "CANCELLED", "PARTIAL"] and (completed >= total or status == "COMPLETED"):
        break

print(f"\nFINAL STATUS: {sdata.get('status')}", flush=True)
results = sdata.get("results", {})
print(f"Total Completed Solvers: {len(results)}/{sdata.get('total_algorithms')}", flush=True)
for k, v in results.items():
    print(f"  - {k}: {v.get('total_distance_km')} km (status={v.get('status')}) in {v.get('execution_time_sec')}s", flush=True)
