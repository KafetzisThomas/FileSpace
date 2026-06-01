import pyotp
import qrcode
import base64
from io import BytesIO
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import update_session_auth_hash, login
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .models import CustomUser
from .forms import RegistrationForm, UsernameUpdateForm, NewPasswordChangeForm, TwoFactorToggleForm, TwoFactorVerificationForm
from .utils import send_discord_signup_alert

def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            messages.success(request, "Your account is pending approval. You'll be able to log in once approved.")
            send_discord_signup_alert(user)
            return redirect("users:login")
    else:
        form = RegistrationForm()
    return render(request, "users/register.html", {"form": form})

def two_factor_verification(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("users:login")

    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == "POST":
        form = TwoFactorVerificationForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data.get("otp")
            if user.otp_secret and pyotp.TOTP(user.otp_secret).verify(otp):
                login(request, user, backend="django.contrib.auth.backends.ModelBackend")
                request.session.pop("user_id", None)
                return redirect("files:drive")
            else:
                form.add_error("otp", "Invalid OTP.")
    else:
        form = TwoFactorVerificationForm()

    return render(request, "users/2fa_verification.html", {"form": form})

@login_required
def account(request):
    user = request.user
    username_form = UsernameUpdateForm(instance=user)
    tfa_form = TwoFactorToggleForm(instance=user)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "update_username":
            username_form = UsernameUpdateForm(request.POST, instance=user)
            if username_form.is_valid():
                username_form.save()
                messages.success(request, "Username updated successfully.")
                return redirect("users:account")

        elif action == "toggle_2fa":
            tfa_form = TwoFactorToggleForm(request.POST, instance=user)
            if tfa_form.is_valid():
                user = tfa_form.save(commit=False)
                if user.enable_2fa:
                    user.enable_2fa = False
                    user.otp_secret = pyotp.random_base32()
                    user.save()

                    otp = pyotp.TOTP(user.otp_secret)
                    uri = otp.provisioning_uri(name=user.username, issuer_name="FileSpace")

                    qr = qrcode.make(uri)
                    qr = qr.resize((150, 150))
                    buffer = BytesIO()
                    qr.save(buffer, format="PNG")
                    qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

                    user.enable_2fa = True
                    display_form = TwoFactorToggleForm(instance=user)
                    user.enable_2fa = False

                    context = {
                        "username_form": username_form,
                        "show_2fa_modal": True,
                        "qr_code": qr_base64,
                        "otp_secret": user.otp_secret,
                        "tfa_form": display_form,
                    }
                    return render(request, "users/account.html", context)
                else:
                    user.enable_2fa = False
                    user.otp_secret = ""
                    user.save()
                    messages.success(request, "2FA disabled.")
                    return redirect("users:account")

        elif action == "confirm_2fa":
            otp = request.POST.get("otp")
            otp_secret = user.otp_secret

            if otp_secret and pyotp.TOTP(otp_secret).verify(otp):
                user.enable_2fa = True
                user.save()
                messages.success(request, "2FA enabled successfully!")
            else:
                user.otp_secret = ""
                user.save()
                messages.error(request, "Invalid OTP. 2FA setup failed.")
            return redirect("users:account")

        elif action == "cancel_2fa":
            user.enable_2fa = False
            user.otp_secret = ""
            user.save()
            return redirect("users:account")

    context = {"username_form": username_form, "tfa_form": tfa_form}
    return render(request, "users/account.html", context)

@login_required
def update_password(request):
    if request.method == "POST":
        form = NewPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was successfully updated!")
            return redirect("users:account")
    else:
        form = NewPasswordChangeForm(request.user)

    return render(request, "users/update_password.html", {"form": form})

@login_required
@require_POST
def delete_account(request):
    user = request.user
    user.delete()
    return redirect("users:register")


class CustomLoginView(LoginView):
    authentication_form = AuthenticationForm
    def form_valid(self, form):
        user = form.get_user()
        if user.enable_2fa:
            self.request.session["user_id"] = user.id
            return redirect("users:2fa_verification")
        return super().form_valid(form)
