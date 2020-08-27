from django.urls import path

from . import profile_views as views

urlpatterns = [
    path('', views.ProfileView.as_view(), name='profile'),

    path('jobs/', views.ProfileJobs.as_view(), name='profile_jobs'),
    path('jobs/completed_jobs/', views.CompletedJobsListView.as_view(), name='profile_completed_jobs_list'),
    path('jobs/future_jobs/', views.FutureJobsListView.as_view(), name='profile_future_jobs_list'),

    path('settings/', views.ProfileSettings.as_view(), name='profile_settings'),
    path('settings/changeprofile/', views.ProfileChange.as_view(), name='profile_change'),
    path('settings/changepwd/', views.CustomPasswordChangeView.as_view(), name='changepwd'),
]
