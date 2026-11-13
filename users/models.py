from django.db import models


class User(models.Model):
    email = models.EmailField(max_length=255, unique=True)
    password_hash = models.CharField(max_length=128)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, default="")
    role = models.CharField(max_length=20, default="student")
    status = models.CharField(max_length=20, default="active")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "users"
