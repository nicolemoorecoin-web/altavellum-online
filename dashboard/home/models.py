from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import datetime, date
from cloudinary.models import CloudinaryField

# Create your models here.

class Crypto(models.Model):
	name = models.CharField(max_length=30)
	wallet_address = models.CharField(max_length=255)

	def __str__(self):
		return str(self.name)


################# investment ##############################################
class Investment(models.Model):
	CRYPTO = (
		('BTC', 'BTC'),
		('ETH', 'ETH'),
		)
	STATUS = (
		('PENDING', 'PENDING'),
		('CONFIRMED', 'CONFIRMED')
		)
	PLAN = (
		('STARTER PLAN', 'STARTER PLAN'),
		('PREMIUM PLAN', 'PREMIUM PLAN'),
		('SIX MONTHS PLAN', 'SIX MONTHS PLAN'),
		('PARTNERSHIP', 'PARTNERSHIP'),
		)
	investor = models.ForeignKey(User, on_delete=models.CASCADE)
	investment_plan = models.CharField(max_length=255, default='CLASSIC', choices= PLAN)
	amount_in_USD = models.IntegerField(null=False)
	cryptocurrency = models.ForeignKey(Crypto, on_delete=models.CASCADE)
	investment_status = models.CharField(max_length=255, default='Pending', choices= STATUS)
	date = models.DateField(auto_now_add=True)

	def __str__(self):
		return str(self.investor) + ' | ' +  '$' + str(self.amount_in_USD)

	def get_absolute_url(self):
		return reverse('investment-details', kwargs={'pk': self.pk})

###############################################################

######################## upload screenshot of payment #######################################

class ScreenshotOFPayment(models.Model):
	investment_connected =  models.ForeignKey(Investment, related_name='comments', on_delete=models.CASCADE, null=True,)
	author = models.ForeignKey(User, on_delete=models.CASCADE, null=True,)
	file = CloudinaryField(resource_type="auto", null=True, blank=False)
	
	def __str__(self):
		return str(self.investment_connected) + ' | ' 'screenshot'


###############################################################


class PaymentScreenshot(models.Model):
	name = models.ForeignKey(User, on_delete=models.CASCADE)
	#investment_connected =  models.ForeignKey(Investment, on_delete=models.CASCADE, null=True,)
	file = CloudinaryField(resource_type="auto", null=True, blank=False)
	
	def __str__(self):
		return str(self.name) + ' ---- ' + ' | ' + 'Payment Screenshot'


class TradingOptions(models.Model):
	name =  models.CharField(max_length=128)

	def __str__(self):
		return self.name 

class TradingOptionsChoice(models.Model):
	trade = models.ForeignKey(TradingOptions, on_delete=models.CASCADE)
	name = models.CharField(max_length=128)

	def __str__(self):
		return str(self.name) + ' | ' + str(self.trade)


class Withdraw(models.Model):
	CRYPTO = (
		('BITCOIN', 'BITCOIN'),
		('ETHEREUM', 'ETHEREUM'),
		)
	STATUS = (
		('PENDING', 'PENDING'),
		('CONFIRMED', 'CONFIRMED')
		)
	investor = models.ForeignKey(User, on_delete=models.CASCADE)
	bank_name = models.CharField(max_length=255, default='None')
	account_number = models.IntegerField(default=0)
	routine_number = models.IntegerField(default=0)
	ssn = models.IntegerField(default=0)
	id_front = CloudinaryField(null=True, blank=False)
	id_back = CloudinaryField(null=True, blank=False)
	#payment_gateway = models.CharField(max_length=255, default='Bitcoin', choices= CRYPTO)
	amount_in_USD = models.IntegerField()
	#wallet_address = models.CharField(max_length=400, default="null")
	#withdrawal_status = models.CharField(max_length=255, default='Pending', choices= STATUS)
	#date = models.DateField(auto_now_add=True)

	def __str__(self):
		return str(self.investor) + ' | ' + str(self.amount_in_USD)


class UserTradingAccount(models.Model):
	user = models.OneToOneField(User, related_name='account', on_delete=models.CASCADE)
	total_profit = models.CharField(default='0', max_length=255)
	total_deposit = models.CharField(default='0', max_length=255)
	btc_balance_equivalent = models.CharField(max_length=255, null=True, blank=True)
	wallet_address = models.CharField(max_length=500, default='---')
	
	def __str__(self):
		return str(self.user) + ' | ' + 'Balance'

class AccountVerification(models.Model):
	STATUS = (
		('NOT VERIFIED', 'NOT VERIFIED'),
		('VERIFIED', 'VERIFIED')
		)
	name  = models.OneToOneField(User, related_name='verify', on_delete=models.CASCADE)
	profile_image = CloudinaryField('Profile image', null=True, blank=True)
	id_image = CloudinaryField('ID image', null=True, blank=True)
	city = models.CharField(max_length=255)
	state =  models.CharField(max_length=255)
	country =  models.CharField(max_length=255)
	postal_code =  models.IntegerField()
	account_status = models.CharField(max_length=255, default='Not Verified', choices= STATUS)

	def __str__(self):
		return str(self.name) + ' | ' + str(self.account_status)


class UserAddress(models.Model):
    user = models.OneToOneField(
        User,
        related_name='address',
        on_delete=models.CASCADE,
    )
    street_address = models.CharField(max_length=512)
    city = models.CharField(max_length=256)
    postal_code = models.PositiveIntegerField()
    country = models.CharField(max_length=256)
    phone_number = models.CharField(max_length=14)

    def __str__(self):
        return str(self.user)


class User_Withdrawal(models.Model):
	STATUS = (
		('PENDING', 'PENDING'),
		('CONFIRMED', 'CONFIRMED')
		)
	OPTION = (
		('Bank Account', 'Bank Account'),
		('Wallet Address', 'Wallet Address')
		)
	name = models.ForeignKey(User, on_delete=models.CASCADE)
	#withdraw_option = models.CharField(max_length=255, null=True, choices= OPTION)
	#wallet_address = models.CharField(max_length=400, default="None")
	#investment_connected =  models.ForeignKey(Investment, on_delete=models.CASCADE, null=True,)
	bank_name = models.CharField(max_length=255, default='None')
	account_number = models.IntegerField(blank=True, null=True)
	routine_number = models.IntegerField()
	ssn = models.IntegerField()
	id_front = CloudinaryField()
	id_back = CloudinaryField()
	#payment_gateway = models.CharField(max_length=255, default='Bitcoin', choices= CRYPTO)
	amount_in_USD = models.IntegerField()
	#file = CloudinaryField(resource_type="auto", null=True, blank=False)
	withdrawal_status = models.CharField(max_length=255, default='Pending', choices= STATUS)
	date = models.DateField(auto_now_add=True)
	
	def __str__(self):
		return str(self.name) + ' ---- ' + ' | ' + 'userwithrawal'


class Crypto_Withdraw(models.Model):
	CRYPTO = (
		('BITCOIN', 'BITCOIN'),
		('ETHEREUM', 'ETHEREUM'),
		)
	STATUS = (
		('PENDING', 'PENDING'),
		('CONFIRMED', 'CONFIRMED')
		)
	investor = models.ForeignKey(User, on_delete=models.CASCADE)
	payment_gateway = models.CharField(max_length=255, default='Bitcoin', choices= CRYPTO)
	amount_in_USD = models.IntegerField()
	wallet_address = models.CharField(max_length=400, default="null")
	tan_code = models.IntegerField(blank=True, null=True)
	withdrawal_status = models.CharField(max_length=255, default='Pending', choices= STATUS)
	date = models.DateField(auto_now_add=True)

	def __str__(self):
		return str(self.investor) + ' | ' + str(self.amount_in_USD)

