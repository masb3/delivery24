from django.urls import path
from django.contrib.auth.views import PasswordResetDoneView, PasswordResetCompleteView

from . import pwd_reset_views as views

urlpatterns = [
    path('', views.CustomPasswordResetView.as_view(), name='password_reset'),

    path('done/', PasswordResetDoneView.as_view(template_name='accounts/pwd_reset/password_reset_done.html'),
         name='password_reset_done'),

    path('<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    path('complete/', PasswordResetCompleteView.as_view(template_name='accounts/pwd_reset/password_reset_complete.html'),
         name='password_reset_complete'),
]
