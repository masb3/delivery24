from django.urls import path

from . import views

urlpatterns = [
    path('', views.ProfileView.as_view(), name='profile'),
    path('changepwd/', views.CustomPasswordChangeView.as_view(), name='changepwd'),
]
