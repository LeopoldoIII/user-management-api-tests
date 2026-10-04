import re

EMAIL_REGEX = re.compile(r'^[^@]+@[^@]+\.[^@]+$')


def validate_user(data: dict, check_email_format: bool = True) -> str | None:
    """
    Validates user payload for POST and PUT operations.

    Args:
        data:               Request body as dict.
        check_email_format: If True, validates email against EMAIL_REGEX.

    Returns:
        Error message string if validation fails, None if valid.
    """
    if not data.get("name"):
        return "name is required"

    if not data.get("email"):
        return "email is required"

    if check_email_format and not EMAIL_REGEX.match(str(data["email"])):
        return "Invalid email format"

    age = data.get("age")
    if age is None:
        return "age is required"

    if not isinstance(age, int) or isinstance(age, bool):
        return "age must be an integer"

    if not (1 <= age <= 150):
        return "Age must be between 1 and 150"

    return None


def validate_note(data: dict) -> str | None:
    """
    Validates note payload for POST /users/<email>/notes.

    Returns:
        Error message string if validation fails, None if valid.
    """
    if not data.get("note"):
        return "Note is required"
    return None
