# button_actions.py

"""
خريطة الأزرار (Buttons) القادمة من Evolution WhatsApp
تربط بين:
- button_id من Evolution (مثل BTN_CUS_BAL)
- الدور المطلوب (CUSTOMER / STAFF / MANAGER)
- الصلاحية المطلوبة (permission)
- اسم دالة الـ Use Case التي يجب تنفيذها

يتم استخدام هذه الخريطة في worker.py:
- لو وصل button_id، نبحث عنه هنا
- نتأكد من الدور والصلاحية
- ننفّذ الـ use_case المناسب من use_cases.py
"""

BUTTON_ACTIONS = {
    # =======================
    # 1) CUSTOMER BUTTONS
    # =======================

    # رصيدي
    "BTN_CUS_BAL": {
        "role": "CUSTOMER",
        "permission": "CHECK_BALANCE",
        "use_case": "uc_customer_check_balance",
    },

    # نقاطي
    "BTN_CUS_POINTS": {
        "role": "CUSTOMER",
        "permission": "CHECK_POINTS",
        "use_case": "uc_customer_check_points",
    },

    # الأجهزة المتاحة الآن
    "BTN_CUS_HOSTS": {
        "role": "CUSTOMER",
        "permission": "LIST_HOSTS_FREE",
        "use_case": "uc_customer_list_hosts_free",
    },

    # المنيو (عرض الأقسام والمنتجات)
    "BTN_CUS_MENU": {
        "role": "CUSTOMER",
        "permission": "LIST_PRODUCTS",
        "use_case": "uc_customer_show_menu",
    },

    # شحن رصيد 50 درهم
    "BTN_CUS_TOPUP_50": {
        "role": "CUSTOMER",
        "permission": "CHECK_BALANCE",  # أو MANAGE_USER_BALANCE لو حاب تشدد
        "use_case": "uc_customer_topup_50",
    },

    # تسجيل عضوية جديدة برقم الواتساب
    "BTN_CUS_REGISTER": {
        "role": "CUSTOMER",
        "permission": "CHECK_BALANCE",  # أو صلاحية خاصة للتسجيل لو أردت
        "use_case": "uc_customer_register",
    },

    # حجوزاتي
    "BTN_CUS_MY_RES": {
        "role": "CUSTOMER",
        "permission": "VIEW_SELF_SESSIONS",  # أو صلاحية جديدة مثل VIEW_SELF_RESERVATIONS
        "use_case": "uc_customer_view_reservations",
    },

    # جهازي الحالي
    "BTN_CUS_CUR_HOST": {
        "role": "CUSTOMER",
        "permission": "VIEW_SELF_SESSIONS",
        "use_case": "uc_customer_view_current_host",
    },

    # الوقت المتبقي
    "BTN_CUS_TIME_LEFT": {
        "role": "CUSTOMER",
        "permission": "VIEW_SELF_SESSIONS",
        "_case": "uc_customer_view_remaining_time",
    },

    # يمكن لاحقاً إضافة زر لحجز جديد بسيط:
    # "BTN_CUS_NEW_RES": {
    #     "role": "CUSTOMER",
    #     "permission": "MAKE_SELF_RESERVATION",
    #     "use_case": "uc_customer_create_reservation_simple",
    # },

    # =======================
    # 2) STAFF BUTTONS
    # =======================

    # من يلعب الآن؟
    "BTN_STF_ACTIVE_SESS {
        "role": "STAFF",
        "permission": "VIEW_ACTIVE_SESSIONS",
        "use_case": "uc_staff_view_active_sessions",
    },

    # حجوزات اليوم
    "BTN_STF_TODAY_RES": {
        "role": "STAFF",
        "permission": "MANAGE_RESERVATIONS",
        "use_case": "uc_staff_today_reservations",
    },

    # شحن رصيد لعميل (ستحتاج حوار إضافي لرقم العميل والمبلغ)
    # يمكن أن يكون هذا الزر فقط لبدء حوار، والـ use_case يعطي تعليمات للموظف
    "BTN_STF_TOPUP_CUSTOM": {
        "role": "STAFF",
        "permission": "MANAGE_USER_BALANCE",
        "use_case": "uc_staff_topup_customer_balance",  # تتوقع target_phone + amount من الحوار
    },

    # تعديل نقاط عميل (إضافة / خصم)
    "BTN_STF_EDIT_POINTS": {
        "role": "STAFF",
        "permission": "MANAGE_USER_POINTS",
        "use_case": "uc_staff_edit_customer_points",  # تتوقع target_phone + points_delta
    },

    # يمكن إضافة أزرار أخرى للموظف مثل التحكم بالأجهزة، حسب ما توفره Gizmo

    # =======================
    # 3) MANAGER BUTTONS
    # =======================

    # دخل اليوم
    "BTN_AD_Z_TODAY": {
        "role": "MANAGER",
        "permission": "VIEW_REPORTS_BASIC",  # أو VIEW_REPORTS_FINANCIAL لو عرفتها
        "use_case": "uc_manager_today_income",
    },

    # نسبة إشغال الأجهزة الحالية
    "BTN_AD_HOSTS_UTIL": {
        "role": "MANAGER",
        "permission": "VIEW_HOSTS_STATUS",
        "use_case": "uc_manager_hosts_utilization",
    },

    # أفضل العملاء آخر 30 يوم
    "BTN_AD_TOP_USERS_30D": {
        "role": "MANAGER",
        "permission": "VIEW_REPORTS_BASIC",
        "use_case": "uc_manager_top_users_last30days",
    },

    # يمكنك إضافة أزرار لتقارير أخرى (دخل أمس، آخر 7 أيام، حركة المخزون... إلخ)
}
