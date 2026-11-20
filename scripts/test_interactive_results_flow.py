from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import os

out_dir = r"C:\Users\DELL\.gemini\antigravity\brain\aba14f7b-722c-4648-8da1-214dc979ac26\production_evidence"
os.makedirs(out_dir, exist_ok=True)

opts = Options()
opts.add_argument('--headless=new')
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-dev-shm-usage')
opts.add_argument('--window-size=1920,1080')
opts.page_load_strategy = 'eager'

driver = webdriver.Chrome(options=opts)
try:
    print("Step 1: Navigating to production app...", flush=True)
    driver.get("https://route-iq-frontend-nine.vercel.app/")
    time.sleep(3)
    driver.execute_script("localStorage.setItem('routeiq_active_tab', 'plan');")
    driver.execute_script("localStorage.setItem('routeiq_selection_mode', 'compare');")
    driver.execute_script("""
        localStorage.setItem('routeiq_selected_algorithms', JSON.stringify([
            'routeiq_cooperative', 'ortools', 'clarke_wright', 'two_opt',
            'dijkstra', 'astar', 'tabu_search', 'kernighan_lin', 'vnd', 'qaoa', 'qiga'
        ]));
    """)
    driver.refresh()
    time.sleep(4)

    # Find Run Optimization button
    opt_btn = None
    for _ in range(15):
        time.sleep(1)
        for b in driver.find_elements(By.TAG_NAME, "button"):
            if "18 Stops" in b.text:
                opt_btn = b
                break
        if opt_btn:
            break

    assert opt_btn is not None, "Run Optimization button not found!"
    print(f"Step 2: Clicking '{opt_btn.text}'...", flush=True)
    driver.execute_script("arguments[0].click();", opt_btn)

    print("Step 3: Waiting for background comparison evaluation to complete (35s)...", flush=True)
    for w in range(35):
        time.sleep(1)
        try:
            body = driver.find_element(By.TAG_NAME, "body").text
            if "11/11 completed" in body or "All 11 algorithms evaluated" in body:
                print(f"Background evaluation complete in {w+1}s!", flush=True)
                break
        except Exception:
            pass

    view_btn = None
    for _ in range(20):
        time.sleep(1)
        try:
            for b in driver.find_elements(By.TAG_NAME, "button"):
                try:
                    if "View Solution" in b.text:
                        view_btn = b
                        break
                except Exception:
                    continue
            if view_btn:
                break
        except Exception:
            continue

    assert view_btn is not None, "View Solution in Results button did not appear!"
    print(f"Step 4: Clicking '{view_btn.text}'...", flush=True)
    driver.execute_script("arguments[0].click();", view_btn)
    time.sleep(4)

    # Capture initial Results view
    shot1 = os.path.join(out_dir, "final_05_results_initial.png")
    driver.save_screenshot(shot1)
    print(f"Captured initial results: {shot1}", flush=True)

    # Find algorithm buttons in the Results page
    buttons = driver.find_elements(By.TAG_NAME, "button")
    chips = {}
    for b in buttons:
        txt = b.text.strip()
        if "km" in txt:
            # e.g. "CLARKE_WRIGHT 91.7 km"
            name = txt.split()[0]
            chips[name] = b

    print(f"\nFound {len(chips)} algorithm chip buttons:", flush=True)
    for name, btn in chips.items():
        print(f"  - {name}: {btn.text.replace(chr(10), ' | ')}", flush=True)

    # Test clicking across multiple algorithms and verifying state change
    results_observed = {}
    test_algos = ["ORTOOLS", "CLARKE_WRIGHT", "DIJKSTRA", "TABU_SEARCH", "QAOA"]
    
    for algo in test_algos:
        # Re-find buttons because DOM updates
        buttons = driver.find_elements(By.TAG_NAME, "button")
        target_btn = None
        for b in buttons:
            txt = b.text.upper()
            if algo in txt and "KM" in txt:
                target_btn = b
                break
        
        if target_btn:
            print(f"\n--- Clicking Algorithm: {algo} ---", flush=True)
            driver.execute_script("arguments[0].click();", target_btn)
            time.sleep(2)
            
            # Inspect displayed metrics
            body_text = driver.find_element(By.TAG_NAME, "body").text
            lines = [l.strip() for l in body_text.split("\n") if l.strip()]
            
            # Extract Selected Algorithm, Distance, Vehicles, Duration
            selected_algo_val = None
            distance_val = None
            duration_val = None
            drivers_val = None
            
            for i, line in enumerate(lines):
                if line == "SELECTED ALGORITHM" and i + 1 < len(lines):
                    selected_algo_val = lines[i+1]
                elif line == "TOTAL DISTANCE" and i + 1 < len(lines):
                    distance_val = lines[i+1]
                elif line == "ESTIMATED DURATION" and i + 1 < len(lines):
                    duration_val = lines[i+1]
                elif line == "VEHICLES ASSIGNED" and i + 1 < len(lines):
                    drivers_val = lines[i+1]

            # Find driver schedules
            driver_schedules = []
            for line in lines:
                if line.startswith("Driver #"):
                    driver_schedules.append(line)

            results_observed[algo] = {
                "selected_algo": selected_algo_val,
                "distance": distance_val,
                "duration": duration_val,
                "drivers": drivers_val,
                "schedules": driver_schedules[:3]
            }

            print(f"  Selected Algorithm Header: {selected_algo_val}", flush=True)
            print(f"  Total Distance Displayed: {distance_val}", flush=True)
            print(f"  Estimated Duration: {duration_val}", flush=True)
            print(f"  Vehicles Assigned: {drivers_val}", flush=True)
            print(f"  Schedules (first 3): {driver_schedules[:3]}", flush=True)

            shot = os.path.join(out_dir, f"final_06_results_view_{algo.lower()}.png")
            driver.save_screenshot(shot)
            print(f"  Saved screenshot: {shot}", flush=True)

    print("\n" + "=" * 60, flush=True)
    print("INTERACTIVE RESULTS VERIFICATION SUMMARY:", flush=True)
    print("=" * 60, flush=True)
    for a, data in results_observed.items():
        print(f"Algorithm: {a:15} | Displayed: {data['selected_algo']} | Distance: {data['distance']} | Duration: {data['duration']}", flush=True)

    # Check distinctness
    distances_shown = [d["distance"] for d in results_observed.values() if d["distance"]]
    print(f"\nDistinct Distances Observed: {set(distances_shown)}", flush=True)
    assert len(set(distances_shown)) >= 3, f"Expected at least 3 distinct distances, got {set(distances_shown)}"
    print("INTERACTIVE SELECTION & RE-RENDERING VERIFIED SUCCESSFULLY!", flush=True)

finally:
    driver.quit()
