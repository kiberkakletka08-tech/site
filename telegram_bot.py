import httpx
import logging

BOT_TOKEN = "8336385730:AAE9YGuk9_f-IC_s4R0nMCy0Pa8n_R6Rz9o"
ADMIN_CHAT_ID = 740478354

logger = logging.getLogger("telegram_bot")

async def send_telegram_notification(message: str):
    """Sends a notification to the configured Telegram chat."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": ADMIN_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            logger.info("Telegram notification sent.")
        except httpx.HTTPError as e:
            logger.error(f"Failed to send Telegram notification: {e}")
