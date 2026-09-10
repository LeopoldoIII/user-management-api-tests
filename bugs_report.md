# Bugs Report — User Management API

## Status

| Environment | Tests executed | Bugs found |
|-------------|----------------|------------|
| dev         | Yes            | 7          |
| prod        | Yes            | 7          |

---

## Bugs

### [BUG-001] — Server crashes with 500 when creating a user with a duplicate email

- **Environment:** dev/prod
- **Endpoint:** `POST /users`
- **Tag:** `@BUG-001`
- **Scenario:** Fail to create a user with a duplicate email
- **Expected behavior (contract):** Status 409 Conflict with an ErrorResponse body.
- **Actual behavior:** Status 500 Internal Server Error. The server crashes and does not return a JSON body.
- **Evidence:** Docker logs show a 500 error immediately after the second POST request.

### [BUG-002] — Server crashes with 500 on invalid email formats

- **Environment:** dev/prod
- **Endpoint:** `POST /users`
- **Tag:** `@BUG-002`
- **Scenario:** Fail to create a user with invalid email format
- **Expected behavior (contract):** Status 400 Bad Request with a validation error message.
- **Actual behavior:** Status 500 Internal Server Error. The server fails to handle the bad string and crashes instead
  of returning a clean validation error.
- **Evidence:** The test fails because we expected a 400 but got a 500. Happens with both `"not-an-email"` and
  `"r2d2@xvhows@#$@.com"`.

### [BUG-003] — Documentation Typo: POST 400 Error shows "User not found"

- **Environment:** N/A (Documentation/Contract)
- **Endpoint:** `POST /users`
- **Tag:** Ninguno (Documentación)
- **Scenario:** OpenAPI Contract verification
- **Expected behavior (contract):** The example for a 400 validation error on user creation should reflect a validation
  issue (e.g., "Invalid age" or "Missing name").
- **Actual behavior:** The Swagger/OpenAPI `contract_api.yml` shows `{"error": "User not found"}` as the example for a
  400 Bad Request on a POST. This makes no logical sense since we are creating a user, not fetching one.
- **Evidence:** Line 45-50 of `contract_api.yml`. Looks like a copy-paste error from the GET/DELETE endpoints.

### [BUG-004] — GET on a non-existent user crashes with 500 instead of returning 404

- **Environment:** dev, prod
- **Endpoint:** `GET /users/{email}`
- **Tag:** `@BUG-004`
- **Scenario:** Fail to get a non-existent user
- **Expected behavior (contract):** Status 404 Not Found with an ErrorResponse body.
- **Actual behavior:** Status 500 Internal Server Error. The server crashes and returns `{"error": "Internal server error"}` instead of a 404 error.
- **Evidence:** The test requesting `/users/nonexistent@loanpro.com` receives a 500 status code instead of the expected 404 error object.

### [BUG-005] — DELETE endpoint processes requests without validating token

- **Environment:** dev, prod
- **Endpoint:** `DELETE /users/{email}`
- **Tag:** `@BUG-005`
- **Scenario:** Fail to delete a user without authentication / Fail to delete a user with invalid authentication token
- **Expected behavior (contract):** Status 401 Unauthorized with an ErrorResponse body since an Authentication header is
  required.
- **Actual behavior:** Status 204 No Content. The server successfully deletes the user (or pretends to) even if the
  Authentication token is missing or completely invalid.
- **Evidence:** The test requesting a DELETE without an Authentication header receives a 204 status code, meaning the
  endpoint is unprotected and anyone can delete users.

---

### [BUG-006] — API is vulnerable to malicious payloads (SQLi, XSS, HTML Injection)

- **Environment:** dev, prod
- **Endpoint:** `POST /users`
- **Tag:** `@BUG-006`
- **Scenario:** Fail to create a user with malicious payloads (SQLi / XSS)
- **Expected behavior (contract):** Status 400 Bad Request since names shouldn't allow arbitrary scripts or SQL
  injection sequences (or at least they should be sanitized/rejected).
- **Actual behavior:** The server accepts the malicious payloads without validation, returning 201 Created or failing
  internally.
- **Evidence:** Tests inserting `<script>`, `<h1>`, and SQL drop table commands do not receive the expected 400
  validation error.

### [BUG-007] — API is vulnerable to large payload

- **Environment:** dev, prod
- **Endpoint:** `POST /users`
- **Tag:** `@BUG-007`
- **Scenario:** Fail to create a user with a massive payload
- **Expected behavior (contract):** Status 400 Bad Request with a payload too large or validation error message.
- **Actual behavior:** The server attempts to process the massive payload (e.g. name with 500 characters), potentially
  causing performance degradation or a 500 error instead of a clean 400.
- **Evidence:** A test sending a massive 500-character name fails to receive a proper 400 Bad Request response.

---

## Template for new bugs

```
### [BUG-XXX] — Title

- **Environment:**
- **Endpoint:**
- **Tag:** `@BUG-XXX`
- **Scenario:**
- **Expected behavior:**
- **Actual behavior:**
- **Evidence:**
```
