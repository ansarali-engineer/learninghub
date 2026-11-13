
def validate_paginations_params(
    page: str | None, page_size: str | None, max_size: int = 100
) -> tuple[int, int]:
    try:
        page_number = max(1, int(page or 1))
        page_length = max(1, min(int(page_size or 20), max_size))
    except (TypeError, ValueError) as exc:
        raise ValueError("page and page_size must be valid integers") from exc
    return page_number, page_length

def validate_email(email:str) ->str:
    if not email or "@" not in email:
        raise ValueError("Email is not valid")

    return email.strip().lower()

def validate_password(password:str) ->str:
    if not password or len(password)<8:
        raise ValueError("Password must be atleast 8 charactors")

    has_letter = any(c.isalpha() for c in password)
    has_digit = any(c.isdigit() for c in password)
    if not has_letter or not has_digit:
        raise ValueError("Password must contain atleast one charactor and one digit")
    return password
    