Feature: POST /users — Create User

  # ─────────────────────────────────────────────────────────
  # Happy path
  # ─────────────────────────────────────────────────────────

  @dev @prod
  Scenario Outline: Create a new user successfully
    When I send a POST request to "/users" with name "<name>", email "<email>", and age <age>
    Then the response status code should be 201
    And the response body should contain the created user details
    Examples:
      | name          | email                     | age |
      | John Doe      | john.doe@loanpro.com      | 30  |
      | Jane TT       | jane.TT@loanpro.com       | 25  |
      | Alice Johnson | alice.johnson@loanpro.com | 40  |
      | Bob bb        | bob.brown@loanpro.com     | 55  |
      | Charlie Davis | charlie.davis@loanpro.com | 22  |
      # user with alphanumeric name
      | R2-D2         | R2-D2@loanpro.com         | 10  |

  # ─────────────────────────────────────────────────────────
  # Age boundary values (contract: minimum 1, maximum 150)
  # ─────────────────────────────────────────────────────────

  @dev @prod
  Scenario Outline: Validate user age with valid/invalid age values
    When I send a POST request to "/users" with age <age>
    Then the response status code should be <status>
    Examples:
      | age | status |
      | 1   | 201    |
      | 0   | 400    |
      | -5  | 400    |
      | 150 | 201    |
      | 151 | 400    |

  # ─────────────────────────────────────────────────────────
  # Missing required fields
  # ─────────────────────────────────────────────────────────

  @dev @prod
  Scenario Outline: Fail to create a user with missing required fields
    When I send a POST request to "/users" missing the "<field>" field
    Then the response status code should be 400
    And the response body should contain a validation error message
    Examples:
      | field |
      | name  |
      | email |
      | age   |

  @dev @prod
  Scenario: Fail to create a user with empty request body
    When I send a POST request to "/users" with an empty body
    Then the response status code should be 400
    And the response body should contain a validation error message

  # ─────────────────────────────────────────────────────────
  # Conflict and format errors
  # ─────────────────────────────────────────────────────────

  @dev @prod @BUG-001
  Scenario Outline: Fail to create a user with a duplicate email
    Given a user with email "<duplicate_email>" already exists
    When I send a POST request to "/users" with the email "<duplicate_email>"
    Then the response status code should be 409
    And the response body should contain a duplicate email error message
    Examples:
      | duplicate_email           |
      | hannah.irving@loanpro.com |
      | george.harris@loanpro.com |

  @dev @prod @BUG-002
  Scenario Outline: Fail to create a user with invalid email format
    When I send a POST request to "/users" with an invalid email format "<invalid_email>"
    Then the response status code should be 400
    And the response body should contain a validation error message
    Examples:
      | invalid_email       |
      | not-an-email        |
      | r2d2@xvhows@#$@.com |
