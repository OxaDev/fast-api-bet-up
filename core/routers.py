from api.cryptos.routers import router as crypto_router
from api.routers import router as api_router


def apply_router(app):
    app.include_router(api_router)
    app.include_router(crypto_router)
