from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.payments import router as payments_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="Payment Processing Service", version="1.0.0", lifespan=lifespan)
app.include_router(payments_router)
