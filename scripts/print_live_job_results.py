import requests
import json

url = 'https://route-iq-backend.onrender.com/api/optimization/jobs/2c9d8ae0-1d2e-44a3-a883-6f969297446c/status'
r = requests.get(url, timeout=15)
data = r.json()

print('================================================================')
print(f"LIVE RENDER PRODUCTION JOB: {data['job_id']}")
print(f"Status: {data['status']} | Label: {data['progress_label']}")
print(f"Completed: {data['completed_algorithms']}/{data['total_algorithms']}")
print('================================================================')
print(f"{'Algorithm':<25} | {'Status':<10} | {'Distance (km)':<13} | {'Time (s)':<8} | {'Served':<6}")
print('----------------------------------------------------------------')

results = data.get('results', {})
statuses = data.get('solver_statuses', {})

for algo_id in data.get('selected_algorithms', []):
    res = results.get(algo_id, {})
    st = statuses.get(algo_id, 'unknown')
    dist = res.get('total_distance_km', 0.0)
    exec_t = res.get('execution_time_sec', 0.0)
    served = res.get('served_customers', 0)
    print(f"{algo_id:<25} | {st:<10} | {dist:<13.3f} | {exec_t:<8.3f} | {served:<6}")

print('================================================================')
best = data.get('comparison_summary', {})
print(f"Best Algorithm: {best.get('best_algorithm_name')} ({best.get('best_feasible_distance_km')} km)")
print(f"Reason: {best.get('best_reason')}")
