from datetime import date

from django.core.exceptions import ValidationError


def date_is_past(value):
    if isinstance(value, date):
        if value >= date.today() or value.year < 1900():
            raise ValidationError(
                ("Дата введена не верно.")
            )
    else:
        raise ValidationError(
            ("Дата введена не верно.")
        )