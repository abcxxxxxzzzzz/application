import asyncio
import logging

import aiohttp

from config import settings


logger = logging.getLogger(
    "kk-monitor"
)


async def send_alarm(message):

    if not settings.telegram_enable:
        logger.info(
            "telegram disabled"
        )
        return

    if (
        not settings.telegram_bot_token
        or not settings.telegram_chat_id
    ):
        logger.warning(
            "telegram config missing"
        )
        return

    url = (
        f"https://api.telegram.org/"
        f"bot{settings.telegram_bot_token}/sendMessage"
    )

    data = {
        "chat_id": settings.telegram_chat_id,
        "text": message,
        "disable_web_page_preview": True
    }

    for retry in range(3):

        try:
            timeout = aiohttp.ClientTimeout(
                total=20
            )

            async with aiohttp.ClientSession(
                timeout=timeout
            ) as session:

                async with session.post(
                    url,
                    json=data
                ) as resp:

                    text = await resp.text()

                    if resp.status == 200:

                        logger.info(
                            "telegram send success"
                        )

                        return True

                    logger.warning(
                        "telegram failed status=%s body=%s",
                        resp.status,
                        text
                    )

        except Exception as e:

            logger.error(
                "telegram error retry=%s error=%s",
                retry + 1,
                e
            )

        await asyncio.sleep(
            retry + 1
        )

    logger.error(
        "telegram send failed after retry"
    )

    return False