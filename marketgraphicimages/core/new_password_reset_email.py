from templated_mail.mail import BaseEmailMessage

from .utils import six_digit_code_generator, user_confirmation_code_to_db


class PasswordResetEmail(BaseEmailMessage):
    """Sends a confirmation code to the user."""
    template_name = "email/password_reset.html"

    def get_context_data(self):
        context = super().get_context_data()
        user = context.get("user")
        context["token"] = six_digit_code_generator.make_token()
        user_confirmation_code_to_db(context["token"], user)
        print(context["token"])
        return context
