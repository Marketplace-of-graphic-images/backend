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
