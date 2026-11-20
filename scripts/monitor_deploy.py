import requests
import time

print("Monitoring Render deploy of commit 6ef6816...")
for i in range(25):
    try:
        r = requests.get("https://route-iq-backend.onrender.com/api/health", timeout=10)
        data = r.json()
        print(f"[{i*10}s] Status: {r.status_code}, App: {data.get('app')}, Python: {data.get('python_version')}")
    except Exception as e:
        print(f"[{i*10}s] Waiting for deploy/restart: {e}")
    time.sleep(10)
