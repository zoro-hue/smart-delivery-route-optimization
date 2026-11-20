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
    print("Navigating...", flush=True)
    driver.get("https://route-iq-frontend-nine.vercel.app/")
    time.sleep(3)
    driver.execute_script("localStorage.setItem('routeiq_active_tab', 'plan');")
    driver.execute_script("localStorage.setItem('routeiq_selection_mode', 'compare');")
    driver.refresh()
    time.sleep(4)

    # Click the planning controls or find Compare button
    body = driver.find_element(By.TAG_NAME, "body").text
    print("Initial Plan Page text (snippet):", flush=True)
    for line in body.split("\n")[:20]:
        print("  ", line, flush=True)

    # Find button with 'Compare' or 'Run'
    btn = None
    for b in driver.find_elements(By.TAG_NAME, "button"):
        if "Compare" in b.text or "Run Optimization" in b.text:
            btn = b
            print(f"Found target button: '{b.text}'", flush=True)
            break
            
    if btn:
        driver.execute_script("arguments[0].click();", btn)
        print("Clicked button! Waiting 15s...", flush=True)
        time.sleep(15)
        
        # Screenshot plan during comparison
        driver.save_screenshot(os.path.join(out_dir, "plan_during_comparison.png"))
        
        body2 = driver.find_element(By.TAG_NAME, "body").text
        print("\nPage text during comparison:", flush=True)
        for line in body2.split("\n")[:25]:
            print("  ", line, flush=True)

finally:
    driver.quit()
