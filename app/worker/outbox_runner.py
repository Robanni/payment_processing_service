import asyncio
import logging

from app.broker import broker
from app.worker.outbox_publisher import OutboxPublisher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    await broker.start()
    publisher = OutboxPublisher()
    try:
        await publisher.run()
    finally:
        await broker.close()


if __name__ == "__main__":
    asyncio.run(main())
