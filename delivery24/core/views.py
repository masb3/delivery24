from random import random, randrange

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseNotFound, JsonResponse, HttpResponse
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views import View

from core.forms import OrderForm, OrderVeriffForm, OrderCompleteForm
from core.models import Order, Work
from accounts.models import User

from .services.veriff_code import confirm_veriff_code, order_veriff_code_set
from .services.order import find_suitable_drivers, is_driver_available, send_order_veriff_code_email
from .services.tokens import job_confirm_token
from .tasks import work_confirmation_timeout_task, driver_find_timeout_task
from .proj_conf import CUSTOMER_CONFIRM_WORK_TIMEOUT_S, DRIVER_FIND_TIMEOUT_S


class IndexView(View):
    template_name = "core/index.html"
    form_class = OrderForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'order_form': form})


class OrderView(View):
    template_name = "core/order.html"
    form_class = OrderForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order_veriff_code_set(order)
            send_order_veriff_code_email(order, request)
            return redirect('core:veriff')
        else:
            return render(request, self.template_name, {'order_form': form})

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'order_form': form})


class OrderVeriffView(View):
    template_name = "core/order_veriff.html"
    form_class = OrderVeriffForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            veriff_code = form.cleaned_data.get('verification_code')
            new_order = confirm_veriff_code(veriff_code)
            return redirect('core:complete', order_id=new_order.order_id)
        else:
            return render(request, self.template_name, {'veriff_form': form})

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'veriff_form': form})


class OrderCompleteView(View):
    template_name = "core/order_complete.html"
    form_class = OrderCompleteForm

    def get(self, request, order_id, *args, **kwargs):
        order = get_object_or_404(Order, order_id=order_id)
        if not order.verified:
            if not order.verification_code_sent:
                order_veriff_code_set(order)
                send_order_veriff_code_email(order, request)
            return redirect('core:veriff')

        if order.work is None or order.work.order_confirmed is False:
            form = self.form_class(instance=order)
            if order.drivers_notified is False:
                find_suitable_drivers(order, request)
                driver_find_timeout_task.delay(order_id, DRIVER_FIND_TIMEOUT_S)
            return render(request, self.template_name, {'order_form': form, 'order_id': order_id})
        else:
            return render(request, self.template_name, {'already_confirmed': True})

    def post(self, request, order_id, *args, **kwargs):
        order = get_object_or_404(Order, order_id=order_id)
        if not order.verified:
            if not order.verification_code_sent:
                order_veriff_code_set(order)
                send_order_veriff_code_email(order, request)
            return redirect('core:veriff')
        elif order.no_free_drivers:
            return redirect('core:order')
        else:
            order.work.order_confirmed = True
            order.work.save()
            return render(request, self.template_name, {'confirmed': True})


class WaitDriver(View):
    def get(self, request, order_id, *args, **kwargs):
        order = get_object_or_404(Order, order_id=order_id)

        if order.no_free_drivers:
            resp = JsonResponse({'no_free_drivers': True})

        elif order.work_id:
            driver = order.work.driver
            driver_email = driver.email
            driver_first_name = driver.first_name
            driver_last_name = driver.first_name
            driver_phone = driver.phone
            car_model = driver.car_model
            price = order.work.price

            resp = JsonResponse({'driver_first_name': f'{driver_first_name}',
                                 'driver_last_name': f'{driver_last_name}',
                                 'driver_email': f'{driver_email}',
                                 'driver_phone': f'{driver_phone}',
                                 'car_model': f'{car_model}',
                                 'price': f'{price}', })
        else:
            resp = HttpResponse(b"Please wait ...")
            resp.status_code = 202
        return resp


class NewJob(View):
    """ Driver takes new job here """
    template_name = 'core/driver_newjob_confirm.html'

    def get(self, request, order_id, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        order = get_object_or_404(Order, order_id=order_id)
        if user is not None and job_confirm_token.check_token(user, order, token):
            if order.work is not None:
                return render(request, self.template_name, context={'completed': True})
            else:
                return render(request, self.template_name,
                              context={'order_id': order_id, 'uidb64': uidb64, 'token': token})

        return HttpResponseNotFound('<h1>Page not found</h1>')

    def post(self, request, order_id, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        order = get_object_or_404(Order, order_id=order_id)
        if user is not None and job_confirm_token.check_token(user, order, token):
            if order.work is None:
                # For use case when two new orders with same delivery start/end and driver attempts to confirms both
                if not is_driver_available(user, order):
                    return render(request, self.template_name, context={'driver_has_work_at_same_time': True})

                work = Work(driver=user,
                            deliver_from=order.address_from,
                            deliver_to=order.address_to,
                            delivery_start=order.delivery_start,
                            delivery_end=order.delivery_end,
                            price=randrange(30, 150.0) + random(),  # TODO
                            status=1,  # TODO
                            )
                work.save()
                order.work = work
                order.save()

                #  Now driver is reserved for specific start/end date, release reservation if customer not confirm work
                work_confirmation_timeout_task.delay(order_id, CUSTOMER_CONFIRM_WORK_TIMEOUT_S)

            return render(request, self.template_name, context={'completed': True})

        return HttpResponseNotFound('<h1>Page not found</h1>')


class BlogView(View):
    template_name = "core/blog.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class ContactView(View):
    template_name = "core/contact.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class PartnerView(View):
    template_name = "core/partner.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class FeaturesView(View):
    template_name = "core/features.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)