import requests
import json
import time
import os

BASE_URL = "https://route-iq-backend.onrender.com"
EVIDENCE_DIR = r"C:\Users\DELL\.gemini\antigravity\brain\aba14f7b-722c-4648-8da1-214dc979ac26\production_evidence"
os.makedirs(EVIDENCE_DIR, exist_ok=True)

def get_mem():
    try:
        r = requests.get(f"{BASE_URL}/api/system/memory", timeout=20)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"Memory check err: {e}", flush=True)
    return {}

def fetch_canonical_18_stops():
    r = requests.get(f"{BASE_URL}/api/delivery-stops?limit=25", timeout=30)
    r.raise_for_status()
    stops = r.json().get("stops", [])
    print(f"Fetched {len(stops)} stops from backend.", flush=True)
    return stops

def run_single_solver(algo_name, stops):
    print(f"\n--- Testing Single Solver: {algo_name} ---", flush=True)
    m_before = get_mem()
    rss_before = m_before.get("process_rss_mb", 0.0)
    print(f"RSS before {algo_name}: {rss_before:.2f} MB", flush=True)

    payload = {
        "selection_mode": "custom",
        "selected_algorithms": [algo_name],
        "custom_customers": stops,
        "num_customers": len(stops),
        "num_vehicles": 3,
        "vehicle_capacity": 1000.0,
        "depot_lat": 40.7128,
        "depot_lon": -74.0060,
        "classical_time_limit_sec": 1,
    }

    t0 = time.time()
    res = requests.post(f"{BASE_URL}/api/optimization/jobs", json=payload, timeout=40)
    res.raise_for_status()
    job_data = res.json()
    init_time = time.time() - t0
    job_id = job_data.get("job_id")

    # Poll until terminal
    final_data = None
    peak_rss = rss_before
    for _ in range(15):
        time.sleep(2)
        m = get_mem()
        crss = m.get("process_rss_mb", 0.0)
        if crss > peak_rss:
            peak_rss = crss
        sr = requests.get(f"{BASE_URL}/api/optimization/jobs/{job_id}/status", timeout=20)
        if sr.status_code == 200:
            final_data = sr.json()
            if final_data.get("status") in ["COMPLETED", "PARTIAL", "FAILED"]:
                break

    total_time = time.time() - t0
    time.sleep(4)
    m_after = get_mem()
    rss_after = m_after.get("process_rss_mb", 0.0)

    algo_res = final_data.get("results", {}).get(algo_name, {})
    dist = algo_res.get("total_distance_km")
    feas = algo_res.get("is_feasible")

    print(f"Result {algo_name}: dist={dist} km, feasible={feas}, time={total_time:.2f}s | Peak RSS: {peak_rss:.2f} MB, Post RSS: {rss_after:.2f} MB", flush=True)
    return {
        "algo": algo_name,
        "job_id": job_id,
        "distance_km": dist,
        "feasible": feas,
        "init_time_s": round(init_time, 2),
        "total_time_s": round(total_time, 2),
        "rss_before_mb": round(rss_before, 2),
        "peak_rss_mb": round(peak_rss, 2),
        "rss_after_mb": round(rss_after, 2),
        "algo_details": algo_res
    }

def run_comparison_job(run_idx, stops):
    print(f"\n==================== COMPARISON RUN {run_idx}/5 ====================", flush=True)
    m_before = get_mem()
    rss_before = m_before.get("process_rss_mb", 0.0)
    print(f"[{run_idx}] Baseline RSS before run: {rss_before:.2f} MB (Headroom: {m_before.get('render_headroom_mb', 0):.2f} MB)", flush=True)

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
    res = requests.post(f"{BASE_URL}/api/optimization/jobs", json=payload, timeout=45)
    res.raise_for_status()
    start_data = res.json()
    init_time = time.time() - t0
    job_id = start_data.get("job_id")
    primary_algo = start_data.get("primary_algorithm", "routeiq_cooperative")
    primary_dist = start_data.get("results", {}).get(primary_algo, {}).get("total_distance_km")

    print(f"[{run_idx}] Job {job_id} launched in {init_time:.2f}s | Primary: {primary_algo} ({primary_dist} km)", flush=True)

    peak_rss = rss_before
    final_data = None

    for poll in range(40):
        time.sleep(3)
        m = get_mem()
        crss = m.get("process_rss_mb", 0.0)
        if crss > peak_rss:
            peak_rss = crss

        try:
            sr = requests.get(f"{BASE_URL}/api/optimization/jobs/{job_id}/status", timeout=25)
            if sr.status_code == 200:
                final_data = sr.json()
                st = final_data.get("status")
                c_cnt = final_data.get("completed_algorithms", 0)
                tot = final_data.get("total_algorithms", 0)
                plabel = final_data.get("progress_label", "")
                elapsed = round(time.time() - t0, 1)
                print(f"[{run_idx} @ {elapsed}s] Status={st} | {plabel} | Solvers={c_cnt}/{tot} | RSS={crss:.2f} MB", flush=True)
                if st in ["COMPLETED", "FAILED", "CANCELLED"] or (tot > 0 and c_cnt >= tot):
                    break
        except Exception as pe:
            print(f"[{run_idx}] Polling note: {pe}", flush=True)

    total_time = time.time() - t0
    print(f"[{run_idx}] Job completed in {total_time:.2f}s with status '{final_data.get('status')}'", flush=True)

    # Cooldown and memory reading
    time.sleep(6)
    m_after = get_mem()
    rss_after = m_after.get("process_rss_mb", 0.0)
    print(f"[{run_idx}] Post-job RSS: {rss_after:.2f} MB (Delta: {rss_after - rss_before:+.2f} MB, Headroom: {m_after.get('render_headroom_mb', 0):.2f} MB)", flush=True)

    # Detailed solver verification
    solvers_summary = {}
    distinct_distances = set()
    all_served_ok = True

    for aname, ares in final_data.get("results", {}).items():
        d_val = ares.get("total_distance_km")
        if d_val:
            distinct_distances.add(round(float(d_val), 1))
        
        # Check visited stops
        visited = set()
        for r in ares.get("routes", []):
            for s in r.get("customer_stops", []):
                visited.add(s)
        
        # If stop coverage is in customer_stops or stops list
        if len(visited) == 0:
            for r in ares.get("routes", []):
                for s in r.get("stops", []):
                    if s != 0:
                        visited.add(s)

        solvers_summary[aname] = {
            "status": ares.get("status"),
            "distance_km": d_val,
            "execution_time_sec": ares.get("execution_time_sec"),
            "is_feasible": ares.get("is_feasible"),
            "stops_served": len(visited),
            "algorithm_name": ares.get("algorithm_name"),
            "category": ares.get("category"),
            "compute_type": ares.get("compute_type"),
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
        "num_solvers": len(solvers_summary),
        "distinct_distances_count": len(distinct_distances),
        "solvers": solvers_summary
    }

def main():
    print("=================================================================", flush=True)
    print("ROUTE/IQ INDEPENDENT PRODUCTION VERIFICATION & AUDIT SUITE", flush=True)
    print("=================================================================", flush=True)

    stops = fetch_canonical_18_stops()

    audit_results = {
        "environment": {
            "backend_url": BASE_URL,
            "frontend_url": "https://route-iq-frontend-nine.vercel.app/",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "git_commit": "81cc541",
        },
        "phase_a_single_solvers": {},
        "phase_b_sequential_runs": []
    }

    # Phase A: Single Solvers (OR-Tools vs ROUTE/IQ Cooperative)
    ortools_res = run_single_solver("ortools", stops)
    audit_results["phase_a_single_solvers"]["ortools"] = ortools_res
    time.sleep(5)

    coop_res = run_single_solver("routeiq_cooperative", stops)
    audit_results["phase_a_single_solvers"]["routeiq_cooperative"] = coop_res
    time.sleep(5)

    # Phase B: 5 Sequential 18-stop comparison runs
    print("\n--- Starting 5 Sequential Comparison Runs ---", flush=True)
    for i in range(1, 6):
        c_res = run_comparison_job(i, stops)
        audit_results["phase_b_sequential_runs"].append(c_res)
        time.sleep(6) # Safe pause between jobs to verify GC and prevent CPU spikes

    out_file = os.path.join(EVIDENCE_DIR, "audit_5_runs_detailed.json")
    with open(out_file, "w") as f:
        json.dump(audit_results, f, indent=2)
    print(f"\nAUDIT SUITE COMPLETE! Saved detailed results to {out_file}", flush=True)

if __name__ == "__main__":
    main()
