import random
from smtplib import SMTP_SSL

from string import digits
from email.message import EmailMessage
from django.template.loader import render_to_string

from .models import User
from amity_api.settings import EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_PORT, EMAIL_HOST


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

    html = render_to_string(template, context=context)

    with SMTP_SSL(EMAIL_HOST, EMAIL_PORT) as smtp:
        smtp.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        try:
            msg = EmailMessage()
            msg.add_alternative(html, subtype='html')
            msg['Subject'] = 'Amity security code'
            msg['From'] = EMAIL_HOST_USER
            msg['To'] = email
            smtp.send_message(msg)
        except:
            print("Something went wrong!")
    print("Done!")
