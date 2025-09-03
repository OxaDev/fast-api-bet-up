from api.routers import router as api_router


def apply_router(app):
    app.include_router(api_router)
