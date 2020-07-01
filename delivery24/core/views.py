from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from core.forms import OrderForm, OrderVeriffForm, OrderCompleteForm
from core.models import Order

from .services.veriff_code import get_veriff_code, confirm_veriff_code


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
            new_order = form.save(commit=False)
            new_order.verification_code = get_veriff_code()
            new_order.save()
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
            new_order = confirm_veriff_code(veriff_code)
            return redirect('core:complete', order_id=new_order.order_id)

    return render(request, template_name=template_name, context={'veriff_form': form})


def order_complete(request, order_id):
    new_order = Order.objects.get(order_id=order_id)
    order_complete_form = OrderCompleteForm(instance=new_order)

    return render(request, template_name='core/order_complete.html', context={'order_form': order_complete_form})
