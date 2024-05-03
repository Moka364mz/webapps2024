import decimal

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from register.models import UserAccounts
import conversion.views
from conversion import convert_currency


class UserRegisterForm(UserCreationForm):
    CURRENCY_CODE = (
        ('GBP', 'GBP'),
        ('USD', 'USD'),
        ('EUR', 'EUR'),
    )

    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    currency = forms.ChoiceField(choices=CURRENCY_CODE)

    class Meta:
        model = User
        fields = (
            "username", "first_name", "last_name", "email", "password1", "password2", "currency",
        )

    def save(self, *args, **kwargs):
        instance = super(UserRegisterForm, self).save(*args, **kwargs)
        baseline = 1000
        currency1 = 'GBP'
        currency2 = self.cleaned_data['currency']
        convert_to_currency = conversion.convert_currency.convert_currency(currency1, currency2, baseline)
        UserAccounts.objects.create(username=instance, balance=convert_to_currency, currency=self.cleaned_data['currency'])
        return instance
