from django.db.transaction import atomic
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from . import models, serializers
from .utils import mapped_weekday

from django.utils.dateparse import parse_date


@api_view(["POST"])
def add_daily_income(request: Request):
    current_time = timezone.now()
    weekday = mapped_weekday[current_time.weekday()]

    with atomic():
        courier = models.Courier.objects.get(name=request.data["courier"])

        models.CouriersDailyIncome.objects.create(
            courier=courier, income=request.data["income"]
        )

        try:
            persisted_courier = models.CouriersWeeklyIncome.objects.get(
                courier=courier,
                created_at__date__range=(current_time - timezone.timedelta(days=weekday), current_time)
            )
            persisted_courier.income += request.data["income"]
            persisted_courier.save()

        except models.CouriersWeeklyIncome.DoesNotExist:
            models.CouriersWeeklyIncome.objects.create(
                courier=courier, income=request.data["income"], created_at=timezone.now()
            )

    return Response(status=status.HTTP_201_CREATED)


@api_view(["GET"])
def get_weekly_income(request: Request):
    """
    We can add pagination for production
    """
    from_date = parse_date(request.GET["from_date"])
    to_date = parse_date(request.GET["to_date"])

    incomes = models.CouriersWeeklyIncome.objects.filter(
        created_at__date__range=[from_date, to_date]
    ).prefetch_related("courier")

    serializer = serializers.WeeklyIncomeSerializer(incomes, many=True)

    return Response(data=serializer.data)
