import sys, os, time
sys.path.insert(0, '.')
sys.path.insert(0, 'backend')
from app.services.road_network_service import road_network_service
from app.services.optimization.classical_solver import classical_solver
from phase_v_independent_quantum_validation.prototypes.algorithmic_vnd import AlgorithmicVND
import asyncio
from app.api.routes.optimization import get_delivery_stops
import numpy as np

road_network_service.ensure_loaded()
stops = asyncio.run(get_delivery_stops(limit=25))['stops']
depot = (40.7128, -74.0060)
locations = [depot] + [(s['lat'], s['lon']) for s in stops]
demands = [0] + [max(1, int(round(s.get('demand', 10)))) for s in stops]
d_mat, _, _ = road_network_service.build_road_matrix(locations)

# Test with 3 vehicles, capacity 100
caps = [100, 100, 100]
res_ort = classical_solver.solve_ortools(d_mat, 3, 0, demands, caps, 0.25)
routes = res_ort["routes"]
print("OR-Tools routes:")
for r in routes:
    print(f"  V{r['vehicle_id']}: {r['customer_stops']}, load={r['load']}, dist={r['distance_km']}")

# Check pairs of adjacent routes
for i in range(len(routes)):
    for j in range(i + 1, len(routes)):
        ra, rb = routes[i], routes[j]
        ta, tb = list(ra["customer_stops"]), list(rb["customer_stops"])
        if not ta or not tb:
            continue
        
        orig_dist = AlgorithmicVND.compute_tour_length(ta, d_mat, 0) + AlgorithmicVND.compute_tour_length(tb, d_mat, 0)
        print(f"\nExamining route pair ({ra['vehicle_id']}, {rb['vehicle_id']}): orig_dist = {orig_dist:.3f} km")
        
        # Test 1: Relocate moves
        best_ta, best_tb = list(ta), list(tb)
        best_d = orig_dist
        
        # Try moving each node from A to B
        for u in ta:
            new_ta = [x for x in ta if x != u]
            if sum(demands[x] for x in tb) + demands[u] <= caps[j]:
                # Test best insertion of u into tb
                for pos in range(len(tb) + 1):
                    cand_tb = tb[:pos] + [u] + tb[pos:]
                    # 2-opt optimize both
                    opt_a = AlgorithmicVND.run_2opt(new_ta, d_mat, 0)
                    opt_b = AlgorithmicVND.run_2opt(cand_tb, d_mat, 0)
                    cd = AlgorithmicVND.compute_tour_length(opt_a, d_mat, 0) + AlgorithmicVND.compute_tour_length(opt_b, d_mat, 0)
                    if cd < best_d - 1e-4:
                        print(f"  -> Relocate {u} from A to B improves: {best_d:.3f} -> {cd:.3f} km (delta: {best_d - cd:.3f} km)")
                        best_d = cd
                        best_ta, best_tb = opt_a, opt_b
                        
        # Try moving each node from B to A
        for v in tb:
            new_tb = [x for x in tb if x != v]
            if sum(demands[x] for x in ta) + demands[v] <= caps[i]:
                for pos in range(len(ta) + 1):
                    cand_ta = ta[:pos] + [v] + ta[pos:]
                    opt_a = AlgorithmicVND.run_2opt(cand_ta, d_mat, 0)
                    opt_b = AlgorithmicVND.run_2opt(new_tb, d_mat, 0)
                    cd = AlgorithmicVND.compute_tour_length(opt_a, d_mat, 0) + AlgorithmicVND.compute_tour_length(opt_b, d_mat, 0)
                    if cd < best_d - 1e-4:
                        print(f"  -> Relocate {v} from B to A improves: {best_d:.3f} -> {cd:.3f} km (delta: {best_d - cd:.3f} km)")
                        best_d = cd
                        best_ta, best_tb = opt_a, opt_b
                        
        # Try swapping u in A with v in B
        for u in ta:
            for v in tb:
                load_a = sum(demands[x] for x in ta) - demands[u] + demands[v]
                load_b = sum(demands[x] for x in tb) - demands[v] + demands[u]
                if load_a <= caps[i] and load_b <= caps[j]:
                    cand_ta = [v if x == u else x for x in ta]
                    cand_tb = [u if x == v else x for x in tb]
                    opt_a = AlgorithmicVND.run_2opt(cand_ta, d_mat, 0)
                    opt_b = AlgorithmicVND.run_2opt(cand_tb, d_mat, 0)
                    cd = AlgorithmicVND.compute_tour_length(opt_a, d_mat, 0) + AlgorithmicVND.compute_tour_length(opt_b, d_mat, 0)
                    if cd < best_d - 1e-4:
                        print(f"  -> Swap ({u}, {v}) improves: {best_d:.3f} -> {cd:.3f} km (delta: {best_d - cd:.3f} km)")
                        best_d = cd
                        best_ta, best_tb = opt_a, opt_b

print("\nDone testing pair neighborhood moves.")
