from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from zxcvbn import zxcvbn
from .models import CustomUser


class RegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ["username"]

    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        if password:
            result = zxcvbn(password)
            if result["score"] < 3:  # 0 – 4 (=5 levels)
                raise forms.ValidationError("Password is too weak. Try adding more characters, numbers or symbols.")

        return password


class UsernameUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ("username",)


class NewPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label="Old Password",
        widget=forms.PasswordInput(attrs={"autofocus": "autofocus", "class": "form-control"})
    )
    new_password1 = forms.CharField(label="New Password", widget=forms.PasswordInput)
    new_password2 = forms.CharField(label="Confirm New Password", widget=forms.PasswordInput)

    def clean_new_password1(self):
        password = self.cleaned_data.get("new_password1")
        if password:
            result = zxcvbn(password)
            if result["score"] < 3:  # 0 – 4 (=5 levels)
                raise forms.ValidationError("Password is too weak. Try adding more characters, numbers or symbols.")

        return password


class TwoFactorToggleForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ("enable_2fa",)
        widgets = {
            'enable_2fa': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'role': 'switch',
                'onchange': 'this.form.submit();'
            })
        }


class TwoFactorVerificationForm(forms.Form):
    otp = forms.CharField(label="Generated OTP",
        widget=forms.TextInput(attrs={"autofocus": "autofocus", "class": "form-control"})
    )
