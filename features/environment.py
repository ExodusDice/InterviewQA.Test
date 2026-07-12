import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

def before_all(context):
    # Base evidence directory
    context.base_evidence_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "evidence"))
    os.makedirs(context.base_evidence_dir, exist_ok=True)
    
    # Unique timestamped folder inside evidence (Format: DDMMYYIIMMp, e.g. 1307261208am)
    timestamp = time.strftime("%d%m%y%I%M%p").lower()
    context.evidence_dir = os.path.join(context.base_evidence_dir, timestamp)
    os.makedirs(context.evidence_dir, exist_ok=True)
    
    # Determine if headless mode should be used
    context.headless = os.getenv("HEADLESS", "true").lower() in ("true", "1", "yes")

def before_scenario(context, scenario):
    # API scenarios do not need webdriver
    if "api" in scenario.tags:
        return

    # Rate-limit mitigation for public test server
    time.sleep(6)

    # Setup Chrome options
    chrome_options = Options()
    chrome_options.page_load_strategy = 'eager'
    
    if context.headless:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Support Chromium inside Docker
    if os.getenv("IS_DOCKER") == "true" or os.path.exists("/usr/bin/chromium"):
        chrome_options.binary_location = "/usr/bin/chromium"
        service = Service(executable_path="/usr/bin/chromedriver")
        context.driver = webdriver.Chrome(service=service, options=chrome_options)
    else:
        context.driver = webdriver.Chrome(options=chrome_options)
        
    context.driver.implicitly_wait(10)
    context.driver.set_page_load_timeout(15)

def after_scenario(context, scenario):
    if hasattr(context, "driver") and context.driver:
        if scenario.status == "failed" or scenario.status == "errored":
            # Automatically take screenshot on failure
            try:
                fail_name = f"failure_{scenario.name.replace(' ', '_').lower()}"
                hist_path = os.path.join(context.evidence_dir, f"{fail_name}.png")
                root_path = os.path.join(context.base_evidence_dir, f"{fail_name}.png")
                context.driver.save_screenshot(hist_path)
                context.driver.save_screenshot(root_path)
                print(f"Saved failure screenshots to:")
                print(f"  - History: {hist_path}")
                print(f"  - Latest:  {root_path}")
            except Exception as e:
                print(f"Could not take failure screenshot: {e}")

            try:
                print("\n--- BROWSER CONSOLE LOGS ---")
                logs = context.driver.get_log('browser')
                for entry in logs:
                    print(f"[{entry['level']}] {entry['message']}")
                print("----------------------------\n")
            except Exception as e:
                print(f"Could not retrieve console logs: {e}")
        context.driver.quit()
        context.driver = None

def take_screenshot(context, screenshot_name):
    """Helper function to save screenshots as evidence."""
    if hasattr(context, "driver") and context.driver:
        # Save in the timestamped folder for historical record
        hist_path = os.path.join(context.evidence_dir, f"{screenshot_name}.png")
        context.driver.save_screenshot(hist_path)
        
        # Save in the root evidence folder for HTML report and Word document compilation
        root_path = os.path.join(context.base_evidence_dir, f"{screenshot_name}.png")
        context.driver.save_screenshot(root_path)
        
        print(f"Screenshot saved to:")
        print(f"  - History: {hist_path}")
        print(f"  - Latest:  {root_path}")
