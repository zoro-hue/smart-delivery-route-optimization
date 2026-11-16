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
    print("Navigating to production Plan workspace...", flush=True)
    driver.get("https://route-iq-frontend-nine.vercel.app/")
    time.sleep(3)
    driver.execute_script("localStorage.setItem('routeiq_active_tab', 'plan');")
    driver.refresh()
    time.sleep(4)

    # Wait for delivery stops to load
    opt_btn = None
    for _ in range(15):
        time.sleep(1)
        for b in driver.find_elements(By.TAG_NAME, "button"):
            if "18 Stops" in b.text:
                opt_btn = b
                break
        if opt_btn:
            break
    print(f"Found button: {opt_btn.text if opt_btn else 'None'}", flush=True)
    if opt_btn:
        driver.execute_script("arguments[0].click();", opt_btn)
        print("Clicked Run Optimization. Waiting 10s for route to compute...", flush=True)

    time.sleep(12)

    # Find View Solution in Results button
    view_btn = None
    for b in driver.find_elements(By.TAG_NAME, "button"):
        if "View Solution" in b.text:
            view_btn = b
            break
    print(f"Found View Solution button: {view_btn.text if view_btn else 'None'}", flush=True)

    if view_btn:
        driver.execute_script("arguments[0].click();", view_btn)
        print("Clicked 'View Solution in Results' button!", flush=True)
        time.sleep(4)

        # Capture Results view
        res_shot = os.path.join(out_dir, "final_03_results_view_interactive.png")
        driver.save_screenshot(res_shot)
        print(f"Captured: {res_shot}", flush=True)

        body_text = driver.find_element(By.TAG_NAME, "body").text
        print("\nResults Page Summary Text (first 600 chars):", flush=True)
        print(body_text[:600], flush=True)
    else:
        print("View Solution button did not appear.", flush=True)

finally:
    driver.quit()
