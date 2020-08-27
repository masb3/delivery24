from django.views import View
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView, FormView
from .forms import CustomPasswordChangeForm, ChangeProfileForm
from django.urls import reverse_lazy
from django.shortcuts import render

from core.models import Work


class ProfileView(LoginRequiredMixin, View):
    login_required = True
    template_name = "accounts/profile/profile.html"

    def get(self, request, *args, **kwargs):
        jobs = request.user.work_set.all()  # TODO: completed jobs
        total_income = 0
        for _ in jobs:
            total_income += _.price
        total_income = round(total_income, 2)
        return render(request, self.template_name, {'profile': request.user, 'total_income': total_income})


class ProfileJobs(LoginRequiredMixin, View):
    login_required = True
    template_name = "accounts/profile/jobs.html"

    def get(self, request, *args, **kwargs):
        completed_jobs_number = request.user.work_set.filter(status=Work.WORK_STATUS[2][0]).count()
        future_jobs_number = request.user.work_set.filter(status__lt=Work.WORK_STATUS[2][0],
                                                          order_confirmed=True).count()
        return render(request, self.template_name, {'completed_jobs_number': completed_jobs_number,
                                                    'future_jobs_number': future_jobs_number})


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

    def get_initial(self):
        """ Prefill form with user data """
        initial = super(ProfileChange, self).get_initial()
        initial['first_name'] = self.request.user.first_name
        initial['last_name'] = self.request.user.last_name
        initial['phone'] = self.request.user.phone
        initial['car_model'] = self.request.user.car_model
        initial['car_number'] = self.request.user.car_number
        initial['car_carrying'] = self.request.user.car_carrying
        initial['movers_num'] = self.request.user.movers_num
        initial['payment'] = self.request.user.payment

        return initial

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


class CompletedJobsListView(LoginRequiredMixin, ListView):
    login_required = True
    model = Work
    paginate_by = 2
    template_name = 'accounts/profile/completed_jobs_list.html'

    def get_queryset(self):
        queryset = super(CompletedJobsListView, self).get_queryset()
        return queryset.filter(driver=self.request.user.pk, status__gte=Work.WORK_STATUS[2][0])


class FutureJobsListView(LoginRequiredMixin, ListView):
    login_required = True
    model = Work
    paginate_by = 2
    template_name = 'accounts/profile/future_jobs_list.html'

    def get_queryset(self):
        queryset = super(FutureJobsListView, self).get_queryset()
        return queryset.filter(driver=self.request.user.pk, status__lte=Work.WORK_STATUS[1][0])
