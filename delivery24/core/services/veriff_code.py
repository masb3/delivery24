import secrets
import string

from core.models import Order


VERIFF_CODE_LEN = 4


def gen_unique_veriff_code() -> int:
    return int(''.join(secrets.choice(string.digits)
                       for _ in range(VERIFF_CODE_LEN)))


def get_veriff_code() -> int:
    unique_veriff_code = gen_unique_veriff_code()
    is_exists = Order.objects.filter(verification_code=unique_veriff_code).exists()
    while is_exists:
        unique_veriff_code = gen_unique_veriff_code()
        is_exists = Order.objects.filter(unique_view_id=unique_veriff_code).exists()
    return unique_veriff_code


def confirm_veriff_code(veriff_code: int) -> Order:
    order = Order.objects.get(verification_code=veriff_code)
    order.verified = True
    order.verification_code = None
    order.save()
    return order
