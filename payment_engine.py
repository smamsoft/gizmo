import os
import logging
import httpx
import redis
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PAYMENT_ENGINE")

r = redis.from_url(os.getenv("REDIS_URI", "redis://localhost:6379/0"), decode_responses=True)

ZIINA_KEY = os.getenv("ZIINA_SECRET_KEY") or os.getenv("ZIINA_API_KEY")
GIZMO_AUTH = (os.getenv("GIZMO_USER"), os.getenv("GIZMO_PASS"))
GIZMO_BASE = f"http://{os.getenv('GIZMO_IP')}:{os.getenv('GIZMO_PORT', '8080')}/api"

class PaymentEngine:
    def __init__(self):
        if not ZIINA_KEY:
            logger.warning("Ziina API key not configured!")
        self.api_key = ZIINA_KEY

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def create_payment_intent(self, phone: str, amount_aed: float):
        if not self.api_key:
            return None
        payload = {
            "amount": int(amount_aed * 100),
            "currency": "AED",
            "metadata": {"phone": phone, "source": "Sultan_AI_System"},
        }
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                res = await client.post(
                    "https://api-v2.ziina.com/api/payment_intent", json=payload, headers=self._headers()
                )
                if res.status_code in (200, 201):
                    data = res.json()
                    link = data.get("redirect_url")
                    if link:
                        self._log_payment_request(phone, amount_aed, link)
                        logger.info(f"Payment link created for {phone} amount {amount_aed}")
                        return link
        except Exception as e:
            logger.error(f"Payment intent creation error: {e}")
        return None

    def _log_payment_request(self, phone: str, amount: float, url: str):
        ts = datetime.now(timezone.utc).isoformat()
        entry = f"{ts}|{amount}|{url}"
        try:
            r.lpush(f"paylog:{phone}", entry)
            r.ltrim(f"paylog:{phone}", 0, 50)
            r.set(f"last_payment_req:{phone}", entry)
        except Exception as e:
            logger.error(f"Logging payment request failed: {e}")

payment_engine = PaymentEngine()

async def generate_wallet_topup_link(phone: str, amount: float) -> str:
    link = await payment_engine.create_payment_intent(phone, amount)
    if not link:
        return "فشل إنشاء رابط الدفع، حاول مرة أخرى."
    return f"تفضل رابط الشحن بقيمة {amount:.0f} درهم:\n{link}\nبعد الدفع سيتم تحديث رصيدك تلقائياً."
