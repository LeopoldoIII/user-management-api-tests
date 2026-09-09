"""
Data Factory — Test payload constructors

- Functions returning dicts ready to be sent as JSON
- Unique emails (with uuid) where the test can succeed (201/200)
  to avoid conflicts between executions of the same Scenario Outline
- For cases that always fail (400/409)
"""

import uuid


def _unique_email(prefix: str = "test") -> str:
    """
    Generates a unique email to avoid conflicts between scenarios

    Tests should be isolated. If a test creates a user with 'test@loanpro.com'
    and another test tries to do the same, it will fail with a 409 Conflict
    """
    return f"{prefix}_{str(uuid.uuid4())[:8]}@loanpro.com"


def valid_user(name: str = "Test User", email: str = None, age: int = 30, ) -> dict:
    """valid user according to the contract (name, email, age)"""
    return {
        "name": name,
        "email": email or _unique_email("valid"),
        "age": age,
    }


def user_missing_field(field: str) -> dict:
    """User missing a required field (name | email | age)"""
    user = {
        "name": "Missing Field User",
        "email": "missing_field@loanpro.com",
        "age": 30,
    }
    user.pop(field, None)
    return user


def user_with_age(age: int) -> dict:
    """
    Unique email via uuid to avoid conflict when the test succeeds (201)
    """
    return {
        "name": "User Test Age",
        "email": _unique_email(f"test_age_{age}"),
        "age": age,
    }


def user_with_invalid_email(invalid_email: str = "not-an-email") -> dict:
    """User with invalid email format"""
    return {
        "name": "Invalid Email User",
        "email": invalid_email,
        "age": 30,
    }


def empty_body() -> dict:
    return {}
