from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from register.forms import UserRegisterForm


@csrf_protect
def user_register_view(request):
    if request.method == "POST":
        userregisterform = UserRegisterForm(request.POST)
        if userregisterform.is_valid():
            userregisterform.save()
            messages.success(request, "Registration successful")
            return redirect("register:login")
        else:
            messages.error(request, "Unsuccessful registration. Invalid information.")
            return render(request, "register/register.html", {"user_register": userregisterform})
    else:
        if request.user.is_authenticated:
            messages.success(request, "You are already registrated")
            return redirect("payapp:dashboard")
        else:
            userregisterform = UserRegisterForm()
            return render(request, "register/register.html", {"user_register": userregisterform})


@csrf_protect
def user_login_view(request):
    if request.user.is_authenticated:
        return redirect("payapp:dashboard")
    if request.method == "POST":
        authform = AuthenticationForm(request, request.POST)
        if authform.is_valid():
            username = authform.cleaned_data['username']
            password = authform.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"Welcome {username}.")
                return redirect("payapp:dashboard")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        authform = AuthenticationForm()
    return render(request, "register/login.html", {"user_login": authform})


@csrf_protect
def user_logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out")
    return redirect("register:main")


@csrf_protect
def main_page_view(request):
    return render(request, "register/main.html")
