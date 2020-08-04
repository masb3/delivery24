from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.db.models import Q


from .tokens import job_confirm_token
from core.models import Order, Work
from accounts.models import User


def find_suitable_drivers(order: Order, request) -> list:
    # TODO: remove log
    print('------------')
    print('order_start = {}, order_end = {}'.format(order.delivery_start, order.delivery_end))
    print('------------')

    # drivers = User.objects.filter(is_admin=False,
    #                               is_active=True,
    #                               email_confirmed=True,
    #                               movers_num__gte=order.movers_num,
    #                               payment=order.payment,
    #                               )
    drivers = User.objects.filter(Q(is_admin=False) &
                                  Q(is_active=True) &
                                  Q(email_confirmed=True) &
                                  Q(movers_num__gte=order.movers_num) &
                                  (Q(payment=order.payment) | Q(payment=3)))

    suitable_drivers_list = []
    for driver in drivers:
        if driver.work_set.all():  # Drivers with work
            driver_ok = True  # For use case if one of driver's work is suitable and other is not
            for driver_work in driver.work_set.all():
                if not (((order.delivery_start > driver_work.delivery_start and
                          order.delivery_start > driver_work.delivery_end) and
                         (order.delivery_end > driver_work.delivery_start and
                          order.delivery_end > driver_work.delivery_end)) or
                        ((order.delivery_start < driver_work.delivery_start and
                          order.delivery_start < driver_work.delivery_end) and
                         (order.delivery_end < driver_work.delivery_start and
                          order.delivery_end < driver_work.delivery_end))):
                    driver_ok = False
            if driver_ok:
                suitable_drivers_list.append(driver)
        else:  # Drivers without work
            suitable_drivers_list.append(driver)

    # TODO: remove
    print('///////////////////')
    print('Suitable drivers')
    for driver in suitable_drivers_list:
        print(driver)
    print('///////////////////')

    # order.drivers_notified = True must be set before notify_drivers_email(), otherwise token hash will not match
    order.drivers_notified = True
    order.save()

    notify_drivers_email(suitable_drivers_list, order, request)


def notify_drivers_email(drivers: list, order, request):
    subject = 'delivery24.ee New Job'
    current_site = get_current_site(request)
    for driver in drivers:
        message = render_to_string('core/new_job_notify_email.html', {
            'user': driver,
            'domain': current_site.domain,
            'order': order.order_id,
            'uid': urlsafe_base64_encode(force_bytes(driver.pk)),
            'token': job_confirm_token.make_token(driver, order),
        })
        to_email = driver.email
        email = EmailMessage(subject, message, to=[to_email])
        email.content_subtype = "html"
        email.send()

# work = Work()
# work.driver = driver
# work.price = 123
# work.delivery_start = order.delivery_start
# work.delivery_end = order.delivery_end
# work.deliver_to = order.address_to
# work.deliver_from = order.address_from
# work.status = Work.WORK_STATUS[0][0]
# work.save()
