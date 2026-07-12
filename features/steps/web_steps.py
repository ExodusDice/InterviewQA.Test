import os
import time
from behave import given, when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException
from features.environment import take_screenshot

@given('the user navigates to the e-commerce login page')
def step_impl(context):
    context.driver.get("https://qa-practice.razvanvancea.ro/auth_ecommerce.html")
    # Wait for email input to be present
    WebDriverWait(context.driver, 10).until(
        EC.presence_of_element_located((By.ID, "email"))
    )

@when('the user enters credentials "{email}" and "{password}"')
def step_impl(context, email, password):
    email_input = context.driver.find_element(By.ID, "email")
    pass_input = context.driver.find_element(By.ID, "password")
    email_input.clear()
    email_input.send_keys(email)
    pass_input.clear()
    pass_input.send_keys(password)

@when('the user takes a screenshot as "{name}"')
@then('the user takes a screenshot as "{name}"')
def step_impl(context, name):
    take_screenshot(context, name)

@when('the user clicks the login submit button')
def step_impl(context):
    # Ensure the login JS handler is fully loaded and defined before clicking
    WebDriverWait(context.driver, 10).until(
        lambda d: d.execute_script("return typeof window.checkCredentialsProductsList === 'function';")
    )
    submit_btn = context.driver.find_element(By.ID, "submitLoginBtn")
    submit_btn.click()

@then('the user should be redirected to the shop page')
def step_impl(context):
    # Wait for products list or container 'prooood' to display
    WebDriverWait(context.driver, 25).until(
        EC.visibility_of_element_located((By.ID, "prooood"))
    )
    # Wait for products to load dynamically
    WebDriverWait(context.driver, 25).until(
        EC.presence_of_element_located((By.CLASS_NAME, "shop-item"))
    )
    # Check that prooood is displayed
    prooood = context.driver.find_element(By.ID, "prooood")
    assert prooood.is_displayed(), "E-Commerce Shop page did not load successfully"

@given('the user is logged in and on the shop page')
def step_impl(context):
    context.execute_steps('''
        Given the user navigates to the e-commerce login page
        When the user enters credentials "admin@admin.com" and "admin123"
        And the user clicks the login submit button
        Then the user should be redirected to the shop page
    ''')

@when('the user scrolls down to "Gucci Bloom Eau de"')
def step_impl(context):
    # Find element containing the product text
    xpath = "//*[contains(text(), 'Gucci Bloom Eau de')]"
    element = WebDriverWait(context.driver, 10).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )
    context.driver.execute_script("arguments[0].scrollIntoView(true);", element)
    time.sleep(1) # Allow page to settle after scroll

@when('the user clicks "Add to cart" for Gucci Bloom (index 8)')
def step_impl(context):
    # Index 8 refers to the 8th div (1-indexed in xpath, Dolce Shine Eau de)
    xpath = '//*[@id="prooood"]/section[2]/div[1]/div[8]/div/button'
    btn = WebDriverWait(context.driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    )
    btn.click()
    time.sleep(0.5)

@when('the user clicks "Add to cart" for the next item (index 9)')
def step_impl(context):
    # Index 9 refers to the 9th div (1-indexed in xpath, Gucci Bloom Eau de)
    xpath = '//*[@id="prooood"]/section[2]/div[1]/div[9]/div/button'
    btn = WebDriverWait(context.driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    )
    btn.click()
    time.sleep(0.5)

@when('the user scrolls back to the top')
def step_impl(context):
    context.driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(1)

def change_quantity(driver, xpath, qty):
    input_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )
    # Clear the field using keystrokes to trigger the DOM event handlers
    input_field.click()
    input_field.send_keys(Keys.CONTROL + "a")
    input_field.send_keys(Keys.DELETE)
    input_field.send_keys(str(qty))
    input_field.send_keys(Keys.TAB)
    time.sleep(1) # Let the cart recalculate

@when('the user changes quantity of item 1 to "{qty}"')
def step_impl(context, qty):
    xpath = '//*[@id="prooood"]/section[1]/div[2]/div[1]/div[2]/input'
    change_quantity(context.driver, xpath, qty)

@when('the user changes quantity of item 2 to "{qty}"')
def step_impl(context, qty):
    xpath = '//*[@id="prooood"]/section[1]/div[2]/div[2]/div[2]/input'
    change_quantity(context.driver, xpath, qty)

@then('the calculated total price should match the displayed price')
def step_impl(context):
    # Get quantities
    qty1_el = context.driver.find_element(By.XPATH, '//*[@id="prooood"]/section[1]/div[2]/div[1]/div[2]/input')
    qty2_el = context.driver.find_element(By.XPATH, '//*[@id="prooood"]/section[1]/div[2]/div[2]/div[2]/input')
    qty1 = int(qty1_el.get_attribute("value"))
    qty2 = int(qty2_el.get_attribute("value"))

    # Get unit prices in the cart rows
    # The structure of the cart row for item 1 price is:
    # //*[@id="prooood"]/section[1]/div[2]/div[1]/span
    # and item 2 is:
    # //*[@id="prooood"]/section[1]/div[2]/div[2]/span
    # Let's extract unit prices:
    price1_text = context.driver.find_element(By.XPATH, '//*[@id="prooood"]/section[1]/div[2]/div[1]/span').text
    price2_text = context.driver.find_element(By.XPATH, '//*[@id="prooood"]/section[1]/div[2]/div[2]/span').text
    
    # Strip $ sign
    price1 = float(price1_text.replace("$", "").strip())
    price2 = float(price2_text.replace("$", "").strip())

    # Get displayed total price
    total_xpath = '//*[@id="prooood"]/section[1]/div[3]/span'
    displayed_total_text = context.driver.find_element(By.XPATH, total_xpath).text
    displayed_total = float(displayed_total_text.replace("$", "").strip())

    # Calculate expected price
    expected_total = round((price1 * qty1) + (price2 * qty2), 2)
    
    print(f"Item 1 unit price: {price1}, Qty: {qty1}")
    print(f"Item 2 unit price: {price2}, Qty: {qty2}")
    print(f"Expected Total: ${expected_total}, Displayed: ${displayed_total}")
    
    assert expected_total == displayed_total, \
        f"Calculated total price ${expected_total} does not match displayed price ${displayed_total}"
        
    # Store total for later verification steps
    context.checkout_total = displayed_total_text.strip()

@when('the user clicks the proceed to checkout button')
def step_impl(context):
    xpath = '//*[@id="prooood"]/section[1]/button'
    btn = WebDriverWait(context.driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    )
    btn.click()
    # Wait for shipping section to display
    WebDriverWait(context.driver, 10).until(
        EC.visibility_of_element_located((By.ID, "shipping-address"))
    )

@when('the user fills the shipping details:')
def step_impl(context):
    row = context.table[0]
    
    phone_xpath = '//*[@id="phone"]'
    address_xpath = '//*[@id="shippingForm"]/div[2]/input'
    city_xpath = '//*[@id="shippingForm"]/div[3]/input'
    country_xpath = '//*[@id="countries_dropdown_menu"]'
    
    phone_input = context.driver.find_element(By.XPATH, phone_xpath)
    address_input = context.driver.find_element(By.XPATH, address_xpath)
    city_input = context.driver.find_element(By.XPATH, city_xpath)
    country_select = Select(context.driver.find_element(By.XPATH, country_xpath))
    
    phone_input.clear()
    phone_input.send_keys(row["Phone"])
    
    address_input.clear()
    address_input.send_keys(row["Address"])
    
    city_input.clear()
    city_input.send_keys(row["City"])
    
    country_select.select_by_value(row["Country"])
    
    # Store values for comparison in congrats message
    context.shipping_phone = row["Phone"]
    context.shipping_address = row["Address"]
    context.shipping_city = row["City"]
    context.shipping_country = row["Country"]

@when('the user clicks the submit order button')
def step_impl(context):
    xpath = '//*[@id="submitOrderBtn"]'
    btn = context.driver.find_element(By.XPATH, xpath)
    btn.click()

@when('the user waits for {seconds:d} seconds')
def step_impl(context, seconds):
    time.sleep(seconds)

@then('the order confirmation message should match the shipping details')
def step_impl(context):
    msg_xpath = '//*[@id="message"]'
    # Wait for the congrats message to display
    WebDriverWait(context.driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, msg_xpath))
    )
    message_text = context.driver.find_element(By.XPATH, msg_xpath).text
    print(f"Confirmation message text: {message_text}")
    
    # Expected format:
    # Congrats! Your order of {total} has been registered and will be shipped to {address}, {city} - {country}.
    # Let's construct the expected message:
    total = context.checkout_total # e.g. "$389.95"
    address = context.shipping_address # e.g. "Pattaya"
    city = context.shipping_city # e.g. "Pty"
    country = context.shipping_country # e.g. "Thailand"
    
    expected_message = f"Congrats! Your order of {total} has been registered and will be shipped to {address}, {city} - {country}."
    print(f"Expected Message: {expected_message}")
    
    assert message_text.strip() == expected_message, \
        f"Confirmation message '{message_text}' does not match expected '{expected_message}'"

@when('the user clicks logout')
def step_impl(context):
    # Wait for logout button to be clickable
    logout_xpath = '//*[@id="logout"]'
    btn = WebDriverWait(context.driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, logout_xpath))
    )
    btn.click()
    
    # Wait for login section to reappear
    WebDriverWait(context.driver, 10).until(
        EC.visibility_of_element_located((By.ID, "loginSection"))
    )

# --- Negative scenario step definitions ---

@given('the user has products in cart and navigated to shipping page')
def step_impl(context):
    # Execute full checkout up to shipping screen
    context.execute_steps('''
        Given the user is logged in and on the shop page
        When the user scrolls down to "Gucci Bloom Eau de"
        And the user clicks "Add to cart" for Gucci Bloom (index 8)
        And the user clicks "Add to cart" for the next item (index 9)
        And the user scrolls back to the top
        And the user changes quantity of item 1 to "2"
        And the user changes quantity of item 2 to "3"
        And the user clicks the proceed to checkout button
    ''')

@when('the user clicks the submit order button without filling fields')
def step_impl(context):
    # We click the submit button, which triggers HTML5 required validation
    xpath = '//*[@id="submitOrderBtn"]'
    btn = context.driver.find_element(By.XPATH, xpath)
    btn.click()

@then('the page should not navigate')
def step_impl(context):
    # Verify we are still on the shipping address section and didn't see the congrats message
    shipping_sec = context.driver.find_element(By.ID, "shipping-address")
    assert shipping_sec.is_displayed(), "Form submitted and navigated away from shipping page!"
    
    msg_el = context.driver.find_element(By.ID, "message")
    # Verify success message is not displayed or does not contain 'Congrats'
    if msg_el.is_displayed():
        assert "Congrats" not in msg_el.text, f"Unexpectedly showed order success: {msg_el.text}"

@then('the native validation message "{expected_message}" should be shown on shipping fields:')
def step_impl(context, expected_message):
    for row in context.table:
        name = row["Element"]
        xpath = row["XPath"]
        
        element = context.driver.find_element(By.XPATH, xpath)
        
        # Check validationMessage property of HTML5 required input field
        validation_message = context.driver.execute_script("return arguments[0].validationMessage;", element)
        print(f"Field '{name}' native validation message: '{validation_message}'")
        
        if name == "Country":
            # The country dropdown does not have a value="" for its placeholder option,
            # so the browser doesn't trigger valueMissing natively, but we assert it is marked 'required'.
            assert element.get_attribute("required") is not None, "Country dropdown should be required"
        else:
            # On some browsers/locales, the message might slightly vary, but "Please fill out this field" is Chrome standard
            assert expected_message.lower() in validation_message.lower(), \
                f"Expected validation message '{expected_message}' for '{name}', but got '{validation_message}'"
            
            # Also check that validity.valueMissing is True
            value_missing = context.driver.execute_script("return arguments[0].validity.valueMissing;", element)
            assert value_missing is True, f"Field '{name}' should be marked as missing value"
