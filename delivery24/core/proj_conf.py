from django.utils.translation import ugettext_lazy as _

from delivery24 import settings


if settings.DEBUG:
    CUSTOMER_CONFIRM_WORK_TIMEOUT_S = 60 * 2  # 2 minutes
    DRIVER_FIND_TIMEOUT_S = 60 * 1  # 1 minutes
    PERIODIC_SET_WORK_DONE_S = 10.0  # 10 seconds
    PERIODIC_DELETE_UNCONFIRMED_SIGNUP_S = 60 * 1  # 1 minute
    USER_SIGNUP_CONFIRM_TIMEOUT_S = 60 * 1  # 1 minute
else:
    CUSTOMER_CONFIRM_WORK_TIMEOUT_S = 60 * 10  # 10 minutes
    DRIVER_FIND_TIMEOUT_S = 60 * 3  # 3 minutes
    PERIODIC_SET_WORK_DONE_S = 60.0 * 60.0 * 1.0  # 1 hour
    PERIODIC_DELETE_UNCONFIRMED_SIGNUP_S = 60 * 15  # 15 minutes
    USER_SIGNUP_CONFIRM_TIMEOUT_S = 60 * 15  # 15 minutes

#######################################################################
VERIFF_CODE_LEN = 4
ORDER_ID_LEN = 8

PAYMENT_METHOD_CASH = 0
PAYMENT_METHOD_BANK = 1
PAYMENT_METHOD_BOTH = 2

# Below are choices used in User and Order models
PAYMENT_METHOD = [
    (PAYMENT_METHOD_CASH, _('Cash')),
    # (PAYMENT_METHOD_BANK, _('Bank')),
    # (PAYMENT_METHOD_BOTH, _('Both')),
]

PREFERRED_LANGUAGE = [
    (1, _('English')),
    (2, _('Russian')),
    (3, _('Estonian')),
]

CAR_TYPE = [
    (1, _('S')),
    (2, _('M')),
    (3, _('L')),
]

WORK_STATUS = [
    (1, 'Not started'),
    (2, 'In progress'),
    (3, 'Done'),
    (4, 'Canceled'),
]

