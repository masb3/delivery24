from random import random, randrange

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseNotFound, JsonResponse, HttpResponse
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views import View

from core.forms import OrderForm, OrderVeriffForm, OrderCompleteForm
from core.models import Order, Work
from accounts.models import User

from .services.veriff_code import get_veriff_code, confirm_veriff_code
from .services.order import find_suitable_drivers
from .services.tokens import job_confirm_token


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
            order.verification_code = get_veriff_code()
            order.save()
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
        if order.work is None or order.work.order_confirmed is False:
            form = self.form_class(instance=order)
            if order.drivers_notified is False:
                drivers = find_suitable_drivers(order, request)
            return render(request, self.template_name, {'order_form': form, 'order_id': order_id})
        else:
            return render(request, self.template_name, {'confirmed': True, 'order_id': order_id})

    def post(self, request, order_id, *args, **kwargs):
        # TODO: don't confirm until driver accept job, hide confirm button
        order = get_object_or_404(Order, order_id=order_id)
        order.work.order_confirmed = True
        order.save()
        # TODO: render with green Confirmed
        return render(request, self.template_name, {'confirmed': True, 'order_id': order_id})


class WaitDriver(View):
    def get(self, request, order_id, *args, **kwargs):
        order = get_object_or_404(Order, order_id=order_id)
        if order.work_id:  # and order.work.order_confirmed is False:
            resp = JsonResponse({'foo': 'bar'})
        else:
            resp = HttpResponse(b"Please wait ...")
            resp.status_code = 301  # TODO: correct code
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