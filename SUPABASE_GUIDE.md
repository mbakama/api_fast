# Guide d'utilisation de Supabase avec FastAPI

## Configuration

1. **Variables d'environnement (.env)** :
   ```bash
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_KEY=your-anon-key
   DATABASE_URL=postgresql://postgres:your-password@db.your-project-id.supabase.co:5432/postgres
   ```

2. **Installation des dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

## Utilisation de base

### Test de connexion
```bash
python test_supabase_connection.py
```

### Démarrer l'API
```bash
uvicorn main:app --reload
```

## Exemples d'utilisation avec Supabase

### 1. Client Supabase direct

```python
from supabase import create_client, Client
import os

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# Insérer des données
data = {"name": "John", "age": 30}
result = supabase.table('users').insert(data).execute()

# Lire des données
result = supabase.table('users').select('*').execute()

# Mettre à jour
result = supabase.table('users').update({"age": 31}).eq('id', 1).execute()

# Supprimer
result = supabase.table('users').delete().eq('id', 1).execute()
```

### 2. Avec SQLAlchemy (recommandé)

```python
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)

# Créer les tables
Base.metadata.create_all(bind=engine)

# Utilisation
db = SessionLocal()
new_user = User(name="John", age=30)
db.add(new_user)
db.commit()
db.refresh(new_user)
db.close()
```

## Points d'API ajoutés

- `GET /supabase/status` - Vérifier la connexion Supabase
- `GET /supabase/insert-test` - Insérer des données de test

## Sécurité

- Ne jamais exposer la `SUPABASE_KEY` côté client
- Utiliser RLS (Row Level Security) dans Supabase
- Configurer les politiques d'accès appropriées

## Migration depuis SQLite vers Supabase

1. Exporter les données SQLite :
   ```bash
   python export_readings_to_json.py
   ```

2. Créer les tables dans Supabase (voir `SUPABASE_MIGRATION.md`)

3. Importer les données dans Supabase PostgreSQL

## Ressources

- [Documentation Supabase](https://supabase.com/docs)
- [Guide FastAPI avec PostgreSQL](https://fastapi.tiangolo.com/tutorial/sql-databases/)
