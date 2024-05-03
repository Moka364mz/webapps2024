from decimal import Decimal

rates = {
    'USD': {
        'EUR': Decimal('0.93'),
        'GBP': Decimal('0.80'),
        'USD': Decimal('1.0'),
    },
    'EUR': {
        'USD': Decimal('1.07'),
        'GBP': Decimal('0.86'),
        'EUR': Decimal('1.0'),
    },
    'GBP': {
        'USD': Decimal('1.24'),
        'EUR': Decimal('1.16'),
        'GBP': Decimal('1.0'),
    }
}


def convert_currency(currency1, currency2, amount):
    if currency1 not in rates or currency2 not in rates[currency1]:
        return None

    rate = rates[currency1][currency2]
    converted_amount = round(rate * amount, 2)

    return converted_amount
