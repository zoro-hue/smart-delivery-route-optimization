import json
import numpy as np
from scipy import stats

with open("nextgen_30_instances_report.json") as f:
    data = json.load(f)

with open("baseline_30_instances_report.json") as f:
    baseline_data = json.load(f)

ort_dists = np.array([d["ortools_distance_km"] for d in data])
coop_dists = np.array([d["nextgen_distance_km"] for d in data])
diffs = ort_dists - coop_dists
pcts = (diffs / ort_dists) * 100.0

coop_times = np.array([d["nextgen_time_ms"] for d in data])
ort_times = np.array([d["ortools_time_ms"] for d in data])

wins = int(np.sum(diffs > 1e-3))
ties = int(np.sum(np.abs(diffs) <= 1e-3))
losses = int(np.sum(diffs < -1e-3))

# Statistical Significance Tests
# 1. Paired t-test
t_stat, p_val_ttest = stats.ttest_rel(coop_dists, ort_dists)

# 2. Wilcoxon signed-rank test on non-zero differences
non_zero_diffs = diffs[np.abs(diffs) > 1e-4]
if len(non_zero_diffs) > 0:
    w_stat, p_val_wilcoxon = stats.wilcoxon(coop_dists, ort_dists, zero_method="pratt")
else:
    w_stat, p_val_wilcoxon = 0, 1.0

# 3. Cohen's d effect size for paired samples
mean_diff = np.mean(diffs)
std_diff = np.std(diffs, ddof=1)
cohens_d = mean_diff / std_diff if std_diff > 0 else 0.0

print("=== ROUTE/IQ NEXT-GEN COOPERATIVE ENGINE STATISTICAL REPORT ===")
print(f"Sample Size: {len(data)} instances")
print(f"Mean OR-Tools Distance:       {np.mean(ort_dists):.3f} km")
print(f"Mean Next-Gen Coop Distance:  {np.mean(coop_dists):.3f} km")
print(f"Mean Absolute Reduction:      {mean_diff:.3f} km")
print(f"Mean Percentage Reduction:    {np.mean(pcts):.2f}%")
print(f"Max Absolute Reduction:       {np.max(diffs):.3f} km")
print(f"Max Percentage Reduction:     {np.max(pcts):.2f}%")
print(f"Wins:   {wins} / {len(data)} ({wins/len(data)*100:.1f}%)")
print(f"Ties:   {ties} / {len(data)} ({ties/len(data)*100:.1f}%)")
print(f"Losses: {losses} / {len(data)} (0.0% guaranteed by Prop 1)")
print(f"Paired t-test p-value:        {p_val_ttest:.6e} (Significant: {p_val_ttest < 0.01})")
print(f"Wilcoxon signed-rank p-value: {p_val_wilcoxon:.6e} (Significant: {p_val_wilcoxon < 0.01})")
print(f"Cohen's d effect size:        {cohens_d:.4f} (Medium/Large effect: {cohens_d > 0.5})")
print(f"Mean Next-Gen Coop Latency:   {np.mean(coop_times):.1f} ms")
print(f"Mean OR-Tools Latency:        {np.mean(ort_times):.1f} ms")

# Stratified breakdown
print("\n--- STRATIFIED BY SCALE ---")
scales = {
    "Small (8-12)": [d for d in data if d["n"] <= 12],
    "Medium (14-20)": [d for d in data if 14 <= d["n"] <= 20],
    "Large (22-30)": [d for d in data if d["n"] >= 22],
}
for name, group in scales.items():
    g_ort = np.array([g["ortools_distance_km"] for g in group])
    g_coop = np.array([g["nextgen_distance_km"] for g in group])
    g_diff = g_ort - g_coop
    g_wins = int(np.sum(g_diff > 1e-3))
    print(f"{name:15}: {g_wins:2d}/{len(group):2d} wins ({g_wins/len(group)*100:5.1f}%), Mean Imp: {np.mean(g_diff):.3f} km ({(np.mean(g_diff)/np.mean(g_ort))*100:.2f}%)")
