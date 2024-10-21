# subscriptions/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("subscribe/", views.subscription_view, name="subscribe"),
    path("payment/<int:subscription_id>/", views.payment_view, name="payment"),
    path("payment-success/", views.payment_success_view, name="payment_success"),
    path('checkout-session/',views.create_checkout_session,name="checkout_session"),
]
