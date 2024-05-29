from django.contrib import admin
from .models import Customer, MealOff, MealPrice

class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'lunch_category', 'dinner_category', 'plan_days', 'balance']

admin.site.register(Customer, CustomerAdmin)

admin.site.register(MealPrice)

@admin.register(MealOff)
class MealOffAdmin(admin.ModelAdmin):
    list_display = ('customer', 'date', 'lunch_off', 'dinner_off')
