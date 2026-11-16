import sys, os, time
sys.path.insert(0, '.')
sys.path.insert(0, 'backend')

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("Testing /api/health...")
r_health = client.get("/api/health")
print("Health:", r_health.status_code, r_health.json())

print("Testing /api/delivery-stops...")
r_stops = client.get("/api/delivery-stops?limit=25")
stops = r_stops.json().get("stops", [])
print(f"Stops returned: {len(stops)}")

payload = {
    "selection_mode": "custom",
    "selected_algorithms": ["routeiq_cooperative"],
    "custom_customers": stops[:18],
    "num_customers": 18,
    "num_vehicles": 3,
    "vehicle_capacity": 1000.0,
    "depot_lat": 40.7128,
    "depot_lon": -74.0060,
    "classical_time_limit_sec": 1,
}

print("\nSubmitting POST /api/optimization/jobs with ROUTE/IQ Cooperative...")
t0 = time.perf_counter()
res = client.post("/api/optimization/jobs", json=payload)
t_post = time.perf_counter() - t0
print(f"POST Response Code: {res.status_code} in {t_post:.3f} s")
data = res.json()
print("Job ID:", data.get("job_id"))
print("Status:", data.get("status"))
print("Primary Algorithm:", data.get("primary_algorithm"))

primary_result = data.get("results", {}).get("routeiq_cooperative", {})
print("Distance:", primary_result.get("total_distance_km"), "km")
print("Execution Time:", primary_result.get("execution_time_sec"), "s")
print("Is Feasible:", primary_result.get("is_feasible"))

telemetry = primary_result.get("cooperative_telemetry", {})
print("Spark Mode:", telemetry.get("spark_mode"))
print("Proposition 1 Guaranteed:", telemetry.get("proposition1_guaranteed"))
print("Profiling Breakdown:")
for k, v in telemetry.get("profiling_breakdown", {}).items():
    print(f"  {k}: {v} ms")

print("\nAPI TEST COMPLETED SUCCESSFULLY!")
