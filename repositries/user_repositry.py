from django.contrib.auth.hashers import make_password
from database.connection import get_cursor
from database.query_helper import fetch_one, fetchall, fetch_scalar

def _user_select() -> str:
    return ("SELECT id,email,first_name,last_name,phone,role,status,created_at FROM users")
USER_COLUMNS = "id, email, first_name, last_name, phone, role, status, created_at"

def users_list(page:int,page_size:int,role:str,status:str,search:str):
    filters ,params = [] , []

    if role:
        filters.append("role=%s")
        params.append(role)
    if status:
        filters.append("status=%s")
        params.append(status)

    if search:
        filters.append("(email LIKE %s OR first_name LIKE %s OR last_name LIKE %s)")
        search_patterns = (f"%{search}%")
        params.extend([search_patterns,search_patterns,search_patterns])
    where_clause = f" WHERE {' AND '.join(filters)}" if filters else ""
    total = fetch_scalar(
        f"SELECT COUNT(*) FROM users u{where_clause}", params
    )
    offset = (page - 1) * page_size
    users = fetchall(
        f"""SELECT {USER_COLUMNS}
            FROM users {where_clause}
            ORDER BY id ASC LIMIT %s OFFSET %s""",
        [*params, page_size, offset],
    )
    return users, total


def create_user(
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    phone: str = "",
    role: str = "student",
    status: str = "active",
):
    query = """INSERT INTO users
        (email, password_hash, first_name, last_name, phone, role, status, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)"""

    hashed = make_password(password)
    with get_cursor() as cursor:
        cursor.execute(
            query,
            [email.lower().strip(), hashed, first_name, last_name, phone, role, status],
        )
        user_id = cursor.lastrowid
    user = get_user_by_id(user_id)
    if user:
        user.pop("password_hash",None)
    return user


def get_user_by_id(user_id):
    sql = _user_select() + " WHERE id = %s"
    return fetch_one(sql, [user_id])


