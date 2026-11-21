"""Verify vehicle profile optimization job through FastAPI test client."""
import asyncio
from app.main import app
from httpx import AsyncClient, ASGITransport

async def main():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Fetch propulsion models
        res = await client.get("/api/optimization/propulsion-models")
        print("Propulsion models:", res.status_code, list(res.json().get("models", {}).keys()))

        # Submit optimization job with 3 heterogeneous vehicle profiles
        payload = {
            "num_customers": 4,
            "num_vehicles": 3,
            "vehicle_capacity": 80,
            "depot_lat": 40.7580,
            "depot_lon": -73.8292,
            "selection_mode": "recommended",
            "selected_algorithms": ["routeiq_cooperative", "ortools"],
            "vehicle_profiles": [
                {
                    "id": "veh-1",
                    "name": "Vehicle 1 (Ford E-Transit BEV)",
                    "vehicle_type": "electric_van",
                    "powertrain": "electric",
                    "capacity_kg": 90,
                    "condition": "excellent",
                    "battery_capacity_kwh": 68.0,
                    "battery_soc_percent": 85.0,
                    "battery_soh_percent": 96.0,
                    "max_range_km": 190.0,
                    "is_available": True,
                    "maintenance_status": "ok",
                },
                {
                    "id": "veh-2",
                    "name": "Vehicle 2 (Mercedes Sprinter Diesel)",
                    "vehicle_type": "van",
                    "powertrain": "diesel",
                    "capacity_kg": 120,
                    "condition": "good",
                    "fuel_tank_capacity_l": 75.0,
                    "fuel_level_percent": 80.0,
                    "max_range_km": 280.0,
                    "is_available": True,
                    "maintenance_status": "ok",
                },
                {
                    "id": "veh-3",
                    "name": "Vehicle 3 (Grounded Broken Van)",
                    "vehicle_type": "van",
                    "powertrain": "petrol",
                    "capacity_kg": 70,
                    "condition": "poor",
                    "is_available": False,
                    "maintenance_status": "critical",
                }
            ],
            "custom_customers": [
                {"id": 1, "lat": 40.7600, "lon": -73.8320, "demand": 15},
                {"id": 2, "lat": 40.7520, "lon": -73.8250, "demand": 25},
                {"id": 3, "lat": 40.7650, "lon": -73.8210, "demand": 20},
                {"id": 4, "lat": 40.7480, "lon": -73.8350, "demand": 18},
            ]
        }

        job_resp = await client.post("/api/optimization/jobs", json=payload)
        print("Start job status:", job_resp.status_code)
        job_data = job_resp.json()
        job_id = job_data.get("job_id")
        print("Job ID:", job_id, "Status:", job_data.get("status"))

        # Poll status
        for _ in range(15):
            await asyncio.sleep(0.5)
            stat_res = await client.get(f"/api/optimization/jobs/{job_id}/status")
            stat_data = stat_res.json()
            if stat_data.get("status") in ("COMPLETED", "FAILED"):
                print("Final job status:", stat_data.get("status"))
                results = stat_data.get("results", {})
                for algo, a_res in results.items():
                    print(f"Algorithm: {algo}")
                    print(f"  Distance: {a_res.get('total_distance_km')} km")
                    print(f"  Routes: {len(a_res.get('routes', []))}")
                    for r in a_res.get("routes", []):
                        vp = r.get("vehicle_profile", {})
                        print(f"    Driver {r.get('vehicle_id')}: {vp.get('name')} ({vp.get('powertrain')}) - load {r.get('load')}/{r.get('capacity')} kg")
                summary = stat_data.get("comparison_summary", {})
                print("Energy analysis included:", "energy_analysis" in summary)
                break

if __name__ == "__main__":
    asyncio.run(main())
