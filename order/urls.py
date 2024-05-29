from django.urls import path
from . import views

urlpatterns = [
    path('customers/create/', views.customer_create, name='customer_create'),
    path('customers/<int:customer_id>/update/', views.customer_update, name='customer_update'),
    path('customers/<int:customer_id>/delete/', views.customer_delete, name='customer_delete'),
    path('meal_off/<int:customer_id>/', views.meal_off, name='meal_off'),
    path('customer/<int:customer_id>/', views.customer_detail, name='customer_detail'),
    path('admin_panel/', views.admin_panel, name='admin_panel'),
    path('calculate_balance/', views.calculate_balance, name='calculate_balance'),
    path('consume_meal/<int:customer_id>/<str:meal_type>/', views.consume_meal, name='consume_meal'),
]

