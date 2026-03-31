import asyncio
import logging
import random
from datetime import datetime, timezone

import httpx
from faststream import FastStream
from faststream.rabbit.annotations import RabbitMessage

from app.broker import broker, payments_exchange, payments_queue
from app.db.models import Payment
from app.db.session import async_session_maker

from sqlalchemy import select

logger = logging.getLogger(__name__)

MAX_RETRIES = 3

app = FastStream(broker)


async def _send_webhook(url: str, payload: dict) -> None:
    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.post(url, json=payload)
                r.raise_for_status()
                return
        except Exception:
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(2**attempt)
            else:
                raise


async def _process(data: dict) -> tuple[str, datetime]:
    payment_id: str = data["payment_id"]

    await asyncio.sleep(random.uniform(2, 5))
    success = random.random() < 0.9
    status = "succeeded" if success else "failed"
    processed_at = datetime.now(timezone.utc)

    async with async_session_maker() as db:
        result = await db.execute(select(Payment).where(Payment.id == payment_id))
        payment = result.scalar_one_or_none()
        if payment:
            payment.status = status
            payment.processed_at = processed_at
            await db.commit()

    return status, processed_at


@broker.subscriber(payments_queue, payments_exchange)
async def handle_payment(data: dict, raw_message: RabbitMessage) -> None:
    try:
        status, processed_at = await _process(data)
    except Exception as exc:
        logger.error("processing failed for %s: %s", data.get("payment_id"), exc)
        await raw_message.nack(requeue=False)
        return

    try:
        await _send_webhook(
            data["webhook_url"],
            {
                "payment_id": data["payment_id"],
                "status": status,
                "processed_at": processed_at.isoformat(),
            },
        )
        await raw_message.ack()
    except Exception as exc:
        logger.error("webhook exhausted for %s: %s", data.get("payment_id"), exc)
        await raw_message.nack(requeue=False)
