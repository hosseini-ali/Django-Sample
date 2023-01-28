from django.contrib import admin
from django.urls import path
from courier import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("couriers/daily_income/", views.add_daily_income),
    path("incomes/weekly/", views.get_weekly_income),
]
