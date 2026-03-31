import asyncio
import logging

from aiormq.exceptions import AMQPConnectionError

from app.broker import broker, declare_topology
from app.worker.outbox_publisher import OutboxPublisher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    while True:
        try:
            await broker.start()
            break
        except AMQPConnectionError as exc:
            logger.warning("rabbitmq is not ready yet: %s", exc)
            await asyncio.sleep(5)

    await declare_topology()
    publisher = OutboxPublisher()
    try:
        await publisher.run()
    finally:
        await broker.close()


if __name__ == "__main__":
    asyncio.run(main())
