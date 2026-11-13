from django.test import TestCase
from django.test import RequestFactory
from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model
from rest_framework.test import force_authenticate

from repositries.user_repositry import users_list
from services.auth_service import register_user
from users.models import User
from users.views import user_list


class UserWorkflowTests(TestCase):
    def test_registration_persists_hashed_password_and_optional_phone(self):
        response_user = register_user(
            "student@example.com", "learn1234", "Avery", "Student"
        )

        self.assertEqual(response_user["email"], "student@example.com")
        self.assertNotIn("password_hash", response_user)
        stored_user = User.objects.get(email="student@example.com")
        self.assertTrue(check_password("learn1234", stored_user.password_hash))
        self.assertEqual(stored_user.phone, "")

    def test_registration_accepts_admin_role(self):
        response_user = register_user(
            "admin@example.com", "learn1234", "Alex", "Admin", role="admin"
        )

        self.assertEqual(response_user["role"], "admin")

    def test_duplicate_email_returns_a_friendly_error(self):
        register_user("student@example.com", "learn1234", "Avery", "Student")

        with self.assertRaisesRegex(ValueError, "already exists"):
            register_user("student@example.com", "learn5678", "Alex", "Learner")

    def test_user_search_respects_role_and_status_filters(self):
        register_user(
            "ada@example.com", "learn1234", "Ada", "Lovelace", role="instructor"
        )
        register_user(
            "ada.student@example.com", "learn1234", "Ada", "Student"
        )

        users, total = users_list(1, 10, "instructor", "active", "Ada")

        self.assertEqual(total, 1)
        self.assertEqual([user["email"] for user in users], ["ada@example.com"])

    def test_invalid_page_parameter_returns_bad_request(self):
        request = RequestFactory().get("/api/users_list?page=not-a-number")
        staff_user = get_user_model().objects.create_user(
            username="staff", password="temporary-password", is_staff=True
        )
        force_authenticate(request, user=staff_user)

        response = user_list(request)

        self.assertEqual(response.status_code, 400)

    def test_user_list_requires_staff_authentication(self):
        request = RequestFactory().get("/api/users_list")

        response = user_list(request)

        self.assertEqual(response.status_code, 403)

    def test_public_registration_cannot_assign_privileged_role(self):
        from rest_framework.test import APIRequestFactory
        from users.views import register

        request = APIRequestFactory().post(
            "/api/create_user",
            {
                "email": "admin@example.com",
                "password": "learn1234",
                "first_name": "Alex",
                "last_name": "Admin",
                "role": "admin",
            },
            format="json",
        )

        response = register(request)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.filter(email="admin@example.com").exists())
