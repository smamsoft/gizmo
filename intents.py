# intents.py

import os
from typing import Dict, Any, List, Optional

from authz import has_permission
from gizmo_tools import (
    get_user_by_phone,
    get_balance_by_phone,
    get_points_by_phone,
    list_products_grouped_for_menu,
    list_free_hosts_simple,
    generate_topup_link_fixed,
    register_user_by_phone,
    uc_customer_view_my_reservations,
    uc_customer_view_current_host_uc,
    uc_customer_view_remaining_time_uc,
)
from session_store import save_menu, load_menu, save_state, load_state

CURRENCY = os.getenv("CURRENCY", "AED")
SHOP_NAME = os.getenv("SHOP_NAME", "HGC GAMING")
SHOP_LOCATION_URL = os.getenv("SHOP_LOCATION_URL", "")
SHOP_CONTACT_PHONE = os.getenv("SHOP_CONTACT_PHONE", "")

MAIN_MENU_STATE = "main"
PRODUCTS_MENU_STATE = "products"
CUSTOMER_ADV_STATE = "cust_adv"


def _welcome_and_menu(role: str, is_registered: bool = True) -> str:
    base = (
        f"أهلاً وسهلاً بك في {SHOP_NAME} 👋\n\n"
        f"موقعنا على الخريطة:\n{SHOP_LOCATION_URL}\n"
        f"للتواصل: {SHOP_CONTACT_PHONE}\n\n"
    )

    note = ""
    if role == "CUSTOMER" and not is_registered:
        note = (
            "📌 ملاحظة: رقمك غير مسجّل كعضو في النظام، "
            "يمكنك التسجيل من الخيار (7) للاستفادة من الرصيد والنقاط.\n\n"
        )

    if role == "CUSTOMER":
        options = (
            "القائمة الرئيسية (العميل) – اكتب رقم الخيار:\n"
            "0) رجوع / إعادة هذه القائمة\n"
            "1) 💰 رصيدي\n"
            "2) ⭐ نقاطي\n"
            "3) 🖥️ الأجهزة المتاحة الآن\n"
            "4) 📋 المنيو (مقسّمة حسب الأقسام)\n"
            "5) 💳 شحن رصيد (50 درهم)\n"
            "6) خدمات أخرى (حجوزات وجلسات)\n"
            "7) 📝 تسجيل عضوية جديدة برقمك\n"
        )
    elif role == "STAFF":
        options = (
            "قائمة الموظف – اكتب رقم الخيار:\n"
            "0) رجوع / إعادة هذه القائمة\n"
            "1) من يلعب الآن؟ (قريباً)\n"
            "2) حجوزات اليوم (قريباً)\n"
            "3) شحن رصيد لعميل (قريباً)\n"
            "4) قفل / فتح جهاز (قريباً)\n"
            "5) خدمات أخرى (قريباً)\n"
        )
    else:  # MANAGER
        options = (
            "قائمة المدير – اكتب رقم الخيار:\n"
            "0) رجوع / إعادة هذه القائمة\n"
            "1) تقرير دخل اليوم (قريباً)\n"
            "2) أفضل 10 عملاء (قريباً)\n"
            "3) نسبة إشغال الأجهزة (قريباً)\n"
            "4) حالة المخزون (قريباً)\n"
            "5) تقارير أخرى (قريباً)\n"
        )

    return base + note + options


async def handle_intent(
    text: str,
    phone: str,
    role: str,
    button_id: Optional[str] = None,
) -> str:
    t = (text or "").strip().lower()
    state = load_state(phone) or MAIN_MENU_STATE

    gizmo_user = await get_user_by_phone(phone)
    is_registered = gizmo_user is not None

    # دعم الأزرار من Evolution: تحويل button_id لأرقام
    if button_id and role == "CUSTOMER":
        if button_id == "BTN_CUS_BAL":
            t = "1"
        elif button_id == "BTN_CUS_POINTS":
            t = "2"
        elif button_id == "BTN_CUS_HOSTS":
            t = "3"
        elif button_id == "BTN_CUS_MENU":
            t = "4"
        elif button_id == "BTN_CUS_TOPUP_50":
            t = "5"

    # 0) رجوع
    if t == "0":
        save_state(phone, MAIN_MENU_STATE)
        return _welcome_and_menu(role, is_registered=is_registered)

    # أرقام
    if t.isdigit():
        num = int(t)

        # الحالة الرئيسية
        if state == MAIN_MENU_STATE:
            if role == "CUSTOMER":
                # 1) رصيدي
                if num == 1:
                    if not has_permission(role, "CHECK_BALANCE"):
                        return "عذراً، ليست لديك صلاحية للاستعلام عن الرصيد."
                    if not is_registered:
                        return (
                            "رقمك غير مسجّل كعضو في النظام، لا يمكن عرض الرصيد.\n"
                            "اختر 7 لتسجيل عضوية جديدة، ثم أرسل 'رصيدي' مرة أخرى.\n\n"
                            + _welcome_and_menu(role, is_registered=is_registered)
                        )
                    bal = await get_balance_by_phone(phone)
                    if bal is None:
                        return "لم أتمكن من إيجاد حسابك في النظام. تأكد أن رقمك مسجّل لدينا."
                    return f"رصيدك الحالي هو {bal:.2f} {CURRENCY}.\n\n" + _welcome_and_menu(role, is_registered=is_registered)

                # 2) نقاطي
                if num == 2:
                    if not has_permission(role, "CHECK_POINTS"):
                        return "عذراً، ليست لديك صلاحية للاستعلام عن النقاط."
                    if not is_registered:
                        return (
                            "رقمك غير مسجّل كعضو في النظام، لا يمكن عرض النقاط.\n"
                            "اختر 7 لتسجيل عضوية جديدة، ثم أرسل 'نقاطي' مرة أخرى.\n\n"
                            + _welcome_and_menu(role, is_registered=is_registered)
                        )
                    pts = await get_points_by_phone(phone)
                    if pts is None:
                        return "لم أتمكن من إيجاد نقاطك حالياً. تأكد أن رقمك مسجّل لدينا."
                    return f"لديك حالياً {pts} نقطة ولاء.\n\n" + _welcome_and_menu(role, is_registered=is_registered)

                # 3) الأجهزة المتاحة
                if num == 3:
                    if not has_permission(role, "LIST_HOSTS_FREE"):
                        return "عذراً، ليست لديك صلاحية لرؤية حالة الأجهزة."
                    try:
                        hosts = await list_free_hosts_simple()
                    except Exception as e:
                        print("### ERROR list_free_hosts_simple:", e)
                        return "تعذر جلب حالة الأجهزة من Gizmo حالياً، حاول لاحقاً."
                    if not hosts:
                        return "لا توجد أجهزة متاحة حالياً.\n\n" + _welcome_and_menu(role, is_registered=is_registered)
                    nums = [str(h.get("number") or h.get("name")) for h in hosts]
                    return (
                        "الأجهزة المتاحة الآن: " + ", ".join(nums) + ".\n\n"
                        + _welcome_and_menu(role, is_registered=is_registered)
                    )

                # 4) المنيو (مقسّمة حسب الأقسام)
                if num == 4:
                    if not has_permission(role, "LIST_PRODUCTS"):
                        return "عذراً، ليست لديك صلاحية لرؤية قائمة المنتجات."
                    save_state(phone, PRODUCTS_MENU_STATE)
                    return await _show_customer_menu(phone)

                # 5) شحن رصيد
                if num == 5:
                    msg = await generate_topup_link_fixed(phone, 50.0)
                    return msg + "\n\n" + _welcome_and_menu(role, is_registered=is_registered)

                # 6) خدمات أخرى
                if num == 6:
                    save_state(phone, CUSTOMER_ADV_STATE)
                    return (
                        "خدمات أخرى (اكتب رقم الخيار):\n"
                        "0) رجوع للقائمة الرئيسية\n"
                        "1) عرض حجوزاتي الحالية / القادمة\n"
                        "2) معرفة على أي جهاز ألعب الآن\n"
                        "3) معرفة الوقت المتبقي في جلستي\n"
                    )

                # 7) تسجيل عضوية جديدة
                if num == 7:
                    msg = await register_user_by_phone(phone)
                    return msg + "\n\n" + _welcome_and_menu(role, is_registered=True)

                return "الرجاء اختيار رقم من 0 إلى 7.\n\n" + _welcome_and_menu(role, is_registered=is_registered)

            # STAFF / MANAGER لم يُفعّلوا بعد
            return "هذا الخيار لم يتم تفعيله بعد، سيتم إضافته قريباً.\n\n" + _welcome_and_menu(role, is_registered=is_registered)

        # خدمات أخرى للعميل
        if state == CUSTOMER_ADV_STATE and role == "CUSTOMER":
            if num == 0:
                save_state(phone, MAIN_MENU_STATE)
                return _welcome_and_menu(role, is_registered=is_registered)

            if num == 1:
                msg = await uc_customer_view_my_reservations(phone)
                return msg + "\n\n" + _welcome_and_menu(role, is_registered=is_registered)

            if num == 2:
                msg = await uc_customer_view_current_host_uc(phone)
                return msg + "\n\n" + _welcome_and_menu(role, is_registered=is_registered)

            if num == 3:
                msg = await uc_customer_view_remaining_time_uc(phone)
                return msg + "\n\n" + _welcome_and_menu(role, is_registered=is_registered)

            return (
                "الرجاء اختيار رقم من 0 إلى 3 في قائمة الخدمات الأخرى.\n\n"
                "0) رجوع\n"
                "1) حجوزاتي\n"
                "2) جهازي الحالي\n"
                "3) الوقت المتبقي\n"
            )

        # منيو المنتجات: مستوى المجموعات وداخل المجموعة
        if state == PRODUCTS_MENU_STATE:
            menu = load_menu(phone)
            if not menu:
                save_state(phone, MAIN_MENU_STATE)
                return (
                    "لا توجد قائمة منتجات حالية. اكتب 4 من القائمة الرئيسية لعرض المنيو.\n\n"
                    + _welcome_and_menu(role, is_registered=is_registered)
                )

            mtype = menu.get("type")

            # اختيار قسم
            if mtype == "product_groups":
                groups: List[str] = menu.get("groups") or []
                idx = num - 1
                if idx < 0 or idx >= len(groups):
                    return "الرقم غير موجود في قائمة الأقسام. اكتب 0 للرجوع أو 4 لإعادة عرض المنيو."

                chosen_group = groups[idx]
                grouped_products: Dict[str, List[Dict[str, Any]]] = menu.get("grouped_products") or {}
                products = grouped_products.get(chosen_group) or []
                if not products:
                    return f"لا توجد منتجات في القسم {chosen_group} حالياً."

                lines = [f"منتجات قسم {chosen_group} (اكتب رقم المنتج للاختيار أو 0 للرجوع):\n"]
                flat_items: List[Dict[str, Any]] = []
                p_idx = 1
                for p in products:
                    if not isinstance(p, dict):
                        continue
                    name = p.get("name") or p.get("description") or "منتج"
                    price = p.get("price", 0)
                    lines.append(f"{p_idx}) {name} - {price} {CURRENCY}")
                    flat_items.append({
                        "id": p.get("id"),
                        "name": name,
                        "price": price,
                        "group": chosen_group,
                    })
                    p_idx += 1

                if not flat_items:
                    return f"لا توجد منتجات قابلة للعرض في القسم {chosen_group}."

                save_menu(phone, "products_in_group", {"type": "products_in_group", "items": flat_items})
                return "\n".join(lines).strip()

            # اختيار منتج داخل قسم
            if mtype == "products_in_group":
                items: List[Dict[str, Any]] = menu.get("items") or []
                idx = num - 1
                if idx < 0 or idx >= len(items):
                    return "الرقم غير موجود في هذه القائمة. اكتب 0 للرجوع أو 4 لإعادة عرض المنيو."

                chosen = items[idx]
                return await _handle_product_selection(phone, chosen, role)

            # نوع غير معروف
            save_state(phone, MAIN_MENU_STATE)
            return _welcome_and_menu(role, is_registered=is_registered)

    # أوامر نصية مكافئة للأرقام
    if any(k in t for k in ["رصيدي", "رصيد", "balance", "credit"]):
        if not has_permission(role, "CHECK_BALANCE"):
            return "عذراً، ليست لديك صلاحية للاستعلام عن الرصيد."
        if not is_registered and role == "CUSTOMER":
            return (
                "رقمك غير مسجّل كعضو في النظام، لا يمكن عرض الرصيد.\n"
                "اختر 7 لتسجيل عضوية جديدة، ثم أرسل 'رصيدي' مرة أخرى.\n\n"
                + _welcome_and_menu(role, is_registered=is_registered)
            )
        bal = await get_balance_by_phone(phone)
        if bal is None:
            return "لم أتمكن من إيجاد حسابك في النظام. تأكد أن رقمك مسجّل لدينا."
        return f"رصيدك الحالي هو {bal:.2f} {CURRENCY}.\n\n" + _welcome_and_menu(role, is_registered=is_registered)

    if any(k in t for k in ["نقاطي", "نقاط", "points"]):
        if not has_permission(role, "CHECK_POINTS"):
            return "عذراً، ليست لديك صلاحية للاستعلام عن النقاط."
        if not is_registered and role == "CUSTOMER":
            return (
                "رقمك غير مسجّل كعضو في النظام، لا يمكن عرض النقاط.\n"
                "اختر 7 لتسجيل عضوية جديدة، ثم أرسل 'نقاطي' مرة أخرى.\n\n"
                + _welcome_and_menu(role, is_registered=is_registered)
            )
        pts = await get_points_by_phone(phone)
        if pts is None:
            return "لم أتمكن من إيجاد نقاطك حالياً. تأكد أن رقمك مسجّل لدينا."
        return f"لديك حالياً {pts} نقطة ولاء.\n\n" + _welcome_and_menu(role, is_registered=is_registered)

    if any(k in t for k in ["الأجهزة المتاحة", "الاجهزه المتاحه", "الاجهزة المتاحة", "hosts"]):
        if not has_permission(role, "LIST_HOSTS_FREE"):
            return "عذراً، ليست لديك صلاحية لرؤية حالة الأجهزة."
        try:
            hosts = await list_free_hosts_simple()
        except Exception as e:
            print("### ERROR list_free_hosts_simple:", e)
            return "تعذر جلب حالة الأجهزة من Gizmo حالياً، حاول لاحقاً."
        if not hosts:
            return "لا توجد أجهزة متاحة حالياً.\n\n" + _welcome_and_menu(role, is_registered=is_registered)
        nums = [str(h.get("number") or h.get("name")) for h in hosts]
        return (
            "الأجهزة المتاحة الآن: " + ", ".join(nums) + ".\n\n"
            + _welcome_and_menu(role, is_registered=is_registered)
        )

    if any(k in t for k in ["المنيو", "المنتجات", "menu", "products"]):
        if not has_permission(role, "LIST_PRODUCTS"):
            return "عذراً، ليست لديك صلاحية لرؤية قائمة المنتجات."
        save_state(phone, PRODUCTS_MENU_STATE)
        return await _show_customer_menu(phone)

    # أي شيء آخر → عرض الترحيب + القائمة الرئيسية
    save_state(phone, MAIN_MENU_STATE)
    return _welcome_and_menu(role, is_registered=is_registered)


async def _show_customer_menu(phone: str) -> str:
    """
    الخطوة الأولى: قائمة الأقسام (Groups) حسب Gizmo.
    """
    try:
        grouped = await list_products_grouped_for_menu()
    except Exception as e:
        print("### ERROR list_products_grouped_for_menu:", e)
        return "تعذر جلب قائمة المنتجات من Gizmo حالياً، حاول لاحقاً."

    if not grouped:
        return "حالياً لا توجد منتجات مسجّلة في النظام."

    group_names = [g for g, items in grouped.items() if items]
    if not group_names:
        return "حالياً لا توجد مجموعات منتجات قابلة للعرض."

    menu_payload = {
        "type": "product_groups",
        "groups": group_names,
        "grouped_products": grouped,
    }
    save_menu(phone, "product_groups", menu_payload)

    lines = ["أقسام المنتجات (اكتب رقم القسم للاختيار أو 0 للرجوع):\n"]
    for idx, gname in enumerate(group_names, start=1):
        lines.append(f"{idx}) {gname}")

    return "\n".join(lines).strip()


async def _handle_product_selection(phone: str, product: Dict[str, Any], role: str) -> str:
    name = product.get("name", "منتج")
    price = product.get("price", 0)
    group = product.get("group", "")

    return (
        f"اخترت المنتج:\n"
        f"{name} ({group}) بسعر {price} {CURRENCY}"
    )