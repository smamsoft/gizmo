# worker.py

import asyncio
import json
import os
from typing import Dict, Any, Optional

import aio_pika

from authz import get_role_for_phone
from intents import handle_intent
from evo_client import send_text
from smart_brain import chat_with_gemini, save_chat_history  # كود الذكاء


RABBITMQ_URI = os.getenv("RABBITMQ_URI", "amqp://guest:guest@smam_rabbitmq:5672/")
INBOUND_QUEUE = "whatsapp_inbound"


async def handle_job(message: aio_pika.IncomingMessage) -> None:
    """
    يُستدعى لكل رسالة (Job) في الطابور:
      - يحدد الدور من رقم الواتساب
      - ينادي handle_intent (القوائم + Gizmo)
      - لو لم يُفهم الطلب، يحاول chat_with_gemini
      - يحفظ سجل المحادثة في Redis
      - يرسل الرد عبر Evolution
    """
    async with message.process():
        try:
            job: Dict[str, Any] = json.loads(message.body.decode("utf-8"))
        except Exception as e:
            print("### WORKER: Failed to decode message:", e)
            return

        from_phone: Optional[str] = job.get("from_phone")
        from_name: str = job.get("from_name") or "ضيف"
        text: str = job.get("text") or ""
        button_id: Optional[str] = job.get("button_id")

        print("### WORKER RECEIVED JOB:", {
            "from_phone": from_phone,
            "from_name": from_name,
            "text": text,
            "button_id": button_id,
        })

        if not from_phone:
            print("### WORKER: Missing from_phone, skipping job.")
            return

        # 1) تحديد الدور
        role = get_role_for_phone(from_phone)
        print("### WORKER ROLE DECISION:", {"phone": from_phone, "role": role})

        # 2) استدعاء منطق الـ Intents
        try:
            reply_text = await handle_intent(text, from_phone, role, button_id=button_id)
        except Exception as e:
            print("### WORKER ERROR in handle_intent:", e)
            reply_text = "حدث خطأ داخلي أثناء معالجة طلبك، حاول لاحقاً."
        print("### WORKER INTENT REPLY:", reply_text)

        # 3) لو الرد عام ولم يفهم الطلب، جرّب Gemini كمساعد ثانوي
        if ("لم أفهم طلبك" in reply_text) or ("الخيار غير معروف" in reply_text):
            try:
                ai_reply = await chat_with_gemini(from_phone, text, role)
                if ai_reply:
                    reply_text = ai_reply
                    print("### WORKER GEMINI REPLY USED")
            except Exception as e:
                print("### WORKER ERROR in chat_with_gemini:", e)

        # 4) إرسال الرد عبر Evolution
        try:
            evo_result = await send_text(from_phone, reply_text)
            print("### WORKER EVOLUTION SEND RESULT:", evo_result)
        except Exception as e:
            print("### WORKER ERROR sending via Evolution:", e)

        # 5) حفظ سجل المحادثة في Redis
        try:
            await save_chat_history(from_phone, text, reply_text)
        except Exception as e:
            print("### WORKER ERROR save_chat_history:", e)


async def main() -> None:
    """
    يتصل بـ RabbitMQ، ويستهلك طابور whatsapp_inbound إلى الأبد.
    """
    print("### WORKER: Connecting to RabbitMQ:", RABBITMQ_URI)
    connection = await aio_pika.connect_robust(RABBITMQ_URI)

    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue(INBOUND_QUEUE, durable=True)

        print(f"### WORKER: Waiting for messages in queue '{INBOUND_QUEUE}' ...")
        await queue.consume(handle_job)

        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
