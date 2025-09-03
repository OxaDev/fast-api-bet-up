# fastapi-proj

Starter FastAPI + PostgreSQL + Alembic

## Prérequis

- Python 3.11+
- PostgreSQL
- [uv](https://github.com/astral-sh/uv) (gestionnaire de paquets rapide)
- Docker (optionnel, pour le développement conteneurisé)

## Installation

### Avec uv

```sh
python -m venv venv
source venv/bin/activate # Unix
"venv/Scripts/activate.bat" # Windows
pip install uv
uv pip install -r requirements.txt
```

### Variables d'environnement

Configurez le fichier `.env` à la racine :

```
# Postgres
POSTGRES_USER=app
POSTGRES_PASSWORD=app
POSTGRES_DB=app_db
POSTGRES_PORT=5432
POSTGRES_ENDPOINT=localhost

# Redis
REDIS_MAIN_ENDPOINT=localhost
REDIS_MAIN_PORT=6379
REDIS_MAIN_USER=redis
REDIS_MAIN_PASSWORD=redis

APP_ENV=development
```

## Stack Docker

Lancez la stack avec :

```sh
docker compose up --force-recreate --build -d beat worker db redis 
```

## Appliquez les migrations Alembic

```sh
alembic upgrade head
```

## Lancer l'API en local

### Avec Docker

```sh
docker compose up --force-recreate --build -d api
```

### Sur sa machine

```sh
uvicorn core.main:app --reload
```

Accédez à [http://localhost:8000](http://localhost:8000)  
La documentation interactive est disponible sur [http://localhost:8000/docs](http://localhost:8000/docs)

## Développement

- Formatage : `black`, `isort`
- Lint : `flake8`
- Pre-commit :  
  ```sh
  pre-commit install
  ```

## Migrations

Créer une migration :

```sh
alembic revision --autogenerate -m "message"
```

Appliquer :

```sh
alembic upgrade head
```

## Structure

- `core/` : Entrée FastAPI et configuration principale
- `db/` : Modèles SQLAlchemy et configuration base
- `alembic/` : Migrations
- `api/` : Routes et logique métier

---

**Licence** : MIT
