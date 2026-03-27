from datetime import datetime
from decimal import Decimal
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PaymentCreate(BaseModel):
    amount: Decimal
    currency: Literal["RUB", "USD", "EUR"]
    description: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    webhook_url: str


class PaymentCreateResponse(BaseModel):
    payment_id: UUID
    status: str
    created_at: datetime


class PaymentResponse(BaseModel):
    id: UUID
    amount: Decimal
    currency: str
    description: str
    metadata: dict[str, Any] = Field(validation_alias="payment_metadata")
    status: str
    idempotency_key: str
    webhook_url: str
    created_at: datetime
    processed_at: datetime | None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
