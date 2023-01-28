import pytz
from django.utils import timezone
from unittest.mock import patch, MagicMock
from django.http import HttpResponse
from rest_framework.test import APITestCase
from rest_framework import status
from . import models


class TestCouriersIncome(APITestCase):
    def setUp(self) -> None:
        self.courier = models.Courier.objects.create(name="ali")

    def _add_daily_income(self, name: str, income: int) -> HttpResponse:
        res = self.client.post(
            "/couriers/daily_income/",
            {"courier": name, "income": income},
            format="json",
        )
        return res

    def test_add_daily_income(self):
        res = self._add_daily_income(self.courier.name, 2)
        self.assertEqual(status.HTTP_201_CREATED, res.status_code)

        daily_income = models.CouriersDailyIncome.objects.get(courier=self.courier)
        self.assertEqual(daily_income.income, 2)

    @patch("django.utils.timezone.now")
    def test_add_when_weekly_income_already_exists_in_current_week(
        self, mocked_now: MagicMock
    ):
        current_date = timezone.datetime(
            year=2023, month=1, day=27, hour=12, tzinfo=pytz.UTC
        )  # weekday is 7
        mocked_now.return_value = current_date
        yesterday_date = current_date - timezone.timedelta(days=1)
        yesterday_income = 4
        today_income = 2

        models.CouriersWeeklyIncome.objects.create(
            courier=self.courier, income=yesterday_income, created_at=yesterday_date
        )
        self._add_daily_income(self.courier.name, today_income)
        real_income = models.CouriersWeeklyIncome.objects.filter(courier=self.courier)

        expected_income = yesterday_income + today_income
        assert real_income.count() == 1
        assert expected_income == real_income.first().income

    @patch("django.utils.timezone.now")
    def test_add_when_weekly_income_already_exists_out_of_week(
        self, mocked_now: MagicMock
    ):
        current_date = timezone.datetime(
            year=2023, month=1, day=27, hour=12, tzinfo=pytz.UTC
        )  # weekday is 7
        mocked_now.return_value = current_date
        last_week_date = current_date - timezone.timedelta(days=8)
        last_week_income = 4
        today_income = 2
        models.CouriersWeeklyIncome.objects.create(
            courier=self.courier, income=last_week_income, created_at=last_week_date
        )
        self._add_daily_income(self.courier.name, today_income)
        weekly_incomes = models.CouriersWeeklyIncome.objects.filter(courier=self.courier)

        assert weekly_incomes.count() == 2

    @patch("django.utils.timezone.now")
    def test_weekly_incomes(self, mocked_now: MagicMock):
        mocked_now.return_value = timezone.datetime(year=2023, month=1, day=27, hour=12, tzinfo=pytz.UTC)

        from_date = timezone.now() - timezone.timedelta(days=5)
        to_date = timezone.now()

        self._add_daily_income(self.courier.name, 1000)
        self._add_daily_income(self.courier.name, 1000)

        res = self.client.get(
            "/incomes/weekly/?from_date=%d-%d-%d&to_date=%d-%d-%d"
            % (
                from_date.year,
                from_date.month,
                from_date.day,
                to_date.year,
                to_date.month,
                to_date.day,
            ),
            format="json",
        )

        self.assertEqual(200, res.status_code)

        json = res.json()
        self.assertEqual(1, len(json))

        self.assertEqual(json[0]["courier"]["name"], self.courier.name)
        self.assertEqual(json[0]["income"], 2000)
