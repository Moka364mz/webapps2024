from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from payapp.models import Transactions, User
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import AdminRegisterForm
from django.contrib import messages
from register.models import UserAccounts, User


@staff_member_required
@login_required
def admin_accounts(request):
    accounts = UserAccounts.objects.all()
    return render(request, 'admin_register/admin_accounts.html', {'accounts': accounts})


def is_superuser(user):
    return user.is_authenticated and user.is_superuser


@staff_member_required
@login_required
def admin_transactions_view(request):
    transaction_list = Transactions.objects.all()
    return render(request, 'register/dashboard.html', {'transaction_list': transaction_list})


@staff_member_required
@login_required
def admin_view(request):
    if not request.user.is_superuser:
        messages.error(request, "Unauthorized access.")
        return redirect('home')  # Redirect to a safe home page URL

    transaction_list = Transactions.objects.all().order_by('-transaction_date_time')[:10]  # Adjust as necessary
    user_list = UserAccounts.objects.all()  # You may want to filter or paginate this

    context = {'transaction_list': transaction_list, 'user_list': user_list, }
    return render(request, 'adminapp/admin.html', context)


@login_required
@user_passes_test(is_superuser)
def admin_register(request):
    if request.method == 'POST':
        form = AdminRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_registration:admin_view')
    else:
        form = AdminRegisterForm()
    return render(request, 'adminapp/admin_register.html', {'form': form})
