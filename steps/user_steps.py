"""
user_steps.py — Specific steps for User CRUD operations.

Covers all Given/When from the feature file for:
  POST   /users
  GET    /users
  GET    /users/{email}
  PUT    /users/{email}
  DELETE /users/{email}

Principles:
- context.created_emails accumulates emails for automatic teardown
- Emails from the Outline that can succeed use data_factory (uuid)
- Fixed emails from the feature (e.g., "delete@example.com") are registered in Given
"""

from behave import given, when
from utils.data_factory import (
    valid_user,
    user_missing_field,
    user_with_age,
    user_with_invalid_email,
    empty_body,
)


# ══════════════════════════════════════════════
# GIVEN — preconditions
# ══════════════════════════════════════════════

@given('a user with email "{email}" exists')
@given('a user with email "{email}" already exists')
def step_given_user_exists(context, email):
    """
    Creates the user if they do not exist registers the email

    It ensures the preconditions of our test are met,
    whether the user already existed or not. We explicitly save the email to `context.created_emails`
    so that the `after_scenario` hook automatically cleans up the database after the test
    """
    payload = valid_user(name="Precondition User", email=email, age=30)
    resp = context.api_client.post("/users", json=payload)
    context.user_data = resp.json()
    # 201 = created now | 409 = already existed
    if resp.status_code in (201, 409):
        if email not in context.created_emails:
            context.created_emails.append(email)


@given("no users exist in the system")
def step_given_no_users(context):
    """Deletes all existing users to ensure an empty list"""
    resp = context.api_client.get("/users")
    if resp.status_code == 200:
        for user in resp.json():
            email = user.get("email")
            if email:
                context.api_client.delete(f"/users/{email}", token=context.auth_token)


@given("{count:d} users are created in the system")
def step_create_multiple_users(context, count):
    """Creates multiple users"""
    for index in range(count):
        payload = valid_user(name=f"Test User {index}")
        resp = context.api_client.post("/users", json=payload)
        if resp.status_code == 201:
            context.created_emails.append(payload["email"])
        else:
            raise Exception(f"Failed to create user {index}: {resp.text}")


# ══════════════════════════════════════════════
# WHEN — POST /users
# ══════════════════════════════════════════════

@when('I send a POST request to "/users" with name "{name}", email "{email}", and age {age}')
def step_post_user_full(context, name, email, age):
    """Successful creation with full data"""
    payload = valid_user(name=name, email=email, age=int(age))
    context.response = context.api_client.post("/users", json=payload)
    if context.response.status_code == 201:
        context.created_emails.append(email)


@when('I send a POST request to "/users" with age {age}')
def step_post_with_age(context, age):
    """POST test Unique email via uuid to avoid conflicts on 201"""
    payload = user_with_age(age=int(age))
    context.response = context.api_client.post("/users", json=payload)
    if context.response.status_code == 201:
        context.created_emails.append(payload["email"])


@when('I send a POST request to "/users" with the email "{email}"')
def step_post_duplicate_email(context, email):
    """Attempts to create a user with an email that already exists -> expects 409"""
    payload = valid_user(email=email)
    context.response = context.api_client.post("/users", json=payload)


@when('I send a POST request to "/users" missing the "{field}" field')
def step_post_missing_field(context, field):
    """POST without a required field (name | email | age) -> expects 400"""
    payload = user_missing_field(field=field)
    context.response = context.api_client.post("/users", json=payload)


@when('I send a POST request to "/users" with an invalid email format "{invalid_email}"')
def step_post_invalid_email_format(context, invalid_email):
    """POST with invalid email format -> expects 400"""
    payload = user_with_invalid_email(invalid_email=invalid_email)
    context.response = context.api_client.post("/users", json=payload)


@when('I send a POST request to "/users" with an empty body')
def step_post_empty_body(context):
    payload = empty_body()
    context.response = context.api_client.post("/users", json=payload)


@when('I send a POST request to "/users" with a name of {length:d} characters')
def step_post_massive_name(context, length):
    massive_name = "A" * length
    payload = valid_user(name=massive_name)
    context.response = context.api_client.post("/users", json=payload)
    if context.response.status_code == 201:
        context.created_emails.append(payload["email"])


# ══════════════════════════════════════════════
# WHEN — GET /users  and  GET /users/{email}
# ══════════════════════════════════════════════

@when('I send a GET request to "/users"')
def step_get_all_users(context):
    context.response = context.api_client.get("/users")


@when('I send a GET request to "/users/{email}"')
def step_get_user_by_email(context, email):
    context.response = context.api_client.get(f"/users/{email}")


# ══════════════════════════════════════════════
# WHEN — PUT /users/{email}
# ══════════════════════════════════════════════

@when('I send a PUT request to "/users/{email}" with valid updated data')
def step_put_valid_data(context, email):
    """Valid update — changes name and age but keeps email."""
    payload = valid_user(name="Updated Name", email=email, age=35)
    context.response = context.api_client.put(f"/users/{email}", json=payload)


@when('I send a PUT request to "/users/{email}" with valid data')
def step_put_valid_nonexistent(context, email):
    """PUT on user that does not exist -> expects 404."""
    payload = valid_user(name="Ghost User", email=email, age=25)
    context.response = context.api_client.put(f"/users/{email}", json=payload)


@when('I send a PUT request to "/users/{email}" with an invalid age')
def step_put_invalid_age(context, email):
    """PUT with age=999 (out of range) -> expects 400."""
    payload = valid_user(name="Invalid Age User", email=email, age=999)
    context.response = context.api_client.put(f"/users/{email}", json=payload)


@when('I send a PUT request to "/users/{from_email}" changing the email to "{to_email}"')
def step_put_change_email(context, from_email, to_email):
    """PUT attempting to change the email to one that already belongs to another user -> expects 409."""
    payload = valid_user(name="Change Email User", email=to_email, age=30)
    context.response = context.api_client.put(f"/users/{from_email}", json=payload)


@when('I send a PUT request to "/users/{email}" missing the "{field}" field')
def step_put_missing_field(context, email, field):
    """PUT without required field -> expects 400."""
    payload = user_missing_field(field=field)
    context.response = context.api_client.put(f"/users/{email}", json=payload)


@when('I send a PUT request to "/users/{email}" with an invalid email format "{invalid_email}"')
def step_put_invalid_email_format(context, email, invalid_email):
    """PUT with invalid email format in body -> expects 400."""
    payload = user_with_invalid_email(invalid_email=invalid_email)
    context.response = context.api_client.put(f"/users/{email}", json=payload)


@when('I send a PUT request to "/users/{email}" with age {age}')
def step_put_with_age(context, email, age):
    """PUT boundary test — keeps email from path, changes age."""
    payload = valid_user(name="Boundary User", email=email, age=int(age))
    context.response = context.api_client.put(f"/users/{email}", json=payload)


@when('I send a PUT request to "/users/{email}" with an empty body')
def step_put_empty_body(context, email):
    """PUT without body -> expects 400."""
    context.response = context.api_client.put(f"/users/{email}", json=empty_body())


# ══════════════════════════════════════════════
# WHEN — DELETE /users/{email}
# ══════════════════════════════════════════════

@when('I send a DELETE request to "/users/{email}" with a valid Authentication token')
def step_delete_valid_token(context, email):
    """DELETE with correct token -> expects 204."""
    context.response = context.api_client.delete(f"/users/{email}", token=context.auth_token)


@when('I send a DELETE request to "/users/{email}" without an Authentication token')
def step_delete_no_token(context, email):
    """DELETE without Authentication header -> expects 401."""
    context.response = context.api_client.delete(f"/users/{email}", token=None)


@when('I send a DELETE request to "/users/{email}" with an invalid Authentication token')
def step_delete_invalid_token(context, email):
    """DELETE with incorrect token -> expects 401."""
    context.response = context.api_client.delete(f"/users/{email}", token="wrongtoken123")
