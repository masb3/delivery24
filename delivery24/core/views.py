from django.shortcuts import render, HttpResponse, redirect, reverse
from django.views.generic import TemplateView, FormView
from core.forms import OrderForm


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
            pass

    else:
        form = OrderForm()

    return render(request, template_name=template_name, context={'order_form': form})


class OrderFormView(FormView):
    form_class = OrderForm()
    template_name = "core/order.html"