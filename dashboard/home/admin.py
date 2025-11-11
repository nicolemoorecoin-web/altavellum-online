# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from .models import Investment, Crypto, Withdraw, UserTradingAccount, Crypto_Withdraw, ScreenshotOFPayment, PaymentScreenshot, UserAddress, User_Withdrawal
# Register your models here.

admin.site.register(Crypto)
admin.site.register(Investment)
#admin.site.register(AccountManager)
#admin.site.register(TradingOptions)
#admin.site.register(TradingOptionsChoice)
#admin.site.register(Withdraw)
#admin.site.register(UserTradingAccount)
#admin.site.register(ScreenshotOFPayment)
admin.site.register(PaymentScreenshot)
#.site.register(AccountVerification)
admin.site.register(UserAddress)
admin.site.register(User_Withdrawal)
admin.site.register(Crypto_Withdraw)