from django.urls import path
from payapp import views

app_name = 'payapp'

urlpatterns = [
    path('payapp/dashboard', views.dashboard_view, name="dashboard"),
    path('payapp/transfer', views.transfer_money_view, name="transfer"),
    path('payapp/request', views.request_money_view, name='request'),
    path('payapp/payment requests', views.payment_requests_view, name='paymentrequests'),

]
