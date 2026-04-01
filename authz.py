# authz.py

import os
from typing import List

# ==============
# إعداد الأدوار
# ==============

# رقم المدير (من .env)
ADMIN_PHONE = os.getenv("ADMIN_PHONE", "").strip()

# أرقام الموظفين (مفصولة بفاصلة في .env)
# مثال: STAFF_PHONES=9715xxxxxxx,9715yyyyyyy
STAFF_PHONES: List[str] = [
    p.strip() for p in os.getenv("STAFF_PHONES", "").split(",") if p.strip()
]

ROLES = ["CUSTOMER", "STAFF", "MANAGER"]

# ==========================
# Matrix الصلاحيات لكل دور
# ==========================

ROLE_PERMISSIONS = {
    # 👤 عميل عادي عبر الواتساب
    "CUSTOMER": [
        # استعلامات أساسية
        "CHECK_BALANCE",        # يسأل عن رصيده
        "CHECK_POINTS",         # يسأل عن نقاطه
        "LIST_PRODUCTS",        # المنيو / المنتجات
        "LIST_HOSTS_FREE",      # الأجهزة المتاحة

        # مرتبطة بحسابه فقط
        "MAKE_SELF_RESERVATION",  # يحجز لنفسه (عبر واتساب مستقبلاً)
        "VIEW_SELF_SESSIONS",     # يشوف حجوزاته / جلسته الحالية / جهازه / الوقت المتبقي
    ],

    # 🧑‍💼 موظف الكاشير / المشرف
    "STAFF": [
        # كل ما يملكه العميل
        "CHECK_BALANCE",
        "CHECK_POINTS",
        "LIST_PRODUCTS",
        "LIST_HOSTS_FREE",
        "MAKE_SELF_RESERVATION",
        "VIEW_SELF_SESSIONS",

        # صلاحيات تشغيلية على العملاء
        "MANAGE_USER_BALANCE",   # شحن / سحب رصيد
        "MANAGE_USER_POINTS",    # إضافة / سحب نقاط
        "MANAGE_USER_SESSIONS",  # تشغيل / إيقاف جلسة
        "MANAGE_RESERVATIONS",   # إنشاء / تعديل / إلغاء حجوزات
        "VIEW_ACTIVE_SESSIONS",  # من يلعب الآن
        "VIEW_USERS_BASIC",      # البحث عن عميل / عرض بياناته الأساسية

        # تقارير بسيطة
        "VIEW_REPORTS_BASIC",    # تقارير تشغيلية مبسّطة

        # إدارة الأجهزة
        "VIEW_HOSTS_STATUS",     # حالات الأجهزة
        "CONTROL_HOST_LOCK",     # قفل / فتح جهاز (لو فعّلتها من Gizmo)
    ],

    # 👑 المدير / صاحب المحل
    "MANAGER": [
        "*",  # كل الصلاحيات، بما فيها المالية والمخزون والتقارير الكاملة
    ],
}

# ==========================
# دوال مساعدة
# ==========================

def normalize_phone(p: str) -> str:
    """
    تطبيع رقم الهاتف: إزالة '+' والمسافات.
    مثال: "+971 50 123 4567" -> "971501234567"
    """
    return (p or "").replace("+", "").replace(" ", "").strip()


def get_role_for_phone(phone: str) -> str:
    """
    يحدد الدور (Role) بناءً على رقم الواتساب:
    - ADMIN_PHONE من .env => MANAGER
    - STAFF_PHONES من .env => STAFF
    - غير ذلك => CUSTOMER
    """
    phone_n = normalize_phone(phone)
    admin_n = normalize_phone(ADMIN_PHONE)
    staff_n = [normalize_phone(p) for p in STAFF_PHONES]

    if admin_n and phone_n == admin_n:
        return "MANAGER"

    if phone_n in staff_n:
        return "STAFF"

    return "CUSTOMER"


def has_permission(role: str, permission: str) -> bool:
    """
    يتحقق إن كان الدور لديه صلاحية استخدام Intent / Use Case معيّن.
    - لو الدور MANAGER وعنده "*" -> دائماً مسموح.
    - غير ذلك، يتأكد أن permission موجودة في ROLE_PERMISSIONS.
    """
    perms = ROLE_PERMISSIONS.get(role.upper(), [])
    return "*" in perms or permission in perms
