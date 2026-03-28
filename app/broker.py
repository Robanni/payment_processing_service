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
