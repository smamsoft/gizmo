# evo_client.py

import os
from typing import Dict, Any

import httpx

# إعدادات Evolution من .env
EVO_URL = os.getenv("EVO_URL")            # مثال: http://smam_evolution:8080
EVO_INSTANCE = os.getenv("EVO_INSTANCE")  # مثال: gizmo_bot
EVO_API_KEY = os.getenv("EVO_API_KEY")    # مثال: GlobalApiKey_123


def _check_config() -> None:
    if not EVO_URL:
        raise RuntimeError("EVO_URL is not configured.")
    if not EVO_INSTANCE:
        raise RuntimeError("EVO_INSTANCE is not configured.")
    if not EVO_API_KEY:
        raise RuntimeError("EVO_API_KEY is not configured.")


async def send_text(phone: str, message: str) -> Dict[str, Any]:
    """
    إرسال رسالة نصية عادية عبر Evolution API v2:
      POST {EVO_URL}/message/sendText/{EVO_INSTANCE}

    Payload:
      {
        "number": "9715....",
        "text": "الرسالة"
      }
    """
    _check_config()

    payload = {
        "number": str(phone),
        "text": message,
    }

    url = f"{EVO_URL}/message/sendText/{EVO_INSTANCE}"
    headers = {"apikey": EVO_API_KEY}

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, headers=headers, timeout=15)
    except Exception as e:
        print("### EVO_CLIENT ERROR (request failed):", e)
        return {
            "ok": False,
            "status_code": None,
            "error": str(e),
        }

    result: Dict[str, Any] = {
        "ok": resp.status_code in (200, 201),
        "status_code": resp.status_code,
    }

    try:
        result["body"] = resp.json()
    except Exception:
        result["body"] = resp.text

    if not result["ok"]:
        print("### EVO_CLIENT SEND ERROR:", result)

    return result
