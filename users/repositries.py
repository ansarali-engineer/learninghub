
from django.db import connection
from database.query_helper import fetchall


def fetch_scalar(sql:str,params:list | None = None) -> any:
    with connection.cursor() as cursor:
        cursor.execute(sql,params or [])
        row = cursor.fetchone()
        if row is None:
            return None
        return row[0]



