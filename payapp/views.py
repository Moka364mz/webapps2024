from datetime import datetime
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.db.models import Q
from conversion.convert_currency import convert_currency
from payapp.forms import TransferForm, RequestForm, PaymentRequestForm
from payapp.models import Transactions
from register.models import UserAccounts
import requests
import json
import decimal
from django.urls import reverse
import thriftpy2
from thriftpy2.rpc import make_client
from thriftpy2.thrift import TException

timestamp_thrift = thriftpy2.load(
    'timestamp.thrift', module_name='timestamp_thrift')
Timestamp = timestamp_thrift.TimestampService


@login_required
@transaction.atomic
@csrf_protect
def transfer_money_view(request):
    if request.method == "POST":
        form = TransferForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                client = make_client(Timestamp, '127.0.0.1', 9090)
                timestamp = datetime.fromtimestamp(int(str(client.getCurrentTimestamp())))
                sender_account = UserAccounts.objects.select_related().get(username=request.user)
                receiver = form.cleaned_data['receiving_money_from_user']
                receiver_account = UserAccounts.objects.select_related().get(username=receiver)
                amount = form.cleaned_data['amount']
                if amount <= 0:
                    messages.error(request, "Invalid amount: Amount should be greater than zero.")
                    return render(request, "payapp/transfer.html", {"send_money": form})
                elif receiver_account != sender_account:
                    url = request.build_absolute_uri(reverse('conversion', kwargs={'currency1': sender_account.currency,
                                                                                   'currency2': receiver_account.currency,
                                                                                   'amount': amount}))
                    response = requests.get(url, verify=False)
                    if response.status_code == 200:
                        data = json.loads(response.text)
                        converted_amount = decimal.Decimal(data['converted_amount'])
                        if sender_account.balance >= amount:
                            sender_account.balance -= amount
                            receiver_account.balance += converted_amount
                            messages.success(request, f'''
                            Transfer successful. You transferred 
                            {amount}{sender_account.currency} to {receiver}.
                            {receiver} received {converted_amount}{receiver_account.currency}.
                            ''')
                            Transactions(transfering_money_to_user=request.user, receiving_money_from_user=receiver,
                                         amount=amount,
                                         state_of_transaction='Accepted', transaction_date_time=timestamp).save()
                            sender_account.save()
                            receiver_account.save()
                            return redirect('payapp:dashboard')
                        else:
                            messages.error(request,
                                           'Transfer failed. You do not have sufficient funds in your account.')
                            return render(request, "payapp/transfer.html", {"send_money": form})
                    else:
                        messages.error(request, 'Currency conversion API error')
                        return render(request, "payapp/transfer.html", {"send_money": form})
                else:
                    messages.error(request, 'Cannot send money to yourself.')
                    return render(request, "payapp/transfer.html", {"send_money": form})
            except TException as e:
                return HttpResponse("An error occurred: {}".format(str(e)))
        else:
            messages.error(request, "Form is not valid")
            return render(request, "payapp/transfer.html", {"send_money": form})
    else:
        form = TransferForm(user=request.user)
        return render(request, "payapp/transfer.html", {"send_money": form})


@login_required
@csrf_protect
def request_money_view(request):
    if request.method == "POST":
        form = RequestForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                client = make_client(Timestamp, '127.0.0.1', 9090)
                timestamp = datetime.fromtimestamp(int(str(client.getCurrentTimestamp())))
                sender_account = form.cleaned_data['transfering_money_to_user']
                receiver_account = request.user
                amount = form.cleaned_data['amount']
                if amount <= 0:
                    messages.error(request, "Invalid amount: Amount should be greater than zero.")
                    return render(request, "payapp/request.html", {"request_money": form})

                t = Transactions(transfering_money_to_user=sender_account, receiving_money_from_user=receiver_account,
                                 amount=amount, state_of_transaction='Pending',
                                 transaction_date_time=timestamp)
                t.save()

                messages.success(request,
                                 f"Money request has been sent to {sender_account}")  # modified to use sender_account
                return redirect("payapp:dashboard")
            except TException as e:
                return HttpResponse("An error occurred: {}".format(str(e)))
        else:
            messages.error(request, "Request failed")
            return render(request, "payapp/request.html", {"request_money": form})
    else:
        form = RequestForm(user=request.user)
        return render(request, "payapp/request.html", {"request_money": form})


@login_required
@csrf_protect
def dashboard_view(request):
    if request.user.is_authenticated:
        try:
            transaction_list = Transactions.objects.select_related(
                'transfering_money_to_user', 'receiving_money_from_user'
            ).filter(
                Q(transfering_money_to_user=request.user) | Q(receiving_money_from_user=request.user)
            ).order_by('-transaction_date_time')

            for transaction in transaction_list:
                sender_account = UserAccounts.objects.get(username_id=transaction.transfering_money_to_user)
                receiver_account = UserAccounts.objects.get(username_id=transaction.receiving_money_from_user)

                sent_currency = sender_account.currency
                received_currency = receiver_account.currency
                converted_amount = convert_currency(
                    sent_currency, received_currency, transaction.amount
                )

                print(converted_amount)
                transaction.converted_amount = converted_amount
                transaction.sender_currency = sender_account.currency.upper()
                transaction.receiver_currency = receiver_account.currency.upper()

            context = {'transaction_list': transaction_list}
            return render(request, 'payapp/dashboard.html', context)
        except Exception as e:
            print("No transactions to show", e)
            transaction_list = []
            context = {'transaction_list': transaction_list}
            return render(request, 'payapp/dashboard.html', context)

    else:
        return render(request, 'payapp/dashboard.html', {'transaction_list': []})


@login_required
@transaction.atomic
@csrf_protect
def payment_requests_view(request):
    if request.method == 'POST':
        form = PaymentRequestForm(request.POST, user=request.user)
        if form.is_valid():
            transaction_id = form.cleaned_data['transaction_id']
            action = form.cleaned_data['action']

            t = Transactions.objects.select_related().get(pk=transaction_id.id)

            if action == 'Accept':
                sender_account = UserAccounts.objects.select_related().get(username=t.transfering_money_to_user)
                receiver_account = UserAccounts.objects.select_related().get(username=t.receiving_money_from_user)

                if sender_account != receiver_account:
                    url = request.build_absolute_uri(reverse('conversion', kwargs={'currency1': sender_account.currency,
                                                                                   'currency2': receiver_account.currency,
                                                                                   'amount': t.amount}))
                    response = requests.get(url, verify=False)
                    print(f"this is a response",response)
                    if response.status_code == 200:
                        data = json.loads(response.text)
                        converted_amount = decimal.Decimal(data['converted_amount'])
                        requested_amount = decimal.Decimal(data['original_amount'])
                        print(f"this is a response2222")

                        if sender_account.balance >= t.amount:
                            sender_account.balance -= converted_amount
                            sender_account.save()
                            receiver_account.balance += requested_amount
                            receiver_account.save()
                            t.state_of_transaction = 'Accepted'
                            t.save()

                            messages.success(request, f'''
                                Transaction accepted and processed. You transferred 
                                {t.amount}{sender_account.currency} to {t.receiving_money_from_user}.
                                {t.receiving_money_from_user} got {converted_amount}{receiver_account.currency}.
                                ''')
                            return redirect('payapp:paymentrequests')
                        else:
                            messages.error(request,
                                           'Transaction failed. You do not have sufficient funds in your account.')
                            return redirect('payapp:paymentrequests')
                    else:
                        messages.error(request, 'Currency conversion API error')
                        return redirect('payapp:paymentrequests')
                else:
                    messages.error(request, 'Cannot send money yourself.')
                    return redirect('payapp:paymentrequests')

            elif action == 'Reject':
                t.state_of_transaction = 'rejected'
                t.save()
                messages.success(request, 'Transaction rejected.')
                return redirect('payapp:paymentrequests')
            else:
                messages.error(request, 'Invalid action')
                return redirect('payapp:paymentrequests')

        else:
            messages.error(request, 'Transaction processing failed')
            return redirect('payapp:paymentrequests')

    else:

        form = PaymentRequestForm(user=request.user)

        if request.user.is_authenticated:
            pending_transactions = Transactions.objects.select_related().filter(
                Q(transfering_money_to_user=request.user) & Q(state_of_transaction='Pending')
            ).order_by('-transaction_date_time')
        else:
            pending_transactions = []
        return render(request, 'payapp/payment_request.html', {
            'process_pending': form,
            'pending_transactions': pending_transactions
        })
