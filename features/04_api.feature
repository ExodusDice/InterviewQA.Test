Feature: Backend API Employee Verification
  As a QA Engineer
  I want to verify the employee REST API endpoints
  So that I can ensure backend services operate correctly

  @api
  Scenario: Create Employee successfully (Positive)
    Given the employee API is available at "http://localhost:8887"
    When the user sends a POST request to "/api/v1/employees" with:
      | firstName | lastName | email            |
      | John      | Doe      | john.doe@test.com|
    Then the API response status code should be 201
    And the response body should contain the created employee details and a new ID

  @api
  Scenario: Create Employee with invalid email (Negative)
    Given the employee API is available at "http://localhost:8887"
    When the user sends a POST request to "/api/v1/employees" with:
      | firstName | lastName | email        |
      | Jane      | Doe      | invalidemail |
    Then the API response status code should be 400
    And the response validation message should mention "must be a well-formed email address"

  @api
  Scenario: Get Employee by ID (Positive)
    Given the employee API is available at "http://localhost:8887"
    And a valid employee exists and has ID 1
    When the user sends a GET request to "/api/v1/employees/1"
    Then the API response status code should be 200
    And the response body should contain the employee details for ID 1

  @api
  Scenario: Get Employee by non-existing ID (Negative)
    Given the employee API is available at "http://localhost:8887"
    When the user sends a GET request to "/api/v1/employees/9999"
    Then the API response status code should be 404
    And the response error message should be "Employee not found with ID 9999"
