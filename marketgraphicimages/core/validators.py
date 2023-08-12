from datetime import date

from django.core.exceptions import ValidationError


def date_is_past(value: date) -> None:
    """
    Validates whether a given date is in the past.

    Args:
        value (date): The date to be validated.

    Raises:
        ValidationError: If the input date is not in the past
        or if the year is before 1900.

    Returns:
        None
    """
    if isinstance(value, date):
        if value >= date.today() or value.year < 1900:
            raise ValidationError(
                ("Дата введена не верно.")
            )
    else:
        raise ValidationError(
            ("Дата введена не верно.")
        )
