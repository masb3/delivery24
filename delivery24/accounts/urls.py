from django.urls import path, reverse_lazy
from django.conf.urls import url
from django.contrib.auth.views import LogoutView, LoginView, PasswordChangeView, \
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView

from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
]