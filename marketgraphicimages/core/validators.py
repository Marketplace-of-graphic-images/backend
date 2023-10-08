import re
from datetime import date

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def date_is_past(value: date) -> None:
    message = _('Date is not correct.')
    if isinstance(value, date):
        if value >= date.today() or value.year < 1900:
            raise ValidationError(message)
    else:
        raise ValidationError(message)


def validate_email(email: str) -> None:
    errors = []
    regex = re.compile(
        r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
    if not re.fullmatch(regex, email):
        errors.append(_('Invalid email'))
    domain_area = email.split('@')[-1]

    if len(domain_area) > 253:
        errors.append(_('Allowed number of characters in the domain'
                        ' area: less than 254'))
    elif len(email) > 256:
        errors.append(_('Maximum email length 256 characters'))

    if errors:
        raise ValidationError(errors)
