# Bugs Report — User Management API

## Status

| Environment | Tests executed | Confirmed bugs | Contract gaps |
|-------------|----------------|----------------|---------------|
| dev         | Yes            | 5              | 2             |
| prod        | Yes            | 5              | 2             |

---

## Confirmed Bugs (backed by the OpenAPI contract)

### [BUG-001] — Server crashes with 500 when creating a user with a duplicate email

- **Environment:** dev / prod
- **Endpoint:** `POST /users`
- **Tag:** `@BUG-001`
- **Scenario:** Fail to create a user with a duplicate email
- **Expected behavior (contract):** Status 409 Conflict with an ErrorResponse body.
- **Actual behavior:** Status 500 Internal Server Error. The server crashes and does not return a JSON body.
- **Evidence:** Docker logs show a 500 error immediately after the second POST request.

---

### [BUG-002] — Server crashes with 500 on invalid email formats

- **Environment:** dev / prod
- **Endpoint:** `POST /users`
- **Tag:** `@BUG-002`
- **Scenario:** Fail to create a user with invalid email format
- **Expected behavior (contract):** Status 400 Bad Request with a validation error message.
- **Actual behavior:** Status 500 Internal Server Error. The server fails to handle the bad string and crashes instead of returning a clean validation error.
- **Evidence:** The test fails because we expected a 400 but got a 500. Happens with both `"not-an-email"` and `"r2d2@xvhows@#$@.com"`.

---

### [BUG-003] — Documentation Typo: POST 400 Error shows "User not found"

- **Environment:** N/A (Documentation / Contract)
- **Endpoint:** `POST /users`
- **Tag:** None (documentation defect)
- **Expected behavior (contract):** The example for a 400 validation error on user creation should reflect a validation issue (e.g., `"Invalid age"` or `"Missing name"`).
- **Actual behavior:** The Swagger / OpenAPI `contract_api.yml` shows `{"error": "User not found"}` as the example for a 400 Bad Request on a POST. This makes no logical sense since we are creating a user, not fetching one.
- **Evidence:** Line 45–50 of `contract_api.yml`. Likely a copy-paste error from the GET / DELETE endpoints.

---

### [BUG-004] — GET on a non-existent user crashes with 500 instead of returning 404

- **Environment:** dev / prod
- **Endpoint:** `GET /users/{email}`
- **Tag:** `@BUG-004`
- **Scenario:** Fail to get a non-existent user
- **Expected behavior (contract):** Status 404 Not Found with an ErrorResponse body.
- **Actual behavior:** Status 500 Internal Server Error. The server crashes and returns `{"error": "Internal server error"}` instead of a 404 error object.
- **Evidence:** The test requesting `/users/nonexistent@loanpro.com` receives a 500 status code instead of the expected 404.

---

### [BUG-005] — DELETE endpoint processes requests without validating token

- **Environment:** dev / prod
- **Endpoint:** `DELETE /users/{email}`
- **Tag:** `@BUG-005`
- **Scenario:** Fail to delete a user without authentication / Fail to delete a user with invalid authentication token
- **Expected behavior (contract):** Status 401 Unauthorized with an ErrorResponse body — the `Authentication` header is marked `required: true` in the contract.
- **Actual behavior:** Status 204 No Content. The server successfully deletes the user even if the Authentication token is missing or completely invalid.
- **Evidence:** The test requesting a DELETE without an `Authentication` header receives a 204 status code, meaning the endpoint is unprotected.

---

## Contract Gaps / Security Recommendations

> These are **not bugs** against the current contract. The `CreateUserRequest` schema
> in `contract_api.yml` defines no `maxLength`, `pattern`, or sanitization rules for
> the `name` field. A 201 response for the payloads below is therefore spec-compliant.
>
> **Recommended action:** open a separate ticket to add input constraints to the
> OpenAPI contract (`minLength`, `maxLength`, `pattern`) *before* coding server-side
> enforcement. Once the contract is updated, these become testable functional
> requirements, not speculative assertions.

### [SECURITY-001] — No input validation against injection payloads (SQLi / XSS)

- **Environment:** dev / prod
- **Endpoint:** `POST /users`
- **Tag:** `@security`
- **Scenario:** Fail to create a user with malicious payloads (SQLi / XSS)
- **Observed behavior:** The server accepts names like `Robert'); DROP TABLE users;--` or `<script>alert("XSS")</script>` and returns 201 Created. This is spec-compliant today but is a significant security risk.
- **Recommendation:** Add a `pattern` constraint to `name` in the OpenAPI contract and enforce input sanitization on the server.

### [SECURITY-002] — No length limit on the `name` field

- **Environment:** dev / prod
- **Endpoint:** `POST /users`
- **Tag:** `@security`
- **Scenario:** Fail to create a user with a massive payload
- **Observed behavior:** The server processes a 500-character name without returning a 400. This is spec-compliant today but risks performance degradation or storage abuse.
- **Recommendation:** Add `maxLength: 255` (or a domain-appropriate limit) to the `name` field in the OpenAPI contract.

---

## Template for new bugs

```
### [BUG-XXX] — Title

- **Environment:**
- **Endpoint:**
- **Tag:** `@BUG-XXX`
- **Scenario:**
- **Expected behavior (contract):**
- **Actual behavior:**
- **Evidence:**
```
