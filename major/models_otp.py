# major/models_otp.py
from django.conf import settings
from django.db import models
from django.utils import timezone
from datetime import timedelta
import secrets

def _make_code():
    # 6-digit numeric code, zero-padded
    return f"{secrets.randbelow(1_000_000):06d}"

class LoginOTP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    attempts = models.PositiveIntegerField(default=0)
    is_used = models.BooleanField(default=False)
    ip = models.CharField(max_length=64, blank=True)
    user_agent = models.TextField(blank=True)

    @classmethod
    def create_for(cls, user, minutes=10, ip="", ua=""):
        now = timezone.now()
        return cls.objects.create(
            user=user,
            code=_make_code(),
            expires_at=now + timedelta(minutes=minutes),
            ip=ip or "",
            user_agent=ua or "",
        )

    def is_expired(self):
        return timezone.now() > self.expires_at
