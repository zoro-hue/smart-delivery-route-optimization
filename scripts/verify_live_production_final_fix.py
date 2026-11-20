import os
import sys
import time
import json

# Unbuffered stdout for immediate live logging
sys.stdout.reconfigure(line_buffering=True)

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

ARTIFACT_DIR = r"C:\Users\DELL\.gemini\antigravity\brain\aba14f7b-722c-4648-8da1-214dc979ac26\production_evidence"
os.makedirs(ARTIFACT_DIR, exist_ok=True)

PROD_URL = "https://route-iq-frontend-nine.vercel.app/"

print("Initializing Chrome for Final Release Verification...")
options = Options()
options.add_argument("--headless=new")
options.add_argument("--window-size=1600,1050")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 35)

try:
    print(f"Loading {PROD_URL}...")
    driver.get(PROD_URL)
    time.sleep(5)

    # 1. Connection Pill Verification
    pill_shot = os.path.join(ARTIFACT_DIR, "live_01_initial_navbar.png")
    driver.save_screenshot(pill_shot)
    print(f"Saved initial screen: {pill_shot}")

    # Wait for connection to reach CONNECTED
    print("Waiting for backend connection state...")
    time.sleep(6)

    # 2. Navigate to Plan Workspace
    print("Navigating to Plan Workspace...")
    plan_btns = driver.find_elements(By.XPATH, "//button[contains(text(), 'Plan')]")
    if plan_btns:
        plan_btns[0].click()
    else:
        driver.get(f"{PROD_URL}#plan")
    time.sleep(4)

    plan_shot = os.path.join(ARTIFACT_DIR, "live_02_plan_fresh.png")
    driver.save_screenshot(plan_shot)
    print(f"Saved Plan workspace screen: {plan_shot}")

    # 3. Click Compare Mode
    print("Selecting Compare mode...")
    compare_btns = driver.find_elements(By.XPATH, "//button[contains(text(), 'Compare')]")
    if compare_btns:
        compare_btns[0].click()
        time.sleep(2)

    # Check solver count text (e.g. 11 of 11 Solvers Selected)
    body_text = driver.find_element(By.TAG_NAME, "body").text
    print("Body text snippet around solvers:")
    for line in body_text.split("\n"):
        if "Solvers Selected" in line or "selected" in line.lower():
            print(f"  -> {line}")

    compare_select_shot = os.path.join(ARTIFACT_DIR, "live_03_compare_selected.png")
    driver.save_screenshot(compare_select_shot)
    print(f"Saved Compare selection screen: {compare_select_shot}")

    # 4. Trigger Compare / Run Optimization
    print("Triggering Optimization...")
    run_btns = driver.find_elements(By.XPATH, "//button[contains(., 'Compare') and contains(., 'Stops')]")
    if not run_btns:
        run_btns = driver.find_elements(By.XPATH, "//button[contains(., 'Run Optimization')]")
    assert run_btns, "Could not find Run / Compare button"

    print(f"Clicking: {run_btns[0].text}")
    run_btns[0].click()
    time.sleep(3)

    first_feasible_shot = os.path.join(ARTIFACT_DIR, "live_04_first_feasible.png")
    driver.save_screenshot(first_feasible_shot)
    print(f"Saved First Feasible Route screen: {first_feasible_shot}")

    # 5. Monitor Polling until all 11 complete
    print("Monitoring background comparison progression...")
    t_start = time.time()
    max_wait = 120
    last_label = ""

    while time.time() - t_start < max_wait:
        time.sleep(3)
        b_text = driver.find_element(By.TAG_NAME, "body").text
        # Look for progress text
        for line in b_text.split("\n"):
            if "completed" in line.lower() or "evaluating" in line.lower():
                if line != last_label:
                    print(f"  [{int(time.time() - t_start)}s] Progress: {line}")
                    last_label = line
        if "All 11 algorithms evaluated" in b_text or "11/11 completed" in b_text:
            print("Detected 11/11 completion!")
            break

    time.sleep(4)
    completed_shot = os.path.join(ARTIFACT_DIR, "live_05_job_completed.png")
    driver.save_screenshot(completed_shot)
    print(f"Saved Completion screen: {completed_shot}")

    # 6. Navigate to Results View to verify all 11 algorithms appear
    print("Navigating to Results View...")
    results_btns = driver.find_elements(By.XPATH, "//button[contains(text(), 'Results')]")
    if results_btns:
        driver.execute_script("arguments[0].click();", results_btns[0])
        time.sleep(4)
    else:
        driver.get(f"{PROD_URL}#results")
        time.sleep(4)

    results_shot = os.path.join(ARTIFACT_DIR, "live_06_results_all_11.png")
    driver.save_screenshot(results_shot)
    print(f"Saved Results screen: {results_shot}")

    res_body = driver.find_element(By.TAG_NAME, "body").text
    expected_algos = [
        "ROUTE/IQ",
        "OR-Tools",
        "Clarke-Wright",
        "2-opt",
        "Dijkstra",
        "A*",
        "Tabu Search",
        "Kernighan-Lin",
        "Variable Neighborhood Descent",
        "QAOA",
        "Quantum-Inspired",
    ]

    print("\nVerifying all 11 algorithms present in Results:")
    all_present = True
    for algo in expected_algos:
        present = algo.lower() in res_body.lower()
        status_sym = "✓" if present else "✗"
        print(f"  [{status_sym}] {algo}: {'FOUND' if present else 'NOT FOUND'}")
        if not present:
            all_present = False

    print(f"\nAll 11 algorithms present in Results UI: {all_present}")

finally:
    driver.quit()
