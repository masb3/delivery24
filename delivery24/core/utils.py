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
            _('Isikukood is not correct'),
            params={'ik': ik},
        )


if __name__ == '__main__':
    pass
