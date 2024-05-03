from django.contrib.auth.models import User
from django.db import models


class Transactions(models.Model):
    STATE_CHOICES = (
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    )

    transfering_money_to_user = models.ForeignKey(User, related_name='transfering_money_to_user', on_delete=models.CASCADE)
    receiving_money_from_user = models.ForeignKey(User, related_name='receiving_money_from_user', on_delete=models.CASCADE)
    state_of_transaction = models.CharField(max_length=10, choices=STATE_CHOICES, default="pending_transaction", null=False)
    transaction_date_time = models.DateTimeField(auto_now_add=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=False)

    def __str__(self):
        details = ''
        details += f'Transaction Date Time   : {self.transaction_date_time}\n'
        details += f'User Sending         : {self.transfering_money_to_user}\n'
        details += f'User Receiving       : {self.receiving_money_from_user}\n'
        details += f'State                : {self.state_of_transaction}\n'
        details += f'Amount of money      : {self.amount}\n'
        return details
