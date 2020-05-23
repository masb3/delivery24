from django.contrib import admin
#from django.contrib.auth.models import User
from core.models import Work, Order


@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    pass


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Order._meta.fields]
