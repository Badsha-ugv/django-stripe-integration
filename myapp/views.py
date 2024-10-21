# subscriptions/views.py
from django.conf import settings
from django.shortcuts import render, redirect
from .forms import SubscriptionForm
from .models import Subscription
import stripe
from django.http import JsonResponse

stripe.api_key = settings.STRIPE_SECRET_KEY



def create_checkout_session(request):
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Subscription',
                    },
                    'unit_amount': 5000,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri('/payment-success/'),
            cancel_url=request.build_absolute_uri('/payment-cancel/'),
        )
        return JsonResponse({
            'id': checkout_session.id
        })
    except Exception as e:
        return JsonResponse({'error': str(e)})



def subscription_view(request):
    if request.method == "POST":
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            subscription = form.save()  # Save the subscription details
            return redirect("payment", subscription_id=subscription.id)
    else:
        form = SubscriptionForm()
    return render(request, "subscription_form.html", {"form": form})


def payment_view(request, subscription_id):
    subscription = Subscription.objects.get(id=subscription_id)
    if request.method == "POST":
        try:
            # Create Stripe PaymentIntent
            stripe.PaymentIntent.create(
                amount=5000,  # Example amount in cents (e.g., $50)
                currency="usd",
                payment_method=request.POST["stripeToken"],
                confirm=True,
            )
            return redirect("payment_success")
        except stripe.error.StripeError:
            return render(request, "payment_failed.html")
    return render(
        request,
        "payment.html",
        {"stripe_public_key": settings.STRIPE_PUBLIC_KEY, "subscription": subscription},
    )


def payment_success_view(request):
    return render(request, "payment_success.html")
