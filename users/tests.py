from django.test import TestCase, override_settings
from django.test import RequestFactory
from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, force_authenticate

from repositries.user_repositry import users_list
from services.auth_service import register_user
from users.models import User
from users.views import login, register, user_list


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

        self.assertEqual(response.status_code, 401)

    def test_login_bearer_token_authorizes_admin_user_list(self):
        register_user(
            "admin@example.com",
            "learn1234",
            "Alex",
            "Admin",
            role="admin",
        )
        factory = APIRequestFactory()
        login_request = factory.post(
            "/api/login",
            {"email": "admin@example.com", "password": "learn1234"},
            format="json",
        )

        login_response = login(login_request)
        token = login_response.data["data"]["access_token"]
        list_request = factory.get(
            "/api/users_list",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        list_response = user_list(list_request)

        self.assertEqual(login_response.status_code, 200)
        self.assertEqual(login_response.data["data"]["token_type"], "Bearer")
        self.assertEqual(list_response.status_code, 200)

    def test_login_rejects_invalid_password(self):
        register_user(
            "student@example.com", "learn1234", "Avery", "Student"
        )
        request = APIRequestFactory().post(
            "/api/login",
            {"email": "student@example.com", "password": "wrong-password"},
            format="json",
        )

        response = login(request)

        self.assertEqual(response.status_code, 401)

    def test_public_registration_cannot_assign_privileged_role(self):
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

        self.assertEqual(response.status_code, 403)
        self.assertFalse(User.objects.filter(email="admin@example.com").exists())

    def test_admin_can_assign_other_roles_and_statuses(self):
        admin = register_user(
            "operator@example.com",
            "learn1234",
            "Alex",
            "Operator",
            role="admin",
        )
        admin_user = User.objects.get(email=admin["email"])
        request = APIRequestFactory().post(
            "/api/create_user",
            {
                "email": "instructor@example.com",
                "password": "learn1234",
                "first_name": "Avery",
                "last_name": "Instructor",
                "role": "instructor",
                "status": "inactive",
            },
            format="json",
        )
        force_authenticate(request, user=admin_user)

        response = register(request)

        self.assertEqual(response.status_code, 200)
        created_user = User.objects.get(email="instructor@example.com")
        self.assertEqual(created_user.role, "instructor")
        self.assertEqual(created_user.status, "inactive")

    @override_settings(ADMIN_BOOTSTRAP_TOKEN="test-bootstrap-token")
    def test_bootstrap_token_can_create_only_the_first_admin(self):
        request = APIRequestFactory().post(
            "/api/create_user",
            {
                "email": "first-admin@example.com",
                "password": "learn1234",
                "first_name": "First",
                "last_name": "Admin",
                "role": "admin",
                "bootstrap_token": "test-bootstrap-token",
            },
            format="json",
        )

        response = register(request)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(role="admin").exists())

        second_request = APIRequestFactory().post(
            "/api/create_user",
            {
                "email": "second-admin@example.com",
                "password": "learn1234",
                "first_name": "Second",
                "last_name": "Admin",
                "role": "admin",
                "bootstrap_token": "test-bootstrap-token",
            },
            format="json",
        )

        second_response = register(second_request)

        self.assertEqual(second_response.status_code, 403)
        self.assertFalse(User.objects.filter(email="second-admin@example.com").exists())
