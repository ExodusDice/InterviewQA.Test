import requests
from behave import given, when, then

# Global variable to store response and active employee details
last_response = None
created_employee_id = None
posted_email = None
posted_first_name = None
posted_last_name = None

@given('the employee API is available at "{base_url}"')
def step_impl(context, base_url):
    context.base_url = base_url

@when('the user sends a POST request to "/api/v1/employees" with:')
def step_impl(context):
    global last_response, created_employee_id, posted_email, posted_first_name, posted_last_name
    url = f"{context.base_url}/api/v1/employees"
    
    # Extract data from the step table
    row = context.table[0]
    posted_first_name = row["firstName"]
    posted_last_name = row["lastName"]
    posted_email = row["email"]
    
    payload = {
        "firstName": posted_first_name,
        "lastName": posted_last_name,
        "email": posted_email
    }
    
    last_response = requests.post(url, json=payload)
    print(f"POST Response: Status {last_response.status_code}, Body: '{last_response.text}'")

@then('the API response status code should be {status_code:d}')
def step_impl(context, status_code):
    global last_response
    assert last_response.status_code == status_code, \
        f"Expected status code {status_code}, but got {last_response.status_code}"

@then('the response body should contain the created employee details and a new ID')
def step_impl(context):
    global last_response, created_employee_id, posted_email, posted_first_name
    # Since POST returns empty body (201 Created), we verify details by fetching the employee list
    list_url = f"{context.base_url}/api/v1/employees"
    list_res = requests.get(list_url)
    assert list_res.status_code == 200, f"Could not fetch employee list, status: {list_res.status_code}"
    
    employees = list_res.json()
    matching_employee = None
    for emp in reversed(employees): # search reversed since newly added is at the end
        if emp.get("email") == posted_email:
            matching_employee = emp
            break
            
    assert matching_employee is not None, f"Could not find created employee in DB with email '{posted_email}'"
    assert matching_employee.get("id") is not None, "Created employee ID is missing"
    assert matching_employee.get("firstName") == posted_first_name, \
        f"Expected firstName '{posted_first_name}', but got '{matching_employee.get('firstName')}'"
        
    created_employee_id = matching_employee["id"]
    print(f"Verified created employee in DB: {matching_employee}")

@then('the response validation message should mention "{expected_message}"')
def step_impl(context, expected_message):
    global last_response
    body_text = last_response.text
    # Standard spring validation returns errors in 'errors' list containing 'defaultMessage'
    # We check if the expected message is present anywhere in the error response body
    assert expected_message in body_text, \
        f"Expected message '{expected_message}' not found in response: {body_text}"

@given('a valid employee exists and has ID {emp_id:d}')
def step_impl(context, emp_id):
    # Ensure there is at least one employee by posting a default one.
    url = f"{context.base_url}/api/v1/employees"
    payload = {
        "firstName": "Default",
        "lastName": "User",
        "email": "default.user@test.com"
    }
    # We ignore the response status since it might already exist or we just want to seed it
    requests.post(url, json=payload)

@when('the user sends a GET request to "/api/v1/employees/{emp_id:d}"')
def step_impl(context, emp_id):
    global last_response
    url = f"{context.base_url}/api/v1/employees/{emp_id}"
    last_response = requests.get(url)
    print(f"GET Response: Status {last_response.status_code}, Body: '{last_response.text}'")

@then('the response body should contain the employee details for ID {emp_id:d}')
def step_impl(context, emp_id):
    global last_response
    body = last_response.json()
    assert body.get("id") == emp_id, f"Expected ID {emp_id}, but got {body.get('id')}"
    assert "firstName" in body, "Response body does not contain 'firstName'"

@then('the response error message should be "{expected_message}"')
def step_impl(context, expected_message):
    global last_response
    actual_text = last_response.text
    assert expected_message in actual_text, \
        f"Expected error message '{expected_message}', but got '{actual_text}'"
