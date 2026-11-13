from rest_framework import serializers

class UsersSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(min_length=8, max_length=128, write_only=True)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True, default="")
    role = serializers.ChoiceField(
        choices=["admin", "instructor", "student"],
        default="student",
    )
    status = serializers.ChoiceField(
        choices=["active", "inactive", "blocked"],
        default="active",
    )
    bootstrap_token = serializers.CharField(
        write_only=True, required=False, trim_whitespace=False
    )
    created_at = serializers.DateTimeField(read_only=True)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(write_only=True, trim_whitespace=False)

