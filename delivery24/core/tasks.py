import datetime
import logging

from time import sleep

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils import translation
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

from delivery24.celery import app
from .proj_conf import PERIODIC_SET_WORK_DONE_S, CUSTOMER_CONFIRM_WORK_TIMEOUT_S, \
    PERIODIC_DELETE_UNCONFIRMED_SIGNUP_S, USER_SIGNUP_CONFIRM_TIMEOUT_S
from core.models import Order, Work
from core.utils import set_language
from accounts.models import User


logger = logging.getLogger('celery')


@app.task
def send_email_task(subject, message, to_email):
    email = EmailMessage(subject, message, to=[to_email])
    email.content_subtype = "html"
    email.send()


@app.task
def send_order_veriff_code_email_task(to_email, message, subject, order_id):
    send_email_task(subject, message, to_email)
    order = Order.objects.get(order_id=order_id)
    order.verification_code_sent = True
    order.save()


@app.task
def send_driver_offer_accepted_email_task(work_id):
    current_lang = translation.get_language()
    work = Work.objects.get(id=work_id)

    logger.info('++++++++++++ ACCEPTED ++++++++++++++')
    logger.info(User.objects.get(id=work.driver.id))

    set_language(work.driver.preferred_language)

    subject = _('delivery24.ee New Job Accepted')
    message = render_to_string('core/new_job_accepted_email.html', {
        'first_name': work.driver.first_name,
        'last_name': work.driver.last_name,
        'address_from': work.order.address_from,
        'address_to': work.order.address_to,
        'delivery_start': work.order.delivery_start,
        'delivery_end': work.order.delivery_end,
        'movers_num': work.order.movers_num,
        'price': work.price,
    })
    send_email_task(subject, message, work.driver.email)

    translation.activate(current_lang)


@app.task
def send_driver_offer_not_accepted_email_task(work_id):
    current_lang = translation.get_language()
    work = Work.objects.get(id=work_id)
    logger.info('++++++++++++ NOT ACCEPTED ++++++++++++++')
    logger.info(User.objects.get(id=work.driver.id))

    set_language(work.driver.preferred_language)

    subject = _('delivery24.ee New Job Canceled')
    message = render_to_string('core/new_job_not_accepted_email.html', {
        'first_name': work.driver.first_name,
        'last_name': work.driver.last_name,
        'address_from': work.order.address_from,
        'address_to': work.order.address_to,
        'delivery_start': work.order.delivery_start,
        'delivery_end': work.order.delivery_end,
        'movers_num': work.order.movers_num,
        'price': work.price,
    })
    send_email_task(subject, message, work.driver.email)

    work.delete()
    translation.activate(current_lang)


@app.task
def customer_work_confirmation_timeout_task(work_id, timeout):
    sleep(timeout)
    work = Work.objects.get(id=work_id)
    if not work.order_confirmed:
        work.order.verified = False
        work.order.verification_code_sent = False
        work.order.drivers_notified = False
        work.order.collecting_works = True
        work.order.save()

        logger.info('+++++++++++ CUSTOMER CONFIRM WORK TIMEOUT ++++++++++++++++')
        send_driver_offer_not_accepted_email_task.delay(work.id)
    else:
        send_driver_offer_accepted_email_task.delay(work.id)


@app.task
def driver_find_timeout_task(order_id, timeout):
    sleep(timeout)
    order = Order.objects.get(order_id=order_id)
    order.collecting_works = False
    if order.work_set.all().count() == 0:
        order.no_free_drivers = True
    else:
        # Choose cheapest work, rework to let customer choose by himself TODO: DEL-153
        offers = order.work_set.all().order_by('created')
        offer_min = offers[0]
        for offer in offers[1:]:
            if offer.price < offer_min.price:
                send_driver_offer_not_accepted_email_task.delay(offer_min.id)
                offer_min = offer
            else:
                send_driver_offer_not_accepted_email_task.delay(offer.id)
        customer_work_confirmation_timeout_task.delay(offer_min.id, CUSTOMER_CONFIRM_WORK_TIMEOUT_S)
    order.save()


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(PERIODIC_SET_WORK_DONE_S, set_work_done.s(), name='periodically set work done')
    sender.add_periodic_task(PERIODIC_DELETE_UNCONFIRMED_SIGNUP_S,
                             delete_unconfirmed_user_signup.s(), name='periodically clear unconfirmed user signup')


@app.task
def set_work_done():
    time_now_delta = timezone.now() + datetime.timedelta(hours=0)  # Tallinn time UTC+3
    works = Work.objects.filter(status__lt=Work.WORK_STATUS[2][0], delivery_end__lt=time_now_delta)

    for work in works:
        if work.order_confirmed:
            work.status = Work.WORK_STATUS[2][0]  # Done
        else:
            work.status = Work.WORK_STATUS[3][0]  # Canceled
        work.save()
        logger.info(work.status)


@app.task
def delete_unconfirmed_user_signup():
    time_now_delta = timezone.now() - datetime.timedelta(seconds=USER_SIGNUP_CONFIRM_TIMEOUT_S)
    users = User.objects.filter(is_active=False, email_confirmed=False, is_admin=False, created_at__lt=time_now_delta)
    for user in users:
        logger.info('delete unconfirmed signup {}'.format(user))
        user.delete()