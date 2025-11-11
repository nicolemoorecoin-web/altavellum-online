# dashboard/app/models.py
from decimal import Decimal
from django.conf import settings
from django.db import models, IntegrityError
from django.utils import timezone
from django.utils.crypto import get_random_string


def make_ref(prefix: str) -> str:
    return f"{prefix}-{get_random_string(8).upper()}"


# statuses you allow to be stored on any Tx
STATUS = [
    ("pending", "Pending"),
    ("processing", "Processing"),
    ("completed", "Completed"),
    ("failed", "Failed"),
    ("rejected", "Rejected"),
]

# what the dashboard should treat as “credited” / “done”
APPROVED_STATUSES = ("approved", "completed", "success", "paid")


class ApprovedOnlyManager(models.Manager):
    """Convenience manager for approved/credited rows only."""
    def get_queryset(self):
        return super().get_queryset().filter(status__in=APPROVED_STATUSES)

    def for_user(self, user):
        return self.get_queryset().filter(user=user)


class BaseTx(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(class)ss",
    )
    reference = models.CharField(
        max_length=32, unique=True, blank=True, editable=False
    )
    amount_usd = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    status = models.CharField(max_length=12, choices=STATUS, default="pending")
    notes = models.TextField(blank=True)

    # Immutable audit time (keep)
    created_at = models.DateTimeField(auto_now_add=True)
    # Business/visible time — editable by staff (we provide a staff form)
    occurred_at = models.DateTimeField(default=timezone.now, db_index=True)

    # default/all rows
    objects = models.Manager()
    # only approved/completed/success/paid rows
    approved = ApprovedOnlyManager()

    class Meta:
        abstract = True
        # Prefer business time in lists; fall back to created_at
        ordering = ("-occurred_at", "-created_at")

    def __str__(self):
        return f"{self.__class__.__name__} {self.reference or '(new)'} (${self.amount_usd})"

    def save(self, *args, **kwargs):
        """
        Normalize status to lowercase, ensure a unique reference, then save.
        Also ensure occurred_at is set for legacy rows.
        """
        # normalize status
        if isinstance(self.status, str):
            s = (self.status or "").strip().lower()
            self.status = s or "pending"
        else:
            self.status = "pending"

        # ensure reference
        if not self.reference:
            gen = getattr(self.__class__, "new_ref", None)
            self.reference = gen() if callable(gen) else make_ref(self.__class__.__name__[:3].upper())

        # ensure occurred_at
        if self.occurred_at is None:
            self.occurred_at = timezone.now()

        # try to avoid rare unique collisions
        for _ in range(2):
            try:
                return super().save(*args, **kwargs)
            except IntegrityError:
                gen = getattr(self.__class__, "new_ref", None)
                self.reference = gen() if callable(gen) else make_ref(self.__class__.__name__[:3].upper())
        return super().save(*args, **kwargs)


class Deposit(BaseTx):
    method = models.CharField(max_length=50, blank=True)   # e.g. "Crypto"
    asset = models.CharField(max_length=50, blank=True)    # e.g. "USDT"
    network = models.CharField(max_length=50, blank=True)  # e.g. "TRC-20"

    @staticmethod
    def new_ref() -> str:
        return make_ref("DEP")


class Withdrawal(BaseTx):
    asset = models.CharField(max_length=50, blank=True)
    network = models.CharField(max_length=50, blank=True)
    address = models.CharField(max_length=120, blank=True)

    @staticmethod
    def new_ref() -> str:
        return make_ref("WDR")


class Investment(BaseTx):
    # amount_usd = principal invested
    plan = models.CharField(max_length=60, blank=True)
    profit_usd = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    @staticmethod
    def new_ref() -> str:
        return make_ref("INV")


class PaymentAddress(models.Model):
    """
    Admin-configured wallet address for a specific asset/network.
    Optional qr_image lets you upload a pre-generated QR code to show on the
    deposit page (we still support on-the-fly QR generation too).
    """
    ASSET_CHOICES = [
        ("BTC", "Bitcoin"),
        ("ETH", "Ethereum"),
        ("USDT", "Tether"),
    ]
    NETWORK_CHOICES = [
        ("Bitcoin", "Bitcoin"),
        ("ERC-20", "ERC-20"),
        ("TRC-20", "TRC-20"),
    ]

    asset = models.CharField(max_length=10, choices=ASSET_CHOICES)
    network = models.CharField(max_length=20, choices=NETWORK_CHOICES, blank=True)
    address = models.CharField(max_length=200, unique=True)
    is_active = models.BooleanField(default=True)
    label = models.CharField(max_length=50, blank=True)

    # optional uploaded QR image for this address
    qr_image = models.ImageField(upload_to="wallet_qr/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("asset", "network"),)
        ordering = ("asset", "network")

    def __str__(self):
        preview = (self.address[:8] + "…") if len(self.address) > 9 else self.address
        net = f" {self.network}" if self.network else ""
        return f"{self.get_asset_display()}{net} • {preview}"
