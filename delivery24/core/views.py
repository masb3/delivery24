from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from core.forms import OrderForm, OrderVeriffForm, OrderCompleteForm
from core.models import Order, gen_unique_veriff_code


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
            unique_veriff_code = gen_unique_veriff_code()
            is_exists = Order.objects.filter(verification_code=unique_veriff_code).exists()
            while is_exists:
                unique_veriff_code = gen_unique_veriff_code()
                is_exists = Order.objects.filter(unique_view_id=unique_veriff_code).exists()
            new_order.verification_code = unique_veriff_code
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
            try:
                order = Order.objects.get(verification_code=veriff_code)
            except Order.DoesNotExist:
                order = None

            if order:
                order.verified = True
                order.verification_code = None
                order.save()

                return redirect('core:complete', order_id=order.order_id)

    return render(request, template_name=template_name, context={'veriff_form': form})


def order_complete(request, order_id):
    order = Order.objects.get(order_id=order_id)
    order_complete_form = OrderCompleteForm(instance=order)

    return render(request, template_name='core/order_complete.html', context={'order_form': order_complete_form})
