# main.py

from typing import Dict, Any

from fastapi import FastAPI, Request

from rabbit_client import publish_inbound_message

print("### LOADED MAIN.PY FOR SMAM_ORCHESTRATOR (EVOLUTION + RABBITMQ + GIZMO) ###")

app = FastAPI(title="SMAM Orchestrator", version="1.0.0")


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def root() -> Dict[str, Any]:
    return {
        "service": "SMAM Orchestrator",
        "status": "running",
        "endpoints": [
            "/health",
            "/Webhook/messages-upsert",
            "/Webhook/messages-update",
            "/Webhook//messages-upsert",
            "/Webhook/messages-upsert/messages-upsert",
        ],
    }


async def _handle_evolution_webhook(body: Dict[str, Any]) -> Dict[str, Any]:
    """
    منطق مشترك لمعالجة Webhook من Evolution.
    يحوّل الحدث إلى Job وينشره في RabbitMQ ليعالجه worker.py.
    يدعم:
      - رسائل نصية عادية (conversation)
      - ضغط الأزرار (buttonsResponseMessage / templateButtonReplyMessage)
    """
    print("### messages-* RAW EVENT:", body)

    data = body.get("data", {}) or {}
    key = data.get("key", {}) or {}
    msg = data.get("message", {}) or {}

    remote_jid = key.get("remoteJid")
    from_phone = remote_jid.split("@")[0] if remote_jid else None
    push_name = data.get("pushName") or "ضيف"

    # 1) نص الرسالة العادية
    text = msg.get("conversation") or ""

    # 2) قراءة رد زر من Evolution (Buttons / Template Buttons)
    button_id = None

    # هذه البنية شائعة في Evolution؛ عدّل الأسماء إذا رأيت اختلافاً في اللوغ
    buttons_resp = msg.get("buttonsResponseMessage") or msg.get("templateButtonReplyMessage") or {}
    if buttons_resp:
        button_id = (
            buttons_resp.get("selectedButtonId")
            or buttons_resp.get("id")
            or buttons_resp.get("buttonId")
        )
        print("### EVOLUTION BUTTON RESPONSE:", buttons_resp)
        print("### BUTTON_ID DETECTED:", button_id)

    job = {
        "from_phone": from_phone,
        "from_name": push_name,
        "text": text,
        "button_id": button_id,
        "instance": body.get("instance"),
        "event": body.get("event"),
        "timestamp": data.get("messageTimestamp"),
        "raw": body,
    }

    print("### QUEUING JOB:", job)

    await publish_inbound_message(job)

    return {"status": "queued"}


@app.post("/Webhook/messages-upsert")
async def webhook_messages_upsert(request: Request) -> Dict[str, Any]:
    body: Dict[str, Any] = await request.json()
    return await _handle_evolution_webhook(body)


@app.post("/Webhook/messages-update")
async def webhook_messages_update(request: Request) -> Dict[str, Any]:
    body: Dict[str, Any] = await request.json()
    print("### messages-update received, redirecting to common handler")
    return await _handle_evolution_webhook(body)


@app.post("/Webhook//messages-upsert")
async def webhook_messages_upsert_double_slash(request: Request) -> Dict[str, Any]:
    body: Dict[str, Any] = await request.json()
    print("### messages-upsert (double slash) received, redirecting to common handler")
    return await _handle_evolution_webhook(body)


@app.post("/Webhook/messages-upsert/messages-upsert")
async def webhook_messages_upsert_double_path(request: Request) -> Dict[str, Any]:
    body: Dict[str, Any] = await request.json()
    print("### messages-upsert/messages-upsert received, redirecting to common handler")
    return await _handle_evolution_webhook(body)
