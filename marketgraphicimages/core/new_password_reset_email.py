from templated_mail.mail import BaseEmailMessage

from .confirmation_code import (
    create_six_digit_confirmation_code,
    user_confirmation_code_to_db,
)


class PasswordResetEmail(BaseEmailMessage):
    """Sends a confirmation code to the user.
    Save confirmation code to db(UserConfirmationCode)."""
    template_name = "email/password_reset.html"

    def get_context_data(self) -> dict:
        context = super().get_context_data()
        user = context.get("user")
        context["token"] = create_six_digit_confirmation_code()
        user_confirmation_code_to_db(context["token"], user)
        return context
