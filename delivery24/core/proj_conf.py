from delivery24 import settings

if settings.DEBUG:
    CUSTOMER_CONFIRM_WORK_TIMEOUT_S = 60 * 2  # 2 minutes
    DRIVER_FIND_TIMEOUT_S = 60 * 1  # 1 minutes
    PERIODIC_SET_WORK_DONE_S = 10.0  # 10 seconds
else:
    CUSTOMER_CONFIRM_WORK_TIMEOUT_S = 60 * 10  # 10 minutes
    DRIVER_FIND_TIMEOUT_S = 60 * 3  # 3 minutes
    PERIODIC_SET_WORK_DONE_S = 60.0 * 60.0 * 1.0  # 1 hour
