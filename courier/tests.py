import pytz
from django.test import TestCase
from django.test import Client
from django.utils import timezone
from unittest.mock import patch, MagicMock
from django.http import HttpResponse
from . import models


class TestCouriersIncome(TestCase):
    def setUp(self) -> None:
        self.courier = models.Courier.objects.create(name="ali")
        self.client = Client()

    def _add_daily_income(self, name: str, income: int) -> HttpResponse:
        res = self.client.post(
            "/couriers/daily_income/",
            {"courier": name, "income": income},
            "application/json",
        )
        return res

    def test_add_daily_income(self):
        res = self._add_daily_income("ali", 2)
        daily_income = models.CouriersDailyIncome.objects.get(courier__name="ali")

        assert res.status_code == 201
        assert daily_income.income == 2

    def test_when_weekly_income_doesnt_exist(self):
        self._add_daily_income("ali", 2)
        daily_income = models.CouriersWeeklyIncome.objects.get(courier__name="ali")

        assert daily_income.income == 2

    @patch("django.utils.timezone.now")
    def test_when_weekly_income_already_exists(self, mocked_now: MagicMock):
        current = timezone.datetime(
            year=2023, month=1, day=27, hour=12, tzinfo=pytz.UTC
        )  # weekday is 7
        mocked_now.return_value = current
        yesterday = current - timezone.timedelta(days=1)
        yesterday_income = 4
        today_income = 2

        models.CouriersWeeklyIncome.objects.create(
            courier=self.courier, income=yesterday_income, created_at=yesterday
        )
        self._add_daily_income("ali", today_income)
        expected_income = yesterday_income + today_income
        real_income = models.CouriersWeeklyIncome.objects.get(
            courier__name="ali"
        ).income

        assert expected_income == real_income
