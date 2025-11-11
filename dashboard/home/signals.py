from .models import UserTradingAccount
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def post_save_create_account(sender, instance, created, *args, **kwargs):
    if created:
        UserTradingAccount.objects.create(user=instance)