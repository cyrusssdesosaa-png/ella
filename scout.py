"""Read OpenRouter's public model list. No key. Zero-price and :free only."""

import json
import urllib.request

LIST_URL = "https://openrouter.ai/api/v1/models"


def _zero(price):
    if price is None:
        return False
    try:
        return float(price) == 0.0
    except (TypeError, ValueError):
        return str(price).strip() in {"0", "0.0"}


def fetch_free_models():
    req = urllib.request.Request(LIST_URL, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as res:
        payload = json.loads(res.read().decode("utf-8"))
    found = []
    for item in payload.get("data") or []:
        model_id = item.get("id") or ""
        pricing = item.get("pricing") or {}
        free_id = model_id.endswith(":free") or model_id == "openrouter/free"
        free_price = _zero(pricing.get("prompt")) and _zero(pricing.get("completion"))
        if free_id or free_price:
            found.append(
                {
                    "id": model_id,
                    "name": item.get("name") or model_id,
                }
            )
    found.sort(key=lambda row: row["id"])
    return found
