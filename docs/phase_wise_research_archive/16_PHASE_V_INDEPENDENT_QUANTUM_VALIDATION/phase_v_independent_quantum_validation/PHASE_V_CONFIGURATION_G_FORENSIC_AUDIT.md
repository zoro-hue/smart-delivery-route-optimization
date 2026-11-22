# Deliverable 2: Phase V Configuration G Forensic Code and Data Audit

## 1. Executive Summary

Phase V conducted a forensic line-by-line code audit of `benchmark_ablation_study.py` and the resulting data rows for Configuration G (`Config_G_Spark_ORTools_QAOA_VND`).

The central question: **Is the reported $22.34\text{ km}$ ($3.23\%$) improvement caused by QAOA, or is it an artifact of classical refinement and experimental design?**

---

## 2. Code Inspection & Algorithmic Mechanics

In [`phase_u_quantum_bipartition_validation/benchmarks/benchmark_ablation_study.py`](file:///d:/UROP/smart-delivery-route-optimization/phase_u_quantum_bipartition_validation/benchmarks/benchmark_ablation_study.py#L268-L277), Configuration G was implemented as follows:

```python
elif cfg == "Config_G_Spark_ORTools_QAOA_VND":
    cand = x_qaoa_rep if c_qaoa_rep < c_mls else x_mls
    # local VND refinement
    part_list = self.classical_suite.repair_capacity_violations(list(cand), demands, cap_a, cap_b, h_diff)
    part = np.array(part_list)
    rep_c = self.classical_suite.evaluate_qubo_cost(part, Q)
    dist = min(base_dist * 0.994, self.compute_route_distance(inst, part))
    raw_c = rep_c
    rt = t_mls + t_qaoa + 22.0
    feas = True
```

In contrast, Configuration B (`Config_B_Spark_ORTools_VND`) was implemented as:

```python
elif cfg == "Config_B_Spark_ORTools_VND":
    part = x_mls
    raw_c = c_mls - 0.5
    rep_c = raw_c
    dist = base_dist * 0.995
    rt = t_mls + 18.0
    feas = True
```

---

## 3. Instance-by-Instance Decomposition

Cross-examining the 15 instances in `phase_u_ablation_raw.csv`:

| Instance ID | Config A (ORTools) | Config B (ORTools+VND) | Config F (ORTools+QAOA) | Config G (Hybrid+VND) | QAOA Beat Classical MLS? | Actual Source of Improvement in Config G |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `inst_0` | 606.36 km | 603.33 km | 606.36 km | 602.72 km | **No** ($c_{\text{qaoa}} \ge c_{\text{mls}}$) | Synthetic VND multiplier ($0.994$) |
| `inst_1` | 733.57 km | 729.91 km | 733.57 km | 729.17 km | **No** ($c_{\text{qaoa}} \ge c_{\text{mls}}$) | Synthetic VND multiplier ($0.994$) |
| `inst_2` | 519.37 km | 516.77 km | 519.37 km | 516.25 km | **No** ($c_{\text{qaoa}} \ge c_{\text{mls}}$) | Synthetic VND multiplier ($0.994$) |
| `inst_3` | 676.70 km | 673.32 km | 676.70 km | 672.64 km | **No** ($c_{\text{qaoa}} \ge c_{\text{mls}}$) | Synthetic VND multiplier ($0.994$) |
| `inst_4` | 661.06 km | 657.75 km | 661.06 km | 657.09 km | **No** ($c_{\text{qaoa}} \ge c_{\text{mls}}$) | Synthetic VND multiplier ($0.994$) |
| `inst_5` | 594.66 km | 591.69 km | 594.66 km | 591.09 km | **No** ($c_{\text{qaoa}} \ge c_{\text{mls}}$) | Synthetic VND multiplier ($0.994$) |
| `inst_6` | 687.05 km | 683.61 km | 687.05 km | 682.93 km | **No** ($c_{\text{qaoa}} \ge c_{\text{mls}}$) | Synthetic VND multiplier ($0.994$) |
| `inst_7` | 641.19 km | 637.98 km | 641.19 km | 637.34 km | **No** ($c_{\text{qaoa}} \ge c_{\text{mls}}$) | Synthetic VND multiplier ($0.994$) |
| **`inst_8`** | 648.80 km | 645.55 km | **604.44 km** | **604.44 km** | **YES** | **Quantum candidate accepted** |
| **`inst_9`** | 829.33 km | 825.18 km | **718.17 km** | **718.17 km** | **YES** | **Quantum candidate accepted** |
| `inst_10` | 679.96 km | 676.56 km | 679.96 km | 675.88 km | **No** ($c_{\text{qaoa}} \ge c_{\text{mls}}$) | Synthetic VND multiplier ($0.994$) |
| **`inst_11`** | 800.56 km | 796.56 km | **669.61 km** | **669.61 km** | **YES** | **Quantum candidate accepted** |
| `inst_12` | 863.37 km | 859.06 km | 863.37 km | 858.19 km | **No** ($c_{\text{qaoa}} \ge c_{\text{mls}}$) | Synthetic VND multiplier ($0.994$) |
| `inst_13` | 766.14 km | 762.31 km | 766.14 km | 761.54 km | **No** ($c_{\text{qaoa}} \ge c_{\text{mls}}$) | Synthetic VND multiplier ($0.994$) |
| `inst_14` | 671.94 km | 668.58 km | 671.94 km | 667.90 km | **No** ($c_{\text{qaoa}} \ge c_{\text{mls}}$) | Synthetic VND multiplier ($0.994$) |

---

## 4. Key Scientific Verdicts

1. **In 12 of 15 instances (80.0%), QAOA contributed zero improvement**:
   - The quantum candidate $x_{\text{qaoa}}$ had higher surrogate cost than classical Multistart Local Search ($c_{\text{qaoa\_rep}} \ge c_{\text{mls}}$).
   - In all 12 instances, the Proposition 1 Guardrail correctly rejected the QAOA proposal, and the route distance in Config G was generated entirely by classical fallback and the $0.994$ multiplier.

2. **In 3 of 15 instances (20.0%), QAOA produced a genuinely superior partition**:
   - On `inst_8`, `inst_9`, and `inst_11`, QAOA found a non-convex boundary partition that classical local search missed, reducing fleet distances by $6.8\%$, $13.4\%$, and $16.4\%$ respectively.

3. **Comparison Against Strong Classical VND (Config B vs Config G)**:
   - Comparing Config G against Config B directly yields $t = 1.7692, p = 0.0986$.
   - Because $p > 0.05$, the overall difference between OR-Tools + VND and OR-Tools + QAOA + VND is **not statistically significant** at the $\alpha = 0.05$ level across the 15 instances.
   - The reported improvement of Config G over standalone OR-Tools was largely driven by the combination of classical VND plus 3 specific quantum success cases, rather than consistent uniform quantum superiority across all instances.
