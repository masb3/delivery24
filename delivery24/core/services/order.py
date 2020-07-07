from django.db.models import Q

from core.models import Order, Work
from accounts.models import User


def find_suitable_drivers(order: Order):
    # TODO: remove log
    print('------------')
    print('order_start = {}, order_end = {}'.format(order.delivery_start, order.delivery_end))
    print('------------')

    # Get drivers without work
    drivers = User.objects.filter(is_active=True,
                                  email_confirmed=True,
                                  movers_num__gte=order.movers_num,
                                  )
    suitable_drivers_list = []
    for driver in drivers:
        if driver.work_set.all():  # Drivers with work
            driver_ok = True  # For use case if one of driver's work is suitable and other is not
            for driver_work in driver.work_set.all():
                if not ((driver_work.delivery_start <= order.delivery_start <= driver_work.delivery_end) or
                        (driver_work.delivery_start <= order.delivery_end <= driver_work.delivery_end)):
                    driver_ok = False
            if driver_ok:
                suitable_drivers_list.append(driver)
        else:  # Drivers without work
            suitable_drivers_list.append(driver)

    # TODO: remove
    for driver in suitable_drivers_list:
        print(driver)

# work = Work()
# work.driver = driver
# work.price = 123
# work.deliver_date = order.delivery_start
# work.deliver_to = order.address_to
# work.deliver_from = order.address_from
# work.status = Work.WORK_STATUS[0][0]
# work.save()
