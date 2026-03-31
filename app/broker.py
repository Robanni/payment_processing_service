from faststream.rabbit import RabbitBroker, RabbitExchange, RabbitQueue
from faststream.rabbit.schemas import ExchangeType

from app.config import settings

broker = RabbitBroker(settings.RABBITMQ_URL)

payments_exchange = RabbitExchange("payments", type=ExchangeType.DIRECT, durable=True)
payments_queue = RabbitQueue(
    "payments.new",
    durable=True,
    arguments={
        "x-dead-letter-exchange": "payments.dlx",
        "x-dead-letter-routing-key": "payments.new",
    },
)


async def declare_topology() -> None:
    declared_exchange = await broker.declare_exchange(payments_exchange)
    declared_queue = await broker.declare_queue(payments_queue)
    await declared_queue.bind(declared_exchange, routing_key="payments.new")

    dlx = RabbitExchange("payments.dlx", type=ExchangeType.DIRECT, durable=True)
    dlq = RabbitQueue("payments.dlq", durable=True)
    declared_dlx = await broker.declare_exchange(dlx)
    declared_dlq = await broker.declare_queue(dlq)
    await declared_dlq.bind(declared_dlx, routing_key="payments.new")
