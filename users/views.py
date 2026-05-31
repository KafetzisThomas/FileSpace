from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistrationForm, UsernameUpdateForm, NewPasswordChangeForm
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


@login_required
def account(request):
    user = request.user
    username_form = UsernameUpdateForm(instance=user)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "update_username":
            username_form = UsernameUpdateForm(request.POST, instance=user)
            if username_form.is_valid():
                username_form.save()
                messages.success(request, "Username updated successfully.")
                return redirect("users:account")

    return render(request, "users/account.html", {"username_form": username_form})

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
def delete_account(request):
    user = request.user
    user.delete()
    return redirect("users:register")
