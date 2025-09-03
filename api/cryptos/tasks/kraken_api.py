from datetime import datetime, timezone

import pydantic
from celery import shared_task
from requests import request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core import env
from core.logger import Logger
from db.models.cryptos import CryptoCurrency, CryptoPrice
from db.models.periodic_tasks import PeriodicTask

# Create synchronous engine for Celery tasks
sync_engine = create_engine(env.DATABASE_URL.replace("postgresql+asyncpg", "postgresql"))
SessionLocal = sessionmaker(sync_engine)


class KrakenAPIResponse(pydantic.BaseModel):
    prices: list[float] = pydantic.Field(alias="price")
    high: float
    low: float


@shared_task
def scrape_crypto(crypto_code: str, task_uuid: str | None = None) -> None:
    Logger.info(f"Kraken API - starting scraping task for crypto '{crypto_code}'")

    with SessionLocal() as session:
        crypto_currency = session.query(CryptoCurrency).filter(CryptoCurrency.crypto_code == crypto_code).first()

        if not crypto_currency:
            Logger.error(f"Kraken API - invalid CryptoCurrency configuration for '{crypto_code}'")
            return 1

        clean_crypto_code = crypto_code.lower()

        kraken_api_url = (
            f"https://iapi.kraken.com/api/internal/markets/all/market-charts"
            f"?symbol={clean_crypto_code}&timeframe=5y&quote_symbol=usd"
        )
        kraken_api_headers = {"Referer": "https://www.kraken.com/"}

        try:
            kraken_request = request(
                method="GET",
                url=kraken_api_url,
                headers=kraken_api_headers,
                timeout=10,
            )
            kraken_request.raise_for_status()
        except Exception as e:
            Logger.error(f"Kraken API - request failed for '{crypto_code}': {e}")
            return 1

        prices_data = kraken_request.json().get("result", {}).get("data", {}).get(crypto_code, {})

        if not prices_data:
            Logger.error(f"Kraken API - empty data for '{crypto_code}'")
            return 1

        validated_response = KrakenAPIResponse(**prices_data)

        new_price = CryptoPrice(
            currency=crypto_currency,
            high=validated_response.high,
            low=validated_response.low,
            price=validated_response.prices[-1],
        )

        session.add(new_price)
        session.commit()

        if task_uuid is not None:
            task = session.query(PeriodicTask).filter(PeriodicTask.uuid == task_uuid).first()
            if task:
                task.last_run = datetime.now(timezone.utc)
                session.commit()

        Logger.info(f"Kraken API - successfully scraped price for currency '{crypto_code}'")
    return 0
