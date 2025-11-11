from django.contrib import admin
from .models import Investment, Contact, Profit, WalletAddress
from .models_otp import LoginOTP



@admin.action(description="Mark selected Investments as Active")
def mark_active(modeladmin, request, queryset):
    queryset.update(status="active")


@admin.action(description="Mark selected Investments as Closed")
def mark_closed(modeladmin, request, queryset):
    queryset.update(status="closed")


class ProfitInline(admin.TabularInline):
    model = Profit
    extra = 0
    fields = ("amount", "note", "is_approved", "created_at")
    readonly_fields = ("created_at",)
    show_change_link = True


@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "amount", "status", "created_at")
    list_filter = ("plan", "status")
    search_fields = ("user__username", "user__email")
    actions = [mark_active, mark_closed]
    inlines = [ProfitInline]


@admin.action(description="Approve selected profits")
def approve_profits(modeladmin, request, queryset):
    queryset.update(is_approved=True)


@admin.action(description="Unapprove selected profits")
def unapprove_profits(modeladmin, request, queryset):
    queryset.update(is_approved=False)


@admin.register(Profit)
class ProfitAdmin(admin.ModelAdmin):
    list_display = ("user", "investment", "amount", "is_approved", "created_at")
    list_filter = ("is_approved",)
    search_fields = ("user__username", "user__email", "note")
    actions = [approve_profits, unapprove_profits]


@admin.register(WalletAddress)
class WalletAddressAdmin(admin.ModelAdmin):
    list_display = ("asset", "network", "address", "is_active", "updated_at")
    list_filter = ("asset", "network", "is_active")
    search_fields = ("address",)
    save_on_top = True

@admin.register(LoginOTP)
class LoginOTPAdmin(admin.ModelAdmin):
    list_display = ("user", "code", "created_at", "expires_at", "attempts", "is_used")
    search_fields = ("user__username", "code")

admin.site.register(Contact)
