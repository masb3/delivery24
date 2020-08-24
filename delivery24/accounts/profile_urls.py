from django.urls import path

from . import profile_views as views

urlpatterns = [
    path('', views.ProfileView.as_view(), name='profile'),
    path('changepwd/', views.CustomPasswordChangeView.as_view(), name='changepwd'),
]
