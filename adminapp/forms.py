from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from register.models import UserAccounts
import conversion.views
from conversion import convert_currency

class AdminRegisterForm(UserCreationForm):
    CURRENCY_CHOICES = (
        ('GBP', 'GBP'),
        ('USD', 'USD'),
        ('EUR', 'EUR'),
    )

    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    currency = forms.ChoiceField(choices=CURRENCY_CHOICES)
    #Designates whether the user can log into this admin site
    is_staff = forms.BooleanField(initial=True, disabled=True)
    #Designates that this user has all permissions without explicitly assigning them
    is_superuser = forms.BooleanField(initial=True, disabled=True)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2",
                  "currency", 'is_staff', 'is_superuser')

    def save(self, *args, **kwargs):
        instance = super(AdminRegisterForm, self).save(*args, **kwargs)
        baseline = 1000
        currency1 = 'GBP'
        currency2 = self.cleaned_data['currency']
        convert_to_currency = conversion.convert_currency.convert_currency(currency1, currency2, baseline)
        UserAccounts.objects.create(username=instance, balance=convert_to_currency, currency=self.cleaned_data['currency'])
        return instance
