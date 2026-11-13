
from utils.validators import validate_password, validate_email
from repositries.user_repositry import create_user
from database.connection import DuplicateRecordError


def register_user(
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    phone: str = "",
    role: str = "student",
    status: str = "active",
):
    email = validate_email(email)
    password = validate_password(password)

    if role not in ("admin", "instructor", "student"):
        raise ValueError("Invalid Role")
    try:
        user = create_user(email, password, first_name, last_name, phone, role, status)
    except DuplicateRecordError:
        raise ValueError("An account with this email already exists")
    return user





