import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

def inspect_page():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        print("Navigating to login page...")
        driver.get("https://qa-practice.razvanvancea.ro/auth_ecommerce.html")
        time.sleep(2)
        
        # Save page source to inspect selectors
        with open(os.path.join(script_dir, "login_page_debug.html"), "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Saved login page source to login_page_debug.html")
        
        print("Entering credentials...")
        driver.find_element(By.ID, "email").send_keys("admin@admin.com")
        driver.find_element(By.ID, "password").send_keys("admin123")
        
        # Try finding submit button in different ways
        print("Finding submit button...")
        try:
            submit_btn = driver.find_element(By.ID, "submit")
            print("Found by ID 'submit'")
        except Exception:
            try:
                submit_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
                print("Found by XPATH //button[@type='submit']")
            except Exception:
                submit_btn = driver.find_element(By.XPATH, "//input[@type='submit']")
                print("Found by XPATH //input[@type='submit']")
        
        submit_btn.click()
        time.sleep(3)
        
        print(f"Current URL after login: {driver.current_url}")
        
        # Write post-login page source to see if login succeeded
        with open(os.path.join(script_dir, "post_login_debug.html"), "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Saved post-login page source to post_login_debug.html")
        
        # Print HTML of the page to inspect structure
        # We can find all product names and their add-to-cart buttons
        products = driver.find_elements(By.CLASS_NAME, "card")
        print(f"Found {len(products)} products on page.")
        
        # Print out details of some products
        for idx, prod in enumerate(products[:12]):
            try:
                title = prod.find_element(By.CLASS_NAME, "card-title").text
                button = prod.find_element(By.TAG_NAME, "button")
                print(f"Product {idx}: {title} | button element tag: {button.tag_name}")
            except Exception as e:
                print(f"Product {idx} parsing error: {e}")
                
        # Scroll and add products
        # Click index 8 button (Gucci Bloom Eau de)
        print("Clicking product at index 8 and 9...")
        btn_8 = driver.find_element(By.XPATH, '//*[@id="prooood"]/section[2]/div[1]/div[8]/div/button')
        btn_9 = driver.find_element(By.XPATH, '//*[@id="prooood"]/section[2]/div[1]/div[9]/div/button')
        driver.execute_script("arguments[0].scrollIntoView(true);", btn_8)
        time.sleep(1)
        btn_8.click()
        time.sleep(1)
        btn_9.click()
        time.sleep(1)
        
        # Scroll back to top
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        # Let's inspect the cart section
        cart_html = driver.find_element(By.ID, "prooood").get_attribute("innerHTML")
        with open(os.path.join(script_dir, "cart_section_debug.html"), "w", encoding="utf-8") as f:
            f.write(cart_html)
        print("Cart section HTML saved to cart_section_debug.html")
        
    except Exception as e:
        print(f"Error during inspection: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    inspect_page()
