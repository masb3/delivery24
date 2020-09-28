import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def ik_validator(ik: int):
    """
    Isikukood validator
    Verifies Estonian national id (isikukood) validity
    :param ik: Estonian national id (isikukood)
    :return: Raises Django 'ValidationError' on failure
    """
    multipliers1 = (1, 2, 3, 4, 5, 6, 7, 8, 9, 1)
    multipliers2 = (3, 4, 5, 6, 7, 8, 9, 1, 2, 3)
    divider = 11

    ik_list = list(map(int, str(ik)))

    check_num = sum(list(map(lambda x, y: x * y, ik_list, multipliers1))) % divider

    if check_num == 10:
        check_num = sum(list(map(lambda x, y: x * y, ik_list, multipliers2))) % divider

    if check_num == 10:
        check_num = 0

    if ik_list[-1] != check_num:
        raise ValidationError(
            _('Isikukood is incorrect'),
            params={'ik': ik},
        )


def car_number_validator(num: str):
    """
    Verifies entered car number
    :param num: car number
    :return:
    """
    pattern1 = re.compile(r'^\d{3}[A-Za-z]{3}$')  # 123abc
    pattern2 = re.compile(r'^\d{3} [A-Za-z]{3}$')  # 123 abc
    pattern3 = re.compile(r'^[A-Za-z]{6}\d{1}$')  # abcdef1
    pattern4 = re.compile(r'^\d{2}[A-Za-z]{3}$')  # 12abc

    if not pattern1.match(num) and \
            not pattern2.match(num) and \
            not pattern3.match(num) and \
            not pattern4.match(num):
        raise ValidationError(
            _('Car number is incorrect'),
            params={'car_number': num},
        )


def get_price(str_price):
    """
    Converts entered price to int
    :param str_price:
    :return: Price on success, otherwise None
    """
    try:
        price = int(str_price)
        if price <= 0:
            return None
        return price
    except ValueError:
        return None


if __name__ == '__main__':
    pass
