# gizmo_endpoints.py

GIZMO_V2 = {
    # ========== 1. المستخدمون (Users) ==========
    "USERS_GET_ALL": ("GET", "/api/v2.0/users"),
    "USERS_CREATE": ("POST", "/api/v2.0/users"),
    "USERS_UPDATE": ("PUT", "/api/v2.0/users"),
    "USERS_GET_BY_ID": ("GET", "/api/v2.0/users/{id}"),
    "USERS_DELETE": ("DELETE", "/api/v2.0/users/{id}"),
    "USERS_ATTR_GET": ("GET", "/api/v2.0/users/{id}/attributes"),
    "USERS_ATTR_ADD": ("POST", "/api/v2.0/users/{id}/attributes"),
    "USERS_NOTES_GET": ("GET", "/api/v2.0/users/{id}/notes"),
    "USERS_NOTES_ADD": ("POST", "/api/v2.0/users/{id}/notes"),
    "USERS_PICTURE_GET": ("GET", "/api/v2.0/users/{id}/picture"),
    "USERS_PICTURE_UPDATE": ("PUT", "/api/v2.0/users/{id}/picture"),
    "USERS_USAGE_TIME": ("GET", "/api/v2.0/users/{id}/userusagetime"),

    # ========== 2. مجموعات المستخدمين (User Groups) ==========
    "USERGROUPS_GET_ALL": ("GET", "/api/v2.0/usergroups"),
    "USERGROUPS_CREATE": ("POST", "/api/v2.0/usergroups"),
    "USERGROUPS_UPDATE": ("PUT", "/api/v2.0/usergroups"),
    "USERGROUPS_GET_BY_ID": ("GET", "/api/v2.0/usergroups/{id}"),

    # ========== 3. الأجهزة (Hosts) ==========
    "HOSTS_GET_ALL": ("GET", "/api/v2.0/hosts"),
    "HOSTS_CREATE": ("POST", "/api/v2.0/hosts"),
    "HOSTS_UPDATE": ("PUT", "/api/v2.0/hosts"),
    "HOSTS_GET_BY_ID": ("GET", "/api/v2.0/hosts/{id}"),
    "HOSTS_DELETE": ("DELETE", "/api/v2.0/hosts/{id}"),
    "HOSTS_GET_DEVICES": ("GET", "/api/v2.0/hosts/{id}/hostdevices"),

    # ========== 4. مجموعات الأجهزة ==========
    "HOSTGROUPS_GET_ALL": ("GET", "/api/v2.0/hostgroups"),
    "HOSTGROUPS_GET_BY_ID": ("GET", "/api/v2.0/hostgroups/{id}"),
    "HOSTLAYOUTS_GET_ALL": ("GET", "/api/v2.0/hostlayoutgroups"),

    # ========== 5. التطبيقات والألعاب ==========
    "APPS_GET_ALL": ("GET", "/api/v2.0/applications"),
    "APPS_CREATE": ("POST", "/api/v2.0/applications"),
    "APPS_GET_BY_ID": ("GET", "/api/v2.0/applications/{id}"),
    "APP_CATEGORIES_GET": ("GET", "/api/v2.0/applicationcategories"),
    "APP_GROUPS_GET": ("GET", "/api/v2.0/applicationgroups"),
    "APP_EXECUTABLES_GET": ("GET", "/api/v2.0/applicationexecutables"),
    "APP_LICENSES_GET": ("GET", "/api/v2.0/applicationlicenses"),

    # ========== 6. الموظفين والورديات ==========
    "OPERATORS_GET_ALL": ("GET", "/api/v2.0/operators"),
    "OPERATORS_CURRENT": ("GET", "/api/v2.0/operators/current"),
    "SHIFT_START_CURRENT": ("POST", "/api/v2.0/operators/current/shift/start"),
    "SHIFT_ACTIVE_GET": ("GET", "/api/v2.0/operators/current/shift/active"),
    "SHIFT_ACTIVE_EXPECTED": ("GET", "/api/v2.0/operators/current/shift/active/expected"),
    "SHIFT_ACTIVE_END": ("POST", "/api/v2.0/operators/current/shift/active/end"),
    "SHIFT_ACTIVE_LOCK": ("PUT", "/api/v2.0/operators/current/shift/active/lock"),
    "SHIFT_ACTIVE_UNLOCK": ("PUT", "/api/v2.0/operators/current/shift/active/unlock"),
    "SHIFTS_HISTORY_GET": ("GET", "/api/v2.0/shift"),
    "REGISTERS_GET_ALL": ("GET", "/api/v2.0/registers"),

    # ========== 7. الطلبات والمنتجات ==========
    "ORDERS_GET_ALL": ("GET", "/api/v2.0/orders"),
    "ORDERS_GET_BY_ID": ("GET", "/api/v2.0/orders/{id}"),
    "ORDERS_INVOICE": ("POST", "/api/v2.0/orders/{id}/invoice"),
    "ORDERS_COMPLETE": ("PUT", "/api/v2.0/orders/{id}/complete"),
    "ORDERS_CANCEL": ("PUT", "/api/v2.0/orders/{id}/cancel"),
    "ORDERS_DELIVERED_GET": ("GET", "/api/v2.0/orders/{id}/delivered"),
    "ORDERS_DELIVERED_SET": ("PUT", "/api/v2.0/orders/{id}/delivered"),
    "PRODUCTS_GET_ALL": ("GET", "/api/v2.0/products"),
    "PRODUCTS_GET_BY_ID": ("GET", "/api/v2.0/products/{id}"),
    "PRODUCTS_STOCK_GET": ("GET", "/api/v2.0/productsstock"),
    "STOCK_TRANSACTIONS_GET": ("GET", "/api/v2.0/stocktransactions"),

    # ========== 8. الفواتير والمدفوعات ==========
    "INVOICES_GET_ALL": ("GET", "/api/v2.0/invoices"),
    "INVOICES_GET_BY_ID": ("GET", "/api/v2.0/invoices/{id}"),
    "INVOICES_VOID": ("PUT", "/api/v2.0/invoices/{id}/void"),
    "INVOICE_PAYMENTS_GET": ("GET", "/api/v2.0/invoicepayments"),
    "INVOICE_PAYMENTS_ADD": ("POST", "/api/v2.0/invoicepayments"),
    "PAYMENT_INTENT_GET": ("GET", "/api/v2.0/paymentintent"),
    "PAYMENT_INTENT_DEPOSIT": ("POST", "/api/v2.0/paymentintent/deposit"),
    "PAYMENT_METHODS_GET": ("GET", "/api/v2.0/paymentmethods"),
    "BILLING_PROFILES_GET": ("GET", "/api/v2.0/billingprofiles"),

    # ========== 9. الأرصدة والنقاط ==========
    "DEPOSITS_GET_ALL": ("GET", "/api/v2.0/deposittransactions"),
    "DEPOSITS_ADD": ("POST", "/api/v2.0/deposittransactions"),
    "POINTS_GET_ALL": ("GET", "/api/v2.0/pointstransactions"),
    "POINTS_ADD": ("POST", "/api/v2.0/pointstransactions"),

    # ========== 10. طلبات المساعدة ==========
    "ASSISTANCE_GET_ALL": ("GET", "/api/v2.0/assistancerequest"),
    "ASSISTANCE_CREATE_USER": ("POST", "/api/user/v2.0/assistancerequest"),
    "ASSISTANCE_CHECK_PENDING": ("GET", "/api/user/v2.0/assistancerequest/pending/any"),
    "ASSISTANCE_ACCEPT": ("PUT", "/api/v2.0/assistancerequest/{id}/accept"),
    "ASSISTANCE_REJECT": ("PUT", "/api/v2.0/assistancerequest/{id}/reject"),

    # ========== 11. المصادقة والتحقق ==========
    "AUTH_TOKEN_OPERATOR": ("GET", "/api/v2.0/auth/accesstoken"),
    "AUTH_TOKEN_USER": ("GET", "/api/user/v2.0/auth/accesstoken"),
    "VERIFY_SMS_START": ("POST", "/api/v2.0/verifications/mobilephone/{userId}/{mobilePhoneNumber}"),
    "VERIFY_SMS_COMPLETE": ("POST", "/api/v2.0/verifications/mobilephone/{token}/{confirmationCode}/complete"),

    # ========== 12. الحجوزات ==========
    "RESERVATIONS_GET_ALL": ("GET", "/api/v2.0/reservations"),
    "RESERVATIONS_CREATE": ("POST", "/api/v2.0/reservations"),
    "RESERVATIONS_UPDATE": ("PUT", "/api/v2.0/reservations"),
    "RESERVATIONS_GET_BY_ID": ("GET", "/api/v2.0/reservations/{id}"),
    "RESERVATIONS_DELETE": ("DELETE", "/api/v2.0/reservations/{id}"),
}
