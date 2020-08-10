from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.db.models import Q

from .tokens import job_confirm_token
from core.models import Order
from accounts.models import User
from core.tasks import send_drivers_newjob_email_task, send_order_veriff_code_email_task
from core.services.veriff_code import get_veriff_code


def find_suitable_drivers(order: Order, request):
    # TODO: remove log
    print('------------')
    print('order_start = {}, order_end = {}'.format(order.delivery_start, order.delivery_end))
    print('------------')

    drivers = User.objects.filter(Q(is_admin=False) &
                                  Q(is_active=True) &
                                  Q(email_confirmed=True) &
                                  Q(movers_num__gte=order.movers_num) &
                                  (Q(payment=order.payment) | Q(payment=3)))

    suitable_drivers_list = []
    for driver in drivers:
        if is_driver_available(driver, order):
            suitable_drivers_list.append(driver)

    # TODO: remove
    print('///////////////////')
    print('Suitable drivers')
    for driver in suitable_drivers_list:
        print(driver)
    print('///////////////////')

    order.drivers_notified = True  # must be set before notify_drivers_email(), otherwise token hash will not match
    order.save()

    notify_drivers_email(suitable_drivers_list, order, request)


def notify_drivers_email(drivers: list, order, request):
    subject = 'delivery24.ee New Job'
    current_site = get_current_site(request)
    for driver in drivers:
        to_email = driver.email
        message = {'subject': subject,
                   'first_name': driver.first_name,
                   'last_name': driver.last_name,
                   'domain': current_site.domain,
                   'order_id': order.order_id,
                   'uid': urlsafe_base64_encode(force_bytes(driver.pk)),
                   'token': job_confirm_token.make_token(driver, order),
                   }

        send_drivers_newjob_email_task.delay(to_email, **message)


def is_driver_available(driver: User, order: Order) -> bool:
    driver_works = driver.work_set.all()  # TODO: filter out too old works, maybe works with status completed
    if driver_works:
        for driver_work in driver_works:
            if not (((order.delivery_start > driver_work.delivery_start and
                      order.delivery_start > driver_work.delivery_end) and
                     (order.delivery_end > driver_work.delivery_start and
                      order.delivery_end > driver_work.delivery_end)) or
                    ((order.delivery_start < driver_work.delivery_start and
                      order.delivery_start < driver_work.delivery_end) and
                     (order.delivery_end < driver_work.delivery_start and
                      order.delivery_end < driver_work.delivery_end))):
                return False
    return True


def send_order_veriff_code_email(order, request):
    subject = 'delivery24.ee Order verification code'
    current_site = get_current_site(request)
    to_email = order.email
    message = {'subject': subject,
               'first_name': order.first_name,
               'last_name': order.last_name,
               'domain': current_site.domain,
               'order_id': order.order_id,
               'veriff_code': order.verification_code,
               }

    send_order_veriff_code_email_task.delay(to_email, **message)