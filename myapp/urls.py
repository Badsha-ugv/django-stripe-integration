from django.urls import path
from . import views

urlpatterns = [
    path('', views.package_list, name='package_list'),
    path('subscribe/<int:package_id>/', views.subscribe, name='subscribe'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('secret-page/', views.secret_page, name='secret_page'),
]
