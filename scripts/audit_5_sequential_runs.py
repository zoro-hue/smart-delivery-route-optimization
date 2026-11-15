import json
import time
import requests
import sys

BASE_URL = "https://route-iq-backend.onrender.com"

def get_mem():
    try:
        r = requests.get(f"{BASE_URL}/api/system/memory", timeout=15)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"Memory check err: {e}", flush=True)
    return {}

def run_single_audit(run_idx, stops):
    print(f"\n==================== RUN {run_idx}/5 ====================", flush=True)
    mem_before = get_mem()
    rss_before = mem_before.get("process_rss_mb", 0.0)
    print(f"[{run_idx}] Baseline RSS before job: {rss_before:.2f} MB", flush=True)

    payload = {
        "selection_mode": "compare",
        "custom_customers": stops,
        "num_customers": len(stops),
        "num_vehicles": 3,
        "vehicle_capacity": 1000.0,
        "depot_lat": 40.7128,
        "depot_lon": -74.0060
    }

    t0 = time.time()
    try:
        res = requests.post(f"{BASE_URL}/api/optimization/jobs", json=payload, timeout=60)
        res.raise_for_status()
        data = res.json()
    except Exception as e:
        print(f"[{run_idx}] Error starting job: {e}", flush=True)
        return None

    init_time = time.time() - t0
    job_id = data.get("job_id")
    primary_solver = data.get("primary_solver")
    primary_dist = data.get("primary_result", {}).get("total_distance_km")
    print(f"[{run_idx}] Job created: {job_id} in {init_time:.2f}s | Primary: {primary_solver} ({primary_dist} km)", flush=True)

    peak_rss = rss_before
    final_data = None
    poll_count = 0

    while True:
        time.sleep(3)
        poll_count += 1
        m = get_mem()
        current_rss = m.get("process_rss_mb", 0.0)
        if current_rss > peak_rss:
            peak_rss = current_rss

        try:
            r = requests.get(f"{BASE_URL}/api/optimization/jobs/{job_id}/status", timeout=20)
            if r.status_code == 200:
                final_data = r.json()
                status = final_data.get("status")
                completed_count = final_data.get("completed_algorithms", 0)
                total_expected = final_data.get("total_algorithms", 0)
                print(f"[{run_idx}] Poll {poll_count}: Status={status}, Solvers={completed_count}/{total_expected}, Current RSS={current_rss:.2f} MB (Peak={peak_rss:.2f} MB)", flush=True)
                if status in ["COMPLETED", "FAILED", "CANCELLED"] or (total_expected > 0 and completed_count >= total_expected):
                    break
            else:
                print(f"[{run_idx}] Poll HTTP {r.status_code}", flush=True)
        except Exception as e:
            print(f"[{run_idx}] Poll error: {e}", flush=True)

    total_time = time.time() - t0
    print(f"[{run_idx}] Job finished in {total_time:.2f}s with status {final_data.get('status')} ({completed_count}/{total_expected} algorithms)", flush=True)

    # Wait 8s for gc/cleanup
    time.sleep(8)
    mem_after = get_mem()
    rss_after = mem_after.get("process_rss_mb", 0.0)
    print(f"[{run_idx}] Post-job RSS: {rss_after:.2f} MB (Delta from baseline: {rss_after - rss_before:+.2f} MB)", flush=True)

    solvers = {}
    for name, sdata in final_data.get("results", {}).items():
        solvers[name] = {
            "status": sdata.get("status") or ("completed" if sdata.get("total_distance_km") else "failed"),
            "distance_km": sdata.get("total_distance_km"),
            "vehicles": sdata.get("vehicles_used") or (len(sdata.get("routes", [])) if sdata.get("routes") else 0),
            "execution_time_s": sdata.get("execution_time_s")
        }

    return {
        "run_idx": run_idx,
        "job_id": job_id,
        "status": final_data.get("status"),
        "init_time_s": round(init_time, 2),
        "total_time_s": round(total_time, 2),
        "rss_before_mb": round(rss_before, 2),
        "peak_rss_mb": round(peak_rss, 2),
        "rss_after_mb": round(rss_after, 2),
        "solvers": solvers
    }

def main():
    print("Fetching 18 delivery stops from backend...", flush=True)
    resp = requests.get(f"{BASE_URL}/api/delivery-stops?limit=25", timeout=30)
    resp.raise_for_status()
    raw_stops = resp.json().get("stops", [])
    print(f"Fetched {len(raw_stops)} stops.", flush=True)

    all_runs = []
    for i in range(1, 6):
        res = run_single_audit(i, raw_stops)
        if res:
            all_runs.append(res)
        time.sleep(5) # Cooldown between sequential runs

    with open("scripts/audit_5_runs_results.json", "w") as f:
        json.dump(all_runs, f, indent=2)
    print("\nSaved all 5 runs to scripts/audit_5_runs_results.json", flush=True)

if __name__ == "__main__":
    main()
