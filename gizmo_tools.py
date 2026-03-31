# gizmo_tools.py

import os
from typing import Dict, Any, List, Optional
import logging

import redis

# الاستغناء عن gizmo_client القديم واستخدام الكلاينت الجديد v2.0
from gizmo_client import gizmo_v2
from payment_engine import generate_wallet_topup_link  

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GIZMO_TOOLS")

CURRENCY = os.getenv("CURRENCY", "AED")
REDIS_URI = os.getenv("REDIS_URI", "redis://smam_redis:6379/0")
_r = redis.from_url(REDIS_URI, decode_responses=True)


# ================ المستخدمون (Gizmo v2.0) ================

async def get_user_by_phone(phone: str) -> Optional[Dict[str, Any]]:
    """
    يحاول إيجاد عميل Gizmo بناءً على رقم الواتساب باستخدام Gizmo v2.0.
    نبحث في القائمة باستخدام Pagination.Limit و Username filter.
    """
    clean_phone = (phone or "").replace("+", "").replace(" ", "").strip()
    if not clean_phone:
        return None
        
    try:
        # البحث عن العميل باستخدام الـ Username
        res = await gizmo_v2.execute(
            "USERS_GET_ALL", 
            query_params={"Username": clean_phone, "Pagination.Limit": 1}
        )
        
        if isinstance(res, dict) and "data" in res:
            users = res["data"]
            if users and len(users) > 0:
                return users[0]  # إرجاع أول مستخدم مطابق
    except Exception as e:
        logger.error(f"Error finding user {clean_phone}: {e}")
        
    return None


async def register_user_by_phone(phone: str) -> str:
    """
    تسجيل عميل جديد في Gizmo v2.0 إذا لم يكن مسجّلاً.
    يجب أن يتوافق الـ Payload مع UserModelCreate.
    """
    clean_phone = (phone or "").replace("+", "").replace(" ", "").strip()
    if not clean_phone:
        return "رقم الهاتف غير صالح."

    existing = await get_user_by_phone(clean_phone)
    if existing:
        username = existing.get("username") or existing.get("firstName") or clean_phone
        return f"رقمك مسجّل مسبقاً كعضو ({username})، يمكنك استخدام خدمات الرصيد والنقاط."

    # الهيكلية الصحيحة للإصدار 2.0 (أول حرف Capital)
    payload = {
        "Username": clean_phone,
        "FirstName": "عميل",
        "LastName": "واتساب",
        "MobilePhone": clean_phone,
        "UserGroupId": 1  # تأكد أن 1 هو رقم المجموعة الافتراضية (Guests/Customers) في نظامك
    }

    try:
        res = await gizmo_v2.execute("USERS_CREATE", json_data=payload)
        
        if isinstance(res, dict) and "id" in res:
            new_id = res["id"]
            return (
                "تم تسجيلك كعضو جديد في النظام ✅\n"
                f"رقم العضوية الخاص بك: {new_id}\n"
                "يمكنك الآن استخدام أوامر: رصيدي، نقاطي، وغيرها."
            )
        elif isinstance(res, dict) and "error" in res:
            logger.error(f"Register Error Details: {res.get('details')}")
            return "تعذر إنشاء الحساب، يبدو أن هناك خطأ في إعدادات المجموعات (UserGroups) في الخادم."
            
    except Exception as e:
        logger.error(f"Exception during register_user_by_phone: {e}")
        return "تعذر الاتصال بالسيرفر لإتمام التسجيل، حاول لاحقاً."

    return "تمت محاولة التسجيل، لكن لم أستطع تأكيد إنشاء الحساب. تحقق مع الكاشير."


# ================ الرصيد والنقاط (Gizmo v2.0) ================

async def get_balance_by_phone(phone: str) -> Optional[float]:
    user = await get_user_by_phone(phone)
    if not user:
        return None

    # في إصدار 2.0، يمكن أن يكون الرصيد داخل تفاصيل المستخدم
    user_id = user.get("id")
    if not user_id:
        return None
        
    try:
        # جلب التفاصيل الإضافية (مثل الرصيد) إذا لم تكن موجودة في البحث الأولي
        # يمكن استخدام مسار جلب الرصيد المباشر إذا كان متاحاً في v2.0
        # أو الاعتماد على حقل Balance من نموذج المستخدم
        res = await gizmo_v2.execute("USERS_GET_BY_ID", path_params={"id": user_id})
        
        if isinstance(res, dict) and "error" not in res:
            # افتراض أن حقل الرصيد هو 'balance' أو 'cashBalance' في النموذج
            bal = res.get("balance") or res.get("cashBalance") or res.get("money", 0.0)
            return float(bal)
            
    except Exception as e:
        logger.error(f"Error fetching balance for user {user_id}: {e}")
        
    return 0.0


async def get_points_by_phone(phone: str) -> Optional[int]:
    user = await get_user_by_phone(phone)
    if not user:
        return None

    user_id = user.get("id")
    if not user_id:
        return None
        
    try:
        res = await gizmo_v2.execute("USERS_GET_BY_ID", path_params={"id": user_id})
        
        if isinstance(res, dict) and "error" not in res:
            pts = res.get("points") or res.get("loyaltyPoints") or res.get("bonusPoints", 0)
            return int(pts)
            
    except Exception as e:
        logger.error(f"Error fetching points for user {user_id}: {e}")
        
    return 0


# ================ المنتجات (للمنيو - Gizmo v2.0) ================

async def list_products_grouped_for_menu() -> Dict[str, List[Dict[str, Any]]]:
    """
    يجلب كل المنتجات من Gizmo ويقسمها حسب ProductGroupId.
    """
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    
    try:
        res = await gizmo_v2.execute("PRODUCTS_GET_ALL", query_params={"Pagination.Limit": 500})
        
        if isinstance(res, dict) and "data" in res:
            products = res["data"]
            
            for p in products:
                # في v2.0، التصنيف يعتمد على productGroupId، لذلك سنضع اسماً مؤقتاً 
                # أو نجلب اسم المجموعة إذا أردت لاحقاً إضافة مسار جلب مجموعات المنتجات
                group_id = p.get("productGroupId")
                group_name = f"قسم {group_id}" if group_id else "أخرى"
                
                # استخدام الحقول الصحيحة للإصدار 2.0 (name, price)
                safe_product = {
                    "id": p.get("id"),
                    "name": p.get("name") or p.get("description") or "بدون اسم",
                    "price": p.get("price", 0.0),
                    "group": group_name
                }
                
                grouped.setdefault(group_name, []).append(safe_product)
                
    except Exception as e:
        logger.error(f"Error fetching products: {e}")

    return grouped


# ================ الأجهزة المتاحة (Gizmo v2.0) ================

async def list_free_hosts_simple() -> List[Dict[str, Any]]:
    """
    يعيد قائمة مبسّطة عن الأجهزة المتاحة فقط.
    """
    simple_list: List[Dict[str, Any]] = []
    
    try:
        res = await gizmo_v2.execute("HOSTS_GET_ALL", query_params={"Pagination.Limit": 200})
        
        if isinstance(res, dict) and "data" in res:
            hosts = res["data"]
            
            for h in hosts:
                # في v2.0، التحقق إذا كان الجهاز يعمل وغير معطل (isOutOfOrder == False)
                # ولا ننسى التأكد أنه غير مشغول (يعتمد على مسارات الـ Sessions لاحقاً لمعرفة الإشغال الدقيق)
                if h.get("isOutOfOrder") is True or h.get("isDeleted") is True:
                    continue
                    
                simple_list.append({
                    "id": h.get("id"),
                    "number": h.get("number"),
                    "name": h.get("name") or str(h.get("number")),
                })
    except Exception as e:
        logger.error(f"Error fetching hosts: {e}")

    return simple_list


# ================ الشحن عبر Ziina ================

async def generate_topup_link_fixed(phone: str, amount: float = 50.0) -> str:
    """
    إنشاء رابط شحن رصيد بقيمة ثابتة عبر Ziina.
    """
    clean_phone = (phone or "").replace("+", "").replace(" ", "").strip()
    if not clean_phone:
        return "رقم الهاتف غير صالح."

    link = await generate_wallet_topup_link(clean_phone, amount)
    
    if link == "فشل إنشاء رابط الدفع حالياً، حاول بعد شوي أو تواصل مع الكاونتر.":
        # في حال وجود مشكلة في Ziina API (مثل 401 Unauthorized)
        return "عذراً، خدمة الدفع الإلكتروني معطلة حالياً. (تأكد من تحديث مفتاح Ziina في الخادم). يمكنك الشحن عبر الكاشير."

    return (
        f"تفضل رابط الشحن بقيمة {amount:.0f} {CURRENCY}:\n"
        f"{link}\n"
        f"بعد الدفع سيتم تحديث رصيدك تلقائياً."
    )


# ================ خدمات أخرى للعميل (حجوزات/جلسات) ================

async def uc_customer_view_my_reservations(phone: str) -> str:
    return "عرض حجوزاتك سيتم تفعيله قريباً بإذن الله."

async def uc_customer_view_current_host_uc(phone: str) -> str:
    return "معرفة جهازك الحالي سيتم تفعيلها قريباً بإذن الله."

async def uc_customer_view_remaining_time_uc(phone: str) -> str:
    return "عرض الوقت المتبقي لجلسة اللعب سيتم تفعيله قريباً بإذن الله."