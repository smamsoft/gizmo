# use_cases.py

from typing import Optional, List, Dict
from datetime import datetime, timedelta

from gizmo_tools import (
    get_user_by_phone,
    get_balance_by_phone,
    get_points_by_phone,
    list_free_hosts_simple,
    list_products_grouped_for_menu,
    generate_topup_link_fixed,
    register_user_by_phone,
)

from gizmo_client_v2 import gizmo_v2

CURRENCY = "AED"


# =========================
# 1) USE CASES - CUSTOMER
# =========================

async def uc_customer_check_balance(phone: str) -> str:
    user = await get_user_by_phone(phone)
    if not user:
        return (
            "رقمك غير مسجّل كعضو في النظام، لا يمكن عرض الرصيد.\n"
            "اكتب (7) من القائمة الرئيسية لتسجيل عضوية جديدة."
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
            "اكتب (7) من القائمة الرئيسية لتسجيل عضوية جديدة."
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
    grouped = await list_products_grouped_for_menu()
    if not grouped:
        return "حالياً لا توجد منتجات مسجّلة في النظام."
    # هنا فقط رسالة عامة؛ التفاصيل تُعرض في منيو الأرقام
    return "سيتم عرض أقسام المنيو الآن، اختر القسم المطلوب من القائمة."


async def uc_customer_topup_50(phone: str) -> str:
    return await generate_topup_link_fixed(phone, 50.0)


async def uc_customer_register(phone: str) -> str:
    return await register_user_by_phone(phone)


# --- حجوزات العميل ---

async def uc_customer_view_reservations(phone: str) -> str:
    user = await get_user_by_phone(phone)
    if not user:
        return (
            "رقمك غير مسجّل كعضو، لذلك لا توجد حجوزات مرتبطة برقمك.\n"
            "سجّل عضوية أولاً من القائمة الرئيسية."
        )
    user_id = user.get("id")
    if not user_id:
        return "تعذر قراءة رقم عضويتك في النظام."

    # جلب الحجوزات الخاصة بالمستخدم
    res = await gizmo_v2.execute(
        "RESERVATIONS_GET_ALL",
        query_params={"UserId": user_id, "Pagination.Limit": 50},
    )
    items = res.get("data") or []
    if not items:
        return "لا توجد لديك حجوزات حالية أو قادمة."

    lines = ["حجوزاتك الحالية / القادمة:\n"]
    for r in items:
        # عدّل أسماء الحقول حسب سكيمة Gizmo عندك
        host_name = r.get("hostName") or f"جهاز #{r.get('hostId')}"
        start = r.get("startTime") or r.get("from")
        end = r.get("endTime") or r.get("to")
        status = r.get("status") or "غير محدد"
        lines.append(f"- {host_name} | من: {start} إلى: {end} | الحالة: {status}")

    return "\n".join(lines)


# --- جهازه الحالي ---

async def uc_customer_view_current_host(phone: str) -> str:
    user = await get_user_by_phone(phone)
    if not user:
        return "لا أجد أي عضوية مرتبطة برقمك حالياً."
    user_id = user.get("id")
    if not user_id:
        return "تعذر قراءة رقم عضويتك في النظام."

    # محاولة استخدام USERS_USAGE_TIME (تعتمد على ما يرجعه عندك)
    res = await gizmo_v2.execute(
        "USERS_USAGE_TIME",
        path_params={"id": user_id},
    )
    # مثال تقريبي: ابحث في الرد عن "currentHost" أو ما يشابهه
    current_host = res.get("currentHost") or res.get("host") or None
    if isinstance(current_host, dict):
        name = current_host.get("name") or f"جهاز #{current_host.get('id')}"
        return f"أنت تلعب حالياً على: {name}."
    elif isinstance(current_host, str):
        return f"أنت تلعب حالياً على: {current_host}."

    # بديل احتياطي: فحص كل الأجهزة لمحاولة معرفة أين مسجّل
    hosts = await gizmo_v2.execute("HOSTS_GET_ALL", query_params={"Pagination.Limit": 200})
    data = hosts.get("data") or []
    for h in data:
        # لو فيه حقل مثل currentUserId أو loggedOnUserId
        current_uid = h.get("currentUserId") or h.get("loggedOnUserId")
        if current_uid == user_id:
            name = h.get("name") or f"جهاز #{h.get('number')}"
            return f"أنت تلعب حالياً على: {name}."

    return "لا يوجد جهاز مسجّل عليك حالياً."


# --- الوقت المتبقي ---

async def uc_customer_view_remaining_time(phone: str) -> str:
    user = await get_user_by_phone(phone)
    if not user:
        return "لا أجد أي عضوية مرتبطة برقمك حالياً."
    user_id = user.get("id")
    if not user_id:
        return "تعذر قراءة رقم عضويتك في النظام."

    res = await gizmo_v2.execute(
        "USERS_USAGE_TIME",
        path_params={"id": user_id},
    )
    # حسب ما يوفره Gizmo، ابحث عن وقت متبقّي أو وقت انتهاء
    # هذه أمثلة افتراضية؛ تحتاج مطابقة مع الـ Swagger عندك
    remaining_sec = res.get("remainingSeconds") or res.get("timeLeftSeconds")
    if remaining_sec:
        minutes = int(remaining_sec // 60)
        return f"الوقت المتبقي في جلستك تقريباً: {minutes} دقيقة."

    expected_end = res.get("expectedEndTime")
    if expected_end:
        try:
            end_dt = datetime.fromisoformat(expected_end)
            now = datetime.utcnow()
            delta = end_dt - now
            if delta.total_seconds() <= 0:
                return "يبدو أن جلستك قاربت على الانتهاء أو انتهت فعلاً."
            minutes = int(delta.total_seconds() // 60)
            return f"الوقت المتبقي في جلستك: حوالي {minutes} دقيقة."
        except Exception:
            pass

    return "لم أتمكن من حساب الوقت المتبقي من بيانات السيرفر حالياً."


# --- حجز جديد بسيط (تجريبي) ---

async def uc_customer_create_reservation_simple(
    phone: str,
    host_id: int,
    start_time: datetime,
    duration_minutes: int = 60,
) -> str:
    """
    هذه الدالة تفترض أنك حصلت على host_id و start_time من حوار سابق مع العميل.
    يمكن لاحقاً أن تجعل Gemini يساعد في فهم هذه المعطيات من نص حر.
    """
    user = await get_user_by_phone(phone)
    if not user:
        return "لا أجد أي عضوية مرتبطة برقمك، لا يمكن إنشاء حجز."
    user_id = user.get("id")
    if not user_id:
        return "تعذر قراءة رقم عضويتك في النظام."

    end_time = start_time + timedelta(minutes=duration_minutes)

    payload = {
        "userId": user_id,
        "hostId": host_id,
        "startTime": start_time.isoformat(),
        "endTime": end_time.isoformat(),
        "note": "WhatsApp Reservation",
    }

    res = await gizmo_v2.execute("RESERVATIONS_CREATE", json_data=payload)
    if "error" in res:
        return "تعذر إنشاء الحجز، تأكد من الوقت والجهاز أو تواصل مع الكاشير."

    return (
        "تم إنشاء حجزك بنجاح ✅\n"
        f"الجهاز: #{host_id}\n"
        f"من: {start_time} إلى: {end_time}"
    )


# =========================
# 2) USE CASES - STAFF
# =========================

async def uc_staff_view_active_sessions() -> str:
    """
    عرض الأجهزة التي عليها لاعب حالياً.
    """
    res = await gizmo_v2.execute("HOSTS_GET_ALL", query_params={"Pagination.Limit": 200})
    hosts = res.get("data") or []
    active: List[str] = []

    for h in hosts:
        state = h.get("state") or h.get("hostState")
        is_user_logged = h.get("isUserLoggedOn", False)
        if is_user_logged or str(state).lower() not in ("1", "free"):
            name = h.get("name") or f"جهاز #{h.get('number')}"
            active.append(name)

    if not active:
        return "لا يوجد حالياً أي جهاز عليه لاعب."

    return "الأجهزة التي عليها لاعب الآن:\n- " + "\n- ".join(active)


async def uc_staff_today_reservations() -> str:
    """
    حجوزات اليوم (عرض مبسط).
    من الأفضل أن تضيف فلاتر تاريخ في query_params حسب ما يدعمه Gizmo.
    """
    # مثال: تجلب آخر 100 حجز وتفلتر بالتاريخ في الكود
    res = await gizmo_v2.execute("RESERVATIONS_GET_ALL", query_params={"Pagination.Limit": 100})
    items = res.get("data") or []
    if not items:
        return "لا توجد حجوزات مسجّلة."

    today = datetime.utcnow().date()
    today_reservations: List[str] = []

    for r in items:
        start = r.get("startTime") or r.get("from")
        host_name = r.get("hostName") or f"جهاز #{r.get('hostId')}"
        user_name = r.get("userName") or f"عضو #{r.get('userId')}"
        try:
            start_dt = datetime.fromisoformat(start)
            if start_dt.date() != today:
                continue
        except Exception:
            continue

        status = r.get("status") or "غير محدد"
        today_reservations.append(
            f"{start_dt.time()} | {host_name} | {user_name} | {status}"
        )

    if not today_reservations:
        return "لا توجد حجوزات لهذا اليوم."

    return "حجوزات اليوم:\n" + "\n".join("- " + x for x in today_reservations)


async def uc_staff_topup_customer_balance(target_phone: str, amount: float) -> str:
    """
    شحن رصيد لعميل معيّن بواسطة الموظف.
    target_phone: رقم العميل (قد يكون مختلف عن رقم الموظف نفسه).
    """
    user = await get_user_by_phone(target_phone)
    if not user:
        return "لم أجد هذا العميل في النظام."

    user_id = user.get("id")
    if not user_id:
        return "تعذر قراءة رقم عضوية العميل."

    # تحتاج أن تضبط الـ payload حسب سكيمة DepositTransaction في Gizmo v2.0
    payload = {
        "userId": user_id,
        "amount": amount,
        # قد تحتاج PaymentMethodId حقيقية من PAYMENT_METHODS_GET
        # مثال تقريبي:
        # "paymentMethodId": 1,
        "comment": "Topup by staff via WhatsApp",
    }

    res = await gizmo_v2.execute("DEPOSITS_ADD", json_data=payload)
    if "error" in res:
        return "تعذر تنفيذ عملية الشحن، تحقق من البيانات أو اجرب لاحقاً."

    return f"تم شحن {amount:.2f} {CURRENCY} للعميل بنجاح."


async def uc_staff_edit_customer_points(target_phone: str, points_delta: int) -> str:
    """
    إضافة أو خصم نقاط لعميل.
    points_delta > 0 لإضافة نقاط، < 0 لخصم نقاط.
    """
    user = await get_user_by_phone(target_phone)
    if not user:
        return "لم أجد هذا العميل في النظام."

    user_id = user.get("id")
    if not user_id:
        return "تعذر قراءة رقم عضوية العميل."

    payload = {
        "userId": user_id,
        "points": points_delta,
        "comment": "Points adjusted by staff via WhatsApp",
    }

    res = await gizmo_v2.execute("POINTS_ADD", json_data=payload)
    if "error" in res:
        return "تعذر تعديل نقاط العميل."

    action = "إضافة" if points_delta > 0 else "خصم"
    return f"تم {action} {abs(points_delta)} نقطة للعميل بنجاح."


# =========================
# 3) USE CASES - MANAGER
# =========================

async def uc_manager_today_income() -> str:
    """
    تقرير دخل اليوم (بناءً على الفواتير).
    """
    res = await gizmo_v2.execute("INVOICES_GET_ALL", query_params={"Pagination.Limit": 500})
    items = res.get("data") or []
    if not items:
        return "لا توجد فواتير مسجّلة."

    today = datetime.utcnow().date()
    total = 0.0
    count = 0

    for inv in items:
        # تحقق من تاريخ الفاتورة
        inv_date_str = inv.get("date") or inv.get("createdOn") or inv.get("createdAt")
        try:
            inv_dt = datetime.fromisoformat(inv_date_str)
        except Exception:
            continue

        if inv_dt.date() != today:
            continue

        # تجاهل الفواتير الملغاة لو لديها status
        status = inv.get("status")
        if status and str(status).lower() in ("void", "cancelled"):
            continue

        amount = inv.get("totalAmount") or inv.get("grandTotal") or inv.get("total") or 0
        try:
            total += float(amount)
            count += 1
        except Exception:
            continue

    return fعدد فواتير اليوم: {count}، إجمالي دخل اليوم: {total:.2f} {CURRENCY}."


async def uc_manager_hosts_utilization() -> str:
    """
    نسبة إشغال الأجهزة الحالية.
    """
    res = await gizmo_v2.execute("HOSTS_GET_ALL", query_params={"Pagination.Limit": 200})
    hosts = res.get("data") or []
    if not hosts:
        return "لا توجد أجهزة مسجّلة في النظام."

    total = len(hosts)
    active = 0

    for h in hosts:
        state = h.get("state") or h.get("hostState")
        is_user_logged = h.get("isUserLoggedOn", False)
        if is_user_logged or str(state).lower() not in ("1", "free"):
            active += 1

    util = (active / total) * 100 if total > 0 else 0
    return (
        f"إجمالي الأجهزة: {total}\n"
        f"الأجهزة المشغولة حالياً: {active}\n"
        f"نسبة الإشغال التقريبية: {util:.1f}%"
    )


async def uc_manager_top_users_last30days(limit: int = 10) -> str:
    """
    أفضل العملاء حسب الإنفاق في آخر 30 يوم (بناءً على الفواتير).
    """
    res = await gizmo_v2.execute("INVOICES_GET_ALL", query_params={"Pagination.Limit": 1000})
    items = res.get("data") or []
    if not items:
        return "لا توجد فواتير كافية لحساب أفضل العملاء."

    now = datetime.utcnow()
    cutoff = now - timedelta(days=30)

    spend_by_user: Dict[int, float] = {}

    for inv in items:
        inv_date_str = inv.get("date") or inv.get("createdOn") or inv.get("createdAt")
        try:
            inv_dt = datetime.fromisoformat(inv_date_str)
        except Exception:
            continue

        if inv_dt < cutoff:
            continue

        user_id = inv.get("userId")
        if not user_id:
            continue

        amount = inv.get("totalAmount") or inv.get("grandTotal") or inv.get("total") or 0
        try:
            spend_by_user[user_id] = spend_by_user.get(user_id, 0.0) + float(amount)
        except Exception:
            continue

    if not spend_by_user:
        return "لا يوجد إنفاق كافٍ لاحتساب أفضل العملاء في آخر 30 يوم."

    # ترتيب من الأعلى للأقل
    top = sorted(spend_by_user.items(), key=lambda x: x[1], reverse=True)[:limit]

    lines = ["أفضل العملاء (آخر 30 يوم):"]
    for user_id, total_spent in top:
        user = await gizmo_v2.execute("USERS_GET_BY_ID", path_params={"id": user_id})
        name = user.get("fullName") or user.get("firstName") or f"User #{user_id}"
        lines.append(f"- {name}: {total_spent:.2f} {CURRENCY}")

    return "\n".join(lines)
