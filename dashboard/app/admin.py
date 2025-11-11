# dashboard/app/admin.py
from django.contrib import admin
from django import forms
from django.utils import timezone
from django.utils.html import format_html

from .models import Deposit, Withdrawal, Investment, PaymentAddress

# ---------- Common admin form with a pseudo datetime editor ----------
class CreatedAtEditForm(forms.ModelForm):
    """
    Adds a non-model field 'created_at_edit' so staff can adjust the visible time.
    """
    created_at_edit = forms.DateTimeField(
        required=False,
        label="Created at (override)",
        help_text="Optional: set a specific date & time for this record.",
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "vDateTimeInput form-control"}
        ),
        input_formats=[
            "%Y-%m-%dT%H:%M",      # HTML datetime-local
            "%Y-%m-%d %H:%M:%S",   # fallback
            "%Y-%m-%d %H:%M",
        ],
    )

    class Meta:
        fields = "__all__"  # model fields + our extra pseudo-field


class BaseTxAdmin(admin.ModelAdmin):
    """
    Base options shared by Deposit / Withdrawal / Investment.
    Uses created_at everywhere (safe; always exists).
    """
    form = CreatedAtEditForm

    list_display        = ("reference", "user", "amount_usd", "status", "created_at")
    list_filter         = ("status",)  # keep simple; no non-field names here
    search_fields       = ("reference", "user__username", "notes")
    ordering            = ("-created_at",)
    date_hierarchy      = "created_at"
    list_select_related = ("user",)
    readonly_fields     = ("reference", "created_at")

    # Quick status actions
    def _mark_status(self, value):
        def action(modeladmin, request, queryset):
            queryset.update(status=value)
        action.__name__ = f"mark_{value}"
        action.short_description = f"Mark selected as {value}"
        return action

    def get_actions(self, request):
        actions = super().get_actions(request)
        for v in ("approved", "completed", "pending", "failed",
                  "rejected", "processing", "success", "paid"):
            actions[f"mark_{v}"] = (self._mark_status(v), f"mark_{v}", f"Mark selected as {v}")
        return actions

    # Add our pseudo-field to the form layout.
    def get_fieldsets(self, request, obj=None):
        base_fields = [f.name for f in obj._meta.fields] if obj else []
        main = [f for f in base_fields if f != "id"]
        if "created_at" not in main:
            main.append("created_at")
        main.append("created_at_edit")
        return ((None, {"fields": tuple(main)}),)

    # When saving, apply the override if provided.
    def save_model(self, request, obj, form, change):
        dt = form.cleaned_data.get("created_at_edit")
        if dt:
            if timezone.is_naive(dt):
                dt = timezone.make_aware(dt, timezone.get_current_timezone())
            obj.created_at = dt
        super().save_model(request, obj, form, change)


# ---------------- Deposit ----------------
@admin.register(Deposit)
class DepositAdmin(BaseTxAdmin):
    list_display = ("reference", "user", "method", "asset", "amount_usd", "status", "created_at")
    list_filter  = ("status", "method", "asset")


# ---------------- Withdrawal ----------------
@admin.register(Withdrawal)
class WithdrawalAdmin(BaseTxAdmin):
    list_display = ("reference", "user", "asset", "amount_usd", "status", "created_at")
    list_filter  = ("status", "asset")


# ---------------- Investment ----------------
@admin.register(Investment)
class InvestmentAdmin(BaseTxAdmin):
    list_display = ("reference", "user", "plan", "amount_usd", "profit_usd", "status", "created_at")
    list_filter  = ("status", "plan")


# ---------------- Payment addresses ----------------
@admin.register(PaymentAddress)
class PaymentAddressAdmin(admin.ModelAdmin):
    list_display    = ("asset", "network", "short_address", "is_active", "updated_at", "qr_preview")
    list_filter     = ("asset", "network", "is_active")
    search_fields   = ("address", "label")
    ordering        = ("asset", "network")
    fields          = ("asset", "network", "address", "label", "is_active", "qr_image", "qr_preview")
    readonly_fields = ("qr_preview",)

    def short_address(self, obj):
        s = obj.address or ""
        return (s[:10] + "…") if len(s) > 12 else s
    short_address.short_description = "Address"

    def qr_preview(self, obj):
        if getattr(obj, "qr_image", None):
            try:
                return format_html(
                    '<img src="{}" style="height:120px;width:120px;object-fit:contain;border-radius:8px;border:1px solid #ddd;" />',
                    obj.qr_image.url,
                )
            except Exception:
                return "—"
        return "—"
    qr_preview.short_description = "QR"
