from random import randint
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class SixDigitCodeGenerator(PasswordResetTokenGenerator):
    def make_token(self, user):
        number = randint(1000000, 9999999) % 1000000
        token = "{:06d}".format(number)
        user.code_owner.all().delete()
        user.code_owner.create(confirmation_code=token)
        return token


six_digit_code_generator = SixDigitCodeGenerator()
