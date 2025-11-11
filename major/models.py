# major/models.py
from django.conf import settings
from django.db import models


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=100)
    message = models.TextField()

    def __str__(self) -> str:
        return self.name


class Investment(models.Model):
    PLAN_CHOICES = [
        ("starter", "Starter"),
        ("premium", "Premium"),
        ("business", "Business"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="major_investments",
    )
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, default="pending")  # pending/active/closed
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.user} - {self.plan} - {self.amount}"


class Profit(models.Model):
    """
    Admin-posted profits that roll up into a user's dashboard.
    Mark `is_approved=True` for it to count toward Total Profit.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="major_profits",
    )
    investment = models.ForeignKey(
        Investment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="profits",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    note = models.CharField(max_length=255, blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        state = "approved" if self.is_approved else "pending"
        return f"Profit {self.amount} for {self.user} ({state})"


class WalletAddress(models.Model):
    ASSET_CHOICES = [
        ("BTC", "Bitcoin"),
        ("ETH", "Ethereum"),
        ("USDT", "Tether"),
    ]

    asset = models.CharField(max_length=10, choices=ASSET_CHOICES)
    network = models.CharField(max_length=20, blank=True)  # e.g. ERC-20, TRC-20
    address = models.CharField(max_length=200)

    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("asset", "network")
        ordering = ("asset", "network")
        verbose_name = "Wallet address"
        verbose_name_plural = "Wallet addresses"

    def __str__(self) -> str:
        net = f" {self.network}" if self.network else ""
        preview = (self.address[:10] + "…") if len(self.address) > 11 else self.address
        return f"{self.asset}{net} — {preview}"
