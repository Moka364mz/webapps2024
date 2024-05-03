from django.db import models

class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=100)
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.code
