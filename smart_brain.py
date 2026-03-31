import os
import logging
from google import genai
from google.genai import types
import redis
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SMART_BRAIN")

r = redis.from_url(os.getenv("REDIS_URI", "redis://localhost:6379/0"), decode_responses=True)

ai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-2.5-flash"

async def select_gemini_model():
    logger.info(f"Gemini model set to: {MODEL}")

async def chat_with_gemini(phone: str, message: str, role: str) -> str:
    system_prompt = f"""
أنت "سلطان"، مدير صالة HGC GAMING في العين.
رد بلغة عربية بسيطة ومحترمة.
معلومات المتصل: رقم الهاتف: {phone}, الدور: {role}.
تعامل مع طلبات الزبائن بناءً على الأدوات المتاحة.
"""
    try:
        response = ai_client.models.generate_content(
            model=MODEL,
            contents=message,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                tools=[],
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            ),
        )
        return response.text or "تم تنفيذ طلبك."
    except Exception as e:
        logger.error(f"Gemini chat error: {e}")
        return "عذرًا، حدث خطأ في الخدمة، يرجى المحاولة لاحقًا."

async def save_chat_history(phone: str, user_msg: str, bot_msg: str, max_length: int = 2000):
    old_chat = r.get(f"chat:{phone}") or ""
    new_chat = f"{old_chat}\n👤: {user_msg}\n🤖: {bot_msg}"
    r.setex(f"chat:{phone}", 3600, new_chat[-max_length:])
