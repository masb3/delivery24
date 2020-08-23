from time import sleep
from celery import shared_task

from django.template.loader import render_to_string
from django.core.mail import EmailMessage, EmailMultiAlternatives

from delivery24.celery import app
from core.models import Order, Work


@shared_task
def send_drivers_newjob_email_task(to_email, **kwargs):
    message = render_to_string('core/new_job_notify_email.html', {
        'first_name': kwargs['first_name'],
        'last_name': kwargs['last_name'],
        'domain': kwargs['domain'],
        'order_id': kwargs['order_id'],
        'uid': kwargs['uid'],
        'token': kwargs['token'],
    })
    email = EmailMessage(kwargs['subject'], message, to=[to_email])
    email.content_subtype = "html"
    email.send()


@shared_task
def send_order_veriff_code_email_task(to_email, **kwargs):
    message = render_to_string('core/order_veriff_code_send_email.html', {
        'first_name': kwargs['first_name'],
        'last_name': kwargs['last_name'],
        'domain': kwargs['domain'],
        'order_id': kwargs['order_id'],
        'veriff_code': kwargs['veriff_code'],
    })
    email = EmailMessage(kwargs['subject'], message, to=[to_email])
    email.content_subtype = "html"
    email.send()
    order = Order.objects.get(order_id=kwargs['order_id'])
    order.verification_code_sent = True
    order.save()


@shared_task
def work_confirmation_timeout_task(order_id, timeout):
    """ Waits until customer confirms proposed work (price, driver, car) """
    sleep(timeout)
    order = Order.objects.get(order_id=order_id)
    if not order.work.order_confirmed:
        order.verified = False
        order.verification_code_sent = False
        order.drivers_notified = False
        order.save()
        Work.objects.filter(pk=order.work.id).delete()


@shared_task
def driver_find_timeout_task(order_id, timeout):
    sleep(timeout)
    order = Order.objects.get(order_id=order_id)
    if order.work is None:
        order.no_free_drivers = True
        order.save()


@shared_task
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


@shared_task
def add(x, y):
    sleep(10)
    print(x+y)


@app.task
def hello_world():
    sleep(10)
    print('hello celery')
