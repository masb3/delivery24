from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.db.models import Q

from .tokens import job_confirm_token
from core.models import Order
from core.forms import OrderForm
from accounts.models import User
from core.tasks import send_drivers_newjob_email_task, send_order_veriff_code_email_task


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
    subject = _('delivery24.ee New Job')
    current_site = get_current_site(request)
    current_lang = translation.get_language()
    for driver in drivers:
        if driver.preferred_language == 1:
            translation.activate('en-us')
        elif driver.preferred_language == 2:
            translation.activate('ru')
        else:
            pass  # TODO estonian
        to_email = driver.email
        message = render_to_string('core/new_job_notify_email.html', {
            'first_name': driver.first_name,
            'last_name': driver.last_name,
            'domain': current_site.domain,
            'order_id': order.order_id,
            'address_from': order.address_from,
            'address_to': order.address_to,
            'delivery_start': order.delivery_start,
            'delivery_end': order.delivery_end,
            'movers_num': order.movers_num,
            'uid': urlsafe_base64_encode(force_bytes(driver.pk)),
            'token': job_confirm_token.make_token(driver, order),
        })

        send_drivers_newjob_email_task.delay(to_email, message, subject)
    translation.activate(current_lang)


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
    subject = _('delivery24.ee Order verification code')
    current_site = get_current_site(request)
    to_email = order.email
    message = render_to_string('core/order_veriff_code_send_email.html', {
        'first_name': order.first_name,
        'last_name': order.last_name,
        'domain': current_site.domain,
        'order_id': order.order_id,
        'veriff_code': order.verification_code,
    })

    send_order_veriff_code_email_task.delay(to_email, message, subject=subject, order_id=order.order_id)


def change_order_prefill_form(order: Order, form: OrderForm):
    new_email = form.cleaned_data.get('email')
    new_phone = form.cleaned_data.get('phone')
    if new_email != order.email or new_phone != order.phone:
        order.email = new_email
        order.phone = new_phone
        order.verification_code_sent = False
        order.verified = False

    order.first_name = form.cleaned_data.get('first_name')
    order.last_name = form.cleaned_data.get('last_name')
    order.address_from = form.cleaned_data.get('address_from')
    order.address_to = form.cleaned_data.get('address_to')
    order.delivery_start = form.cleaned_data.get('delivery_start')
    order.delivery_end = form.cleaned_data.get('delivery_end')
    order.movers_num = form.cleaned_data.get('movers_num')
    order.message = form.cleaned_data.get('message')
    order.payment = form.cleaned_data.get('payment')

    order.no_free_drivers = False
    order.drivers_notified = False
    order.collecting_works = True
    order.save()