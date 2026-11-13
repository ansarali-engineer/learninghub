from rest_framework.status import HTTP_200_OK,HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from rest_framework import status as http_status

def success_response(message,data,status_code=HTTP_200_OK):
    return Response({
        "message":message,
        "data": data,
        "status_code":status_code
    },status=status_code)

def paginated_response(rows, total, page, page_size, base_url=""):
    """Return a paginated list response with metadata."""
    total_pages = (total + page_size - 1) // page_size
    return Response(
        {
            "success": True,
            "data": rows,
            "error": None,
            "meta": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1,
            },
        },
        status=http_status.HTTP_200_OK,
    )


def error_response(message,data,status_code=HTTP_400_BAD_REQUEST):
    return Response({
        "message":message,
        "data": data,
        "status_code":status_code
    },status=status_code)

