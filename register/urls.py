from django.urls import path
from register import views

app_name = 'register'

urlpatterns = [
    path('', views.main_page_view, name="main"),
    path('register/', views.user_register_view, name="register"),
    path('login/', views.user_login_view, name="login"),
    path('logout/', views.user_logout_view, name="logout"),
]
