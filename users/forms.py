from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from zxcvbn import zxcvbn

class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username"]

    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        if password:
            result = zxcvbn(password)
            if result["score"] < 3:  # 0 – 4 (=5 levels)
                raise forms.ValidationError("Password is too weak. Try adding more characters, numbers or symbols.")

        return password

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']
