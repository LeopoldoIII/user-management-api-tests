Feature: GET /users and GET /users/{email} — List and Retrieve Users

  # ─────────────────────────────────────────────────────────
  # GET /users — list all users
  # ─────────────────────────────────────────────────────────

  @dev @prod
  Scenario: List empty list of users — validate response is a JSON array
    When I send a GET request to "/users"
    Then the response status code should be 200
    And the response body should be a JSON array

  @dev @prod
  Scenario: List multiple users successfully
    Given 10 users are created in the system
    When I send a GET request to "/users"
    Then the response status code should be 200
    And the response body should be a JSON array
    And the response body should contain at least 10 users

  # ─────────────────────────────────────────────────────────
  # GET /users/{email} — get user by email
  # ─────────────────────────────────────────────────────────

  @dev @prod
  Scenario: Get an existing user by email
    Given a user with email "existing@loanpro.com" exists
    When I send a GET request to "/users/existing@loanpro.com"
    Then the response status code should be 200
    And the response body should contain the user details

  @dev @prod @BUG-004
  Scenario: Fail to get a non-existent user
    When I send a GET request to "/users/nonexistent@loanpro.com"
    Then the response status code should be 404
    And the response body should contain a user not found error message
