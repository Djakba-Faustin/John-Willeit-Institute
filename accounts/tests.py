from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import User

UserModel = get_user_model()


class RegistrationRoleTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("accounts:register")
        self.valid = {
            "username": "newuser",
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "password1": "complex-pass-123!",
            "password2": "complex-pass-123!",
        }

    def test_register_student_saves_role_student(self):
        data = {**self.valid, "role": User.Role.STUDENT}
        r = self.client.post(self.url, data, follow=True)
        self.assertEqual(r.status_code, 200)
        u = UserModel.objects.get(username="newuser")
        self.assertEqual(u.role, User.Role.STUDENT)

    def test_register_lecturer_saves_role_lecturer(self):
        data = {**self.valid, "username": "newlec", "role": User.Role.LECTURER}
        r = self.client.post(self.url, data, follow=True)
        self.assertEqual(r.status_code, 200)
        u = UserModel.objects.get(username="newlec")
        self.assertEqual(u.role, User.Role.LECTURER)
