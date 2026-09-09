"""
common_steps.py — Generic steps reused across all endpoints

A single status code step covers all scenarios (200, 201, 204, 400, 401, 404, 409)
The body Then steps validate the ErrorResponse structure defined in the contract:
  { "error": "<message>" }
"""

from behave import then


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


@then("the response body should contain at least {count:d} users")
def step_body_contains_at_least_users(context, count):
    body = context.response.json()
    assert isinstance(body, list), f"Expected list, got {type(body)}"
    actual = len(body)
    assert actual >= count, f"Expected at least {count} users, got {actual}.\nBody: {body}"


@then("the response body should contain the created user details")
def step_body_has_created_user(context):
    body = context.response.json()
    _assert_user_shape(body, "POST /users")


@then("the response body should contain the user details")
def step_body_has_user_details(context):
    body = context.response.json()
    _assert_user_shape(body, "GET /users/{email}")


@then("the response body should contain the updated user details")
def step_body_has_updated_user(context):
    body = context.response.json()
    _assert_user_shape(body, "PUT /users/{email}")


@then("the response body should contain a validation error message")
def step_body_has_validation_error(context):
    _assert_error_shape(context.response.json(), "Validation error")


@then("the response body should contain a duplicate email error message")
def step_body_has_duplicate_error(context):
    _assert_error_shape(context.response.json(), "Duplicate email")


@then("the response body should contain a user not found error message")
def step_body_has_not_found_error(context):
    _assert_error_shape(context.response.json(), "User not found")


@then("the response body should contain an authentication error message")
def step_body_has_auth_error(context):
    _assert_error_shape(context.response.json(), "Authentication error")


#
#  Asserts
# ─────────────────────────────────────────────
# Error responses — schema ErrorResponse { "error": "..." }
# ─────────────────────────────────────────────

def _assert_error_shape(body, context_msg: str = ""):
    assert isinstance(body, dict), f"Expected dict, got {type(body)}: {body}"
    assert "error" in body, (
        f"Missing field 'error' in ErrorResponse. {context_msg}\nBody: {body}"
    )
    assert isinstance(body["error"], str), (
        f"'error' should be a string, got {type(body['error'])}"
    )

# ─────────────────────────────────────────────
# Error responses — schema ErrorResponse { "error": "..." }
# ─────────────────────────────────────────────
def _assert_user_shape(body: dict, context_msg: str = ""):
    """Verifies that the body has the fields of the User schema from the contract."""
    for field in ("name", "email", "age"):
        assert field in body.keys(), (
            f"Missing field '{field}' in response. {context_msg}\nBody: {body}"
        )