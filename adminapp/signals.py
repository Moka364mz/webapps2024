import decimal
import logging
from django.db.models.signals import post_migrate
from register.models import User, UserAccounts
from django.dispatch import receiver

logger = logging.getLogger(__name__)

@receiver(post_migrate)
def create_admin_user(sender, **kwargs):
    if sender.name == 'payapp':
        if not User.objects.filter(username='admin1').exists():
            user = User.objects.create_superuser('admin1', 'admin1@example.com', 'admin1')
            UserAccounts.objects.create(username=user, balance=decimal.Decimal('1000.00'), currency='GBP')
        else:
            logger.info("Oops, the user with admin1 username is already exist.")
