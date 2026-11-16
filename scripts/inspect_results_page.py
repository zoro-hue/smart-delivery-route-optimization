from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

opts = Options()
opts.add_argument('--headless=new')
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-dev-shm-usage')
opts.add_argument('--window-size=1920,1080')
opts.page_load_strategy = 'eager'

driver = webdriver.Chrome(options=opts)
try:
    driver.get('https://route-iq-frontend-nine.vercel.app/')
    time.sleep(3)
    driver.execute_script("localStorage.setItem('routeiq_active_tab', 'results');")
    driver.refresh()
    time.sleep(4)
    print("RESULTS PAGE BODY TEXT:")
    body = driver.find_element(By.TAG_NAME, 'body').text
    print(body[:2000])
finally:
    driver.quit()
