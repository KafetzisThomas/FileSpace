from django.conf import settings
from django.core.mail import mail_admins
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_new_user_registration(user):
    html_message = render_to_string(
        "emails/new_user_registration.html",
        {
            "user_id": user.id,
            "user_username": user.username,
            "date_joined": user.date_joined.strftime("%d/%m/%Y %H:%M:%S"),
        },
    )
    plain_message = strip_tags(html_message)
    mail_admins("New User Registration", message=plain_message, html_message=html_message)
