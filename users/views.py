import secrets

from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from config.helper import error_response, paginated_response, success_response
from .authentication import ACCESS_TOKEN_TTL_SECONDS, create_access_token
from .models import User
from .serializer import LoginSerializer, UsersSerializer
from utils.validators import validate_paginations_params
from repositries.user_repositry import users_list
from database.query_helper import serialize_rows
from services.auth_service import authenticate_user, register_user


@api_view(["GET"])
@permission_classes([IsAdminUser])
def user_list(request):
    try:
        page, page_size = validate_paginations_params(
            request.GET.get("page"), request.GET.get("page_size")
        )
    except ValueError as exc:
        return error_response(str(exc), "VALIDATION_ERROR")
    role = request.GET.get('role')
    status = request.GET.get('status')
    search = request.GET.get("search","").strip()

    if role and role not in ("admin","instructor","student"):
        return error_response("Role should be admin, instructor or student","VALIDATION_ERROR")
    if status and status not in ("active","inactive","blocked"):
        return error_response("Status should be active, inactive or blocked","VALIDATION_ERROR")
    if search and len(search)>100:
        return error_response("Search text should be 100 characters or fewer","VALIDATION_ERROR")
    users,total = users_list(page,page_size,role,status,search)

    return paginated_response(serialize_rows(users), total, page, page_size)

@api_view(["POST"])
def register(request):
    serializer = UsersSerializer(data=request.data)
    if not serializer.is_valid():
        return error_response("Data is not valid", serializer.errors)
    data = serializer.validated_data
    is_admin = request.user.is_authenticated and request.user.is_staff
    if not is_admin:
        if data["role"] == "admin":
            expected_token = settings.ADMIN_BOOTSTRAP_TOKEN
            supplied_token = data.get("bootstrap_token", "")
            can_bootstrap = (
                expected_token
                and supplied_token
                and not User.objects.filter(role="admin").exists()
                and data["status"] == "active"
                and secrets.compare_digest(supplied_token, expected_token)
            )
            if not can_bootstrap:
                return error_response(
                    "Initial admin registration requires the configured "
                    "bootstrap token and an active status.",
                    "ADMIN_BOOTSTRAP_REQUIRED",
                    status_code=403,
                )
        elif data["role"] != "student" or data["status"] != "active":
            return error_response(
                "Only admins can assign non-default roles or statuses",
                "FORBIDDEN",
                status_code=403,
            )
    try:
       user = register_user(
           data["email"],
           data["password"],
           data["first_name"],
           data["last_name"],
           data.get("phone", ""),
           data["role"],
           data["status"],
       )
    except ValueError as e:
        return error_response(str(e),"Error")


    return success_response("User created Successfully",user)


@api_view(["POST"])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return error_response("Data is not valid", serializer.errors)

    user = authenticate_user(
        serializer.validated_data["email"],
        serializer.validated_data["password"],
    )
    if user is None:
        return error_response(
            "Invalid email or password",
            "INVALID_CREDENTIALS",
            status_code=401,
        )

    return success_response(
        "Login successful",
        {
            "access_token": create_access_token(user.pk),
            "token_type": "Bearer",
            "expires_in": ACCESS_TOKEN_TTL_SECONDS,
            "user": {
                "id": user.pk,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role,
            },
        },
    )

