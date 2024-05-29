from django.shortcuts import render, get_object_or_404, redirect
from .models import Customer, MealOff, MealPrice
from .forms import CustomerForm, MealOffForm
from django.utils import timezone
from datetime import time
from django.http import JsonResponse

def meal_off(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    now = timezone.now().time()
    if request.method == 'POST':
        form = MealOffForm(request.POST)
        if form.is_valid():
            meal_off = form.save(commit=False)
            meal_off.customer = customer
            if (meal_off.lunch_off and not meal_off.dinner_off and time(0, 0) <= now <= time(9, 0)) or \
               (meal_off.dinner_off and not meal_off.lunch_off and time(0, 0) <= now <= time(15, 0)) or \
               (meal_off.lunch_off and meal_off.dinner_off and time(0, 0) <= now <= time(9, 0)):
                meal_off.save()
                return redirect('customer_detail', customer_id=customer.id)
            else:
                error_message = "You can only turn off meals during the allowed times."
                return render(request, 'meal_off.html', {'form': form, 'customer': customer, 'error_message': error_message})
    else:
        form = MealOffForm()
    return render(request, 'meal_off.html', {'form': form, 'customer': customer})

def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'customer_list.html', {'customers': customers})

def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, 'customer_form.html', {'form': form})

def customer_update(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customer_list')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'customer_form.html', {'form': form})

def customer_delete(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == 'POST':
        customer.delete()
        return redirect('customer_list')
    return render(request, 'customer_confirm_delete.html', {'customer': customer})

def customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    return render(request, 'customer_detail.html', {'customer': customer})

def admin_panel(request):
    today = timezone.now().date()
    meal_offs = MealOff.objects.filter(date=today)
    customers = Customer.objects.all()

    basic_lunch = sum(1 for c in customers if c.lunch_category == 'Basic' and not any(mo.lunch_off for mo in meal_offs if mo.customer == c))
    premium_lunch = sum(1 for c in customers if c.lunch_category == 'Premium' and not any(mo.lunch_off for mo in meal_offs if mo.customer == c))
    basic_dinner = sum(1 for c in customers if c.dinner_category == 'Basic' and not any(mo.dinner_off for mo in meal_offs if mo.customer == c))
    premium_dinner = sum(1 for c in customers if c.dinner_category == 'Premium' and not any(mo.dinner_off for mo in meal_offs if mo.customer == c))

    context = {
        'basic_lunch': basic_lunch,
        'premium_lunch': premium_lunch,
        'basic_dinner': basic_dinner,
        'premium_dinner': premium_dinner,
    }
    return render(request, 'admin_panel.html', context)

def consume_meal(request, customer_id, meal_type):
    customer = get_object_or_404(Customer, id=customer_id)
    customer.reduce_balance(meal_type)
    return redirect('customer_detail', customer_id=customer.id)


def calculate_balance(request):
    lunch_category = request.GET.get('lunch_category')
    dinner_category = request.GET.get('dinner_category')
    plan_days = request.GET.get('plan_days')

    if not lunch_category or not dinner_category or not plan_days:
        return JsonResponse({'error': 'Missing parameters'}, status=400)

    try:
        plan_days = int(plan_days)
    except ValueError:
        return JsonResponse({'error': 'Invalid plan_days value'}, status=400)

    meal_prices = MealPrice.objects.first()
    if meal_prices is None:
        return JsonResponse({'error': 'Meal prices not found. Please ensure there is at least one MealPrice entry in the database.'}, status=500)

    customer = Customer()
    lunch_cost = customer.get_meal_cost('lunch', lunch_category, meal_prices)
    dinner_cost = customer.get_meal_cost('dinner', dinner_category, meal_prices)

    balance = (plan_days * lunch_cost) + (plan_days * dinner_cost)

    return JsonResponse({'balance': balance})

def consume_meal(request, customer_id, meal_type):
    customer = get_object_or_404(Customer, id=customer_id)
    customer.reduce_balance(meal_type)
    return redirect('customer_detail', customer_id=customer.id)