import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.celery.periodic_tasks.services import PeriodicTaskManager
from db.models.cryptos import CryptoCurrency, CryptoPrice


@dataclass
class CryptoCurrencyManager:
    db_session: AsyncSession

    async def create_crypto_currency(self, crypto_code: str, interval: int) -> CryptoCurrency:
        task_uuid = str(uuid.uuid4())
        periodic_task_manager = PeriodicTaskManager(self.db_session)
        task = await periodic_task_manager.create(
            task_name="api.cryptos.tasks.kraken_api.scrape_crypto",
            task_uuid=task_uuid,
            interval=interval,
            task_args=[crypto_code],
            task_kwargs={"task_uuid": task_uuid},
        )

        new_currency = CryptoCurrency(crypto_code=crypto_code, periodic_task=task)
        self.db_session.add(new_currency)
        await self.db_session.commit()
        await self.db_session.refresh(new_currency)

        return new_currency

    async def list_crypto_prices(self, crypto_code: str) -> list[CryptoPrice]:
        result = await self.db_session.execute(
            select(CryptoPrice)
            .where(CryptoPrice.currency.has(CryptoCurrency.crypto_code == crypto_code))
            .order_by(CryptoPrice.created_at.desc())
        )
        return result.scalars().all()
