import time
import requests
import sys

BACKEND_URL = "https://route-iq-backend.onrender.com/api/health"
FRONTEND_URL = "https://route-iq-frontend-nine.vercel.app/"

print("Monitoring live production deployment for commit f92b4c2...")
max_wait_seconds = 360
interval = 15
start_time = time.time()

backend_healthy = False
frontend_healthy = False

while time.time() - start_time < max_wait_seconds:
    elapsed = int(time.time() - start_time)

    # Check backend
    try:
        r_back = requests.get(BACKEND_URL, timeout=10)
        if r_back.status_code == 200:
            b_data = r_back.json()
            b_status = b_data.get("status", "unknown")
            b_qiskit = b_data.get("qiskit_available", False)
            backend_healthy = True
            print(f"[{elapsed}s] Backend UP! Status: {b_status}, Qiskit: {b_qiskit}")
        else:
            print(f"[{elapsed}s] Backend returned {r_back.status_code}")
    except Exception as e:
        print(f"[{elapsed}s] Backend waiting... ({e})")

    # Check frontend
    try:
        r_front = requests.get(FRONTEND_URL, timeout=10)
        if r_front.status_code == 200:
            frontend_healthy = True
            print(f"[{elapsed}s] Frontend UP! (HTTP 200)")
        else:
            print(f"[{elapsed}s] Frontend returned {r_front.status_code}")
    except Exception as e:
        print(f"[{elapsed}s] Frontend waiting... ({e})")

    if backend_healthy and frontend_healthy and elapsed >= 30:
        print("\nProduction environment is UP and RESPONDING!")
        break

    time.sleep(interval)

if not backend_healthy or not frontend_healthy:
    print("\nTimeout waiting for production deployment.")
    sys.exit(1)
