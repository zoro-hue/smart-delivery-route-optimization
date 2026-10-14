import urllib.request
import json
import time

res = urllib.request.urlopen('http://localhost:8000/api/delivery-stops?limit=25')
data = json.loads(res.read().decode())
all_stops = data['stops'][:16]
depot = data['depot']
print(f"Sending 16 stops with depot ({depot['lat']}, {depot['lon']})...")

req_data = {
    'num_vehicles': 5,
    'vehicle_capacity': 80,
    'depot_lat': depot['lat'],
    'depot_lon': depot['lon'],
    'depot_name': depot.get('name', 'Origin Depot'),
    'num_customers': 16,
    'custom_customers': all_stops,
    'selection_mode': 'compare',
    'selected_algorithms': ['dijkstra', 'astar', 'ortools', 'clarke_wright', 'two_opt', 'qiga'],
    'algorithm': 'classical',
    'traffic_scenario': 'normal',
}

t0 = time.time()
req = urllib.request.Request(
    'http://localhost:8000/api/optimization/run',
    data=json.dumps(req_data).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
try:
    res = urllib.request.urlopen(req, timeout=120)
    d = json.loads(res.read().decode())
    elapsed = time.time() - t0
    print(f"Completed in {elapsed:.2f}s! Status: {d.get('status')}")
    for k, v in d.get('results', {}).items():
        print(f"  {k}: {v.get('status')} in {v.get('solve_time_sec')}s, distance: {v.get('total_distance_km')}km")
except Exception as e:
    print('Failed after', round(time.time() - t0, 2), 's:', e)
