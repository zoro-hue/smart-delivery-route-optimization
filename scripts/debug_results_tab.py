from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

opts = Options()
opts.add_argument('--headless=new')
opts.add_argument('--no-sandbox')
opts.add_argument('--window-size=1920,1080')
opts.page_load_strategy = 'eager'

d = webdriver.Chrome(options=opts)
try:
    d.get('https://route-iq-frontend-nine.vercel.app/')
    time.sleep(3)
    d.execute_script("localStorage.setItem('routeiq_active_tab', 'plan');")
    d.refresh()
    time.sleep(3)

    # Click run optimization
    for b in d.find_elements(By.TAG_NAME, "button"):
        if "18 Stops" in b.text:
            d.execute_script("arguments[0].click();", b)
            print("Clicked Run Optimization", flush=True)
            break

    # Wait for View Solution button
    view_btn = None
    for _ in range(25):
        time.sleep(1)
        for b in d.find_elements(By.TAG_NAME, "button"):
            if "View Solution" in b.text:
                view_btn = b
                break
        if view_btn:
            break

    if view_btn:
        print("Found View button:", view_btn.text, flush=True)
        d.execute_script("arguments[0].click();", view_btn)
        time.sleep(3)

    print("Current URL:", d.current_url)
    h1s = [h.text for h in d.find_elements(By.TAG_NAME, 'h1')]
    print("H1 elements:", h1s)
    h2s = [h.text for h in d.find_elements(By.TAG_NAME, 'h2')]
    print("H2 elements:", h2s)
    body = d.find_element(By.TAG_NAME, 'body').text
    print("Body preview:\n", body[:800])
    d.save_screenshot("production_evidence/debug_results_screenshot.png")
finally:
    d.quit()
