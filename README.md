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

## Test Scenarios Covered

### 1. Web UI Tests (E-Commerce Platform)
The UI tests target the public environment `https://qa-practice.razvanvancea.ro/auth_ecommerce.html`:
*   **Scenario 1 (Successful Login)**: Navigates to the login page, enters credentials (`admin@admin.com`/`admin123`), takes a screenshot, submits, and verifies redirection to the shop. Saves screenshot evidence of success.
*   **Scenario 2 (Shopping Flow & Checkout)**:
    *   Scrolls down to the product "Gucci Bloom Eau de".
    *   Clicks "Add to cart" for product index 8 (Dior J'adore) and index 9 (Dolce Shine Eau de) using the requested XPath selectors.
    *   Scrolls back to top and takes a screenshot.
    *   Modifies quantities of item 1 to `2` and item 2 to `3` in the cart inputs.
    *   Verifies that the calculated total price (Unit Price * Quantity) matches the total price displayed in the cart span.
    *   Proceeds to checkout, inputs shipping details (Phone, Address: Pattaya, City: Pty, Country: Thailand), and submits order.
    *   Waits 5 seconds and validates the message: `Congrats! Your order of $389.95 has been registered and will be shipped to Pattaya, Pty - Thailand.`.
    *   Logs out and saves screenshots at each critical milestone.
*   **Scenario 3 (Negative Shipping Details)**: Attempts to submit the shipping details form with empty inputs and verifies that HTML5 native validation blocks form submission (checks native validation messages on required input elements).

### 2. Backend REST API Tests
The API tests target the mock backend container running on `http://localhost:8887`:
*   **POST /api/v1/employees**:
    *   *Positive*: Creates a new employee (returns 201 Created), then validates that the employee is stored in the database by checking the `GET /api/v1/employees` endpoint.
    *   *Negative*: Attempts creation with an invalid email format (e.g. `invalidemail`), verifies response status is 400 Bad Request, and validates the `defaultMessage` containing `"must be a well-formed email address"`.
*   **GET /api/v1/employees/{id}**:
    *   *Positive*: Fetches an existing employee ID (status 200) and asserts their name.
    *   *Negative*: Fetches a non-existing employee ID (e.g. `9999`), asserts status 404, and validates the plain text message `"Employee not found with ID 9999"`.

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
6.  Uploads the entire `evidence/` folder (HTML report + 9 screenshots) as run artifacts.
