"""
common_steps.py — Generic steps reused across all endpoints

A single status code step covers all scenarios (200, 201, 204, 400, 401, 404, 409).

Assertion strategy (two layers):
  1. Schema layer   — _assert_user_shape / _assert_error_shape verify structure
  2. Content layer  — _assert_values_match compares sent payload vs. response values
                    — _assert_error_shape validates error message content, not just key presence
  3. Contract layer — ContractValidator wires contract_api.yml as an active oracle
                    — called on every successful (2xx) user response
  4. Persistence    — step_body_has_updated_user does a follow-up GET after PUT to
                    — confirm the server committed the change to the database
"""

from behave import then
from utils.contract_validator import ContractValidator

_contract = ContractValidator()


# ─────────────────────────────────────────────
# Status code — reused by ALL Then steps
# ─────────────────────────────────────────────

@then("the response status code should be {code:d}")
def step_check_status_code(context, code):
    actual = context.response.status_code
    assert actual == code, (
        f"Expected HTTP {code}, got {actual}.\n"
        f"Body: {context.response.text}"
    )


# ─────────────────────────────────────────────
# GET /users — array responses
# ─────────────────────────────────────────────

@then("the response body should be a JSON array")
def step_body_is_json_array(context):
    body = context.response.json()
    assert isinstance(body, list), f"Expected a JSON array, got {type(body)}.\nBody: {body}"
    for item in body:
        assert isinstance(item, dict), f"Expected JSON object inside array, got {type(item)}: {item}"
    _contract.assert_response("/users", "get", 200, body)


@then("the response body should contain at least {count:d} users")
def step_body_contains_at_least_users(context, count):
    body = context.response.json()
    assert isinstance(body, list), f"Expected list, got {type(body)}"
    actual = len(body)
    assert actual >= count, f"Expected at least {count} users, got {actual}.\nBody: {body}"


# ─────────────────────────────────────────────
# 2xx user shape assertions
# ─────────────────────────────────────────────

@then("the response body should contain the created user details")
def step_body_has_created_user(context):
    """Validates schema, compares values against sent payload, and checks the contract."""
    body = context.response.json()
    _assert_user_shape(body, "POST /users")
    _assert_values_match(body, context.request_payload, "POST /users")
    _contract.assert_response("/users", "post", 201, body)


@then("the response body should contain the user details")
def step_body_has_user_details(context):
    """Validates schema, compares values against the user created in the Given step."""
    body = context.response.json()
    _assert_user_shape(body, "GET /users/{email}")
    # context.user_data is populated by step_given_user_exists with the POST response
    if context.user_data:
        _assert_values_match(body, context.user_data, "GET /users/{email}")
    _contract.assert_response("/users/{email}", "get", 200, body)


@then("the response body should contain the updated user details")
def step_body_has_updated_user(context):
    """
    Three-layer assertion for PUT:
      1. Schema check  — all required fields are present
      2. Value check   — response values match what was sent in the PUT body
      3. Persistence   — a follow-up GET confirms the server actually committed the change
    """
    body = context.response.json()
    _assert_user_shape(body, "PUT /users/{email}")
    _assert_values_match(body, context.request_payload, "PUT /users/{email}")
    _contract.assert_response("/users/{email}", "put", 200, body)

    # ── Persistence check ────────────────────────────────────────────────────────
    # A server can return 200 with the correct body but fail to commit the update
    # (e.g. missing db.commit()). Re-fetching the resource catches that bug.
    if context.last_path:
        confirm = context.api_client.get(context.last_path)
        assert confirm.status_code == 200, (
            f"Persistence check: GET {context.last_path} returned "
            f"HTTP {confirm.status_code} after a successful PUT.\n"
            f"Body: {confirm.text}"
        )
        confirm_body = confirm.json()
        _assert_user_shape(confirm_body, f"GET {context.last_path} [persistence check]")
        _assert_values_match(
            confirm_body,
            context.request_payload,
            f"GET {context.last_path} [persistence check]",
        )


# ─────────────────────────────────────────────
# Error assertions — schema + content validation
# ─────────────────────────────────────────────

@then("the response body should contain a validation error message")
def step_body_has_validation_error(context):
    """
    Expects an ErrorResponse where the 'error' message communicates a
    validation failure (field missing, type mismatch, value out of range, etc.).
    """
    _assert_error_shape(
        context.response.json(),
        expected_keywords=["invalid", "required", "missing", "validation", "must be", "bad request"],
        context_msg="Validation error (400)",
    )


@then("the response body should contain a duplicate email error message")
def step_body_has_duplicate_error(context):
    """
    Expects an ErrorResponse where the 'error' message communicates that the
    provided email is already in use.
    """
    _assert_error_shape(
        context.response.json(),
        expected_keywords=["duplicate", "already exists", "conflict", "email"],
        context_msg="Duplicate email (409)",
    )


@then("the response body should contain a user not found error message")
def step_body_has_not_found_error(context):
    """
    Expects an ErrorResponse where the 'error' message communicates that no
    user was found for the provided identifier.
    """
    _assert_error_shape(
        context.response.json(),
        expected_keywords=["not found", "does not exist", "no user"],
        context_msg="User not found (404)",
    )


@then("the response body should contain an authentication error message")
def step_body_has_auth_error(context):
    """
    Expects an ErrorResponse where the 'error' message communicates an
    authentication failure (missing or invalid token).
    """
    _assert_error_shape(
        context.response.json(),
        expected_keywords=["unauthorized", "authentication", "token", "auth", "invalid"],
        context_msg="Authentication error (401)",
    )


# ─────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────

def _assert_error_shape(body: object, expected_keywords: list, context_msg: str = "") -> None:
    """
    Two-layer validation for an ErrorResponse body:
      Layer 1 (schema)  — body is a dict with an 'error' key of type str
      Layer 2 (content) — error message contains at least one of expected_keywords

    This ensures that a wrong-but-present error (e.g. always returning
    {"error": "Internal server error"}) will fail the assertion.
    """
    assert isinstance(body, dict), (
        f"Expected dict for ErrorResponse, got {type(body)}: {body}"
    )
    assert "error" in body, (
        f"Missing field 'error' in ErrorResponse. {context_msg}\nBody: {body}"
    )
    assert isinstance(body["error"], str), (
        f"'error' should be a string, got {type(body['error'])}: {body['error']}"
    )

    # Content validation — catches "correct shape, wrong message" bugs
    error_text = body["error"].lower()
    matched = any(keyword.lower() in error_text for keyword in expected_keywords)
    assert matched, (
        f"Error message content does not match expected context.\n"
        f"  Scenario:        {context_msg}\n"
        f"  Expected one of: {expected_keywords}\n"
        f"  Got:             '{body['error']}'"
    )


def _assert_user_shape(body: object, context_msg: str = "") -> None:
    """Verifies that the body is a dict with all User schema fields from the contract."""
    assert isinstance(body, dict), (
        f"Expected a User object (dict), got {type(body)}: {body}"
    )
    for field in ("name", "email", "age"):
        assert field in body, (
            f"Missing field '{field}' in User response. {context_msg}\nBody: {body}"
        )


def _assert_values_match(
    response_body: dict,
    sent_payload: dict,
    context_msg: str = "",
) -> None:
    """
    Compares values in the response against what was actually sent in the request.

    Only checks keys that exist in sent_payload — additional server-generated
    fields in the response are ignored. A mismatch on any key fails the assertion.
    """
    if not sent_payload:
        return
    mismatches = []
    for key, sent_value in sent_payload.items():
        got_value = response_body.get(key)
        if got_value != sent_value:
            mismatches.append(f"  '{key}': sent={sent_value!r}, got={got_value!r}")
    assert not mismatches, (
        f"Response values do not match the sent payload. {context_msg}\n"
        + "\n".join(mismatches)
    )