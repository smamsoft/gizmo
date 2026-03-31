# use_cases.py

from typing import Optional

from gizmo_tools import (
    get_user_by_phone,
    get_balance_by_phone,
    get_points_by_phone,
    list_free_hosts_simple,
    list_products_grouped_for_menu,
    generate_topup_link_fixed,
    register_user_by_phone,
    uc_customer_view_my_reservations,
    uc_customer_view_current_host_uc,
    uc_customer_view_remaining_time_uc,
)

CURRENCY = "AED"  # يمكنك استيراده من env لو أحببت


# ========== CUSTOMER Use Cases ==========

async def uc_customer_check_balance(phone: str) -> str:
    user = await get_user_by_phone(phone)
    if not user:
        return (
            "رقمك غير مسجّل كعضو في النظام، لا يمكن عرض الرصيد.\n"
            "اختر 7 لتسجيل عضوية جديدة، ثم أرسل 'رصيدي' مرة أخرى."
        )
    bal = await get_balance_by_phone(phone)
    if bal is None:
        return "لم أتمكن من إيجاد رصيدك حالياً، تحقق من تسجيلك أو تواصل مع الكاشير."
    return f"رصيدك الحالي هو {bal:.2f} {CURRENCY}."


async def uc_customer_check_points(phone: str) -> str:
    user = await get_user_by_phone(phone)
    if not user:
        return (
            "رقمك غير مسجّل كعضو في النظام، لا يمكن عرض النقاط.\n"
            "اختر 7 لتسجيل عضوية جديدة، ثم أرسل 'نقاطي' مرة أخرى."
        )
    pts = await get_points_by_phone(phone)
    if pts is None:
        return "لم أتمكن من إيجاد نقاطك حالياً."
    return f"لديك حالياً {pts} نقطة ولاء."


async def uc_customer_list_hosts_free(phone: str) -> str:
    hosts = await list_free_hosts_simple()
    if not hosts:
        return "لا توجد أجهزة متاحة حالياً."
    nums = [str(h.get("number") or h.get("name")) for h in hosts]
    return "الأجهزة المتاحة الآن: " + ", ".join(nums) + "."


async def uc_customer_show_menu(phone: str) -> str:
    """
    هذه الدالة يمكن أن تعيد نصاً بسيطاً أو تُستخدم فقط كـ hook،
    لأن بناء المنيو الفعلي يتم في intents.py (مع save_menu).
    """
    grouped = await list_products_grouped_for_menu()
    if not grouped:
        return "حالياً لا توجد منتجات مسجّلة في النظام."
    return "سيتم عرض قائمة المنتجات الآن."


async def uc_customer_topup_50(phone: str) -> str:
    return await generate_topup_link_fixed(phone, 50.0)


async def uc_customer_register(phone: str) -> str:
    return await register_user_by_phone(phone)


async def uc_customer_view_reservations(phone: str) -> str:
    return await uc_customer_view_my_reservations(phone)


async def uc_customer_view_current_host_uc(phone: str) -> str:
    return await uc_customer_view_current_host_uc(phone)


async def uc_customer_view_remaining_time_uc(phone: str) -> str:
    return await uc_customer_view_remaining_time_uc(phone)
