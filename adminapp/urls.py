from django.urls import path
from adminapp import views

app_name = 'admin_registration'

urlpatterns = [
    path('admin_accounts/', views.admin_accounts, name='admin_accounts'),
    path('transactions/', views.admin_transactions_view, name='admin_transactions_view'),
    path('adminview/', views.admin_view, name='admin_view'),
    path('adminregister/', views.admin_register, name='admin_register'),

]