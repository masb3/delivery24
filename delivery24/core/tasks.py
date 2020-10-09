import datetime

from time import sleep

from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import EmailMessage, EmailMultiAlternatives

from delivery24.celery import app
from .proj_conf import PERIODIC_SET_WORK_DONE_S, CUSTOMER_CONFIRM_WORK_TIMEOUT_S
from core.models import Order, Work
from accounts.models import User


@app.task
def send_drivers_newjob_email_task(to_email, message, subject):
    email = EmailMessage(subject, message, to=[to_email])
    email.content_subtype = "html"
    email.send()


@app.task
def send_order_veriff_code_email_task(to_email, message, subject, order_id):
    email = EmailMessage(subject, message, to=[to_email])
    email.content_subtype = "html"
    email.send()
    order = Order.objects.get(order_id=order_id)
    order.verification_code_sent = True
    order.save()


@app.task
def send_driver_offer_accepted_email_task(driver_id):
    # TODO
    print('++++++++++++ ACCEPTED ++++++++++++++')
    print(User.objects.get(id=driver_id))


@app.task
def send_driver_offer_not_accepted_email_task(driver_id):
    # TODO
    print('++++++++++++ NOT ACCEPTED ++++++++++++++')
    print(User.objects.get(id=driver_id))


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

        print('+++++++++++ CUSTOMER CONFIRM WORK TIMEOUT ++++++++++++++++')  # TODO: remove log
        send_driver_offer_not_accepted_email_task.delay(work.driver.id)
        work.delete()
    else:
        send_driver_offer_accepted_email_task.delay(work.driver.id)


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
                send_driver_offer_not_accepted_email_task.delay(offer_min.driver.id)
                offer_min.delete()
                offer_min = offer
            else:
                send_driver_offer_not_accepted_email_task.delay(offer.driver.id)
                offer.delete()
        customer_work_confirmation_timeout_task.delay(offer_min.id, CUSTOMER_CONFIRM_WORK_TIMEOUT_S)
    order.save()


@app.task
def reset_password_email_task(subject_template_name, email_template_name, to_email, **kwargs):
    subject = render_to_string(subject_template_name, {
        'email': kwargs['email'],
        'domain': kwargs['domain'],
        'site_name': kwargs['site_name'],
        'uid': kwargs['uid'],
        'user': kwargs['user'],
        'token': kwargs['token'],
        'protocol': kwargs['protocol'],
    })
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    body = render_to_string(email_template_name, {
        'email': kwargs['email'],
        'domain': kwargs['domain'],
        'site_name': kwargs['site_name'],
        'uid': kwargs['uid'],
        'user': kwargs['user'],
        'token': kwargs['token'],
        'protocol': kwargs['protocol'],
    })

    email = EmailMultiAlternatives(subject, body, to=[to_email])
    email.content_subtype = "text"
    email.send()


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    beat_time = PERIODIC_SET_WORK_DONE_S
    sender.add_periodic_task(beat_time, set_work_done.s(), name='periodically set work done')


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
        print(work.status)
