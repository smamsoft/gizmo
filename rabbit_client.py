# rabbit_client.py

import os
import json
from typing import Dict, Any

import aio_pika

# من .env: RABBITMQ_URI=amqp://guest:guest@smam_rabbitmq:5672/
RABBITMQ_URI = os.getenv("RABBITMQ_URI", "amqp://guest:guest@smam_rabbitmq:5672/")
INBOUND_QUEUE = "whatsapp_inbound"


async def publish_inbound_message(job: Dict[str, Any]) -> None:
    """
    ينشر رسالة (Job) في طابور RabbitMQ باسم whatsapp_inbound.

    شكل job المتوقع مثلاً:
      {
        "from_phone": "9715....",
        "from_name": "اسم المرسل",
        "text": "رسالة المستخدم",
        "instance": "gizmo_bot",
        "event": "messages.upsert",
        "timestamp": 1234567890,
        "raw": {...}  # جسم Webhook الكامل من Evolution
      }
    """
    connection = await aio_pika.connect_robust(RABBITMQ_URI)

    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue(INBOUND_QUEUE, durable=True)

        body = json.dumps(job, ensure_ascii=False).encode("utf-8")

        await channel.default_exchange.publish(
            aio_pika.Message(
                body=body,
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=queue.name,
        )

        print("### RABBIT_CLIENT: Published job to queue:", queue.name)
