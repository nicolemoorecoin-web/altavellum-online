# dashboard/home/services.py
from decimal import Decimal
import time
import requests

# simple in‑memory cache for 60s per symbol
_PRICE_CACHE = {}

def get_price(symbol_id: str) -> Decimal:
    """
    symbol_id is a CoinGecko id like 'bitcoin', 'ethereum', 'tether', 'cardano'
    """
    now = time.time()
    entry = _PRICE_CACHE.get(symbol_id)
    if entry and (now - entry["ts"] < 60):
        return entry["price"]

    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": symbol_id, "vs_currencies": "usd"}
    try:
        r = requests.get(url, params=params, timeout=8)
        r.raise_for_status()
        price = Decimal(str(r.json()[symbol_id]["usd"]))
    except Exception:
        # fallback if API is down—keep app working
        fallback = {
            "bitcoin": Decimal("60000"),
            "ethereum": Decimal("3000"),
            "tether": Decimal("1"),
            "cardano": Decimal("0.5"),
        }
        price = fallback.get(symbol_id, Decimal("0"))

    _PRICE_CACHE[symbol_id] = {"price": price, "ts": now}
    return price