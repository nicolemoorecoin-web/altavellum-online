# major/views_login_otp.py
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render, redirect
from django.template.loader import render_to_string, TemplateDoesNotExist
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django import forms
from django.urls import reverse, NoReverseMatch

from .models_otp import LoginOTP

User = get_user_model()

# ===== Flags / Settings
OTP_EXP_MIN = int(getattr(settings, "LOGIN_OTP_EXPIRY_MINUTES", 10))
OTP_MAX_ATTEMPTS = int(getattr(settings, "LOGIN_OTP_MAX_ATTEMPTS", 5))
REQUIRE_OTP = bool(getattr(settings, "LOGIN_REQUIRE_OTP", True))
ALLOW_OTP_FALLBACK = bool(getattr(settings, "LOGIN_ALLOW_OTP_FALLBACK", False))

# Show dev OTP in Django messages as well as printing to console
SHOW_DEV_OTP_IN_MESSAGES = bool(getattr(settings, "SHOW_DEV_OTP_IN_MESSAGES", True))


# ===== Forms
class LoginStep1Form(forms.Form):
    username = forms.CharField(label="Email or Username")
    password = forms.CharField(widget=forms.PasswordInput)

class LoginStep2Form(forms.Form):
    code = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={"inputmode": "numeric", "autocomplete": "one-time-code"})
    )

class SignupForm(forms.Form):
    username  = forms.CharField(max_length=150)
    email     = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm password")

    def clean_username(self):
        u = self.cleaned_data["username"]
        if User.objects.filter(username__iexact=u).exists():
            raise ValidationError("Username is already taken.")
        return u

    def clean(self):
        c = super().clean()
        p1, p2 = c.get("password1"), c.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Passwords do not match.")
        if p1:
            validate_password(p1)
        email = c.get("email")
        if email and User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Email is already in use.")
        return c


# ===== Helpers
def _safe_reverse(name, *args, **kwargs) -> str | None:
    try:
        return reverse(name, args=args, kwargs=kwargs)
    except NoReverseMatch:
        return None

def _redirect_after_login(request):
    nxt = request.GET.get("next") or request.POST.get("next")
    if nxt:
        return redirect(nxt)
    for candidate in ("user-home", "dashboard:index"):
        url = _safe_reverse(candidate)
        if url:
            return redirect(url)
    return redirect("/")

def _dev_emit_otp(user, otp_code, request=None):
    """
    In DEBUG, always show the OTP in the terminal.
    Optionally also via Django messages to speed up testing.
    """
    if settings.DEBUG:
        print(f"\n[DEV OTP] user={getattr(user, 'username', '<unknown>')}  code={otp_code}\n")
        if SHOW_DEV_OTP_IN_MESSAGES and request is not None:
            messages.info(request, f"DEV OTP: {otp_code}")

def _send_html_email(subject, to_email, html, text_fallback=""):
    """
    Send HTML email; if no recipient or email backend fails, don't crash login.
    """
    try:
        msg = EmailMultiAlternatives(
            subject,
            text_fallback or subject or "",
            getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@local"),
            [to_email] if to_email else [],   # allow empty list
        )
        if html:
            msg.attach_alternative(html, "text/html")
        # Even if recipients list is empty, trying to send is harmless with console backend,
        # but some backends might choke—so guard it:
        if to_email:
            msg.send()
    except Exception:
        # Never block auth flow due to email issues
        pass

def _render_login_otp_html(ctx):
    """
    Try to render emails/login_otp.html; if missing, return a simple text fallback as HTML.
    """
    try:
        return render_to_string("emails/login_otp.html", ctx)
    except TemplateDoesNotExist:
        # minimal fallback
        return f"<p>Your {ctx.get('site_name','Altavellum')} login code is <b>{ctx.get('otp')}</b>. It expires in {ctx.get('expiry_min', OTP_EXP_MIN)} minutes.</p>"
    except Exception:
        return None

def _send_otp_email(user, otp_obj):
    ctx = {
        "user": user,
        "otp": otp_obj.code,
        "site_name": getattr(settings, "SITE_NAME", "Altavellum"),
        "site_url": getattr(settings, "SITE_URL", ""),
        "expiry_min": OTP_EXP_MIN,
        "ip": otp_obj.ip,
        "ua": (otp_obj.user_agent or "")[:200],
        "created_at": otp_obj.created_at,
    }
    html = _render_login_otp_html(ctx)
    _send_html_email(
        subject=f"{ctx['site_name']} Login OTP",
        to_email=(user.email or "").strip() or None,
        html=html,
        text_fallback=f"Your {ctx['site_name']} login code is {ctx['otp']}. Expires in {ctx['expiry_min']} minutes.",
    )

def _send_login_alert_email(user, request):
    ctx = {
        "user": user,
        "site_name": getattr(settings, "SITE_NAME", "Altavellum"),
        "site_url": getattr(settings, "SITE_URL", ""),
        "ip": request.META.get("REMOTE_ADDR", ""),
        "ua": (request.META.get("HTTP_USER_AGENT") or "")[:200],
        "time": timezone.now(),
    }
    try:
        html = render_to_string("emails/login_alert.html", ctx)
    except TemplateDoesNotExist:
        html = f"<p>New login to {ctx['site_name']} detected.</p>"
    except Exception:
        html = None
    _send_html_email(
        subject=f"{ctx['site_name']} New Login",
        to_email=(user.email or "").strip() or None,
        html=html,
        text_fallback="New login detected. If this wasn't you, change your password immediately.",
    )

def _authenticate_by_identifier(identifier: str, password: str):
    if not identifier or not password:
        return None
    user = authenticate(username=identifier, password=password)
    if user:
        return user
    try:
        email_user = User.objects.filter(email__iexact=identifier).first()
        if email_user:
            return authenticate(username=email_user.username, password=password)
    except Exception:
        pass
    return None


# ===== Views
@require_http_methods(["GET", "POST"])
def signup(request):
    if request.user.is_authenticated:
        return _redirect_after_login(request)

    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password1"],
            )
        except Exception as e:
            messages.error(request, f"Could not create account: {e}")
            return render(request, "auth/signup.html", {"form": form})

        authed = _authenticate_by_identifier(user.username, form.cleaned_data["password1"]) or (
            user.email and _authenticate_by_identifier(user.email, form.cleaned_data["password1"])
        )
        if authed:
            login(request, authed)
            messages.success(request, "Account created. You are now signed in.")
            return _redirect_after_login(request)

        messages.warning(request, "Account created, but automatic sign-in failed. Please sign in.")
        return redirect(_safe_reverse("login") or "/accounts/login/")

    return render(request, "auth/signup.html", {"form": form})


@require_http_methods(["GET", "POST"])
def login_step1(request):
    if request.user.is_authenticated:
        return _redirect_after_login(request)

    form = LoginStep1Form(request.POST or None)
    if request.method == "POST" and form.is_valid():
        ident = form.cleaned_data["username"].strip()
        pwd = form.cleaned_data["password"]
        user = _authenticate_by_identifier(ident, pwd)

        if not user:
            messages.error(request, "Invalid credentials. Check your email/username and password.")
            return render(request, "auth/login_step1.html", {"form": form})

        if not user.is_active:
            messages.error(request, "Account is inactive.")
            return render(request, "auth/login_step1.html", {"form": form})

        if REQUIRE_OTP:
            try:
                otp = LoginOTP.create_for(
                    user,
                    minutes=OTP_EXP_MIN,
                    ip=request.META.get("REMOTE_ADDR", ""),
                    ua=request.META.get("HTTP_USER_AGENT", ""),
                )
                _send_otp_email(user, otp)
                _dev_emit_otp(user, otp.code, request)  # <= always prints in DEBUG
                request.session["otp_user_id"] = user.id
                request.session.modified = True
                messages.success(request, "We sent a 6-digit code to your email.")
                return redirect(_safe_reverse("login-otp-id", kwargs={"uid": user.id}) or _safe_reverse("login-otp") or "/accounts/otp/")
            except Exception as e:
                # Respect switch: do NOT auto-login if email/OTP fails, unless explicitly allowed
                if ALLOW_OTP_FALLBACK:
                    login(request, user)
                    _send_login_alert_email(user, request)
                    return _redirect_after_login(request)
                messages.error(request, f"Could not send OTP right now. Please try again. ({e})")
                return render(request, "auth/login_step1.html", {"form": form})
        else:
            # Plain password login
            login(request, user)
            _send_login_alert_email(user, request)
            return _redirect_after_login(request)

    return render(request, "auth/login_step1.html", {"form": form})


@require_http_methods(["GET", "POST"])
def login_step2(request, uid=None):
    if not REQUIRE_OTP:
        return redirect(_safe_reverse("login") or "/accounts/login/")

    sess_uid = request.session.get("otp_user_id")
    qs_uid = request.GET.get("u")
    uid = sess_uid or uid or qs_uid
    if not uid:
        messages.error(request, "Your login session expired. Please sign in again.")
        return redirect(_safe_reverse("login") or "/accounts/login/")

    try:
        user = User.objects.get(id=uid)
    except User.DoesNotExist:
        messages.error(request, "Your login session expired. Please sign in again.")
        return redirect(_safe_reverse("login") or "/accounts/login/")

    # RESEND
    if request.method == "GET" and request.GET.get("resend") == "1":
        latest = (
            LoginOTP.objects.filter(user=user, is_used=False).order_by("-created_at").first()
        )
        cooldown_seconds = 60
        can_send = True
        if latest:
            delta = (timezone.now() - latest.created_at).total_seconds()
            if delta < cooldown_seconds:
                can_send = False
                messages.info(request, f"Please wait {int(cooldown_seconds - delta)}s before requesting a new code.")
        if can_send:
            try:
                otp = LoginOTP.create_for(
                    user,
                    minutes=OTP_EXP_MIN,
                    ip=request.META.get("REMOTE_ADDR", ""),
                    ua=request.META.get("HTTP_USER_AGENT", ""),
                )
                _send_otp_email(user, otp)
                _dev_emit_otp(user, otp.code, request)  # <= dev print
                messages.success(request, "A new code has been sent to your email.")
            except Exception as e:
                messages.error(request, f"Could not send a new code. Try again shortly. ({e})")

    form = LoginStep2Form(request.POST or None)
    if request.method == "POST" and form.is_valid():
        code = form.cleaned_data["code"].strip()
        otp = (
            LoginOTP.objects.filter(user=user, is_used=False).order_by("-created_at").first()
        )
        if not otp:
            messages.error(request, "No OTP found. Please sign in again.")
            return redirect(_safe_reverse("login") or "/accounts/login/")

        if otp.attempts >= OTP_MAX_ATTEMPTS:
            messages.error(request, "Too many attempts. Start over.")
            return redirect(_safe_reverse("login") or "/accounts/login/")

        if otp.is_expired():
            messages.error(request, "Code expired. Start over.")
            return redirect(_safe_reverse("login") or "/accounts/login/")

        if code != otp.code:
            otp.attempts += 1
            otp.save(update_fields=["attempts"])
            messages.error(request, "Incorrect code. Please try again.")
        else:
            otp.is_used = True
            otp.save(update_fields=["is_used"])
            login(request, user)
            request.session.pop("otp_user_id", None)
            _send_login_alert_email(user, request)
            messages.success(request, "Welcome back!")
            return _redirect_after_login(request)

    # masked email
    masked = (user.email or "")
    if "@" in masked:
        name, dom = masked.split("@", 1)
        masked = (name[:1] + "•••@" + dom) if name else "•••@" + dom

    return render(request, "auth/login_step2.html", {"form": form, "masked_email": masked})


@require_http_methods(["GET", "POST"])
def logout_view(request):
    logout(request)
    messages.success(request, "You’ve been logged out.")
    return redirect(_safe_reverse("home") or "/")

def terms_view(request):
    return render(request, "pages/terms.html")
