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


class CustomPasswordChangeView(PasswordChangeView):
    login_required = True
    template_name = 'accounts/profile/changepwd.html'
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy('accounts:profile')
