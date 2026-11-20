import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

ARTIFACT_DIR = r"C:\Users\DELL\.gemini\antigravity\brain\aba14f7b-722c-4648-8da1-214dc979ac26\production_evidence"
os.makedirs(ARTIFACT_DIR, exist_ok=True)

PROD_URL = "https://route-iq-frontend-nine.vercel.app/"
JOB_ID = "2c9d8ae0-1d2e-44a3-a883-6f969297446c"

options = Options()
options.add_argument("--headless=new")
options.add_argument("--window-size=1600,1050")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    print(f"Loading {PROD_URL}...")
    driver.get(PROD_URL)
    time.sleep(4)

    # Set active job in localStorage and reload
    driver.execute_script(f"""
        localStorage.setItem('routeiq_active_job_id', '{JOB_ID}');
        localStorage.setItem('routeiq_active_tab', 'results');
    """)
    driver.refresh()
    time.sleep(5)

    shot1 = os.path.join(ARTIFACT_DIR, "live_production_results_all_11_algorithms.png")
    driver.save_screenshot(shot1)
    print(f"Captured: {shot1}")

    # Switch to Plan workspace to show top banner & scorecard
    driver.execute_script("localStorage.setItem('routeiq_active_tab', 'plan');")
    driver.refresh()
    time.sleep(5)

    shot2 = os.path.join(ARTIFACT_DIR, "live_production_plan_completed_11_algorithms.png")
    driver.save_screenshot(shot2)
    print(f"Captured: {shot2}")

    # Inspect rendered text
    body = driver.find_element(By.TAG_NAME, "body").text
    print("\nRendered text highlights on Plan page:")
    for line in body.split("\n"):
        if any(w in line.lower() for w in ["completed", "route/iq", "best", "ortools", "qiga", "qaoa"]):
            print(f"  -> {line}")

finally:
    driver.quit()
