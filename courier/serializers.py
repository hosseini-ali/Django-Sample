from . import models
from rest_framework.serializers import ModelSerializer


class CourierSerializer(ModelSerializer):
    class Meta:
        model = models.Courier
        fields = (
            "id",
            "name",
        )


class WeeklyIncomeSerializer(ModelSerializer):
    courier = CourierSerializer(read_only=True)

    class Meta:
        model = models.CouriersWeeklyIncome
        fields = ("income", "created_at", "courier")
