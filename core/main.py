from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.routers import apply_router


# Lifespan : plus d'appel à init_db, Alembic gère le schéma
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Au démarrage : éventuellement vérifier la connexion DB
    yield
    # À l'arrêt : rien de spécial pour l'instant


app = FastAPI(title="FastAPI + PostgreSQL + Alembic Starter", lifespan=lifespan)

# Inclusion des routes
apply_router(app)


@app.get("/")
async def root():
    return {"status": "ok"}
