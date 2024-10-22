from django.shortcuts import render, redirect
from .models import Package, Subscription
from django.contrib.auth.decorators import login_required
from django.conf import settings
import stripe
from django.http import JsonResponse
from datetime import timezone

# import csrf_exempt
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.contrib.auth.models import User


stripe.api_key = settings.STRIPE_SECRET_KEY


def package_list(request):
    packages = Package.objects.all()
    return render(request, "package_list.html", {"packages": packages})


@login_required
def subscribe(request, package_id):
    package = Package.objects.get(id=package_id)
    if request.method == "POST":
        try:
            # Convert the price to cents
            price_in_cents = int(package.ammount * 100)

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": package.title,
                                # 'description': package.description,  # Pass the package description dynamically
                                # 'duration':package.duration
                            },
                            "unit_amount": price_in_cents,  # Pass the price dynamically
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=request.build_absolute_uri("/payment-success/"),
                cancel_url=request.build_absolute_uri("/"),
                metadata={
                    "package_id": package.id,  
                    "user_id": request.user.id
                },
            )
            return redirect(checkout_session.url, code=303)
        except Exception as e:
            return JsonResponse({"error": str(e)})
    return render(request, "subscribe.html", {"package": package})


@login_required
def payment_success(request):

    return render(request, "payment_success.html")


@login_required
def secret_page(request):
    subscription = Subscription.objects.filter(user=request.user).first()
    if subscription and subscription.is_active():
        return render(request, "secret_page.html")
    return redirect("package_list")


@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    event = None

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]  # Get the session object

        user_id = session.get("metadata", {}).get("user_id")
        package_id = session.get("metadata", {}).get("package_id") 
        print('user_id',user_id, 'package_id',package_id)

        try:
            user = User.objects.get(id=user_id)
            print('user ',user)
            # Retrieve package using the package_id from metadata
            package = Package.objects.get(id=package_id)
            print('package', package)

            # Create a new Subscription object and save it in the database
            subscription = Subscription(
                user=user, 
                package=package, 
                
            )

            # Print subscription object details before saving
            print(f"Subscription object: {subscription}")

            subscription.save()

            # Confirm that the subscription has been saved
            print(f"Subscription saved successfully for user {user}")



            
        except User.DoesNotExist:
            print(f"User with email {user} does not exist.")
            return HttpResponse(status=400)
        except Package.DoesNotExist:
            print(f"Package with ID {package_id} does not exist.")
            return HttpResponse(status=400)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return HttpResponse(status=500)

    return HttpResponse(status=200)
