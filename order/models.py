from django.db import models
from django.utils import timezone
import datetime
class MealPrice(models.Model):
    basic_lunch_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    premium_lunch_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    basic_dinner_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    premium_dinner_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return "Meal Prices"

class Customer(models.Model):
    BASIC = 'Basic'
    PREMIUM = 'Premium'
    CATEGORY_CHOICES = [
        (BASIC, 'Basic'),
        (PREMIUM, 'Premium'),
    ]

    PACKAGE_3_DAYS = 3
    PACKAGE_7_DAYS = 7
    PACKAGE_15_DAYS = 15
    PACKAGE_30_DAYS = 30
    PLAN_CHOICES = [
        (PACKAGE_3_DAYS, '3 Days'),
        (PACKAGE_7_DAYS, '7 Days'),
        (PACKAGE_15_DAYS, '15 Days'),
        (PACKAGE_30_DAYS, '30 Days'),
    ]

    name = models.CharField(max_length=100)
    lunch_category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    dinner_category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    plan_days = models.IntegerField(choices=PLAN_CHOICES)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    meals_consumed = models.IntegerField(default=0)

    def get_meal_cost(self, meal_type, category, meal_prices):
        if meal_prices is None:
            raise ValueError("Meal prices not found. Please ensure there is at least one MealPrice entry in the database.")
        if meal_type == 'lunch':
            return meal_prices.premium_lunch_price if category == 'Premium' else meal_prices.basic_lunch_price
        elif meal_type == 'dinner':
            return meal_prices.premium_dinner_price if category == 'Premium' else meal_prices.basic_dinner_price

    def calculate_balance(self):
        meal_prices = MealPrice.objects.first()
        if meal_prices is None:
            raise ValueError("Meal prices not found. Please ensure there is at least one MealPrice entry in the database.")
        lunch_cost = self.get_meal_cost('lunch', self.lunch_category, meal_prices)
        dinner_cost = self.get_meal_cost('dinner', self.dinner_category, meal_prices)
        balance = (self.plan_days * lunch_cost) + (self.plan_days * dinner_cost)
        return balance

    def save(self, *args, **kwargs):
        if not self.pk:  # Check if it's a new instance
            # Calculate the initial balance based on the meal plan
            meal_prices = MealPrice.objects.first()
            if meal_prices is None:
                raise ValueError("Meal prices not found. Please ensure there is at least one MealPrice entry in the database.")
            
            lunch_cost = self.get_meal_cost('lunch', self.lunch_category, meal_prices)
            dinner_cost = self.get_meal_cost('dinner', self.dinner_category, meal_prices)
            self.balance = (self.plan_days * lunch_cost) + (self.plan_days * dinner_cost)

        super(Customer, self).save(*args, **kwargs)

    def reduce_balance(self, meal_type):
        # Update balance only if the customer has subscribed
        if self.pk:
            meal_prices = MealPrice.objects.first()
            if meal_prices is None:
                raise ValueError("Meal prices not found. Please ensure there is at least one MealPrice entry in the database.")

            if meal_type == 'lunch':
                cost = self.get_meal_cost('lunch', self.lunch_category, meal_prices)
            elif meal_type == 'dinner':
                cost = self.get_meal_cost('dinner', self.dinner_category, meal_prices)
            elif meal_type == 'both':
                cost = self.get_meal_cost('lunch', self.lunch_category, meal_prices) + \
                       self.get_meal_cost('dinner', self.dinner_category, meal_prices)
            else:
                cost = 0
            
            self.balance -= cost
            self.meals_consumed += 1
            self.save()

class MealOff(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    lunch_off = models.BooleanField(default=False)
    dinner_off = models.BooleanField(default=False)
    
    def can_turn_off_meal(self, meal_type):
        now = timezone.now().time()
        if meal_type == 'lunch':
            return datetime.time(0, 0) <= now <= datetime.time(9, 0)
        elif meal_type == 'dinner':
            return datetime.time(0, 0) <= now <= datetime.time(15, 0)
        elif meal_type == 'both':
            return datetime.time(0, 0) <= now <= datetime.time(9, 0)
        return False