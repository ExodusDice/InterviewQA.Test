Feature: E-Commerce Login
  As a registered user
  I want to login to the e-commerce website
  So that I can purchase products

  @web @login
  Scenario: Successful Login
    Given the user navigates to the e-commerce login page
    When the user enters credentials "admin@admin.com" and "admin123"
    And the user takes a screenshot as "01_login_filled"
    And the user clicks the login submit button
    Then the user should be redirected to the shop page
    And the user takes a screenshot as "02_login_success"
