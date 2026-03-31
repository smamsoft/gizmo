# action_map.py

"""
خريطة (Mapping) تربط بين:
- أرقام المنيو (مثل CUS_MENU_1)
- IDs الأزرار من Evolution (مثل BTN_CUS_BAL)
وبين:
- الدور المطلوب (role)
- الصلاحية المطلوبة (permission)
- اسم دالة الـ Use Case التي يجب تنفيذها في الكود

هذه الطبقة تجعل ربط كل الخيارات بـ Gizmo و Use Cases أسهل كثيراً.
"""

ACTIONS = {
    # ========== CUSTOMER: أرقام المنيو الرئيسية ==========
    "CUS_MENU_1": {
        "role": "CUSTOMER",
        "permission": "CHECK_BALANCE",
        "use_case": "uc_customer_check_balance",  # رصيدي
    },
    "CUS_MENU_2": {
        "role": "CUSTOMER",
        "permission": "CHECK_POINTS",
        "use_case": "uc_customer_check_points",   # نقاطي
    },
    "CUS_MENU_3": {
        "role": "CUSTOMER",
        "permission": "LIST_HOSTS_FREE",
        "use_case": "uc_customer_list_hosts_free",  # الأجهزة المتاحة
    },
    "CUS_MENU_4": {
        "role": "CUSTOMER",
        "permission": "LIST_PRODUCTS",
        "use_case": "uc_customer_show_menu",     # المنيو (عرض فقط)
    },
    "CUS_MENU_5": {
        "role": "CUSTOMER",
        "permission": "CHECK_BALANCE",           # أو صلاحية خاصة للشحن لو أحببت
        "use_case": "uc_customer_topup_50",      # شحن رصيد 50
    },
    "CUS_MENU_6": {
        "role": "CUSTOMER",
        "permission": "CHECK_BALANCE",
        "use_case": None,                        # الانتقال لقائمة الخدمات الأخرى
    },
    "CUS_MENU_7": {
        "role": "CUSTOMER",
        "permission": "CHECK_BALANCE",
        "use_case": "uc_customer_register",      # تسجيل عضوية جديدة
    },

    # ========== CUSTOMER: خدمات أخرى (القائمة الثانية) ==========
    "CUS_ADV_1": {
        "role": "CUSTOMER",
        "permission": "CHECK_BALANCE",
        "use_case": "uc_customer_view_reservations",  # حجوزاتي
    },
    "CUS_ADV_2": {
        "role": "CUSTOMER",
        "permission": "CHECK_BALANCE",
        "use_case": "uc_customer_view_current_host_uc",  # جهازي الحالي
    },
    "CUS_ADV_3": {
        "role": "CUSTOMER",
        "permission": "CHECK_BALANCE",
        "use_case": "uc_customer_view_remaining_time_uc",  # الوقت المتبقي
    },

    # ========== CUSTOMER: أزرار Evolution (اختياري) ==========
    "BTN_CUS_BAL": {
        "role": "CUSTOMER",
        "permission": "CHECK_BALANCE",
        "use_case": "uc_customer_check_balance",
    },
    "BTN_CUS_POINTS": {
        "role": "CUSTOMER",
        "permission": "CHECK_POINTS",
        "use_case": "uc_customer_check_points",
    },
    "BTN_CUS_HOSTS": {
        "role": "CUSTOMER",
        "permission": "LIST_HOSTS_FREE",
        "use_case": "uc_customer_list_hosts_free",
    },
    "BTN_CUS_MENU": {
        "role": "CUSTOMER",
        "permission": "LIST_PRODUCTS",
        "use_case": "uc_customer_show_menu",
    },
    "BTN_CUS_TOPUP_50": {
        "role": "CUSTOMER",
        "permission": "CHECK_BALANCE",
        "use_case": "uc_customer_topup_50",
    },
}
