# Mon API FastAPI

Une API simple créée avec FastAPI qui permet de gérer une liste d'items.

## Installation

1. Assurez-vous d'avoir Python 3.8+ installé
2. Créez un environnement virtuel :
   ```bash
   python -m venv .venv
   ```
3. Activez l'environnement virtuel :
   - Windows :
     ```bash
     .\.venv\Scripts\activate
     ```
   - Linux/Mac :
     ```bash
     source .venv/bin/activate
     ```
4. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

## Lancement de l'application

```bash
python main.py
```

L'application sera accessible à l'adresse : http://localhost:8000

## Documentation de l'API

Une fois l'application lancée, vous pouvez accéder à :
- Documentation Swagger UI : http://localhost:8000/docs
- Documentation ReDoc : http://localhost:8000/redoc

## Endpoints disponibles

- `GET /` : Message de bienvenue
- `GET /items/` : Liste tous les items
- `GET /items/{item_id}` : Récupère un item spécifique
- `POST /items/` : Crée un nouvel item

## Exemple d'utilisation

Pour créer un nouvel item, envoyez une requête POST à `/items/` avec un corps JSON comme ceci :
```json
{
    "name": "Mon Item",
    "description": "Description de mon item",
    "price": 29.99
}
``` 