from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView, FormView
from .forms import CustomPasswordChangeForm, ChangeProfileForm
from django.urls import reverse_lazy
from django.shortcuts import render


class ProfileView(LoginRequiredMixin, View):
    login_required = True
    template_name = "accounts/profile/profile.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'profile': request.user})


class ProfileSettings(LoginRequiredMixin, View):
    login_required = True
    template_name = "accounts/profile/settings.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'profile': request.user})


class ProfileChange(LoginRequiredMixin, FormView):
    login_required = True
    template_name = "accounts/profile/profile_change.html"
    form_class = ChangeProfileForm
    success_url = reverse_lazy('accounts:profile')

    def form_valid(self, form):
        self.request.user.first_name = form.cleaned_data.get('first_name')
        self.request.user.last_name = form.cleaned_data.get('last_name')
        self.request.user.phone = form.cleaned_data.get('phone')
        self.request.user.car_model = form.cleaned_data.get('car_model')
        self.request.user.car_number = form.cleaned_data.get('car_number').replace(' ', '').upper()
        self.request.user.car_carrying = form.cleaned_data.get('car_carrying')
        self.request.user.movers_num = form.cleaned_data.get('movers_num')
        self.request.user.payment = form.cleaned_data.get('payment')

        self.request.user.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class CustomPasswordChangeView(PasswordChangeView):
    login_required = True
    template_name = 'accounts/profile/changepwd.html'
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy('accounts:profile')
