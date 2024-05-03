from django.contrib.auth.models import User
from django.db import models


class UserAccounts(models.Model):
    CURRENCY_CODE = (
        ('USD', 'USD'),
        ('GBP', 'GBP'),
        ('EUR', 'EUR'),
    )
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=1000)
    currency = models.CharField(max_length=3, choices=CURRENCY_CODE, null=False)

    def __str__(self):
        return (
            f"Username   : {self.username}\n"
            f"Balance    : {self.balance}\n"
            f"Currency   : {self.currency}"
        )



