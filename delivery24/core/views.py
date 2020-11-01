import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseNotFound, JsonResponse, HttpResponse, HttpResponseRedirect
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views import View

from core.forms import OrderForm, OrderVeriffForm, OrderCompleteForm
from core.models import Order, Work
from accounts.models import User

from .services.veriff_code import confirm_veriff_code, order_veriff_code_set
from .services.order import find_suitable_drivers, is_driver_available, send_order_veriff_code_email, \
    change_order_prefill_form, confirmed_order_customer_email, confirmed_order_driver_email
from .services.tokens import job_confirm_token
from .tasks import driver_find_timeout_task, send_email_task
from .proj_conf import DRIVER_FIND_TIMEOUT_S
from .utils import get_price
from delivery24 import settings


logger = logging.getLogger(__name__)


class IndexView(View):
    template_name = "core/index.html"
    form_class = OrderForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'order_form': form})


def set_language_from_url(request, user_language):
    # TODO: est
    response = HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    current_site_str = str(get_current_site(request))

    if request.method == 'GET' and \
            (current_site_str + '/' + user_language + '/') not in request.META.get('HTTP_REFERER'):
        if user_language != settings.LANGUAGE_CODE and [lang for lang in settings.LANGUAGES if lang[0] == user_language]:
            full = request.META.get('HTTP_REFERER')
            end_index = full.index(current_site_str) + len(current_site_str)
            end_path = full[end_index:]
            redirect_path = f'/{user_language}' + end_path

        elif user_language == settings.LANGUAGE_CODE:
            full = request.META.get('HTTP_REFERER')
            if current_site_str + '/ru/' in full:
                end_index = full.index(current_site_str + '/ru/') + len(current_site_str + '/ru/')
                end_path = full[end_index:]
                redirect_path = '/' + end_path
            elif current_site_str + '/et/' in full:
                end_index = full.index(current_site_str + '/et/') + len(current_site_str + '/et/')
                end_path = full[end_index:]
                redirect_path = '/' + end_path
            else:
                redirect_path = full
        else:
            return response

        translation.activate(user_language)
        response = HttpResponseRedirect(redirect_path)

    return response


class OrderView(View):
    template_name = "core/order.html"
    form_class = OrderForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order_veriff_code_set(order)
            send_order_veriff_code_email(order, request)
            request.session['order_email'] = order.email
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
        if 'order_email' in request.session:
            order_email = request.session['order_email']
            del request.session['order_email']
        else:
            order_email = ''
        return render(request, self.template_name, {'veriff_form': form, 'order_email': order_email})


class OrderCompleteView(View):
    template_name = "core/order_complete.html"
    form_class = OrderCompleteForm
    prefilled_form_class = OrderForm

    def get(self, request, order_id, *args, **kwargs):
        order = get_object_or_404(Order, order_id=order_id)
        if not order.verified:
            if not order.verification_code_sent:
                order_veriff_code_set(order)
                send_order_veriff_code_email(order, request)
            return redirect('core:veriff')

        if order.work_set.all().count == 0 or order.work_set.all().filter(order_confirmed=True).count() == 0:
            form = self.form_class(instance=order)
            if order.drivers_notified is False:
                find_suitable_drivers(order, request)
                driver_find_timeout_task.delay(order_id, DRIVER_FIND_TIMEOUT_S)
            return render(request, self.template_name, {'order_form': form, 'order_id': order_id})
        else:
            return render(request, self.template_name, {'already_confirmed': True})

    def post(self, request, order_id, *args, **kwargs):
        order = get_object_or_404(Order, order_id=order_id)
        if 'change_order' in request.POST:
            form = self.prefilled_form_class(request.POST)
            if form.is_valid():
                change_order_prefill_form(order, form)
                return redirect('core:complete', order_id=order.order_id)
            else:
                return render(request, self.template_name, {'order_form': form,
                                                            'order_id': order_id,
                                                            'change_order': True})
        else:
            if not order.verified:
                if not order.verification_code_sent:
                    order_veriff_code_set(order)
                    send_order_veriff_code_email(order, request)
                return redirect('core:veriff')
            elif order.no_free_drivers:
                form = self.prefilled_form_class(instance=order)
                form.initial['delivery_start'] = None
                form.initial['delivery_end'] = None
                return render(request, self.template_name, {'order_form': form,
                                                            'order_id': order_id,
                                                            'change_order': True})
            else:
                work_id = request.POST['work_id']
                work = order.work_set.get(id=work_id)
                work.order_confirmed = True
                work.save()
                confirmed_order_customer_email(work.id)
                confirmed_order_driver_email(work.id)
                return render(request, self.template_name, {'confirmed': True})


class WaitDriver(View):
    def get(self, request, order_id, *args, **kwargs):
        order = get_object_or_404(Order, order_id=order_id)

        if order.no_free_drivers:
            resp = JsonResponse({'no_free_drivers': True})

        elif order.work_set.all().exists() and order.collecting_works is False:
            work_min = order.work_set.all()[0]  # [0] is only one offer, filtered in driver_find_timeout_task
            driver = work_min.driver
            resp = JsonResponse({'driver_first_name': f'{driver.first_name}',
                                 'driver_last_name': f'{driver.last_name}',
                                 'driver_email': f'{driver.email}',
                                 'driver_phone': f'{driver.phone}',
                                 'car_model': f'{driver.car_model}',
                                 'price': f'{work_min.price}',
                                 'work_id': f'{work_min.id}', })
        else:
            resp = HttpResponse(_('Please wait ...').encode())  # Need to encode to bytes
            resp.status_code = 202
        return resp


class NewJob(View):
    """ Driver takes new job here """
    template_name = 'core/driver_newjob_confirm.html'
    show_order_form = OrderCompleteForm

    def get(self, request, order_id, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        order = get_object_or_404(Order, order_id=order_id)
        if user is not None and job_confirm_token.check_token(user, order, token):
            if order.work_set.filter(driver_id=user.id).exists():
                return render(request, self.template_name, context={'completed': True})
            else:
                form = self.show_order_form(instance=order)
                return render(request, self.template_name,
                              context={'order_form': form, 'order_id': order_id, 'uidb64': uidb64, 'token': token})

        return HttpResponseNotFound('<h1>Page not found</h1>')

    def post(self, request, order_id, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        order = get_object_or_404(Order, order_id=order_id)
        if user is not None and job_confirm_token.check_token(user, order, token):
            # For use case when two new orders with same delivery start/end and driver attempts to confirms both
            if not is_driver_available(user, order):
                return render(request, self.template_name, context={'driver_has_work_at_same_time': True})

            price = get_price(request.POST['price'])
            if price is None:
                form = self.show_order_form(instance=order)
                return render(request, self.template_name,
                              context={'order_form': form,
                                       'order_id': order_id,
                                       'uidb64': uidb64,
                                       'token': token,
                                       'price_error': True})
            else:
                work = Work(driver=user,
                            deliver_from=order.address_from,
                            deliver_to=order.address_to,
                            delivery_start=order.delivery_start,
                            delivery_end=order.delivery_end,
                            price=price,
                            status=1,  # TODO
                            order=order,
                            )
                work.save()
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

    def post(self, request, *args, **kwargs):
        to_email = settings.CONTACT_TO_EMAIL
        subject = 'CONTACT FORM'
        message = "<html> <b>fname:</b> {}<br><b>lname:</b> {}<br><b>email:</b> {}<br>" \
                  "<b>subject:</b> {}<br><b>message:</b> {}</html>".format(request.POST['fname'], request.POST['lname'],
                                                                           request.POST['email'], request.POST['subject'],
                                                                           request.POST['message'])
        send_email_task.delay(subject, message, to_email)
        return render(request, self.template_name, context={'message_received': True})


class PartnerView(View):
    template_name = "core/partner.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class FeaturesView(View):
    template_name = "core/features.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


def page_not_found_view(request, exception):
    return render(request, "core/errors/404.html", {})


def bad_request_view(request, exception):
    return render(request, "core/errors/400.html", {})


def server_error_view(request):
    return render(request, "core/errors/500.html", {})


def http_forbidden_view(request, exception):
    return render(request, "core/errors/403.html", {})
