Feature: E-Commerce Negative Shipping Details
  As a logged-in user on the shipping page
  I want to attempt to submit empty shipping details
  So that I can verify field validation works correctly

  @web @negative
  Scenario: Validate HTML5 required fields during shipping submit
    Given the user has products in cart and navigated to shipping page
    When the user clicks the submit order button without filling fields
    Then the page should not navigate
    And the native validation message "Please fill out this field" should be shown on shipping fields:
      | Element                      | XPath                                       |
      | Phone                        | //*[@id="phone"]                            |
      | Address                      | //*[@id="shippingForm"]/div[2]/input        |
      | City                         | //*[@id="shippingForm"]/div[3]/input        |
      | Country                      | //*[@id="countries_dropdown_menu"]          |
    And the user takes a screenshot as "09_shipping_validation_errors"
