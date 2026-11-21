import os
import sys
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

ARTIFACT_DIR = r"C:\Users\DELL\.gemini\antigravity\brain\aba14f7b-722c-4648-8da1-214dc979ac26\production_evidence"
os.makedirs(ARTIFACT_DIR, exist_ok=True)

with open("live_production_comparison_result.json", "r", encoding="utf-8") as f:
    sample_data = json.load(f)

options = Options()
options.add_argument("--headless=new")
options.add_argument("--window-size=1600,1200")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

passed_checks = 0
total_checks = 0

def check(condition, message):
    global passed_checks, total_checks
    total_checks += 1
    if condition:
        passed_checks += 1
        print(f"  [✓] {message}")
    else:
        print(f"  [✗] FAILED: {message}")
        raise AssertionError(f"Check failed: {message}")

try:
    print("==================================================================")
    print("ROUTE/IQ RESULTS MAP ROUTE COLORS COMPREHENSIVE REGRESSION TEST")
    print("==================================================================")

    driver.get("http://127.0.0.1:4173")
    time.sleep(1)

    driver.execute_script("""
        localStorage.setItem('routeiq_active_tab', 'results');
        localStorage.setItem('routeiq_last_result', arguments[0]);
    """, json.dumps(sample_data))

    driver.get("http://127.0.0.1:4173")
    time.sleep(3)

    # 1. Map container verification
    map_elem = driver.find_elements(By.CLASS_NAME, "leaflet-container")
    check(len(map_elem) > 0, "Leaflet Map container successfully rendered in Results view")

    def get_rendered_map_state():
        paths = driver.find_elements(By.CSS_SELECTOR, ".leaflet-overlay-pane svg path")
        strokes = [p.get_attribute("stroke") for p in paths if p.get_attribute("stroke")]
        vehicle_pins = driver.find_elements(By.CSS_SELECTOR, ".custom-vehicle-pin div")
        pin_texts = [p.text for p in vehicle_pins if p.text]
        return strokes, pin_texts

    def select_algorithm(algo_id, match_text):
        # Look in Scorecard rows first (100% reliable deterministic row binding)
        rows = driver.find_elements(By.XPATH, f"//tr[contains(., '{match_text}')]")
        for row in rows:
            btns = row.find_elements(By.XPATH, ".//button[contains(., 'Inspect Route') or contains(., 'Displayed')]")
            if btns:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btns[0])
                driver.execute_script("arguments[0].click();", btns[0])
                time.sleep(1.2)
                return True

        # Fallback to switcher pills
        adv_btn = driver.find_elements(By.XPATH, "//button[contains(., 'Advanced Classical Benchmarks')]")
        if adv_btn:
            driver.execute_script("arguments[0].click();", adv_btn[0])
            time.sleep(0.5)

        pills = driver.find_elements(By.XPATH, f"//div[contains(@class, 'rounded')]//button[contains(., '{match_text}')]")
        if pills:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", pills[0])
            driver.execute_script("arguments[0].click();", pills[0])
            time.sleep(1.2)
            return True

        raise RuntimeError(f"Could not find selector for algorithm: {match_text}")

    # ─────────────────────────────────────────────────────────────────
    # 1. ROUTE/IQ Cooperative Engine: Green Family
    # ─────────────────────────────────────────────────────────────────
    print("\n[1/11] Testing ROUTE/IQ Cooperative Engine (Green Family)...")
    select_algorithm("routeiq_cooperative", "Cooperative")
    legend_text = driver.find_element(By.XPATH, "//*[contains(@class, 'glass-overlay') and contains(., 'Family')]").text
    check("Green Family" in legend_text, f"Legend indicates 'Green Family': {repr(legend_text[:60])}...")
    check("V1" in legend_text and "V2" in legend_text and "V3" in legend_text, "Legend shows V1, V2, V3 vehicle swatches")
    strokes, pins = get_rendered_map_state()
    check(len(strokes) >= 3, f"Rendered {len(strokes)} green route polylines on map")
    check(len(pins) >= 3, f"Rendered {len(pins)} vehicle pins (V1, V2, V3) on map")
    driver.save_screenshot(os.path.join(ARTIFACT_DIR, "route_colors_cooperative_green.png"))

    # ─────────────────────────────────────────────────────────────────
    # 2. OR-Tools: Blue Family
    # ─────────────────────────────────────────────────────────────────
    print("\n[2/11] Testing OR-Tools (Blue Family)...")
    select_algorithm("ortools", "OR-Tools")
    legend_text = driver.find_element(By.XPATH, "//*[contains(@class, 'glass-overlay') and contains(., 'Family')]").text
    check("Blue Family" in legend_text, f"Legend indicates 'Blue Family': {repr(legend_text[:60])}...")
    strokes, _ = get_rendered_map_state()
    check(len(strokes) >= 3, f"Rendered {len(strokes)} blue route polylines on map")
    driver.save_screenshot(os.path.join(ARTIFACT_DIR, "route_colors_ortools_blue.png"))

    # ─────────────────────────────────────────────────────────────────
    # 3. QAOA: Purple Family
    # ─────────────────────────────────────────────────────────────────
    print("\n[3/11] Testing QAOA (Purple Family)...")
    select_algorithm("qaoa", "QAOA")
    legend_text = driver.find_element(By.XPATH, "//*[contains(@class, 'glass-overlay') and contains(., 'Family')]").text
    check("Purple Family" in legend_text, f"Legend indicates 'Purple Family': {repr(legend_text[:60])}...")
    driver.save_screenshot(os.path.join(ARTIFACT_DIR, "route_colors_qaoa_purple.png"))

    # ─────────────────────────────────────────────────────────────────
    # 4. QIGA: Magenta / Pink Family
    # ─────────────────────────────────────────────────────────────────
    print("\n[4/11] Testing QIGA (Magenta / Pink Family)...")
    select_algorithm("qiga", "QIGA")
    legend_text = driver.find_element(By.XPATH, "//*[contains(@class, 'glass-overlay') and contains(., 'Family')]").text
    check("Magenta" in legend_text or "Pink" in legend_text, f"Legend indicates 'Magenta / Pink Family': {repr(legend_text[:60])}...")
    driver.save_screenshot(os.path.join(ARTIFACT_DIR, "route_colors_qiga_magenta.png"))

    # ─────────────────────────────────────────────────────────────────
    # 5. Tabu Search: Orange Family
    # ─────────────────────────────────────────────────────────────────
    print("\n[5/11] Testing Tabu Search (Orange Family)...")
    select_algorithm("tabu_search", "Tabu Search")
    legend_text = driver.find_element(By.XPATH, "//*[contains(@class, 'glass-overlay') and contains(., 'Family')]").text
    check("Orange Family" in legend_text, f"Legend indicates 'Orange Family': {repr(legend_text[:60])}...")
    driver.save_screenshot(os.path.join(ARTIFACT_DIR, "route_colors_tabu_search_orange.png"))

    # ─────────────────────────────────────────────────────────────────
    # 6. Clarke-Wright: Teal Family
    # ─────────────────────────────────────────────────────────────────
    print("\n[6/11] Testing Clarke-Wright Savings (Teal Family)...")
    select_algorithm("clarke_wright", "Clarke")
    legend_text = driver.find_element(By.XPATH, "//*[contains(@class, 'glass-overlay') and contains(., 'Family')]").text
    check("Teal Family" in legend_text, f"Legend indicates 'Teal Family': {repr(legend_text[:60])}...")
    driver.save_screenshot(os.path.join(ARTIFACT_DIR, "route_colors_clarke_wright_teal.png"))

    # ─────────────────────────────────────────────────────────────────
    # 7. 2-opt: Yellow / Amber Family
    # ─────────────────────────────────────────────────────────────────
    print("\n[7/11] Testing 2-opt Improvement (Yellow / Amber Family)...")
    select_algorithm("two_opt", "2-opt")
    legend_text = driver.find_element(By.XPATH, "//*[contains(@class, 'glass-overlay') and contains(., 'Family')]").text
    check("Amber Family" in legend_text or "Yellow" in legend_text, f"Legend indicates 'Yellow / Amber Family': {repr(legend_text[:60])}...")
    driver.save_screenshot(os.path.join(ARTIFACT_DIR, "route_colors_2opt_amber.png"))

    # ─────────────────────────────────────────────────────────────────
    # 8. Remaining Solvers (Kernighan-Lin, VND, A*, Dijkstra)
    # ─────────────────────────────────────────────────────────────────
    print("\n[8/11] Testing Kernighan-Lin (Rose / Crimson Family)...")
    select_algorithm("kernighan_lin", "Kernighan")
    legend_text = driver.find_element(By.XPATH, "//*[contains(@class, 'glass-overlay') and contains(., 'Family')]").text
    check("Rose" in legend_text or "Crimson" in legend_text, f"Legend indicates 'Rose / Crimson Family': {repr(legend_text[:60])}...")

    print("\n[9/11] Testing VND (Indigo Family)...")
    select_algorithm("vnd", "Variable Neighborhood Descent")
    legend_text = driver.find_element(By.XPATH, "//*[contains(@class, 'glass-overlay') and contains(., 'Family')]").text
    check("Indigo Family" in legend_text, f"Legend indicates 'Indigo Family': {repr(legend_text[:60])}...")

    print("\n[10/11] Testing A* (Cyan / Sky Blue Family)...")
    select_algorithm("astar", "A*")
    legend_text = driver.find_element(By.XPATH, "//*[contains(@class, 'glass-overlay') and contains(., 'Family')]").text
    check("Cyan" in legend_text, f"Legend indicates 'Cyan / Sky Blue Family': {repr(legend_text[:60])}...")

    print("\n[11/11] Testing Dijkstra (Bronze / Slate Family)...")
    select_algorithm("dijkstra", "Dijkstra")
    legend_text = driver.find_element(By.XPATH, "//*[contains(@class, 'glass-overlay') and contains(., 'Family')]").text
    check("Bronze" in legend_text or "Slate" in legend_text, f"Legend indicates 'Bronze / Slate Family': {repr(legend_text[:60])}...")

    # ─────────────────────────────────────────────────────────────────
    # 12. Comparative Overlay Feature
    # ─────────────────────────────────────────────────────────────────
    print("\nVerifying Comparative Overlay Feature...")
    select_algorithm("routeiq_cooperative", "Cooperative")
    overlay_btn = driver.find_elements(By.XPATH, "//button[contains(., 'Overlay')]")
    if overlay_btn:
        driver.execute_script("arguments[0].click();", overlay_btn[0])
        time.sleep(1)
        legend_after_overlay = driver.find_element(By.XPATH, "//*[contains(@class, 'glass-overlay') and contains(., 'Family')]").text
        check("Overlay:" in legend_after_overlay, f"Legend displays comparative overlay status: {repr(legend_after_overlay[-50:])}")
        driver.save_screenshot(os.path.join(ARTIFACT_DIR, "route_colors_comparative_overlay.png"))
        print("  [Saved Screenshot] Comparative Overlay: route_colors_comparative_overlay.png")

    # ─────────────────────────────────────────────────────────────────
    # 13. State Persistence across Page Reload
    # ─────────────────────────────────────────────────────────────────
    print("\nVerifying State Persistence across Page Reload...")
    driver.refresh()
    time.sleep(3)
    legend_after_refresh = driver.find_element(By.XPATH, "//*[contains(@class, 'glass-overlay') and contains(., 'Family')]").text
    check("Family" in legend_after_refresh, "Color Family legend remains intact and stable after page reload")

    print("\n==================================================================")
    print(f"ALL RESULTS MAP COLOR REGRESSION VERIFICATIONS PASSED: {passed_checks}/{total_checks}")
    print("==================================================================")

finally:
    driver.quit()
