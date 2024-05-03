import decimal

from django.http import JsonResponse
from .convert_currency import convert_currency, rates as exchange_rates


def conversion(request,currency1, currency2, amount):
    try:
        amount_decimal = decimal.Decimal(amount)
        if amount_decimal <= 0:
            return JsonResponse({'error': 'Amount must be greater than zero'}, status=400)
    except decimal.InvalidOperation:
        return JsonResponse({'error': 'Could not convert amount to a decimal number'}, status=400)

    try:
        exchange_rate = exchange_rates[currency1][currency2]
    except KeyError:
        return JsonResponse({'error': 'One or both of the provided currencies are not supported'}, status=400)

    try:
        converted_amount = convert_currency(currency1, currency2, amount_decimal)
        return JsonResponse({
            'conversion_rate': exchange_rate,
            'converted_amount': converted_amount,
            'original_amount': amount_decimal
        })
    except Exception as e:
        return JsonResponse({'error': f'An error occurred during conversion: {str(e)}'}, status=500)