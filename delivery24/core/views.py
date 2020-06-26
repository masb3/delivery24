from django.shortcuts import render, HttpResponse, redirect, reverse,get_object_or_404
from django.views.generic import TemplateView, FormView
from core.forms import OrderForm, OrderVeriffForm
from core.models import Order, get_rand_id


class IndexView(TemplateView):
    template_name = "core/index.html"

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['order_form'] = OrderForm()
        return context


def order(request):
    template_name = "core/order.html"

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)

            unique_veriff_code = get_rand_id()
            is_exists = Order.objects.filter(verification_code=unique_veriff_code).exists()
            while is_exists:
                unique_veriff_code = get_rand_id()
                is_exists = Order.objects.filter(unique_view_id=unique_veriff_code).exists()

            order.verification_code = unique_veriff_code
            order.save()

            return redirect('core:veriff')

    else:
        form = OrderForm()

    return render(request, template_name=template_name, context={'order_form': form})


def order_veriff(request):
    template_name = "core/order_veriff.html"
    form = OrderVeriffForm()
    if request.method == 'POST':
        form = OrderVeriffForm(request.POST)
        if form.is_valid():
            veriff_code = form.cleaned_data.get('verification_code')
            try:
                order = Order.objects.get(verification_code=veriff_code)
            except Order.DoesNotExist:
                order = None

            if order:
                order.verified = True
                order.verification_code = None
                order.save()

    return render(request, template_name=template_name, context={'veriff_form': form})


class OrderFormView(FormView):
    form_class = OrderForm()
    template_name = "core/order.html"