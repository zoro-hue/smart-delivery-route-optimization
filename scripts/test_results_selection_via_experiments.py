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
    print("Navigating to production app...", flush=True)
    driver.get("https://route-iq-frontend-nine.vercel.app/")
    time.sleep(3)
    
    # 1. Click 'Experiments' in navigation bar
    exp_nav = None
    for b in driver.find_elements(By.TAG_NAME, "button"):
        if b.text.strip() == "Experiments":
            exp_nav = b
            break
            
    assert exp_nav is not None, "Experiments nav button not found"
    print("Clicking 'Experiments' tab...", flush=True)
    driver.execute_script("arguments[0].click();", exp_nav)
    time.sleep(4)

    # 2. In Experiments page, find completed experiment and click it
    exp_rows = driver.find_elements(By.XPATH, "//tr | //div[contains(@class, 'cursor-pointer')]")
    print(f"Found {len(exp_rows)} potential experiment elements.", flush=True)
    
    # Take screenshot of Experiments page
    driver.save_screenshot(os.path.join(out_dir, "experiments_page.png"))
    
    # Find any 'View in Results' or row click
    load_btn = None
    for b in driver.find_elements(By.TAG_NAME, "button"):
        if "Results" in b.text or "View" in b.text or "Load" in b.text:
            if b != exp_nav:
                load_btn = b
                break
                
    if load_btn:
        print(f"Clicking '{load_btn.text}' in Experiments...", flush=True)
        driver.execute_script("arguments[0].click();", load_btn)
        time.sleep(3)
    else:
        # Click the first experiment card/row
        print("Clicking first experiment card/row...", flush=True)
        for elem in exp_rows:
            txt = elem.text
            if "Job" in txt or "COMPLETED" in txt or "km" in txt:
                driver.execute_script("arguments[0].click();", elem)
                time.sleep(3)
                break

    # 3. Now navigate to Results tab
    res_nav = None
    for b in driver.find_elements(By.TAG_NAME, "button"):
        if b.text.strip() == "Results":
            res_nav = b
            break
            
    assert res_nav is not None, "Results nav button not found"
    print("Clicking 'Results' tab...", flush=True)
    driver.execute_script("arguments[0].click();", res_nav)
    time.sleep(4)

    # 4. In Results view, find all algorithm buttons
    driver.save_screenshot(os.path.join(out_dir, "results_from_experiment.png"))
    
    algo_chips = []
    for b in driver.find_elements(By.TAG_NAME, "button"):
        txt = b.text.strip()
        if "km" in txt.lower() and len(txt) < 35:
            algo_chips.append(b)

    print(f"Found {len(algo_chips)} algorithm chips in Results view:", flush=True)
    for c in algo_chips:
        print(f"  Chip: {c.text.replace(chr(10), ' | ')}", flush=True)

    # 5. Click through algorithms and test responsiveness
    target_algos = ["ORTOOLS", "CLARKE_WRIGHT", "DIJKSTRA", "TABU_SEARCH", "QAOA", "ROUTEIQ_COOPERATIVE"]
    clicks_recorded = {}
    
    for algo in target_algos:
        # Re-query buttons to avoid stale element references
        all_btns = driver.find_elements(By.TAG_NAME, "button")
        target_btn = None
        for b in all_btns:
            txt = b.text.upper()
            if algo in txt and "KM" in txt:
                target_btn = b
                break
                
        if target_btn:
            print(f"\n--- Clicking chip: {algo} ---", flush=True)
            driver.execute_script("arguments[0].click();", target_btn)
            time.sleep(2)
            
            # Read metrics
            body = driver.find_element(By.TAG_NAME, "body").text
            lines = [l.strip() for l in body.split("\n") if l.strip()]
            
            selected_name = None
            total_dist = None
            duration = None
            drivers_count = None
            schedules = []
            
            for i, line in enumerate(lines):
                if line == "SELECTED ALGORITHM" and i + 1 < len(lines):
                    selected_name = lines[i+1]
                elif line == "TOTAL DISTANCE" and i + 1 < len(lines):
                    total_dist = lines[i+1]
                elif line == "ESTIMATED DURATION" and i + 1 < len(lines):
                    duration = lines[i+1]
                elif line == "VEHICLES ASSIGNED" and i + 1 < len(lines):
                    drivers_count = lines[i+1]
                elif line.startswith("Driver #"):
                    schedules.append(line)
                    
            clicks_recorded[algo] = {
                "name": selected_name,
                "distance": total_dist,
                "duration": duration,
                "drivers": drivers_count,
                "schedules": schedules[:2]
            }
            print(f"  Name: {selected_name} | Distance: {total_dist} | Duration: {duration} | Vehicles: {drivers_count}", flush=True)
            print(f"  Schedules: {schedules[:2]}", flush=True)
            
            driver.save_screenshot(os.path.join(out_dir, f"results_click_{algo.lower()}.png"))

    print("\n" + "=" * 60, flush=True)
    print("RESULTS VERIFICATION RESULTS:", flush=True)
    print("=" * 60, flush=True)
    for a, info in clicks_recorded.items():
        print(f"Algo: {a:20} -> Selected: {info['name']} | Dist: {info['distance']} | Scheds: {len(info['schedules'])} drivers", flush=True)

    dists = [v['distance'] for v in clicks_recorded.values() if v['distance']]
    print(f"\nDistinct Distances Displayed: {set(dists)}", flush=True)
    assert len(set(dists)) >= 3, f"Expected at least 3 distinct distances, got {set(dists)}"
    print("RESULTS INTERACTIVE SELECTION CONFIRMED WORKING!", flush=True)

finally:
    driver.quit()
