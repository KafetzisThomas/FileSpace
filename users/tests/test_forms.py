from django.test import TestCase
from django.contrib.auth import get_user_model
from ..forms import RegistrationForm

User = get_user_model()


class RegistrationFormTests(TestCase):

    def setUp(self):
        self.password_strength_weak = {
            "username": "user",
            "password1": "password123",
            "password2": "password123"
        }
        self.password_strength_strong = {
            "username": "user",
            "password1": "Str0ng_p@ssword",
            "password2": "Str0ng_p@ssword"
        }

    def test_password_strength_validation_weak(self):
        form = RegistrationForm(data=self.password_strength_weak)
        self.assertFalse(form.is_valid())

    def test_password_strength_validation_strong(self):
        form = RegistrationForm(data=self.password_strength_strong)
        self.assertTrue(form.is_valid(), form.errors)
