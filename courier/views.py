from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from . import models
from .utils import mapped_weekday


@api_view(["POST"])
def add_daily_income(request: Request):
    courier = models.Courier.objects.get(name=request.data["courier"])
    models.CouriersDailyIncome.objects.create(
        courier=courier, income=request.data["income"]
    )

    try:
        current_time = timezone.now()
        weekday = mapped_weekday[current_time.weekday()]

        persisted_courier = models.CouriersWeeklyIncome.objects.get(
            courier=courier,
            created_at__year=current_time.year,
            created_at__day__gte=current_time.day - weekday,
            created_at__day__lte=current_time.day,
        )
        persisted_courier.income += request.data["income"]
        persisted_courier.save()

    except models.CouriersWeeklyIncome.DoesNotExist:
        models.CouriersWeeklyIncome.objects.create(
            courier=courier, income=request.data["income"]
        )

    return Response(status=status.HTTP_201_CREATED)
