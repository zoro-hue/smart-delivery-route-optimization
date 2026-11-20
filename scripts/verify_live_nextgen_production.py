import urllib.request
import json
import time
import sys

base_url = "https://route-iq-backend.onrender.com"
print("Fetching 18 valid delivery stops from live backend...")

# 1. Fetch delivery stops
try:
    with urllib.request.urlopen(f"{base_url}/api/delivery-stops?limit=50", timeout=15) as resp:
        stops_data = json.loads(resp.read().decode("utf-8"))
        raw_stops = stops_data.get("stops", [])
        print(f"Retrieved {len(raw_stops)} available delivery stops.")
except Exception as e:
    print("Failed to fetch delivery stops:", e)
    sys.exit(1)

valid_stops = raw_stops[:18]
depot_lat = 40.7580
depot_lon = -73.8292

custom_customers = [
    {
        "id": s.get("id", f"cust_{i+1}"),
        "lat": s["lat"],
        "lon": s["lon"],
        "demand": float(s.get("demand", 10.0)),
    }
    for i, s in enumerate(valid_stops)
]

print(f"Prepared {len(custom_customers)} custom customer stops.")

payload = {
    "num_customers": len(custom_customers),
    "num_vehicles": 3,
    "vehicle_capacity": 100.0,
    "depot_lat": depot_lat,
    "depot_lon": depot_lon,
    "selection_mode": "compare",
    "selected_algorithms": [
        "routeiq_cooperative",
        "ortools",
        "clarke_wright",
        "two_opt",
        "dijkstra",
        "astar",
        "tabu_search",
        "kernighan_lin",
        "vnd",
        "qiga",
        "qaoa"
    ],
    "custom_customers": custom_customers,
    "random_seed": 42
}

req_data = json.dumps(payload).encode("utf-8")
headers = {"Content-Type": "application/json"}
req = urllib.request.Request(f"{base_url}/api/optimization/jobs", data=req_data, headers=headers, method="POST")

try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        job = json.loads(resp.read().decode("utf-8"))
        job_id = job.get("job_id")
        print(f"Successfully started optimization job: {job_id}, initial status: {job.get('status')}")
except Exception as e:
    print("Failed to start job:", e)
    sys.exit(1)

# Poll until complete
print("Polling job status until completion...")
for poll_idx in range(40):
    time.sleep(3)
    try:
        url = f"{base_url}/api/optimization/jobs/{job_id}/status"
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            status = data.get("status")
            comp_val = data.get("completed_algorithms", 0)
            comp_count = comp_val if isinstance(comp_val, int) else len(comp_val)
            print(f"[{poll_idx+1:2d}] Status: {status:10} | Completed: {comp_count:2d}/{len(payload['selected_algorithms'])} algorithms")
            if status in ("COMPLETED", "FAILED"):
                print("\n=== OPTIMIZATION JOB FINISHED ===")
                results = data.get("results", {})
                for algo_id, r in results.items():
                    dist = r.get("total_distance_km")
                    t_sec = r.get("execution_time_sec", 0.0)
                    st = r.get("status")
                    print(f"  - {algo_id:22}: {dist} km ({t_sec:.2f}s) [{st}]")
                summary = data.get("comparison_summary", {})
                best = summary.get("best_solution", {})
                print(f"\nBest Solution: {best.get('algorithm_name')} ({best.get('total_distance_km')} km)")
                with open("live_production_comparison_result.json", "w") as f:
                    json.dump(data, f, indent=2)
                sys.exit(0)
    except Exception as e:
        print(f"[{poll_idx+1:2d}] Polling error: {e}")
