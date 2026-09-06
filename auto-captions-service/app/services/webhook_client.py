import logging
import httpx
from typing import Dict, Any

logger = logging.getLogger(__name__)

class WebhookClient:
    """Delivers callback payloads upon job completion or failure."""

    @staticmethod
    async def send_callback(callback_url: str, payload: Dict[str, Any], max_retries: int = 3):
        if not callback_url:
            return

        async with httpx.AsyncClient(timeout=15.0) as client:
            for attempt in range(1, max_retries + 1):
                try:
                    logger.info(f"Sending webhook notification to {callback_url} (attempt {attempt})...")
                    response = await client.post(callback_url, json=payload)
                    if response.status_code < 400:
                        logger.info(f"Webhook delivered successfully: {response.status_code}")
                        return
                    else:
                        logger.warning(f"Webhook responded with HTTP {response.status_code}")
                except Exception as e:
                    logger.error(f"Webhook delivery attempt {attempt} failed: {e}")
