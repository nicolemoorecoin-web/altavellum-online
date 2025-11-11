# dashboard/home/views.py
from decimal import Decimal, InvalidOperation
from collections import defaultdict
import json
from types import SimpleNamespace

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import localtime
from django.views.decorators.http import require_http_methods

from dashboard.app.models import Deposit, Withdrawal, Investment, PaymentAddress
from .forms import WithdrawalRequestForm, WithdrawalConfirmForm, TxTimeFormAdmin

# ----------------- Constants -----------------
APPROVED = ("approved", "completed", "success", "paid")
ASSET_NAME  = {"BTC": "Bitcoin", "ETH": "Ethereum", "USDT": "Tether"}
ASSET_COLOR = {"BTC": "#D08B2F", "ETH": "#3862F5", "USDT": "#1FA386"}
CRYPTO_MIN = Decimal("20.00")
BANK_MIN   = Decimal("5000.00")
ALLOWED_ASSETS  = {"BTC", "ETH", "USDT"}
ALLOWED_NETWORK = {"TRC20", "ERC20", "BTC", ""}
PENDING_SESSION_KEY = "pending_withdrawal"





# ----------------- Helpers -----------------
def _sum(qs, field):
    return qs.aggregate(s=Sum(field))["s"] or Decimal("0.00")

def _norm_asset(val: str) -> str:
    s = (val or "").strip().upper()
    if s.startswith("BTC"): return "BTC"
    if s.startswith("ETH"): return "ETH"
    if "USDT" in s or "TETHER" in s: return "USDT"
    return s or "USDT"

def _parse_amount(s: str) -> Decimal:
    try:
        return Decimal((s or "0").strip()).quantize(Decimal("0.01"))
    except (InvalidOperation, AttributeError):
        return Decimal("0.00")

def _has_field(model, name: str) -> bool:
    return any(getattr(f, "name", None) == name for f in model._meta.get_fields())

def _order_business(qs):
    """Order by occurred_at if available; else fallback to created_at."""
    return qs.order_by("-occurred_at", "-created_at") \
        if _has_field(qs.model, "occurred_at") else qs.order_by("-created_at")

def _when(obj):
    """Prefer occurred_at if present; else created_at; return localized dt."""
    dt = getattr(obj, "occurred_at", None) or getattr(obj, "created_at", None)
    return localtime(dt) if dt else None









    return localtime(dt) if dt else None

# ----------------- Auth -----------------
@require_http_methods(["GET", "POST"])
def logout_and_home(request):
    logout(request)
    return redirect(request.GET.get("next") or "home")

# ----------------- Dashboard -----------------
@login_required
def index(request):
    u = request.user

    dep_done = Deposit.objects.filter(user=u, status__in=APPROVED)
    wdr_done = Withdrawal.objects.filter(user=u, status__in=APPROVED)
    inv_done = Investment.objects.filter(user=u, status__in=APPROVED)

    deposit_total    = _sum(dep_done, "amount_usd")
    withdrawal_total = _sum(wdr_done, "amount_usd")
    profit_total     = _sum(inv_done, "profit_usd")
    balance          = deposit_total + profit_total - withdrawal_total

    from django.db.models import Sum as _Sum
    dep_by_asset = defaultdict(Decimal)
    for r in dep_done.values("asset").annotate(total=_Sum("amount_usd")):
        dep_by_asset[_norm_asset(r["asset"])] += r["total"]

    wdr_by_asset = defaultdict(Decimal)
    for r in wdr_done.values("asset").annotate(total=_Sum("amount_usd")):
        wdr_by_asset[_norm_asset(r["asset"])] += r["total"]

    net_by_asset = {}
    for sym in set(dep_by_asset) | set(wdr_by_asset):
        amt = dep_by_asset.get(sym, Decimal("0")) - wdr_by_asset.get(sym, Decimal("0"))
        if amt > 0:
            net_by_asset[sym] = amt

    total_usd = sum(net_by_asset.values()) or Decimal("0")
    ordered = sorted(net_by_asset.items(), key=lambda kv: float(kv[1]), reverse=True)
    alloc_symbols = [sym for sym, _ in ordered]
    alloc_labels  = [ASSET_NAME.get(sym, sym) for sym in alloc_symbols]
    alloc_values  = ([round(float(v / total_usd * 100), 2) for _, v in ordered] if total_usd > 0 else [])
    alloc_colors  = [ASSET_COLOR.get(sym, "#888888") for sym in alloc_symbols]
    currency_rows = [{"symbol": s, "name": ASSET_NAME.get(s, s), "usd": v} for s, v in ordered]

    ctx = {
        "segment": "index",
        "balance": balance,
        "deposit_total": deposit_total,
        "profit_total": profit_total,
        "alloc_labels_json": json.dumps(alloc_labels),
        "alloc_values_json": json.dumps(alloc_values),
        "alloc_colors_json": json.dumps(alloc_colors),
        "currency_rows": currency_rows,
        "pending_deposits_total": _sum(
            Deposit.objects.filter(user=u).exclude(status__in=APPROVED),
            "amount_usd",
        ),
    }
    return render(request, "home/dashboard2.html", ctx)

# ----------------- Investments -----------------
@login_required
def investments(request):
    qs = _order_business(Investment.objects.filter(user=request.user))
    return render(request, "home/investments.html", {"object_list": qs})

@login_required
def invest(request):
    return investments(request)

@login_required
def plans(request):
    return render(request, "home/plans.html", {})

# ----------------- Deposit -----------------
@login_required
def deposit(request):
    u = request.user

    if request.method == "POST":
        amount  = _parse_amount(request.POST.get("amount_usd"))
        method  = (request.POST.get("method") or "Crypto").strip()
        asset   = (request.POST.get("asset") or "").strip()
        network = (request.POST.get("network") or "").strip()
        notes   = (request.POST.get("notes") or "").strip()

        if amount < CRYPTO_MIN:
            messages.error(request, f"Enter a valid amount (minimum ${CRYPTO_MIN}).")
        else:
            Deposit.objects.create(
                user=u,
                reference=Deposit.new_ref(),
                amount_usd=amount,
                method=method,
                asset=asset,
                network=network,
                notes=notes,
                status="pending",
            )
            messages.success(request, "Deposit submitted and is pending approval.")
            return redirect("dashboard:deposit")

    dep_done = Deposit.objects.filter(user=u, status__in=APPROVED)
    inv_done = Investment.objects.filter(user=u, status__in=APPROVED)
    wdr_done = Withdrawal.objects.filter(user=u, status__in=APPROVED)
    balance  = _sum(dep_done, "amount_usd") + _sum(inv_done, "profit_usd") - _sum(wdr_done, "amount_usd")

    addr_map = {}
    for row in PaymentAddress.objects.filter(is_active=True):
        qr_url = ""
        if hasattr(row, "qr_image") and getattr(row, "qr_image"):
            try:
                qr_url = row.qr_image.url
            except Exception:
                qr_url = ""
        addr_map[row.asset] = {"address": row.address, "network": row.network, "qr_url": qr_url}

    recent = _order_business(Deposit.objects.filter(user=u))[:20]

    ctx = {"balance_usd": balance, "object_list": recent, "addr_map": addr_map}
    return render(request, "home/deposit.html", ctx)

# ----------------- Withdraw (2-step) -----------------
@login_required
@require_http_methods(["GET", "POST"])
def withdraw_request(request):
    u = request.user

    if request.method == "POST":
        form = WithdrawalRequestForm(request.POST)
        if form.is_valid():
            data = {
                "method": "Crypto",
                "asset": form.cleaned_data.get("asset", "").upper(),
                "network": (form.cleaned_data.get("network") or "").upper(),
                "address": (form.cleaned_data.get("address") or "").strip(),
                "amount_usd": str(form.cleaned_data["amount_usd"]),
                "notes": (form.cleaned_data.get("notes") or "").strip(),
            }
            request.session[PENDING_SESSION_KEY] = data
            request.session.modified = True
            return redirect("dashboard:withdraw_confirm")
        else:
            for _, errs in form.errors.items():
                for e in errs:
                    messages.error(request, e)

    object_list = _order_business(Withdrawal.objects.filter(user=u))
    deposit_total    = _sum(Deposit.objects.filter(user=u, status__in=APPROVED), "amount_usd")
    profit_total     = _sum(Investment.objects.filter(user=u, status__in=APPROVED), "profit_usd")
    withdrawn_total  = _sum(Withdrawal.objects.filter(user=u, status__in=APPROVED), "amount_usd")
    balance          = deposit_total + profit_total - withdrawn_total
    pending_total    = _sum(Withdrawal.objects.filter(user=u).exclude(status__in=APPROVED), "amount_usd")

    ctx = {"object_list": object_list, "balance_usd": balance, "pending_withdrawals_total": pending_total}
    return render(request, "home/withdraw.html", ctx)

@login_required
@require_http_methods(["GET", "POST"])
def withdraw_confirm(request):
    payload = request.session.get(PENDING_SESSION_KEY)
    if not payload:
        messages.error(request, "No withdrawal request to confirm.")
        return redirect("dashboard:withdraw")

    if request.method == "POST":
        form = WithdrawalConfirmForm(request.POST)
        if form.is_valid():
            if not request.user.check_password(form.cleaned_data["password"]):
                form.add_error("password", "Incorrect password.")
            else:
                w = Withdrawal.objects.create(
                    user=request.user,
                    reference=Withdrawal.new_ref(),
                    amount_usd=payload["amount_usd"],
                    asset=payload["asset"],
                    network=payload["network"],
                    address=payload["address"],
                    status="pending",
                    notes=payload.get("notes", ""),
                )
                request.session.pop(PENDING_SESSION_KEY, None)
                messages.success(request, f"Withdrawal request {w.reference} submitted and is pending review.")
                return redirect("dashboard:withdraw")
    else:
        form = WithdrawalConfirmForm()

    try:
        amount_float = float(payload["amount_usd"])
    except Exception:
        amount_float = 0.0

    ctx = {"payload": payload, "amount_float": amount_float, "form": form}
    return render(request, "home/withdraw_confirm.html", ctx)

# ----------------- Misc -----------------
@login_required
def chart(request):
    return render(request, "home/charts.html", {})

# ----------------- Transactions -----------------
@login_required
def transactions(request):
    u = request.user
    rows = []

    for d in _order_business(Deposit.objects.filter(user=u)):
        rows.append({
            "reference": d.reference,
            "category": "deposit",
            "method": getattr(d, "method", "Crypto"),
            "asset": getattr(d, "asset", "") or "",
            "amount": d.amount_usd,
            "status": d.status,
            "date": _when(d),
            "notes": getattr(d, "notes", "") or "",
            "flow": "in",
            "network": getattr(d, "network", "") or "",
            "cryptocurrency": getattr(d, "asset", "") or "",
            "plan": "",
        })

    for w in _order_business(Withdrawal.objects.filter(user=u)):
        rows.append({
            "reference": w.reference,
            "category": "withdrawal",
            "method": getattr(w, "method", "Crypto"),
            "asset": getattr(w, "asset", "") or "",
            "amount": w.amount_usd,
            "status": w.status,
            "date": _when(w),
            "notes": getattr(w, "notes", "") or "",
            "flow": "out",
            "network": getattr(w, "network", "") or "",
            "cryptocurrency": getattr(w, "asset", "") or "",
            "plan": "",
        })

    for i in _order_business(Investment.objects.filter(user=u)):
        profit = getattr(i, "profit_usd", Decimal("0.00")) or Decimal("0.00")
        if profit != 0:
            rows.append({
                "reference": i.reference,
                "category": "investment",
                "method": "Profit",
                "asset": getattr(i, "plan", "") or "Plan",
                "amount": profit,
                "status": i.status,
                "date": _when(i),
                "notes": getattr(i, "notes", "") or "",
                "flow": "in",
                "plan": getattr(i, "plan", "") or "",
                "network": "",
                "cryptocurrency": "",
            })

    inflows  = _sum(Deposit.objects.filter(user=u, status__in=APPROVED), "amount_usd") \
             + _sum(Investment.objects.filter(user=u, status__in=APPROVED), "profit_usd")
    outflows = _sum(Withdrawal.objects.filter(user=u, status__in=APPROVED), "amount_usd")
    totals = {"inflows": inflows, "outflows": outflows, "net": inflows - outflows}

    rows.sort(key=lambda r: (r["date"] or 0), reverse=True)
    return render(request, "home/transactions.html", {"object_list": rows, "totals": totals})

# ----------------- Profile (unchanged below) -----------------
try:
    from profiles.models import Profile as ProfilesProfile
except Exception:
    ProfilesProfile = None

try:
    from major.models import Profile as MajorProfile
except Exception:
    MajorProfile = None

def _resolve_profile(user):
    prof = None
    if ProfilesProfile:
        prof = ProfilesProfile.objects.filter(user=user).first()
        if prof is None:
            try:
                prof = ProfilesProfile.objects.create(user=user)
            except Exception:
                pass
    if not prof and MajorProfile:
        prof = MajorProfile.objects.filter(user=user).first()
    if not prof:
        prof = SimpleNamespace(
            phone=getattr(user, "phone", "") or "",
            country=getattr(user, "country", "") or "",
            avatar=getattr(user, "avatar", None),
        )
    return prof

@login_required
def profile(request):
    user = request.user
    prof = _resolve_profile(user)
    phone_display = getattr(prof, "phone", "") or getattr(user, "phone", "")
    country_display = getattr(prof, "country", "") or getattr(user, "country", "")
    avatar_url = ""
    try:
        if getattr(prof, "avatar", None) and hasattr(prof, "avatar") and hasattr(prof.avatar, "url"):
            avatar_url = prof.avatar.url
    except Exception:
        avatar_url = ""

    ctx = {
        "profile": prof,
        "avatar_url": avatar_url,
        "phone_display": phone_display,
        "country_display": country_display,
    }
    return render(request, "home/profile.html", ctx)

@login_required
@require_http_methods(["GET", "POST"])
def profile_edit(request):
    user = request.user
    prof = _resolve_profile(user)

    if request.method == "POST":
        user.first_name = (request.POST.get("first_name") or "").strip()
        user.last_name  = (request.POST.get("last_name") or "").strip()
        email = (request.POST.get("email") or "").strip()
        if email:
            user.email = email
        user.save()

        prof.phone   = (request.POST.get("phone") or "").strip()
        prof.country = (request.POST.get("country") or "").strip()
        if request.FILES.get("avatar"):
            prof.avatar = request.FILES["avatar"]
        if hasattr(prof, "save"):
            try:
                prof.save()
            except Exception:
                pass

        messages.success(request, "Profile updated.")
        return redirect("dashboard:profile")

    avatar_url = ""
    try:
        if getattr(prof, "avatar", None) and hasattr(prof, "avatar") and hasattr(prof.avatar, "url"):
            avatar_url = prof.avatar.url
    except Exception:
        avatar_url = ""

    return render(request, "home/edit_profile.html", {"profile": prof, "avatar_url": avatar_url})

# ========================= Staff-only: occurred_at editor =========================
def _get_tx_for_kind(kind: str, pk: int):
    kind = (kind or "").lower()
    model = {"deposit": Deposit, "withdrawal": Withdrawal, "investment": Investment}.get(kind)
    if not model:
        return None
    return get_object_or_404(model, pk=pk)

@user_passes_test(lambda u: u.is_staff)
@require_http_methods(["GET", "POST"])
def tx_time_edit_staff(request, kind: str, pk: int):
    tx = _get_tx_for_kind(kind, pk)
    if tx is None:
        messages.error(request, "Unknown transaction type.")
        return redirect("dashboard:index")

    class _BoundForm(TxTimeFormAdmin):
        class Meta(TxTimeFormAdmin.Meta):
            model = tx.__class__

    if request.method == "POST":
        form = _BoundForm(request.POST, instance=tx)
        if form.is_valid():
            form.save()
            messages.success(request, f"{kind.title()} {tx.reference} time updated.")
            return redirect(request.GET.get("next") or "dashboard:index")
    else:
        form = _BoundForm(instance=tx)

    return render(request, "home/tx_time_form_staff.html", {"form": form, "tx": tx, "kind": kind})
