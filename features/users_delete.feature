Feature: DELETE /users/{email} — Delete User

  # ─────────────────────────────────────────────────────────
  # Happy path — requires valid Authentication header
  # ─────────────────────────────────────────────────────────

  @dev @prod
  Scenario: Delete a user successfully with valid authentication
    Given a user with email "delete@loanpro.com" exists
    When I send a DELETE request to "/users/delete@loanpro.com" with a valid Authentication token
    Then the response status code should be 204

  # ─────────────────────────────────────────────────────────
  # Authentication failures  (BUG-005: endpoint ignores token)
  # ─────────────────────────────────────────────────────────

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

  # ─────────────────────────────────────────────────────────
  # Not found
  # ─────────────────────────────────────────────────────────

  @dev @prod
  Scenario: Fail to delete a non-existent user
    When I send a DELETE request to "/users/nonexistent@loanpro.com" with a valid Authentication token
    Then the response status code should be 404
    And the response body should contain a user not found error message
