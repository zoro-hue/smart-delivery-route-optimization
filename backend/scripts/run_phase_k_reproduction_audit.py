"""
Phase K: Independent Reproduction Audit & Statistical Re-Analysis Script.

Recomputes all benchmark metrics and statistical hypothesis tests directly from raw CSV data:
  - scratch/phase6_benchmark/phase_i_qgar_benchmark_raw.csv
  - scratch/phase6_benchmark/dual_pillar_benchmark_raw.csv
  - scratch/phase6_benchmark/bigdata_scaling_results.csv

Outputs:
  - scratch/phase_k_reproduction/reproduction_summary_tables.csv
  - scratch/phase_k_reproduction/reproduction_statistical_tests.csv
  - scratch/phase_k_reproduction/reproduction_audit_report.json
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from scipy import stats

def compute_rank_biserial(w_pos, w_neg):
    total = w_pos + w_neg
    if total == 0:
        return 0.0
    return (w_pos - w_neg) / total

def bootstrap_ci_mean_diff(diffs, n_boot=10000, alpha=0.05, seed=42):
    rng = np.random.default_rng(seed)
    boot_means = [np.mean(rng.choice(diffs, size=len(diffs), replace=True)) for _ in range(n_boot)]
    low = np.percentile(boot_means, 100 * (alpha / 2))
    high = np.percentile(boot_means, 100 * (1 - alpha / 2))
    return float(low), float(high)

def run_reproduction_audit():
    print("=" * 80)
    print("ROUTE/IQ — PHASE K: INDEPENDENT REPRODUCTION & STATISTICAL AUDIT")
    print("=" * 80)

    raw_path_phase_i = r"C:\Users\DELL\.gemini\antigravity\brain\aba14f7b-722c-4648-8da1-214dc979ac26\scratch\phase6_benchmark\phase_i_qgar_benchmark_raw.csv"
    if not os.path.exists(raw_path_phase_i):
        raw_path_phase_i = r"scratch/phase6_benchmark/phase_i_qgar_benchmark_raw.csv"

    raw_path_bigdata = r"C:\Users\DELL\.gemini\antigravity\brain\aba14f7b-722c-4648-8da1-214dc979ac26\scratch\phase6_benchmark\bigdata_scaling_results.csv"
    if not os.path.exists(raw_path_bigdata):
        raw_path_bigdata = r"scratch/phase6_benchmark/bigdata_scaling_results.csv"

    df_raw = pd.read_csv(raw_path_phase_i)
    df_bigdata = pd.read_csv(raw_path_bigdata)

    out_dir = r"scratch/phase_k_reproduction"
    os.makedirs(out_dir, exist_ok=True)

    # -------------------------------------------------------------
    # 1. Summary Tables Recomputed from Raw Data
    # -------------------------------------------------------------
    print("\n[1] Recomputing Algorithm Aggregates from Raw Records...")
    summary = df_raw.groupby(["N", "algorithm"]).agg(
        sample_count=("total_distance_km", "count"),
        mean_dist_km=("total_distance_km", "mean"),
        std_dist_km=("total_distance_km", "std"),
        median_dist_km=("total_distance_km", "median"),
        min_dist_km=("total_distance_km", "min"),
        max_dist_km=("total_distance_km", "max"),
        mean_runtime_ms=("runtime_total_ms", "mean"),
        mean_spark_ms=("runtime_spark_ms", "mean"),
        mean_qaoa_ms=("runtime_qaoa_circuit_ms", "mean"),
        mean_lambda=("lambda_mean", "mean"),
        total_qaoa_accepted=("qaoa_accepted", "sum"),
        total_spatial_retained=("spatial_retained", "sum"),
        total_crossings_prevented=("crossings_prevented", "sum")
    ).reset_index()

    summary_csv = os.path.join(out_dir, "reproduction_summary_tables.csv")
    summary.to_csv(summary_csv, index=False)
    print(f"  Summary table saved to {summary_csv}")
    print(summary[["N", "algorithm", "sample_count", "mean_dist_km", "std_dist_km"]].to_string())

    # -------------------------------------------------------------
    # 2. Rigorous Inferential Statistics & Hypothesis Testing
    # -------------------------------------------------------------
    print("\n[2] Performing Paired Hypothesis Testing & Effect Size Estimation...")
    # Evaluate scales N in [10, 25, 50, 100] with paired complete blocks
    df_eval = df_raw[df_raw["N"].isin([10, 25, 50, 100])].copy()
    piv = df_eval.pivot(index=["N", "seed"], columns="algorithm", values="total_distance_km")

    target_algo = "Full QGAR (Proposed)"
    baselines = [
        ("Spatial Baseline (No QAOA)", "greater"),      # H1: Spatial > QGAR (QGAR is shorter)
        ("Phase H (Spark + QAOA)", "greater"),          # H1: Phase H > QGAR (QGAR is shorter)
        ("OR-Tools GLS", "two-sided"),
        ("Clarke-Wright + 2-opt", "two-sided"),
        ("RB-QCD Baseline", "two-sided")
    ]

    stat_records = []
    p_values_for_fdr = []

    for base_name, alt in baselines:
        # Global test across all 20 paired instances
        y_qgar = piv[target_algo].values
        y_base = piv[base_name].values
        diffs = y_base - y_qgar  # positive means base is larger (QGAR is better)

        wins = int(np.sum(diffs > 1e-4))
        losses = int(np.sum(diffs < -1e-4))
        ties = int(np.sum(np.abs(diffs) <= 1e-4))

        # Wilcoxon signed-rank test
        # Note: handle zero differences by extracting non-zero ranks
        non_zero_diffs = diffs[np.abs(diffs) > 1e-4]
        if len(non_zero_diffs) > 0:
            w_res = stats.wilcoxon(y_base, y_qgar, alternative=alt)
            w_stat = float(w_res.statistic)
            p_val = float(w_res.pvalue)

            # Rank biserial calculation
            # Rank magnitudes
            ranks = stats.rankdata(np.abs(non_zero_diffs))
            w_pos = np.sum(ranks[non_zero_diffs > 0])
            w_neg = np.sum(ranks[non_zero_diffs < 0])
            r_b = compute_rank_biserial(w_pos, w_neg)
        else:
            w_stat = 0.0
            p_val = 1.0
            r_b = 0.0

        low_ci, high_ci = bootstrap_ci_mean_diff(diffs)
        pct_diffs = (y_qgar - y_base) / y_base * 100.0

        rec_global = {
            "comparison": f"QGAR vs {base_name} (Global N=10-100)",
            "scale_N": "10-100 (All)",
            "sample_size": len(diffs),
            "wins": wins,
            "losses": losses,
            "ties": ties,
            "mean_diff_km": round(float(np.mean(diffs)), 4),
            "median_diff_km": round(float(np.median(diffs)), 4),
            "std_diff_km": round(float(np.std(diffs, ddof=1)), 4),
            "mean_pct_change": round(float(np.mean(pct_diffs)), 2),
            "ci_95_low_km": round(low_ci, 4),
            "ci_95_high_km": round(high_ci, 4),
            "wilcoxon_stat": round(w_stat, 1),
            "p_value": p_val,
            "effect_size_rb": round(r_b, 3)
        }
        stat_records.append(rec_global)
        p_values_for_fdr.append(p_val)

        # Scale-by-scale breakdown
        for n_val in [10, 25, 50, 100]:
            sub_piv = piv.loc[n_val]
            y_qg_n = sub_piv[target_algo].values
            y_bs_n = sub_piv[base_name].values
            d_n = y_bs_n - y_qg_n

            w_n = int(np.sum(d_n > 1e-4))
            l_n = int(np.sum(d_n < -1e-4))
            t_n = int(np.sum(np.abs(d_n) <= 1e-4))

            nz_n = d_n[np.abs(d_n) > 1e-4]
            if len(nz_n) > 0:
                res_n = stats.wilcoxon(y_bs_n, y_qg_n, alternative=alt)
                w_stat_n = float(res_n.statistic)
                p_val_n = float(res_n.pvalue)
                ranks_n = stats.rankdata(np.abs(nz_n))
                r_b_n = compute_rank_biserial(np.sum(ranks_n[nz_n > 0]), np.sum(ranks_n[nz_n < 0]))
            else:
                w_stat_n = 0.0
                p_val_n = 1.0
                r_b_n = 0.0

            low_n, high_n = bootstrap_ci_mean_diff(d_n)
            pct_n = (y_qg_n - y_bs_n) / y_bs_n * 100.0

            rec_n = {
                "comparison": f"QGAR vs {base_name}",
                "scale_N": str(n_val),
                "sample_size": len(d_n),
                "wins": w_n,
                "losses": l_n,
                "ties": t_n,
                "mean_diff_km": round(float(np.mean(d_n)), 4),
                "median_diff_km": round(float(np.median(d_n)), 4),
                "std_diff_km": round(float(np.std(d_n, ddof=1)), 4),
                "mean_pct_change": round(float(np.mean(pct_n)), 2),
                "ci_95_low_km": round(low_n, 4),
                "ci_95_high_km": round(high_n, 4),
                "wilcoxon_stat": round(w_stat_n, 1),
                "p_value": p_val_n,
                "effect_size_rb": round(r_b_n, 3)
            }
            stat_records.append(rec_n)

    # Benjamini-Hochberg FDR adjustments
    df_stats = pd.DataFrame(stat_records)
    # Apply FDR across the scale-specific confirmatory comparisons for Spatial and Phase H
    confirmatory_mask = df_stats["comparison"].str.contains("Spatial|Phase H") & (df_stats["scale_N"] != "10-100 (All)")
    conf_p = df_stats.loc[confirmatory_mask, "p_value"].values
    sorted_indices = np.argsort(conf_p)
    m_tests = len(conf_p)
    adj_p = np.zeros(m_tests)
    for i, idx in enumerate(sorted_indices):
        rank = i + 1
        adj_p[idx] = min(1.0, conf_p[idx] * (m_tests / rank))

    # Enforce monotonicity of adjusted p-values
    for i in range(m_tests - 2, -1, -1):
        idx = sorted_indices[i]
        next_idx = sorted_indices[i + 1]
        adj_p[idx] = min(adj_p[idx], adj_p[next_idx])

    df_stats["fdr_adjusted_p"] = np.nan
    df_stats.loc[confirmatory_mask, "fdr_adjusted_p"] = np.round(adj_p, 4)

    stats_csv = os.path.join(out_dir, "reproduction_statistical_tests.csv")
    df_stats.to_csv(stats_csv, index=False)
    print(f"  Statistical test results saved to {stats_csv}")
    print(df_stats[["comparison", "scale_N", "mean_pct_change", "wins", "ties", "p_value", "fdr_adjusted_p"]].to_string())

    # -------------------------------------------------------------
    # 3. Big Data Scaling Verification
    # -------------------------------------------------------------
    print("\n[3] Auditing Big Data Scaling Results...")
    print(df_bigdata.to_string())

    audit_json = os.path.join(out_dir, "reproduction_audit_report.json")
    with open(audit_json, "w") as f:
        json.dump({
            "verified_runs_phase_i": len(df_raw),
            "verified_runs_bigdata": len(df_bigdata),
            "monotonic_non_degradation_held_all": bool(np.all(piv[target_algo] <= piv["Spatial Baseline (No QAOA)"] + 1e-4)),
            "qgar_vs_spatial_global_p": float(df_stats.loc[0, "p_value"]),
            "qgar_vs_phase_h_global_p": float(df_stats.loc[5, "p_value"]),
            "customer_preservation_100pct": bool(np.all(df_raw["unassigned_customers"] == 0)),
            "capacity_compliance_100pct": bool(np.all(df_raw["capacity_violations"] == 0))
        }, f, indent=2)

    print(f"\nReproduction audit report successfully saved to {audit_json}")


if __name__ == "__main__":
    run_reproduction_audit()

