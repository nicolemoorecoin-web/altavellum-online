# dashboard/home/forms.py

from decimal import Decimal
from django import forms
from django.utils import timezone

# Your existing app models (unchanged)
from .models import (
    Investment,
    Withdraw,
    Crypto_Withdraw,
    ScreenshotOFPayment,
    UserAddress,
    PaymentScreenshot,
    User_Withdrawal,
)
from cloudinary.models import CloudinaryField


# ---------------------------
# Existing forms (unchanged)
# ---------------------------
class DocumentForm(forms.ModelForm):
    # NOTE: Usually you don't redeclare file fields on ModelForm if they already exist on the model.
    # Kept as-is to match your prior code/behavior.
    file = CloudinaryField()

    class Meta:
        model = PaymentScreenshot
        fields = ["file", "name"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "value": "", "id": "elder", "type": "hidden"}
            ),
        }


choice_list = ["basic", "advanced"]


class InvestmentForm(forms.ModelForm):
    class Meta:
        model = Investment
        fields = ("investor", "investment_plan", "amount_in_USD", "cryptocurrency")
        widgets = {
            "investor": forms.TextInput(
                attrs={
                    "class": "form-input peer w-full rounded-full border border-slate-300 bg-transparent px-3 py-2 pl-9 placeholder:text-slate-400/70 hover:border-slate-400 focus:border-primary dark:border-navy-450 dark:hover:border-navy-400 dark:focus:border-accent",
                    "value": "",
                    "id": "elder",
                    "type": "hidden",
                }
            ),
            "investment_plan": forms.Select(
                attrs={
                    "class": "form-input peer w-full rounded-full border border-slate-300 bg-transparent px-3 py-2 pl-9 placeholder:text-slate-400/70 hover:border-slate-400 focus:border-primary dark:border-navy-450 dark:hover:border-navy-400 dark:focus:border-accent"
                }
            ),
            "cryptocurrency": forms.Select(
                attrs={
                    "class": "form-select mt-1.5 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 hover:border-slate-400 focus:border-primary dark:border-navy-450 dark:bg-navy-700 dark:hover:border-navy-400 dark:focus:border-accent"
                }
            ),
            "amount_in_USD": forms.TextInput(
                attrs={
                    "class": "form-input mt-1.5 h-12 w-full rounded-lg border border-slate-300 bg-transparent px-3 py-2 placeholder:text-slate-400/70 hover:border-slate-400 focus:border-primary dark:border-navy-450 dark:hover:border-navy-400 dark:focus:border-accent"
                }
            ),
        }


class WithdrawForm(forms.ModelForm):
    class Meta:
        model = Withdraw
        fields = (
            "investor",
            "id_front",
            "id_back",
            "bank_name",
            "account_number",
            "amount_in_USD",
            "routine_number",
            "ssn",
        )
        widgets = {
            "investor": forms.TextInput(
                attrs={"class": "form-control", "value": "", "id": "elder", "type": "hidden"}
            ),
            "amount_in_USD": forms.TextInput({"class": "form-control"}),
        }


class ScreenShotForm(forms.ModelForm):
    file = CloudinaryField()

    class Meta:
        model = ScreenshotOFPayment
        fields = ["file"]


class AddressForm(forms.ModelForm):
    class Meta:
        model = UserAddress
        fields = ("user", "street_address", "city", "postal_code", "country", "phone_number")
        widgets = {
            "user": forms.TextInput(
                attrs={
                    "class": "form-input peer w-full rounded-lg border border-slate-300 bg-transparent px-3 py-2 pl-9 placeholder:text-slate-400/70 hover:z-10 hover:border-slate-400 focus:z-10 focus:border-primary dark:border-navy-450 dark:hover:border-navy-400 dark:focus:border-accent",
                    "value": "",
                    "id": "elder",
                    "type": "hidden",
                    "placeholder": "",
                }
            ),
            "street_address": forms.TextInput(
                {
                    "class": "form-input peer w-full rounded-lg border border-slate-300 bg-transparent px-3 py-2 pl-9 placeholder:text-slate-400/70 hover:z-10 hover:border-slate-400 focus:z-10 focus:border-primary dark:border-navy-450 dark:hover:border-navy-400 dark:focus:border-accent",
                    "placeholder": "Street Address",
                }
            ),
            "city": forms.TextInput(
                {
                    "class": "form-input peer w-full rounded-lg border border-slate-300 bg-transparent px-3 py-2 pl-9 placeholder:text-slate-400/70 hover:z-10 hover:border-slate-400 focus:z-10 focus:border-primary dark:border-navy-450 dark:hover:border-navy-400 dark:focus:border-accent",
                    "placeholder": "City",
                }
            ),
            "postal_code": forms.TextInput(
                {
                    "class": "form-input peer w-full rounded-lg border border-slate-300 bg-transparent px-3 py-2 pl-9 placeholder:text-slate-400/70 hover:z-10 hover:border-slate-400 focus:z-10 focus:border-primary dark:border-navy-450 dark:hover:border-navy-400 dark:focus:border-accent",
                    "placeholder": "Postal Code",
                }
            ),
            "country": forms.TextInput(
                {
                    "class": "form-input peer w-full rounded-lg border border-slate-300 bg-transparent px-3 py-2 pl-9 placeholder:text-slate-400/70 hover:z-10 hover:border-slate-400 focus:z-10 focus:border-primary dark:border-navy-450 dark:hover:border-navy-400 dark:focus:border-accent",
                    "placeholder": "Country",
                }
            ),
            "phone_number": forms.TextInput(
                {
                    "class": "form-input peer w-full rounded-lg border border-slate-300 bg-transparent px-3 py-2 pl-9 placeholder:text-slate-400/70 hover:z-10 hover:border-slate-400 focus:z-10 focus:border-primary dark:border-navy-450 dark:hover:border-navy-400 dark:focus:border-accent",
                    "placeholder": "Phone Number",
                }
            ),
        }


class WithdrawalForm(forms.ModelForm):
    file = CloudinaryField()

    class Meta:
        model = User_Withdrawal
        fields = [
            "name",
            "bank_name",
            "account_number",
            "amount_in_USD",
            "routine_number",
            "ssn",
            "id_front",
            "id_back",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "value": "", "id": "elder", "type": "hidden"}
            ),
            "bank_name": forms.TextInput(
                {
                    "class": "form-input peer w-full rounded-full border border-slate-300 bg-transparent px-3 py-2 pl-9 placeholder:text-slate-400/70 hover:border-slate-400 focus:border-primary dark:border-navy-450 dark:hover:border-navy-400 dark:focus:border-accent"
                }
            ),
            "account_number": forms.TextInput(
                {
                    "class": "form-input peer w-full rounded-full border border-slate-300 bg-transparent px-3 py-2 pl-9 placeholder:text-slate-400/70 hover:border-slate-400 focus:border-primary dark:border-navy-450 dark:hover:border-navy-400 dark:focus:border-accent"
                }
            ),
            "amount_in_USD": forms.TextInput(
                {
                    "class": "form-input peer w-full rounded-full border border-slate-300 bg-transparent px-3 py-2 pl-9 placeholder:text-slate-400/70 hover:border-slate-400 focus:border-primary dark:border-navy-450 dark:hover:border-navy-400 dark:focus:border-accent"
                }
            ),
            "routine_number": forms.TextInput(
                {
                    "class": "form-input peer w-full rounded-full border border-slate-300 bg-transparent px-3 py-2 pl-9 placeholder:text-slate-400/70 hover:border-slate-400 focus:border-primary dark:border-navy-450 dark:hover:border-navy-400 dark:focus:border-accent"
                }
            ),
            "ssn": forms.TextInput(
                {
                    "class": "form-input peer w-full rounded-full border border-slate-300 bg-transparent px-3 py-2 pl-9 placeholder:text-slate-400/70 hover:border-slate-400 focus:border-primary dark:border-navy-450 dark:hover:border-navy-400 dark:focus:border-accent"
                }
            ),
        }


class CryptoWithdrawalForm(forms.ModelForm):
    class Meta:
        model = Crypto_Withdraw
        fields = ("investor", "payment_gateway", "amount_in_USD", "wallet_address", "tan_code")
        widgets = {
            "investor": forms.TextInput(
                attrs={
                    "class": "form-input peer w-full rounded-full border border-slate-300 bg-transparent px-3 py-2 pl-9 placeholder:text-slate-400/70 hover:border-slate-400 focus:border-primary dark:border-navy-450 dark:hover:border-navy-400 dark:focus:border-accent",
                    "value": "",
                    "id": "elder",
                    "type": "hidden",
                }
            ),
            "amount_in_USD": forms.TextInput(
                {
                    "class": "form-input peer w-full rounded-full border border-slate-300 bg-transparent px-3 py-2 pl-9 placeholder:text-slate-400/70 hover:border-slate-400 focus:border-primary dark:border-navy-450 dark:hover:border-navy-400 dark:focus:border-accent"
                }
            ),
            "payment_gateway": forms.Select(
                attrs={
                    "class": "form-input peer w-full rounded-full border border-slate-300 bg-transparent px-3 py-2 pl-9 placeholder:text-slate-400/70 hover:border-slate-400 focus:border-primary dark:border-navy-450 dark:hover:border-navy-400 dark:focus:border-accent"
                }
            ),
            "wallet_address": forms.TextInput(
                {
                    "class": "form-input peer w-full rounded-full border border-slate-300 bg-transparent px-3 py-2 pl-9 placeholder:text-slate-400/70 hover:border-slate-400 focus:border-primary dark:border-navy-450 dark:hover:border-navy-400 dark:focus:border-accent"
                }
            ),
            "tan_code": forms.TextInput(
                {
                    "class": "form-input peer w-full rounded-full border border-slate-300 bg-transparent px-3 py-2 pl-9 placeholder:text-slate-400/70 hover:border-slate-400 focus:border-primary dark:border-navy-450 dark:hover:border-navy-400 dark:focus:border-accent"
                }
            ),
        }


# ---------------------------------------------------------
# NEW: Two-step crypto withdrawal (request + confirm)
#   (non-model forms so imports are migration-safe)
# ---------------------------------------------------------
CRYPTO_MIN = Decimal("20.00")  # align with your views
ASSET_CHOICES = [("BTC", "BTC"), ("ETH", "ETH"), ("USDT", "USDT")]
NETWORK_CHOICES = [("TRC20", "TRC20"), ("ERC20", "ERC20"), ("BTC", "BTC"), ("", "—")]


class WithdrawalRequestForm(forms.Form):
    """Step 1: user enters crypto withdrawal details (no model dependency)."""
    asset = forms.ChoiceField(choices=ASSET_CHOICES)
    network = forms.ChoiceField(choices=NETWORK_CHOICES, required=False)
    address = forms.CharField(min_length=6, max_length=200)
    amount_usd = forms.DecimalField(min_value=CRYPTO_MIN, max_digits=12, decimal_places=2)
    notes = forms.CharField(required=False, max_length=500)


class WithdrawalConfirmForm(forms.Form):
    """Step 2: user confirms with account password."""
    password = forms.CharField(widget=forms.PasswordInput, label="Account password")


# ---------------------------------------------------------
# NEW: Staff-only datetime edit form for Deposit/Withdrawal/Investment
#   (bind model dynamically in the view)
# ---------------------------------------------------------
class TxTimeFormAdmin(forms.ModelForm):
    occurred_at = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
        input_formats=[
            "%Y-%m-%dT%H:%M",      # HTML datetime-local
            "%Y-%m-%d %H:%M:%S",   # fallbacks
            "%Y-%m-%d %H:%M",
        ],
        required=True,
        help_text="Set the business time of this transaction.",
    )

    def clean_occurred_at(self):
        dt = self.cleaned_data["occurred_at"]
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.get_current_timezone())
        return dt

    class Meta:
        # Model is set dynamically in the view. Only field needed here:
        fields = ("occurred_at",)
