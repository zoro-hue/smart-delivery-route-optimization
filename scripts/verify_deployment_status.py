import urllib.request
import json
import time

print("--- 1. Render Production Backend Health ---")
req = urllib.request.Request("https://route-iq-backend.onrender.com/health", headers={"User-Agent": "Mozilla/5.0"})
try:
    with urllib.request.urlopen(req, timeout=20) as r:
        print("HTTP Status:", r.status)
        data = json.loads(r.read().decode())
        print(json.dumps(data, indent=2))
except Exception as e:
    print("Health error:", e)

print("\n--- 2. Render Live Memory Telemetry ---")
req_mem = urllib.request.Request("https://route-iq-backend.onrender.com/api/system/memory", headers={"User-Agent": "Mozilla/5.0"})
try:
    with urllib.request.urlopen(req_mem, timeout=20) as r:
        print("HTTP Status:", r.status)
        mem_data = json.loads(r.read().decode())
        print(json.dumps(mem_data, indent=2))
except Exception as e:
    print("Memory endpoint error:", e)

print("\n--- 3. Vercel Production Frontend Bundle Check ---")
req_v = urllib.request.Request("https://route-iq-frontend-nine.vercel.app/", headers={"User-Agent": "Mozilla/5.0"})
try:
    with urllib.request.urlopen(req_v, timeout=20) as r:
        print("Vercel HTTP Status:", r.status)
        headers = dict(r.getheaders())
        print("Vercel Headers:", {k: headers[k] for k in ["x-vercel-id", "date", "etag"] if k in headers})
        html = r.read().decode()
        print("HTML length:", len(html))
        # Find script tags in html
        import re
        scripts = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', html)
        print("Bundled assets:", scripts)
except Exception as e:
    print("Vercel check error:", e)
