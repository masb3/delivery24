from django.shortcuts import render, HttpResponse
from django.views.generic import TemplateView
from core.forms import OrderForm


class IndexView(TemplateView):
    template_name = "core/index.html"

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['order_form'] = OrderForm()
        return context
