Feature: Security — Input Validation and Abuse Prevention

  # ─────────────────────────────────────────────────────────
  # NOTE on BUG-006 and BUG-007
  # ─────────────────────────────────────────────────────────
  # The OpenAPI contract does NOT define maxLength, pattern, or sanitization
  # rules for the 'name' field (contract_api.yml, CreateUserRequest schema).
  # Therefore a 201 response for these payloads is technically spec-compliant.
  #
  # These scenarios are kept as security *recommendations*:
  #   - If the API returns 201 → open a Contract Gap ticket to add input
  #     constraints to the spec before treating it as a server bug.
  #   - If the API returns 400 → this is a bonus defence-in-depth behaviour.
  #
  # Tags: @dev @prod @security so these run in the env jobs AND can be
  # filtered independently with --tags=@security.
  # ─────────────────────────────────────────────────────────

  @dev @prod @security
  Scenario Outline: API response to malicious payloads (SQLi / XSS) — contract gap
    When I send a POST request to "/users" with name "<malicious_name>", email "<email>", and age 30
    Then the response status code should be 400
    And the response body should contain a validation error message
    Examples:
      | malicious_name                | email            |
      | Robert'); DROP TABLE users;-- | sqli@loanpro.com |
      | <script>alert("XSS")</script> | xss@loanpro.com  |
      | <h1>HTML Injection</h1>       | html@loanpro.com |

  @dev @prod @security
  Scenario: API response to a massive payload — contract gap
    When I send a POST request to "/users" with a name of 500 characters
    Then the response status code should be 400
    And the response body should contain a validation error message
