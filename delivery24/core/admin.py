from django.contrib import admin
from django.contrib.auth.models import User
from core.models import Driver, Work, Order


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    #TODO: replace with custom auth
    list_display = ('name',)


@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    pass


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Order._meta.fields]
