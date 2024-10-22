from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Package(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    duration = models.IntegerField()  # Duration in days
    ammount = models.DecimalField(decimal_places=2, max_digits=10, default=0)


    def __str__(self):
        return self.title

class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateTimeField(blank=True, null=True)
    @property
    def end_date(self):
        return self.start_date + timedelta(days=self.package.duration)

    def is_active(self):
        return timezone.now().date() <= self.end_date

