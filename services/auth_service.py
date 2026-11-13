
from utils.validators import validate_password, validate_email
from repositries.user_repositry import create_user
from database.connection import DuplicateRecordError
from django.contrib.auth.hashers import check_password
from users.models import User


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
    if status not in ("active", "inactive", "blocked"):
        raise ValueError("Invalid Status")
    try:
        user = create_user(email, password, first_name, last_name, phone, role, status)
    except DuplicateRecordError:
        raise ValueError("An account with this email already exists")
    return user


def authenticate_user(email: str, password: str) -> User | None:
    user = User.objects.filter(email=email.strip().lower()).first()
    if user is None or not user.is_active:
        return None
    if not check_password(password, user.password_hash):
        return None
    return user



