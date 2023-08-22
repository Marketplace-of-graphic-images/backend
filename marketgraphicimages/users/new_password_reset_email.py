from templated_mail.mail import BaseEmailMessage

from core.new_token_generator import six_digit_code_generator


class PasswordResetEmail(BaseEmailMessage):
    template_name = "email/password_reset.html"

    def get_context_data(self):

        context = super().get_context_data()
        user = context.get("user")
        context["token"] = six_digit_code_generator.make_token(user)
        print(context["token"])
        return context
