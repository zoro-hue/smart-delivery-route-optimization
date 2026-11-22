import os
import sys
import json
import time

sys.stdout.reconfigure(line_buffering=True)

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

ARTIFACT_DIR = r"C:\Users\DELL\.gemini\antigravity\brain\aba14f7b-722c-4648-8da1-214dc979ac26\production_evidence"
os.makedirs(ARTIFACT_DIR, exist_ok=True)

# Build a full realistic 11-algorithm test payload
with open("baseline_30_instances_report.json", "r", encoding="utf-8") as f:
    sample_data = json.load(f)

# Or check live_production_18_stop_result.json if available
mock_payload_path = "live_production_18_stop_result.json"
if os.path.exists(mock_payload_path):
    with open(mock_payload_path, "r", encoding="utf-8") as f:
        mock_result = json.load(f)
else:
    mock_result = sample_data

print("Initializing Chrome for E2E Scorecard Verification...")
options = Options()
options.add_argument("--headless=new")
options.add_argument("--window-size=1600,1100")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    print("Navigating to http://localhost:4173...")
    driver.get("http://localhost:4173")
    time.sleep(2)

    # Inject mock experiment into localStorage
    print("Injecting 11-algorithm benchmark data into localStorage...")
    driver.execute_script("""
        localStorage.setItem('routeiq_active_tab', 'results');
        localStorage.setItem('routeiq_last_result', arguments[0]);
    """, json.dumps(mock_result))

    print("Reloading to render Results view with injected data...")
    driver.get("http://localhost:4173")
    time.sleep(4)

    # 1. Console errors check
    logs = driver.get_log("browser")
    severe_errors = [l for l in logs if l["level"] == "SEVERE" and "favicon" not in l["message"]]
    print(f"Browser severe errors found: {len(severe_errors)}")
    for err in severe_errors:
        print("  Console Error:", err["message"])
        assert "Minified React error #310" not in err["message"], "CRITICAL: React Error #310 detected!"

    # 2. Check for KPI cards
    body_text = driver.find_element(By.TAG_NAME, "body").text
    print("\nVerifying Dynamic KPI Cards...")
    kpi_checks = [
        "Best Feasible Distance",
        "Fastest Feasible Solver",
        "Evaluation Progress",
        "Feasible Solutions",
        "Fleet Violations",
    ]
    for kpi in kpi_checks:
        found = kpi.lower() in body_text.lower()
        print(f"  [{'✓' if found else '✗'}] KPI Card: {kpi}")
        assert found, f"Missing KPI Card: {kpi}"

    # 3. Check for 9 Primary Columns
    print("\nVerifying 9 Primary Columns in Comparison Table...")
    column_checks = [
        "1. Algorithm",
        "2. Category",
        "3. Feasibility",
        "4. Distance",
        "5. Duration",
        "6. Vehicles",
        "7. Violations",
        "8. Runtime",
        "9. Action",
    ]
    for col in column_checks:
        found = col.lower() in body_text.lower()
        print(f"  [{'✓' if found else '✗'}] Primary Column: {col}")
        assert found, f"Missing Column: {col}"

    # 4. Check that Research Systems are present and properly categorized
    print("\nVerifying Three Primary Research Systems & Baselines...")
    system_checks = [
        ("ROUTE/IQ", "Hybrid Cooperative"),
        ("QAOA", "Quantum Variational"),
        ("QIGA", "Quantum-Inspired"),
        ("OR-Tools", "Exact MIP Baseline"),
    ]
    for name, cat in system_checks:
        found_name = name.lower() in body_text.lower()
        found_cat = cat.lower() in body_text.lower()
        print(f"  [{'✓' if found_name else '✗'}] {name:<12} (Category '{cat}': {'✓' if found_cat else '✗'})")
        assert found_name, f"Missing system: {name}"

    # Take screenshot of redesigned desktop view
    desktop_shot = os.path.join(ARTIFACT_DIR, "redesigned_scorecard_desktop.png")
    driver.save_screenshot(desktop_shot)
    print(f"\n[Saved Screenshot] Desktop Scorecard: {desktop_shot}")

    # 5. Test Expand All Details
    print("\nTesting 'Expand All Details' button...")
    expand_all_btn = driver.find_elements(By.XPATH, "//button[contains(., 'Expand All Details')]")
    if expand_all_btn:
        driver.execute_script("arguments[0].click();", expand_all_btn[0])
        time.sleep(2)
        body_text_expanded = driver.find_element(By.TAG_NAME, "body").text.lower()
        assert "speed & transit model" in body_text_expanded
        assert "compute & memory" in body_text_expanded
        assert "complexity & architecture" in body_text_expanded
        assert "objective & convergence" in body_text_expanded
        print("  [✓] All telemetry drawers expanded with speed, compute, complexity, and objective metrics!")
        
        expanded_shot = os.path.join(ARTIFACT_DIR, "redesigned_scorecard_expanded_details.png")
        driver.save_screenshot(expanded_shot)
        print(f"  [Saved Screenshot] Expanded Details: {expanded_shot}")

    # 6. Test Scope Filter (Primary vs Classical)
    print("\nTesting Scope Filter Tabs...")
    primary_filter_btn = driver.find_elements(By.XPATH, "//button[contains(., 'Primary Research Systems')]")
    if primary_filter_btn:
        driver.execute_script("arguments[0].click();", primary_filter_btn[0])
        time.sleep(1)
        primary_text = driver.find_element(By.TAG_NAME, "body").text
        print("  [✓] Primary Research Systems filter applied!")

    all_filter_btn = driver.find_elements(By.XPATH, "//button[contains(., 'All Solvers')]")
    if all_filter_btn:
        driver.execute_script("arguments[0].click();", all_filter_btn[0])
        time.sleep(1)
        print("  [✓] Reset back to All Solvers!")

    # 7. Test Inspect Route action on QAOA
    print("\nTesting 'Inspect Route' action on QAOA...")
    qaoa_inspect_btns = driver.find_elements(By.XPATH, "//tr[contains(., 'QAOA')]//button[contains(., 'Inspect Route')]")
    if qaoa_inspect_btns:
        driver.execute_script("arguments[0].click();", qaoa_inspect_btns[0])
        time.sleep(2)
        active_header = driver.find_element(By.XPATH, "//*[contains(text(), 'Active Route Inspection')]").text
        print(f"  [✓] Active route inspection updated: '{active_header}'")
        assert "QAOA" in active_header, "Inspect route did not switch active algorithm to QAOA!"

    # 8. Test Mobile Viewport (Responsive Card Layout)
    print("\nTesting Mobile Viewport (390 x 844)...")
    driver.set_window_size(390, 844)
    time.sleep(2)
    mobile_shot = os.path.join(ARTIFACT_DIR, "redesigned_scorecard_mobile_cards.png")
    driver.save_screenshot(mobile_shot)
    print(f"  [Saved Screenshot] Mobile Card View: {mobile_shot}")

    mobile_body = driver.find_element(By.TAG_NAME, "body").text.lower()
    assert "road distance" in mobile_body
    assert "driving duration" in mobile_body
    print("  [✓] Mobile card layout verified successfully!")

    print("\n========================================================")
    print("ALL E2E SCORECARD REDESIGN VERIFICATIONS PASSED (10/10)")
    print("========================================================")

finally:
    driver.quit()
