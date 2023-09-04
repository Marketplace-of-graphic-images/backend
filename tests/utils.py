import re


def take_confirmation_code(message):
    code_match = re.search(r'(\d{6})', message)

    if code_match:
        confirmation_code = code_match.group()
        return confirmation_code
