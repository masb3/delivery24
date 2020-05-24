from django.shortcuts import render
from django.urls import path, reverse_lazy
from django.views.generic.edit import FormView
from .forms import SignUpForm, LoginForm


class SignUpView(FormView):
    template_name = 'accounts/form.html'
    form_class = SignUpForm
    success_url = reverse_lazy('core:index')


# class LoginView(FormView):
#     template_name = 'accounts/form.html'
#     form_class = LoginForm
#     success_url = reverse_lazy('core:index')