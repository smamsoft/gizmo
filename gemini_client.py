# gemini_client.py

import os
from typing import Dict, Any, List

import httpx  # مستخدم فقط إذا فعّلت الخدمة الخارجية

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = os.getenv("GEMINI_URL")  # اختياري: لو عندك خدمة وسيطة لGemini
CURRENCY = os.getenv("CURRENCY", "AED")


async def detect_intent(text: str, role: str, user_ctx: Dict[str, Any]) -> Dict[str, Any]:
    """
    تحديد الـ Intent من نص المستخدم ودوره.
    الآن: منطق بسيط محلي (بدون استدعاء خارجي).
    لاحقاً: يمكنك استبداله باستدعاء فعلي لـ Gemini عبر GEMINI_URL.
    """
    t = (text or "").strip().lower()

    # أمثلة بسيطة
    if any(k in t for k in ["رصيدي", "رصيد", "balance", "credit"]):
        return {"intent": "CHECK_BALANCE", "entities": {}}

    if any(k in t for k in ["الأجهزة المتاحة", "الاجهزه المتاحه", "hosts"]):
        return {"intent": "LIST_HOSTS_FREE", "entities": {}}

    if any(k in t for k in ["المنيو", "المنتجات", "menu", "products"]):
        return {"intent": "LIST_PRODUCTS", "entities": {}}

    if any(k in t for k in ["المستخدمين", "users"]):
        return {"intent": "COUNT_USERS", "entities": {}}

    # يمكنك لاحقاً إضافة كلمات مفتاحية أخرى مثل:
    # "حجز", "reservation", "booking" -> MAKE_RESERVATION
    # "تقرير", "report" -> VIEW_REPORT ...

    return {"intent": "UNKNOWN", "entities": {}}


async def generate_reply(intent: str, gizmo_result: Any, full_ctx: Dict[str, Any]) -> str:
    """
    صياغة الرد النهائي كنص للمستخدم، بناءً على Intent ونتيجة Gizmo وسياق المستخدم.
    حالياً: منطق محلي بسيط؛ لاحقاً يمكن استبداله باستدعاء Gemini فعلي.
    """
    user = full_ctx.get("user", {})
    name = user.get("name") or full_ctx.get("from_name") or "ضيف"
    text = full_ctx.get("text", "")

    if intent == "CHECK_BALANCE":
        bal = None
        if isinstance(gizmo_result, dict):
            bal = gizmo_result.get("balance")
        if bal is None:
            return f"مرحباً {name}، لم أستطع قراءة رصيدك حالياً."
        return f"مرحباً {name}، رصيدك الحالي في Gizmo هو {bal} {CURRENCY}."

    if intent == "LIST_HOSTS_FREE":
        hosts: List[Dict[str, Any]] = gizmo_result or []
        if not hosts:
            return f"مرحباً {name}، لا توجد أجهزة متاحة حالياً."
        nums = [str(h.get("number", h.get("id"))) for h in hosts if isinstance(h, dict)]
        return f"مرحباً {name}، الأجهزة المتاحة الآن: {', '.join(nums)}."

    if intent == "LIST_PRODUCTS":
        products: List[Dict[str, Any]] = gizmo_result or []
        if not products:
            return f"مرحباً {name}، لا توجد منتجات متاحة حالياً."
        lines = []
        for p in products[:10]:
            if not isinstance(p, dict):
                continue
            pname = p.get("name") or p.get("description") or "منتج"
            price = p.get("price", 0)
            lines.append(f"- {pname}: {price} {CURRENCY}")
        return f"مرحباً {name}، بعض المنتجات المتاحة:\n" + "\n".join(lines)

    if intent == "COUNT_USERS":
        count = 0
        if isinstance(gizmo_result, list):
            count = len(gizmo_result)
        return f"مرحباً {name}، عدد المستخدمين في Gizmo حالياً: {count}."

    # رد افتراضي
    return (
        f"مرحباً {name}، استقبلت رسالتك:\n"
        f"\"{text}\"\n"
        f"لكن لم أتعرف على الطلب بدقة. "
        f"يمكنك أن تقول مثلاً: رصيدي، الأجهزة المتاحة، المنيو."
    )


async def _call_external_gemini(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    مثال استدعاء خدمة Gemini خارجية (إذا بنيت خدمة خاصة بك تستقبل JSON).
    حالياً غير مستخدمة؛ يمكنك تفعيلها عند ضبط GEMINI_URL و GEMINI_API_KEY.
    """
    if not (GEMINI_URL and GEMINI_API_KEY):
        return {"reply": "Gemini service not configured.", "intent": "UNKNOWN"}

    headers = {
        "Authorization": f"Bearer {GEMINI_API_KEY}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(GEMINI_URL, json=payload, headers=headers, timeout=25)
        resp.raise_for_status()
        return resp.json()
