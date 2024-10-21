from django.contrib import admin

# Register your models here.
from .models import Package,Subscription

admin.site.register(Package)
admin.site.register(Subscription)
