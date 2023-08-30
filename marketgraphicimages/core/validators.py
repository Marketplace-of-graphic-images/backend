from datetime import date

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import status


def date_is_past(value: date) -> None:
    message = _('Date is not correct.')
    if isinstance(value, date):
        if value >= date.today() or value.year < 1900:
            raise ValidationError(message)
    else:
        raise ValidationError(message)

def validate_email(email: str) -> None:
    try:
        local_area, domain_area = email.split('@')
    except ValueError:
        raise ValidationError(
                detail={'errors': _('Email can only contain one "@"')},
                code=status.HTTP_400_BAD_REQUEST,
        )
    if len(local_area) < 6 or len(local_area) > 64:
        raise ValidationError('Allowed number of characters in the local'
                              ' area: more than 5 and less than 65')
    elif len(domain_area) > 255:
        raise ValidationError('Allowed number of characters in the domain'
                              ' area: less than 256')
