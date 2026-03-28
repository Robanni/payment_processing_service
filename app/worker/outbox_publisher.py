import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import select

from app.broker import broker, payments_exchange, payments_queue
from app.db.models import OutboxEvent
from app.db.session import async_session_maker

logger = logging.getLogger(__name__)


class OutboxPublisher:
    async def _publish_batch(self) -> None:
        async with async_session_maker() as db:
            result = await db.execute(
                select(OutboxEvent)
                .where(OutboxEvent.published.is_(False))
                .with_for_update(skip_locked=True)
                .limit(10)
            )
            events = result.scalars().all()
            if not events:
                return

            for event in events:
                await broker.publish(
                    event.payload,
                    queue=payments_queue,
                    exchange=payments_exchange,
                )
                event.published = True
                event.published_at = datetime.now(timezone.utc)

            await db.commit()

    async def run(self) -> None:
        while True:
            try:
                await self._publish_batch()
            except Exception as exc:
                logger.error("outbox error: %s", exc)
            await asyncio.sleep(1)
