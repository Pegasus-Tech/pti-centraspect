from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from centraspect import settings


def send_user_added_email(to_user, account):
    msg = EmailMessage(
        from_email=settings.CENTRASPECT_FROM_EMAIL,
        to=[to_user.email],
    )
    uid = urlsafe_base64_encode(force_bytes(to_user.pk))
    token = default_token_generator.make_token(to_user)
    url = f'{settings.APP_HOST_URL}/reset/{uid}/{token}'
    msg.template_id = "d-130b3ad30f814886abf6876154b3501b"
    msg.dynamic_template_data = {
        "account_name": account.name,
        "verify_email_link": url
    }
    msg.send(fail_silently=False)


def send_user_forgot_password_email(to_user):
    msg = EmailMessage(
        from_email=settings.CENTRASPECT_FROM_EMAIL,
        to=[to_user.email],
    )
    uid = urlsafe_base64_encode(force_bytes(to_user.pk))
    token = default_token_generator.make_token(to_user)
    url = f'{settings.APP_HOST_URL}/reset/{uid}/{token}'
    msg.template_id = "d-23117c33dffd411db66c6ea626a5bd43"
    msg.dynamic_template_data = {
        "reset_password_link": url
    }
    msg.send(fail_silently=False)
