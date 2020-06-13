from django.urls import path, reverse_lazy
from django.contrib.auth.views import PasswordResetDoneView, \
    PasswordResetConfirmView, PasswordResetCompleteView

from . import views

urlpatterns = [
    path('', views.CustomPasswordResetView.as_view(success_url=reverse_lazy('accounts:password_reset_done'),
                                                   template_name='accounts/password_reset_form.html',
                                                   email_template_name='accounts/password_reset_email.html',
                                                   subject_template_name='accounts/password_reset_subject.txt'),
         name='password_reset'),

    path('done/', PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'),
         name='password_reset_done'),

    path('<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(success_url=reverse_lazy('accounts:password_reset_complete'),
                                          template_name='accounts/password_reset_confirm.html'),
         name='password_reset_confirm'),

    path('complete/', PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'),
         name='password_reset_complete'),
]
