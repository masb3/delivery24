import logging

from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.db.models import Q

import core.proj_conf as conf

from .tokens import job_confirm_token
from core.models import Order, Work
from core.forms import OrderForm
from core.utils import set_language
from accounts.models import User
from core.tasks import send_order_veriff_code_email_task, send_email_task


logger = logging.getLogger(__name__)


def find_suitable_drivers(order: Order, request):
    logger.debug('order_start = {}, order_end = {}'.format(order.delivery_start, order.delivery_end))

    drivers = User.objects.filter(Q(is_admin=False) &
                                  Q(is_active=True) &
                                  Q(email_confirmed=True) &
                                  Q(movers_num__gte=order.movers_num) &
                                  (Q(payment=order.payment) | Q(payment=conf.PAYMENT_METHOD_BOTH)))

    suitable_drivers_list = []
    for driver in drivers:
        if is_driver_available(driver, order):
            suitable_drivers_list.append(driver)

    logger.debug('Suitable drivers')
    for driver in suitable_drivers_list:
        logger.debug(driver)

    order.drivers_notified = True  # must be set before notify_drivers_email(), otherwise token hash will not match
    order.save()

    notify_drivers_email(suitable_drivers_list, order, request)


def notify_drivers_email(drivers: list, order, request):
    subject = _('New Job')
    current_site = get_current_site(request)
    current_lang = translation.get_language()
    for driver in drivers:
        set_language(driver.preferred_language)
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
            'payment_method': conf.PAYMENT_METHOD[order.payment][1],
            'uid': urlsafe_base64_encode(force_bytes(driver.pk)),
            'token': job_confirm_token.make_token(driver, order),
        })

        send_email_task.delay(subject, message, to_email)
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
    subject = _('Order verification code')
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
    order.car_type = form.cleaned_data.get('car_type')
    order.message = form.cleaned_data.get('message')
    order.payment = form.cleaned_data.get('payment')

    order.no_free_drivers = False
    order.drivers_notified = False
    order.collecting_works = True
    order.save()


def confirmed_order_customer_email(work_id: Work.id):
    work = Work.objects.get(id=work_id)
    subject = _('Order confirmed')
    to_email = work.order.email
    message = render_to_string('core/order_complete_customer_email.html', {
        'first_name': work.order.first_name,
        'last_name': work.order.last_name,
        'address_from': work.order.address_from,
        'address_to': work.order.address_to,
        'delivery_start': work.order.delivery_start,
        'delivery_end': work.order.delivery_end,
        'movers_num': work.order.movers_num,
        'price': work.price,
        'payment_method': conf.PAYMENT_METHOD[work.order.payment][1],
        'driver_name': str(work.driver.first_name) + ' ' + str(work.driver.last_name),
        'driver_phone': work.driver.phone,
    })
    send_email_task.delay(subject, message, to_email)


def confirmed_order_driver_email(work_id: Work.id):
    current_lang = translation.get_language()
    work = Work.objects.get(id=work_id)

    set_language(work.driver.preferred_language)

    subject = _('New Job Accepted')
    message = render_to_string('core/new_job_accepted_email.html', {
        'first_name': work.driver.first_name,
        'last_name': work.driver.last_name,
        'address_from': work.order.address_from,
        'address_to': work.order.address_to,
        'delivery_start': work.order.delivery_start,
        'delivery_end': work.order.delivery_end,
        'movers_num': work.order.movers_num,
        'price': work.price,
        'payment_method': conf.PAYMENT_METHOD[work.order.payment][1],
        'customer_name': str(work.order.first_name) + ' ' + str(work.order.last_name),
        'customer_phone': work.order.phone,
    })
    send_email_task.delay(subject, message, work.driver.email)

    translation.activate(current_lang)