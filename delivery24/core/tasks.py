from time import sleep
from celery import shared_task

from django.template.loader import render_to_string
from django.core.mail import EmailMessage

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
def work_confirmation_timeout_task(order_id, timeout):
    """ Waits until customer confirms proposed work (price, driver, car) """
    sleep(timeout)
    order = Order.objects.get(order_id=order_id)
    if not order.work.order_confirmed:
        order.verified = False
        order.drivers_notified = False
        order.save()
        Work.objects.filter(pk=order.work.id).delete()


@shared_task
def add(x, y):
    sleep(10)
    print(x+y)


@app.task
def hello_world():
    sleep(10)
    print('hello celery')
