from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),

    path('order/', views.OrderView.as_view(), name='order'),
    path('order/veriff/', views.OrderVeriffView.as_view(), name='veriff'),
    path('order/<slug:order_id>/', views.OrderCompleteView.as_view(), name='complete'),
    path('order/<slug:order_id>/waitdriver/', views.WaitDriver.as_view(), name='waitdriver'),

    path('partner/', views.PartnerView.as_view(), name='partner'),
    path('features/', views.FeaturesView.as_view(), name='features'),
    path('blog/', views.BlogView.as_view(), name='blog'),
    path('contact/', views.ContactView.as_view(), name='contact'),

    path('newjob/<slug:order_id>/<uidb64>/<token>/', views.NewJob.as_view(), name='newjob'),
]