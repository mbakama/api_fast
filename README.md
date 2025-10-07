# API FastAPI — Lectures Bahá'íes

API FastAPI avec SQLAlchemy. Supporte SQLite en local et Postgres (Supabase) en prod.

## Installation

1. Python 3.10+
2. Environnement virtuel
   ```bash
   python -m venv .venv && source .venv/bin/activate
   ```
3. Dépendances
   ```bash
   pip install -r requirements.txt
   ```

## Configuration (Supabase / Postgres)

Créez un fichier `.env` à la racine en vous basant sur l'exemple ci-dessous.

```bash
# Exemple .env
# URL de connexion Postgres (Supabase -> Project Settings -> Database -> Connection string)
# Formats acceptés:
# - postgresql://USER:PASSWORD@HOST:PORT/DB
# - postgresql+psycopg://USER:PASSWORD@HOST:PORT/DB
SUPABASE_DB_URL=postgresql://USER:PASSWORD@HOST:6543/postgres

# Alternative générique
# DATABASE_URL=postgresql://USER:PASSWORD@HOST:6543/postgres
```

En absence de `SUPABASE_DB_URL` ou `DATABASE_URL`, l'app utilisera `sqlite:///./bahai_readings.db`.

## Lancer l'application (auto-reload)

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Accès:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Base de données et migrations (Alembic)

Alembic est configuré pour lire l'URL depuis l'environnement.

- Générer les tables (si vides) via l'app: au premier démarrage, `main.py` appelle `Base.metadata.create_all`.
- Seed (optionnel):
  ```bash
  python seed_data.py
  ```
- Migrations:
  ```bash
  # Révision auto à partir des modèles
  alembic revision --autogenerate -m "message"
  # Appliquer
  alembic upgrade head
  ```

## Notes

- L'URL fournie par Supabase peut être `postgres://...` ou `postgresql://...`. L'app convertit automatiquement en `postgresql+psycopg://` pour utiliser `psycopg` v3.
- Sur SQLite, `check_same_thread` est géré automatiquement.