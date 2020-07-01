import secrets
import string


ORDER_ID_LEN = 8


def gen_unique_order_id():
    return ''.join(secrets.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits)
                   for _ in range(ORDER_ID_LEN))
