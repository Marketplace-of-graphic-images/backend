import re
from datetime import date

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

# from rest_framework import status


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
    # try:
    local_area, domain_area = email.split('@')
    # except ValueError:
    #     raise ValidationError(
    #             detail={'errors': _('Email can only contain one "@"')},
    #             code=status.HTTP_400_BAD_REQUEST,
    #     )
    if len(local_area) < 6 or len(local_area) > 64:
        errors.append(_('Allowed number of characters in the local'
                              ' area: more than 5 and less than 65'))
    elif len(domain_area) > 253:
        errors.append(_('Allowed number of characters in the domain'
                              ' area: less than 254'))
    elif len(email) > 256:
        errors.append(_('Maximum email length 256 characters'))
    # elif local_area[0] == '.' or local_area[len(local_area) - 1] == '.':
    #     raise ValidationError('A local area cannot begin or end with .')
    # elif local_area.count('.') > 1:
    #     if local_area[local_area.find('.') + 1] == '.':
    #         raise ValidationError(". can't repeated more than twice in a row")
    if errors:
        raise ValidationError(errors)
