import random
from string import digits

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from amity_api.settings import EMAIL_HOST_USER
from .models import User


def generate_security_code(length=6):
    return ''.join(random.choice(digits) for _ in range(length))


def send_security_code(email, template):
    security_code = generate_security_code()

    # save security_code to db
    user = User.objects.get(email=email)
    user.security_code = security_code
    user.save()

    context = {
        'first_name': user.first_name,
        'second_name': user.second_name,
        'security_code': security_code
    }

    subject = 'Amity security code'
    html_message = render_to_string(template, context=context)
    plain_message = strip_tags(html_message)
    from_email = EMAIL_HOST_USER
    to = email

    send_mail(subject, plain_message, from_email, [to], html_message=html_message)
