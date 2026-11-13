from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAdminUser
from config.helper import success_response,error_response,paginated_response
from .serializer import UsersSerializer
from utils.validators import validate_paginations_params
from repositries.user_repositry import users_list
from services.auth_service import register_user
from database.query_helper import serialize_rows


@api_view(["GET"])
# @permission_classes([IsAdminUser])
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

    


