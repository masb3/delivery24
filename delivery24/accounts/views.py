from django.shortcuts import render
from django.urls import path, reverse_lazy
from django.views.generic.edit import FormView
from .forms import SignUpForm


class SignUpView(FormView):
    template_name = 'accounts/form.html'
    form_class = SignUpForm
    success_url = reverse_lazy('core:index')

    # def form_valid(self, form):
    #     # This method is called when valid form data has been POSTed.
    #     # It should return an HttpResponse.
    #     #form.send_email()
    #     print('++++++++++++++++++++++++++++++++++++++++++')
    #     return super().form_valid(form)
