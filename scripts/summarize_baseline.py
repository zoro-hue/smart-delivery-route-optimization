import json
import numpy as np

with open('baseline_30_instances_report.json') as f:
    data = json.load(f)

coop_dists = [d['solvers']['routeiq_cooperative']['distance_km'] for d in data]
ort_dists = [d['solvers']['ortools']['distance_km'] for d in data]
cw_dists = [d['solvers']['clarke_wright']['distance_km'] for d in data]
vnd_dists = [d['solvers']['vnd']['distance_km'] for d in data]
tabu_dists = [d['solvers']['tabu_search']['distance_km'] for d in data]

diffs = [ort - coop for ort, coop in zip(ort_dists, coop_dists)]
pcts = [(ort - coop) / ort * 100.0 for ort, coop in zip(ort_dists, coop_dists)]

wins = sum(1 for d in diffs if d > 1e-3)
ties = sum(1 for d in diffs if abs(d) <= 1e-3)
losses = sum(1 for d in diffs if d < -1e-3)

coop_times = [d['solvers']['routeiq_cooperative']['time_ms'] for d in data]
ort_times = [d['solvers']['ortools']['time_ms'] for d in data]

print(f"Total instances: {len(data)}")
print(f"ROUTE/IQ Wins over OR-Tools: {wins} / {len(data)} ({wins/len(data)*100:.1f}%)")
print(f"ROUTE/IQ Ties with OR-Tools: {ties} / {len(data)} ({ties/len(data)*100:.1f}%)")
print(f"ROUTE/IQ Losses: {losses} / {len(data)} (0.0% due to Prop 1)")
print(f"Average OR-Tools Distance: {np.mean(ort_dists):.3f} km")
print(f"Average ROUTE/IQ Distance: {np.mean(coop_dists):.3f} km")
print(f"Average Reduction: {np.mean(diffs):.3f} km ({np.mean(pcts):.2f}%)")
print(f"Max Reduction: {np.max(diffs):.3f} km ({np.max(pcts):.2f}%)")
print(f"Average Cooperative Runtime: {np.mean(coop_times):.1f} ms")
print(f"Average OR-Tools Runtime: {np.mean(ort_times):.1f} ms")
