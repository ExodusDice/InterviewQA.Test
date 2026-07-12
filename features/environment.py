import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

def before_all(context):
    # Ensure evidence folder exists
    context.evidence_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "evidence"))
    os.makedirs(context.evidence_dir, exist_ok=True)
    
    # Determine if headless mode should be used
    context.headless = os.getenv("HEADLESS", "true").lower() in ("true", "1", "yes")

def before_scenario(context, scenario):
    # API scenarios do not need webdriver
    if "api" in scenario.tags:
        return

    # Rate-limit mitigation for public test server
    time.sleep(3)

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

def after_scenario(context, scenario):
    if hasattr(context, "driver") and context.driver:
        if scenario.status == "failed" or scenario.status == "errored":
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
        path = os.path.join(context.evidence_dir, f"{screenshot_name}.png")
        context.driver.save_screenshot(path)
        print(f"Screenshot saved to: {path}")
