# gemini_bot.py

from typing import Dict, Any

from authz import has_permission
from gizmo_tools import (
    get_balance_by_phone,
    get_points_by_phone,
    list_products_grouped_for_menu,
    list_free_hosts_simple,
)

CURRENCY = "AED"  # أو من .env إذا أحببت


async def handle_user_message_with_gemini(
    text: str,
    phone: str,
    role: str,
    user_ctx: Dict[str, Any] | None = None,
) -> str:
    """
    طبقة منطق فوق Gizmo + الصلاحيات،
    مخصصة لاحقاً لدمج Gemini (الآن منطق بسيط يشبه intents.py).

    يمكنك مستقبلاً:
      - استدعاء Gemini لتحديد intent + entities
      - ثم توجيه الطلب إلى إحدى الدوال أدناه.
    """
    t = (text or "").strip().lower()
    user_ctx = user_ctx or {}

    # رصيدي
    if any(k in t for k in ["رصيدي", "رصيد", "balance", "credit"]):
        if not has_permission(role, "CHECK_BALANCE"):
            return "عذراً، ليست لديك صلاحية للاستعلام عن الرصيد."
        bal = await get_balance_by_phone(phone)
        if bal is None:
            return "لم أتمكن من إيجاد حسابك في النظام. تأكد أن رقمك مسجّل لدينا."
        return f"رصيدك الحالي هو {bal:.2f} {CURRENCY}."

    # نقاطي
    if any(k in t for k in ["نقاطي", "نقاط", "points"]):
        if not has_permission(role, "CHECK_POINTS"):
            return "عذراً، ليست لديك صلاحية للاستعلام عن النقاط."
        pts = await get_points_by_phone(phone)
        if pts is None:
            return "لم أتمكن من إيجاد نقاطك حالياً. تأكد أن رقمك مسجّل لدينا."
        return f"لديك حالياً {pts} نقطة ولاء."

    # الأجهزة المتاحة
    if any(k in t for k in ["الأجهزة المتاحة", "الاجهزه المتاحه", "الاجهزة المتاحة", "hosts"]):
        if not has_permission(role, "LIST_HOSTS_FREE"):
            return "عذراً، ليست لديك صلاحية لرؤية حالة الأجهزة."
        hosts = await list_free_hosts_simple()
        if not hosts:
            return "لا توجد أجهزة متاحة حالياً."
        nums = [str(h.get("number") or h.get("name")) for h in hosts]
        return "الأجهزة المتاحة الآن: " + ", ".join(nums) + "."

    # المنيو
    if any(k in t for k in ["المنيو", "المنتجات", "menu", "products"]):
        if not has_permission(role, "LIST_PRODUCTS"):
            return "عذراً، ليست لديك صلاحية لرؤية قائمة المنتجات."
        grouped = await list_products_grouped_for_menu()
        if not grouped:
            return "حالياً لا توجد منتجات مسجّلة في النظام."

        lines = ["قائمة المنتجات (ملخّص):"]
        idx = 1
        for group_name, products in grouped.items():
            if not products:
                continue
            lines.append(f"\n🔹 {group_name}:")
            for p in products[:5]:  # نعرض أول 5 من كل مجموعة في الملخص
                name = p.get("name") or p.get("description") or "منتج"
                price = p.get("price", 0)
                lines.append(f"  - {name}: {price} {CURRENCY}")
                idx += 1
        lines.append("\nلرؤية القائمة الكاملة مع الترقيم، اكتب: المنيو")
        return "\n".join(lines)

    # افتراضي
    return (
        "مرحباً 👋\n"
        "يمكنني مساعدتك حالياً في:\n"
        "- معرفة رصيدك (اكتب: رصيدي)\n"
        "- معرفة نقاطك (اكتب: نقاطي)\n"
        "- معرفة الأجهزة المتاحة\n"
        "- عرض قائمة المنتجات (اكتب: المنيو)\n"
    )
