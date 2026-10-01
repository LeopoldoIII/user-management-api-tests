Feature: PUT /users/{email} — Update User

  # ─────────────────────────────────────────────────────────
  # Happy path — includes persistence verification via GET
  # ─────────────────────────────────────────────────────────

  @dev @prod
  Scenario: Update an existing user successfully
    Given a user with email "update@loanpro.com" exists
    When I send a PUT request to "/users/update@loanpro.com" with valid updated data
    Then the response status code should be 200
    And the response body should contain the updated user details

  # ─────────────────────────────────────────────────────────
  # Age boundary values (contract: minimum 1, maximum 150)
  # ─────────────────────────────────────────────────────────

  @dev @prod
  Scenario Outline: Update a user with age boundary values
    Given a user with email "update@loanpro.com" exists
    When I send a PUT request to "/users/update@loanpro.com" with age <age>
    Then the response status code should be <status>
    Examples:
      | age | status |
      | 0   | 400    |
      | 1   | 200    |
      | 150 | 200    |
      | 151 | 400    |

  # ─────────────────────────────────────────────────────────
  # Missing required fields
  # ─────────────────────────────────────────────────────────

  @dev @prod
  Scenario Outline: Fail to update a user with missing required fields
    Given a user with email "update@loanpro.com" exists
    When I send a PUT request to "/users/update@loanpro.com" missing the "<field>" field
    Then the response status code should be 400
    And the response body should contain a validation error message
    Examples:
      | field |
      | name  |
      | email |
      | age   |

  @dev @prod
  Scenario: Fail to update a user with empty request body
    Given a user with email "update@loanpro.com" exists
    When I send a PUT request to "/users/update@loanpro.com" with an empty body
    Then the response status code should be 400
    And the response body should contain a validation error message

  # ─────────────────────────────────────────────────────────
  # Format and conflict errors
  # ─────────────────────────────────────────────────────────

  @dev @prod
  Scenario: Fail to update a user with invalid data — age out of range
    Given a user with email "update_invalid@example.com" exists
    When I send a PUT request to "/users/update_invalid@example.com" with an invalid age
    Then the response status code should be 400
    And the response body should contain a validation error message

  @dev @prod
  Scenario: Fail to update a user with invalid email format in body
    Given a user with email "update@loanpro.com" exists
    When I send a PUT request to "/users/update@loanpro.com" with an invalid email format "not-an-email"
    Then the response status code should be 400
    And the response body should contain a validation error message

  # ─────────────────────────────────────────────────────────
  # Not found and conflict
  # ─────────────────────────────────────────────────────────

  @dev @prod
  Scenario: Fail to update a non-existent user
    When I send a PUT request to "/users/nonexistent@loanpro.com" with valid data
    Then the response status code should be 404
    And the response body should contain a user not found error message

  @dev @prod
  Scenario: Fail to update a user to a duplicate email
    Given a user with email "user1@loanpro.com" exists
    And a user with email "user2@loanpro.com" exists
    When I send a PUT request to "/users/user1@loanpro.com" changing the email to "user2@loanpro.com"
    Then the response status code should be 409
    And the response body should contain a duplicate email error message
