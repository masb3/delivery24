from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('order/', views.order, name='order'),
    path('order/veriff/', views.order_veriff, name='veriff'),
    path('order/<slug:order_id>/', views.order_complete, name='complete'),
]