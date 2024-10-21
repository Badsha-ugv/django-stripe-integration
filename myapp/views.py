from django.shortcuts import render, redirect
from .models import Package, Subscription
from django.contrib.auth.decorators import login_required
from django.conf import settings
import stripe
from django.http import JsonResponse
from datetime import timezone


stripe.api_key = settings.STRIPE_SECRET_KEY

def package_list(request):
    packages = Package.objects.all()
    return render(request, 'package_list.html', {'packages': packages})

# @login_required
# def subscribe(request, package_id):
#     package = Package.objects.get(id=package_id)
#     if request.method == 'POST':
#         checkout_session = stripe.checkout.Session.create(
#             payment_method_types=['card'],
#             line_items=[{
#                 'price_data': {
#                     'currency': 'usd',
#                     'product_data': {'name': package.title},
#                     'unit_amount': 1000,  # Example amount in cents
#                 },
#                 'quantity': 1,
#             }],
#             mode='payment',
#             success_url=request.build_absolute_uri('/payment-success/'),
#             cancel_url=request.build_absolute_uri('/'),
#         )
#         return redirect(checkout_session.url, code=303)
#     return render(request, 'subscribe.html', {'package': package})

@login_required
def subscribe(request, package_id):
    package = Package.objects.get(id=package_id)
    if request.method == 'POST':
        try:
            # Convert the price to cents
            price_in_cents = int(package.ammount * 100)
            
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': package.title,
                        },
                        'unit_amount': price_in_cents,  # Pass the price dynamically
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri('/payment-success/'),
                cancel_url=request.build_absolute_uri('/'),
            )
            return redirect(checkout_session.url, code=303)
        except Exception as e:
            return JsonResponse({'error': str(e)})
    return render(request, 'subscribe.html', {'package': package})


@login_required
def payment_success(request):
    # Retrieve the current package that was subscribed to
    package_id = request.session.get('package_id')
    if package_id:
        package = Package.objects.get(id=package_id)
        # Create the subscription for the user
        subscription = Subscription.objects.create(
            user=request.user,
            package=package,
            start_date=timezone.now()  # Set the start date to the current date
        )
        subscription.save()

    return render(request, 'payment_success.html')

@login_required
def secret_page(request):
    subscription = Subscription.objects.filter(user=request.user).first()
    if subscription and subscription.is_active():
        return render(request, 'secret_page.html')
    return redirect('package_list')
