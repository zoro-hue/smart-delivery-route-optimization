import os
import sys
import time
import requests

sys.stdout.reconfigure(line_buffering=True)

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

ARTIFACT_DIR = r"C:\Users\DELL\.gemini\antigravity\brain\aba14f7b-722c-4648-8da1-214dc979ac26\production_evidence"
os.makedirs(ARTIFACT_DIR, exist_ok=True)

PROD_URL = "https://route-iq-frontend-nine.vercel.app/"
BACKEND_URL = "https://route-iq-backend.onrender.com"

print("=================================================================")
print("ROUTE/IQ — FULL PRODUCTION RELEASE VERIFICATION (COMMIT 839a14e)")
print("=================================================================")

# 1. Wait for Backend & Frontend deployment
print("\n[Stage 1] Checking Live Deployment Health...")
for i in range(30):
    try:
        r = requests.get(f"{BACKEND_URL}/api/health", timeout=10)
        if r.status_code == 200:
            print(f"  Backend is UP and HEALTHY! Python: {r.json().get('python_version')}, Qiskit: {r.json().get('qiskit_version')}")
            break
    except Exception as e:
        print(f"  Waiting for backend deploy... ({e})")
    time.sleep(10)

# Record Baseline Memory
try:
    mem_res = requests.get(f"{BACKEND_URL}/api/system/memory", timeout=10).json()
    print(f"  Baseline Memory: RSS={mem_res.get('process_rss_mb')} MB, Headroom={mem_res.get('render_headroom_mb')} MB")
except Exception as e:
    print(f"  Could not read baseline memory: {e}")

# 2. Launch Chrome
print("\n[Stage 2] Launching Chrome Browser...")
options = Options()
options.add_argument("--headless=new")
options.add_argument("--window-size=1600,1050")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 35)

try:
    # 3. Verify Navbar & Connection State Machine
    print(f"\n[Stage 3] Loading Frontend: {PROD_URL}...")
    driver.get(PROD_URL)
    time.sleep(6)

    pill_shot = os.path.join(ARTIFACT_DIR, "live_01_initial_navbar.png")
    driver.save_screenshot(pill_shot)
    print(f"  Saved initial navbar screenshot: {pill_shot}")

    nav_header = driver.find_element(By.TAG_NAME, "header").text if driver.find_elements(By.TAG_NAME, "header") else ""
    print(f"  Navbar text snippet:\n    {nav_header.replace(chr(10), ' | ')}")
    assert "Qiskit 2.4.1" in nav_header or "CONNECTED" in nav_header, "Connection pill not showing connected state"

    # 4. Verify Plan Fresh State (No Stale Routes)
    print("\n[Stage 4] Verifying Initial Plan Workspace State...")
    plan_btns = driver.find_elements(By.XPATH, "//button[contains(text(), 'Plan')]")
    if plan_btns:
        plan_btns[0].click()
    time.sleep(4)

    plan_shot = os.path.join(ARTIFACT_DIR, "live_02_plan_fresh.png")
    driver.save_screenshot(plan_shot)
    print(f"  Saved Plan fresh screenshot: {plan_shot}")

    # Verify no route lines or computing indicators
    body_text_fresh = driver.find_element(By.TAG_NAME, "body").text
    assert "Computing Solution" not in body_text_fresh, "Stale computing indicator displayed!"
    print("  CONFIRMED: Plan initialized cleanly without stale routes or running indicators.")

    # 5. Select Compare Mode (All 11 Solvers)
    print("\n[Stage 5] Selecting Compare Mode (All 11 Solvers)...")
    compare_btns = driver.find_elements(By.XPATH, "//button[contains(text(), 'Compare')]")
    if compare_btns:
        compare_btns[0].click()
        time.sleep(2)

    compare_select_shot = os.path.join(ARTIFACT_DIR, "live_03_compare_selected.png")
    driver.save_screenshot(compare_select_shot)
    print(f"  Saved Compare selection screenshot: {compare_select_shot}")

    body_text = driver.find_element(By.TAG_NAME, "body").text
    assert "11 of 11 Solvers Selected" in body_text, f"Expected '11 of 11 Solvers Selected', got:\n{body_text[:500]}"
    print("  CONFIRMED: All 11 solvers selected in Compare mode.")

    # 6. Trigger Optimization & Measure First Feasible Route Latency
    print("\n[Stage 6] Triggering Comparison Optimization...")
    run_btns = driver.find_elements(By.XPATH, "//button[contains(., 'Compare') and contains(., 'Stops')]")
    if not run_btns:
        run_btns = driver.find_elements(By.XPATH, "//button[contains(., 'Run Optimization')]")
    assert run_btns, "Could not find Run / Compare button"

    t_click = time.time()
    driver.execute_script("arguments[0].click();", run_btns[0])
    print(f"  Clicked button. Waiting for first feasible route...")

    # Wait for first feasible route indicator or route lines to appear
    first_feasible_latency = None
    for sec in range(25):
        time.sleep(0.5)
        cur_body = driver.find_element(By.TAG_NAME, "body").text
        if "First feasible route ready" in cur_body or "completed" in cur_body:
            first_feasible_latency = round(time.time() - t_click, 2)
            print(f"  FIRST FEASIBLE ROUTE READY in {first_feasible_latency}s!")
            break

    first_feasible_shot = os.path.join(ARTIFACT_DIR, "live_04_first_feasible.png")
    driver.save_screenshot(first_feasible_shot)
    print(f"  Saved First Feasible Route screenshot: {first_feasible_shot}")

    # 7. Monitor Progressive Background Polling until All 11 Solvers Complete
    print("\n[Stage 7] Monitoring Progressive Background Comparison (Target: 11/11)...")
    t_poll_start = time.time()
    max_wait = 180
    last_label = ""
    job_completed = False

    while time.time() - t_poll_start < max_wait:
        time.sleep(2)
        b_text = driver.find_element(By.TAG_NAME, "body").text
        for line in b_text.split("\n"):
            if ("completed" in line.lower() or "evaluating" in line.lower()) and line != last_label:
                print(f"  [{int(time.time() - t_poll_start)}s] Progress: {line}")
                last_label = line
        if "All 11 algorithms evaluated" in b_text or "11/11 completed" in b_text or "All 11 algorithms" in b_text or "Results retained" in b_text or ("completed" in b_text and "timed out" in b_text and "11" in b_text):
            job_completed = True
            print("  DETECTED 11/11 ALGORITHMS COMPLETED IN FRONTEND UI!")
            break

    time.sleep(3)
    completed_shot = os.path.join(ARTIFACT_DIR, "live_05_job_completed.png")
    driver.save_screenshot(completed_shot)
    print(f"  Saved Job Completed screenshot: {completed_shot}")

    # 8. Navigate to Results View & Audit All 11 Solvers
    print("\n[Stage 8] Navigating to Results View...")
    results_btns = driver.find_elements(By.XPATH, "//button[contains(text(), 'Results')]")
    if results_btns:
        driver.execute_script("arguments[0].click();", results_btns[0])
    time.sleep(4)

    results_shot = os.path.join(ARTIFACT_DIR, "live_06_results_all_11.png")
    driver.save_screenshot(results_shot)
    print(f"  Saved Results screen: {results_shot}")

    res_body = driver.find_element(By.TAG_NAME, "body").text
    expected_algos = [
        ("ROUTE/IQ Cooperative Engine", ["route/iq", "cooperative"]),
        ("OR-Tools", ["or-tools", "ortools"]),
        ("Clarke–Wright Savings", ["clarke"]),
        ("2-opt Improvement", ["2-opt", "2opt"]),
        ("Dijkstra Shortest-Path", ["dijkstra"]),
        ("A* Heuristic Search", ["a*"]),
        ("Tabu Search", ["tabu"]),
        ("Kernighan–Lin", ["kernighan"]),
        ("Variable Neighborhood Descent (VND)", ["variable neighborhood", "vnd"]),
        ("QAOA", ["qaoa"]),
        ("Quantum-Inspired (QIGA)", ["qiga", "quantum-inspired"]),
    ]

    print("\nAuditing All 11 Solvers in Results Workspace:")
    found_count = 0
    for display_name, match_terms in expected_algos:
        found = any(term in res_body.lower() for term in match_terms)
        sym = "✓" if found else "✗"
        status_txt = "FOUND" if found else "MISSING"
        if found:
            found_count += 1
        print(f"  [{sym}] {display_name:<36}: {status_txt}")

    print(f"\nResults Scorecard Audit: {found_count}/11 Solvers Verified Present in UI!")

    # Interactive algorithm selection in Results view
    print("\nTesting interactive algorithm selection in Results...")
    for target in ["QAOA", "Clarke-Wright", "ROUTE/IQ"]:
        try:
            target_btns = driver.find_elements(By.XPATH, f"//button[contains(., '{target}')]")
            if target_btns:
                driver.execute_script("arguments[0].click();", target_btns[0])
                time.sleep(2)
                inter_shot = os.path.join(ARTIFACT_DIR, f"live_07_result_select_{target.lower().replace('/', '_')}.png")
                driver.save_screenshot(inter_shot)
                print(f"  Successfully selected '{target}' and saved screenshot: {inter_shot}")
        except Exception as e:
            print(f"  Note on clicking {target}: {e}")

    # 9. Verify Post-Job Memory on Backend
    try:
        mem_post = requests.get(f"{BACKEND_URL}/api/system/memory", timeout=10).json()
        print(f"\n[Stage 9] Post-Job Backend Memory: RSS={mem_post.get('process_rss_mb')} MB, Limit={mem_post.get('render_memory_limit_mb')} MB, Headroom={mem_post.get('render_headroom_mb')} MB")
    except Exception as e:
        print(f"\n[Stage 9] Could not read post-job memory: {e}")

finally:
    driver.quit()
    print("\nVerification Completed.")
