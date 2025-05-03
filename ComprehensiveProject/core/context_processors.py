
from django.conf import settings

def paypal_settings(request):
    return {
        'PAYPAL_DONATE_BUSINESS_EMAIL': settings.PAYPAL_DONATE_BUSINESS_EMAIL,
        'PAYPAL_DONATE_CURRENCY':       settings.PAYPAL_DONATE_CURRENCY,
    }
