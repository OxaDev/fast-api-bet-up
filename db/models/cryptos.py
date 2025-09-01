from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, select
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Session, relationship

from db.config import Base

PRICE_HISTORY_LIMIT = 100


class CryptoCurrency(Base):
    __tablename__ = "crypto_currency"

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String(100), default="Undefined")
    crypto_code = Column(String(20), unique=True, nullable=False)

    prices = relationship("CryptoPrice", back_populates="currency", cascade="all, delete-orphan")

    @hybrid_property
    def current_price(self):
        """
        Retourne le prix le plus récent ou 0.0 s'il n'existe pas.
        """
        if not self.prices:
            return 0.0
        return sorted(self.prices, key=lambda p: p.created_at, reverse=True)[0].price

    def get_price_history(self, session: Session):
        """
        Récupère l'historique des prix limité à PRICE_HISTORY_LIMIT.
        """
        stmt = (
            select(CryptoPrice)
            .where(CryptoPrice.currency_id == self.id)
            .order_by(CryptoPrice.created_at.desc())
            .limit(PRICE_HISTORY_LIMIT)
        )
        return session.scalars(stmt).all()


class CryptoPrice(Base):
    __tablename__ = "crypto_price"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    price = Column(Float, nullable=False)
    high = Column(Float, nullable=True)
    low = Column(Float, nullable=True)

    currency_id = Column(Integer, ForeignKey("crypto_currency.id", ondelete="CASCADE"), nullable=False)

    currency = relationship("CryptoCurrency", back_populates="prices")
