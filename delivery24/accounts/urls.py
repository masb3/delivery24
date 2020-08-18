from django.urls import path, reverse_lazy
from django.conf.urls import include
from django.contrib.auth.views import LogoutView, PasswordChangeView

from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('changepwd/', PasswordChangeView.as_view(template_name='accounts/changepwd.html',
                                                  success_url=reverse_lazy('core:index')), name='changepwd'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('reset/', include('accounts.pwd_reset_urls')),
    # TODO: profile
    # path('profile/', views.profile, name='profile'),
]
