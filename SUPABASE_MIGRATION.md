# Migration vers Supabase (PostgreSQL)

## Configuration Supabase

1. **Créer un projet Supabase** :
   - Allez sur [supabase.com](https://supabase.com)
   - Créez un nouveau projet
   - Notez l'URL de votre projet et votre clé API

2. **Configurer les variables d'environnement** :
   - Copiez le fichier `.env.example` vers `.env`
   - Remplacez les valeurs par vos vraies informations Supabase :
   ```env
   DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
   ```

3. **Variables d'environnement Supabase** :
   ```env
   SUPABASE_URL=https://your-project-ref.supabase.co
   SUPABASE_KEY=your-anon-key
   ```

## Étapes de migration

Une fois Supabase configuré :

1. **Créer les tables dans Supabase** :
   ```bash
   cd e:/fastapi
   python -m alembic upgrade head
   ```

2. **Migrer les données existantes** (optionnel) :
   - Si vous avez des données dans SQLite à migrer
   - Utilisez l'outil d'export/import de données

3. **Tester la connexion** :
   ```bash
   python main.py
   ```

## Configuration de production

Pour déployer sur un service comme Render avec Supabase :

1. Définissez la variable `DATABASE_URL` dans votre plateforme de déploiement
2. Assurez-vous que les variables d'environnement sont correctement configurées

## Commandes utiles

- **Créer une nouvelle migration** : `alembic revision --autogenerate -m "description"`
- **Appliquer les migrations** : `alembic upgrade head`
- **Revenir en arrière** : `alembic downgrade -1`

## Notes importantes

- PostgreSQL est sensible à la casse pour les noms de tables/colonnes
- Les modèles SQLAlchemy sont compatibles avec PostgreSQL
- Assurez-vous que votre projet Supabase a les bonnes permissions de base de données
