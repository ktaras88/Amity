import re

from django.core.exceptions import ValidationError

"""
Password requirements:
At least 8  characters
Not longer than 128 characters
Includes at least 1 lower case character
Includes at least 1 upper case character
Includes at least 1 special character
Includes at least 1 number
"""


class MaximumLengthValidator:
    def __init__(self, max_length=128):
        self.max_length = max_length

    def validate(self, password, user=None):
        if len(password) > self.max_length:
            raise ValidationError(
                "This password must contain at most %(min_length)d characters.",
                code='password_too_long',
                params={'min_length': self.max_length},
            )


class NumberValidator:
    def __init__(self, min_digits=0):
        self.min_digits = min_digits

    def validate(self, password, user=None):
        if not len(re.findall('\d', password)) >= self.min_digits:
            raise ValidationError(
                "The password must contain at least %(min_digits)d digit(s), 0-9.",
                code='password_no_number',
                params={'min_digits': self.min_digits},
            )


class UppercaseValidator:
    def validate(self, password, user=None):
        if not re.findall('[A-Z]', password):
            raise ValidationError(
                "The password must contain at least 1 uppercase letter, A-Z.",
                code='password_no_upper',
            )


class LowercaseValidator:
    def validate(self, password, user=None):
        if not re.findall('[a-z]', password):
            raise ValidationError(
                "The password must contain at least 1 lowercase letter, a-z.",
                code='password_no_lower',
            )


class SymbolValidator:
    def validate(self, password, user=None):
        if not re.findall('[()[\]{}|\\`~!@#$%^&*_\-+=;:\'",<>./?]', password):
            raise ValidationError(
                "The password must contain at least 1 symbol: " +
                "()[]{}|\`~!@#$%^&*_-+=;:'\",<>./?",
                code='password_no_symbol',
            )
