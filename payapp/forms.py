from django import forms
from django.forms import ModelChoiceField
from payapp.models import Transactions
from django.contrib.auth.models import User


class TransferForm(forms.ModelForm):
    class Meta:
        model = Transactions
        fields = ('receiving_money_from_user', 'amount')

    def __init__(self, *args, user=None, **kwargs):
        super(TransferForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['receiving_money_from_user'].queryset = self.fields['receiving_money_from_user'].queryset.exclude(pk=user.pk)
        self.fields['receiving_money_from_user'].label = "Transfer money to"



class RequestForm(forms.ModelForm):
    class Meta:
        model = Transactions
        fields = ('transfering_money_to_user', 'amount')

    def __init__(self, *args, user=None, **kwargs):
        super(RequestForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['transfering_money_to_user'].queryset = self.fields['transfering_money_to_user'].queryset.exclude(pk=user.pk)
        self.fields['transfering_money_to_user'].label = "Request money from"



class TransactionModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return f"ID: {obj.id}, Amount: {obj.amount}, To: {obj.receiving_money_from_user}"



class PaymentRequestForm(forms.Form):
    ACCEPT_OR_REJECT_CHOICES = (
        ('Accept', 'Accept'),
        ('Reject', 'Reject'),
    )

    action = forms.ChoiceField(choices=ACCEPT_OR_REJECT_CHOICES)
    transaction_id = TransactionModelChoiceField(queryset=Transactions.objects.all())

    class Meta:
        model = Transactions
        fields = ('transaction_id', 'action')

    def __init__(self, *args, user=None, **kwargs):
        super(PaymentRequestForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['transaction_id'].queryset = Transactions.objects.filter(transfering_money_to_user=user, state_of_transaction='Pending')

        self.fields['transaction_id'].label = "Transaction ID"
