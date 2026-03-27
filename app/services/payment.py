import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import OutboxEvent, Payment


async def get_payment(db: AsyncSession, payment_id: uuid.UUID) -> Payment | None:
    result = await db.execute(select(Payment).where(Payment.id == payment_id))
    return result.scalar_one_or_none()


async def create_payment(
    db: AsyncSession,
    *,
    amount: Decimal,
    currency: str,
    description: str,
    payment_metadata: dict,
    webhook_url: str,
    idempotency_key: str,
) -> Payment:
    payment = Payment(
        id=uuid.uuid4(),
        amount=amount,
        currency=currency,
        description=description,
        payment_metadata=payment_metadata,
        status="pending",
        idempotency_key=idempotency_key,
        webhook_url=webhook_url,
    )
    db.add(payment)
    db.add(
        OutboxEvent(
            id=uuid.uuid4(),
            payment_id=payment.id,
            event_type="payment.created",
            payload={
                "payment_id": str(payment.id),
                "amount": str(amount),
                "currency": currency,
                "webhook_url": webhook_url,
            },
        )
    )

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        result = await db.execute(
            select(Payment).where(Payment.idempotency_key == idempotency_key)
        )
        return result.scalar_one()

    await db.refresh(payment)
    return payment
