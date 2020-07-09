from django.shortcuts import render, redirect
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View

from core.forms import OrderForm, OrderVeriffForm, OrderCompleteForm
from core.models import Order
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
        order = Order.objects.get(order_id=order_id)
        form = self.form_class(instance=order)
        if order.work is None:
            drivers = find_suitable_drivers(order, request)
            # TODO: notify_drivers(drivers)
        return render(request, self.template_name, {'order_form': form})


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


class NewJob(View):
    template_name = 'core/driver_newjob_confirm.html'

    def get(self, request, order_id, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and job_confirm_token.check_token(user, token):
            # TODO: some logic here
            pass

        return render(request, self.template_name, context={'order_id': order_id, 'uidb64': uidb64, 'token': token})

    def post(self, request, order_id, uidb64, token, *args, **kwargs):
        return render(request, self.template_name, context={'order_id': order_id, 'uidb64': uidb64, 'token': token})
