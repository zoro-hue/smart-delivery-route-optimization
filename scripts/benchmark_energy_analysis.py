"""
Comprehensive Empirical Benchmark: Energy Consumption & Carbon Abatement.
Evaluates all 11 ROUTE/IQ algorithms on 30 benchmark instances across:
- Diesel Light Commercial Van
- Petrol Urban Delivery Van
- Hybrid Electric Van
- Battery Electric Delivery Van (EV)

Computes:
- Thermal & electrical energy (kWh)
- Fuel consumption (L)
- Direct tailpipe CO2 vs upstream power generation CO2 (kg)
- Operational economic costs ($ USD)
- Savings % vs OR-Tools baseline
"""

import os
import sys
import json

sys.path.insert(0, os.path.abspath('backend'))

from app.services.optimization.energy_service import (
    PROPULSION_MODELS,
    compute_algorithm_energy_profile,
    compute_energy_comparison,
)

def run_energy_benchmark():
    with open('baseline_30_instances_report.json', 'r', encoding='utf-8') as f:
        baseline_instances = json.load(f)

    nextgen_map = {}
    if os.path.exists('nextgen_30_instances_report.json'):
        with open('nextgen_30_instances_report.json', 'r', encoding='utf-8') as f:
            for item in json.load(f):
                nextgen_map[item['instance_id']] = item['nextgen_distance_km']

    all_algorithms = [
        'routeiq_cooperative',
        'ortools',
        'clarke_wright',
        'vnd',
        'tabu_search',
        'two_opt',
        'kernighan_lin',
        'qiga',
        'qaoa',
        'astar',
        'dijkstra',
    ]

    propulsion_types = ['diesel', 'petrol', 'hybrid', 'electric']
    results_by_propulsion = {}

    for p_type in propulsion_types:
        model = PROPULSION_MODELS[p_type]
        algo_aggregates = {a: {'dist': 0.0, 'fuel': 0.0, 'kwh': 0.0, 'co2': 0.0, 'cost': 0.0, 'feasible_count': 0} for a in all_algorithms}

        for inst in baseline_instances:
            inst_id = inst['instance_id']
            solvers = inst.get('solvers', {})

            for a_key in all_algorithms:
                solver_data = solvers.get(a_key, {})
                dist = solver_data.get('distance_km', solver_data.get('total_distance_km', 0.0))
                # If next-gen cooperative engine result is available, use it
                if a_key == 'routeiq_cooperative' and inst_id in nextgen_map:
                    dist = nextgen_map[inst_id]

                dur = solver_data.get('time_ms', 0.0) / 1000.0 / 60.0  # min
                feas = solver_data.get('feasible', solver_data.get('is_feasible', True))

                # Format minimal payload for energy profile calculation
                mock_algo_data = {
                    'total_distance_km': dist,
                    'total_duration_min': dur,
                    'is_feasible': feas,
                    'routes': solver_data.get('routes', []),
                }

                prof = compute_algorithm_energy_profile(
                    algo_key=a_key,
                    algo_data=mock_algo_data,
                    propulsion_type=p_type,
                    vehicle_capacity=100.0,
                    traffic_factor=1.0,
                )

                algo_aggregates[a_key]['dist'] += prof['total_distance_km']
                algo_aggregates[a_key]['fuel'] += prof['fuel_consumption_litres']
                algo_aggregates[a_key]['kwh'] += prof['energy_consumption_kwh']
                algo_aggregates[a_key]['co2'] += prof['total_co2_kg']
                algo_aggregates[a_key]['cost'] += prof['operational_cost_usd']
                if feas:
                    algo_aggregates[a_key]['feasible_count'] += 1

        n = len(baseline_instances)
        table = {}
        ortools_avg = {
            'dist': algo_aggregates['ortools']['dist'] / n,
            'kwh': algo_aggregates['ortools']['kwh'] / n,
            'co2': algo_aggregates['ortools']['co2'] / n,
            'cost': algo_aggregates['ortools']['cost'] / n,
        }

        for a_key in all_algorithms:
            avg_dist = round(algo_aggregates[a_key]['dist'] / n, 2)
            avg_fuel = round(algo_aggregates[a_key]['fuel'] / n, 3)
            avg_kwh = round(algo_aggregates[a_key]['kwh'] / n, 2)
            avg_co2 = round(algo_aggregates[a_key]['co2'] / n, 3)
            avg_cost = round(algo_aggregates[a_key]['cost'] / n, 2)

            delta_kwh = round(ortools_avg['kwh'] - avg_kwh, 2)
            pct_kwh = round((delta_kwh / ortools_avg['kwh']) * 100.0, 2)
            delta_co2 = round(ortools_avg['co2'] - avg_co2, 3)
            delta_cost = round(ortools_avg['cost'] - avg_cost, 2)

            table[a_key] = {
                'avg_distance_km': avg_dist,
                'avg_fuel_litres': avg_fuel,
                'avg_energy_kwh': avg_kwh,
                'avg_total_co2_kg': avg_co2,
                'avg_cost_usd': avg_cost,
                'delta_energy_kwh_vs_ortools': delta_kwh,
                'pct_energy_savings_vs_ortools': pct_kwh,
                'delta_co2_kg_vs_ortools': delta_co2,
                'delta_cost_usd_vs_ortools': delta_cost,
                'feasible_instances': algo_aggregates[a_key]['feasible_count'],
            }

        results_by_propulsion[p_type] = {
            'propulsion': p_type,
            'name': model['name'],
            'unit': model['unit_label'],
            'algorithms': table,
        }

    report = {
        'benchmark_dataset': '30 Realistic NYC Benchmark Instances (10-25 stops, 2-4 vehicles)',
        'results_by_propulsion': results_by_propulsion,
    }

    with open('energy_benchmark_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print("Energy Benchmark Successfully Generated!")
    print("\n=== SUMMARY: Cooperative Engine vs OR-Tools (Diesel Van) ===")
    d_coop = results_by_propulsion['diesel']['algorithms']['routeiq_cooperative']
    d_ort = results_by_propulsion['diesel']['algorithms']['ortools']
    print(f"ROUTE/IQ Coop Distance: {d_coop['avg_distance_km']} km | OR-Tools: {d_ort['avg_distance_km']} km")
    print(f"Energy: {d_coop['avg_energy_kwh']} kWh vs {d_ort['avg_energy_kwh']} kWh ({d_coop['pct_energy_savings_vs_ortools']}% saved)")
    print(f"CO2 Avoided: {d_coop['delta_co2_kg_vs_ortools']} kg CO2 per trip")
    print(f"Cost Saved: ${d_coop['delta_cost_usd_vs_ortools']} per trip")

    print("\n=== SUMMARY: Cooperative Engine vs OR-Tools (Electric EV) ===")
    ev_coop = results_by_propulsion['electric']['algorithms']['routeiq_cooperative']
    ev_ort = results_by_propulsion['electric']['algorithms']['ortools']
    print(f"Energy: {ev_coop['avg_energy_kwh']} kWh vs {ev_ort['avg_energy_kwh']} kWh ({ev_coop['pct_energy_savings_vs_ortools']}% saved)")
    print(f"Lifecycle Grid CO2: {ev_coop['avg_total_co2_kg']} kg vs {ev_ort['avg_total_co2_kg']} kg")
    print(f"EV Cost Saved: ${ev_coop['delta_cost_usd_vs_ortools']} per trip")

if __name__ == '__main__':
    run_energy_benchmark()
