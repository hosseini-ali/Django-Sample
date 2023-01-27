from django.contrib import admin
from .models import Courier


@admin.register(Courier)
class CourierAdmin(admin.ModelAdmin):
    pass
