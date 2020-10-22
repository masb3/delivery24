import secrets
import string

from core.models import Order
import core.proj_conf as conf


def gen_unique_veriff_code() -> str:
    return ''.join(secrets.choice(string.digits)
                   for _ in range(conf.VERIFF_CODE_LEN))


def get_veriff_code() -> str:
    unique_veriff_code = gen_unique_veriff_code()
    is_exists = Order.objects.filter(verification_code=unique_veriff_code).exists()
    while is_exists:
        unique_veriff_code = gen_unique_veriff_code()
        is_exists = Order.objects.filter(unique_view_id=unique_veriff_code).exists()
    return unique_veriff_code


def confirm_veriff_code(veriff_code: str) -> Order:
    order = Order.objects.get(verification_code=veriff_code)
    order.verified = True
    order.verification_code = None
    order.save()
    return order


def order_veriff_code_set(order):
    order.verification_code = get_veriff_code()
    order.save()

