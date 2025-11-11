from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import datetime, date
from cloudinary.models import CloudinaryField

# Create your models here.

class UserAccount(models.Model):
	user = models.OneToOneField(User, related_name='accounts', on_delete=models.CASCADE)
	total_profit = models.CharField(default='0.00', max_length=255)
	total_deposit = models.CharField(default='0.00', max_length=255)
	btc_balance_equivalent = models.CharField(max_length=255, null=True, blank=True, default='0.00')
	account_balance = models.CharField(max_length=500, default='0.00')
	
	def __str__(self):
		return str(self.user) + ' | ' + 'Balance'