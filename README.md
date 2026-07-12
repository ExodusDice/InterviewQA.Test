# Finkub QA Engineering Assignment - Cucumber/Selenium Automation

This repository contains the completed QA automation test suite using the **Cucumber (Behave) Framework** in **Python & Selenium**, containerized using **Docker** with **GitHub Actions CI/CD integration**.

## Tech Stack
*   **Language**: Python 3.11+
*   **Test Runner**: Behave (Gherkin-based BDD Cucumber framework)
*   **UI Automation**: Selenium WebDriver 4
*   **API Client**: Python `requests` library
*   **Containerization**: Docker
*   **Reporting**: Node.js `cucumber-html-reporter`
*   **CI/CD**: GitHub Actions

---

## Project Structure
```
Finkub Project/
├── .github/
│   └── workflows/
│       └── test.yml           # GitHub Actions workflow
├── features/
│   ├── steps/
│   │   ├── api_steps.py       # Python REST API test step definitions
│   │   └── web_steps.py       # Python Web UI test step definitions
│   ├── 01_login.feature       # Question 1: Login scenarios
│   ├── 02_checkout.feature    # Question 2 & 3: Purchase flow & positive shipping details
│   ├── 03_shipping_neg.feature# Question 4: Negative shipping details (HTML5 validation)
│   ├── 04_api.feature         # Question 5: Backend API test scenarios
│   └── environment.py         # Selenium webdriver hooks & screenshot evidence setup
├── evidence/                  # Generated test outputs (Screenshots & HTML Dashboard)
├── requirements.txt           # Python packages list
├── package.json               # Node.js dependencies for report generator
├── generate_report.js         # Custom script to build Cucumber HTML Dashboard
├── Dockerfile                 # Packages tests with headless Chromium for CI runs
└── README.md                  # Project documentation
```

---

## 1. The Goal: What does this suite actually test?

This automation suite is designed to fully validate user-facing E-Commerce purchase flows and verify the backend employee database REST API endpoints. Below is the detailed list of test cases covered by the suite:

### A. Web UI Browser Automation (E-Commerce Platform)
*   **Scenario 1: Successful Login**
    *   Navigates to the e-commerce login page.
    *   Enters valid credentials (`admin@admin.com` / `admin123`).
    *   Takes screenshot evidence of filled credentials (`evidence/01_login_filled.png`).
    *   Clicks the login submit button.
    *   Verifies successful redirection to the main shop page by checking that the products catalog has loaded.
    *   Takes a screenshot of the landing catalog page (`evidence/02_login_success.png`).
*   **Scenario 2: Successful Product Addition, Quantity Modification, and Checkout**
    *   Navigates to the shop page and scrolls down to locate the element "Gucci Bloom Eau de".
    *   Clicks "Add to cart" for product index 8 (Dior J'adore) and index 9 (Dolce Shine) using the required XPath selectors.
    *   Scrolls back to the top and captures screenshot evidence (`evidence/03_cart_items_added.png`).
    *   Modifies the quantities in the shopping cart (item 1 changed to "2" and item 2 changed to "3").
    *   Dynamically calculates the expected total price based on unit prices and quantities, and asserts that the calculated sum matches the displayed UI cart total ($389.95).
    *   Captures screenshot evidence of the updated quantities and totals (`evidence/04_cart_quantities_changed.png`).
    *   Clicks the "Proceed to Checkout" button.
    *   Fills in the shipping address details (Phone: `12345678`, Address: `Pattaya`, City: `Pty`, Country: `Thailand`).
    *   Captures screenshot evidence of the filled checkout form (`evidence/06_shipping_details_filled.png`).
    *   Clicks the "Submit Order" button.
    *   Waits for 5 seconds to allow order processing and captures screenshot evidence of the final completion (`evidence/07_order_completed.png`).
    *   Asserts that the registration confirmation message exactly matches the delivery details.
    *   Clicks the logout button and captures screenshot evidence of the redirected login page (`evidence/08_logged_out.png`).
*   **Scenario 3: Negative Shipping Validation**
    *   Navigates to the checkout page with items in the cart.
    *   Attempts to click "Submit Order" without filling in the required inputs.
    *   Asserts that the browser natively blocks the form submission (checks HTML5 native required field validation tooltips: "Please fill out this field").
    *   Captures screenshot evidence of the browser validation tooltips (`evidence/09_shipping_validation_errors.png`).

### B. Backend REST API Validation (Employee Mock Database)
*   **Scenario 4: Create Employee successfully (Positive)**
    *   Sends a `POST` request to `/api/v1/employees` with a valid JSON payload containing first name, last name, and email.
    *   Asserts that the response status code is `201 Created`.
    *   Sends a `GET` request to `/api/v1/employees` and verifies that the new employee entry is present in the database, verifying the auto-generated unique ID.
*   **Scenario 5: Create Employee with invalid email (Negative)**
    *   Sends a `POST` request to `/api/v1/employees` with an invalid email address (e.g. `invalidemail`).
    *   Asserts that the response status code is `400 Bad Request`.
    *   Verifies that the JSON response body contains the validation error message `"must be a well-formed email address"`.
*   **Scenario 6: Get Employee by ID (Positive)**
    *   Sends a `GET` request to `/api/v1/employees/1` (fetching a valid existing employee).
    *   Asserts that the response status code is `200 OK`.
    *   Verifies that the returned JSON body contains the correct employee details corresponding to ID 1.
*   **Scenario 7: Get Employee by non-existing ID (Negative)**
    *   Sends a `GET` request to `/api/v1/employees/9999` (fetching an invalid/missing employee).
    *   Asserts that the response status code is `404 Not Found`.
    *   Verifies that the plain-text response body matches the error message `"Employee not found with ID 9999"`.

---

## Setup & Running the Tests

### Prerequisites
Make sure you have Python, Node.js, and Docker installed.

### Step 1: Start the Backend API
Start the target API service inside a Docker container:
```bash
docker run -d --rm --name qa-practice-api -p 8887:8081 rvancea/qa-practice-api:latest
```

### Step 2: Run Tests Locally (headed/headless)
Install dependencies:
```bash
pip install -r requirements.txt
npm install
```

To run tests in **headless mode** (browser in the background):
```bash
# On Windows PowerShell
$env:HEADLESS="true"; python -c "import os, sys, behave.__main__; behave.__main__.main()"
# On Linux/MacOS
HEADLESS=true python -m behave
```

To run tests in **headed mode** (shows the Chrome browser performing clicks):
```bash
# On Windows PowerShell
$env:HEADLESS="false"; python -c "import os, sys, behave.__main__; behave.__main__.main()"
```

### Step 3: Generate the HTML Report
Compile the test results into a beautiful HTML Dashboard:
```bash
node generate_report.js
```
The report will be created at: `evidence/cucumber_report.html`

---

## Running inside Docker

### Step 1: Build the Test Image
```bash
docker build -t behave-selenium-tests .
```

### Step 2: Run the Test Container
Run the tests containerized, using the host's network namespace (so the container can communicate with the backend API on `http://localhost:8887`) and mounting the local `evidence/` folder to retrieve the HTML report and screenshots:
```bash
docker run --rm --net=host -v "F:\Projects\PythonProject\Finkub Project\evidence:/app/evidence" behave-selenium-tests
```
After the run, execute `node generate_report.js` to compile the report.

---

## Continuous Integration (GitHub Actions)
The project includes a pre-configured CI pipeline in `.github/workflows/test.yml` that:
1.  Triggers on every commit pushed to `main`/`master` or on Pull Requests.
2.  Launches the `rvancea/qa-practice-api` Docker container.
3.  Builds the Python test Docker image.
4.  Executes the tests inside the container using the host network.
5.  Compiles the `cucumber-html-reporter` HTML dashboard.
6.  Uploads the entire evidence/ folder (including execution screenshots and the generated HTML dashboard) as workflow run artifacts.
