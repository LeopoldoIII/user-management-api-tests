Feature: User Management API

  # - ---------------------------------------
  # POST /users
  # ----------------------------------------
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
      #user with numbers*e
      | R2-D2         | R2-D2@loanpro.com         | 10  |

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

  # ----------------------------------------
  # GET /users
  # ----------------------------------------

  @dev @prod
  Scenario: List empty list of users validate response JSON array
    When I send a GET request to "/users"
    Then the response status code should be 200
    And the response body should be a JSON array

  @dev @prod
  Scenario: List multiple users successfully listed
    Given 10 users are created in the system
    When I send a GET request to "/users"
    Then the response status code should be 200
    And the response body should be a JSON array
    And the response body should contain at least 10 users

  # ----------------------------------------
  # GET /users/{email}
  # ----------------------------------------
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

  # ----------------------------------------
  # PUT /users/{email}
  # ----------------------------------------
  @dev @prod
  Scenario: Update an existing user successfully
    Given a user with email "update@loanpro.com" exists
    When I send a PUT request to "/users/update@loanpro.com" with valid updated data
    Then the response status code should be 200
    And the response body should contain the updated user details

  @dev @prod
  Scenario: Fail to update a user with invalid data
    Given a user with email "update_invalid@example.com" exists
    When I send a PUT request to "/users/update_invalid@example.com" with an invalid age
    Then the response status code should be 400
    And the response body should contain a validation error message

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
  Scenario: Fail to update a user with invalid email format in body
    Given a user with email "update@loanpro.com" exists
    When I send a PUT request to "/users/update@loanpro.com" with an invalid email format "not-an-email"
    Then the response status code should be 400
    And the response body should contain a validation error message

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

  @dev @prod
  Scenario: Fail to update a user with empty request body
    Given a user with email "update@loanpro.com" exists
    When I send a PUT request to "/users/update@loanpro.com" with an empty body
    Then the response status code should be 400
    And the response body should contain a validation error message

  # ----------------------------------------
  # DELETE /user/{email} *Token
  # ----------------------------------------
  @dev @prod
  Scenario: Delete a user successfully with valid authentication
    Given a user with email "delete@loanpro.com" exists
    When I send a DELETE request to "/users/delete@loanpro.com" with a valid Authentication token
    Then the response status code should be 204

  @dev @prod @BUG-005
  Scenario: Fail to delete a user without authentication
    Given a user with email "noauth@loanpro.com" exists
    When I send a DELETE request to "/users/noauth@loanpro.com" without an Authentication token
    Then the response status code should be 401
    And the response body should contain an authentication error message

  @dev @prod @BUG-005
  Scenario: Fail to delete a user with invalid authentication token
    Given a user with email "invalidauth@loanpro.com" exists
    When I send a DELETE request to "/users/invalidauth@loanpro.com" with an invalid Authentication token
    Then the response status code should be 401
    And the response body should contain an authentication error message

  @dev @prod
  Scenario: Fail to delete a non-existent user
    When I send a DELETE request to "/users/nonexistent@loanpro.com" with a valid Authentication token
    Then the response status code should be 404
    And the response body should contain a user not found error message

  @security @BUG-006
  Scenario Outline: Fail to create a user with malicious payloads (SQLi / XSS)
    When I send a POST request to "/users" with name "<malicious_name>", email "<email>", and age 30
    Then the response status code should be 400
    And the response body should contain a validation error message
    Examples:
      | malicious_name                | email            |
      | Robert'); DROP TABLE users;-- | sqli@loanpro.com |
      | <script>alert("XSS")</script> | xss@loanpro.com  |
      | <h1>HTML Injection</h1>       | html@loanpro.com |

  @security @BUG-007
  Scenario: Fail to create a user with a massive payload
    When I send a POST request to "/users" with a name of 500 characters
    Then the response status code should be 400
    And the response body should contain a validation error message
