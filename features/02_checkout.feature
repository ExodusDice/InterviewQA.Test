Feature: E-Commerce Product Checkout Flow
  As a logged-in user
  I want to add products to the cart, modify their quantities, and complete the order
  So that I can verify the checkout and shipping process

  @web @checkout
  Scenario: Successful Product Addition and Checkout Flow
    Given the user is logged in and on the shop page
    When the user scrolls down to "Gucci Bloom Eau de"
    And the user clicks "Add to cart" for Gucci Bloom (index 8)
    And the user clicks "Add to cart" for the next item (index 9)
    And the user scrolls back to the top
    Then the user takes a screenshot as "03_cart_items_added"
    When the user changes quantity of item 1 to "2"
    And the user changes quantity of item 2 to "3"
    Then the calculated total price should match the displayed price
    And the user takes a screenshot as "04_cart_quantities_changed"
    When the user clicks the proceed to checkout button
    Then the user takes a screenshot as "05_shipping_page"
    When the user fills the shipping details:
      | Phone     | Address   | City | Country  |
      | 12345678  | Pattaya   | Pty  | Thailand |
    Then the user takes a screenshot as "06_shipping_details_filled"
    When the user clicks the submit order button
    And the user waits for 5 seconds
    Then the user takes a screenshot as "07_order_completed"
    And the order confirmation message should match the shipping details
    When the user clicks logout
    Then the user takes a screenshot as "08_logged_out"
