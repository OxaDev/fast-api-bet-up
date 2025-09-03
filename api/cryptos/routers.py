import logging

from fastapi import APIRouter, Query
from pydantic import BaseModel

from api.cryptos.crud import CryptoCurrencyManager
from db.config import get_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cryptos", tags=["celery", "redbeat"])


class CreateCryptoTaskRequest(BaseModel):
    interval: int
    crypto_code: str


@router.post("/tasks")
async def create_crypto_task(request: CreateCryptoTaskRequest):
    async for session in get_session():  # Utilise async for pour obtenir la session
        crypto_currency_manager = CryptoCurrencyManager(session)
        crypto_currency = await crypto_currency_manager.create_crypto_currency(request.crypto_code, request.interval)
        return {"status": "success", "crypto_currency": crypto_currency}


@router.get("/prices")
async def get_crypto_prices(
    crypto_code: str = Query(..., description="The code of the cryptocurrency to fetch prices for")
):
    async for session in get_session():  # Utilise async for pour obtenir la session
        crypto_currency_manager = CryptoCurrencyManager(session)
        crypto_currency = await crypto_currency_manager.list_crypto_prices(crypto_code)
        return {"status": "success", "crypto_currency": crypto_currency}
