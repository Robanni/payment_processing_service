from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import verify_api_key
from app.db.session import get_db
from app.schemas.payment import PaymentCreate, PaymentCreateResponse, PaymentResponse
from app.services.payment import create_payment, get_payment

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])


@router.post("", status_code=status.HTTP_202_ACCEPTED, response_model=PaymentCreateResponse)
async def create(
    body: PaymentCreate,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_api_key),
) -> PaymentCreateResponse:
    payment = await create_payment(
        db,
        amount=body.amount,
        currency=body.currency,
        description=body.description,
        payment_metadata=body.metadata,
        webhook_url=body.webhook_url,
        idempotency_key=idempotency_key,
    )
    return PaymentCreateResponse(
        payment_id=payment.id,
        status=payment.status,
        created_at=payment.created_at,
    )


@router.get("/{payment_id}", response_model=PaymentResponse)
async def retrieve(
    payment_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_api_key),
) -> PaymentResponse:
    payment = await get_payment(db, payment_id)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    return PaymentResponse.model_validate(payment)
