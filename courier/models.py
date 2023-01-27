from django.db import models
from django.utils import timezone


class Courier(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class CouriersDailyIncome(models.Model):
    courier = models.ForeignKey(Courier, on_delete=models.CASCADE)
    income = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)


class CouriersWeeklyIncome(models.Model):
    courier = models.ForeignKey(Courier, on_delete=models.CASCADE)
    income = models.BigIntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    last_update_at = models.DateTimeField(default=timezone.now)
