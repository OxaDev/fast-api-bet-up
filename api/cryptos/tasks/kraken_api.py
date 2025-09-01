import pydantic
from celery import shared_task
from requests import request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.logger import Logger
from db.config import get_session
from db.models.cryptos import CryptoCurrency, CryptoPrice  # tes modèles


class KrakenAPIResponse(pydantic.BaseModel):
    prices: list[float] = pydantic.Field(alias="price")
    high: float
    low: float


@shared_task
def scrape_crypto(crypto_code: str) -> None:
    Logger.info(f"Kraken API - starting scraping task for crypto '{crypto_code}'")

    with get_session() as session:
        session: AsyncSession

        stmt = select(CryptoCurrency).where(CryptoCurrency.crypto_code == crypto_code)
        crypto_currency = session.scalar(stmt)

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

        Logger.info(f"Kraken API - successfully scraped price for currency '{crypto_code}'")
    return 0
