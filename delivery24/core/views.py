from django.shortcuts import render, HttpResponse
from django.views.generic import TemplateView
from core.forms import OrderForm


class IndexView(TemplateView):
    template_name = "core/index.html"

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['order_form'] = OrderForm()
        return context


def index(request):
    template_name = "core/index.html"
    context = {'order_form': OrderForm()}

    if request.method == 'POST':
        print('*************************************++++')

    if request.method == 'GET':
        print('----------------*************************************++++')

    return render(request, template_name=template_name, context=context)