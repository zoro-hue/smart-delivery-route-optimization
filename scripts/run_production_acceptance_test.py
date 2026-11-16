import os
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

out_dir = r"C:\Users\DELL\.gemini\antigravity\brain\aba14f7b-722c-4648-8da1-214dc979ac26\production_evidence"
os.makedirs(out_dir, exist_ok=True)

opts = Options()
opts.add_argument("--headless=new")
opts.add_argument("--no-sandbox")
opts.add_argument("--disable-dev-shm-usage")
opts.add_argument("--window-size=1920,1080")
opts.page_load_strategy = "eager"

driver = webdriver.Chrome(options=opts)
driver.set_page_load_timeout(30)
report = {}

try:
    print("\n--- STEP 1: Navigate to Production & Open Plan Tab ---", flush=True)
    driver.get("https://route-iq-frontend-nine.vercel.app/")
    time.sleep(3)

    # Switch to Plan tab with compare mode enabled
    driver.execute_script("localStorage.setItem('routeiq_active_tab', 'plan'); localStorage.setItem('routeiq_selection_mode', 'compare');")
    driver.refresh()
    time.sleep(4)

    fresh_path = os.path.join(out_dir, "final_01_plan_fresh.png")
    driver.save_screenshot(fresh_path)
    print(f"Captured Plan fresh state: {fresh_path}", flush=True)

    # Check for overlay paths (route lines)
    svg_paths = driver.find_elements(By.CSS_SELECTOR, ".leaflet-pane.leaflet-overlay-pane path")
    print(f"Leaflet overlay paths on initial load: {len(svg_paths)} (Expected: 0 or boundary only)", flush=True)

    # Find Run Optimization button
    buttons = driver.find_elements(By.TAG_NAME, "button")
    opt_button = None
    for b in buttons:
        t = b.text.strip()
        if "Run Optimization" in t:
            opt_button = b
            print(f"Found optimization button: '{t}'", flush=True)
            break

    report["initial_overlay_paths"] = len(svg_paths)
    report["opt_button_text"] = opt_button.text.strip() if opt_button else "Not found"

    print("\n--- STEP 2: Trigger Optimization & Monitor Dynamic Status ---", flush=True)
    if opt_button:
        driver.execute_script("arguments[0].click();", opt_button)
        print("Clicked 'Run Optimization' via JavaScript.", flush=True)
    else:
        # Fallback: find any button with 'Optimization'
        for b in driver.find_elements(By.TAG_NAME, "button"):
            if "Optimization" in b.text:
                driver.execute_script("arguments[0].click();", b)
                print(f"Clicked fallback button: '{b.text}'", flush=True)
                break

    # Monitor status for up to 90 seconds
    t_start = time.time()
    observed_statuses = []
    completed = False

    for poll in range(50):
        time.sleep(2.5)
        elapsed = round(time.time() - t_start, 1)

        current_buttons = [b.text.strip() for b in driver.find_elements(By.TAG_NAME, "button") if b.text.strip()]
        body_text = driver.find_element(By.TAG_NAME, "body").text
        matching_lines = [line.strip() for line in body_text.split("\n") if any(k in line for k in ["completed", "Comparing", "Computing", "Solution", "Feasible", "Algos", "surplus"])]

        observed_statuses.append({
            "elapsed_s": elapsed,
            "matching_lines": matching_lines[:5],
            "buttons": current_buttons[:6]
        })
        print(f"[{elapsed}s] Button state: {[b for b in current_buttons if 'Optimization' in b or 'Comparing' in b or 'Completed' in b or 'Partial' in b or 'View Solution' in b][:3]} | Lines: {matching_lines[:2]}", flush=True)

        # Check if terminal or results button appeared
        if any("View Solution" in b for b in current_buttons) or any("Completed" in b for b in current_buttons) or any("Partial" in b for b in current_buttons):
            # Check if all completed or if progress label indicates finish
            if any("Completed:" in b or "Completed with" in b or "Partial results:" in b for b in current_buttons):
                completed = True
                print(f"Job reached terminal state at {elapsed}s!", flush=True)
                break

    comp_path = os.path.join(out_dir, "final_02_job_completion.png")
    driver.save_screenshot(comp_path)
    print(f"Captured: {comp_path}", flush=True)
    report["observed_statuses"] = observed_statuses
    report["completed_in_time"] = completed

    print("\n--- STEP 3: Verify Results Page & Distinct Algorithms ---", flush=True)
    driver.execute_script("localStorage.setItem('routeiq_active_tab', 'results');")
    driver.refresh()
    time.sleep(4)

    res_path = os.path.join(out_dir, "final_03_results_view.png")
    driver.save_screenshot(res_path)
    print(f"Captured: {res_path}", flush=True)

    # Inspect algorithm buttons and displayed distances
    algo_elements = driver.find_elements(By.XPATH, "//button[contains(., 'km')] | //div[contains(., 'km')]")
    distances_found = set()
    for el in algo_elements:
        txt = el.text.strip()
        if "km" in txt and len(txt) < 50:
            distances_found.add(txt)
    print(f"Distances text found on Results page: {list(distances_found)}", flush=True)
    report["distances_found"] = list(distances_found)

    # Click on ROUTEIQ_COOPERATIVE and ORTOOLS if available
    for target in ["ROUTEIQ_COOPERATIVE", "ORTOOLS", "CLARKE_WRIGHT"]:
        try:
            for b in driver.find_elements(By.TAG_NAME, "button"):
                if target in b.text:
                    driver.execute_script("arguments[0].click();", b)
                    time.sleep(1.5)
                    driver.save_screenshot(os.path.join(out_dir, f"final_03_algo_{target.lower()}.png"))
                    print(f"Clicked {target} chip and captured screenshot.", flush=True)
                    break
        except Exception as e:
            print(f"Click error for {target}: {e}", flush=True)

    print("\n--- STEP 4: Verify Datasets Page Connectivity ---", flush=True)
    driver.execute_script("localStorage.setItem('routeiq_active_tab', 'datasets');")
    driver.refresh()
    time.sleep(4)

    data_path = os.path.join(out_dir, "final_04_datasets_view.png")
    driver.save_screenshot(data_path)
    print(f"Captured: {data_path}", flush=True)

    body_datasets = driver.find_element(By.TAG_NAME, "body").text
    has_network_error = "Network Error" in body_datasets or "Failed to connect" in body_datasets
    print(f"Datasets page Network Error present: {has_network_error}", flush=True)
    report["datasets_network_error"] = has_network_error

    # Save summary report
    with open(os.path.join(out_dir, "acceptance_report.json"), "w") as f:
        json.dump(report, f, indent=2)
    print("\nAcceptance report saved successfully!", flush=True)

except Exception as ex:
    print(f"AUDIT EXCEPTION: {ex}", flush=True)
    import traceback
    traceback.print_exc()
finally:
    driver.quit()
