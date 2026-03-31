# button_map.py

BUTTON_ACTIONS = {
    # ========= CUSTOMER =========
    "BTN_CUS_BAL": {
        "role": "CUSTOMER",
        "permission": "CHECK_BALANCE",
        "action": "customer_check_balance",
    },
    "BTN_CUS_POINTS": {
        "role": "CUSTOMER",
        "permission": "CHECK_POINTS",
        "action": "customer_check_points",
    },
    "BTN_CUS_HOSTS": {
        "role": "CUSTOMER",
        "permission": "LIST_HOSTS_FREE",
        "action": "customer_list_hosts",
    },
    "BTN_CUS_MENU": {
        "role": "CUSTOMER",
        "permission": "LIST_PRODUCTS",
        "action": "customer_show_menu",
    },
    "BTN_CUS_TOPUP_50": {
        "role": "CUSTOMER",
        "permission": "CHECK_BALANCE",  # أو صلاحية خاصة لو حبيت
        "action": "customer_topup_50",
    },

    # ========= STAFF =========
    "BTN_STF_ACTIVE_SESS": {
        "role": "STAFF",
        "permission": "VIEW_ACTIVE_SESSIONS",
        "action": "staff_active_sessions",
    },
    "BTN_STF_TODAY_RES": {
        "role": "STAFF",
        "permission": "MANAGE_RESERVATIONS",
        "action": "staff_today_reservations",
    },
    # ... تكمل باقي أزرار الموظف

    # ========= MANAGER =========
    "BTN_AD_Z_TODAY": {
        "role": "MANAGER",
        "permission": "VIEW_REPORTS_BASIC",  # أو VIEW_REPORTS_FINANCIAL
        "action": "manager_today_income",
    },
    "BTN_AD_HOSTS": {
        "role": "MANAGER",
        "permission": "VIEW_HOSTS_STATUS",
        "action": "manager_hosts_status",
    },
    # ... تكمل باقي أزرار المدير
}
