from django.urls import path
from django.conf.urls import include
from django.contrib.auth.views import LogoutView

from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('reset/', include('accounts.pwd_reset_urls')),
    path('profile/', include('accounts.profile_urls')),
]
