from django.urls import path

from . import profile_views as views

urlpatterns = [
    path('', views.ProfileView.as_view(), name='profile'),
    path('settings/', views.ProfileSettings.as_view(), name='profile_settings'),

    path('settings/changeprofile/', views.ProfileChange.as_view(), name='profile_change'),
    path('settings/changepwd/', views.CustomPasswordChangeView.as_view(), name='changepwd'),
]
