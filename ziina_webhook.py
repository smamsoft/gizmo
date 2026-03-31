import os
import logging
from datetime import datetime, timezone

import redis
from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("ZIINA_WEBHOOK")

app = FastAPI()

r = redis.from_url(os.getenv("REDIS_URI", "redis://localhost:6379/0"), decode_responses=True)

GIZMO_AUTH = (os.getenv("GIZMO_USER"), os.getenv("GIZMO_PASS"))
GIZMO_BASE = f"http://{os.getenv('GIZMO_IP')}:{os.getenv('GIZMO_PORT', '8080')}/api"
WEBHOOK_SECRET = os.getenv("ZIINA_WEBHOOK_SECRET", "")

async def _update_gizmo_balance(phone: str, amount: float):
    # هنا استدعاء API Gizmo لشحن رصيد المستخدم (بدون كود تفاصيل)
    # يُفترض وجود API مثل POST /users/{user_id}/deposit/{amount}
    # أولاً جلب user_id عبر رقم الهاتف
    import httpx
    try:
        async with httpx.AsyncClient(auth=GIZMO_AUTH, verify=False) as client:
            # جلب المستخدم
            res_user = await client.get(f"{GIZMO_BASE}/users", params={"username": phone})
            if res_user.status_code == 200 and res_user.json().get("result"):
                user_id = res_user.json()["result"][0]["id"]
                
                res_dep = await client.put(f"{GIZMO_BASE}/users/{user_id}/deposit/{amount}/some_payment_method_id")
                if res_dep.status_code == 200:
                    logger.info(f"تم تحديث رصيد {phone} في Gizmo بمبلغ {amount}")
                    return True
    except Exception as e:
        logger.error(f"خطأ تحديث رصيد Gizmo: {e}")
    return False

@app.post("/ziina/webhook")
async def ziina_webhook(request: Request):
    if WEBHOOK_SECRET:
        secret_header = request.headers.get("X-Ziina-Signature", "")
        if secret_header != WEBHOOK_SECRET:
            logger.warning("توقيع webhook غير صحيح")
            raise HTTPException(status_code=403, detail="Invalid signature")

    body = await request.json()
    logger.info(f"استلام webhook من Ziina: {body}")

    status = body.get("status")
    amount_cents = body.get("amount", 0)
    currency = body.get("currency", "AED")
    metadata = body.get("metadata", {})
    phone = str(metadata.get("phone", "")).strip()

    if not phone:
        logger.error("رقم الهاتف مفقود في بيانات الدفع")
        raise HTTPException(status_code=400, detail="Missing phone metadata")

    amount_aed = amount_cents / 100.0

    if status == "succeeded":
        logger.info(f"نجاح عملية دفع {phone} مبلغ {amount_aed} AED")
        # سجل في Redis
        ts = datetime.now(timezone.utc).isoformat()
        r.set(f"ziina:status:{phone}", "SUCCESS")
        r.set(f"ziina:last:{phone}", f"{ts}|{amount_aed}|{body}")

        # تحديث رصيد Gizmo
        success = await _update_gizmo_balance(phone, amount_aed)
        if not success:
            logger.error(f"فشل تحديث رصيد Gizmo للعميل {phone}")
    else:
        r.set(f"ziina:status:{phone}", status or "UNKNOWN")
        r.set(f"ziina:last:{phone}", f"{datetime.now(timezone.utc).isoformat()}|{status}|{amount_aed}|{body}")
        logger.warning(f"عملية دفع غير ناجحة لـ {phone}، الحالة: {status}")

    return {"received": True}
