from django.urls import path
from conversion import views

urlpatterns = [
    path('<str:currency1>/<str:currency2>/<amount>/', views.conversion, name='conversion')
]
