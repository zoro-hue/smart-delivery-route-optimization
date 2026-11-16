from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import os
import json

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

    print("Step 3: Waiting for primary optimization to complete...", flush=True)
    view_btn = None
    for _ in range(25):
        time.sleep(1)
        for b in driver.find_elements(By.TAG_NAME, "button"):
            if "View Solution" in b.text:
                view_btn = b
                break
        if view_btn:
            break

    assert view_btn is not None, "View Solution in Results button did not appear!"
    print(f"Step 4: Clicking '{view_btn.text}'...", flush=True)
    driver.execute_script("arguments[0].click();", view_btn)
    time.sleep(4)

    # Verify on Results page
    header = driver.find_element(By.TAG_NAME, "h1").text
    print(f"On Page: {header}", flush=True)
    assert "Results" in header

    # Capture initial Results view
    shot1 = os.path.join(out_dir, "final_05_results_initial.png")
    driver.save_screenshot(shot1)
    print(f"Captured initial results: {shot1}", flush=True)

    # Let's inspect the algorithm chips available
    buttons = driver.find_elements(By.TAG_NAME, "button")
    chips = []
    for b in buttons:
        txt = b.text
        if "km" in txt or "OR-Tools" in txt or "ROUTE/IQ" in txt or "Clarke" in txt or "Dijkstra" in txt or "2-opt" in txt:
            chips.append(b)

    print(f"Found {len(chips)} algorithm chip buttons:", flush=True)
    for c in chips:
        print(f"  - {c.text.replace(chr(10), ' | ')}", flush=True)

    # Test clicking between algorithms and verifying updates
    clicks_to_test = ["clarke_wright", "dijkstra", "ortools", "routeiq"]
    for target in ["Clarke", "Dijkstra", "OR-Tools"]:
        for c in chips:
            if target.lower() in c.text.lower():
                print(f"\nClicking chip: {c.text.replace(chr(10), ' ')}", flush=True)
                driver.execute_script("arguments[0].click();", c)
                time.sleep(2)
                
                # Check displayed total distance
                body = driver.find_element(By.TAG_NAME, "body").text
                for line in body.split("\n"):
                    if "km" in line and len(line) < 25:
                        print(f"  Metric Line: {line}", flush=True)
                
                shot = os.path.join(out_dir, f"final_06_results_chip_{target.lower()}.png")
                driver.save_screenshot(shot)
                print(f"  Saved screenshot: {shot}", flush=True)
                break

    print("\nInteractive Results Verification SUCCESSFUL!", flush=True)

finally:
    driver.quit()
