import json

with open('energy_benchmark_report.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

for p in ['diesel', 'petrol', 'hybrid', 'electric']:
    print(f"=== {p.upper()} VAN (30 Benchmark Instances Average) ===")
    algos = d['results_by_propulsion'][p]['algorithms']
    print(f"{'Algorithm':<22} | {'Dist(km)':<8} | {'Energy(kWh)':<11} | {'CO2(kg)':<8} | {'Cost($)':<7} | {'Savings vs OR-Tools':<22}")
    print('-'*90)
    for a, vals in algos.items():
        sign = '+' if vals['pct_energy_savings_vs_ortools'] > 0 else ''
        print(f"{a:<22} | {vals['avg_distance_km']:>8.2f} | {vals['avg_energy_kwh']:>11.2f} | {vals['avg_total_co2_kg']:>8.3f} | {vals['avg_cost_usd']:>7.2f} | {sign}{vals['pct_energy_savings_vs_ortools']:>5.2f}% ({sign}{vals['delta_energy_kwh_vs_ortools']:>5.2f} kWh)")
    print()
