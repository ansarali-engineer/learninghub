from rest_framework import serializers

class UsersSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(min_length=8, max_length=128, write_only=True)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True, default="")
    role = serializers.ChoiceField(
        choices=['student'],
        default='student'
    )
    status = serializers.ChoiceField(
        choices=['active'],
        default='active'
    )
    created_at = serializers.DateTimeField(read_only=True)


