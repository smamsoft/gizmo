# session_store.py

import os
import json
from typing import Dict, Any, Optional, List

import redis

# REDIS_URI من .env (مثال: redis://smam_redis:6379/0)
REDIS_URI = os.getenv("REDIS_URI", "redis://smam_redis:6379/0")

# decode_responses=True لكي نتعامل مع نصوص عادية بدلاً من bytes
r = redis.from_url(REDIS_URI, decode_responses=True)


def _menu_key(phone: str) -> str:
    """
    يبني مفتاح Redis خاص بالمنيو لرقم معين.
    """
    phone = (phone or "").strip()
    return f"whatsapp:menu:{phone}"


def save_menu(phone: str, menu_type: str, items: List[Dict[str, Any]]) -> None:
    """
    تخزين آخر منيو أرسلتها لهذا الرقم.
    """
    key = _menu_key(phone)
    payload = {
        "type": menu_type,
        "items": items,
    }
    try:
        r.set(key, json.dumps(payload, ensure_ascii=False))
        # يمكن إضافة TTL إن أحببت:
        # r.expire(key, 3600)
    except Exception as e:
        print("### SESSION_STORE ERROR save_menu:", e)


def load_menu(phone: str) -> Optional[Dict[str, Any]]:
    """
    استرجاع آخر منيو محفوظة لهذا الرقم.
    """
    key = _menu_key(phone)
    try:
        val = r.get(key)
        if not val:
            return None
        return json.loads(val)
    except Exception as e:
        print("### SESSION_STORE ERROR load_menu:", e)
        return None


def clear_menu(phone: str) -> None:
    """
    مسح المنيو المخزّنة لهذا الرقم.
    """
    key = _menu_key(phone)
    try:
        r.delete(key)
    except Exception as e:
        print("### SESSION_STORE ERROR clear_menu:", e)


# ========= حالة القوائم (State) لكل رقم =========

def _state_key(phone: str) -> str:
    """
    مفتاح Redis لحالة المحادثة (القائمة الحالية) لرقم معين.
    """
    phone = (phone or "").strip()
    return f"whatsapp:state:{phone}"


def save_state(phone: str, state: str) -> None:
    """
    حفظ حالة المحادثة (مثلاً: main, products, staff_main, ...).
    """
    key = _state_key(phone)
    try:
        r.set(key, state)
    except Exception as e:
        print("### SESSION_STORE ERROR save_state:", e)


def load_state(phone: str) -> Optional[str]:
    """
    استرجاع حالة المحادثة الحالية لهذا الرقم.
    تعيد None إن لم توجد حالة.
    """
    key = _state_key(phone)
    try:
        return r.get(key)
    except Exception as e:
        print("### SESSION_STORE ERROR load_state:", e)
        return None
